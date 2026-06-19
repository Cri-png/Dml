# Dragon.dat Findings

## Summary

- `Dragon.dat` is **not** a `BRES`/`BDAE` container.
- Its first bytes are a valid uncompressed SWF-style header: `FWS`.
- The little-endian length field in the header matches the exact file size.
- The body contains XML/XMP metadata, ActionScript-style package/class strings, `.bdae` and `.tga` filenames, and `Dragon_fla` tail strings.
- Direct evidence currently supports `Dragon.dat` being a Flash/Scaleform-style application/resource blob rather than the dragon mesh/skin runtime container we are tracing in the BRES pipeline.

## File Identity

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `Dragon.dat` file metadata | Path: `C:\Program Files\WindowsApps\A278AB0D.DragonManiaLegends_9.2.15.0_x64__h6adky7gbf63m\Assets\GameData\Dragon.dat`; size `32,837,600` bytes (`0x01F50FE0`); SHA256 `260138f20c90f8c5aa2b2e124f66465f130c135f72925c36fda71f6fd19b0a75`. | Stable baseline identity for later comparisons. | CONFIRMED | Reuse this hash when correlating other local copies of `Dragon.dat`. |
| `0x00` | First 16 bytes: `46 57 53 1F E0 0F F5 01 80 00 02 58 00 00 01 90`. ASCII: `FWS........X....`. | `FWS` is the classic uncompressed SWF magic. Byte `0x1F` matches a version field. The 32-bit little-endian field at `0x04` is `0x01F50FE0`, exactly the full file size. | CONFIRMED | If needed, parse later SWF tag structure to identify the embedded resource types more formally. |
| `0x20` | Bytes begin `<?xml version="1.0"?>` and continue with RDF/XMP metadata. | Matches common SWF/Adobe metadata embedding rather than BRES relocation/string/record layout. | CONFIRMED | Not immediately needed unless provenance/version metadata becomes relevant. |
| `0x1F50FB0` near EOF | Tail contains `com.gameloft.dragon.items.UserAvatar`, `Dragon_fla`, `Main`, and UI/control-like names. | Strongly indicates a Flash/ActionScript artifact with embedded classes/symbols. | STRONGLY SUPPORTED | If useful later, extract symbol names or SWF tags to map which systems still use Flash-side dragon assets. |

## First 256 Bytes

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x00-0x0F` | `46 57 53 1F E0 0F F5 01 80 00 02 58 00 00 01 90` | `FWS` header plus full-file length `0x01F50FE0`. | CONFIRMED | None needed for file identification. |
| `0x20-0x7F` | `<?xml version="1.0"?>` followed by `<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">` | Embedded XMP/RDF metadata block. | CONFIRMED | None needed unless provenance metadata matters. |
| `0x80-0xFF` | XML continues with `dc:` and `asc:` namespace strings. | Adobe/authoring-tool metadata is present very early in the file. | STRONGLY SUPPORTED | Not needed for the BRES pipeline directly. |

## String and Signature Search

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| whole file | `BRES`: `0` hits. | No direct `BRES` container magic was found anywhere in `Dragon.dat`. | CONFIRMED | This sharply separates `Dragon.dat` from the BDAE/BRES containers. |
| whole file | `Dragon_Eye`: `0` hits in generic ASCII scan. | `Dragon.dat` does not appear to directly mention `Dragon_Eye` resources by name. | CONFIRMED | Not necessary unless eye-side integration starts depending on `.dat` files. |
| whole file | `3DMesh`: `0` hits; `bone`: `0` hits. | No direct evidence that `Dragon.dat` stores the same kind of mesh/skeleton naming vocabulary found in the runtime BDAE. | STRONGLY SUPPORTED | If needed, deeper binary parsing could still check for non-string binary geometry blocks. |
| whole file | `.bdae`: `52` hits. Early examples include `max_level_raiser_icon_fx.bdae`, `boardgame_chest_0.bdae`, `fx_levelup.bdae`. | `Dragon.dat` references many BDAE assets as names, but these are mixed UI/effect/game objects rather than a single dragon mesh resource list. | STRONGLY SUPPORTED | Group these filenames by subsystem later if SWF-side asset loading becomes relevant. |
| whole file | `.tga`: `39` hits. Early examples include `Dragon_atlas_default_32.tga`, `Dragon_atlas_default_31.tga`, `Dragon_atlas_default_35.tga`. | The file references texture atlases by name, consistent with SWF/UI resource usage. | STRONGLY SUPPORTED | Not part of the custom BRES mesh/animation path currently under investigation. |
| whole file | `mesh`: `105` hits, but early examples are class/method names such as `MeshBuilder`, `initWithMesh`, `chestMesh`. | `mesh` occurs in UI/game code and builder names, not as clear BRES mesh record names. | STRONGLY SUPPORTED | No current evidence that these hits are raw dragon geometry payloads. |
| whole file | `rotation`: `96` hits, with early examples `EndlessRotationSettings`, `rotation`; `translation`: `5` hits, mainly `translationX`, `translationY`, `appendTranslation`. | Rotation/translation strings exist in general application/UI code, not in the BRES track naming style. | STRONGLY SUPPORTED | Not evidence of the runtime BRES transform track format by itself. |
| whole file | `BDAE`: `3` hits at offsets `0x145665`, `0x17D240`, `0x41CAE?`-equivalent decimal offsets `1332965`, `1561152`, `4312316`. | The string `BDAE` exists inside the file, likely as a resource type/token, but not as a top-level file container magic. | HYPOTHESIS | Dump the surrounding bytes later if SWF-side BDAE asset type handling becomes relevant. |

## Comparison Against BRES/BDAE Files

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `Dragon.dat` vs all compared `.bdae` files | `Dragon.dat` begins with `FWS`; every compared `.bdae` begins with `BRES`. | `Dragon.dat` is a different top-level format from the BRES/BDAE files. | CONFIRMED | None needed; this is a clear container-level distinction. |
| `Dragon.dat` vs runtime BDAE | Runtime BDAE has structured fields at `0x08/0x10/0x20/0x28/0x30/0x38` matching relocation/string/record/data boundaries. `Dragon.dat` does not. | `Dragon.dat` does not fit the currently observed BRES header model. | CONFIRMED | None needed before focusing elsewhere. |
| `Dragon.dat` vs runtime BDAE names | Runtime BDAE contains direct dragon node/track names such as `Lwing_bone01-node-rotation`, `3DMesh_Skinned`, and dragon-specific texture references. `Dragon.dat` does not expose that same skeleton/track vocabulary. | The dragon animation/mesh pipeline is file-side centered in BRES/BDAE, not in `Dragon.dat`. | STRONGLY SUPPORTED | Continue mesh/anim work on the BRES/BDAE path. |

## What `Dragon.dat` Most Likely Is

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| whole file | `FWS` header, XMP metadata, ActionScript package/class strings, `.fla`-style symbol names near EOF, many UI/resource references. | `Dragon.dat` is most likely a Flash/Scaleform-style application/resource blob, not the dragon body mesh/skin animation payload. | STRONGLY SUPPORTED | If later needed, parse SWF tags to prove the exact internal structure. |
| whole file | No `BRES`, no `3DMesh`, no `bone`, no `Dragon_Eye`, and string hits are dominated by generic application/UI content. | Current evidence does **not** support `Dragon.dat` as the primary source for dragon geometry, skin weights, or BRES animation tracks. | CONFIRMED | Shift mesh/skin investigation back toward runtime BDAE records and any other non-SWF companions. |
| whole file | The file still contains `.bdae`/`.tga` names and `mesh`/`rotation` terms. | `Dragon.dat` may still reference or orchestrate assets used elsewhere in the game, but that is different from being the raw BRES dragon container. | HYPOTHESIS | Only revisit if an executable path proves a dragon scene load goes through SWF/AS3 metadata first. |

