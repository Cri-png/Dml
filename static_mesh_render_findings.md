# Static Mesh Render Findings

## Scope

This report records the current static runtime-mesh reconstruction status for the two validated dragon samples:

- `dragon_crystal_lady_runtime.bdae`
- `dragon_metal_seahorse_runtime.bdae`

It intentionally separates:

- `CONFIRMED` static geometry reconstruction and exported artifacts;
- `STRONGLY SUPPORTED` per-pass/body-eye interpretations;
- `EXPERIMENTAL` visual-fit hints that still need record-backed or executable-backed confirmation.

## Runtime Summary

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Crystal mesh owner `0x8728` | Generic renderer rebuilds a static mesh from `stage0 -> 0xC098`, `516` records, `28` bytes each, plus five primitive groups. `XZ` is the best projection. Body DDS render is coherent. | Crystal static body-mesh extraction is now reusable and no longer a one-off experiment. | CONFIRMED | Keep the generated PNG/OBJ/glTF outputs as regression fixtures. |
| Metal mesh owner `0x11DA18` | Generic renderer rebuilds a static mesh from `stage0 -> 0x120DD8`, `529` records, `24` bytes each, plus four primitive groups. `XZ` is the best projection. Body DDS render is coherent. | The same mesh-owner/stage/primitive model generalizes to a second dragon with a different candidate vertex format. | CONFIRMED | Add more samples later to expand the layout family. |
| Crystal vs Metal stage0 layouts | Crystal uses `float3 + marker + float2 + marker` over `28` bytes. Metal uses `float3 + float2 + marker` over `24` bytes. | The viewer/exporter must detect per-runtime candidate stream layout instead of hardcoding Crystal globally. | CONFIRMED | Tie both formats to the executable mesh reader and decode marker word semantics. |

## Validation Checks

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Crystal validation report | `vertexPayloadSizeMatchesCountTimesStride = true`, `allAdjustedIndicesInBounds = true`, `claimedRangesMatchAdjustedRanges = true`, `fullAdjustedCoverage = 516 / 516`, vertices `0..515`. | Crystal primitive-group/base-vertex reconstruction is structurally consistent. | CONFIRMED | Preserve these checks in the renderer so regressions fail loudly. |
| Metal validation report | `vertexPayloadSizeMatchesCountTimesStride = true`, `allAdjustedIndicesInBounds = true`, `claimedRangesMatchAdjustedRanges = true`, `fullAdjustedCoverage = 529 / 529`, vertices `0..528`. | Metal primitive-group/base-vertex reconstruction is structurally consistent too. | CONFIRMED | Use the same checks on future dragons before promoting a layout. |

## Drawable / Pass Status

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Crystal body pass | Body DDS render is coherent and recognizable. Group hints keep `group_0`, `group_1`, and `group_2` as strong body candidates. | Main Crystal body mesh/pass is working for static display. | CONFIRMED | Recover record-backed material/profile ownership for each group. |
| Crystal eye pass | `group_3` becomes one clean isolated eye when rendered with `eye_crystal_lady.tga`; eye-role metrics keep it as the strongest eye candidate. | Crystal eye pass is partially separable already, but still not yet record-proven. | STRONGLY SUPPORTED | Recover the exact body/eye binding table entry or executable-side material assignment. |
| Crystal detached island | `group_4` remains detached under both body and eye experiments, with UVs extending outside `0..1`. | This looks more like a remaining transform/binding/material-pass issue than a failed vertex/index decode. | STRONGLY SUPPORTED | Trace group-to-node and group-to-pass binding next. |
| Crystal missing passes | `fx_spark_alpha.tga` and `shadow_dragon.tga` remain unresolved locally and are emitted as missing-texture debug renders. | Effect/shadow are now explicit dependency/pass problems, not geometry problems. | CONFIRMED | Find those textures or prove a non-textured pass path. |
| Metal body pass | Body DDS render is coherent and recognizable. Group hints keep `group_0` and `group_2` as strong body candidates. | Main Metal body mesh/pass is working for static display. | CONFIRMED | Recover the exact material/pass split for each primitive group. |
| Metal unresolved alternate pass | `group_3` has off-atlas UVs and both body/eye centroid alpha remain `0.0`. | Metal has at least one alternate unresolved pass that is neither explained by the body atlas nor by the current eye atlas. | STRONGLY SUPPORTED | Compare `group_3` against shadow/effect/profile records and future binding evidence. |
| Metal eye pass | Tiny `group_1` remains plausible as a secondary pass, but current visual metrics alone are not enough to call it the eye group. | Metal eye binding remains unresolved. | HYPOTHESIS | Recover record-backed eye/material assignment instead of inferring by visual fit. |

## Output Assets

| Runtime | Important outputs |
| --- | --- |
| Crystal Lady | `generated/experimental/dragon_crystal_lady_runtime/render_runtime_mesh/body_texture_only_XZ.png`, `group_debug_XZ.png`, `eye_group_3_XZ.png`, `runtime_mesh_body.obj`, `runtime_mesh_body.gltf`, `render_runtime_mesh_summary.json` |
| Metal Seahorse | `generated/experimental/dragon_metal_seahorse_runtime/render_runtime_mesh/body_texture_only_XZ.png`, `group_debug_XZ.png`, `runtime_mesh_body.obj`, `runtime_mesh_body.gltf`, `render_runtime_mesh_summary.json` |

## Current Safe Boundary

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| generic renderer outputs | The renderer now emits static PNGs, OBJ, glTF, JSON summary, validation checks, missing-dependency reports, and experimental per-group role hints for both validated dragons. | The project now has a real experimental DML static sprite-mesh viewer/exporter boundary. | CONFIRMED | Keep animation, skin deformation, and final material assignment outside this boundary until the remaining bridges are proven. |
