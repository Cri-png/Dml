# Dragon Mania Legends BDAE / Runtime Animation Findings — Update 3

_This update records the new Plane### animation decoder findings from the latest live IDA/debugger session._

## 1. New major result

The `Plane###` animation path is now partially decoded offline.

Two runtime handlers were validated against live node setter inputs:

```text
Plane635-node-translation
  handler = 0x7FF7CB8C3738
  apply   = sub_7FF7C935AE80
  setter  = node vtable +0x168 / sub_7FF7C933EA70

Plane625-node-scale
  handler = 0x7FF7CB8C3538
  setter  = node vtable +0x148 / sub_7FF7C933EE90
```

Both handlers use the same broad **descriptor → row table → sample block** lookup model.

This means the earlier normalized-looking floats at `ptr8 + offC` / `ptr8 + off14` were not the final values. They were nearby stream data. The actual setter values came from indexed sample blocks reached through packed descriptors.

## 2. Confirmed live translation hit

### Setter hit

```text
RIP  = 0x7FF7C933EA70
node = 0x22528BF6C00
```

The setter input was:

```text
translation input:
  x = -3470.14208984375
  y = -95.8230209350586
  z = 3224.494140625
```

The node already had:

```text
old/current T:
  -3473.84033203125
  -95.8230209350586
  3238.29541015625

R:
  0.701057493686676
 -0.09229595214128494
  0.09229595959186554
  0.7010573148727417

S:
  0.7492260336875916
  0.5736842155456543
  0.7492259740829468
```

Return address:

```text
RET = 0x7FF7C935AF1C
```

This places the call inside the `AE80` handler family.

## 3. Node identity for the translation hit

The runtime node had:

```text
node +0x1C0 = 0x2252765C960
```

The serialized record pointed to strings:

```text
serialized +0x00 → "Plane635-node"
serialized +0x08 → "Plane635"
```

So the live translation hit belongs to:

```text
Plane635-node-translation
```

The serialized Plane records are laid out at a stride of:

```text
0x60 bytes
```

Example defaults:

```text
REC 0 Plane635-node
  T = -3922.11328125, -95.8230209350586, 3298.94677734375
  R =  0.701057493686676, -0.09229595214128494, 0.09229595959186554, 0.7010573148727417
  S =  0.8157894015312195, 0.6868419647216797, 0.8157893419265747

REC 1 Plane636-node
  T = -3570.989501953125, -95.8230209350586, 3281.005126953125
  R =  0.7010573744773865, -0.09229595959186554, 0.09229596704244614, 0.7010573744773865
  S =  0.736842155456543, 0.5526315569877625, 0.7368420958518982

REC 2 Plane637-node
  T = -3752.012939453125, -95.82301330566406, 2958.105712890625
  R =  0.7010573744773865, -0.09229595959186554, 0.09229595959186554, 0.7010573744773865
  S =  0.6315789818763733, 0.37368419766426086, 0.6315788626670837
```

## 4. Plane635 channel record

At the live hit:

```text
track = 0x6F608FF1F8
ptr0  = 0x225274F6500
ptr8  = 0x225274F90D8
key   = 0x13 = 19
```

Matching channel records:

```text
Plane635-node-translation
  record  = 0x225274F6500
  offC    = 0x1374
  off14   = 0x138C
  handler = 0x7FF7CB8C3738
  tail    = 0

Plane635-node-scale
  record  = 0x225274F6E88
  offC    = 0x1804
  off14   = 0x181C
  handler = 0x7FF7CB8C3538
  tail    = 0
```

The key value was confirmed from stack:

```text
possible key low32 = 0x13
high32 = 0x225
```

So the current sample key was:

```text
key = 19
```

## 5. Plane635 normalized-looking nearby curves

For `Plane635-node-translation`, the nearby float curves at `ptr8 + offC` and `ptr8 + off14` were:

```text
off 0x1374 at key 19:
  0.185281

off 0x138C at key 19:
  0.388344
```

Neighboring values:

```text
off 0x1374:
  key 16 = 0.104
  key 17 = 0.129094
  key 18 = 0.15625
  key 19 = 0.185281
  key 20 = 0.216
  key 21 = 0.248219
  key 22 = 0.28175

off 0x138C:
  key 16 = 0.28175
  key 17 = 0.316406
  key 18 = 0.352
  key 19 = 0.388344
  key 20 = 0.42525
  key 21 = 0.462531
  key 22 = 0.5
```

These were **not** the final translation values. The actual output comes from a descriptor/sample-block lookup.

## 6. `sub_7FF7C935AE80` single-key translation apply

The disassembly showed this structure:

```text
RCX = handler
RDX = track/source object
R8  = key index
R9  = consumer node
```

Important instructions from `AE80`:

```asm
mov     rcx, [rdx]        ; record table / current record
mov     rdx, [rdx+8]      ; ptr8 stream
mov     r10d, r8d         ; key

movsxd  rax, dword ptr [rcx+0Ch]       ; offC
movsxd  r9, dword ptr [rdx+4]
add     rdx, 4
add     r9, rdx                         ; tablebase = ptr8 + 4 + u32(ptr8+4)

movups  xmm0, xmmword ptr [rax+rcx+1Ch]
psrldq  xmm0, 8
movq    r8, xmm0                        ; packed descriptor qword

movsxd  rcx, r8d                        ; row index
mov     rdx, r8
shr     rdx, 30h                        ; stride
imul    edx, r10d                       ; stride * key
shr     r8, 20h
movzx   eax, r8w                        ; base offset

lea     r9, [r9+rcx*8]                  ; row = tablebase + rowidx*8
movsxd  r8, dword ptr [r9+4]            ; datarel
add     edx, eax                        ; idx = base + stride*key
movsxd  rdx, edx
add     rdx, r9                         ; row + idx

movss   xmm0, dword ptr [r8+rdx+4]
movss   xmm1, dword ptr [r8+rdx+8]
movss   xmm0, dword ptr [r8+rdx+0Ch]
call    qword ptr [node_vtable+168h]
```

This proves `AE80` is an indexed sample-block decoder.

## 7. Shared descriptor/sample-block decoder formula

For the current `Plane###` handlers, the useful decoder pattern is:

```python
record = track.record_ptr       # [track + 0]
ptr8   = track.data_ptr         # [track + 8]
key    = sample_key             # R8 or stack-derived key

table_base = ptr8 + 4 + u32(ptr8 + 4)

off = u32(record + 0x0C)        # usually offC
desc = u64(record + off + 0x24)

row_index   = desc & 0xFFFFFFFF
base_offset = (desc >> 32) & 0xFFFF
stride      = (desc >> 48) & 0xFFFF

idx = base_offset + stride * key
row = table_base + row_index * 8
data_rel = u32(row + 4)

sample = row + data_rel + idx
```

The sample block contains repeated vec3 data.

For the translation hit, the reconstruction produced:

```text
desc       = 0x000C000000000017
rowidx     = 0x17
baseofs    = 0
stride     = 0xC
idx        = 0xE4
row        = 0x225274F9198
datarel    = 0x13714
sample     = 0x2252750C990
```

The float block at `sample` was:

```text
+0x00 =  3283.150146484375
+0x04 = -3478.000732421875
+0x08 =   -95.8230209350586
+0x0C =  3253.822265625

+0x10 = -3470.14208984375
+0x14 =   -95.8230209350586
+0x18 =  3224.494140625

+0x1C = -3438.70849609375
+0x20 =   -95.8230209350586
+0x24 =  3107.1826171875

+0x28 = -3422.9921875
+0x2C =   -95.8230209350586
```

The setter input matched the vec3 at:

```text
sample + 0x10
sample + 0x14
sample + 0x18
```

```text
-3470.14208984375
-95.8230209350586
3224.494140625
```

So for this hit, the effective output read is:

```python
out = vec3(sample + 0x10)
```

The direct disassembly reads `[sample + 4/8/C]`; the observed reconstruction lands one vec3 earlier unless the exact `sample` base is shifted by the internal `r8 + rdx` combination. Offline code should validate alignment by matching known setter data.

## 8. Plane625 scale hit

A valid scale setter hit was captured:

```text
RIP  = 0x7FF7C933EE90
node = 0x22528BF8E00
```

Input to the scale setter:

```text
0.9210526943206787
0.8657894730567932
0.9210526347160339
```

The node identity was:

```text
node +0x1C0 → 0x2252765C8A0
serialized +0x00 → "Plane625-node"
serialized +0x08 → "Plane625"
```

At the hit:

```text
track = 0x6F608FF1F8
record = 0x225274F6E38
ptr8 = 0x225274F90D8
key = 23
tablebase = 0x225274F90E0
```

Channel record:

```text
Plane625-node-scale
  record  = 0x225274F6E38
  offC    = 0x17E4
  off14   = 0x17FC
  handler = 0x7FF7CB8C3538
  tail    = 0
```

## 9. Scale descriptor result

For `Plane625-node-scale`, the useful descriptor was:

```text
offC + 0x24 = 0x000C00000000008D
```

Decoded fields:

```text
rowidx = 0x8D
baseofs = 0
stride = 0xC
key = 23
idx = 0x114
row = 0x225274F9548
datarel = 0xB24BC
sample = 0x225275ABB18
```

The sample block contained:

```text
0.9736842513084412
0.9473684430122375
0.9105262756347656

0.9473683834075928
0.9210526943206787
0.8657894730567932
0.9210526347160339

0.8947367668151855
0.8210524916648865
0.8947367668151855
0.8684210181236267
0.7763158679008484
0.8684210181236267
0.8421053290367126
0.7315790057182312
0.8421052694320679
```

The setter input matched the vec3:

```text
0.9210526943206787
0.8657894730567932
0.9210526347160339
```

Again, this confirms that scale uses the same descriptor/sample-block system.

## 10. Scale `off14` appears sentinel-like for this record

For `Plane625-node-scale`:

```text
off14 = 0x17FC
```

Descriptor-like values:

```text
offC  + 0x24 = 0x000C00000000008D
off14 + 0x24 = 0xFFFFFFFFFFFFFFFF
```

So for this scale codec/record:

```text
offC is the active descriptor
off14 is sentinel/unused/terminator-like
tail is 0
```

This differs from some translation/rotation records where multiple offsets are meaningful.

## 11. Updated offline implementation target

Add a decoder helper like:

```python
def decode_descriptor_sample_vec3(data, record, ptr8, key, off, alignment=0x10):
    table_base = ptr8 + 4 + u32(data, ptr8 + 4)
    desc = u64(data, record + off + 0x24)

    row_index = desc & 0xFFFFFFFF
    base_offset = (desc >> 32) & 0xFFFF
    stride = (desc >> 48) & 0xFFFF

    idx = base_offset + stride * key
    row = table_base + row_index * 8
    data_rel = u32(data, row + 4)
    sample = row + data_rel + idx

    return vec3(data, sample + alignment)
```

For the confirmed live hits, `alignment = 0x10` matched both translation and scale observed setter values.

But because the disassembly directly reads `[sample + 4/8/C]`, the exact offline base/alignment should be validated per handler by comparing against live setter data. The safe implementation can scan nearby vec3 candidates in the sample block and pick the one that matches known live values during validation.

## 12. Current solved animation layers

Now solved:

```text
Runtime node TRS destination layout
Serialized node default TRS layout
Node vtable setter slots
Animation channel 0x28 record structure
Channel target naming: <node>-node-<property>
Generic handler/sampler path
Rotation raw quaternion + slerp helper
Translation/scale setter application
Plane### descriptor/sample-block decoder for single-key translation
Plane### descriptor/sample-block decoder for scale
```

Still unresolved / next:

```text
Exact offline alignment rule for descriptor sample blocks
Interpolated version of descriptor/sample-block handlers
Rotation descriptor/sample-block variants, if any
Mapping all runtime handler classes to codec names
Feeding decoded Plane### animation into the renderer
Comparing against full live playback
```

## 13. Recommended next step

Implement a small offline decoder for the descriptor/sample-block path:

```text
input:
  BDAE data
  track/source record table
  ptr8 stream
  key index
  channel record

output:
  sampled vec3
```

First test with known live cases:

```text
Plane635-node-translation at key 19:
  expected = -3470.14208984375, -95.8230209350586, 3224.494140625

Plane625-node-scale at key 23:
  expected = 0.9210526943206787, 0.8657894730567932, 0.9210526347160339
```

Once those match offline, use the decoder to animate Plane### translation/scale channels in the viewer.
