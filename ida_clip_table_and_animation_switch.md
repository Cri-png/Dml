# IDA Clip Table and Animation Switch Bridge

Read-only IDA evidence from the active `DragonManiaLegends.exe.i64` database. No names, comments, types, or bytes were changed.

## Evidence Table

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_gorillabody_anim.bdae` owner `0x4790` | File-side owner has `u32[+0x54] = 33` and `s32[+0x58] = 0xCD8B8`; `0x4790 + 0x58 + 0xCD8B8 = 0xD20A0`. | The owner points to a `33`-entry table at `0xD20A0`. | `CONFIRMED` | Compare the same fields in another body-type animation BDAE. |
| `dragon_gorillabody_anim.bdae` table `0xD20A0..0xD23B8` | `33` contiguous `0x18` entries shaped as `stringPtr, 0, start_ms, end_ms, 0, 0`; includes `idle_basic`, `idle_walk`, `levelup`, `attack`, `win`, and other named states. | This is the shared animation clip/state range table. | `CONFIRMED` for shape and values | Prove the exact clock source that maps selected clip time to row-table sampling. |
| `0x7FF720952D00` | Pseudocode reads `count` from owner/base `+0x54`, relative offset from `+0x58`, computes table base as `base + 0x58 + rel`, walks entries with `i += 3` qwords (`0x18` stride), compares `entry[0]` to the requested clip name with `strcmp`, and returns the matching entry pointer. | The file-side clip table is directly consumed by executable clip-name lookup. | `CONFIRMED` | Follow returned pointers in callers to find where `start_ms/end_ms` are stored. |
| `0x7FF7215515C0` | The helper builds a `"custom_" + requestedName` string, scans runtime animation entries through `0x7FF720952D00`, and if no match is found scans again for the plain requested name. | Runtime clip selection supports custom override clips before falling back to shared/default entries. | `CONFIRMED` | Search BDAEs for `custom_*` clip entries and add a viewer warning/override indicator. |
| `0x7FF721552F60` | High-level switch/play wrapper calls `0x7FF7215515C0(a1, animName, &outIndex)`, checks current animation state, and updates active slot/bookkeeping fields before continuing through animation object vmethods. | Game-side playback is selected by string clip name, then resolved through the clip table. | `STRONGLY SUPPORTED` | Continue through the post-lookup calls to prove which object receives the selected entry and whether the time range is converted to clip-local time. |
| `0x7FF721DC86F0` | Script/property bridge recognizes `switchToAnim`, `loopEnabled`, and `currentAnimationSpeed`; `switchToAnim` extracts a string and calls `0x7FF721552F60(receiver, animName, 0, 0, 0)`. | There is an exposed high-level animation control API matching the viewer concept of selecting a named clip. | `CONFIRMED` | Check UI/game callers for the common clip names they pass. |
| `0x7FF720C99370` | The `SetNodeAnimation` route also uses `0x7FF720952D00`, then calls an animation-object vmethod at `+0x30` with the selected clip string, applies the returned clip/index through vmethod `+0x28`, and later computes `([object+0x2C] - [object+0x28]) / durationArg` before calling vmethod `+0x98`. | The selected animation object stores an active range at `+0x28/+0x2C`; these fields are strongly supported as the live clip start/end window. | `STRONGLY SUPPORTED` | Resolve the concrete vtable behind the animation object to prove the method that writes `+0x28/+0x2C`. |

## Viewer Implication

The viewer should not play a shared body-type animation BDAE as one global timeline by default. It should:

1. Resolve dragon `BODY_TYPE` to exact shared animation BDAE names.
2. Read the shared animation BDAE clip table.
3. Present named clips such as `idle_basic`, `idle_walk`, `levelup`, `attack`, and `win`.
4. Search for `custom_<clip>` before plain `<clip>` when the runtime asset provides custom overrides.
5. Use the selected clip object's active range as the next timing bridge, but keep full game-accurate timing marked incomplete until `+0x28/+0x2C` is tied to the row-table sampler.
