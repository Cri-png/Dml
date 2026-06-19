# Track To Runtime Bridge

## Current IDB Runtime Descriptor Refinement - 2026-06-12

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current IDB `0x7FF72094FDAE-0x7FF72094FDC4` | The case-12 path computes `r9 = r13 + s32[r13+0xC0] + (index*3 + 0x18) * 8`, equivalent to `owner + rel + 0xC0 + index*0x18`. | The runtime descriptor table shape is now proven in the active IDB: owner-relative table plus `0x18` stride. | CONFIRMED | Find the population code that fills this table and assigns indices/names. |
| current IDB `0x7FF72094FDCD` | The selector byte is read from `byte ptr [r9+0x10]`. | The runtime selector is inside the cooked `0x18` descriptor, not the raw file-side `0x28` track record. | CONFIRMED | Trace stores into `descriptor+0x10`. |
| current IDB `0x7FF72094FDD2-0x7FF72094FE7F` | Selector `0/1/2/3` calls builder-interface slots `+0x168/+0x170/+0x178/+0x180`; the constructed/result object is returned through `var_A8`. | The named lookup reaches a four-way cooked object builder before downstream value evaluation. | CONFIRMED | Resolve the builder interface object in `var_1F0` and map each slot to concrete evaluator-family vtables. |
| current IDB `0x7FF72094EBA8-0x7FF72094EBAC` | The function stores `var_1F0 = arg0 + 8`; the selector dispatch later dereferences `[var_1F0]` and calls methods on that object's vtable. | The selector builder/helper object is owned by the first argument to `sub_7FF72094EB20` at offset `+8`. | CONFIRMED | Trace callers of `sub_7FF72094EB20` to find who initializes `arg0+8`. |
| current IDB evaluator-family blocks near `0x7FF722D333B0` | With vptr alignment at block `+0x18`, evaluator slots `+0x60/+0x68` are direct/blended output methods and `+0x90/+0x98` are higher-level timing wrappers. | The constructed evaluator families can now be interpreted without the earlier slot-offset confusion. | STRONGLY SUPPORTED | Connect one cooked descriptor for `Lwing_bone01-node-rotation` or `head_ctrl-node-rotation` to a specific evaluator-family block. |

## Target Track

Primary target in this pass:

- `Lwing_bone01-node-rotation`

## File-Side Track Record Proof Across Two Runtime Samples

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal Seahorse `0x2000 -> 0x35C0` | String offset `0x2000` (`8192`) is `Lwing_bone01-node-rotation`; the matching `0x28` track record is at `0x35C0` with `inputRel=2980`, `outputRel=3004`, `extraRel=3016`, and absolute targets `0xB354`, `0xB36C`, `0xB378`. | The original target track remains a solid file-side anchor. | CONFIRMED | Keep using it as the main named-track bridge target. |
| Crystal Lady `0x1FB4 -> 0x36F0` | String offset `0x1FB4` (`8116`) is the same track name; the matching `0x28` track record is at `0x36F0` with `inputRel=2412`, `outputRel=2436`, `extraRel=2448`, and absolute targets `0xBCC4`, `0xBCDC`, `0xBCE8`. | The same named track exists in the second runtime sample with the same visible record shape. | CONFIRMED | Compare the actual payload bytes later to test whether the same decoder family is reused. |
| both runtime samples | The target track's record is part of a contiguous transform-track array starting at `records_start + 0x10`, with fixed `0x28` stride in both files. | The file-side target-record type is stable across runtime dragon BDAEs. | CONFIRMED | Keep using this to reject false candidate record owners. |

## Payload Pattern Around The Target Record

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| both runtime samples, target record | `outputRel - inputRel = 24`. | The first two target payload references are packed in a fixed local step. | CONFIRMED | Match the 24-byte step against runtime-side packed sample structures. |
| both runtime samples, target record | `extraRel - outputRel = 12`. | The optional third target sits immediately after the output payload cluster rather than far away in the runtime payload arena. | CONFIRMED | Compare that 12-byte step against decoder-side nested relative structures. |
| all currently recovered non-zero `extraRel` tracks | The same `24` then `12` spacing pattern holds for every current non-zero `extraRel` transform track in both samples. | The target-track pattern is not unique noise; it generalizes across the selective `extraRel` subset. | CONFIRMED | Keep using `extraRel` tracks as the best bridge candidates. |

## Why The Runtime Descriptor Is Not The Raw Track Record

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| on-disk `0x28` track records, offset `+0x10` | For both target records, the dword at `+0x10` is `1` (`outputCount`). More broadly, the visible transform-track records in both samples currently show `outputCount = 1`. | The raw file-side track record does not have a `+0x10` field that can explain the executable-side `0..3` dispatch selector. | CONFIRMED | Continue treating the runtime `0x18` descriptor as a distinct structure. |
| executable-side case 12 | In `sub_7FF7A7ECEB20`, the matched runtime descriptor is `0x18` bytes wide and the byte at `+0x10` dispatches among four handlers. | The executable-side selector is read from a smaller cooked/runtime descriptor family, not directly from the visible file-side `0x28` track record. | CONFIRMED | Find the constructor or translator that produces the `0x18` runtime descriptor table. |
| `0x7FF7A7EDCC30` / `0x7FF7A7EDDA10` | The decoder-side structure reached after the bridge uses `*(int *)(base + 12)` with `base + 28` semantics and `*(int *)(base + 36)` as a live nested relative pointer source. In the raw on-disk `0x28` record, offset `+0x24` (`36`) is currently `extra2 = 0`, not a live relative. | The object fed into the decoder is not the untouched on-disk `0x28` bytes. There is at least one cooked/relocated record form between file-side metadata and decoder consumption. | CONFIRMED | Find the routine that rewrites or rebuilds this cooked record form. |

## Runtime-Side Name Bridge

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7ECFD00-0x7FF7A7ECFD08` | Case 12 compares `strcmp([runtime_desc_name], [r12+1])`. | The executable bridges a file-derived name string to a runtime descriptor by exact text match. | CONFIRMED | Prove the exact source-object type feeding `r12`. |
| `0x7FF7A7ECFCEA-0x7FF7A7ECFDC4` | The runtime descriptor array has `count = *(int *)(owner + 0xBC)`, `rel = *(int *)(owner + 0xC0)`, `stride = 0x18`, and matched record `r9 = owner + rel + 0xC0 + index * 0x18`. | The case-12 lookup is against a compact runtime table rather than a direct walk over raw file records. | CONFIRMED | Recover the table-population code. |
| `0x7FF7A7ECFDCD` | The matched runtime descriptor byte at `+0x10` is consumed immediately for local dispatch. | The bridge reaches a runtime-local per-descriptor mode/type field before any quaternion decoder is chosen. | CONFIRMED | Identify where that byte is assigned. |

## Selector-Path Refinement

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7ECFDD2-0x7FF7A7ECFE7F` | Selector `0 -> +0x168 -> EDCC30`, `1 -> +0x170 -> EDDA10`, `2 -> +0x178 -> ECD110 -> EDCC30 -> consumer`, `3 -> +0x180 -> ECD090 -> EDDA10 -> consumer`. | The target-track bridge definitely reaches a four-way packed-value dispatch stage. | CONFIRMED | Determine the actual selector value used by `Lwing_bone01-node-rotation`. |
| sibling runtime-descriptor code | Other nearby runtime-descriptor families also use a byte at `+0x10` as compact per-entry behavior/type information. | The `+0x10` byte is best treated as a small runtime mode field, not as a direct copy of the raw file-side layout. | STRONGLY SUPPORTED | Find a constructor that derives this field from parsed BRES metadata. |

## Ordinary Shared-Track Anchors In `dragon_gorillabody_anim.bdae`

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `head_ctrl-node-rotation`: `recordOffset = 0x4DC0` | `inputRel = 0xD14`; qword at `recordOffset + inputRel + 0x24 = 0x5AF8` is `0x0010000000000041`, which parses as `stride = 0x10`, `baseOffset = 0`, `rowIndex = 0x41`. | One ordinary shared-body rotation track is now anchored to an exact file-side descriptor qword. | CONFIRMED | Match `stride = 16`, `row = 0x41` against one concrete runtime rotation decode/sampler family. |
| `body_root-node-translation`: `recordOffset = 0x49B0` | `inputRel = 0xB34`; qword at `recordOffset + inputRel + 0x24 = 0x5508` is `0x000C00000000000D`, which parses as `stride = 0x0C`, `baseOffset = 0`, `rowIndex = 0x0D`. | One ordinary shared-body translation track is now anchored to an exact file-side descriptor qword. | CONFIRMED | Match `stride = 12`, `row = 0x0D` against the runtime translation decode/sampler family. |
| `IKRFChain-node-rotation`: `recordOffset = 0x4F10` | `inputRel` descriptor qword at `0x6230` is `0x0004000000000083` (`stride = 4`, `row = 0x83`), while `extraRel` descriptor qword at `0x6254` is `0x0000000800000004` (`baseOffset = 8`, `row = 0x04`). | The already-known special-case subset now has an exact descriptor-qword anchor that can be compared directly against the ordinary families. | CONFIRMED | Keep using this as the clean contrast case when the cooked descriptor builder is recovered. |

## Current DML Handler-Family Map

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML imagebase `0x7FF72094FDD2-0x7FF72094FE7F` | In the active DML IDB, the case-12 selector byte dispatches exactly as: `0 -> vtable + 0x168`, `1 -> +0x170`, `2 -> +0x178`, `3 -> +0x180`. | The cooked runtime descriptor byte at `+0x10` is a real small selector into four concrete handler slots. | CONFIRMED | Recover the routine that writes this byte for ordinary shared-body tracks. |
| handler base `0x7FF722D33788` | Slots are `+0x168 -> 0x7FF720958550 -> 0x7FF72095C810`, `+0x170 -> 0x7FF72094CA60 -> 0x7FF72095CFA0 -> sink`, `+0x178 -> 0x7FF72094C9E0 -> 0x7FF72095C810 -> sink`, `+0x180 -> 0x7FF7209B53E0`. | One concrete rotation-handler family covers signed-byte packed samples plus a playback-style sampler slot. | CONFIRMED | Determine whether any ordinary gorilla rotation descriptor selects this family. |
| handler base `0x7FF722D336D8` | Slots are `+0x168 -> 0x7FF720958590 -> 0x7FF72095CA20`, `+0x170 -> 0x7FF72094CB40 -> 0x7FF72095D0D0 -> sink`, `+0x178 -> 0x7FF72094CAC0 -> 0x7FF72095CA20 -> sink`, `+0x180 -> 0x7FF7209B53E0`. | A second rotation-handler family covers signed-16-bit packed samples plus the same playback-style sampler slot. | CONFIRMED | Determine where the descriptor builder chooses this family instead of the signed-byte family. |
| handler base `0x7FF722D334C8` | Slots are `+0x168 -> 0x7FF720958600 -> 0x7FF72095D2B0`, `+0x170 -> 0x7FF72094CDE0 -> 0x7FF72095D390 -> sink`, `+0x178 -> 0x7FF72094CD60 -> 0x7FF72095D2B0 -> sink`, `+0x180 -> 0x7FF7209B53E0`. | A third family covers the byte-packed `xyz + sign/control` variant. | CONFIRMED | Tie a named shared-body track to this family if its descriptor bytes point away from the raw-float family. |
| handler base `0x7FF722D33418` | Slots are `+0x168 -> 0x7FF720958640 -> 0x7FF72095D530`, `+0x170 -> 0x7FF72094CEC0 -> 0x7FF72095D610 -> sink`, `+0x178 -> 0x7FF72094CE40 -> 0x7FF72095D530 -> sink`, `+0x180 -> 0x7FF7209B53E0`. | A fourth family covers the signed-16-bit `xyz + sign/control` variant. | CONFIRMED | Compare its descriptor choice against the signed-byte `xyz + sign/control` family. |
| handler base `0x7FF722D332B8` | Slots are `+0x168 -> 0x7FF720958680 -> 0x7FF72095D7B0`, `+0x170 -> 0x7FF72094CFA0 -> 0x7FF72095D940 -> sink`, `+0x178 -> 0x7FF72094CF20 -> 0x7FF72095D7B0 -> sink`, `+0x180 -> 0x7FF7209B53E0`. `0x7FF72095D940` reads one row/stride-indexed direct-float quaternion sample and reconstructs `w`; `0x7FF72095D7B0` uses the same qword split but reads two consecutive `16`-byte samples and blends them through `0x7FF720955D60`. | This is now the strongest executable-side match for the ordinary gorilla rotation descriptor family advertising `stride = 16`. The exact qword math used by the code (`low32=row`, `bits32..47=baseOffset`, `bits48..63=stride`) structurally matches the on-disk `head_ctrl-node-rotation` descriptor `0x0010000000000041`. | STRONGLY SUPPORTED | Prove that `head_ctrl-node-rotation` or another ordinary rotation track selects this family at runtime. |
| handler base `0x7FF722D33360` | Slots are `+0x168 -> 0x7FF7209586F0 -> 0x7FF72095CC30`, `+0x170 -> 0x7FF7209586C0 -> 0x7FF72095DA10`, `+0x178 -> 0x7FF72094D110 -> 0x7FF72095CC30 -> sink`, `+0x180 -> 0x7FF72094D090 -> 0x7FF72095DA10 -> sink`. | This is the already-known family containing the `EDCC30` / `EDDA10` decode path and its immediate rotation-consumer wrappers. | CONFIRMED | Continue using this family as the anchor when checking the special tail/packed variants. |
| adjacent rotation helpers `0x7FF72095CC30`, `0x7FF72095D610`, `0x7FF72095C650`, `0x7FF72095E160`, `0x7FF72095E300` | `0x95CC30` decodes a compact quaternion from packed unsigned `24-bit`-style component fields plus an explicit sign bit for `w`; `0x95D610` does the same broad job from packed signed-16-bit fields. `0x95C650` reconstructs an axis-angle style record, and `0x95E160` / `0x95E300` convert single-sample and scaled/packed axis-angle values into quaternions using `sinf/cosf`. | The runtime rotation layer is now clearly format-polymorphic: direct-float quaternions, compact quantized quaternions, and axis-angle families all sit beside each other behind the same sink interface. This helps explain why the cooked selector builder remains the decisive missing bridge. | CONFIRMED | Keep separating the ordinary `stride = 16` shared-body family from these compact/axis-angle alternatives while searching for the cooked selector byte assignment. |

## `extraRel` Refinement Across Both Runtime Samples

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| Metal non-zero `extraRel` subset | The current Metal subset is `speed_node-node-translation`, `Lleg_01-node-rotation`, `Lleg_03-node-rotation`, `LLwing_bone01-node-rotation`, `Lwing_bone01-node-rotation`, `RLwing_bone01-node-rotation`, `Rwing_bone01-node-rotation`. | `extraRel != 0` is not rotation-only, because at least one translation track participates. | CONFIRMED | Compare the cooked selector for `speed_node-node-translation` if the builder is recovered. |
| Crystal non-zero `extraRel` subset | The current Crystal subset is `Lleg_01-node-rotation`, `Lleg_03-node-rotation`, `LLwing_bone01-node-rotation`, `Lwing_bone01-node-rotation`, `Lwing_bone04-node-rotation`, `Rleg_01-node-rotation`, `RLwing_bone01-node-rotation`, `Rwing_bone01-node-rotation`. | The subset is selective and stable-looking, but not identical between dragons. | CONFIRMED | Use a third runtime dragon to test whether the subset follows rig structure or authored animation content. |
| both runtime samples, `Lwing_bone01-node-rotation` | The target track keeps the same non-zero `extraRel` pattern in both samples: `outputRel - inputRel = 24`, `extraRel - outputRel = 12`. | `Lwing_bone01-node-rotation` remains one of the strongest bridge candidates because the extra payload slice is stable across dragons. | CONFIRMED | Use this track first if a live descriptor-table read path appears. |
| non-zero `extraRel` versus runtime selector | The executable-side runtime selector still dispatches on cooked-descriptor byte `+0x10` values `0..3`, but no recovered code path yet proves how those values derive from `extraRel`, from interpolation style, or from track class. | `extraRel != 0` marks a real optional third payload slice, but not yet a proven one-to-one selector family. | STRONGLY SUPPORTED | Recover the cooked-descriptor builder or a live populated table read. |

## Current IDB Cooked Descriptor Consumption Update - 2026-06-13

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF72094FDAE-0x7FF72094FE7F` | The matched `0x18` descriptor pointer is held in `r9`; selector byte `descriptor+0x10` chooses helper slots `+0x168/+0x170/+0x178/+0x180`, and `r9` is still the fourth argument passed into the chosen helper call. | The cooked descriptor that wins the name lookup is directly passed into the selector-specific object builder. | CONFIRMED | Find the table population stage or dump a populated table to identify the descriptor for one named track. |
| helper singleton `0x7FF722D333A0` / vtable `off_7FF722D33068` | The same helper object provides node creation at slot `+0x130` and selector builders at `+0x168/+0x170/+0x178/+0x180`. | The descriptor bridge is embedded in the same loaded-node construction system, not a detached animation-only cache. | CONFIRMED | Resolve the created node and downstream receiver class. |
| common selector-object constructor `0x7FF720A368D0` | Stores descriptor pointer at object `+424`; reads descriptor `+0x00`, `+0x08`, and `+0x11`; later selector constructors read a relative parameter payload through `descriptor+0x14`. | Runtime descriptor layout is now partially proven beyond the selector byte. | CONFIRMED | Map descriptor `+0x14` payload fields against the file-side row/stride/base descriptors. |
| `0x7FF72092E9E0` called from common constructor | Descriptor `+0x08` is passed as `char *`; the callee calls `strlen` and copies the text into selector object storage at `+56`. | Cooked runtime descriptor `+0x08` is a real string pointer, likely the per-track/per-binding name attached to the built runtime object. | CONFIRMED | Compare this string against `Lwing_bone01-node-rotation`, `head_ctrl-node-rotation`, or another named descriptor in a live/dumped table. |
| selector primary vtable `+0x210` -> `0x7FF720A00360` | The post-build method refreshes object `+440`, choosing between internal blocks `object+88` and `object+152` based on object `+432`, which came from descriptor `+0x11`; an external object at `+280` can override this path. | Descriptor `+0x11` influences the selector object's active target/source block after construction. | CONFIRMED as control flow, NOT YET KNOWN semantically | Identify what `+88/+152/+280/+440` represent in evaluator output. |
| selector builders `0x7FF7209B2540`, `0x7FF7209B2660`, `0x7FF7209B24B0`, `0x7FF7209B25D0` | Selectors `0..3` allocate `0x200`, `0x208`, `0x210`, and `0x228` objects, then call constructors `0xA00F40`, `0xA016A0`, `0xA00740`, and `0x9FFCF0`. | Selector values represent distinct cooked runtime object families with different parameter counts. | CONFIRMED | Determine which family ordinary shared `stride=16` rotation rows select. |
| selector-specific constructors | Selector `0` copies three dwords from descriptor-relative payload; selector `1` copies six; selector `2` copies seven; selector `3` copies twelve plus flags. | The runtime builder is not just choosing a hardcoded decoder; it materializes parameterized evaluator objects from compact payload records. | CONFIRMED | Compare copied payload dwords to `head_ctrl-node-rotation` row `0x41` and `body_root-node-translation` row `0x0D` descriptors. |
| `Lwing_bone01-node-rotation` bridge status | File-side `0x28` record and optional payload slices are known, and executable-side cooked descriptor consumption is now known, but the table writer assigning its cooked `+0x10/+0x14` fields is still not isolated. | The bridge is now complete from cooked runtime descriptor to evaluator-object construction, but not yet complete from this named on-disk track to its exact cooked descriptor. | STRONGLY SUPPORTED | Prioritize stores/population of owner `+0xBC/+0xC0` or a safe live table dump. |

## Follow-Up: Broad Cooker Versus Exact Track Descriptor Bridge - 2026-06-13

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF720A110A0` | The global `qword_7FF722E9DE20` is built as a 119-entry table of runtime field offsets by querying a freshly allocated `0x528` object. | Several suspicious `+0xBC/+0xC0` references in object-cooker code are indexes into a dynamic field-offset table, not necessarily the case-12 descriptor owner fields. | CONFIRMED | Keep case-12 owner `+0xBC/+0xC0` distinct from `qword_7FF722E9DE20[0xBC/4]` and `[0xC0/4]`. |
| `0x7FF7209B7920` | Creates a large runtime object from a source object at construction owner `+0x1B0`, copies many source fields and strings into dynamic runtime fields, and contains a 7-case source-value switch. | This is the best current upstream BRES/object-cooking lead, but it is broader than the track/evaluator bridge. | STRONGLY SUPPORTED | Identify whether the source object for one known animation/transform record flows through this function or through a sibling cooker. |
| `0x7FF7209B7CE0-0x7FF7209B7EFF` | Source field `+0x40` chooses among value-copy cases using relative payload at source `+0x44`; the copied values go into runtime float fields selected by dynamic offsets `+0xAC/+0xB0/+0xB4`. | This switch is a source-record value-format switch, not the cooked descriptor byte selector for `Lwing_bone01-node-rotation`. | CONFIRMED for non-equivalence | Search file-side records for this source `+0x40/+0x44` shape to classify the cooked object family. |
| `0x7FF72094FCDF-0x7FF72094FDC4` | The bridge target table is still reached via `r13 + s32[r13+0xC0] + 0xC0 + index*0x18` and searched by string. | The case-12 descriptor table has BRES-style relative addressing. It may be present as relocated file data rather than built by explicit per-field stores. | STRONGLY SUPPORTED | Search runtime BDAE/BRES object records for a `count + relative-table + 0x18 entries` pattern that contains known track/binding names. |
| `Lwing_bone01-node-rotation` | No current executable evidence assigns this named track to selector `0`, `1`, `2`, or `3`. | The exact named-track bridge remains incomplete. | NOT YET KNOWN | Use a live descriptor dump or file-side `0x18` table discovery to read the descriptor fields for this name. |

## Consumer-Object Refinement

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7ECE940` | This function creates a node-like object through a virtual method at `+0x130`, then calls `sub_7FF7A7ECEB20(..., &node_ptr)` and later finalizes the created node with `+0xC8` and `Scene_FinalizeLoadedNode`. | The bridge endpoint is tied to loaded-node construction and finalization. | STRONGLY SUPPORTED | Identify the concrete node class and its `+0x158` slot. |
| `0x7FF7A7ECD090` / `0x7FF7A7ECD110` / `0x7FF7A7ECCF20` | Each wrapper decodes into a temporary quaternion buffer and forwards that buffer to a receiver object's `vtable + 0x158`. | The bridge currently reaches a load-time runtime transform consumer. | CONFIRMED | Resolve the receiver-class implementation of `+0x158`. |
| `0x7FF7A7ED005B-0x7FF7A7ED00AF` inside `sub_7FF7A7ECEB20` | The same object family in `rdi` receives translation-like data through `+0x168`, quaternion data through `+0x158`, and scale-like data through `+0x148` during node construction. | This makes the bridge endpoint much more likely to be a concrete node/local-transform sink than a generic animation-cache object. | STRONGLY SUPPORTED | Prove that the packed path and the inline path share the same concrete receiver class. |

## Current Bridge Status

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| overall | Proven chain now: `named on-disk runtime track record -> compact payload offsets -> file-derived name used in executable lookup -> matched 0x18 runtime descriptor -> runtime descriptor byte +0x10 -> cooked decoder-side record form -> quaternion decode-handler family -> caller-supplied load-time transform consumer`. | This is materially stronger than the earlier bridge, but it is still not a complete one-track disk-to-final-transform proof. | CONFIRMED | The next required step is still isolating runtime descriptor table construction or the exact receiver `+0x158` implementation. |
| higher-level streamed runtime object chain | A separate executable-side construction path now exists above the sampler helpers: `sub_7FF7209B0A90` allocates a `0x238` object and calls `sub_7FF7209B5B50`, then `sub_7FF7209B3580`, which in turn calls `sub_7FF7209B7920`. In parallel, `sub_7FF7209B0950` allocates a `0x98` object and builds it through `sub_7FF7209FCE50`, while `sub_7FF7209F2410` registers that object in a global sorted cache and `sub_7FF7209F29C0` maintains a `0x18`-stride side table. | The animation system now has a proven higher-level runtime object construction layer above the raw quaternion decoders and time samplers. This is strong evidence that the project is near generalized debug playback, even though the exact cooked descriptor-table writer is still not isolated. | STRONGLY SUPPORTED | Determine whether the `0x18`-stride side table maintained by `0x7FF7209F29C0 / 0x7FF7209F21F0` is the same family as the case-12 descriptor table or a related streaming/cache structure. |
| unresolved point 1 | Targeted xref, wrapper, and field-offset searches still have not isolated the constructor or writer for the runtime descriptor table at `owner+0xBC/0xC0` or its byte selector at descriptor `+0x10`. | The decisive cooked-table builder remains the central missing bridge stage. | NOT YET KNOWN | Trace writes into the descriptor table or find a safe way to inspect a live populated table. |
| unresolved point 2 | The exact selector value for `Lwing_bone01-node-rotation` has not been recovered from a proven table-population path. | I still cannot say whether this specific track uses selector `0`, `1`, `2`, or `3`. | NOT YET KNOWN | Recover the descriptor-table population routine or inspect the live loaded table if a safe read path appears. |
| unresolved point 3 | The packed-path receiver object's concrete class name is still not resolved, and the exact setter function behind `+0x158` is not yet isolated. | It is still too early to upgrade "node/local rotation sink" to a formally named confirmed function. | NOT YET KNOWN | Follow the receiver class upward from `sub_7FF7A7ECE940` and downward from the called `+0x158` slot. |

## 2026-06-19 Correction: Load-Time Descriptor Bridge Is Not The Whole Playback Bridge

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML `0x7FF72094FCDF..0x7FF72094FE85` | Reconfirmed in the active IDB: case-12 searches a `0x18` string table at `owner + s32[owner+0xC0] + 0xC0`; on match, `descriptor+0x10` dispatches to helper slots `+0x168/+0x170/+0x178/+0x180`. | This remains a real cooked descriptor bridge, but it is best classified as load-time/string-binding object construction until proven otherwise. | `CONFIRMED` | Find a serialized runtime-BDAE owner with `+0xBC/+0xC0` to bridge a bind-pose/node descriptor. |
| common constructor `0x7FF720A368D0` | Stores the descriptor pointer at object `+424`, copies `descriptor+0x11` to object `+432`, copies `qword[descriptor+0]` into object state, and copies string pointer `qword[descriptor+8]` through `0x7FF72092E9E0`. | The `0x18` descriptor entry layout is now partially known beyond the selector byte. | `CONFIRMED` | Scan BDAEs for entries matching `{qword id/source, qword string, byte selector, byte flag, rel payload}`. |
| selector constructors | Selector 0/1/2/3 allocate `0x200/0x208/0x210/0x228` byte objects and copy 3/6/7/12 dwords plus flags from `descriptor+0x14+s32[descriptor+0x14]`. | Selector values choose different parameterized object layouts; they are not direct copies of raw track `extraRel` or output count. | `CONFIRMED` | Compare payload lengths against any discovered serialized descriptor entries. |
| current DML `0x7FF7209F9CF0` | Per-frame animation playback walks 16-bit target indices, looks up evaluator objects, and calls their `+0x60/+0x68/+0x88` methods after `0x9B51D0` produces key index/fraction. | The remaining named-track playback bridge is now: `root+0x40 target entry -> target index list -> evaluator object -> direct/blended method`, not merely the case-12 load-time selector. | `CONFIRMED` | Decode the target-index list owner and prove the evaluator object used for `head_ctrl-node-rotation`. |
| `Lwing_bone01-node-rotation` status | The file-side runtime BDAE load-time record remains useful for bind-pose research, while shared-body animation playback should use Gorilla's target table and evaluator-object list. | Do not use the load-time `+0x10` selector as the final answer for shared-body animation playback until the object identity is proven. | `CONFIRMED` as a correction | Retarget the next bridge attempt to `head_ctrl-node-rotation` in `dragon_gorillabody_anim.bdae`, because its `stride=16,row=65` descriptor matches the strongest ordinary rotation evaluator family. |

## 2026-06-19 Head-Control Playback Bridge Narrowing

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_gorillabody_anim.bdae`, root `+0x40` table entry `32` | Generated engine-table JSON maps index `32` to `head_ctrl-node-rotation`, entry offset `0x4DC0`, primary subdescriptor `0x5AEC`, time row `64`, value kind `4`, value row `65`, stride `16`, key count `6`. | `head_ctrl-node-rotation` has a concrete target-table index and a concrete ordinary rotation row descriptor. | `CONFIRMED` | Use this as the first named target for evaluator-object proof. |
| current DML `0x7FF7209FC0C0` | Playback helper selects one target-index list slot from object `+0x30/+0x38/+0x40` according to mode at object `+0x58`. | Playback does not simply walk all named target entries; it walks selected `u16` target lists. | `CONFIRMED` | Locate the constructor/populator for the list slots. |
| current DML `0x7FF7209F9CF0` | Each `u16` target-list value is used directly as an index into evaluator/receiver/target arrays before calling evaluator slots `+0x60/+0x68/+0x88`. | If the selected list contains `32`, that loop iteration directly targets `head_ctrl-node-rotation`. | `CONFIRMED` for direct-index semantics, `NOT YET KNOWN` for membership | Recover selected-list contents. |
| current DML `0x7FF7209F90F0` | Independent helper repeats the same direct-index usage into arrays at `(*a3)[14]`, `(*a3)[15]`, and receiver lookup state. | The `u16` list is not an unrelated row list; it is a playback target-index list. | `CONFIRMED` | Map the arrays back to the exported root target table. |
| local `dragon_gorillabody_anim.bdae` static scan | Multiple small-integer runs contain `32`, but no run has yet been tied to the selected list object fields at `+0x30/+0x38/+0x40`. | Static scans are candidate hints only. | `HYPOTHESIS` | Do not patch viewer playback from these runs until ownership is proven. |

Current one-track status:

```text
head_ctrl-node-rotation
  -> file/root target index 32                 CONFIRMED
  -> target-list values are direct indices     CONFIRMED
  -> selected list includes index 32           NOT YET KNOWN
  -> evaluator vptr for index 32               NOT YET KNOWN
  -> final local rotation sink for this target NOT YET KNOWN
```

## 2026-06-19 Materialized Target/Evaluator Record Bridge

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML `0x7FF7209FCE50` | During construction, the engine reads `targetCount = dword[payload+0x58]` and `targetRecordRel = s32[payload+0x5C]`, then iterates `targetIndex` with record stride `0x58`: `record = payload + 0x58 + targetRecordRel + 0x58*targetIndex`. | There is now a proven cooked/materialized target-record table between the raw root target table and the runtime evaluator objects. | `CONFIRMED` | Locate the exact materialized payload window for Gorilla. |
| current DML `0x7FF7209FCE50 -> 0x7FF7209D7600` | For every `targetIndex`, the engine allocates `0x48` bytes, calls `9D7600(newEvaluator, payload, targetIndex, flags)`, and appends the result to the container vector. | Each target index owns one constructed evaluator/descriptor object. | `CONFIRMED` | Determine the vptr/family for evaluator object at index `32`. |
| current DML `0x7FF7209D7600` | The per-target constructor recomputes the same 88-byte record, reads kind/range/reference fields, and builds auxiliary descriptor state via `9D7F50`. | `9D7600` is the next best executable-side target for classifying how `value kind 4`, row `65`, stride `16` becomes a concrete quaternion evaluator family. | `CONFIRMED` | Classify `9D7F50` and the lookup table `dword_7FF7228019F8`. |
| `dragon_gorillabody_anim.bdae`, `head_ctrl-node-rotation` | File/root target index `32` is known and has ordinary rotation descriptor fields: time row `64`, value kind `4`, value row `65`, stride `16`, key count `6`. | If materialized target record index `32` corresponds one-to-one with the root table index, then this is the exact evaluator record to inspect. | `STRONGLY SUPPORTED` | Prove that materialized target record order preserves root `+0x40` order, or find the remap if it does not. |
| `dragon_gorillabody_anim.bdae`, direct static scan | The previous candidate at `0x6250` does not expose the expected table shape: `count@+0x58 = 1`, `rel@+0x5C = 3`. Broad scans produce many false positives from normal BRES tables. | Raw file scanning alone has not yet found the materialized target/evaluator table. | `CONFIRMED` for failed current candidate, `NOT YET KNOWN` for exact offset | Follow the source/window materialization path from `9B0950/9FCE50` instead of guessing from all count/relative tables. |

Updated bridge target:

```text
head_ctrl-node-rotation
  -> root target index 32                      CONFIRMED
  -> materialized target record stride 0x58    CONFIRMED
  -> materialized record index 32              STRONGLY SUPPORTED
  -> 0x48 evaluator object for index 32        CONFIRMED as construction pattern, NOT YET LOCATED
  -> evaluator vtable/family for index 32      NOT YET KNOWN
  -> local rotation sink during playback       STRONGLY SUPPORTED, not one-track proven
```

## 2026-06-19 Source-Cooker Bridge Update

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209B0A90` | Allocates a `0x238` source/runtime object, initializes it through `0x7FF7209B5B50`, then calls `0x7FF7209B3580`. | One higher-level animation/source object is constructed before playback evaluator containers. | `CONFIRMED` | Locate the raw BDAE record passed as the source pointer. |
| `0x7FF7209B5B50` | Stores the source pointer at object `+0x1B0`, stores helper/context pointers at `+0x1C8/+0x1E8`, and copies the source name/string. | This object can carry a raw/source record identity forward into the cooker. | `CONFIRMED` | Compare copied names against shared animation BDAE strings. |
| `0x7FF7209B3580` | Reads source byte `+0x68` and relative/reference field `+0x6C`; case `1` resolves a named referenced object, while cases `0/2` cook directly with modes `0x10003` or `0x18003`. | Track-to-runtime mapping has a serialized source-mode layer before target/evaluator construction. | `CONFIRMED` | Find which source-mode path is used by the Gorilla shared body animation. |
| `0x7FF720956C10` | Resolves strings through a 24-byte name table under count `+0xA4` and relative table `+0xA8`. | Named references in animation/source records can be chased statically if the owner table is found. | `CONFIRMED` | Add viewer diagnostics for this table family. |
| `0x7FF7209B7920` | Cooks source records into a `0x528` runtime object and copies source fields through dynamic offsets. It has a source-value switch on `source+0x40` and relative payload at `source+0x44`. | The raw target row descriptor for `head_ctrl-node-rotation` is not enough by itself; the engine first cooks source records into another runtime layout. | `CONFIRMED` | Bridge raw target index `32` through the cooked object/materialized payload. |
| negative vtable check | Reading `off_7FF722D3C820 + 0xF8` gives `0x7FF7209B4E80`; this function is an evaluator apply wrapper using `9B51D0` and virtual slots `+0x60/+0x68`, not a proven named-resource builder. | The concrete virtual builder called by `94E1F0` remains unresolved. | `CONFIRMED` for negative result | Do not use `9B0950` or `9B4E80` as the builder until the actual receiver vtable is proven. |

Updated one-track status:

```text
head_ctrl-node-rotation
  -> raw/root target index 32                 CONFIRMED
  -> source-object cooker layer exists        CONFIRMED
  -> source mode/reference fields known       CONFIRMED
  -> cooked target/evaluator materialization  CONFIRMED
  -> exact source record for target 32        NOT YET KNOWN
  -> selected playback list contains 32       NOT YET KNOWN
  -> evaluator family for target 32           NOT YET KNOWN
```

## 2026-06-19 Playback Factory And State-Object Correction

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| current DML `.data` `off_7FF722D3E298` | `0x7FF7209F87F0` installs `off_7FF722D3E298` into the constructed `0x98` playback object. From that actual base, `0x7FF7209F9450` is slot `+0xC0` and `0x7FF7209FC630` is slot `+0x128`. Earlier slot numbering from the nearby `0x7FF722D3E2D8` qword region was base-shifted. | The per-frame path is a virtual playback-object interface; false metadata xrefs and shifted table bases should be ignored. | `CONFIRMED` | Continue using the constructor-installed vtable base, not generic xref noise. |
| current DML `0x7FF7209B01F0` | Factory reads `dword[a5+0x08]` and selects playback subclass: case `0 -> 0x98 object via 9F87F0`, case `1 -> 0xB8`, case `2 -> 0xB0`, cases `3/5/6 -> 0xC8`, case `4 -> 0xD0`. | Shared animation playback has a serialized kind/type before runtime object construction. | `CONFIRMED` | Locate the exact shared-animation file/source record supplying this kind for Gorilla. |
| current DML `0x7FF7209F87F0` | Base constructor installs playback vtables, stores animation resource at object `+0x50`, initializes state fields, and calls `0x7FF7209FC110`. | The base `0x98` object is the concrete state owner for the traced `9F9450` apply family. | `CONFIRMED` | Track object identity carefully when comparing to the `*a3` state used inside apply loops. |
| current DML `0x7FF7209FC110` | Reads resource `+0x48` as target count and resizes playback object's `u32` state/cache vector at `+0x58/+0x60/+0x68`. | This `+0x58` field family is not the same as the selected-list mode field read by `9FC0C0`; the decompiler uses similar offsets on different objects. | `CONFIRMED` | Avoid patching viewer code from offset names alone; always include owning object. |
| current DML `0x7FF7209FC630` | Selects clip/segment index and writes `playback+0x70 = targetCount * index`, `playback+0x74 = index`, then refreshes range metadata and installs a `0x30` helper through the sink/control object's virtual `+0xB0`. The helper methods include `strcmp`-based event-name lookup and byte/u16/int event-time decoding. | `9FC630` is clip/range/event selection, not the transform target-index list walked by `9F9450/9F9CF0`. | `CONFIRMED` | Trace the apply-state object passed into `9F9CF0`, not the `9FC630` event helper, to find a selected list containing target index `32`. |
| current DML `0x7FF721553B10` | Wrapper around `9F90A0` manages transition countdown/duration and two blend weights at `+0x50`. | The current visual “moves then tweaks/holds” symptom is likely caused by incomplete transition/crossfade handling plus incomplete hierarchy/skinning, not by a wrong mesh. | `STRONGLY SUPPORTED` | The viewer should add a diagnostic mode that can disable transition logic and show raw pose evaluation first. |

Updated bridge target:

```text
head_ctrl-node-rotation
  -> root target index 32                       CONFIRMED
  -> playback factory and base object known     CONFIRMED
  -> resource target-count state known          CONFIRMED
  -> clip/segment selector found                CONFIRMED
  -> event helper separated from target lists   CONFIRMED
  -> selected apply-state u16 list contains 32  NOT YET KNOWN
  -> evaluator family for target 32             NOT YET KNOWN
  -> final skinned pose equivalent              NOT YET KNOWN
```

## Apply-State Versus Event-State Correction - 2026-06-20

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| sink/control vtable `off_7FF722D3E410` | `9FC630` calls sink slots `+0xA8/+0xB0/+0xC0`, which resolve to `0x7FF720A34620`, `0x7FF720A345C0`, and `0x7FF720A344E0`. `+0xB0` stores the `0x30` helper at sink `+0x50`. | This receiver manages range/event helper state. | `CONFIRMED` | Keep this layer separate from transform application in viewer code. |
| `0x30` helper object | Its selected pointer at `+0x28` is consumed by `0x7FF720A33CF0`, which switches on event-list type, compares names with `strcmp`, and decodes event times. | This is not the bone/node target-index list for playback transforms. | `CONFIRMED` | Use it later for animation events only. |
| `0x7FF7209F9CF0` | The transform apply loop selects list objects from the `a3` apply-state object using mode `+0x58`, then walks `u16` values from selected-list `+0x10..+0x18`. | The real bridge for `head_ctrl-node-rotation` now goes through the apply-state constructor/populator. | `CONFIRMED` | Locate writes to apply-state `+0x30/+0x38/+0x40/+0x58` and verify membership of target `32`. |

## Apply-State Target-Mask Builder - 2026-06-20

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209F90A0` | Immediately before tail-dispatching to the playback-object virtual apply slot `+0xC0`, it calls `0x7FF720A14A80(*a3)`. | Target-list refresh happens in the per-frame apply path, not merely during resource construction. | `CONFIRMED` | Treat this as the viewer's runtime-shaped pre-apply mask refresh stage. |
| `0x7FF720A14A80` | If dirty byte `state+0x28` is set, it rebuilds list objects at `state+0x30`, `state+0x38`, and `state+0x40`, using primary source `state+0x18` and optional secondary/blend source `state+0x20`, then clears the dirty byte. | This is the missing target-index-list populator for the `9F9CF0/9F90F0` apply loops. | `CONFIRMED` | Recover which source object/bitset corresponds to the selected Gorilla clip and transition state. |
| `0x7FF720A14DB0` | Clears the destination list by resetting end to begin, loops `targetIndex = 0..targetCount-1`, tests a bit in the provided bitset, and appends every set bit as a `uint16`. | Selected lists contain direct playback target indices derived from bitsets. | `CONFIRMED` | Prove whether bit `32` is set in the active mask for `head_ctrl-node-rotation`. |
| `0x7FF720A362C0` | Fills a bitset with all valid target bits, then masks off unused bits in the final dword. | This is the "all active targets" initializer. | `CONFIRMED` | Use it to model fallback/no-primary-source behavior offline. |
| `0x7FF720A363A0` / `0x7FF720A367E0` | Copy bitset words from a source bitset into the temporary mask. | These helpers move primary or secondary target masks into the working mask. | `CONFIRMED` | Identify the file/runtime owner of each source bitset. |
| `0x7FF720A36400` | ANDs the temporary bitset with another source bitset. | The engine explicitly intersects active target sets, likely for clip/crossfade overlap. | `CONFIRMED` | Validate the overlap list `state+0x38` against crossfade behavior. |
| `0x7FF720A36600` | Inverts all valid bits in the temporary bitset. | The engine can form a complement/non-overlap target set. | `CONFIRMED` | Validate the non-overlap list `state+0x40` against transition behavior. |
| `0x7FF720A14A80`, primary-source branch | When `state+0x18` exists, list `+0x30` is built from the primary mask; if `state+0x20` also exists, list `+0x38` is built from `primary AND secondaryMask`, then list `+0x40` is built from `primary AND NOT secondaryMask`. | The three lists are primary, overlap, and primary-only/non-overlap categories. | `STRONGLY SUPPORTED` | Confirm with a live/debug dump or static reconstruction of the source masks. |
| `0x7FF720A14A80`, no-primary branch | Without `state+0x18`, it starts from the all-valid-targets mask; if a secondary source exists, list `+0x38` becomes the secondary subset and list `+0x40` becomes `NOT secondary`. | This is a fallback/full-target mode used when no primary mask object is installed. | `STRONGLY SUPPORTED` | Determine when this branch occurs in normal dragon animation playback. |
| `0x7FF7209F8A00` | Saves old apply-state mode `state+0x58`, temporarily writes mode `1`, creates an all-valid target mask, copies the mask from `state+0x20 + 0x98`, optionally intersects with the existing primary mask at `state+0x18`, checks for empty mask through `0x7FF720A36780`, and if non-empty installs the new mask at `state+0x18` and marks dirty byte `state+0x28 = 1`. | This function propagates/refreshes the primary apply mask that later becomes selected target lists. | `CONFIRMED` | Determine what runtime object sits at `state+0x20` during Gorilla playback and whether its `+0x98` mask includes target index `32`. |
| `0x7FF720A36780` | Scans all target-bitset dwords and returns true only when no word contains a set bit. | Empty masks are rejected instead of being installed as the primary apply mask. | `CONFIRMED` | Use the same empty-mask rule in diagnostics. |
| `0x7FF7209FC8E0` | Replaces apply-state pointer at `state+0x18`, bumps references, and sets dirty byte `state+0x28 = 1` when the pointer changes. | Changing the primary mask object forces `A14A80` to rebuild the u16 target lists before the next apply. | `CONFIRMED` | Track callers that install a mask affecting `head_ctrl-node-rotation`. |

Updated bridge target:

```text
head_ctrl-node-rotation
  -> root target index 32                       CONFIRMED
  -> per-frame apply-state refresh found        CONFIRMED
  -> primary target mask propagation found       CONFIRMED
  -> selected lists are bitset-derived u16s     CONFIRMED
  -> u16 values are direct target indices       CONFIRMED
  -> active bitset contains index 32            NOT YET KNOWN
  -> evaluator family for target 32             NOT YET KNOWN
  -> final skinned pose equivalent              NOT YET KNOWN
```

## Per-Target Component Descriptor Builder - 2026-06-20

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7209D7600` | For each materialized 88-byte target record, the constructor searches a component list shaped as `(componentId, byteIndex)` entries. It probes component IDs including `0`, `1`, `2..3`, `4..16`, `18..21`, `22..25`, `26`, and `27`; each present component calls `0x7FF7209D7F50`. | Target records can own multiple component descriptors; value kind `4` fits the first entry in the `4..16` component-ID family rather than being a global playback selector. | `CONFIRMED` for the ID search/calls, `STRONGLY SUPPORTED` for value-kind interpretation | Inspect materialized target record index `32` to prove which component IDs are present for `head_ctrl-node-rotation`. |
| `0x7FF7209D7F50` | Emits one `24`-byte descriptor at `descriptorBase + 24*componentSlot`. It writes `+0` resource pointer from materialized payload `+0x50`, `+8` computed dword, `+0x0C` dword, `+0x10` byte, `+0x11 = 0`, and `+0x12` word. | The per-target evaluator does not consume raw BDAE row fields directly; it consumes cooked 24-byte component descriptors. | `CONFIRMED` | Add a viewer diagnostic schema for this descriptor, but keep it marked cooked/runtime-shaped until materialized payload location is solved. |
| `dragon_gorillabody_anim.bdae`, `head_ctrl-node-rotation` | Raw target entry has `value kind = 4`, value row `65`, stride `16`, key count `6`. | This aligns with the `9D7600` component-ID `4` family and the previously identified ordinary compact-quaternion evaluator lane. | `STRONGLY SUPPORTED` | Prove the live materialized record for target index `32` preserves this component ID and descriptor. |
