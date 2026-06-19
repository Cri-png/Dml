# Animation Playback Bridge Verification - 2026-06-18

Read-only IDA pass on the currently open `DragonManiaLegends.exe.i64`.

## Scope

This pass focused on the missing playback pieces needed before patching the viewer toward cleaner shared body-type animation:

- clip/subclip time selection;
- lazy payload/window materialization;
- key index plus interpolation fraction selection;
- channel sample/blend dispatch;
- compact quaternion interpolation path;
- skinning matrix/palette composition evidence.

## IDA Access

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| IDA MCP instance | Active reachable instance: `DragonManiaLegends.exe`, IDB `C:\Users\crist\Downloads\DragonManiaLegends.exe.i64`, imagebase `0x7FF720730000`, Hex-Rays ready. | Static read-only verification was possible. | CONFIRMED | Continue to avoid renames/comments/types until explicitly approved. |

## Clip And Segment Cache

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209FBC20` | Builds a selected clip/window tuple, clamps the incoming time to selected entry `+0x08/+0x0C`, then calls `0x7FF7209F2F90(qword_7FF722E9E500, tuple, a1+0x80)`. | Runtime playback does not sample rows directly from the whole BDAE timeline. It first selects and clamps a clip/window. | CONFIRMED | Match one named clip entry from `dragon_gorillabody_anim.bdae` to the tuple fields. |
| `0x7FF7209F2F90` | Compares the existing cached object at `*a3` against tuple fields: clip container, selected entry, and clamped time/range. If invalid, calls `0x7FF7209F2DE0` and replaces the cached pointer. | This is a current playback cache updater keyed by clip container, clip entry, and clamped time. | CONFIRMED | Dump cache object fields from a live run later if dynamic inspection becomes allowed. |
| `0x7FF7209F2DE0` | Searches a sorted cache; if no match, allocates `0x58` bytes and calls `0x7FF7209F2410(newNode, clipContainer, selectedEntry, clampedTime)`. | The evaluator uses reusable `0x58` segment/cache nodes rather than rebuilding every time. | CONFIRMED | Identify all fields of the `0x58` node from consumers. |
| `0x7FF7209F2410` | Initializes the cache node, stores selected entry at `+0x30`, calls `0x7FF720952E70(resource, clampedTime)`, stores the returned descriptor at `+0x38`, and lazily materializes payload through `0x7FF7209EB180` when needed. | This is the bridge from clip time to selected segment/sample descriptor. | CONFIRMED | Use the descriptor returned by `952E70` as the next offline model target. |
| `0x7FF7209529E0` | Reads table anchor at `resourceBase + 0x40`; returns `resourceBase + 0x40 + rel + 40*index + 4`. | Root `+0x40/+0x44` is an engine-consumed `0x28` playback target/evaluator table. It is distinct from both the segment table and the named clip table. | CONFIRMED | Expose this table in the shared-animation inspector and use it as the canonical named target table. |
| `0x7FF720952E70` | Reads table anchor at `resourceBase + 0x4C`; table has count then `40`-byte entries; binary-searches records using time data and returns `&table[10*i+1] + table[1]`. | Segment/sample descriptor records are `0x28` / `40` bytes, distinct from the named `0x18` clip table and the `+0x40` playback target table. | CONFIRMED | Model this table as the segment/materialized-payload selector above row sampling. |

## Lazy Payload Materialization

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209EB180` | If descriptor `+0x18` is empty, computes `pointerBytes = 8 * s16[+4]`, `payloadSize = dword[+0x10] - pointerBytes`, `payloadOffset = dword[+0x08] + pointerBytes`, allocates payload, and calls source vtable slot `[2]` to copy bytes. If `s16[+4] > 0`, it also reads a pointer table and fixes relative pointers into the new payload. | Animation segment data is lazily materialized from byte windows and can include a leading relative-pointer table. | CONFIRMED | Update offline decoder to model descriptor windows before interpreting row samples. |
| `0x7FF7209F3320` | Creates a small source wrapper with vtable `off_7FF722D3D900`, then calls `0x7FF7209F3490`. | `9EB180` receives a source interface, not raw file bytes. | CONFIRMED | Track the source wrapper's underlying stream object. |
| `0x7FF7209F3490` | Reads desired window fields from `a2+0x38/+0x3C`; if needed, creates an `"onDemand"` object through `0x7FF720986D20`, otherwise keeps the existing source. | Source objects are window-aware. | CONFIRMED | Compare window start/end with file-side descriptor offsets. |
| `0x7FF720986D20` and `0x7FF7209870E0` | The on-demand stream stores current start at `+0x58`, end at `+0x5C`, cursor at `+0x68`, and wrapped stream pointer at `+0x60`. | On-demand wrapper represents a bounded byte range over another stream/source. | CONFIRMED | Use these fields when naming a future temporary struct, after approval. |
| `off_7FF722D3D900 + 0x10 -> 0x7FF7209F35F0` | Slot `[2]` seeks the wrapped source to `a3`, then reads `a2` bytes into the destination. | This is the byte-copy method used by `9EB180` for the source wrapper. | CONFIRMED | Confirm all caller families use the same slot signature `(size, offset, dst)`. |
| `off_7FF722D3C208 + 0x10 -> 0x7FF7209AB910` | Wrapper slot `[2]` does `memcpy(dst, base + offset - start, size)`. | When data is already buffered, the same interface reads from memory. | CONFIRMED | Keep this as a simple source-memory variant in notes. |

## File-Side Correlation Attempt

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_gorillabody_anim.bdae` `stringsEnd/root = 0x4790` | Root-like record has `+0x40 = 69`, `+0x44 = 236`, `+0x48 = 7008`, `+0x4C = 7660`, `+0x54 = 33`, `+0x58 = 841912`, `+0x5C = 33`, `+0x60 = 842696`. | Shared anim root has the same count/relative table style as runtime BDAEs, plus two `33`-entry named-clip-like table pointers. | CONFIRMED | Split the root fields into named clips, track-array owners, and segment/sample owners. |
| root `+0x40/+0x44` at `0x47D0` | `count=69`, `rel=236`, raw table starts at `0x48BC`, and `0x7FF7209529E0` returns entries at `0x48C0 + index*0x28`. Entry names include `textureOffset`, `textureOffset1`, `textureOffset2`, then transform targets such as `body_root-node-translation`, `Tail_bone01-node-rotation`, and `head_ctrl-node-rotation`. | This is not the segment table, but it is playback-relevant: it is the engine-consumed named target/evaluator descriptor table. | CONFIRMED | Patch the inspector to print this table separately from legacy track scans. |
| root `+0x58` | `0x4790 + 0x58 + 841912 = 0xD20A0`, matching the known `33 x 0x18` named clip table. | The named clip/state table pointer is now file-side tied to root fields. | CONFIRMED | Keep exposing this table in the viewer's animation-state picker. |
| root `+0x4C` | `0x4790 + 0x4C + 7660 = 0x65C8`. The table has `count=1`, `rel=4`; `0x7FF720952E70` returns record `0x65D0`. Record fields are `(0, 98067, 1, 0, 24, 0, 834216, 0, 0, 0)`. The returned payload descriptor at `0x65D8` gives `pointerCount=0`, `payloadOffset=24`, `payloadEndOrSize=834216`, `wrapperSize=0`, matching the field pattern consumed by `0x7FF7209EB180`. | Root `+0x4C` is the full-animation segment/materialized-payload table for this shared anim resource. The one segment covers the root duration `0..98067`. | STRONGLY SUPPORTED | Clarify the source-window base used by `9EB180`; direct file offset `24` is source-relative, not necessarily a final raw-file offset. |
| `head_ctrl-node-rotation` `+0x40` entry | Entry `32` returns at `0x4DC0`, name pointer `0x2700`, output subdescriptor target `0x5AEC`, and time/mode/value fields `(64, 6, 4, 65, 0x00100000, 10012, 0, 5)`. | The named rotation target maps to time row `64`, value kind `4`, value row `65`, stride `16`, key count `6`, matching the earlier offline `stride=16,row=0x41` descriptor. | CONFIRMED | Follow the cooked runtime object for this same target to the concrete rotation evaluator vtable. |
| `body_root-node-translation` `+0x40` entry | Entry `6` returns at `0x49B0`, name pointer `0x21D0`, output subdescriptor target `0x54FC`, and time/mode/value fields `(12, 6, 3, 13, 0x000C0000, 8688, 0, 1)`. | The named translation target maps to time row `12`, value kind `3`, value row `13`, stride `12`, key count `6`, matching the earlier offline vec3 descriptor. | CONFIRMED | Compare against the local-translation sink family at receiver `+0x168`. |

## Key-Time Sampling And Interpolation

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209F9CF0` | Takes a live `float` time, calls `0x7FF7209FBC20`, calls `0x7FF7209B51D0` to get an integer key index and float interpolation fraction, then dispatches per-target evaluator methods. | This is a real runtime evaluator path, not just load-time transform construction. | CONFIRMED | Tie one ordinary track object to this function through its vtable. |
| `0x7FF7209B51D0` | Dispatches by `*(dword *)(*(int *)(*a1 + 0x0C) + *a1 + 0x10)`, with cases `1..4`, and returns `{keyIndex, fraction, valid}`. | The 40-byte segment/sample record selects one of four compact time encodings. | CONFIRMED | Map case values to the file-side time descriptor bytes for multiple shared anims. |
| `0x7FF7209B4410` | Case 1 reads `u8` key times and scales by `33.333332`. | Time mode 1 uses 8-bit time samples. | CONFIRMED | Find a track using case 1 in another asset. |
| `0x7FF7209B46E0` | Case 2 reads signed `i16` key times and scales by `33.333332`. | Time mode 2 uses signed 16-bit time samples. | CONFIRMED | Find a track using case 2 in another asset. |
| `0x7FF7209B49B0` | Case 3 reads unsigned `u16` key times and scales by `33.333332`. | Gorilla shared anim ordinary rows using mode 3 are sampled as `rawTime * 33.333332`. | CONFIRMED | Keep this as the default for current `dragon_gorillabody_anim.bdae`. |
| `0x7FF7209B4C60` | Case 4 reads `i32` key times without the small integer loads used in cases 1-3. | Time mode 4 uses 32-bit time samples. | CONFIRMED | Find a track using case 4 and compare units. |
| `0x7FF7209B51D0` cache branch | If cache byte at `a1[2]+0x0D` is set and incoming float time is unchanged, it reuses cached index/fraction/valid. | Runtime sampler caches the last time result. | CONFIRMED | Viewer does not need this for correctness, but it explains repeated-call performance behavior. |

## Channel Sample/Blend Dispatch

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209F9CF0` | If interpolation is active, calls downstream method at vtable `+0x68` with `(key, key+1, fraction, sink, output)`. If not, calls vtable `+0x60` with `(key, sink, output)`. It also has a special/bulk path at vtable `+0x88`. | Runtime channel evaluation distinguishes direct sample, blended sample, and special/bulk update paths. | CONFIRMED | Resolve one ordinary rotation evaluator vtable instance and compare its `+0x60/+0x68` methods. |
| `0x7FF72094D090` | Initializes an identity quaternion, calls `0x7FF72095DA10(a2, keyA, keyB, t, &tmp)`, then forwards `tmp` to receiver virtual `+0x158` (`344`). | This is a blended compact-quaternion local-rotation output wrapper. | CONFIRMED | Tie `head_ctrl-node-rotation` or another ordinary rotation row to this wrapper. |
| `0x7FF72095DA10` | Builds pointers to packed quaternion row data, computes weights `[1.0 - t, t]`, calls `0x7FF7209517B0`, then calls `0x7FF720955D60`. | Compact quaternion interpolation is selected at runtime through key index plus blend fraction. | CONFIRMED | Confirm exact packed row layout for one ordinary rotation row in the shared anim file. |
| `0x7FF7209517B0` | Reads packed quaternion-like data and computes the missing component through a `sqrtf` path. | This is the current-build equivalent of the compact quaternion decode path. | CONFIRMED | Keep comparing decoded offline quaternions against this formula. |
| `0x7FF720955D60` | Uses `acosf`, `sinf`, `sqrtf` and multiple callers; in the `95DA10` path it receives two decoded quaternions and two weights. | This is a quaternion/vector blend-normalization helper used by runtime animation output. | CONFIRMED | Compare output against viewer's quaternion interpolation, including sign/hemisphere handling. |

## Skinning Matrix Composition

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF720A5D360..0x7FF720A5D397` inside `0x7FF720A5CED0` | Reads count at `[object+8]+0x50`, computes `count << 6`, allocates/stages `count * 64` bytes. | Skinning/deformation path uses 64-byte matrix palette entries. | CONFIRMED | Match this count to Tiki's 24 captured skin matrices. |
| `0x7FF720A5D3C0..0x7FF720A5D763` | Loop iterates palette entries, reads a node/source matrix pointer from `[object+0x10]`, composes/transforms 4 rows, and writes four 16-byte vectors to the output palette at offsets `+0x00/+0x10/+0x20/+0x30`. | Palette entries are full 4x4 matrices; the engine composes them before vertex skinning. | CONFIRMED | Mirror this exact composition order offline instead of using ad hoc branch-mix fixes. |
| `0x7FF720A5F0F0` | Transforms a point by a 4x4 matrix: `x' = m0*x + m4*y + m8*z + m12`, `y' = m1*x + m5*y + m9*z + m13`, `z' = m2*x + m6*y + m10*z + m14`. | Matrix convention is column-basis with translation in float slots `12..14` for point transforms. | CONFIRMED | Audit viewer matrix multiplication against this exact convention. |
| `0x7FF720A48D70` | Same multiply without translation. | Used for vector/direction parts of palette composition. | CONFIRMED | Apply no-translation transforms for basis rows/axes, not for positions. |
| `0x7FF722D3BAF0` | 64 bytes decode to identity matrix `diag(1,1,1,1)`. Fallback path writes these four rows when no source matrix is present. | Default palette entry is identity. | CONFIRMED | Viewer fallback for missing helper/node matrix should use identity, not zero. |

## Viewer Implications

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Current clean static viewer | Static meshes render correctly when skinning is disabled. | Static body render remains the safe baseline. | CONFIRMED | Keep static preview as default GUI behavior. |
| Current experimental playback | Existing GIFs use descriptor-row JSON and partial palette reconstruction, not the full segment/cache/evaluator path above. | Current animation display is diagnostic, not engine-equivalent. | CONFIRMED | Patch playback in stages: clip table selection, segment descriptor selection, direct/blend channel dispatch, then palette composition. |
| Deformation bug | IDA proves 64-byte palette matrices and exact point/vector transform conventions. | Crushed/deformed outputs are most likely matrix-space/composition or clip/evaluator selection errors, not mesh vertex/index parsing errors. | STRONGLY SUPPORTED | First patch should audit matrix convention and disable experimental skinning unless engine-path mode is selected. |

## Current Deformation Blocker - 2026-06-18 Follow-Up

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_gorillabody_anim` frame exports | The shared animation exports `52` transform nodes for Tiki's resolved body family. The current viewer maps only `21` of those to Tiki's `24` skin palette slots. | Slot-direct playback is incomplete by construction. | `CONFIRMED` | Evaluate the full named node hierarchy and only then build the final palette. |
| skipped node inventory | The unmapped `31` include `body_root-node`, IK chains, `leg*_IK-node`, `leg*_heel_roll-node`, `leg*_toe_roll-node`, `wingL/R*`, and helper/food nodes. | These are likely controller/parent nodes whose transforms should flow to deforming slots through the scene graph. | `STRONGLY SUPPORTED` | Recover BRES parent links or the runtime source-matrix pointer list feeding `0xA60020`. |
| `0x7FF720A60020` exact lane reads | The per-slot `64`-byte table is read at offsets `+4/+8/+12`, `+20/+24/+28`, `+36/+40/+44`, `+52/+56/+60`, then combined with the current source matrix pointer. | The raw bind/source table is not the same artifact as the final captured palette. Correct playback needs this source mapping, not only a dumped rest-pose palette. | `CONFIRMED` | Locate the source/cooked table and compare slot 0 against `tiki_auto_24_skin_matrices.bin` under rest pose. |
| row-vector order comparison | The decompiled arithmetic is compatible with `bind_or_inverse_bind @ current_source_world`; the viewer's current `captured_skin @ inverse(rest_world)` solve is consistent with that order. | The remaining bug is unlikely to be solved by flipping matrix multiplication order alone. | `STRONGLY SUPPORTED` | Stop chasing transpose-only fixes; focus on full hierarchy/source matrices and raw slot-table recovery. |

## Current Bottom Line

The playback bridge is now much more concrete:

```text
named clip/state
  -> selected clip window
  -> clamped time
  -> 40-byte segment/sample descriptor
  -> lazy byte-window materialization
  -> time decoder case 1..4
  -> key index + interpolation fraction
  -> direct or blended channel evaluator
  -> local TRS sink
  -> 64-byte skinning palette composition
```

What is still unresolved:

- exact file-side location of the 40-byte segment/sample descriptor table for the current shared anim;
- one named ordinary track, such as `head_ctrl-node-rotation`, proven end-to-end into a concrete evaluator object;
- exact final palette composition inputs for Tiki's helper hierarchy;
- production-safe material/eye/effect pass assignment.

## Segment Window Correction - 2026-06-18 Follow-Up

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209FBC20` | The temporary lookup tuple is exactly `v22 = resource/root`, `v23 = selected clip entry`, `v24 = clamped integer live time`. The clamped time is bounded by selected entry fields `+0x08/+0x0C`. | The selected clip is part of the segment-cache key, but there is no simple local-time subtraction here. | `CONFIRMED` | Keep viewer timing modes labeled diagnostic until the segment payload sampler is reproduced. |
| `0x7FF7209F2410` | Calls `0x7FF720952E70(resource, clampedTime)`, stores returned segment record at object `+0x38`, then calls `0x7FF7209EB180(segmentRecord + 8, sourceInterface, 1)`. | The payload descriptor passed to the materializer begins at returned segment record `+8`. | `CONFIRMED` | In the offline model, parse segment record fields from `returnedOffset + 8`, not from the record start. |
| `0x7FF7209F9CF0` | Saves incoming float time in `xmm7`; after `0x9FBC20` returns a materialized payload pointer, it passes `xmm7` unchanged as `xmm3` into `0x9B51D0`. | The row sampler sees original live time plus the materialized payload. The missing layer is the payload/source-window and row-indirection model. | `CONFIRMED` | Do not implement final playback as `sampleTime = liveTime - clipStart` unless later code proves it elsewhere. |
| `0x7FF7209EB180` | Copies from source offset `dword[descriptor+8] + 8 * s16[descriptor+4]`; for Gorilla's segment descriptor at `0x65D8`, this is source offset `24` and size `834216`. | The source offset is relative to the source interface/window, not the whole raw `.bdae` file. | `CONFIRMED` | Reproduce the source window before interpreting payload bytes. |
| `dragon_gorillabody_anim.bdae` candidate source window | `inspect_animation_time_remap.py` found candidate `sourceBase=0x6238`, making materialized payload start `0x6250`; dword at `0x6250` is `2`, dword at `0x6254` is relative table offset `4`, table base is `0x6258`, and payload end `0xD1CF8` is inside the file. A later row sanity check shows known rows `64/65` do not decode correctly through that apparent table. | This still explains why raw file offset `0x18` was wrong, but `0x6250` should be treated as a candidate materialized-object header, not a solved row-table base. | `STRONGLY SUPPORTED` for header shape, `CONFIRMED` that row decoding is not solved | Find the missing source-window/object indirection before implementing an `engine-window` exporter. |
| `0x7FF7209B49B0` / `0x7FF7209B3EF0` | Mode-3 sampler receives a row descriptor pointer, divides live time by `33.333332`, compares against `u16` key times at `row + 4 + s32[row+4]`, then computes key index and interpolation fraction. | Existing row decoding logic is directionally right, but the row descriptor pointer must come from the materialized payload view used by the engine. | `CONFIRMED` | Re-run clip signature diagnostics after switching row source from raw table scanning to engine-window payload indirection. |

## Evaluator Family Correction - 2026-06-18

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| evaluator-family vtable block `0x7FF722D333B0`, aligned vptr `0x7FF722D333C8` | Slot `+0x60` is `0x7FF72094CFA0`; slot `+0x68` is `0x7FF72094CF20`. These are exactly the virtual slots used by `0x7FF7209F9CF0` for direct and blended target output. | One concrete per-channel runtime evaluator family is now mapped at the vtable level. | `CONFIRMED` | Find which cooked descriptor selects this family. |
| `0x7FF72094CFA0` | Reads descriptor `valueDescriptorQword`, derives row index/base offset/stride, reads three float-like components, reconstructs a fourth component via sqrt, and calls receiver `+0x158`. | This family is not a raw full-XYZW quaternion row reader. | `CONFIRMED` | Do not globally interpret every rotation row with this function until the family selector is known. |
| `0x7FF72094CF20 -> 0x7FF72095D7B0` | Blended path decodes two reconstructed quaternion samples and calls the quaternion blend helper before receiver `+0x158`. | Runtime rotation playback performs descriptor-driven key interpolation. | `CONFIRMED` | Compare with viewer quaternion interpolation after the target-family bridge is known. |
| sibling vptrs `0x7FF722D334B0`, `0x7FF722D336D8`, `0x7FF722D33788` | These expose different direct/blended rotation methods at the same `+0x60/+0x68` slots. | Rotation tracks can use multiple runtime evaluator families. | `CONFIRMED` | Recover the cooked descriptor selector/table writer to choose the right family offline. |
| raw diagnostic row table `0x6604` | `head_ctrl-node-rotation` raw row `65` still validates as full-looking XYZW floats through the old diagnostic formula. | The existing keyframe exporter remains useful for diagnostics, but it is not yet proven engine-equivalent for every target. | `STRONGLY SUPPORTED` | Bridge `head_ctrl-node-rotation` from raw target entry to its cooked evaluator object. |
| payload candidate `0x6250` | Sanity-checking known rows through `payload + 4 + s32[payload+4] + row*8` produces invalid previews for rows such as `64/65`. | The `0x6250` candidate should not be used as a final row table in the viewer. | `CONFIRMED` for failed row sanity check | Locate the relocated/materialized view or additional source-window transformation before implementing `engine-window` playback. |

## Target-Index List Refinement - 2026-06-19

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209FC0C0` | Helper selects one of three 16-bit-list owner fields from a playback object based on mode byte/dword at object `+0x58`: mode `0` returns `object+0x30`, mode `1` returns `object+0x38`, mode `2` returns `object+0x40` when `qword[object+0x20]` is non-zero, otherwise falls back to `object+0x30`. | Playback has explicit target-index list slots. The selected list is not the same as the load-time `0x18` string descriptor table. | `CONFIRMED` | Find the constructor/populator that fills object `+0x30/+0x38/+0x40`. |
| `0x7FF7209F9CF0` | After `0x7FF7209B51D0` returns key index/fraction, the loop reads `u16 targetIndex = *listCursor`, then uses that same value to index arrays at playback object `+0x78`, evaluator/receiver arrays at `+0x90`, a target-state/bitmask path, and target-table-like data rooted from another playback structure. | The 16-bit list entry is used directly as a playback target index, not merely as a local row number. | `CONFIRMED` | Prove that one selected list contains index `32` for `head_ctrl-node-rotation`. |
| `0x7FF7209F90F0` | A separate traversal selects the same list slot family, reads each `u16 targetIndex`, and directly indexes `(*a3)[15] + 8*targetIndex`, `(*a3)[14] + 2*targetIndex`, and a receiver/target collection using the same index. | Independent confirmation that list values are direct target indices shared across playback helpers. | `CONFIRMED` | Map `(*a3)[14]`, `(*a3)[15]`, and receiver lookup results back to the root `+0x40` target table. |
| `dragon_gorillabody_anim.bdae`, target entry index `32` | File-side exported table maps root `+0x40` entry index `32` to `head_ctrl-node-rotation`, entry offset `0x4DC0`, subdescriptor `0x5AEC`, time row `64`, value kind `4`, value row `65`, stride `16`, key count `6`. | If any per-frame target-index list contains `32`, the engine target selected by that list is `head_ctrl-node-rotation`. | `CONFIRMED` for target-table identity, `STRONGLY SUPPORTED` for direct playback mapping | Locate the concrete selected list contents or recover its file-side owner. |
| local unaligned `u16` scans of `dragon_gorillabody_anim.bdae` | Many plausible small-integer runs contain value `32`, including runs near `0x14608` and `0xC6520`, but these runs are not yet tied to the `+0x30/+0x38/+0x40` playback list owner. | Static byte scanning is useful for candidates only; it does not prove the selected runtime list. | `HYPOTHESIS` | Follow object construction for the `+0x30/+0x38/+0x40` fields before using any candidate run in the viewer. |
| `0x7FF7209F29C0` | Maintains a separate `0x18`-stride vector/cache of segment records, with fields including an integer, a materialized/cache object pointer, and a string/label pointer. | This side table belongs to segment/cache management and should not be conflated with the 16-bit target-index lists. | `CONFIRMED` | Keep segment-cache inspection separate from target-index-list decoding in tools and reports. |

Current bridge status after this refinement:

```text
head_ctrl-node-rotation
  -> root+0x40 target index 32                CONFIRMED
  -> per-frame lists use direct u16 indices   CONFIRMED
  -> selected list contains 32                NOT YET KNOWN
  -> evaluator object/vptr for target 32      NOT YET KNOWN
```

## Runtime Target/Evaluator Construction - 2026-06-19 Follow-Up

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209B0950` | Allocates `0x98` bytes, calls virtual interface methods at `+0xC8`, `+0x90`, and `+0x88`, then calls `0x7FF7209FCE50(newObject, a3, a4, a5, v13, v12, v11, 0)`. | `9FCE50` is a constructor/initializer for a `0x98` track/blender/evaluator-container object. It is not the same object as the playback-state structure whose selected u16 lists live at `+0x30/+0x38/+0x40`. | `CONFIRMED` | Trace the concrete interface receiver used by `9B0950` to identify the serialized/materialized blob source passed as `a4/a5`. |
| `0x7FF7209FCE50` | Initializes base object, sets vtable block `off_7FF722D3E4F8`, creates a vector at object `+0x58/+0x60/+0x68`, stores `a4` at object `+0x78`, and copies bounds-like fields into object `+0x80..+0x94`. | This object owns a vector of per-target evaluator objects, but it should be documented as a track/blender/evaluator container rather than the root playback state. | `CONFIRMED` | Compare the vector length after construction with the materialized target count. |
| `0x7FF7209FCE50`, materialized payload path | After `0x9EB180`, it uses materialized pointer `v92/v23`. It reads `targetCount = dword[v92+0x58]`, `targetRecordRel = s32[v92+0x5C]`, and loops `targetIndex = 0..targetCount-1`. Each record address is computed as `v92 + 0x58 + targetRecordRel + 0x58 * targetIndex`. | The engine-side target/evaluator record array is `0x58` / 88 bytes per target. This is a separate cooked/materialized table, not the raw root `+0x40` table itself. | `CONFIRMED` | Find the file-side/window-relative bytes for this materialized table and compare record index `32` with `head_ctrl-node-rotation`. |
| `0x7FF7209FCE50`, per-target loop | For each `targetIndex`, it reads record-relative data at offsets including `+0x2C`, `+0x3C`, `+0x4C`, and `+0x54`; it allocates `0x48` bytes and calls `0x7FF7209D7600(newEvaluator, v92, targetIndex, a8)`. If a flag is set, it stores the evaluator pointer back into the record at a record-relative cached slot. | Each materialized target record produces one `0x48` per-target evaluator/descriptor object. | `CONFIRMED` | Resolve the vtable/family assigned by `9D7600` or by its nested helper for target index `32`. |
| `0x7FF7209D7600` | Computes the same 88-byte target record as `record = base + s32[base+0x5C] + 0x58 + 0x58*targetIndex`. It reads kind/index-like data from the record, looks up `dword_7FF7228019F8[...]`, reads a range using fields equivalent to `record+0x20/+0x24`, stores resulting count at evaluator object `+0x2C`, stores a pointer/ref at object `+0x18`, and builds an auxiliary descriptor via `0x7FF7209D7F50`. | This is the concrete per-target evaluator/descriptor constructor fed by the 88-byte materialized target table. | `CONFIRMED` | Decode the 88-byte target-record fields offline and align them with known root target entries such as index `32`. |
| `0x7FF7209D7F50` | Builds a `24`-byte component descriptor at `dest + 24*componentSlot`. It reads four component-indexed arrays from the materialized payload: `s32[payload+0x0C]`, `s32[payload+0x14]`, `s32[payload+0x1C]`, and `s32[payload+0x24]`. It stores qword `payload+0x50` into descriptor `+0x00`, stores a computed dword offset at `+0x08`, dword at `+0x0C`, byte at `+0x10`, zero byte at `+0x11`, and word at `+0x12`. | The per-target evaluator object contains compact 24-byte component descriptors built from materialized shared arrays. This is a concrete schema layer below the 88-byte target record. | `CONFIRMED` | Identify which component slots are requested for translation versus quaternion rotation and compare descriptor fields to evaluator-family row access. |
| `0x7FF7209D7600`, calls to `9D7F50` | The constructor looks up component-map entries from each 88-byte target record. It first searches code `0`, then optional codes `4..16`, code `1`, codes `2..3`, codes `22..25`, codes `18..21`, code `26`, and code `27`; each found code supplies a byte selector passed into `9D7F50`. It accumulates a bitmask in `v13`. | Target records contain a compact component map from semantic/component codes to materialized component-array slots. | `CONFIRMED` | Locate materialized target record `32` and inspect which component codes it exposes. |
| `dword_7FF7228019F8` | First six dwords at this global table are `6, 4, 3, 1, 2, 0`; later bytes contain repeated small permutation tables. `9D7600` indexes the first dword table using a materialized target-record kind/index field. | There is an executable-side remap from materialized target kind to an internal component/category id. | `CONFIRMED` for bytes and lookup use, `NOT YET KNOWN` semantically | Determine whether raw `value kind 4` maps through this table or whether the materialized target record has its own kind field. |
| `0x7FF720A03EA0` | Emits the error string `A CSceneNodeAnimatorTrackBlender can't be evaluated...`, selects a target-index list from the playback state using mode at `state+0x58`, passes the list payload to `0x7FF720A04C20`, then iterates `u16 targetIndex` values from the selected list. | This is a second apply path for a track blender and independently confirms that per-frame work is target-index-list driven. | `CONFIRMED` | Determine which UI/clip condition enters this blender path versus `9F9CF0`. |
| `0x7FF720A38920` | Receives a `targetIndex`, obtains a receiver object by calling the target collection at `state+0x48` with that index, reads per-target data from `state+0x78`, optionally calls a callback/evaluator function from `state+0x20 + 0x70 + 8*targetIndex`, otherwise calls receiver virtual `+0x80`. | One non-blended apply helper maps the same u16 target index into receiver, per-target state, callback/evaluator, and output arrays. | `CONFIRMED` | Identify receiver virtual `+0x80` for rotation/translation/scale sink equivalence. |
| `0x7FF720A387A0` | Receives a `targetIndex`, obtains the target receiver through `state+0x48`, reads per-target state from `state+0x78`, looks up optional callback/evaluator at `state+0x20 + 0x70 + 8*targetIndex`, and otherwise calls receiver virtual `+0x38/+0x40` depending on a blend flag. | This is a blended apply helper using the same direct target-index mapping. | `CONFIRMED` | Compare helper output with the `+0x60/+0x68` evaluator-slot path in `9F9CF0`. |
| `dragon_gorillabody_anim.bdae`, broad static scan | A naive scan for `count at +0x58`, `rel at +0x5C`, `88-byte records` finds many false positives because ordinary BRES root tables and clip tables also match count/relative-offset patterns. The old `0x6250` candidate has `count@+0x58 = 1`, `rel@+0x5C = 3`, which is not the expected per-target table for the whole shared animation. | The 88-byte materialized target table is not yet safely located by raw scan alone. The viewer should not wire playback to the `0x6250` row-table candidate as if it were the target/evaluator table. | `CONFIRMED` for failed raw match, `NOT YET KNOWN` for exact file-side materialized table | Trace the source/window object used by `9EB180` in the `9FCE50` constructor path, or later dump the live materialized pointer if dynamic inspection becomes allowed. |
| `viewer_prototype/inspect_materialized_target_candidates.py` on Gorilla, `--expected-count 69 --target-index 32` | The stricter component-map scan produced one raw-file match: payload base `0x4778`, record0 `0x48BC`, i.e. the known root `+0x40` raw target table. It scored poorly (`-369`) and target index `32` had `componentMap.mapCount = 0`. | This is useful negative evidence: the engine's materialized 88-byte target/evaluator table is not the raw root `+0x40` table reinterpreted with component-map fields. | `CONFIRMED` for this scan result | Continue tracing materialization/source-window setup; keep the script as a regression diagnostic for future candidates. |

Current refined bridge status:

```text
head_ctrl-node-rotation
  -> raw/shared root target index 32                  CONFIRMED
  -> materialized target table uses 88-byte records    CONFIRMED
  -> per-target evaluator object is 0x48 bytes         CONFIRMED
  -> u16 playback lists use direct target indices      CONFIRMED
  -> materialized record index 32 equals head_ctrl     STRONGLY SUPPORTED, not yet proven
  -> target index 32 evaluator vtable/family           NOT YET KNOWN
```

## Source-Record Cooker Bridge - 2026-06-19 Follow-Up

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML MCP health | Read-only MCP health probe confirms `DragonManiaLegends.exe.i64`, imagebase `0x7ff720730000`, Hex-Rays ready, strings cache ready. | Evidence below is from the expected currently open database. | `CONFIRMED` | Continue read-only unless explicit IDA mutation permission is granted. |
| `0x7FF7209B0A90` | Allocates `0x238` bytes, zeroes it, calls `0x7FF7209B5B50(newObj, a3, a5, a6, a7, 1)`, stores the result through `a2`, then calls `0x7FF7209B3580(a1, a3, a4, a5, a2)`. | This is a high-level source/runtime animation-object construction entry. | `CONFIRMED` | Identify its vtable/data-reference caller to name the asset/object class later. |
| `0x7FF7209B5B50` | Initializes the `0x238` object, assigns vtables including `off_7FF722D3C618`, `off_7FF722D3C820`, `off_7FF722D3C830`, and `off_7FF722D3C840`, stores `a3` at object `+0x1B0`, stores `a4` at `+0x1C8`, stores `a5` at `+0x1E8`, copies `*a3` to object `+0x178`, and copies string/name `a3[1]` through `0x7FF72092E9E0`. | The object keeps a serialized/source record pointer at `+0x1B0` and carries a name/string copied from the source. | `CONFIRMED` | Compare `a3` with a BRES record owning animation/source names. |
| `0x7FF7209B3580` | Reads byte `source+0x68`. Case `0` follows a relative pointer at `source+0x6C`, chooses mode `0x10003` or `0x18003` from the referenced byte `+3`, and calls `0x7FF7209B7920`. Case `1` follows `source+0x6C`, resolves a named referenced object through `0x7FF72094E7D0`, then calls `0x7FF7209B7920` with mode `0`. Case `2` calls `0x7FF7209B7920` with mode `0x10003`. | The serialized source record has an explicit mode byte at `+0x68` and a relative/reference field at `+0x6C`; this is upstream of the broad runtime-object cooker. | `CONFIRMED` | Locate these source records in shared animation BDAEs and classify cases `0/1/2`. |
| `0x7FF72094E7D0 -> 0x7FF720956C10 -> 0x7FF72094E1F0` | `94E7D0` resolves a name/reference by calling `956C10(a1, a4)`, then passes the resolved record to `94E1F0`. `956C10` searches a 24-byte-entry string table with count at resource-relative `+0xA4` and relative table at `+0xA8`, using `strcmp(*entryName, requestedName)`. `94E1F0` rejects null records and records with `dword[record+0x10] != 0`, otherwise calls a virtual builder at receiver slot `+0xF8`. | Case `1` source records can resolve another named resource/subobject before cooking. The builder interface is real, but the concrete implementation is not yet identified. | `CONFIRMED` | Resolve the concrete receiver/vtable passed to `94E1F0`; do not assume it is the `0x238` object's `off_7FF722D3C820` slot. |
| negative check for `94E1F0` virtual slot | Reading `off_7FF722D3C820 + 0xF8` gives `0x7FF7209B4E80`, but `94E1F0`'s receiver is not proven to be the object initialized with `off_7FF722D3C820`. `0x7FF7209B4E80` itself calls `0x7FF7209B51D0` and then dispatches to virtual slots `+0x60/+0x68`, matching evaluator-apply behavior rather than named-resource building. | Earlier suspicion that the `+0xF8` builder might be `0x7FF7209B0950` is not proven and should not be used. The vtable slot check is useful negative evidence. | `CONFIRMED` for the slot bytes and `9B4E80` behavior, `NOT YET KNOWN` for the actual `94E1F0` builder implementation | Trace the concrete `a1` object passed into `94E1F0` from its callers, especially `9B3580`, `9EAEF0`, and `9F5BB0`. |
| `0x7FF7209B7920`, prologue and first cooker stage | Stores/updates reference at object `+0x200`, writes mode/state into object `+0x1F8`, checks source pointer at object `+0x1B0`, calls `0x7FF7209B6620`, then calls `0x7FF720A10EC0`, storing the returned cooked runtime object at object `+0x1A8`. | This is the broad serialized-source-record to cooked-runtime-object copier. | `CONFIRMED` | Use it to explain why raw BDAE scans do not directly equal live playback arrays. |
| `0x7FF720A10EC0` | Allocates `0x528` bytes, initializes it through `0x7FF7209BD8B0`, inserts it into a list-like owner, and calls `0x7FF720A110A0`. | The broad cooker materializes a large dynamic runtime object before individual fields are copied. | `CONFIRMED` | Inspect this object's dynamic field table only as runtime field offsets, not as raw BRES offsets. |
| `0x7FF720A110A0` | Builds global `qword_7FF722E9DE20` as 119 runtime field offsets by querying a newly allocated `0x528` object. | `qword_7FF722E9DE20` is a runtime field-offset catalog. It is not the raw `owner+0xBC/+0xC0` descriptor table. | `CONFIRMED` | Keep field-offset table references separate from BRES relative-offset tables in tools. |
| `0x7FF7209B7920`, field-copy region | Copies source bytes and values including `source+0x68`, `source+0x1B4`, `source+0x69`, `source+0x10..0x17`, vec4-ish data at `source+0x18` and `source+0x28`, `source+0x40`, `source+0x1A8`, and floats at `source+0x1AC/+0x1B0` into fields selected by `qword_7FF722E9DE20`. | This confirms a cooked runtime-object layer that changes addressing and field layout before playback. | `CONFIRMED` | Map source records to raw BRES only after identifying their owner/root. |
| `0x7FF7209B7920`, switch at `0x7FF7209B7CE0` | Switches on `dword[source+0x40]` with 7 cases. Case blocks use a relative payload at `source+0x44` and copy one to three floats into dynamic fields corresponding to offsets `+0xAC/+0xB0/+0xB4` in the field-offset table. | This is a serialized source-value format switch inside the broad object cooker. It should not be confused with the per-frame evaluator-family selector. | `CONFIRMED` | Search raw shared animation BDAEs for source records with `+0x40/+0x44` shape and compare with cooked fields. |

Practical result:

```text
raw/shared BDAE source record
  -> source mode byte +0x68 and reference +0x6C
  -> optional named-resource resolver
  -> broad source cooker 9B7920
  -> cooked 0x528 runtime object via A10EC0
  -> dynamic runtime fields via qword_7FF722E9DE20
  -> later evaluator-container/materialized target table
```

This explains why the previous raw-file materialized-table scans mostly found false positives: the engine is not simply reinterpreting the raw BDAE bytes in place for playback.

## Playback Object Factory And State Fields - 2026-06-19 Follow-Up

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML MCP health | Read-only MCP health probe confirms `DragonManiaLegends.exe.i64`, imagebase `0x7ff720730000`, Hex-Rays ready. | Evidence below is from the active Dragon Mania Legends database. | `CONFIRMED` | Continue read-only until IDA mutation is explicitly approved. |
| `off_7FF722D3E298` installed playback vtable | `0x7FF7209F87F0` writes `off_7FF722D3E298` into the constructed `0x98` playback object. From this actual base, slot `+0x68 -> 0x7FF7209FC950`, slot `+0x70 -> 0x7FF720A116C0`, slot `+0x90 -> 0x7FF7209FBE80`, slot `+0xC0 -> 0x7FF7209F9450`, and slot `+0x128 -> 0x7FF7209FC630`. The nearby qword region at `0x7FF722D3E2D8` is a real table slice but should not be used as the object vtable base. | `9F9450` and `9FC630` are virtual methods in the constructed playback object family; previous slot offsets derived from `0xD3E2D8` were base-shifted. | `CONFIRMED` | Use `off_7FF722D3E298` as the read-only anchor in reports/tools; do not apply IDA renames/types without approval. |
| `0x7FF7209F87F0` | Constructs a `0x98` playback object from an existing animation resource pointer. It installs vtables `off_7FF722D3E298`, `off_7FF722D3E3D0`, `off_7FF722D3E3E0`, stores the resource at object `+0x50`, zeroes `+0x58/+0x60/+0x68/+0x70/+0x78/+0x80`, then calls `0x7FF7209FC110`. | This is the base playback-state constructor for an already loaded animation resource. | `CONFIRMED` | Map the resource object fields, especially target count and clip/segment tables. |
| `0x7FF7209F88C0` | Constructs the same `0x98` playback object but first allocates a `0x108` resource-like object, initializes it via `0x7FF720A34CD0`, calls its virtual slots `+0x28` and `+0x48`, then calls `0x7FF7209FC110`. | There is a second constructor path that builds/fills an animation resource before attaching it to the same playback state. | `CONFIRMED` | Identify the `0x108` resource class and its fields if needed for loading loose/shared anims. |
| `0x7FF7209FC110` | Stores the animation resource pointer at playback object `+0x50`, reads `targetCount = dword[resource+0x48]`, and resizes a `u32` vector at playback object `+0x58/+0x60/+0x68` to that count. It then calls virtual `+0x68` with a freshly obtained object and virtual `+0x128` with clip/segment index `0`. | The `+0x58/+0x60/+0x68` vector is per-target state/cache sized by resource target count. It is not the selected `u16` target-index list. | `CONFIRMED` | Compare the `targetCount` with Gorilla root `+0x40 = 69` and inspect which per-target state values change during playback. |
| `0x7FF7209FC630` | Takes a clip/segment index, bounds-checks against a 40-byte table at resource `+0x88/+0x90`, writes `playback+0x70 = dword[resource+0x48] * index`, writes `playback+0x74 = index`, refreshes clip/range metadata, optionally creates a `0x30` helper object, copies pointers from playback `+0x40/+0x48` into it, then sends it to the sink/control object via virtual `+0xB0`. The helper methods compare event names with `strcmp` and convert byte/u16/int event times to frame-like values. | This is an active clip/segment and event/range selector. It is not the transform target-index list itself. | `CONFIRMED` | Tie one named clip index from the Gorilla `33 x 0x18` clip table to the index passed here, but keep event-list handling separate from transform target-list handling. |
| `0x7FF7209B01F0` | Factory switches on `dword[a5+0x08]`. Case `0` allocates `0x98` and calls `9F87F0`; case `1` allocates `0xB8` and calls `A05040`; case `2` allocates `0xB0` and calls `A01AE0`; cases `3/5/6` allocate `0xC8` and call `A02410`; case `4` allocates `0xD0` and calls `A03C40`. | Serialized playback type/kind selects one of several playback/blender subclasses. Case `0` is the base `0x98` object used by the currently traced per-frame path. | `CONFIRMED` | Locate the source record containing `a5+0x08` to classify shared body anim playback type on disk. |
| `0x7FF721553B10` | External wrapper calls `0x7FF7209F90A0`, then manages transition/fade fields: countdown at `+0xA4`, duration at `+0xA0`, active slot at `+0xA8`, two weights at `+0x50`, and callback/auto-trigger fields at `+0xB0/+0xF0`. | The user-observed GIF behavior where motion runs briefly then tweaks/holds is plausibly tied to transition-window fields and callbacks, not dead decoded keyframes. | `STRONGLY SUPPORTED` | Keep viewer preview separated into raw pose evaluation versus transition/crossfade/callback layers. |
| `0x7FF7209FC0C0` vs `0x7FF7209FC110` | `9FC0C0` selects `u16` target-list owner slots `+0x30/+0x38/+0x40` based on mode at `+0x58`; `9FC110` instead owns a separate `u32` per-target state vector at playback `+0x58/+0x60/+0x68`. | Two different structures share nearby offsets: selected target-index lists live in the object passed as `*a3` to apply helpers, while the playback object itself owns a per-target state/cache vector. | `CONFIRMED` | Do not patch the viewer by treating every `+0x58` as the same field; track object identity carefully. |

Practical viewer implication:

```text
animation resource
  -> playback factory kind at source +0x08
  -> playback subclass
  -> resource target count at +0x48
  -> per-target state/cache vector
  -> selected clip/segment index
  -> selected u16 target-index list
  -> evaluator apply path
```

The safest next implementation patch is a structured animation-debug panel that displays the factory kind, resource target count, clip/segment index, and target-table entries separately, before attempting final skin deformation.

## Playback Sink And Event-Helper Correction - 2026-06-20

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML MCP health | Read-only MCP health probe confirms `DragonManiaLegends.exe.i64`, imagebase `0x7ff720730000`, Hex-Rays ready. | Evidence below is from the active Dragon Mania Legends database. | `CONFIRMED` | Continue read-only until IDA mutation is explicitly approved. |
| `0x7FF7209FC950` | If given a non-null object, stores it at playback `+0x20`; otherwise allocates `0x78`, calls `0x7FF720A34100`, then installs primary vtable `off_7FF722D3E410` and secondary vtable `off_7FF722D3E4E0`. It then tail-calls playback virtual `+0x128` (`9FC630`) with the current segment index at playback `+0x74`. | Playback `+0x20` is a subordinate sink/control object, not a raw BRES resource. | `CONFIRMED` | Track calls into `off_7FF722D3E410` for output/list state. |
| `off_7FF722D3E410` sink/control vtable | From this actual base, slot `+0xA8 -> 0x7FF720A34620`, slot `+0xB0 -> 0x7FF720A345C0`, and slot `+0xC0 -> 0x7FF720A344E0`. | The earlier slot map that placed `A343E0` at `+0xB0` was base-shifted/wrong for the allocated sink object. | `CONFIRMED` | Use these concrete slot addresses when modeling `9FC630` receiver behavior. |
| `0x7FF720A345C0` | Increments the refcount of its argument and stores it at sink/control `+0x50`; releases the old value if present. `9FC630` calls this through sink virtual `+0xB0` with the `0x30` helper object. | Sink `+0x50` stores the active event/list helper object. | `CONFIRMED` | Inspect callers of the helper vtable methods to see when events are polled. |
| `0x7FF720A344E0` | Stores its `_DWORD *` argument at sink/control `+0x40`; if the pointed descriptor is non-null and `*descriptor != 0`, it calls sink virtual `+0x28`; otherwise it resets sink floats at `+0x28/+0x2C` to `0.0/1.0`. | Sink `+0x40` stores the current range/descriptor used by the clip selector. | `CONFIRMED` | Compare descriptor fields with the 40-byte resource segment entries. |
| `0x7FF720A34620` | If no descriptor is installed at sink `+0x40`, stores fallback floats at `+0x28/+0x2C`; if the boolean argument is set, calls sink virtual `+0x18`. | This is range/timing fallback refresh, not target transform output. | `CONFIRMED` | Keep separate from local TRS sinks (`+0x158/+0x168/+0x148`). |
| `0x30` helper vtable `off_7FF722D3E260` | The helper stores a selected pointer at `+0x28`, an index/current state at `+0x20`, and receives playback `+0x40/+0x48` at helper `+0x10/+0x18`. `0x7FF720A33CF0` switches on `dword[*helper+0x28]`, compares event names with `strcmp`, and converts `u8/u16/i32` event times using `33.333332` for small encodings. | This helper is an animation event/name-time helper. It should not be used as the transform-channel target-index list. | `CONFIRMED` | Implement event listing later; do not feed these bytes into skeletal playback. |
| `0x7FF7209F9CF0` selected-list loop | The actual transform apply loop still reads selected `uint16 targetIndex` values from the object passed through `a3`: mode at `(*a3)+0x58` selects a list object from `+0x30`, `+0x38`, or `+0x40`; each list contributes begin/end pointers at list `+0x10/+0x18`. | Transform playback target lists are owned by the apply-state object passed to `9F9CF0`, not by the `9FC630` event helper. | `CONFIRMED` | Find the constructor/populator for this `a3` apply-state object and verify whether selected lists contain target `32`. |

## Apply-State Target-List Builder - 2026-06-20

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209F90A0` | Before dispatching to playback virtual `+0xC0` (`9F9450` for the base object), it calls `0x7FF720A14A80(*a3)`. | The apply-state object is refreshed immediately before per-frame playback evaluation. | `CONFIRMED` | Treat `A14A80` as the pre-apply target-list refresh routine. |
| `0x7FF720A14A80` | If dirty byte `state+0x28` is set, it rebuilds list objects at `state+0x30`, `state+0x38`, and `state+0x40`, using `0x7FF720A14DB0` for each, then clears `state+0x28`. It uses `state+0x18` as a primary source object and `state+0x20` as an optional secondary/blend source. | This is the missing constructor/populator layer for the selected u16 target-index lists. | `CONFIRMED` | Decode how helper bitsets are populated by `A363A0/A36400/A367E0/A36600`. |
| `0x7FF720A14DB0` | Clears a destination list by setting `list+0x18 = list+0x10`, determines `targetCount` from a source payload at `sourcePayload+0x68`, then loops `targetIndex = 0..targetCount-1`. For every bit set in the helper bitset at `helper+0x10`, it appends `targetIndex` as a 16-bit value to the destination list. | Selected target-index lists are bitset-derived `uint16` arrays. List values are the target indices used by `9F9CF0`. | `CONFIRMED` | If the bitset for an active clip has bit `32`, the resulting list contains `head_ctrl-node-rotation`. |
| `0x7FF720A03EA0` | Repeats selected-list mode logic directly: mode `0 -> state+0x30`, mode `1 -> state+0x38`, mode `2 -> state+0x40` when `state+0x20` is present, otherwise `state+0x30`. It passes `selectedList+0x10` to `0x7FF720A04C20` and also iterates `selectedList+0x10..+0x18` directly. | The list object schema is now proven: `+0x10` begin, `+0x18` end, `+0x20` capacity/end, entries are `uint16`. | `CONFIRMED` | Patch tooling to model apply-state list objects with this exact schema. |
| `0x7FF720A362C0` | Fills all valid target bits and masks unused bits in the final dword. | This is the all-target fallback mask initializer. | `CONFIRMED` | Use it as the baseline when no primary mask is installed. |
| `0x7FF720A363A0` / `0x7FF720A367E0` | Copy target-bitset words from a source object into the temporary helper mask. | These are bitset copy helpers. | `CONFIRMED` | Identify each source object's owner. |
| `0x7FF720A36400` | Intersects the temporary helper mask with another source mask by ANDing dwords. | This builds overlap/filtered target sets. | `CONFIRMED` | Use this to model blend overlap lists. |
| `0x7FF720A36600` | Inverts all valid target bits in the temporary helper mask. | This builds complement/non-overlap target sets. | `CONFIRMED` | Use this to model non-overlap transition lists. |
| `0x7FF7209F8A00` | Saves old apply-state mode `state+0x58`, temporarily writes mode `1`, starts from an all-valid target mask, copies the source mask at `state+0x20 + 0x98`, optionally intersects with the existing primary mask at `state+0x18`, rejects empty masks through `0x7FF720A36780`, and installs the non-empty result into `state+0x18`, setting dirty byte `state+0x28 = 1`. | This is a primary target-mask propagation/update function feeding `A14A80`. | `CONFIRMED` | Determine whether the `state+0x20 + 0x98` mask includes target index `32` for the selected Gorilla clip. |
