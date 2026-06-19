# DML BRES Reconstruction — Latest Consolidated Progress

## New achievements in this pass

### 1. Generic multipass renderer implemented

A new experimental script, `render_bres_scene_generic.py`, now reads the runtime BDAE and automatically recovers:

- main mesh primitive groups;
- ordered draw names embedded in `stage0`;
- matching material table entries;
- profile assignment (`Dragon.bdae`, `Dragon_Eye.bdae`, `TextureAnim.bdae`);
- body / eye / FX texture role;
- candidate eye `textureOffset`;
- separate `stage1` shadow quad.

It was run successfully on both Crystal Lady and Metal Seahorse.

### 2. Main draw-group → profile bridge recovered

#### Crystal Lady

| Group | Draw name | Profile | Texture role |
| ---: | --- | --- | --- |
| 0 | `body` | `Dragon.bdae` | body |
| 1 | `front_body` | `Dragon.bdae` | body |
| 2 | `front_wing` | `Dragon.bdae` | body |
| 3 | `eye_10p1s` | `Dragon_Eye.bdae` | eye |
| 4 | `fx` | `TextureAnim.bdae` | `fx_spark_alpha.tga` |

#### Metal Seahorse

| Group | Draw name | Profile | Texture role |
| ---: | --- | --- | --- |
| 0 | `body` | `Dragon.bdae` | body |
| 1 | `eye_10p3` | `Dragon_Eye.bdae` | eye |
| 2 | `body1` | `Dragon.bdae` | body |
| 3 | `body2` | `Dragon.bdae` | body |

Important correction: Metal `group_3` is **not** a shadow/effect pass. It is explicitly named `body2` and bound to `Dragon.bdae`.

### 3. UV/sampler findings tightened

Per-group UV analysis establishes why naive clamp sampling fails:

| Runtime / draw | UV evidence |
| --- | --- |
| Crystal `body` / `front_wing` | Almost entirely within `0..1` |
| Crystal `fx` | Out-of-range UVs, compatible with animated/tiling FX |
| Metal `body` | `84` vertices out of `0..1`, `U` reaches `1.534` |
| Metal `body2` | All `27` vertices have negative `U` |

Using repeat addressing for `Dragon.bdae` body draws restores Metal's missing head and `body2` content. Explicit numeric sampler-state recovery is still pending: no readable `wrap/repeat/clamp` string was found in the profile or shader descriptors.

### 4. Shadow stage decoded

Both runtime BDAEs contain a separate `stage1` shadow drawable:

```text
4 vertices × 24 bytes
2 triangles: [0,1,2, 2,3,0]
material: shadow
texture: shadow_dragon.tga
```

The shadow geometry is byte-equivalent in Crystal and Metal. Its four vertices lie nearly on a constant-Z plane, so:

- the dragon body is best inspected in front projection `XZ`;
- the shadow is best inspected in floor projection `XY`;
- it should not be composited into the front-facing sprite view without a camera/scene transform.

The decoded `XY` render produces the expected soft elliptical shadow.

### 5. Rig palette binding recovered directly from records

The skin influence slot mapping is now explicit. Runtime binding records contain:

```text
semantic-node pointer, semantic-name pointer, Bone# pointer
```

The already decoded 0-based per-vertex slot bytes map as:

```text
slot N → Bone(N+1) → semantic node
```

Recovered counts:

| Runtime | Skin slots used | Explicit palette bindings recovered |
| --- | ---: | ---: |
| Crystal Lady | 37 | 37 |
| Metal Seahorse | 32 | 32 |

Examples:

| Runtime | Slot | Palette | Semantic node |
| --- | ---: | --- | --- |
| Crystal | 4 | `Bone5` | `Head_CTRL-node` |
| Crystal | 14 | `Bone15` | `Lwing_bone01-node` |
| Crystal | 35 | `Bone36` | `tail_A_01-node` |
| Metal | 5 | `Bone6` | `Head_CTRL-node` |
| Metal | 12 | `Bone13` | `Lwing_bone01-node` |
| Metal | 30 | `Bone31` | `tail_A_01-node` |

Many named rotation/translation tracks can now be joined directly to the vertices affected by their bones.

### 6. Animation-stream probe started, but playback is not yet safe

The newly mapped tracks were inspected at their candidate data targets.

- Metal candidate track regions often contain readable float-triplet patterns.
- Crystal candidate track regions more often look like packed/descriptor blocks and are consistent with the IDA-side packed quaternion decoder path already discovered.
- The exact semantics of `inputRel`, `outputRel`, and `extraRel`, and their relation to final per-frame transforms, remain unproven.

Therefore animation playback is **not** implemented yet. The next safe work is to identify the track stream/cooked-descriptor construction path or to decode the packed file-side structures more rigorously.

## Current solved layer

```text
BUD extraction                               solved for current dependencies
DDS-in-.tga texture decoding                 solved
Runtime BRES header/sections                 solved enough for current viewer
Static main mesh geometry / index groups     solved across Crystal + Metal
Group → material/profile role                structurally recovered
Eye pass                                     structurally recovered
Crystal FX pass identity                     structurally recovered
Shadow mesh stage                            decoded as floor quad
Per-vertex skin influence records            validated
Skin palette slot → semantic node            recovered
Track name → influenced bone/vertex region   recovered for mapped rig nodes
Actual animation value sampling/playback     next unresolved layer
```

## No additional assets currently required

The present samples are enough to continue into track decoding. The highest-value future assistance would be IDA tracing of the file-to-cooked-descriptor builder or additional runtime BDAEs exhibiting simpler/smaller animation sets, but neither is required to continue file-side experiments.
