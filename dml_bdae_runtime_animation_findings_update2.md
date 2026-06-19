# Dragon Mania Legends BDAE / Runtime Animation Findings — Update 2

_This file adds the newer animation-channel, handler, interpolation, and codec findings discovered after the first findings document._

---

## 1. Current reverse-engineering status

The core runtime animation destination path is now solved.

The remaining work is mostly implementation and codec coverage, not searching for where animation goes.

### Solved

```text
BDAE/BRES animation channel
  → runtime 0x28 channel record
  → handler/decoder object
  → generic time sampler
  → handler-specific apply/decode function
  → node virtual TRS setter
  → runtime node local TRS fields
```

### Approximate remaining work

For a first working animated dragon preview:

```text
~5–10% reverse engineering left
```

For a full general importer that handles all animation files/codecs:

```text
~25–35% reverse engineering left
```

The difficult unknowns are now mostly:

```text
1. Implementing the confirmed handler formulas offline.
2. Mapping file bytes into the runtime ptr0/ptr8 structures.
3. Covering rarer codec variants from the handler selector.
4. Testing many clips/nodes/material/effect channels.
```

---

## 2. Runtime channel record table

The active animation source object has:

```text
RDX + 0x00 → ptr0 / channel record table
RDX + 0x08 → ptr8 / packed or raw animation data stream
RDX + 0x10 → runtime cache/state/subsource pointer
```

The `ptr0` table contains clean `0x28`-byte records.

### 0x28 channel record layout

```c
struct AnimChannelRecord {
    char*   name;          // +0x00, e.g. "Plane690-node-translation"
    uint32  flag_or_countA;// +0x08, often 1
    uint32  offC;          // +0x0C, offset into ptr8 or related stream
    uint32  flag_or_countB;// +0x10, often 1
    uint32  off14;         // +0x14, offset into ptr8 or related stream
    void*   handler;       // +0x18, runtime handler/decoder object
    uint64  tail;          // +0x20, sometimes 0, sometimes another offset
};
```

The `name` field is a real string pointer, not a binary descriptor.

Example decoded names:

```text
Plane634-node-translation
Plane690-node-translation
Plane690-node-rotation
Plane663-node-scale
```

The target binding is therefore string-based:

```text
<node name>-node-translation
<node name>-node-rotation
<node name>-node-scale
```

For offline import, split the string at `-node-`:

```text
node = text before "-node-"
property = text after "-node-"
```

---

## 3. Confirmed channel groups

A contiguous channel table was observed from index `0` through `107`.

### Translation group A

```text
Plane634-node-translation through Plane680-node-translation
handler = 0x7FF7CB8C3738
```

### Translation group B

```text
Plane690-node-translation through Plane695-node-translation
handler = 0x7FF7CB8C35B8
```

### Rotation group

```text
Plane689-node-rotation through Plane695-node-rotation
handler = 0x7FF7CB8C3838
```

### Scale group

```text
Plane625-node-scale
Plane634-node-scale through Plane680-node-scale
handler = 0x7FF7CB8C3538
```

### Important boundary

The clean `0x28` channel table ends at:

```text
index 107 = Plane680-node-scale
```

Rows after that are a different structure/table. They should not be interpreted as channel records, even if some byte patterns look like strings such as `fade` or `tornado`.

---

## 4. Example Plane690 records

### Plane690 translation

```text
Plane690-node-translation
index   = 47
record  = 0x225274F6C30
offC    = 0x1654
off14   = 0x166C
tail    = 0x1678
handler = 0x7FF7CB8C35B8
```

### Plane690 rotation

```text
Plane690-node-rotation
index   = 54
record  = 0x225274F6D48
offC    = 0x1784
off14   = 0x179C
tail    = 0
handler = 0x7FF7CB8C3838
```

No clean `Plane690-node-scale` record was found in the same channel table. This clip/table may not animate scale for Plane690.

---

## 5. `ptr8` data stream and offsets

The record offset fields point directly into the `ptr8` data stream:

```text
ptr8 = [RDX + 0x08]
data address = ptr8 + record.offset
```

Confirmed by dumping:

```text
ptr8 + 0x1654
ptr8 + 0x166C
ptr8 + 0x1678
ptr8 + 0x1784
ptr8 + 0x179C
```

The data at those offsets was valid `float32` animation data.

### Plane690 translation curves

```text
off 0x1654:
  0.328176, 0.304741, 0.281750, 0.259259,
  0.237324, 0.216000, 0.195343, 0.175407,
  0.156250, 0.137926, 0.120491, 0.104000,
  0.088509, 0.074074, 0.060750, 0.048593

off 0x166C:
  0.195343, 0.175407, 0.156250, 0.137926,
  0.120491, 0.104000, 0.088509, 0.074074,
  0.060750, 0.048593, 0.037657, 0.028000,
  0.019676, 0.012741, 0.007250, 0.003259

off 0x1678:
  0.137926, 0.120491, 0.104000, 0.088509,
  0.074074, 0.060750, 0.048593, 0.037657,
  0.028000, 0.019676, 0.012741, 0.007250,
  0.003259, 0.000824, 0.000000, 0.001844
```

### Plane690 rotation curves

```text
off 0x1784:
  0.879509, 0.862074, 0.843750, 0.824593,
  0.804657, 0.784000, 0.762676, 0.740741,
  0.718250, 0.695259, 0.671824, 0.648000,
  0.623843, 0.599407, 0.574750, 0.549926

off 0x179C:
  0.762676, 0.740741, 0.718250, 0.695259,
  0.671824, 0.648000, 0.623843, 0.599407,
  0.574750, 0.549926, 0.524991, 0.500000,
  0.475009, 0.450074, 0.425250, 0.400593
```

These values are smooth normalized float curves. Some codecs use raw float streams; other codecs use quantized byte/word streams.

---

## 6. Handler objects and vtable slots

### Handler `0x7FF7CB8C3738`

Used by many translation channels.

```text
handler = 0x7FF7CB8C3738
vtable  = 0x7FF7CB759C08

+0x60 → sub_7FF7C935AE80  ; single-key apply
+0x68 → sub_7FF7C935AE00  ; interpolated apply
+0x88 → sub_7FF7C93C4E80  ; generic time sampler with cached cursor
+0x90 → sub_7FF7C93C4F60  ; generic time sampler without external cursor
```

### Handler `0x7FF7CB8C35B8`

Used by `Plane690` through `Plane695` translation records.

```text
handler = 0x7FF7CB8C35B8
vtable  = 0x7FF7CB75A448

+0x60 → sub_7FF7C935AA90  ; single-key translation apply
+0x68 → sub_7FF7C935AA10  ; interpolated translation apply
+0x88 → sub_7FF7C93C4E80  ; generic time sampler
+0x90 → sub_7FF7C93C4F60  ; generic time sampler
```

### Handler `0x7FF7CB8C3838`

Used by rotation records.

```text
handler = 0x7FF7CB8C3838
vtable  = 0x7FF7CB759688

+0x60 → sub_7FF7C935CCA0  ; single-key rotation apply
+0x68 → sub_7FF7C935CBA0  ; interpolated rotation apply
+0x88 → sub_7FF7C93C4E80  ; generic time sampler
+0x90 → sub_7FF7C93C4F60  ; generic time sampler
```

### Handler `0x7FF7CB8C3538`

Used by scale records.

Relevant apply wrappers eventually call:

```text
node vtable +0x148
```

which is the runtime scale setter.

The helper functions observed for scale/vec quantized decoding include:

```text
sub_7FF7C936AC30
sub_7FF7C936ADA0
sub_7FF7C936AEA0
```

These handle signed byte/word quantized data.

---

## 7. Generic sampler layer

The generic sampler functions are shared across handlers:

```text
sub_7FF7C93C4E80 = time sampler with cached cursor
sub_7FF7C93C4F60 = time sampler without external cursor
```

At a live `C4E80` hit:

```text
RCX = handler object
RDX = track/source object
R8  = runtime/context value
R9  = consumer node object
```

The consumer node vtable confirmed:

```text
consumer +0x148 → scale setter
consumer +0x158 → rotation setter
consumer +0x168 → translation setter
```

At lower apply functions, the calling convention can change. For example, in an interpolated apply function:

```text
RCX = handler
RDX = track/source
R8  = key A
R9  = key B
stack +0x30 = consumer node
```

In single-key apply functions:

```text
RCX = handler
RDX = track/source
R8  = key index
R9  = consumer node
```

---

## 8. Translation handler `AA90/AA10`

### `sub_7FF7C935AA90` — single-key translation apply

This function:

```text
1. Reads the track/source object.
2. Builds a temporary vec3 on the stack.
3. Calls node vtable +0x168.
```

The final call is:

```asm
call qword ptr [rax+168h]
```

So it directly applies a decoded translation vector to the runtime node.

The function reads:

```asm
movss [out+0], ...
movss [out+4], ...
movss [out+8], ...
call node+0x168
```

### `sub_7FF7C935AA10` — interpolated translation apply

This function calls:

```text
sub_7FF7C9368A60
```

to build the interpolated translation vector, then calls:

```text
node vtable +0x168
```

### `sub_7FF7C9368A60` — interpolated translation helper

This helper shows a mixed constant + animated component model:

```text
out.x = descriptor/static value
out.y = descriptor/static value
out.z = lerp(sampleA, sampleB, t)
```

The interpolation core is:

```asm
subss xmm1, [sampleA]
mulss xmm1, xmm3      ; xmm3 = interpolation t
addss xmm1, [sampleA]
movss [out+8], xmm1
```

Equivalent pseudocode:

```python
out_z = sample_a + (sample_b - sample_a) * t
```

This means some translation codecs animate only one axis and copy the other components from descriptor/default fields.

---

## 9. Rotation handler `CCA0/CBA0`

### `sub_7FF7C935CCA0` — single-key rotation apply

This function reads four `float32` values from the data stream:

```text
sample + 0x04
sample + 0x08
sample + 0x0C
sample + 0x10
```

Then writes them to the stack as:

```text
x, y, z, w
```

and calls:

```text
node vtable +0x158
```

So this rotation codec’s single-key path is direct raw quaternion XYZW.

### `sub_7FF7C935CBA0` — interpolated rotation apply

This function:

```text
1. Loads quaternion A.
2. Loads quaternion B.
3. Computes 1.0 - t and t.
4. Calls sub_7FF7C9365D60.
5. Applies output through node vtable +0x158.
```

So the rotation interpolated path uses a dedicated quaternion interpolation helper.

---

## 10. Quaternion helper `sub_7FF7C9365D60`

This function is a sign-aware quaternion interpolation routine.

It performs:

```text
1. Load first quaternion.
2. Load second quaternion.
3. Compute dot product.
4. If dot < 0, flip one quaternion.
5. Use shortest path.
6. For larger angular differences, use trig/slerp-style weighting.
7. For small differences, use normalized linear interpolation.
8. Normalize when needed.
9. Write final quaternion XYZW.
```

Important behaviors observed:

```text
- Dot product checks between quaternions.
- Sign flip using XOR masks when dot is negative.
- Trig calls in the larger-angle branch.
- Lerp + normalize in the small-angle branch.
- Final output is written as x, y, z, w.
```

For an offline renderer, implement:

```python
def quat_interp(a, b, t):
    # shortest-path slerp
    if dot(a, b) < 0:
        b = -b
    return slerp_or_nlerp(a, b, t)
```

For close-enough preview quality, sign-corrected normalized lerp may work, but exact matching should use shortest-path slerp with a small-angle nlerp fallback.

---

## 11. Quaternion weighted blend helper `sub_7FF7C9365C80`

This helper processes 5-float records.

If count is 1:

```text
copy 5 floats directly
```

Otherwise it loops over `count` records and accumulates weighted values.

Each record layout appears to be:

```text
float x
float y
float z
float w
float extra
```

The loop multiplies each 5-float record by a weight and accumulates:

```text
out.x += weight * record.x
out.y += weight * record.y
out.z += weight * record.z
out.w += weight * record.w
out.extra += weight * record.extra
```

This likely supports animation blending or multi-sample blend data.

---

## 12. Scale and quantized vec codecs

The scale helper paths show byte and word quantized streams.

### Byte quantized variant

Observed in `sub_7FF7C936AC30`:

```asm
movsx ecx, byte ptr [...]
cvtdq2ps xmm1, xmm1
mulss xmm1, [scale]
addss xmm1, [bias]
```

Equivalent:

```python
decoded = float(int8_sample) * scale + bias
```

For interpolated keys:

```python
value = decoded_a + (decoded_b - decoded_a) * t
```

### Word quantized variant

Observed in `sub_7FF7C936AEA0`:

```asm
movsx ecx, word ptr [...]
cvtdq2ps xmm1, xmm1
mulss xmm1, [scale]
addss xmm1, [bias]
```

Equivalent:

```python
decoded = float(int16_sample) * scale + bias
```

These helpers combine quantized animated components with static/default components, then the wrappers apply the result to:

```text
node vtable +0x148
```

for scale.

---

## 13. Handler selector `sub_7FF7C9366380`

`sub_7FF7C9366380` is a master handler/decoder selector.

It switches on a codec/type value up to:

```text
0x81
```

and assigns handler objects/vtables.

Examples of assigned handler objects/vtables seen in the selector:

```text
unk_7FF7CB8C3090
off_7FF7CB7593B8
unk_7FF7CB8C30A0
```

This function is important for a full general importer because it maps serialized channel codec/type values to runtime handler implementations.

For the current preview/import target, not every case is needed. Only the handlers actually used by the tested dragon/clip need to be implemented first.

---

## 14. Runtime node TRS destination recap

The runtime node setters are still the final destination:

```text
node +0x148 → scale setter       → node +0xF4/+0xF8/+0xFC
node +0x158 → rotation setter    → node +0xE4/+0xE8/+0xEC/+0xF0
node +0x168 → translation setter → node +0xD8/+0xDC/+0xE0
```

Rotation is XYZW:

```text
node +0xE4 = x
node +0xE8 = y
node +0xEC = z
node +0xF0 = w
```

---

## 15. Offline implementation plan

### Step 1 — Parse channels

For each `0x28` record:

```python
name = read_string(record.name)
node_name, prop = name.split("-node-")
handler = record.handler
offC = record.offC
off14 = record.off14
tail = record.tail
```

### Step 2 — Resolve property

```python
if prop == "translation":
    target = node.translation
elif prop == "rotation":
    target = node.rotation_xyzw
elif prop == "scale":
    target = node.scale
```

### Step 3 — Decode by handler/codec

Supported first-pass handlers:

```text
translation handler 0x7FF7CB8C35B8:
  AA90/AA10 style mixed constant + one animated float/axis

rotation handler 0x7FF7CB8C3838:
  raw quaternion XYZW single-key
  shortest-path quaternion slerp interpolated

scale handler 0x7FF7CB8C3538:
  raw/quantized byte/word scalar components
  scale + bias decode
  optional lerp
```

### Step 4 — Apply sampled values

```python
node.translation = (tx, ty, tz)
node.rotation_xyzw = (qx, qy, qz, qw)
node.scale = (sx, sy, sz)
```

### Step 5 — Rebuild transforms

```text
local matrix = T * R * S
world matrix = parent_world * local
skin matrix = bone_world * inverse_bind
```

---

## 16. Immediate next test

Use a known node/channel pair:

```text
Plane690-node-translation
Plane690-node-rotation
```

Known records:

```text
translation:
  offC  = 0x1654
  off14 = 0x166C
  tail  = 0x1678

rotation:
  offC  = 0x1784
  off14 = 0x179C
```

Test procedure:

```text
1. Pick a frame/time that hit the live debugger.
2. Decode Plane690 translation and rotation offline.
3. Apply to a test node.
4. Compare against live setter input values.
```

Live setter values already confirmed examples:

```text
rotation input:
  -0.7071068287, -0.0000010394, 0.0000010394, -0.7071068287

translation input:
  4200.3505859375, -423.4967041015625, 1362.83447265625

scale input:
  0.6524767876, 0.4092105329, 0.6524766684
```

Once one node’s offline values match the live setter values, the animation importer is functionally proven.

---

## 17. Useful one-line debugger dumps

### Dump channel records

```python
import idc;q=idc.get_qword;d=idc.get_wide_dword;rdx=idc.get_reg_value("RDX");p=q(rdx);read=lambda a: bytes([idc.get_wide_byte(a+i) for i in range(0,64)]).split(b"\x00")[0];[print(i,read(q(p+i*0x28)),"rec",hex(p+i*0x28),"d8",d(p+i*0x28+8),"offC",hex(d(p+i*0x28+0xC)),"d10",d(p+i*0x28+0x10),"off14",hex(d(p+i*0x28+0x14)),"handler",hex(q(p+i*0x28+0x18)),"tail",hex(q(p+i*0x28+0x20))) for i in range(0,108)]
```

### Dump float curves at offsets

```python
import idc,struct;q=idc.get_qword;f=lambda a: struct.unpack("<f",idc.get_bytes(a,4))[0];rdx=idc.get_reg_value("RDX");p8=q(rdx+8);offs=[0x1654,0x166C,0x1678,0x1784,0x179C];[print("OFF",hex(base),[round(f(p8+base+o),6) for o in range(0,0x40,4)]) for base in offs]
```

### Dump handler vtable slots

```python
import idc;q=idc.get_qword;handlers=[0x7FF7CB8C3738,0x7FF7CB8C35B8,0x7FF7CB8C3838,0x7FF7CB8C3538];[print("handler",hex(h),"vt",hex(q(h)),"+60",hex(q(q(h)+0x60)),idc.get_name(q(q(h)+0x60)),"+68",hex(q(q(h)+0x68)),idc.get_name(q(q(h)+0x68)),"+88",hex(q(q(h)+0x88)),idc.get_name(q(q(h)+0x88)),"+90",hex(q(q(h)+0x90)),idc.get_name(q(q(h)+0x90))) for h in handlers]
```
