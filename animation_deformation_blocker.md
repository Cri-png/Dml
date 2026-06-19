# Animation Deformation Blocker

Read-only update from 2026-06-18. This report isolates the main remaining blocker after static mesh rendering, shared body-type assignment, row decoding, clip tables, and local TRS sinks were proven.

## Current Finding

The big unresolved piece is not the static mesh, body type assignment, DDS texture decoding, basic keyframe rows, or quaternion decode. The strongest current evidence says the deformation problem is the missing full scene/controller hierarchy and exact skin-palette source matrix set.

The game animates many named controller/helper nodes, then the skinned mesh palette is composed from resolved source matrices plus per-slot bind/inverse-bind data. The viewer currently applies only animation tracks whose names map directly to Tiki's 24 skin-palette slots, so parent/controller tracks such as `body_root-node`, IK chains, heel/toe roll nodes, and wing helpers are skipped. That can produce a recognizable but drifting/crushed/twitchy animation.

## Evidence Table

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_tiki_2024.bdae` string-region skin binding groups | Tiki has `24` extracted skin-palette slots: `body_bone01..06`, `body_front`, `head_ctrl`, `jaw_ctrl`, legs, and `Tail_bone01..03`. | The captured palette has a real `24`-slot semantic map. | `CONFIRMED` | Tie each slot to the engine palette source pointer array used by `0x7FF720A60020`. |
| `dragon_gorillabody_anim_keyframes.json` and `gorilla_attack_export_with_engine_tables.json` | Gorilla shared animation exports `52` transform nodes. Only `21` currently map directly to Tiki skin slots; `31` are unmapped by the current viewer. | Direct slot-only animation application is incomplete. | `CONFIRMED` | Parse/apply the full runtime node hierarchy so controller/helper transforms affect descendant skin slots. |
| unmapped Gorilla nodes | Unmapped names include `body_root-node`, `IKLBChain-node`, `IKLFChain-node`, `IKRBChain-node`, `leg*_IK-node`, `leg*_heel_roll-node`, `leg*_toe_roll-node`, `wingL01/02-node`, and `wingR01/02-node`. | The skipped nodes are exactly parent/controller/helper-style nodes, not random decorative leftovers. | `STRONGLY SUPPORTED` | Recover parent-child relationships from BRES records or the node construction path in IDA. |
| `0x7FF720A60020` | Requests render parameter code `0x0C` (`bone_matrices`) and `0x0D` (`weight_mask`), then iterates source matrix pointers and writes `64` bytes per palette slot. | Final deformation uses a composed matrix palette, not raw local TRS outputs. | `CONFIRMED` | Identify the owner object fields `a1[1]` and `a1[2]` and reproduce the loop offline. |
| `0x7FF720A60020` bind/source math | For each slot, source matrix pointer `v21` is combined with a `64`-byte slot record at `a1[1] + s32[a1[1]+4] + slot*64`; meaningful bind lanes are read at row offsets `+4/+8/+12`, `+20/+24/+28`, `+36/+40/+44`, and `+52/+56/+60`. | The engine-equivalent formula is compatible with row-vector skinning of `bind_or_inverse_bind @ current_source_world`; the raw slot record is not just a flat copied `4x4` with all floats used. | `CONFIRMED` for offsets and composition, `STRONGLY SUPPORTED` for bind semantic | Locate the serialized or cooked source of the `64`-byte bind-slot table. |
| `tiki_auto_24_skin_matrices.bin` | Exact `1536` bytes = `24 x 64`; rows look like normal final affine matrices, for example slot 0 starts `[1.249431, -0.0, -0.037695, 0] ... [-90.498711, 24.879236, 37.104519, 1]`. | This capture is a final palette dump, not the raw skipped-lane bind-slot table consumed by `0xA60020`. | `CONFIRMED` | Compare a live rest-pose source matrix plus raw bind-slot table against this captured final palette. |
| `0x7FF720A5F0F0` | Point transform formula is `x' = m0*x + m4*y + m8*z + m12`, `y' = m1*x + m5*y + m9*z + m13`, `z' = m2*x + m6*y + m10*z + m14`. | Viewer row-vector affine convention is correct; the current bug is not a simple transpose-only issue. | `CONFIRMED` | Keep this convention while adding full hierarchy/controller propagation. |
| local/helper TRS sanity check | Captured helper local matrices are reproduced by current `S * R(conjugated xyzw) * T` composition with median max error `0.0`, and parent-pair checks reproduce child worlds when the parent world is captured. | Quaternion handedness and basic local TRS composition are not the primary blocker. | `CONFIRMED` | Capture or parse the missing non-palette parent/helper worlds and names. |
| current experimental viewer mapping | `load_keyframe_rotation_overrides()` maps frame transforms only through `extract_skin_palette_bindings()` `nodeToSlot`. Unmapped controller/helper nodes are ignored. | This explains why GIFs can move briefly or snap/tweak but not play like the game. | `CONFIRMED` | Replace slot-only mapping with a named scene hierarchy evaluator and then produce palette matrices for the skin slots. |

## Practical Viewer Implication

Static viewer mode is safe and should remain default. Live playback should stay experimental until the viewer can:

1. Resolve the shared animation asset from dragon metadata.
2. Select a named clip and sample the engine-consumed target rows.
3. Apply sampled local TRS to the full named node/controller hierarchy, not only skin slots.
4. Read or reconstruct source matrices for all skin-palette source nodes.
5. Compose final palette entries using the `0x7FF720A60020`-style bind/source loop.
6. Deform the already-rest-posed mesh via rest-unapply/frame-apply, preserving the static silhouette.

## Next Best Target

The next decisive target is the runtime BRES node hierarchy / source-matrix pointer array feeding `0x7FF720A60020`.

Recommended next steps:

- File side: parse the named node records around Tiki's string groups from `body_root-node` through all IK/helper/palette nodes and recover parent links.
- IDA side: continue read-only from the `CMeshSceneNode`/palette setup owner to identify what populates `a1[2]`, the source-matrix pointer array used by `0x7FF720A60020`.
- Viewer side after proof: add an experimental `hierarchy-playback` mode that applies all 52 Gorilla transform nodes, then derives the 24 final skin matrices from the evaluated hierarchy.

## Time-Remap Co-Blocker - 2026-06-18

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `generated/experimental/dragon_tiki_2024_runtime/time_remap/gorilla_time_remap.md` | `clip-local-ms` keeps all decoded transform tracks active but makes many named clips look numerically similar; `clip-absolute-ms` clamps almost all later clips. | The deformation/playback bug now has two proven sides: missing full hierarchy/palette composition and missing clip/segment time remap. | `STRONGLY SUPPORTED` | Solve hierarchy and time remap together before making live playback the default GUI mode. |

Updated next decisive targets:

1. File side: parse named node records around Tiki's `body_root-node` through IK/helper/palette nodes and recover parent links.
2. IDA side: continue read-only from the `CMeshSceneNode`/palette setup owner to identify the source-matrix pointer array used by `0x7FF720A60020`.
3. IDA side: continue read-only from `9FBC20 -> 9F2410 -> 952E70 -> 9EB180` to recover the selected-clip-to-row-time remap.
4. Viewer side after proof: add experimental `hierarchy-playback` using all 52 Gorilla transform nodes and the proven time domain.

## Visual Test Follow-Up - 2026-06-18

Additional outputs and details are in [animation_visual_tests.md](animation_visual_tests.md).

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `viewer_prototype/render_tiki_controller_visual_tests.py` | Heuristic variants apply `body_root` and leg controller deltas to matching skin slots, then render comparison GIFs/contact sheets. | This is a safe diagnostic harness, not a final playback method. | `CONFIRMED` | Keep it available for future comparisons after real hierarchy parsing. |
| Generated controller sheets | `attack`, `idle_walk`, `win`, and `death` variants preserve the static silhouette but do not visibly fix playback. | Direct prefix-based controller propagation is insufficient. | `STRONGLY SUPPORTED` | Avoid baking these heuristics into the GUI as a default. |
| Timing comparison | `clip-local-ms` produces suspiciously similar motion across clips; `clip-absolute-ms` often clamps to constants. | Exact clip-window/segment-local time remapping is still unresolved and must be solved alongside hierarchy. | `STRONGLY SUPPORTED` | Trace the selected clip entry through `9FBC20 -> 9F2410 -> 952E70 -> 9EB180` and reproduce that remap offline. |
