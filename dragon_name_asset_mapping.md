# Dragon Name to Asset Mapping

This report tracks how the game's real in-game dragon text appears to connect back to dragon IDs and asset stems.

The current goal is not only to find the right mesh or animation, but to let the viewer search and display dragons by the same identity the game uses.

## Current Best-Supported Chain

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `data.bud -> dragon_types.json` | Prior extraction and existing tooling already proved per-dragon entries include `ID`, `UID`, `MESHES`, `EGG_MESH`, `BODY_TYPE`, and other gameplay metadata. Example: `D_TIKI_2024` maps to mesh stems `dragon_tiki_2024_baby` and `dragon_tiki_2024`. | `dragon_types.json` is the authoritative identity bridge from mesh stems and asset filenames to the game's internal dragon ID. | CONFIRMED | Keep using `dragon_types.json` as the first lookup stage in the viewer. |
| `generated/cache/bud_asset_index.json` | The base `data.bud` index contains `localization_en.json`, `localization_it.json`, many other `localization_*.json` files, matching `localization_override_*.json` files, and also `player_names.json`. | The shipped display text almost certainly lives in localization tables, while custom/user-entered dragon naming is handled separately. | CONFIRMED | Extract `localization_en.json` and `localization_override_en.json` and inspect how dragon IDs or name keys are stored. |
| `generated/cache/bud_asset_index.json` around localization entries | `localization_en.json` is a large base table (`compressed_size = 592505`, `uncompressed_size = 2429680`), while `localization_override_en.json` is tiny (`compressed_size = 751`, `uncompressed_size = 1275`). | The game most likely uses a base localization table plus a small override layer for recent or patched strings. | STRONGLY SUPPORTED | Merge base and override when building the viewer's display-name resolver. |
| current DML IDB `0x7FF721C3FE60` | The Flash/UI bridge registers `getLocalizedText`, `setDragonPortrait`, `setFullBodyDragonImage`, and `setImageFromBdae` as sibling exported UI helpers. | The executable already separates text lookup from dragon image/asset presentation, which matches the viewer design we want. | CONFIRMED | Trace `getLocalizedText` callers that populate dragon-info UI panels if code-side proof of the final key path is needed. |
| current DML IDB `0x7FF721C410E0` (`getLocalizedText`) | This function handles runtime string-key lookup and pushes the resolved text back into the UI path through shared localization helpers such as `sub_7FF720BEA180` and `sub_7FF720BEA2A0`. | Dragon display names should be treated as localization results, not inferred from asset filenames. | STRONGLY SUPPORTED | Recover one concrete dragon-info UI caller and inspect the exact string key it passes into `getLocalizedText`. |
| local extracted `player_names.json` plus current DML IDB string `player_names.json` at `0x7FF72282CA38` | The extracted JSON contains entries like `{"STR_ID":"NICKNAME_001","EN":"Shellsie",...}` through `NICKNAME_100`, and the executable also contains `player_names.json` as a separate string resource, distinct from the UI `getLocalizedText` bridge. | `player_names.json` is concretely a nickname/custom-name string pool, not the dragon species-name table. | CONFIRMED | Keep nickname/custom-name logic separate from species-name localization in the viewer. |
| `reports/body_type_animation_assignment.md` plus existing resolver | Queries like `D_TIKI_2024` or `dragon_tiki_2024.bdae` already resolve from `dragon_types.json` into the correct mesh and `BODY_TYPE` animation family. | The viewer already has the correct first half of the identity chain; the missing half is the localized display-name layer. | CONFIRMED | Extend the resolver to optionally include localized name fields once localization tables are extracted. |

## Practical Viewer Rule

The viewer should eventually resolve dragon identity in this order:

1. User query:
   - dragon mesh stem
   - `.bdae` filename
   - internal dragon ID like `D_TIKI_2024`
2. `dragon_types.json`:
   - resolve authoritative dragon entry
   - collect `ID`, `UID`, `MESHES`, `EGG_MESH`, `BODY_TYPE`
3. Asset resolution:
   - load mesh, eye, shared animation, FX, and other dependencies from exact stems
4. Localization resolution:
   - load `localization_<lang>.json`
   - overlay `localization_override_<lang>.json`
   - resolve the dragon's displayed species name from the authoritative dragon identity
5. Optional rename layer:
   - if a future save/import path is supported, treat `player_names.json` or save-side rename data as a separate per-instance/custom-name layer

## What Is Proven vs Missing

### Proven

- Mesh and animation selection should start from `dragon_types.json`, not from guessed filenames.
- The shipped game contains explicit localization tables by language.
- The executable exposes a dedicated `getLocalizedText` UI path separate from dragon image helpers.
- `player_names.json` is a nickname/custom-name table and should not be conflated with shipped dragon species names.

### Not Yet Known

- The exact localization key shape for a dragon species name.
  - It may be directly `D_TIKI_2024`.
  - It may be derived from `UID = 1105`.
  - It may use a separate string key stored somewhere else in `dragon_types.json` or another table.
- The exact merge rule between `localization_en.json` and `localization_override_en.json` for dragon names.

## Best Next Step

The next highest-value step is to extract and inspect:

- `localization_en.json`
- `localization_override_en.json`

Then search them for at least:

- `D_TIKI_2024`
- `1105`
- `Masked Dragon`
- a few other already-known dragons

That will let the viewer expose:

- internal ID
- localized display name
- mesh stems
- shared animation family
- exact archive/file dependencies

through one deterministic identity model instead of loosely matched asset names.
