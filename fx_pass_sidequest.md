# FX Pass Sidequest

This report compares a dragon whose effect-looking content appears to be embedded in the main dragon BDAE against a dragon with a tiny standalone FX BDAE.

Current working conclusion:

- `dragon_paper_lantern.bdae` is a mesh/skin-bearing dragon BRES that directly references multiple FX textures, `TextureAnim.bdae`, and additive/premultiplied profile strings.
- `fx_buble_dragon_buble.bdae` is a very small standalone effect/emitter BRES, not a dragon mesh container.
- `fx_paper_lantern.png` looks strange as a standalone image because it is very likely an effect atlas intended for additive or premultiplied treatment rather than a normal final-color sprite.
- Some DML dragon FX are likely animated/composited passes rather than static overlays: direct BRES strings include `TextureAnim.bdae`, `textureOffset`, `overlife_*`, additive/premultiplied profiles, and emitter-like `gnps_emitter` node names.

## Evidence Table

| Address or file offset | Raw observation | Interpretation | Confidence | How to test/confirm next |
| --- | --- | --- | --- | --- |
| `dragon_paper_lantern.bdae`, size `106,272` bytes, SHA256 `3f0918ca3f3a08a7e78b45cb9caec3b9398d1af30203333984d1fe753d7878a8` | File begins with `BRES`. Header and section values from direct inspection are `size=0x19F20`, `headerSize=0x40`, `relocCount=1134`, `stringsStart=0x23B0`, `stringsEnd=0x3780`, `recordsStart=0x38A0`, `dataStart=0x10268`. | Paper Lantern uses the same broad BRES-family container model as the other dragon assets. | CONFIRMED | Keep comparing its record families against runtime and base dragon BDAEs. |
| `dragon_paper_lantern.bdae`, string region | Direct string inspection shows `Dragon.bdae`, `Dragon_Eye.bdae`, `TextureAnim.bdae`, `dragon_paper_latern.tga`, `eye_paper_latern.tga`, `fx_ancient_attack_rings_01.tga`, `fx_paper_lantern.tga`, `fx_spark.tga`, `shadow_dragon.tga`. | Paper Lantern's main dragon file directly carries both normal dragon dependencies and multiple FX dependencies. | CONFIRMED | Tie each texture/BDAE reference to the owning material/profile record. |
| `dragon_paper_lantern.bdae`, profile/material strings | Same direct string scan shows `Dragon_Eye-fx-profile_GLES2/CurrentTechnique`, `Dragon2-fx-profile_GLES2/CurrentTechnique`, `#Dragon_Eye-fx`, `#Dragon2-fx`, `#TextureAnim-fx`, plus many `Additive*`, `AdditivePreMul*`, `_Colorized`, `_Fade`, and `_STENCIL` names. | Paper Lantern is a strong example of FX being expressed through material/profile techniques inside the main dragon BDAE instead of only through a separate `fx_*.bdae`. | STRONGLY SUPPORTED | Find the owning records and executable-side pass binder for these profile names. |
| `dragon_paper_lantern.bdae`, track summary | BRES inspection shows `totalTracks = 0`. | This is not a dragon runtime animation-track bundle like Metal Seahorse or Crystal Lady; it is better modeled as a mesh/render/effect graph asset. | CONFIRMED | Compare with any Paper Lantern runtime-style asset if one is later found. |
| `dragon_paper_lantern.bdae`, mesh bridge | Prior BRES inspection found `meshName = lantern-mesh`, `meshSkinName = lantern-mesh-skin`, `mesh3DName = 3DMesh_Skinned`, owner around `0x4A08`, `stage0Abs = 0x9CB8` size `1744`, `stage1Abs = 0x119D0` size `328`, `skinStageAbs = 0x11B88` size `3000`. | Paper Lantern's main BDAE is not an FX-only asset; it owns a concrete dragon mesh/skin payload alongside its FX/material references. | CONFIRMED | Recover its drawable groups and see which ones bind body, eye, FX, or shadow passes. |
| `dragon_paper_lantern.bdae`, deeper stage targets | Same prior mesh-bridge inspection found skin-stage targets near `0x12740` with normalized-weight-like content and around `0x15DB8` with mixed binding/reference-like content. | Paper Lantern's embedded FX references coexist with normal skinned-dragon payload structure, not a separate non-mesh object model. | STRONGLY SUPPORTED | Compare those references against node/material binding names. |
| `fx_buble_dragon_buble.bdae`, size `2,232` bytes, SHA256 `ef747152dc997117e4728d5e63bf731bc1f24f3b35a9d7d150b936e37cd78f33` | File begins with `BRES`. Direct section values are `size=0x8B8`, `headerSize=0x40`, `relocCount=31`, `stringsStart=0x138`, `stringsEnd=0x348`, `recordsStart=0x468`, `dataStart=0`. | Bubble Dragon's FX file is a tiny standalone BRES object, structurally very different from Paper Lantern's main mesh-bearing BDAE. | CONFIRMED | Compare against more standalone `fx_*.bdae` assets to find recurring emitter/effect patterns. |
| `fx_buble_dragon_buble.bdae`, string region | Direct string inspection shows `Dragon.bdae`, `fx_buble_dragon_buble.bdae`, `fx_soap_bubble.tga`, `Y:/Textures/DLC_0_textures/fx_soap_bubble.tga`, `node-node-gnps_emitter`, `overlife_animations_dummy_clip`. | Bubble Dragon appears to use a separate emitter/effect graph resource for at least one of its effects. | STRONGLY SUPPORTED | Compare this file against other tiny FX BDAEs and inspect whether `gnps_emitter` is a reusable effect-node pattern. |
| `fx_buble_dragon_buble.bdae`, BRES summary | Prior BRES inspection found `totalTracks = 0` and no `meshBridge`. | Bubble's standalone FX BDAE is not a skinned dragon mesh payload and should not be treated like a runtime dragon body asset. | CONFIRMED | Keep it in the viewer as a separate FX/effect asset class. |
| `fx_paper_lantern.tga`, size `349,680` bytes, SHA256 `7cf0172c8c3102ae150d0ba998aacec31d8c238116534b90b595b662585f357f` | Direct DDS inspection shows standard `DDS ` magic, `512x512`, `DXT5/BC3`, `10` mip levels. | Paper Lantern's FX texture container is normal DDS, not a proprietary image wrapper. | CONFIRMED | Decode it directly in the viewer with the existing DDS path. |
| `fx_paper_lantern.png`, SHA256 `a9687f5e5e2e19cfc70193b9e1129804cb3bad5b34b57ec0c3b33c2d6cfff0ca` | Direct pixel stats on the PNG are `512x512`, `MeanA ~ 27.425`, `MeanR ~ 239.668`, `MeanG ~ 172.655`, `MeanB ~ 60.288`, and only about `27.963%` of pixels have nonzero alpha. | The raw exported image is dominated by warm emissive color with sparse visible alpha coverage, which is consistent with an additive or premultiplied effect atlas looking "wrong" when viewed as an ordinary standalone sprite. | STRONGLY SUPPORTED | Render this texture through additive and premultiplied debug compositors in the viewer instead of treating it like a normal diffuse layer. |
| `viewer_prototype/render_fx_texture_preview.py` output | The new standalone FX preview generated raw RGBA, alpha visualization, straight-alpha checker, premultiplied-alpha checker, additive-black, additive-dim-scene, and additive-dim-scene-2x previews for `fx_paper_lantern.tga`. | The viewer can now test the likely compositing families for effect atlases without pretending the final material/pass assignment is solved. | CONFIRMED | Use these previews on more `fx_*.tga/.dds/.png` files and compare against in-game appearance. |
| `generated/experimental/fx_texture_previews/fx_paper_lantern/fx_texture_preview_summary.json` | Summary records `fx_paper_lantern.tga` as `512x512`, SHA256 `7cf0172c8c3102ae150d0ba998aacec31d8c238116534b90b595b662585f357f`, with generated additive and premultiplied preview paths. | Paper Lantern FX atlas is now a regression fixture for blend-mode previews. | CONFIRMED | Keep this output while iterating on FX compositing. |
| IDA strings around particle/effect systems | Read-only string search found `ParticleSystem`, `collada::CParticleSystemEmitterSceneNode`, `_particle_custom_vx_attribute`, `[Glitch / Particle System] - Cannot find or guess texture -> tex coord link for particle system`, and `node_copy-node-gnps_emitter`. `node_copy-node-gnps_emitter` has a code xref from `0x7FF72115A800`. | The engine has a particle/emitter path with texture-coordinate linkage; standalone FX BDAEs with `gnps_emitter` are plausible particle/effect graphs. | STRONGLY SUPPORTED | Decompile `0x7FF72115A800` read-only and trace how emitter nodes connect to texture/material data. |
| `fx_buble_dragon_buble.bdae`, root/strings | Inspector categorizes `node-node-gnps_emitter`, `fx_soap_bubble.tga`, and `overlife_animations_dummy_clip` style evidence in a tiny BRES with no mesh bridge. | Bubble's FX BDAE is a good test case for non-mesh particle/effect asset handling. | STRONGLY SUPPORTED | Build a future `inspect-fx-bres` mode that dumps emitter records and over-life/texture animation data separately from mesh records. |

## Current Best Interpretation

- Paper Lantern is a good counterexample to the assumption that "nice-looking in-game FX implies a separate `fx_*.bdae` file."
- In this sample, the dragon's main BDAE already carries:
  - dragon mesh/skin payload,
  - body/eye/shadow references,
  - dedicated FX textures,
  - `TextureAnim.bdae`,
  - multiple additive/premultiplied technique/profile names.
- Bubble Dragon shows the other pattern:
  - a tiny standalone FX/emitter BDAE that names an effect texture and emitter-like node strings.
- Animated texture clues should be treated as their own layer:
  - `TextureAnim.bdae`,
  - `textureOffset`,
  - `overlife_*` animation names,
  - additive/premultiplied material profiles.
- Particle clues should be treated as separate from static mesh rendering:
  - `gnps_emitter` node names,
  - engine strings mentioning particle systems and particle texture-coordinate linkage.

## Viewer Implication

The viewer should not hardcode one FX asset model. It should support at least two cases:

1. Embedded FX/material passes inside the main dragon BDAE.
2. Separate standalone `fx_*.bdae` effect graphs.

For Paper Lantern specifically, `fx_paper_lantern.png` should not be judged by its standalone appearance alone. The stronger working model is:

`fx_paper_lantern DDS atlas`
-> `Dragon2-fx` / `TextureAnim-fx` / `Dragon_Eye-fx` material-profile path
-> additive or premultiplied compositing in-engine
-> much better-looking in-game result than the raw PNG preview suggests

Current viewer boundary:

- Safe now: decode DDS-backed FX atlases and emit additive/premultiplied/alpha debug previews.
- Safe now: list animated-texture and particle/emitter evidence from BRES strings.
- Not solved yet: UV scrolling, flipbook frame selection, particle spawning, over-life curves, and exact pass-to-texture assignment.
