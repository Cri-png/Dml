# IDA Quaternion Consumer

## Core Decode/Consume Wrappers

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7ECD090` | Decompile and disassembly show: initialize a 16-byte temp quaternion buffer, call `sub_7FF7A7EDDA10(...)`, then call `qword ptr [receiver_vtable + 0x158]` with the receiver object and `&tmp`. | This is a table-dispatched packed-quaternion decode wrapper that immediately forwards the decoded quaternion to a runtime consumer object. | CONFIRMED | Keep identifying the concrete receiver class. |
| `0x7FF7A7ECD110` | Same forwarding pattern, but calls `sub_7FF7A7EDCC30(...)` before the same `+0x158` consumer call. | Companion consume-wrapper for a second packed-quaternion decode family. | CONFIRMED | Compare selector routing to determine when each family is chosen. |
| `0x7FF7A7ECCF20` | Same forwarding pattern again: temp buffer, `sub_7FF7A7EDD7B0(...)`, then the same `+0x158` consumer. | Third packed-rotation wrapper feeding the same quaternion sink. | CONFIRMED | Use it to characterize the full packed-rotation family. |
| `0x7FF7A7EC7E30` | Temp buffer, `sub_7FF7A7ED5D60(...)`, then the same `+0x158` consumer. | The same sink is reused even after a non-packed helper has already produced a quaternion. | CONFIRMED | Treat `+0x158` as the common quaternion sink for this interface family. |
| `0x7FF7A7ECCFA0` | Decompile reconstructs quaternion-like components directly from a descriptor pair, computes the fourth component, then calls `receiver->vtable[0x158/8](receiver, quat)`. | Simpler direct bridge from descriptor data to the same quaternion consumer slot. | CONFIRMED | Compare this descriptor type against the case-12 cooked runtime descriptor family. |
| `0x7FF7A7ED86C0` | Tail-jump wrapper into `sub_7FF7A7EDDA10`. | Non-consuming counterpart of the `EDDA10` family. | CONFIRMED | Compare against `ECD090` to isolate decode-only versus decode-and-forward behavior. |
| `0x7FF7A7ED86F0` | Tail-jump wrapper into `sub_7FF7A7EDCC30`. | Non-consuming counterpart of the `EDCC30` family. | CONFIRMED | Compare against `ECD110` for the same reason. |

## Adjacent Method-Table Evidence

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7AA2B34C8-0x7FF7AA2B34E0` | Raw qwords decode to adjacent method slots: `86F0`, `86C0`, `ECD110`, `ECD090`. | The four selector-dispatched handlers are contiguous entries in the same object interface. | CONFIRMED | Keep using these slots when mapping selector values. |
| `0x7FF7AA2B3360` | Slot arithmetic still aligns: `+0x168 -> 86F0`, `+0x170 -> 86C0`, `+0x178 -> ECD110`, `+0x180 -> ECD090`. | The selector block is a virtual-method dispatch on one handler object family. | CONFIRMED | Trace constructor/vtable ownership later if a class name becomes necessary. |

## What The Consumer Receives

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `ECD090` / `ECD110` / `ECCF20` | Each wrapper decodes into a local 16-byte stack buffer and passes `&tmp` to `receiver->vtable[0x158/8]`. | The consumer receives a quaternion-like 4-float payload by pointer. | CONFIRMED | Determine whether the receiver stores it, applies it, or forwards it again. |
| `EDCC30` | Decompile reconstructs four float components and writes them directly to the output buffer. | One packed path outputs a single quaternion. | CONFIRMED | Compare with paired/interpolated paths. |
| `EDDA10 -> ED17B0` | `EDDA10` prepares nested pointers and blend weights, `ED17B0` reconstructs two packed quaternion-like samples with square-root fourth components, then `ED5D60` blends them into the final output. | Second packed path decodes a two-sample quaternion form before forwarding the result. | CONFIRMED | Continue mapping which selector values reach this family. |
| `EDD7B0` | Existing earlier decompile showed another two-sample quaternion path ending in `ED5D60`. | A third packed family also converges on a blended quaternion result before hitting the sink. | STRONGLY SUPPORTED | Use it later if exact interpolation modes matter. |

## Direct Setter Evidence Inside The Loader

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7ED005B-0x7FF7A7ED00AF` inside `sub_7FF7A7ECEB20` | The current object in `rdi` is called directly with `+0x168` using three floats from `r15+18`, then with `+0x158` using a 16-byte quaternion from `r15+24`, then with `+0x148` using three floats from `r15+34`. | The same interface family uses `+0x168` / `+0x158` / `+0x148` as translation / rotation / scale-style setters during load-time node construction. | STRONGLY SUPPORTED | Resolve the concrete class of `rdi` if a final semantic name is required. |
| same direct call block | The direct `+0x158` call sits between neighboring transform-style calls and before a boolean-style `+0x98` call. | `+0x158` now looks much more like a local-rotation setter than a generic intermediate cache hook. | STRONGLY SUPPORTED | Prove that the packed path reaches the same concrete receiver class. |

## What The Receiver Object Appears To Be

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `ECD090` / `ECD110` / `ECCFA0` prototypes | The receiver is a normal runtime object with its own vtable, not raw file data. | The packed decode output is forwarded into a polymorphic runtime transform sink. | CONFIRMED | Identify the class family by tracing constructors or vtable ownership. |
| `0x7FF7A7ECE940` | This function creates a node-like object through a virtual method at `+0x130`, calls `sub_7FF7A7ECEB20(..., &node_ptr)`, then calls the created node's `+0xC8` method and `Scene_FinalizeLoadedNode`. | The packed decode path is reached during loaded-node construction/finalization. | CONFIRMED | Keep following the created node type. |
| `0x7FF7A7ED0BB0` | This caller walks child-like records in `96`-byte steps and recursively calls `sub_7FF7A7ECEB20(...)`. | The surrounding context is recursive hierarchy construction, not yet a proven per-frame animation update loop. | STRONGLY SUPPORTED | Find a true frame-advance caller before claiming playback-time evaluation. |

## Current Best-Supported Stage In The Pipeline

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `sub_7FF7A7ECEB20` packed paths | The packed decode wrappers are reached from a constructor/dispatch routine that iterates named descriptor tables, creates/refcounts objects, and finalizes loaded nodes. | Current evidence places the packed-quaternion path in load-time runtime-object construction. | CONFIRMED | Keep looking for a separate playback-time sampling path. |
| `vtable + 0x158` | The same slot is used both by packed decode wrappers and by a direct inline quaternion setter block inside `ECEB20`. | `+0x158` is now best modeled as a node/local-rotation sink inside the load-time transform interface, even though the exact class/type name is still unknown. | STRONGLY SUPPORTED | Resolve the concrete receiver class or vtable owner for final confirmation. |

## Deeper Forwarders And Narrow Caller Graph

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x7FF7A7EC7DC0` | Decompile shows: initialize an identity quaternion, call `sub_7FF7A7ED2090(a2, a3, a4, &tmp)`, then immediately forward `&tmp` to another receiver object's `vtable + 0x158`. The function currently has zero direct code xrefs and only data/vtable xrefs. | One apparent `+0x158` implementation is still an adapter layer rather than the final concrete storage sink. | CONFIRMED | Follow the second receiver object passed as `a5` to find the concrete final sink. |
| `0x7FF7A7ED2090` | Caller graph shows only one code caller: `sub_7FF7A7EC7DC0`. The decompile accumulates quaternion/axis-angle-like transforms over `a3` entries before writing a final quaternion to `a4`. | This is a specialized quaternion-composition helper, not a broad animation-system entrypoint. | CONFIRMED | Look for other composition helpers that feed the same second-layer sink. |
| `0x7FF7A7ECCBA0` | Decompile reconstructs two quaternion-like samples from a cooked descriptor pair, blends them through `sub_7FF7A7ED5D60`, then forwards the result to `a6->vtable[0x158/8]`. It has one visible code caller plus data/vtable xrefs. | Another narrow adapter path feeds the same rotation-oriented consumer slot. | CONFIRMED | Compare this descriptor family to the case-12 selector family once the builder is known. |
| `0x7FF7A7EDC810` and `0x7FF7A7EDCA20` | Both helpers read cooked descriptor-relative pointers at `+36/+44`, decode packed component pairs, blend them through `sub_7FF7A7ED5D60`, and each currently has only one code caller. | These are helper-family internals, not yet proven playback-loop functions. | CONFIRMED | Trace outward from their single visible callers to see whether they ever escape load-time setup. |
| `0x7FF7A7EDD2B0` and `0x7FF7A7EDDAF0` | Both build pointer tuples from cooked descriptor-relative data, call `sub_7FF7A7ED12D0` or `sub_7FF7A7ED1CA0`, then forward through `sub_7FF7A7ED5D60`. Each currently has one visible code caller. | More cooked-descriptor decode helpers converge on the same quaternion blending helper before any final consumer slot is reached. | CONFIRMED | Keep using this family to separate helper layers from the real playback sink. |
| `0x7FF7A7ED17B0`, `0x7FF7A7EDCC30`, `0x7FF7A7EDD7B0` xrefs | Code-xref queries show only `1`, `2`, and `2` direct code callers respectively. `ECD090` and `EC7DC0` currently show `0` direct code xrefs and only data/vtable xrefs. | The decode path still looks interface-driven and load-time oriented, with no recovered direct tick/update loop feeding it. | STRONGLY SUPPORTED | Search outward from animation/tick entrypoints rather than only inward from the decode helpers. |

## Remaining Gaps

| Address | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| packed-path receiver class | I still have not isolated the concrete class constructor or exact vtable owner used by the packed decode wrappers. | The receiver can be described functionally, but not yet by a reliable semantic class name. | NOT YET KNOWN | Trace the constructor or vtable assignment for the created node object. |
| final concrete sink | `EC7DC0` proves that at least one apparent `+0x158` implementation forwards to another `+0x158` after quaternion accumulation. | The transform interface is clearly rotation-oriented, but the concrete final storage/write function is still one layer deeper than the currently traced adapter. | NOT YET KNOWN | Follow the second-layer receiver passed to `EC7DC0` and sibling adapters. |
| packed path versus bone object | The direct evidence now supports a node/local-rotation sink, but not yet a specific bone-matrix field write. | It is still too early to claim a confirmed final bone write. | NOT YET KNOWN | Follow the concrete receiver implementation behind the deepest proven `+0x158` call. |
