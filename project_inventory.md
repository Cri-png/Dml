# Project Inventory

## Scope
This first-pass inventory is limited to files directly relevant to the Dragon Mania Legends Metal Seahorse BRES/BDAE investigation that are currently visible from this machine:

- the current workspace;
- DML helper scripts on the Desktop;
- the extracted Metal Seahorse sample bundle on the Desktop;
- accessible base `Assets\GameData` files;
- the protected DLC archive directory after a read-only elevated listing/search;
- the active IDA database and matching executable.

I intentionally excluded unrelated non-DML Desktop files.

## Access Status

| Path | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `C:\Users\crist\Documents\Codex\2026-05-25\files-mentioned-by-the-user-list` | Workspace was effectively empty for DML inputs before this pass; `reports\` did not exist. | First-pass reports needed to be created from scratch inside the project folder. | CONFIRMED | Continue writing all generated reports and helper outputs under this workspace. |
| `C:\Users\crist\Desktop\metal_seahorse_assets_auto` | Read access succeeded. Visible files: `manifest.json`, runtime copy, extracted `Dragon.bdae`, `Dragon_Eye.bdae`, and the two recovered `.tga` files. | This is the main local sample bundle for the current dragon. | CONFIRMED | Use it as the baseline sample set for direct file comparison. |
| `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData` | Read access succeeded. Loose `.bdae`, `.bud`, `.pak`, `.txt`, and related files were listable. | Base installed GameData is directly readable and can supply base resources without asking for copies yet. | CONFIRMED | Inspect `Dragon.dat`, `Eye.bdae`, and material/effect `.bdae` files next. |
| `C:\Users\crist\AppData\Local\Packages\A278AB0D.DragonManiaLegends_h6adky7gbf63m\LocalState\dlcs` | Non-elevated `Test-Path` initially raised access denied. Elevated read-only listing/search then succeeded. 100+ `.pak` archives are present. | DLC archives are reachable for read-only analysis, but this path is permission-gated. | CONFIRMED | Reuse the same read-only elevated access when an archive-level search or extraction is needed. |
| IDA MCP active instance | `list_instances` returned reachable active DB `C:\Users\crist\Downloads\DragonManiaLegends.exe.i64`; `server_health` returned `status=ok`, `imagebase=0x7ff7a7cb0000`, `auto_analysis_ready=true`, `hexrays_ready=true`. | The current Dragon Mania Legends IDA database is reachable and ready for read-only static analysis. | CONFIRMED | Continue MCP-only analysis; do not rename/type/comment without permission. |

## Relevant Files

### Workspace

- `C:\Users\crist\Documents\Codex\2026-05-25\files-mentioned-by-the-user-list\reports\project_inventory.md`
- `C:\Users\crist\Documents\Codex\2026-05-25\files-mentioned-by-the-user-list\reports\needed_files.md`
- `C:\Users\crist\Documents\Codex\2026-05-25\files-mentioned-by-the-user-list\reports\ida_bres_pipeline.md`

### Desktop Helper Scripts and Direct Inputs

- `C:\Users\crist\Desktop\dml_collect_assets.py` - 16,208 bytes
- `C:\Users\crist\Desktop\dml_collect_assets_auto.py` - 18,600 bytes
- `C:\Users\crist\Desktop\dml_collect_assets_auto_v3.py` - 18,635 bytes
- `C:\Users\crist\Desktop\extract_dml_bud.py` - 5,732 bytes
- `C:\Users\crist\Desktop\extract_selected_dml_bud.py` - 2,274 bytes
- `C:\Users\crist\Desktop\find_dml_asset.py` - 2,309 bytes
- `C:\Users\crist\Desktop\find_dml_bud_everywhere.py` - 2,183 bytes
- `C:\Users\crist\Desktop\inspect_bres_header.py` - 3,131 bytes
- `C:\Users\crist\Desktop\inspect_bres_track_links.py` - 3,558 bytes
- `C:\Users\crist\Desktop\inspect_bres_track_targets.py` - 3,947 bytes
- `C:\Users\crist\Desktop\inspect_bres_track_targets_fixed.py` - 5,908 bytes
- `C:\Users\crist\Desktop\list_bres_animation_clips.py` - 3,001 bytes
- `C:\Users\crist\Desktop\search_dml_bud_contents.py` - 4,246 bytes
- `C:\Users\crist\Desktop\trace_bres_strings.py` - 3,405 bytes
- `C:\Users\crist\Desktop\trace_bres_true_refs.py` - 3,489 bytes

### Extracted Metal Seahorse Sample Bundle

- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\manifest.json` - 19,382 bytes
- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\runtime_source\dragon_metal_seahorse_runtime.bdae` - 1,225,400 bytes
- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\GameData\Dragon.bdae` - 18,736 bytes
- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\GameData\Dragon_Eye.bdae` - 3,552 bytes
- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\game_dlc_upd74_w8_default_17\dragon_metal_seahorse.tga` - 349,680 bytes
- `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\game_dlc_upd74_w8_default_17\eye_metal_seahorse.tga` - 87,536 bytes

### Base `Assets\GameData` Files Currently Visible

- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\ApplyFog.bdae` - 2,488 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\crm_game_object_data.txt` - 143,460 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\data.bud` - 10,200,187 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\data_noesis.bud` - 17,934,553 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\DefaultEffects.bdae` - 59,992 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon.bdae` - 18,736 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon_Eye.bdae` - 3,552 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Eye.bdae` - 3,520 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\FogMask.bdae` - 2,408 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\game_dlc0.bud` - 102,840,256 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\game_dlc_splash_art.bud` - 1,083,622 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\gameswf_effects.bdae` - 39,360 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\ImGui.bdae` - 1,720 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\MaskedRgbVertexTextureAnim.bdae` - 18,088 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\MaskedVertexTextureAnim.bdae` - 16,528 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\MaskedVertexTextureAnim_erosion.bdae` - 14,864 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\MaskFade.bdae` - 2,496 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\NoesisCustomEffects.bdae` - 9,792 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\NoesisEffects.bdae` - 60,488 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\shaders_DX.pak` - 480,054 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\shaders_DX_ForceColor.pak` - 617,998 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Simple_Darken.bdae` - 3,080 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Simple_NoAlphaSplit.bdae` - 3,096 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\SkinnedOneSided.bdae` - 2,352 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\TextureAnim.bdae` - 15,168 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\TextureAnim_erosion.bdae` - 16,272 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\ui_textures.bud` - 35,886,967 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\vertexAnim.bdae` - 15,664 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\vertexAnim_erosion.bdae` - 16,000 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\VertexTextureAnim.bdae` - 13,160 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\VertexTextureAnim_erosion.bdae` - 12,584 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Water.bdae` - 3,072 bytes
- `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\ycbcr.bdae` - 2,096 bytes

### Protected DLC Archive Directory (`LocalState\dlcs`) - Exact Top-Level `.pak` Files Currently Visible

- `game_dlc_anniversary_w8_default_10.pak` - 9,074,404 bytes
- `game_dlc_big_bad_boss_w8_default_82.pak` - 24,046,436 bytes
- `game_dlc_boardgame_w8_default_26.pak` - 23,522,621 bytes
- `game_dlc_box_gacha_sequence_w8_default_3.pak` - 18,805,256 bytes
- `game_dlc_christmas_w8_default_4.pak` - 4,091,066 bytes
- `game_dlc_critters_b_w8_default_1.pak` - 120,336 bytes
- `game_dlc_critters_w8_default_1.pak` - 89,442 bytes
- `game_dlc_dragon_anims_w8_default_1.pak` - 4,627,610 bytes
- `game_dlc_dragon_runner_w8_default_29.pak` - 2,078,303 bytes
- `game_dlc_dungeon_w8_default_1.pak` - 1,875,331 bytes
- `game_dlc_dungeongraph_w8_default_1.pak` - 1,455,401 bytes
- `game_dlc_graphevent_w8_default_7.pak` - 20,695,192 bytes
- `game_dlc_puzzle_grid_w8_default_9.pak` - 32,168,355 bytes
- `game_dlc_returninggraph_w8_default_1.pak` - 3,930,102 bytes
- `game_dlc_tycoonisland_crystal_w8_default_1.pak` - 4,417,888 bytes
- `game_dlc_tycoonisland_dieselpunk_w8_default_1.pak` - 4,426,501 bytes
- `game_dlc_tycoonisland_divine_w8_default_83.pak` - 44,601,817 bytes
- `game_dlc_tycoonisland_floating_w8_default_1.pak` - 2,898,050 bytes
- `game_dlc_tycoonisland_greek_w8_default_2.pak` - 6,646,925 bytes
- `game_dlc_tycoonisland_iceland_w8_default_1.pak` - 2,954,045 bytes
- `game_dlc_tycoonisland_molten_w8_default_1.pak` - 3,929,651 bytes
- `game_dlc_tycoonisland_toy_w8_default_1.pak` - 2,755,054 bytes
- `game_dlc_tycoonisland_turtle_w8_default_1.pak` - 3,497,177 bytes
- `game_dlc_tycoonisland_zengarden_w8_default_1.pak` - 3,172,030 bytes
- `game_dlc_upd10_w8_default_1.pak` - 4,403,095 bytes
- `game_dlc_upd11_w8_default_1.pak` - 4,040,439 bytes
- `game_dlc_upd12_w8_default_1.pak` - 3,650,900 bytes
- `game_dlc_upd13_w8_default_1.pak` - 19,519,446 bytes
- `game_dlc_upd14_w8_default_1.pak` - 1,436,157 bytes
- `game_dlc_upd15_w8_default_1.pak` - 2,286,072 bytes
- `game_dlc_upd16_w8_default_1.pak` - 11,500,612 bytes
- `game_dlc_upd17_w8_default_1.pak` - 5,257,728 bytes
- `game_dlc_upd18_w8_default_1.pak` - 3,656,892 bytes
- `game_dlc_upd19_w8_default_1.pak` - 3,697,242 bytes
- `game_dlc_upd20_w8_default_1.pak` - 8,995,460 bytes
- `game_dlc_upd21_w8_default_1.pak` - 7,629,310 bytes
- `game_dlc_upd22_w8_default_1.pak` - 996,219 bytes
- `game_dlc_upd23_w8_default_1.pak` - 3,169,872 bytes
- `game_dlc_upd24_w8_default_1.pak` - 5,492,069 bytes
- `game_dlc_upd26_w8_default_1.pak` - 8,681,904 bytes
- `game_dlc_upd27_w8_default_1.pak` - 6,639,322 bytes
- `game_dlc_upd28_w8_default_1.pak` - 5,989,064 bytes
- `game_dlc_upd30_w8_default_1.pak` - 13,146,499 bytes
- `game_dlc_upd31_w8_default_1.pak` - 4,196,466 bytes
- `game_dlc_upd32_w8_default_1.pak` - 5,524,467 bytes
- `game_dlc_upd33_w8_default_1.pak` - 5,007,210 bytes
- `game_dlc_upd35_w8_default_1.pak` - 11,493,950 bytes
- `game_dlc_upd36_w8_default_2.pak` - 5,728,097 bytes
- `game_dlc_upd37_w8_default_1.pak` - 7,581,217 bytes
- `game_dlc_upd38_w8_default_1.pak` - 4,514,719 bytes
- `game_dlc_upd39_w8_default_1.pak` - 6,820,697 bytes
- `game_dlc_upd4_w8_default_18.pak` - 6,711,050 bytes
- `game_dlc_upd40_w8_default_1.pak` - 2,864,981 bytes
- `game_dlc_upd41_w8_default_1.pak` - 6,173,906 bytes
- `game_dlc_upd42_w8_default_1.pak` - 7,157,742 bytes
- `game_dlc_upd43_w8_default_1.pak` - 1,372,931 bytes
- `game_dlc_upd44_w8_default_1.pak` - 5,903,231 bytes
- `game_dlc_upd45_w8_default_1.pak` - 312,467 bytes
- `game_dlc_upd46_w8_default_4.pak` - 5,260,262 bytes
- `game_dlc_upd47_w8_default_1.pak` - 3,683,246 bytes
- `game_dlc_upd48_w8_default_1.pak` - 3,058,181 bytes
- `game_dlc_upd49_w8_default_1.pak` - 3,821,078 bytes
- `game_dlc_upd5_w8_default_1.pak` - 24,577,546 bytes
- `game_dlc_upd50_w8_default_1.pak` - 7,214,236 bytes
- `game_dlc_upd51_w8_default_1.pak` - 7,893,379 bytes
- `game_dlc_upd52_w8_default_1.pak` - 10,696,390 bytes
- `game_dlc_upd53_w8_default_1.pak` - 7,542,847 bytes
- `game_dlc_upd54_w8_default_1.pak` - 7,740,359 bytes
- `game_dlc_upd55_w8_default_1.pak` - 9,358,953 bytes
- `game_dlc_upd56_w8_default_1.pak` - 8,734,527 bytes
- `game_dlc_upd57_w8_default_1.pak` - 5,625,832 bytes
- `game_dlc_upd58_w8_default_1.pak` - 6,920,158 bytes
- `game_dlc_upd59_w8_default_1.pak` - 4,682,055 bytes
- `game_dlc_upd6_w8_default_1.pak` - 4,696,249 bytes
- `game_dlc_upd60_w8_default_1.pak` - 6,885,842 bytes
- `game_dlc_upd61_w8_default_1.pak` - 12,535,468 bytes
- `game_dlc_upd62_w8_default_1.pak` - 8,578,862 bytes
- `game_dlc_upd63_w8_default_1.pak` - 14,197,064 bytes
- `game_dlc_upd64_w8_default_1.pak` - 7,376,766 bytes
- `game_dlc_upd65_w8_default_1.pak` - 9,924,266 bytes
- `game_dlc_upd66_w8_default_1.pak` - 9,563,108 bytes
- `game_dlc_upd67_w8_default_1.pak` - 13,058,507 bytes
- `game_dlc_upd68_w8_default_1.pak` - 8,626,580 bytes
- `game_dlc_upd69_w8_default_1.pak` - 6,606,997 bytes
- `game_dlc_upd7_w8_default_1.pak` - 7,321,086 bytes
- `game_dlc_upd70_w8_default_2.pak` - 9,602,058 bytes
- `game_dlc_upd71_w8_default_3.pak` - 9,239,891 bytes
- `game_dlc_upd72_w8_default_7.pak` - 9,667,336 bytes
- `game_dlc_upd73_w8_default_11.pak` - 9,618,511 bytes
- `game_dlc_upd74_w8_default_17.pak` - 15,499,926 bytes
- `game_dlc_upd75_w8_default_14.pak` - 11,948,093 bytes
- `game_dlc_upd76_w8_default_15.pak` - 11,467,874 bytes
- `game_dlc_upd77_w8_default_23.pak` - 20,016,932 bytes
- `game_dlc_upd78_w8_default_18.pak` - 14,659,337 bytes
- `game_dlc_upd79_w8_default_27.pak` - 22,925,599 bytes
- `game_dlc_upd8_w8_default_1.pak` - 10,409,460 bytes
- `game_dlc_upd80_w8_default_80.pak` - 16,772,045 bytes
- `game_dlc_upd81_w8_default_56.pak` - 20,259,542 bytes
- `game_dlc_upd82_w8_default_19.pak` - 11,281,632 bytes
- `game_dlc_upd9_w8_default_1.pak` - 6,321,127 bytes
- `game_dlc1_addon_w8_default_1.pak` - 10,747,658 bytes
- `game_dlc2_plant_w8_default_1.pak` - 6,090,094 bytes
- `game_dlc3_metal_w8_default_1.pak` - 7,292,075 bytes
- `game_dlc4_energy_w8_default_1.pak` - 8,094,080 bytes
- `game_dlc5_void_w8_default_1.pak` - 13,323,064 bytes
- `game_dlc6_legendary_w8_default_1.pak` - 6,335,206 bytes
- `game_dlc7_upd1_w8_default_1.pak` - 2,515,147 bytes
- `game_dlc8_upd2_w8_default_1.pak` - 5,163,864 bytes
- `game_dlc9_upd3_w8_default_2.pak` - 14,383,215 bytes
- `voxpack_board_game_w8_default_1.pak` - 1,696,376 bytes
- `voxpack_divine_w8_default_1.pak` - 3,919,988 bytes
- `voxpack_dragon_runner_w8_default_1.pak` - 2,021,291 bytes
- `voxpack_gorilla_w8_default_1.pak` - 677,203 bytes
- `voxpack_graphevent_w8_default_2.pak` - 3,468,130 bytes
- `voxpack_puzzle_grid_w8_default_1.pak` - 1,168,897 bytes
- `voxpack_seahorse_w8_default_1.pak` - 435,970 bytes
- `voxpack_tyrant_w8_default_1.pak` - 167,189 bytes
- `voxpack_upd10_w8_default_1.pak` - 123,682 bytes
- `voxpack_upd13_w8_default_1.pak` - 3,585,400 bytes
- `voxpack_upd16_w8_default_1.pak` - 1,714,847 bytes
- `voxpack_upd17_w8_default_1.pak` - 135,610 bytes
- `voxpack_upd19_w8_default_1.pak` - 226,569 bytes
- `voxpack_upd3_w8_default_1.pak` - 3,714,630 bytes
- `voxpack_upd4_w8_default_1.pak` - 185,587 bytes
- `voxpack_upd40_w8_default_1.pak` - 150,525 bytes
- `voxpack_upd43_w8_default_1.pak` - 343,514 bytes
- `voxpack_upd5_w8_default_1.pak` - 3,939,134 bytes
- `voxpack_upd51_w8_default_1.pak` - 1,125,499 bytes
- `voxpack_upd56_w8_default_1.pak` - 353,701 bytes
- `voxpack_upd67_w8_default_1.pak` - 347,503 bytes
- `voxpack_upd68_w8_default_1.pak` - 1,698,206 bytes
- `voxpack_upd74_w8_default_1.pak` - 1,949,610 bytes
- `voxpack_upd77_w8_default_1.pak` - 2,679,361 bytes
- `voxpack_upd78_w8_default_2.pak` - 902,174 bytes
- `voxpack_upd9_w8_default_1.pak` - 964,555 bytes
- `voxpack_w8_default_1.pak` - 11,601,215 bytes

### Active IDA Database / Executable

- `C:\Users\crist\Downloads\DragonManiaLegends.exe.i64` - active IDB
- `C:\Users\crist\Downloads\DML TEST\DragonManiaLegends.exe` - matching input executable

## BDAE / TGA Size and SHA256

| Path | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `C:\Users\crist\Desktop\metal_seahorse_assets_auto\runtime_source\dragon_metal_seahorse_runtime.bdae` | Size `1,225,400` bytes (`0x12B2B8`); SHA256 `66a8896ee8fe9c0bb4d9d3781be47aedb6cedc33cc3bf70b1dc485544cebe01b`. | Main runtime BRES/BDAE sample for this investigation. | CONFIRMED | Use as the baseline for section/track/object mapping. |
| `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon.bdae` | Size `18,736` bytes; SHA256 `f1ac2677d7db3681a18bfdd7b9e67fc27ea0b7492c379f2822b61e1183d286fd`. | Base dragon resource referenced by the runtime BDAE. | CONFIRMED | Compare strings/sections against the runtime sample next. |
| `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon_Eye.bdae` | Size `3,552` bytes; SHA256 `527f8edf710e8d9c56989aa4fe182bc2c34ad7da419899696e18673af58b93d4`. | Base eye resource referenced by the runtime BDAE. | CONFIRMED | Compare against `Eye.bdae` and runtime eye-node references next. |
| `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\game_dlc_upd74_w8_default_17\dragon_metal_seahorse.tga` | Size `349,680` bytes; SHA256 `728565f533b0c1f8b9d9833a5f872a15d0824cfbc5f5f9529eb1a0bcf1f0a5b6`. | Body texture payload recovered from DLC archive `game_dlc_upd74_w8_default_17.pak`. | CONFIRMED | Inspect header/body bytes and compare against IDA texture-loader code. |
| `C:\Users\crist\Desktop\metal_seahorse_assets_auto\assets\game_dlc_upd74_w8_default_17\eye_metal_seahorse.tga` | Size `87,536` bytes; SHA256 `911d5a973d7d8c40d3df143dccd92a5a73a1f532be7fa9520b9df46903406b99`. | Eye texture payload recovered from the same DLC archive as the body texture. | CONFIRMED | Compare header/body differences against the body texture and look for format markers. |

## Present / Missing

| Path or asset name | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_metal_seahorse_runtime.bdae` | Present at `C:\Users\crist\Desktop\metal_seahorse_assets_auto\runtime_source\dragon_metal_seahorse_runtime.bdae`. | Core current sample is locally available. | CONFIRMED | Begin direct structure comparison against `Dragon.bdae` and `Dragon_Eye.bdae`. |
| `Dragon.bdae` | Present both in the sample bundle copy and in installed `GameData`. | Base body template is locally available and does not need to be provided manually. | CONFIRMED | Compare runtime-only strings/records vs base template-only content. |
| `Dragon_Eye.bdae` | Present both in the sample bundle copy and in installed `GameData`. | Base eye template is locally available and does not need to be provided manually. | CONFIRMED | Compare runtime eye binding paths vs base eye records. |
| `dragon_metal_seahorse.tga` | Present in extracted sample bundle; DLC search also found the same name in `game_dlc_upd74_w8_default_17.pak`. | Body texture dependency is resolved to a concrete archive and extracted file. | CONFIRMED | Inspect bytes and locate the loader path in IDA. |
| `eye_metal_seahorse.tga` | Present in extracted sample bundle; DLC search also found the same name in `game_dlc_upd74_w8_default_17.pak`. | Eye texture dependency is resolved to a concrete archive and extracted file. | CONFIRMED | Inspect bytes and locate the loader path in IDA. |
| `shadow_dragon.tga` | Missing as a loose file in the sample bundle and base `GameData`; no hit in base archive listings searched (`data.bud`, `data_noesis.bud`, `game_dlc0.bud`, `game_dlc_splash_art.bud`, `ui_textures.bud`); no hit in elevated DLC archive-name search for `shadow_dragon.tga`. | The shadow texture dependency is unresolved and currently not available from the scanned locations. | STRONGLY SUPPORTED | Search alternate WindowsApps versions, other extracted asset folders, or any additional archive/index sources for the exact string `shadow_dragon.tga`. |
| IDA MCP database | Reachable and active at `C:\Users\crist\Downloads\DragonManiaLegends.exe.i64`. | Static executable-side analysis can continue immediately. | CONFIRMED | Keep using MCP read-only; do not apply persistent edits without permission. |

