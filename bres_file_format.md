# BRES File Format

## Compared Files

- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\runtime_source\dragon_metal_seahorse_runtime.bdae`
- `C:\Users\crist\Desktop\crystal_lady_assets_auto\runtime_source\dragon_crystal_lady_runtime.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon_Eye.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Eye.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\SkinnedOneSided.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\TextureAnim.bdae`
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\VertexTextureAnim.bdae`

## Shared Header Model

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x00` in every compared `.bdae` | All compared files begin with ASCII `BRES`. | All are instances of the same top-level BRES container family. | CONFIRMED | Reuse one common header parser for these files. |
| `0x08`, `0x10`, `0x20`, `0x28`, `0x30`, `0x38` | The same header field layout works across both runtime samples and all smaller base/effect files: `reloc_start`, `reloc_count`, `strings_start`, `strings_end`, `records_start`, `data_start`. | The earlier inferred header model generalizes cleanly. | CONFIRMED | Continue mapping object types from these offsets. |
| `reloc_start + reloc_count * 8 == strings_start` | Both runtime samples and all small base/effect samples satisfy the same relocation-table boundary rule. | The relocation table is still strongly supported as an array of 8-byte entries immediately before the declared string region. | CONFIRMED | Add relocation-field semantics only after parser/runtime code proves them. |
| whole compared set | The string `0,0,0,930` appears in both runtime samples and all compared base/effect BDAEs. | This string is not runtime-animation specific and should not currently be treated as proven duration metadata. | CONFIRMED | Only promote any duration interpretation after code reads it as such. |

## Runtime Sample Header Comparison

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_metal_seahorse_runtime.bdae` header | Size `1,225,400` (`0x12B2B8`), SHA256 `66a8896ee8fe9c0bb4d9d3781be47aedb6cedc33cc3bf70b1dc485544cebe01b`, `reloc_start=0x40`, `reloc_count=699`, `strings_start=0x1618`, `strings_end=0x2CE8`, `records_start=0x2E08`, `data_start=0xA7B0`. | Baseline runtime sample with a large post-record payload/object arena. | CONFIRMED | Keep attributing slices of `0xA7B0+` to track payloads, mesh data, or other runtime payloads. |
| `dragon_crystal_lady_runtime.bdae` header | Size `94,312` (`0x17068`), SHA256 `910db680cdf888a81956fc4757b9e99237c43ce64a78da093e1c5174823384e3`, `reloc_start=0x40`, `reloc_count=763`, `strings_start=0x1818`, `strings_end=0x2FD0`, `records_start=0x30F0`, `data_start=0xB358`. | Second runtime sample with the same section scheme but a much smaller overall payload. | CONFIRMED | Use it as the best control for stable runtime-only record meanings. |
| both runtime samples | Both declare strings, records, and data sections in the same order, and both keep the same `header_size=0x40`. | The runtime dragon BDAEs share one stable container layout even when content volume differs greatly. | CONFIRMED | Add more runtime dragons later to test whether this remains universal. |

## Root-Like Runtime Record

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse `strings_end = 0x2CE8` | At `0x2CE8`, raw fields include `+0x34 = 133333`, `+0x40 = 52`, `+0x44 = 236`. | The earlier candidate root-like record remains present exactly where first observed. | CONFIRMED | Keep tracing parser/runtime code to prove this record's semantic type. |
| Crystal Lady `strings_end = 0x2FD0` | At `0x2FD0`, the same layout pattern appears, but `+0x34 = 16667`, `+0x40 = 43`, `+0x44 = 236`. | This is the strongest file-side proof so far that the Crystal file contains the same root-like structure as Metal Seahorse. | CONFIRMED | Use executable-side code to confirm whether the same runtime object type reads both samples. |
| both runtime samples, root-like `+0x40` | Metal Seahorse has `52` named transform tracks and Crystal Lady has `43`; in both files the root-like record `+0x40` equals that exact total. | `root_like + 0x40 = total named transform track count` is now supported by two independent runtime samples. | CONFIRMED | Promote from file-side confirmation to parser confirmation once code reads that field directly. |
| both runtime samples, root-like `+0x44` | `+0x44` is `236` in both runtime samples. | This field is stable across both samples, but its meaning is still unknown. | STRONGLY SUPPORTED | Search executable-side reads of the same structure to identify whether `236` is a byte size, record span, or another fixed metadata value. |
| both runtime samples, root-like `+0x34` | `+0x34` differs sharply: `133333` vs `16667`. | `+0x34` is not a simple constant or track-count field. It may be clip-timing-related or another per-animation scalar, but that remains unproven. | STRONGLY SUPPORTED | Compare more runtime samples and find code that consumes this field before assigning meaning. |
| both runtime samples, root-like `+0x00` | Metal has `+0x00 = 0x161C`, Crystal has `+0x00 = 0x181C`. In both files this equals `strings_start + 4`. | The root-like record appears to begin with a stable internal reference back into the declared string section. | STRONGLY SUPPORTED | Determine whether this is a name pointer, string-table handle, or another string-root reference. |
| both runtime samples, root-like `+0x18` | `+0x18 = 2` in both files. | This is a stable small metadata field of the same root-like record type. | STRONGLY SUPPORTED | Find code that branches or counts on this field. |
| both runtime samples, root-like `+0x54/+0x58/+0x5C/+0x60` | Both files contain the same pattern: `+0x54 = 1`, `+0x58 = late offset`, `+0x5C = 1`, `+0x60 = second late offset`, and `+0x60 - +0x58 = 0x10`. | The root-like record likely owns two adjacent late payload-arena subreferences, each paired with a count/flag of `1`, but their exact type is not yet known. | HYPOTHESIS | Find executable-side reads of these four fields or locate matching late payload objects. |

## Transform Track Array

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse `records_start + 0x10 = 0x2E18` | The first transform-track candidate record begins at `0x2E18`, and all 52 candidate track records are contiguous with a fixed `0x28` stride, ending at `0x3610`. | The runtime track records form a compact contiguous array immediately after a 16-byte preamble in the records region. | CONFIRMED | Identify the 16-byte preamble directly preceding the array. |
| Crystal Lady `records_start + 0x10 = 0x3100` | The first transform-track candidate record begins at `0x3100`, and all 43 candidate track records are contiguous with the same `0x28` stride, ending at `0x3790`. | The same runtime track-array layout generalizes to the second runtime sample. | CONFIRMED | Add more samples to test whether every runtime dragon follows the same `records_start + 0x10` rule. |
| runtime track record layout | For both samples, a candidate named track record is `0x28` bytes and decodes as `name_ptr`, `0`, `inputCount`, `inputRel`, `outputCount`, `outputRel`, `flagsA`, `flagsB`, `extraRel`, `extra2`. | The `0x28` track-record layout is now supported across two runtime dragon BDAEs. | STRONGLY SUPPORTED | Tie each field to parser/runtime code for semantic confirmation. |
| runtime track records, offset `+0x10` | In both runtime samples, the track-record dword at `+0x10` is consistently `1` for the matched transform-track records examined so far. | This is strong evidence that the executable-side descriptor byte read at runtime descriptor `+0x10` is not reading these raw `0x28` on-disk track records directly. | CONFIRMED | Keep treating the executable-side `0x18` descriptor as a different cooked/lookup structure until proven otherwise. |
| runtime track records, `outputRel - inputRel` | For every currently recovered transform-track record in both runtime samples, `outputRel - inputRel = 24`. | The first two payload references are packed in a stable fixed-distance pattern. | CONFIRMED | Compare this 24-byte step against decoder-side record packing. |
| runtime track records, `extraRel` | Most track records have `extraRel = 0`, but a smaller subset in both runtime samples has non-zero `extraRel` values. Metal Seahorse examples include `Lwing_bone01-node-rotation`, `LLwing_bone01-node-rotation`, `RLwing_bone01-node-rotation`, `Rwing_bone01-node-rotation`, `Lleg_01-node-rotation`, `Lleg_03-node-rotation`, and `speed_node-node-translation`. Crystal Lady shows the same pattern family plus `Lwing_bone04-node-rotation` and `Rleg_01-node-rotation`. | `extraRel` is a real optional field, not parser noise, and is associated with a specific subset of channels. | CONFIRMED | Walk those specific channels backward from executable decode paths to determine what `extraRel` stores. |
| runtime track records with non-zero `extraRel` | For every currently recovered non-zero `extraRel` track in both samples, `extraRel - outputRel = 12`. | The optional third payload reference sits immediately after the output payload cluster rather than in a distant part of the runtime payload arena. | CONFIRMED | Match this 12-byte step to runtime decoder-side helper structures. |

## Runtime Track Counts And Track Sets

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse runtime strings | `8` translation tracks and `44` rotation tracks, total `52`. | The Metal runtime sample is a broader motion/control set. | CONFIRMED | Use it as the richer sample for bridge attempts. |
| Crystal Lady runtime strings | `2` translation tracks and `41` rotation tracks, total `43`. | Crystal Lady is a reduced transform set, but still uses the same runtime track-array structure. | CONFIRMED | Compare more dragons to see whether reduced translation counts are common. |
| track-set diff | Crystal Lady's rotation set is a subset of Metal Seahorse's visible rotation set in the current string extraction, while Metal has extra translations (`Dragon_center`, `Dragon_root`, `food_position`, `food_position_jump`, `Particle_View_001`, `speed_node`) and visible extra rotations (`Dragon_center`, `Head_CTRL`, `Rwing_bone04`). | The runtime format generalizes even when the authored rig/control set changes. | STRONGLY SUPPORTED | Add one more runtime dragon to verify whether these omissions are dragon-specific or extraction-specific. |

## Runtime String Categories

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse runtime | `.bdae` refs: `Dragon.bdae`, `Dragon_Eye.bdae`; texture refs: `dragon_metal_seahorse.tga`, `eye_metal_seahorse.tga`, `shadow_dragon.tga`; mesh/material strings include `METAL_SEAHORSE_-mesh`, `METAL_SEAHORSE_-mesh-skin`, `shadow-mesh`, `3DMesh_Skinned`, `AdditivePreMul_Skinned`, `Dragon_STENCIL`. | Metal's runtime BDAE directly names both dependent BDAEs, all visible textures, and mesh/material bindings. | CONFIRMED | Continue tying these names to record owners and executable-side loader calls. |
| Crystal Lady runtime | `.bdae` refs: `Dragon.bdae`, `Dragon_Eye.bdae`, `TextureAnim.bdae`; texture refs: `dragon_crystal_lady.tga`, `eye_crystal_lady.tga`, `fx_spark_alpha.tga`, `shadow_dragon.tga`; mesh/material strings include `dragon_crystal_lady002-mesh`, `dragon_crystal_lady002-mesh-skin`, `shadow-mesh`, `3DMesh_Skinned`, `Additive_NoSkin`, `AdditivePreMul_NoSkin_Colorized_Fade`, `TextureAnim`. | Crystal Lady shows the same core body/eye/shadow pattern but adds an effect/material dependency family around `TextureAnim` and `fx_spark_alpha.tga`. | CONFIRMED | Trace how the `TextureAnim.bdae` reference is loaded and bound in the executable. |
| small base/effect BDAEs | `Dragon.bdae`, `Dragon_Eye.bdae`, `Eye.bdae`, `SkinnedOneSided.bdae`, `TextureAnim.bdae`, and `VertexTextureAnim.bdae` remain small, shader/profile-heavy, and have no large declared post-record payload arena. | These files are still best modeled as base body/eye/effect/material graphs, not the per-dragon transform payload containers. | STRONGLY SUPPORTED | Continue matching runtime mesh/material names against these smaller base graphs in code. |

## Data-Blob Organization

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse `data_start=0xA7B0` | The overall runtime payload arena spans `1,182,472` bytes, but the current transform-track `inputRel`/`outputRel`/`extraRel` targets only cover roughly `0x0814` through `0x0C28` relative to `data_start`, a span of about `1,044` bytes. | Only a small early slice of the large runtime payload arena is currently attributable to the visible transform-track array. The large remainder likely holds other payload classes such as geometry, skinning, or other animation/value data. | STRONGLY SUPPORTED | Map non-track record owners that point deeper into the payload arena. |
| Crystal Lady `data_start=0xB358` | The overall runtime payload arena spans `48,400` bytes, but the current transform-track target offsets only cover roughly `0x06AC` through `0x0A50` relative to `data_start`, a span of about `932` bytes. | The same early-track-payload pattern appears in the smaller Crystal file. | STRONGLY SUPPORTED | Correlate deeper payload-arena regions with mesh/material/effect records. |
| both runtime samples | The transform-track payload region sits near the start of the runtime payload arena in both files, while track names and track records sit much earlier in the strings/records sections. | The runtime BRES format separates name/record metadata from compact numeric payload storage consistently. | CONFIRMED | Extend this to mesh/skin records once their pointers are isolated. |
| Metal-only data tail after Crystal-sized payload-arena length | The Metal runtime payload arena still has about `1.13 MB` of extra tail, with many long monotonic `u16` runs and no embedded `BRES` or `DDS ` signatures. | The Metal-only size explosion is much more consistent with native geometry/index-style payload than with extra string or nested-file content. | STRONGLY SUPPORTED | Prove this with a direct mesh/skin record owner or executable-side reader. |
| Metal payload-arena start | The first 20 float triples at `data_start` are smooth position-like values around `x=16..19`, `y=16..23`, `z≈-0.000011`. | The first payload-arena slice looks geometry-like rather than like arbitrary packed animation bytes. | STRONGLY SUPPORTED | Look for matching vertex-count or mesh-owner records. |

## Decoder-Side Structure Mismatch With Raw Track Records

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7EDCC30` | The packed-quaternion path reads `*(int *)(base + 12)` using `base + 28` semantics, and also reads `*(int *)(base + 36)` as a nested relative pointer source. | The structure consumed by the runtime decoder does not use the same base/offset semantics as the raw on-disk `0x28` record. | CONFIRMED | Find the cooked/relocated record builder that feeds this decoder. |
| on-disk `0x28` track record vs runtime decoder | In the raw on-disk track record, offset `+0x24` (`36`) is currently `extra2 = 0` for the visible transform tracks, but the decoder expects a live relative field there. | The decoder is consuming a transformed runtime object, not the untouched file bytes. | CONFIRMED | Trace the record-cooking step between parsed BRES metadata and decoder dispatch. |

## Runtime Texture And Secondary BDAE Reference Structures

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Crystal Lady records around `0x7DB0-0x7E20` | For `dragon_crystal_lady.tga`, `eye_crystal_lady.tga`, `fx_spark_alpha.tga`, and `shadow_dragon.tga`, the record region contains repeated aligned references in paired 16-byte/32-byte patterns such as `[name_ptr, 0, next_name_ptr, 0, ...]`. | Crystal Lady exposes a structured record block for texture references that is separate from the `0x28` transform-track array. | STRONGLY SUPPORTED | Trace code that owns these record offsets to assign exact record types. |
| Crystal Lady records around `0x7E40-0x7FA8` | `Dragon.bdae`, `Dragon_Eye.bdae`, and `TextureAnim.bdae` each have aligned record references with stable word patterns like `[name_ptr, 0, secondary_name_ptr, 0, 6, rel, 0xFFFFFFFF, 0]`. | Runtime secondary BDAE references are stored in a distinct record pattern from transform tracks. | STRONGLY SUPPORTED | Walk executable-side loader code from these names to confirm whether field `6` is a kind/type tag. |
| Metal Seahorse runtime | The same name strings are present, but the simple aligned string-pointer scan did not recover as clean a record block as Crystal Lady for those asset-reference names. | Metal still proves direct naming, but Crystal currently gives the clearer structural evidence for asset-reference record patterns. | STRONGLY SUPPORTED | Refine the Metal string-record walker so both runtime samples can be compared on identical record owners. |

## Current Role Model

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| runtime dragon BDAEs | Both runtime samples directly name body/eye textures, base body/eye BDAEs, mesh/material strings, and transform tracks, and both alone contain a large post-record payload arena. | Runtime dragon BDAEs are the main per-dragon containers for transform-channel metadata and compact numeric payloads, plus binding names for mesh/material/effect composition. | STRONGLY SUPPORTED | Continue proving which deeper payload-arena ranges are mesh/skin data versus additional animation data. |
| `Dragon.bdae` | Tiny, shader/profile-heavy, no large post-record payload arena. | Base body render/profile setup. | STRONGLY SUPPORTED | Trace runtime references into it in the executable. |
| `Dragon_Eye.bdae` | Tiny, eye-specific, shader/profile-heavy, no large post-record payload arena. | Base eye render/profile setup. | STRONGLY SUPPORTED | Trace runtime references into it in the executable. |
| `TextureAnim.bdae` and sibling effect/material BDAEs | Small files dominated by shader/effect strings and parameter names. | Reusable effect/material graphs rather than raw dragon transform payloads. | CONFIRMED | Use later for material reconstruction and effect binding. |
