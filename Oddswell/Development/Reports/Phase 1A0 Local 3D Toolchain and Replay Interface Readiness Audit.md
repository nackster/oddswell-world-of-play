---
tags:
  - development
  - phase-1a0
  - 3d
  - toolchain
  - replay-interface
  - readiness-audit
status: complete
date: 2026-07-18
---

# Phase 1A.0: Local 3D Toolchain and Replay Interface Readiness Audit

## Outcome

**READY FOR OWNER INSTALL APPROVAL.** No measured local prerequisite blocks an owner decision to approve one engine/version download and installation. No engine is installed or selected by this phase.

This was a read-only audit. It installed nothing, downloaded nothing, created no engine project, added no adapter or schema, changed no simulator or Admin behavior, used no external service, and cost **$0.00**.

## Measured workstation

| Area | Read-only result |
| --- | --- |
| Operating system | Windows 11 Pro 64-bit, version `10.0.26200`, build `26200` |
| CPU | Intel Core Ultra 9 185H, 16 physical cores / 22 logical processors |
| Memory | 63.4 GiB total; 33.2 GiB free at audit time |
| Discrete GPU | NVIDIA GeForce RTX 4070 Laptop GPU, 8,188 MiB, driver `596.47` |
| Integrated GPU | Intel Arc Pro Graphics, driver `32.0.101.8517` |
| Workspace disk | `C:` 3,813.2 GiB total; 3,053.6 GiB free at audit time |

These are inventory facts, not an engine compatibility or performance claim. Packaged-build frame time and memory still require the owner-approved representative benchmark.

## Local toolchain

| Tool | Read-only result |
| --- | --- |
| Epic Games Launcher | Installed, version `1.3.150.0`, under `C:\Program Files (x86)\Epic Games` |
| Game engine | No Unreal installation found in PATH, Epic manifests, Unreal registry locations, or common Epic install roots on the fixed drive |
| Blender | `4.5.5 LTS`, available from the local user installation |
| Visual Studio | Community 2022, installation `17.14.36408.4` |
| Native compiler | MSVC `14.44.35207`; x64 `cl.exe` and MSBuild are present in the Visual Studio installation |
| Windows SDK | `10.0.22000.0` present |
| Git | `2.49.0.windows.1` |
| Git LFS | `3.6.1` |

The compiler and MSBuild are not on the ordinary shell PATH, but Visual Studio's own installation inventory resolves both. Exact engine/version compatibility remains deliberately unverified until the owner chooses an installer/version.

## Repository readiness

- `.gitignore` already excludes Unreal `Binaries`, `DerivedDataCache`, `Intermediate`, and `Saved` paths at project depth. `git check-ignore` verified all four patterns.
- `.gitattributes` already routes `.uasset`, `.umap`, `.blend`, `.fbx`, `.glb`, and the existing large texture/audio/video formats through Git LFS. `git check-attr` verified the expected LFS filter, diff, merge, and binary text settings.
- Git LFS is operational, but no large 3D or engine assets are tracked yet.
- `.vsconfig` is currently ignored. No engine project exists, so this audit does not guess whether a future generated workload file should be tracked.
- No ignore or attribute rule changed. Recheck the exact generated tree before the first owner-approved engine-project commit.

## Existing replay interface evidence

The current repository independently regenerated `archived_replay_payload(1, 1)` through the same server-side verification path used by archived Game Theater playback.

- Match: Harbor City Waves `101`–`104` Mesa Vista Sol.
- Complete public playback: **421 frames**.
- Final frame: `kind: final`, clock `0`, score `[101, 104]`, label `Final result · replay evidence sealed`.
- Archive evidence: season `1`, game `1`, `verified: true`.
- Replay SHA-256: `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`; it exactly matches the public League Viewer record.
- Public versions: engine `phase05h-v1`, Basketball Brain `baseline-v2`, league `phase06l-v1`, Athlete Life Brain `athlete-life-v4`, Consistency `athlete-consistency-v2`, Offensive Involvement `offensive-involvement-v1`, and prediction `phase0d4-v1`.

The existing client-facing replay payload already provides:

- summary identity, roster, score, decision count, record count, engine/brain versions, and replay-frame count;
- ordered theater frames with kind, label, clock, score, offense, actor, target, and lineups; and
- archive season/game identity, replay seal, involvement version, and verified status.

The random seed, pregame fatigue/readiness, recovery timers, injury-risk internals, RNG state, and stored resolver snapshots remain server-side. The server uses them to reconstruct and verify the archive, then returns recorded public outcomes. A future 3D client must render this recorded payload and must never run a second basketball simulation.

No new adapter, endpoint, schema, or API is justified before an engine exists; the current read model is sufficient for the first integration spike.

## Validation

- Full frozen regression suite: **65/65 passed**.
- Brain Admin self-check: **passed**.
- Python compilation, Obsidian link targets, affected canvas structure, repository whitespace, and scoped diff checks: **passed**.
- Runtime/source/schema/API changes: **none**.

## Owner gate

The next action requires the owner's explicit approval of one engine and version installation. Only after that approval should a separate phase verify the installed editor, create the smallest empty local project, package it once, and measure baseline build time, frame time, memory, and disk use. Phase 1A.0 does not begin that work.
