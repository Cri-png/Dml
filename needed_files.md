# Needed Files

## Notes

- Items already readable from the local install are not requested from you unless that access becomes blocked.
- `Dragon.dat` was inspected successfully in this pass and turned out to be a Flash/SWF-style blob, not the expected BRES mesh container.
- I only ask for files/samples that remain missing or would meaningfully accelerate the next proof steps.

## REQUIRED NOW

| Path or search term | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Exact filename `shadow_dragon.tga` or any archive/index hit containing that exact internal name | Not found in the sample bundle, loose base `GameData`, searched base BUDs (`data.bud`, `data_noesis.bud`, `game_dlc0.bud`, `game_dlc_splash_art.bud`, `ui_textures.bud`), or the scanned DLC `.pak` index search. | This is the only currently named runtime dependency that remains unresolved. If you already know a source for it, that source is immediately useful. | STRONGLY SUPPORTED | Search alternate install versions, backup extract folders, or any other BUD/PAK index dump for `shadow_dragon.tga` or `shadow_dragon`. |

## VERY USEFUL NEXT

| Path or search term | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Matching companion assets for `C:\Users\crist\Desktop\dragon_crystal_lady_runtime.bdae`: specifically its body texture, eye texture, and any extracted dependency bundle/folder that names the paired base `.bdae` files | The runtime file itself is already readable locally at `C:\Users\crist\Desktop\dragon_crystal_lady_runtime.bdae` (`94,312` bytes). A fresh local sweep found no matching `*crystal_lady*` textures, no extracted companion folder, and no paired manifest in accessible Desktop/Codex/GameData paths. | This is now the highest-value comparative sample for proving which runtime-BRES structures are stable across dragons and which are per-dragon content, and only the missing companion files need to be supplied. | STRONGLY SUPPORTED | Provide the matching extracted texture/dependency set or point me to the folder/archive that contains it so I can compare section boundaries, track layouts, and texture headers without re-asking for the runtime file itself. |
| Any archive, loose file, or previously extracted bundle containing `shadow_dragon.tga` | Still unresolved after searching accessible DLC/base archive indices. | Useful for completing the runtime texture dependency set, but no longer blocks the BRES/track pipeline work. | STRONGLY SUPPORTED | Best next search terms are `shadow_dragon.tga` and `shadow_dragon`. |
| Other runtime dragon `.bdae` samples that also expose `3DMesh_Skinned`, `-mesh-skin`, and `*-node-rotation` strings | The current Metal Seahorse runtime BDAE contains those structures clearly. | Additional samples would help separate generic track/mesh record layouts from dragon-specific names. | STRONGLY SUPPORTED | Any adult dragon runtime sample with its manifest/textures would work. |
| `game_dlc_dragon_anims_w8_default_1.pak` and any extracted assets from it | Visible locally in the DLC directory at `4,627,610` bytes, but not yet indexed for this pass beyond filename listing. | The archive name strongly suggests shared dragon animation content and may contain comparison clips or common rig/anim resources. | HYPOTHESIS | Search its internal BUD index for `Dragon`, `-rotation`, `-translation`, or known node names. |

## OPTIONAL LATER

| Path or search term | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Base effect/material `.bdae` files such as `NoesisEffects.bdae`, `NoesisCustomEffects.bdae`, `SkinnedOneSided.bdae`, `Simple_NoAlphaSplit.bdae`, `TextureAnim.bdae`, `VertexTextureAnim.bdae` | All are visible locally in base `GameData`. | These are likely useful for later material/shader binding and texture-upload path naming, but they are not blocking the immediate BRES layout work. | STRONGLY SUPPORTED | Inspect after the core scene/mesh/animation pipeline is mapped. |
| Additional extracted folders matching `*_assets_auto\manifest.json` | The current Metal Seahorse sample already includes one such manifest. Other extracted folders are not yet inventoried. | Collector manifests preserve archive provenance and discovered dependencies, which helps prove reference resolution paths across multiple dragons. | STRONGLY SUPPORTED | Provide or point me to more extracted folders only after the core sample is mapped. |
| Additional `.dat` files | `Dragon.dat` turned out to be SWF-style, so more `.dat` files are not automatically useful unless one of them proves to be a non-SWF companion to a runtime dragon asset. | Not needed yet. | STRONGLY SUPPORTED | Only surface them if you find a `.dat` with non-`FWS`/non-SWF magic that sits beside a runtime dragon asset. |
| Generated IDA pseudocode export or binary dumps | MCP access is currently sufficient for read-only analysis. | Not needed yet. | CONFIRMED | Only provide if MCP access changes or if you want an offline snapshot for archival. |
