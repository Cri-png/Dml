# Dragon Mania Legends BDAE / Runtime Animation Findings

_Last updated from the live IDA/debugger session._

## 1. Runtime node TRS layout

The runtime node stores local transform channels at these offsets:

| Runtime node offset | Meaning | Format |
|---:|---|---|
| `+0xD8` | Translation X | `float` |
| `+0xDC` | Translation Y | `float` |
| `+0xE0` | Translation Z | `float` |
| `+0xE4` | Rotation X | `float` |
| `+0xE8` | Rotation Y | `float` |
| `+0xEC` | Rotation Z | `float` |
| `+0xF0` | Rotation W | `float` |
| `+0xF4` | Scale X | `float` |
| `+0xF8` | Scale Y | `float` |
| `+0xFC` | Scale Z | `float` |
| `+0x160` | Transform/state flags | `uint32` |

Quaternion order is confirmed as:

```text
x, y, z, w
```

No component shuffle happens in the rotation setter.

---

## 2. Serialized node record TRS layout

The serialized node record uses this layout:

| Serialized node offset | Meaning | Runtime destination |
|---:|---|---|
| `+0x08` | Name/reference-like value | node virtual `+0x68` |
| `+0x18` | Translation `float3` | node `+0xD8/+0xDC/+0xE0` |
| `+0x24` | Rotation quaternion `float4`, XYZW | node `+0xE4/+0xE8/+0xEC/+0xF0` |
| `+0x34` | Scale `float3` | node `+0xF4/+0xF8/+0xFC` |
| `+0x40` | Boolean enabled/visible-style flag | node virtual `+0x98` |
| `+0x44` | Child-list area | recursive node construction |
| `+0x4C` | Typed/component record area | loader switch cases |

Default-pose loading applies these serialized values directly into the runtime node through the node’s virtual setters.

---

## 3. Confirmed node setter functions

Live node vtable from the debugger:

```text
node vtable = 0x7FF7CB763688
```

Relevant slots:

| Vtable slot | Function | Meaning |
|---:|---|---|
| `+0x068` | `sub_7FF7C933E9E0` | name/ref setter |
| `+0x098` | `sub_7FF7C933F060` | bool / visibility / enabled-style setter |
| `+0x0C8` | `sub_7FF7C933C390` | add child |
| `+0x148` | `sub_7FF7C933EE90` | scale `float3` setter |
| `+0x158` | `sub_7FF7C933EDF0` | rotation quaternion `float4` setter |
| `+0x168` | `sub_7FF7C933EA70` | translation `float3` setter |

### `sub_7FF7C933EA70` — translation setter

Writes:

```text
node +0xD8 = input[0]
node +0xDC = input[1]
node +0xE0 = input[2]
```

It ORs `node +0x160` with `0x180`.

It checks whether translation is exactly `(0, 0, 0)` and uses bit `0x10` as a translation-zero optimization flag.

### `sub_7FF7C933EDF0` — rotation setter

Writes:

```text
node +0xE4 = input[0]  ; x
node +0xE8 = input[1]  ; y
node +0xEC = input[2]  ; z
node +0xF0 = input[3]  ; w
```

It ORs `node +0x160` with `0x140`.

It checks identity rotation as:

```text
x == 0
y == 0
z == 0
w == 1
```

and uses bit `0x11` as a rotation-identity optimization flag.

### `sub_7FF7C933EE90` — scale setter

Writes:

```text
node +0xF4 = input[0]
node +0xF8 = input[1]
node +0xFC = input[2]
```

It ORs `node +0x160` with `0x120`.

It checks identity scale as:

```text
x == 1
y == 1
z == 1
```

and uses bit `0x12` as a scale-identity optimization flag.

### Shared flag behavior

Each TRS setter updates `node +0x160`. If the corresponding identity flag is not set, it clears bit `0x0F`, likely invalidating cached local/world matrix state.

---

## 4. Default node construction / initialization

`sub_7FF7C93F7030` is a constructor/initializer for the runtime node class.

It stores the serialized node record pointer at:

```text
node +0x1C0 = serialized node record
```

Then applies the default serialized transform:

```text
[serialized +0x08]      → sub_7FF7C933E9E0
[serialized +0x18..20]  → sub_7FF7C933EA70  ; translation
[serialized +0x24..30]  → sub_7FF7C933EDF0  ; rotation XYZW
[serialized +0x34..3C]  → sub_7FF7C933EE90  ; scale
[serialized +0x40]      → sub_7FF7C933F060  ; flag
```

This confirms the serialized node record and runtime node fields match semantically.

---

## 5. Recursive loader path

`sub_7FF7A7ECEB20` is the larger recursive node/object construction dispatcher.

It receives a loading context and serialized node record, creates/resolves a runtime node object, and then applies the serialized node’s default TRS through the node virtual setters:

```text
rdi + vtable +0x168 = translation setter
rdi + vtable +0x158 = rotation setter
rdi + vtable +0x148 = scale setter
rdi + vtable +0x98  = bool/flag setter
rdi + vtable +0xC8  = add child
```

The creator interface is stored at:

```text
context + 0x08
```

Important creator slots observed:

| Creator slot | Meaning |
|---:|---|
| `+0x108` | normal node creator/resolver |
| `+0x110` | referenced/special node creator/resolver |
| `+0x120` | typed/component create/attach path |
| `+0x128` | alternate typed/component create/attach path |
| `+0x130` | root/top node/container creator |

`sub_7FF7A7ECE940` wraps this by creating a root/top node, calling `ECEB20`, attaching the loaded node to the root, and finalizing.

---

## 6. Animation sampler / handler path

The important live runtime hit was at the rebased cached-cursor sampler:

```text
static: sub_7FF7A7F34E80
live:   sub_7FF7C93C4E80
```

At the live breakpoint:

```text
RCX = handler object
RDX = track/source object
R8  = runtime/context value
R9  = consumer node object
```

The consumer node vtable resolved to the confirmed TRS setter interface:

```text
consumer +0x148 → sub_7FF7C933EE90  ; scale
consumer +0x158 → sub_7FF7C933EDF0  ; rotation
consumer +0x168 → sub_7FF7C933EA70  ; translation
```

This proves the animation sampler sends sampled values directly into the runtime node TRS setters.

---

## 7. Handler vtable observed live

Live handler object:

```text
handler object = 0x7FF7CB8C3738
handler vtable = 0x7FF7CB759C08
```

Observed slots:

| Handler vtable slot | Live function | Meaning |
|---:|---|---|
| `+0x50` | `sub_7FF7C9367B90` | decode one sample / handler-specific |
| `+0x58` | `sub_7FF7C9367B60` | decode/interpolate sample pair / handler-specific |
| `+0x60` | `sub_7FF7C935AE80` | single-key apply |
| `+0x68` | `sub_7FF7C935AE00` | interpolated apply |
| `+0x88` | `sub_7FF7C93C4E80` | time sampler with cached cursor |
| `+0x90` | `sub_7FF7C93C4F60` | time sampler without external cursor |

The static equivalents are the previously investigated `F34E80/F34F60` time sampler family.

---

## 8. Lower interpolated apply function

At the lower interpolated apply hit:

```text
RIP = 0x7FF7C935AE00
```

The calling convention was:

```text
RCX = handler
RDX = track/source object
R8  = key A
R9  = key B
stack +0x30 = consumer node
```

Example live values:

```text
R8 = 0x1F6
R9 = 0x1F7
stack +0x30 = 0x22528BF6000
```

So at this layer, `R9` is not the consumer anymore. It is key index B. The consumer node is passed on the stack.

---

## 9. Live decoded animation values

### Rotation

Breakpoint at:

```text
RIP = 0x7FF7C933EDF0
```

Input:

```text
node = 0x22528BF2200
quat input =
  x = -0.7071068286895752
  y = -0.0000010394470564
  z =  0.0000010394470564
  w = -0.7071068286895752
```

This confirms decoded animated rotation values are passed as XYZW quaternions into the node rotation setter.

Note: quaternion `q` and `-q` represent the same rotation, so `(-0.707, 0, 0, -0.707)` is equivalent to `(0.707, 0, 0, 0.707)`.

### Scale

Breakpoint at:

```text
RIP = 0x7FF7C933EE90
```

Input:

```text
node = 0x22528BF8E00
scale input =
  x = 0.6524767875671387
  y = 0.40921053290367126
  z = 0.6524766683578491
```

This confirms decoded animated scale values are passed into the node scale setter.

### Translation

Breakpoint at:

```text
RIP = 0x7FF7C933EA70
```

Input:

```text
node = 0x22528BF6000
translation input =
  x = 4200.3505859375
  y = -423.4967041015625
  z = 1362.83447265625
```

This confirms decoded animated translation values are passed into the node translation setter.

---

## 10. Current solved pipeline

The full runtime path is now confirmed:

```text
BDAE / BRES serialized node
  → default local TRS loaded into runtime node
  → animation sampler evaluates track at current time
  → lower handler apply decodes keyframe value
  → runtime node virtual TRS setter
  → node local TRS fields
  → local/world matrix rebuild
  → skinning
```

For an offline renderer, the node application rule should be:

```python
node.translation = (tx, ty, tz)
node.rotation_xyzw = (qx, qy, qz, qw)
node.scale = (sx, sy, sz)
```

Then rebuild:

```text
local matrix from translation / rotation XYZW / scale
world matrix through parent hierarchy
skin matrices from bound node world matrices and bind/inverse-bind data
```

---

## 11. Remaining work

The main unresolved work is now offline data parsing, not runtime destination mapping.

Remaining tasks:

1. Parse animation track/source objects from BDAE/BRES data.
2. Map each serialized track to its handler vtable/type.
3. Decode packed quaternion tracks offline.
4. Decode vec3 translation and scale tracks offline.
5. Map track targets to runtime/serialized node names or indices.
6. Recreate the time sampler logic:
   - resolve key A/key B
   - compute interpolation factor
   - choose single-key or interpolated apply
7. Apply decoded values to the confirmed node fields.
8. Rebuild local/world matrices and skin matrices.

---

## 12. Debugger one-liners used

### Dump node TRS from a node pointer

```python
import idc,struct;f=lambda a: struct.unpack("<f",idc.get_bytes(a,4))[0];node=idc.get_reg_value("RCX");[print(hex(o),f(node+o)) for o in [0xD8,0xDC,0xE0,0xE4,0xE8,0xEC,0xF0,0xF4,0xF8,0xFC]]
```

### Dump quaternion input at rotation setter

```python
import idc,struct;f=lambda a: struct.unpack("<f",idc.get_bytes(a,4))[0];rcx=idc.get_reg_value("RCX");rdx=idc.get_reg_value("RDX");print("RIP",hex(idc.get_reg_value("RIP")));print("node",hex(rcx));print("quat input",f(rdx),f(rdx+4),f(rdx+8),f(rdx+12));print("old node quat",f(rcx+0xE4),f(rcx+0xE8),f(rcx+0xEC),f(rcx+0xF0))
```

### Dump vec3 input at translation/scale setter

```python
import idc,struct;f=lambda a: struct.unpack("<f",idc.get_bytes(a,4))[0];rcx=idc.get_reg_value("RCX");rdx=idc.get_reg_value("RDX");print("RIP",hex(idc.get_reg_value("RIP")));print("node",hex(rcx));print("vec input",f(rdx),f(rdx+4),f(rdx+8));print("old T",f(rcx+0xD8),f(rcx+0xDC),f(rcx+0xE0));print("old R",f(rcx+0xE4),f(rcx+0xE8),f(rcx+0xEC),f(rcx+0xF0));print("old S",f(rcx+0xF4),f(rcx+0xF8),f(rcx+0xFC))
```
