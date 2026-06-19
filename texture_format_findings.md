# Texture Format Findings

## Summary

- The examined dragon `.tga` files are not proprietary TGA-like wrappers.
- All four examined files are standard `DDS ` containers misnamed with a `.tga` extension.
- The body textures are byte-for-byte identical at the 128-byte DDS header level across Metal Seahorse and Crystal Lady.
- The eye textures are also byte-for-byte identical at the DDS header level across both dragons.
- All four examined textures are `DXT5` / `BC3` block-compressed mipmapped textures with sizes that exactly match the expected compressed payload size plus the 128-byte DDS header.

## Examined Files

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_metal_seahorse.tga` | Size `349,680`; SHA256 `728565f533b0c1f8b9d9833a5f872a15d0824cfbc5f5f9529eb1a0bcf1f0a5b6`. | Baseline body texture sample. | CONFIRMED | Decode offline with any DDS-capable viewer to verify the visible dragon body texture. |
| `eye_metal_seahorse.tga` | Size `87,536`; SHA256 `911d5a973d7d8c40d3df143dccd92a5a73a1f532be7fa9520b9df46903406b99`. | Baseline eye texture sample. | CONFIRMED | Decode offline with any DDS-capable viewer to verify the visible eye texture. |
| `dragon_crystal_lady.tga` | Size `349,680`; SHA256 `a699c4e9e5ca9c603b65043aaf044c870762215d3cb9f53b7bfeb7695fe7a40e`. | Second body texture sample. | CONFIRMED | Compare decoded pixels against the Metal body DDS to confirm content differs while header stays stable. |
| `eye_crystal_lady.tga` | Size `87,536`; SHA256 `ea672a04ec0210ba24b29920f6eb4432eea3e6b907de1ece136f34024dba20a6`. | Second eye texture sample. | CONFIRMED | Compare decoded pixels against the Metal eye DDS to confirm content differs while header stays stable. |

## First-Bytes And Header Identity

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `0x00-0x03` in all four examined files | The first four bytes are ASCII `DDS ` (`44 44 53 20`). | These are DDS files, not TGA files. | CONFIRMED | None needed; this is direct container-level proof. |
| `0x04` in all four examined files | DDS header size is `124` (`0x7C`). | Matches the standard legacy DDS header size. | CONFIRMED | None needed. |
| body textures, first `0x80` bytes | `dragon_metal_seahorse.tga` and `dragon_crystal_lady.tga` have identical first `128` bytes. | The body-texture container/header format is identical across both dragon samples. | CONFIRMED | Decode both payloads to compare only pixel content. |
| eye textures, first `0x80` bytes | `eye_metal_seahorse.tga` and `eye_crystal_lady.tga` have identical first `128` bytes. | The eye-texture container/header format is identical across both dragon samples. | CONFIRMED | Decode both payloads to compare only pixel content. |
| body vs eye headers | Body headers differ from eye headers only in dimension, mip-count, and linear-size fields; format fields remain the same. | Body and eye textures share one stable texture-container format with different dimensions. | STRONGLY SUPPORTED | Check more dragons to confirm the same body/eye size pattern remains stable. |
| end of file, all four examined files | The final bytes vary with compressed payload contents and do not contain a TGA footer such as `TRUEVISION-XFILE`. | The files behave like ordinary DDS payloads with no extra TGA-style trailer or proprietary footer requirement. | STRONGLY SUPPORTED | Decode the DDS payloads directly and confirm no trailing bytes remain unused. |

## Parsed DDS Fields

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| body textures `0x08-0x1F` | `flags=0x000A1007`, `height=512`, `width=512`, `pitch_or_linear_size=0x00040000`, `mip_count=10`. | Body textures are 512x512 DDS textures with 10 mip levels. | CONFIRMED | Verify decoded mip chain count in an external DDS tool. |
| eye textures `0x08-0x1F` | `flags=0x000A1007`, `height=256`, `width=256`, `pitch_or_linear_size=0x00010000`, `mip_count=9`. | Eye textures are 256x256 DDS textures with 9 mip levels. | CONFIRMED | Verify decoded mip chain count in an external DDS tool. |
| all four files `0x4C-0x57` | Pixel-format header fields: `pf_size=32`, `pf_flags=4`, `fourCC='DXT5'`. | The examined dragon textures are BC3 / DXT5 block-compressed DDS textures. | CONFIRMED | Confirm via decoded alpha-bearing appearance once previewed. |
| all four files `0x6C-0x70` | `caps=0x00401008`, `caps2=0`. | Standard mipmapped 2D DDS texture flags, with no cubemap/volume flags in the examined samples. | STRONGLY SUPPORTED | Compare against more non-dragon textures to see whether the same caps flags are universal. |

## Payload-Size Cross-Check

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| body textures | For 512x512 BC3/DXT5 with 10 mip levels, the expected compressed payload is `349,552` bytes; adding the 128-byte DDS header yields exactly `349,680`, which matches both body files exactly. | The body textures are plain DDS payloads with no extra custom prefix/suffix. | CONFIRMED | None needed. |
| eye textures | For 256x256 BC3/DXT5 with 9 mip levels, the expected compressed payload is `87,408` bytes; adding the 128-byte DDS header yields exactly `87,536`, which matches both eye files exactly. | The eye textures are plain DDS payloads with no extra custom prefix/suffix. | CONFIRMED | None needed. |

## What This Changes In The Pipeline Model

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| body/eye `.tga` references in runtime BDAEs | The referenced body/eye files open directly as DDS and require no custom unwrapping. | The texture-loading side of the offline viewer can treat these dragon `.tga` assets as DDS files identified by extension mismatch, not as an unknown proprietary texture container. | CONFIRMED | Implement extension-agnostic magic-based texture detection in the offline viewer. |
| Crystal Lady manifest unresolved assets | `fx_spark_alpha.tga` and `shadow_dragon.tga` were requested by the manifest but not found during extraction. | Those missing files may still use the same DDS naming convention, but they remain unverified until found. | HYPOTHESIS | Locate either asset in another archive or extracted folder and parse its first 128 bytes the same way. |

## Not Yet Known

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| executable-side upload path | The current direct file evidence fully identifies the on-disk texture format, but the exact game-side texture loader and GPU upload path have not yet been tied to these dragon DDS files in IDA. | The runtime probably detects/loads them as DDS-like textures despite their `.tga` extension, but that code path is not yet proven. | STRONGLY SUPPORTED | Trace the executable-side load path from one of the texture filenames to texture creation calls. |
