# Runtime Payload Arena Comparison

## Section-By-Section Size Breakdown

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse full file | Header `0x40`, relocation bytes `5592`, string bytes `5840`, root-gap bytes `288`, track-array bytes `2080`, post-track pre-data bytes `29048`, `runtime_payload_arena` bytes `1,182,472`. | Almost the entire Metal file volume lives in the post-record payload/object region beginning at `data_start`. | CONFIRMED | Keep assigning named record owners into this payload arena. |
| Crystal Lady full file | Header `0x40`, relocation bytes `6104`, string bytes `6072`, root-gap bytes `288`, track-array bytes `1720`, post-track pre-data bytes `31648`, `runtime_payload_arena` bytes `48,400`. | Crystal uses the same container layout, but with a much smaller post-record payload arena. | CONFIRMED | Keep using Crystal as the control sample for stable structure versus payload volume. |
| Metal vs Crystal delta | The total file-size gap is about `1,131,088` bytes. The payload-arena gap alone is about `1,134,072` bytes. All earlier sections differ only by a few hundred or a few thousand bytes. | The enormous size difference is overwhelmingly caused by the post-record payload arena, not by headers, strings, track-array metadata, or other record headers. | CONFIRMED | Focus deep payload analysis on `data_start..EOF`, not on strings/records. |

## Stable Sections Versus Variable Payload

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| both runtime samples | Both have `header_size=0x40`, the same relocation-table boundary rule, the same root-gap size `0x120`, the same track-array placement at `records_start + 0x10`, and the same `0x28` track stride. | The file format itself is stable. The huge difference is content volume inside the post-record payload arena, not a different container version. | CONFIRMED | Compare more runtime dragons to see whether this layout remains universal. |
| both runtime samples | Both have a small early transform-payload slice near the start of `data_start`, even though only Metal has a much larger tail beyond that. | The shared early payload-arena slice is consistent with compact transform payload storage; the large Metal-only remainder belongs to another payload class. | STRONGLY SUPPORTED | Trace non-track record owners that point deeper into the payload arena. |

## Shared Early Track-Payload Slice

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse track targets | Visible transform tracks currently point to relative payload-arena offsets roughly `0x0814..0x0C28` from `data_start=0xA7B0`. | The visible transform-track array only accounts for a small early slice of the large Metal payload arena. | CONFIRMED | Recover deeper non-track records and compare their target ranges. |
| Crystal Lady track targets | Visible transform tracks currently point to relative payload-arena offsets roughly `0x06AC..0x0A50` from `data_start=0xB358`. | Crystal shows the same early compact-payload pattern. | CONFIRMED | Use the same target-window logic on future samples. |
| both samples, track layout | For every currently recovered transform track, `outputRel - inputRel = 24`. For every track with non-zero `extraRel`, `extraRel - outputRel = 12`. | Track payloads appear to be arranged in tight fixed-size local groups, regardless of dragon. | CONFIRMED | Tie these fixed gaps to decoder-side structures before naming them as specific sample arrays. |

## Metal-Only Extra Tail

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal payload-arena bytes after the first `48,400` bytes | The Metal payload arena still has about `1,134,072` bytes remaining after the entire Crystal-sized payload-arena length. | This tail is the main source of the runtime size explosion. | CONFIRMED | Keep separating Metal-only payload from the shared early transform slice. |
| Metal extra tail start | The first 24 `u16` values in the Metal-only tail are `319, 320, 321, ... 342`, and more monotonic runs follow immediately. | The extra tail begins with index-buffer-like monotonic integer runs, not with obvious string or header data. | CONFIRMED | Search for surrounding count/offset records that describe these runs. |
| Metal extra tail overall | A scan found `1125` monotonic `u16` runs of length `>= 16`; the longest sampled run was length `252` from values `2930..3181`. | The extra tail contains a large amount of index-like structured integer data. | STRONGLY SUPPORTED | Look for neighboring vertex-weight or vertex-attribute tables. |
| Metal extra tail signatures | No `BRES`, `DDS `, or `DXT5` signatures were found in the Metal-only tail; there was also no `256`-byte all-zero block hit in the quick scan. | The extra tail is not simply a nested BRES or embedded texture container. | CONFIRMED | Keep treating it as native runtime payload rather than embedded secondary files. |

## Geometry-Like Float Evidence

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal `data_start = 0xA7B0` | The first 20 float triples are smooth position-like values such as `(16.3201, 22.9691, -0.000011)`, `(16.7028, 22.9006, -0.000011)`, ... `(18.3776, 16.1814, -0.000011)`. | The first payload-arena slice looks more like spatial point/vertex data than compressed keyframe metadata. | STRONGLY SUPPORTED | Check later records for explicit vertex-count or mesh-owner references. |
| Metal first triples | The sampled `z` component stays at approximately `-0.000011` while `x/y` change smoothly across adjacent triples. | This is consistent with a flat mesh strip or ordered vertex ring, not with arbitrary packed animation bytes. | STRONGLY SUPPORTED | Compare against other early payload-arena regions to see whether more vertex blocks exist. |
| Crystal data start | Crystal's initial payload-arena bytes do not show the same immediately human-readable float-triple pattern. | The shared format does not force every runtime to store the same early geometry layout in the same volume. | HYPOTHESIS | Recover more owning records before concluding that Crystal externalizes or omits comparable geometry. |

## Mesh-Owned Proof Inside The Blob

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Crystal mesh owner `0x8728` -> `stage0Abs=0xBD10` / `stage1Abs=0x10808` / `skinStageAbs=0x109C0`; Metal mesh owner `0x11DA18` -> `stage0Abs=0x120B08` / `stage1Abs=0x1250A8` / `skinStageAbs=0x125260` | In both runtime files, the record owning `dragon_crystal_lady002-mesh` or `METAL_SEAHORSE_-mesh` directly points into three deeper payload blocks with stable field positions and companion `-mesh-skin` ownership nearby. | The large post-record payload arena is now tied to concrete mesh-owned records, not just to generic late-file entropy. | CONFIRMED | Locate the executable-side reader for this mesh-owner record family. |
| Crystal stage-0 primary pointer `0xC098` (`+3392` from `data_start`); Metal stage-0 primary pointer `0x120DD8` (`+1140264`) | Both mesh-owned primary targets are float-rich interleaved regions. Crystal begins `-22.200249, 3.885846, -26.788742, FFFFFFFF, 0.037246, 0.594966, ...`; Metal begins `-22.372122, 3.816076, -27.454962, 0.934970, 0.193538, FFFFFFFF, ...`. | The strongest geometry-like float evidence is now mesh-owned rather than only payload-arena-global. | STRONGLY SUPPORTED | Prove the vertex stride and attribute meanings in code. |
| Crystal later stage-0 pointers `0xF908/0x10088/0x104F8/0x10738/0x10748`; Metal later stage-0 pointers `0x123F70/0x124CF0/0x124D00/0x124FE8` | These mesh-owned later targets contain dense small-integer tables, while the Metal tail additionally contains many long monotonic `u16` runs. | The index/topology-like evidence is also mesh-owned now, not merely a file-global coincidence. | STRONGLY SUPPORTED | Match one table to a draw primitive or submesh range in the mesh reader. |
| Crystal skin pointer `0x11AC8` and Metal skin pointer `0x126130` | These skin-owned targets contain repeating `(integer, weight, weight, 0, 0, ...)` style layouts. Companion secondary skin targets contain binding-like names such as `Dragon_center-node`, `eye_crystal_lady.tga`, and `Bone10`. | The payload arena also contains mesh-skin-owned weight/influence and binding-like metadata. | STRONGLY SUPPORTED | Confirm the exact skinning lane layout and binding table semantics in IDA. |

## What The Size Difference Most Likely Represents

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal-only extra tail plus mesh-owned stage pointers | The combination of mesh-owned float-rich primary stage targets, mesh-owned small-integer table targets, and mesh-skin-owned weight/binding-like targets is much more consistent with geometry/index/skin payload than with plain transform-track metadata. | The extra ~1.13 MB in Metal is now best modeled as mesh/skin-owned payload volume, with geometry/index data strongly favored and skin/binding data also present nearby. | STRONGLY SUPPORTED | Prove exact vertex/index/weight layouts through the executable-side mesh reader. |
| full runtime comparison | Crystal still contains a valid runtime track array and early track-payload slice despite being under `100 KB`. | The giant Metal size difference is not required just to store transform channels. | CONFIRMED | Do not model file size as a proxy for animation richness alone. |
| current evidence gap | The payload-arena ownership is now proven at the mesh/skin record level, but no executable-side proof yet assigns exact semantic labels such as `positions`, `UVs`, `indices`, `bone indices`, or `weights` to each subregion. | Static rendering is closer, but still blocked on concrete per-region layout proof. | NOT YET KNOWN | Locate the record type and loader code that consume the stage-0, stage-1, and skin-stage offsets. |
