---
tags:
  - development
  - phase-1a2a
  - unreal-engine
  - graybox
  - benchmark
status: complete
date: 2026-07-19
---

# Phase 1A.2a: Noncanonical Street Block and Basketball Court Graybox

## Outcome

**GRAYBOX AND REPRESENTATIVE ITERATION PASSED.** Unreal Engine 5.8 now has one separate, noncanonical benchmark map at `client/OddsWell/Content/Maps/BlockCourtBenchmark.umap`. It presents a compact neutral street block, recognizable basketball court, two primitive hoop assemblies, road, sidewalks, four anonymous building masses, built-in collision, and native lighting/environment actors.

The unchanged empty `Bootstrap` map remains the editor and game default. This is representative graybox evidence only—not a city identity, gameplay map, final art direction, camera choice, avatar, navigation proof, multiplayer proof, packaged performance result, or permanent Unreal adoption. No C++, Blueprint graph, custom material, imported art, dependency, project plugin declaration, backend, economy, wagering, replay renderer, deployment, API, or model work was added. Cost was **$0.00**.

## Map inventory

The final map contains 25 `Benchmark_` actors:

| Category | Count | Evidence |
| --- | ---: | --- |
| Ground, road, and sidewalks | 4 | One ground slab, one road, and two sidewalks |
| Court surface and markings | 7 | Surface, center line, four boundaries, and center marker |
| Anonymous building masses | 4 | Built-in cube primitives |
| Hoop assemblies | 6 | Two poles, two backboards, and two rim markers |
| Native lighting/environment | 4 | Directional light, sky light, sky atmosphere, and height fog |
| **Total** | **25** | Cold-process actor inventory verification passed |

All 21 mesh actors use only `/Engine/BasicShapes/Cube.Cube` or `/Engine/BasicShapes/Cylinder.Cylinder`, and every mesh component reopens with the native `BlockAll` collision profile. No final mesh, texture, material, rig, animation, or canon was introduced.

## Build and representative iteration

- Initial built-in-primitive construction and save completed in `0.904s` after the editor-command process had started and loaded the map. This is an editor-operation measurement, not total editor startup time.
- The measured follow-up changed exactly one actor, `Benchmark_Building_04`.
- Location changed from `(3000, -2700, 450)` to `(3000, -2500, 450)`.
- Scale changed from `(8, 5, 9)` to `(10, 5, 9)`.
- The edit plus save completed in `0.486s`.
- A later fresh editor-command process reopened the saved map and independently verified the final transform, actor inventory, built-in meshes, and collision.

The final map is `48,831` bytes with SHA-256 `F970A2F4609F2D6EC24475AE48C98E12DB53BDE2CD95A238F2015C3FF0840018`.

## Visual and editor evidence

- A `1920x1080` local proof image frames the entire block, court, hoop assemblies, road, sidewalks, and four buildings. It is generated evidence under ignored `Saved/Screenshots`, not a production asset.
- Final cold-process Map Check: **0 errors and 0 warnings**.
- Standard shader startup used 11 local workers. SM6 and SM5 autogen headers were unchanged and skipped; no distributed compiler was present. The phase added no custom material or shader, so no material-specific compilation count is claimed.
- The first native T3D import experiments hit two UE 5.8 editor assertions. No questionable imported map was saved and no crash bundle was sent. The successful map was created and verified through Unreal's installed editor Python interface using only built-in engine classes and meshes; those helper scripts remain ignored and are not a project dependency.

## Preserved empty-project boundary

The six Phase 1A.1d portable inputs remained byte-identical:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `client/OddsWell/OddsWell.uproject` | 91 | `647D8775736EF90E3590EB7D98F5A301458948C2804AF2CFD68A272F9B5BB6D8` |
| `client/OddsWell/Config/DefaultEditor.ini` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `client/OddsWell/Config/DefaultEngine.ini` | 2,684 | `A3572A2B40D00436686E523150B8796F36C44EF40584F63B25A26BDBACC4BB8A` |
| `client/OddsWell/Config/DefaultGame.ini` | 357 | `728B0C6F53C5112F7715C5E26B901D9735C6D3FFA9CA83DE317CDBEA1CF727FB` |
| `client/OddsWell/Config/DefaultInput.ini` | 9,022 | `967BDF33123519D5270F44B2A686BE523DE7326CD2C038623B1D1C31FE7B49EA` |
| `client/OddsWell/Content/Maps/Bootstrap.umap` | 8,422 | `44FC5E531591672E10E3740A780EAFB34326C2EADC7D85A37CFA352541932C16` |

`EditorStartupMap` and `GameDefaultMap` still point to `/Game/Maps/Bootstrap.Bootstrap`; `bEnablePlugin=False`, `bAllowNetworkConnection=False`, and the portable security token remains empty. The prior generated Phase 1A.1d package remains exactly 51 files and 968,413,407 bytes. It was not rebuilt or edited, so the empty-package performance baseline remains separate from this graybox.

## Networking, exit, and repository hygiene

- No packaged client or game server ran in this phase, and no network actor, service, endpoint, or portable network setting was added.
- Unreal editor-command startup infrastructure may initialize engine/editor messaging, but that is not player networking and no networking capability is claimed.
- After final verification, no Unreal Editor, command editor, Crash Reporter, Shader Compile Worker, or Unreal Trace Server process remained.
- `BlockCourtBenchmark.umap` is covered by the existing Git LFS rule. Helper scripts, logs, screenshots, caches, crash data, and local editor settings remain ignored and unstaged.

## Validation

- Cold-process Unreal map/content/collision/iteration verification: **passed**.
- Final Map Check: **0 errors, 0 warnings**.
- Frozen regression suite: **65/65 passed** in `160.509s`.
- Brain Admin self-check: **passed**.
- Python compilation: **passed**.
- Six portable project hashes and prior package size/count: **exact**.
- Canvas JSON, Obsidian links, Git LFS pointer, generated-file hygiene, whitespace, and scoped-diff checks: **passed**.

## Next gate

Phase 1A.2b should consume the existing verified 421-frame public replay and render it directly in the benchmark client without calling the simulator or exposing hidden state. That phase must remain a bounded adapter/rendering spike. It must not resimulate basketball, alter the frozen brains or event log, choose the permanent engine, add final city art, or begin character, multiplayer, economy, wagering, deployment, or model work.
