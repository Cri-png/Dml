# UI Dragon Image Bridge

This report tracks the executable-side UI helpers that appear relevant for a future asset browser or viewer which can browse dragons by logical identity instead of raw filenames.

## Evidence Table

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML IDB `0x7FF721C3FE60` | The Flash/UI bridge registers `getLocalizedText`, `setDragonPortrait`, `setFullBodyDragonImage`, and `setImageFromBdae` as sibling exported callbacks. | The game already exposes a coherent UI-facing bridge for text lookup plus dragon/asset image rendering. | CONFIRMED | Trace one UI caller for each callback if we need an exact ActionScript-side argument contract. |
| current DML IDB `0x7FF721C410E0` (`getLocalizedText`) | The callback consumes runtime string-key arguments and routes them through localization helpers such as `sub_7FF720BEA180` / `sub_7FF720BEA2A0` before returning text to the UI. | UI text for dragons should be modeled as localization-key lookup, not as direct asset-name formatting. | STRONGLY SUPPORTED | Recover one dragon-info UI caller and capture the exact key passed in. |
| current DML IDB `0x7FF721C455E0` (`setDragonPortrait`) | The callback reads a string argument from the UI argument block, reads a dragon-like descriptor with `sub_7FF720828D10`, builds a runtime object with vtable `off_7FF722DDEF68`, then submits it through `sub_7FF720A6AD40`. It also reads two integer-like parameters from preceding UI arguments. | `setDragonPortrait` is a real render-job submission path for portrait-style dragon imagery, not just a label stub. | STRONGLY SUPPORTED | Find the final consumer/type behind `off_7FF722DDEF68` and identify whether the string argument is a dragon ID, mesh stem, portrait asset name, or another logical image key. |
| current DML IDB `0x7FF721C45840` (`setFullBodyDragonImage`) | Similar to `setDragonPortrait`, but it builds a different runtime object with vtable `off_7FF722DDEF38`, reads two integer-like parameters and one float-like parameter from preceding UI arguments, then submits through the same `sub_7FF720A6AD40` service path. | `setFullBodyDragonImage` is the better candidate for a future full-dragon browser preview than `setDragonPortrait`, because it clearly carries a richer configuration payload. | STRONGLY SUPPORTED | Determine the exact meaning of the extra float/int arguments and whether the string argument is a dragon ID or asset stem. |
| current DML IDB `0x7FF721C45E50` (`setImageFromBdae`) | This callback also reads a string argument, a dragon/asset descriptor, two integer-like values, builds a third render object family, and submits it through `sub_7FF720A6AD40`. | The UI can ask the engine to render an image directly from a BDAE-linked asset path, not only from higher-level dragon portrait/full-body helpers. | STRONGLY SUPPORTED | Compare the accepted string values with a controlled viewer-side test once we can safely mimic the asset selection contract. |
| shared callee `0x7FF720A6AD40` | All three image callbacks end by submitting a constructed object through the same render-service style function. | The game likely uses one central UI image-render queue/service for dragon portraits, full-body images, and generic BDAE image requests. | STRONGLY SUPPORTED | Find the consumer of this submission function and identify the backing renderer or thumbnail cache path. |

## Current Best Interpretation

- `setDragonPortrait` is useful for confirming that the game has a logical "dragon portrait" render path.
- `setFullBodyDragonImage` is more directly relevant to a viewer/browser that wants to preview whole dragons.
- `setImageFromBdae` is the most asset-oriented path and may be the cleanest conceptual bridge for a future asset-browser preview mode.

## Viewer Implication

These callbacks suggest a clean long-term viewer split:

1. Identity resolution:
   - user query
   - `dragon_types.json`
   - localization

2. Preview mode selection:
   - portrait-like preview
   - full-body preview
   - direct BDAE image preview

3. Animation browsing:
   - once the body-type playback bridge is mature enough, a dragon browser could show the resolved dragon, then list the inherited shared animation family beside it

## Important Limitation

These functions prove there is a UI image-render bridge, but they do **not** yet prove a full animation-browsing bridge by themselves. They are still image/render job entry points. Animation browsing will still need:

- correct dragon identity resolution,
- correct shared animation family resolution,
- and the broader playback/sampling path that is still under reverse engineering.
