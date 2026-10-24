---
tags:
  - development
  - phase-1a2b
  - unreal-engine
  - replay
  - benchmark
status: complete
date: 2026-07-19
---

# Phase 1A.2b: Authoritative 421-Frame Replay Renderer

## Outcome

**DIRECT RECORDED-REPLAY RENDERING PASSED.** The UE 5.8 benchmark client now loads and displays the existing verified Season 1 Game 1 public replay from first frame through final result. It does not call the simulator, choose actions, resolve outcomes, expose hidden state, or alter the authoritative record.

The renderer is active only when the executable receives `-ReplayBenchmark`. The unchanged `Bootstrap` map remains the editor and game default. The separate `BlockCourtBenchmark` graybox remains noncanonical. This phase does not choose the permanent engine, final camera, physical player tracking, city identity, character direction, final art, multiplayer, economy, wagering, deployment, or model work. Cost was **$0.00**.

## Frozen public replay input

`client/tools/export_unreal_replay.py` exports `archived_replay_payload(1, 1)` into the staged non-UFS fixture `client/OddsWell/Content/Replay/Season1Game1.json`.

| Evidence | Value |
| --- | --- |
| Schema | `oddswell-public-replay-v1` |
| Match | Harbor City Waves 101 - 104 Mesa Vista Sol |
| Frames | 421 |
| Bytes | 256,442 |
| Fixture SHA-1 runtime lock | `a3b56bf84557babcd58c96acd40f94198b6c8c81` |
| Fixture SHA-256 build evidence | `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| Authoritative replay SHA-256 seal | `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |

The exporter asserts the matchup, scores, frame count, final frame, verified archive flag, replay seal, and forbidden-key boundary. Seed, RNG, fatigue, readiness, recovery, injury-risk, and resolver keys are absent. The packaged fixture is byte-identical to the tracked fixture.

At runtime the client rejects a missing file, malformed JSON, wrong schema, wrong teams, wrong score, wrong player counts, wrong frame count, unverified archive, wrong replay seal, wrong final frame, or changed fixture bytes. Unreal's supported cross-platform SHA-1 helper guards the exact local fixture bytes; the authoritative event-log identity remains the existing SHA-256 replay seal.

## Renderer

The smallest native runtime module adds one benchmark-only replay actor:

- 12 built-in primitive player markers: cylinders for Harbor City and cubes for Mesa Vista;
- fixed, explicitly illustrative court positions because the headless simulator does not record physical coordinates;
- player labels, score, game clock, event kind and label, offense, actor, and target;
- temporary size/height emphasis for the recorded actor and target;
- visible final replay seal;
- optional midpoint and final screenshots;
- automatic exit and configurable playback interval for repeatable checks.

The runtime module spawns the actor only for `-ReplayBenchmark`. It has no Python runtime, simulator import, random source, network call, service, endpoint, plugin declaration, or dependency beyond Unreal's Core, Engine, CoreUObject, and Json modules.

## Build prerequisite and compilation

The first native compile correctly exposed one missing local prerequisite: Unreal Build Tool could not instantiate `SwarmInterface` without a .NET Framework SDK. With explicit owner approval, Visual Studio Installer added only **.NET Framework 4.8 SDK** (`Microsoft.Net.Component.4.8.SDK`, displayed size 27 MB). The owner manually approved Windows UAC. No Visual Studio workload, IDE update, paid component, or unrelated SDK was selected.

The final UE editor and game targets compile with Visual Studio toolchain `14.44.35214` and Windows SDK `10.0.22000.0`. The final incremental Windows BuildCookRun completed successfully in `58.14s`.

An attempted pre-final use of Unreal's generic platform SHA-256 helper compiled but asserted in the packaged Windows runtime because UE 5.8 provides no implementation there. Those two failed diagnostic launches are not acceptance evidence. The helper was removed and replaced with Unreal's supported `FSHA1`; both final packaged runs then completed with zero replay, fatal, or critical errors.

## Packaged execution evidence

The final packaged Development build contains 50 static files totaling 1,040,077,964 bytes (`0.969 GiB`) when runtime-generated `Saved` evidence is excluded. Its loose staged replay fixture matches both tracked fixture hashes above.

Two final packaged runs produced all of the following:

| Check | Run 1 | Run 2 |
| --- | ---: | ---: |
| Process exit code | 0 | 0 |
| Rendered replay frames | 421 | 421 |
| Final score | 101-104 | 101-104 |
| Replay errors | 0 | 0 |
| Canonical frame-trace SHA-256 | `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe` | same |
| Authoritative replay seal | exact | exact |

The canonical trace strips engine timestamps and hashes only the ordered `ODDSWELL_REPLAY_FRAME` records. Both packaged runs match each other and the earlier editor traces exactly, proving that the client replay path is deterministic and does not resimulate the game.

A separate final packaged measurement sampled the process 40 times at 200 ms intervals across startup, all 421 replay frames, and shutdown:

- wall time: `8.861s`;
- average working set: `1.213 GiB`;
- peak working set: `1.763 GiB`;
- peak private bytes: `3.801 GiB`;
- exit code `0`, 421 frames, and zero replay errors.

These are local Development-build measurements, not beta performance targets. The intentionally accelerated `0.01s` event interval is test playback, not the final two-to-five-minute match-presentation cadence.

## Visual evidence

Ignored local `1280x720` midpoint and final screenshots show the full existing graybox, all symbolic player markers, live public replay text, the 101-104 final score, and the verified replay seal. They are proof artifacts under `Saved/Screenshots`, not production assets.

## Preserved boundaries

- `Bootstrap.umap` remains 8,422 bytes with SHA-256 `44fc5e531591672e10e3740a780eafb34326c2eadc7d85a37cfa352541932c16`.
- `BlockCourtBenchmark.umap` remains 48,831 bytes with SHA-256 `f970a2f4609f2d6ec24475ae48c98e12db53bde2cd95a238f2015c3ff0840018`.
- `EditorStartupMap` and `GameDefaultMap` still point to `/Game/Maps/Bootstrap.Bootstrap`.
- Android file-server networking remains disabled and its security token remains empty.
- Generated binaries, packages, logs, screenshots, caches, and local settings remain ignored.
- No authoritative simulation, league, prediction, career, life, consistency, involvement, or Admin runtime file changed.

## Validation

- Final editor/game C++ compilation: **passed**.
- Final Windows BuildCookRun: **passed**.
- Two final packaged 421-frame runs: **passed and trace-identical**.
- Final measured packaged run: **passed**.
- Fixture export, byte hashes, public-only key guard, and packaged-copy equality: **passed**.
- Frozen regression suite: **65/65 passed** in `131.138s`.
- Brain Admin self-check: **passed**.
- Python compilation: **passed**.
- Obsidian links, affected canvas JSON, generated-file hygiene, whitespace, and scoped-diff checks: recorded with the phase commit.

## Next gate

**Phase 1A.3 is an OWNER GATE.** The owner reviews the empty-package, block/court iteration, visual replay, deterministic trace, packaged-build, and local resource evidence and then accepts Unreal Engine 5.8 for continued beta work, rejects it, or requests one specific measured comparison. Character selection, camera/movement, city canon, and every later beta system remain inactive until that decision is recorded.
