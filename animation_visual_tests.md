# Animation Visual Tests

Read-only/generated-output update from 2026-06-18. These tests are visual diagnostics only; they do not change the default viewer path.

## Summary

The new controller-propagation visual tests did not produce a convincing correction. They are useful anyway because they falsify a too-simple fix: applying obvious skipped controller deltas directly to palette slots is not enough to reproduce game-equivalent playback.

The more important result is timing-related. `clip-local-ms` produces visible transform variation, but the sampled motion is suspiciously similar across different clips. `clip-absolute-ms` frequently clamps to constant values for clips such as `win` and `death`. This strongly suggests that the remaining playback issue includes the engine's clip-window/time remap and segment/evaluator selection, not only hierarchy propagation.

## Generated Outputs

| Output | Path | Interpretation | Confidence |
| --- | --- | --- | --- |
| Attack controller variants | `generated/experimental/dragon_tiki_2024_runtime/controller_visual_tests_attack/controller_variant_contact_sheet.png` | `attack` local-time samples barely change; controller variants do not materially improve the image. | `EXPERIMENTAL` |
| Idle-walk local-time variants | `generated/experimental/dragon_tiki_2024_runtime/controller_visual_tests_idle_walk/controller_variant_contact_sheet.png` | `idle_walk` local-time samples again look similar to `attack`; this is suspicious and points to an unresolved local clip remap. | `EXPERIMENTAL` |
| Idle-walk absolute-time variants | `generated/experimental/dragon_tiki_2024_runtime/controller_visual_tests_idle_walk_absolute/controller_variant_contact_sheet.png` | Absolute-time sampling only produces a few IK/roll deltas; visual result remains close to slot-only. | `EXPERIMENTAL` |
| Win absolute-time variants | `generated/experimental/dragon_tiki_2024_runtime/controller_visual_tests_win_absolute/controller_variant_contact_sheet.png` | Absolute-time `win` sample is effectively constant under the current exporter. | `EXPERIMENTAL` |
| Death absolute-time variants | `generated/experimental/dragon_tiki_2024_runtime/controller_visual_tests_death_absolute/controller_variant_contact_sheet.png` | Absolute-time `death` sample is effectively constant under the current exporter. | `EXPERIMENTAL` |

## Evidence Table

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `viewer_prototype/render_tiki_controller_visual_tests.py` | New script renders four variants: `slot_only`, `body_root_delta`, `body_root_rotation_delta`, and `body_plus_leg_controllers`. | Provides a safe falsifiable visual test for skipped-controller hypotheses without changing GUI defaults. | `CONFIRMED` | Keep this as a diagnostic tool while solving the real hierarchy/remap. |
| `attack` with `clip-local-ms` | Variance scan: `29` transform nodes vary; largest non-helper motion includes `body_root-node ~= 0.164`, `wingR01-node ~= 0.0396`, `legLF02-node ~= 0.0307`, `Tail_bone03-node ~= 0.0282`. | The exporter can produce changing transforms, but the visual result is still subtle and not game-equivalent. | `STRONGLY SUPPORTED` | Tie local-time sampling to engine clip remap before trusting clip-local output. |
| `idle_walk` with `clip-local-ms` | Variance scan is nearly identical to `attack` local-time output. | Current `clip-local-ms` is likely a diagnostic stretch/remap, not the real state-specific engine sample path. | `STRONGLY SUPPORTED` | Follow the clip selected entry through `0x7FF7209FBC20` / `0x7FF7209F2410` into segment-local sampling. |
| `idle_walk` with `clip-absolute-ms` | Only `5` nodes vary above threshold; largest are `legRB_IK-node ~= 1.675`, `legLB_IK-node ~= 1.243`, and tiny toe/heel deltas. | Absolute-time sampling hits different data, but appears to clamp or miss most ordinary channels. | `STRONGLY SUPPORTED` | Determine whether row times are segment-local, clip-local, absolute-global, or materialized-payload-local after `9EB180`. |
| `win/death` with `clip-absolute-ms` | No transform nodes varied above threshold. | Current absolute-time sampling is not sufficient for those named clips. | `CONFIRMED` for current exporter behavior, `NOT YET KNOWN` for true engine behavior | Resolve exact time remap and segment materialization before judging those clips. |
| visual controller variants | `body_root_delta` and leg-controller variants preserve the silhouette but do not visibly correct or unlock animation. | The full BRES hierarchy/source-matrix mapping is required; simple name-prefix propagation is not enough. | `STRONGLY SUPPORTED` | Parse actual node parent records or recover source matrix pointer list feeding `0x7FF720A60020`. |

## Current Conclusion

Do not patch the GUI to use these controller heuristics as a fix. Keep them as generated diagnostics only.

The next real patch should target the time/hierarchy boundary:

1. Recover the exact clip/segment time remap used after named clip selection.
2. Parse the full named BRES node hierarchy for Tiki/Gorilla body rigs.
3. Evaluate all `52` shared transform nodes into that hierarchy.
4. Derive the `24` skin-palette source matrices from the evaluated graph.
5. Then compose final palette matrices using the `0x7FF720A60020`-style bind/source loop.

## Time Remap Diagnostic Follow-Up - 2026-06-18

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `generated/experimental/dragon_tiki_2024_runtime/time_remap/gorilla_time_remap.md` | `clip-local-ms` makes all `33` clips overlap all `62` decoded transform tracks, but many clips share the same motion signature. `clip-absolute-ms` clamps almost every clip after `idle_walk` to zero varying transform tracks. | The suspicious visual sameness is now reproducible numerically. The exporter has two useful diagnostics, but neither is the final game remap. | `CONFIRMED` | Add visible labels in GUI/debug output showing which time domain is being used. |
| row axes in `dragon_gorillabody_anim.bdae` | Decoded row axes start at `0` and usually end at short values such as `5`, `10`, `201`, or `250`, while the named clip table spans `0..98067`. | The game likely remaps selected clip state into local row/sample windows through the materialized segment/evaluator layer. | `STRONGLY SUPPORTED` | Continue IDA read-only from `9FBC20 -> 9F2410 -> 952E70 -> 9EB180`. |

Viewer implication: live preview can be added soon as an experimental window, but it should expose the timing mode honestly. The clean default should remain static mesh preview until `engine-remap` is reproduced.
