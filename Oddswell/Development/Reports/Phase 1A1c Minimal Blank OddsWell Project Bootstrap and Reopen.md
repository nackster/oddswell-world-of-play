---
tags:
  - development
  - phase-1a1c
  - unreal-engine
  - project-bootstrap
status: complete
date: 2026-07-19
---

# Phase 1A.1c: Minimal Blank OddsWell Project Bootstrap and Reopen

## Outcome

**READY FOR THE SEPARATE EMPTY-PACKAGE PROOF.** UE 5.8 created the smallest approved Blueprint-only desktop project at `client/OddsWell/OddsWell.uproject`, saved exactly one empty map, closed normally, reopened the project through its exact on-disk path, loaded that same map with zero actors, and closed normally again.

This phase added no packaging, C++, gameplay Blueprint, gameplay plugin, Starter Content, sample, street, court, avatar, camera, movement, NPC, world system, multiplayer, replay adapter, canon, backend, economy, wagering, deployment, model work, Phase 0 change, API, or Admin runtime change. Permanent Unreal adoption remains unclaimed. Cost was **$0.00**.

## Frozen creation settings

| Setting | Verified result |
| --- | --- |
| Category/template | Games -> Blank |
| Project type | Blueprint-only; no `Modules`, source, build rules, or targets |
| Hardware/platform | Desktop / Windows |
| Starter Content | None |
| Ray tracing | Disabled; `r.RayTracing=False` and project proxies `False` |
| Engine association | `5.8` |
| Project path | `client/OddsWell/OddsWell.uproject` |
| Default map | `/Game/Maps/Bootstrap.Bootstrap` for editor and game |

The generated Blank template initially wrote both ray-tracing values as enabled and added the editor-only `ModelingToolsEditorMode` descriptor entry. The scope audit caught both before reopen. After the first normal close, the two values were set false and the unneeded plugin declaration was removed. The reopened editor log confirms ray tracing is disabled through the project setting.

## Portable project files

Only these six files are portable candidates:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `client/OddsWell/OddsWell.uproject` | 91 | `647D8775736EF90E3590EB7D98F5A301458948C2804AF2CFD68A272F9B5BB6D8` |
| `client/OddsWell/Config/DefaultEditor.ini` | 0 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `client/OddsWell/Config/DefaultEngine.ini` | 2,931 | `397496CDE882FAB6FDE14608BC9690C2A348C1CEC660E3D77E4E6EAA30A3EBFB` |
| `client/OddsWell/Config/DefaultGame.ini` | 357 | `728B0C6F53C5112F7715C5E26B901D9735C6D3FFA9CA83DE317CDBEA1CF727FB` |
| `client/OddsWell/Config/DefaultInput.ini` | 9,022 | `967BDF33123519D5270F44B2A686BE523DE7326CD2C038623B1D1C31FE7B49EA` |
| `client/OddsWell/Content/Maps/Bootstrap.umap` | 8,422 | `44FC5E531591672E10E3740A780EAFB34326C2EADC7D85A37CFA352541932C16` |

The descriptor has `FileVersion: 3`, `EngineAssociation: 5.8`, no `Modules`, and no `Plugins`. The Content tree contains one `.umap`, zero `.uasset` files, and no Starter Content. No C++ source, header, `Build.cs`, or `Target.cs` file exists.

## First creation and close

- Project descriptor and editor process began at `2026-07-19 11:45:05` America/Mexico_City.
- The one-time first launch compiled default engine shaders with 11 responsive local workers. Startup completed at `11:50:48`, approximately `5m43s` after process start; this includes the cold shader build.
- An **Empty Level** with zero actors was saved as `Bootstrap` at `11:55:38`. Unreal recorded zero asset thumbnails and a `0.305s` map-save time.
- The save dialog could not register an externally pre-created empty `Maps` folder, so the first save landed at `Content/Bootstrap.umap`. After the normal close, the lone unreferenced map moved within the project to the required `Content/Maps/Bootstrap.umap` path.
- Close was requested at `11:56:23`; the log records editor shutdown, object-subsystem close, `Exiting`, and log close at `11:56:28`. Fatal-like audit count was zero.

## Reopen proof

Windows had no `.uproject` association, and the bounded file-picker attempts exposed no targetable window. No association or system default was changed. The already-approved UE 5.8 Project Browser then showed the exact OddsWell path and Engine 5.8 under Recent Projects; opening that entry produced one unique `OddsWell - Unreal Editor` window.

- The editor showed the `Bootstrap` tab/world, Outliner `Bootstrap (Editor)`, and `0 actors`.
- `OddsWell.log` applied `r.RayTracing=0` and project proxies `0`, then explicitly reported ray tracing disabled through the project setting.
- At `12:06:21`, the log loaded the exact file `client/OddsWell/Content/Maps/Bootstrap.umap`, registered world `Bootstrap`, and reached startup completion at `12:06:22`.
- Fatal audit: zero `Fatal error`, `Critical error`, `Unhandled Exception`, or `Assertion failed` matches.
- Close was requested at `12:07:46`; editor shutdown, object-subsystem close, shader-thread exit, `Exiting`, and log close completed at `12:07:49`.
- Three seconds later no Unreal window remained; seven seconds later no Unreal Editor or shader worker remained.

## Repository boundaries

- `.gitattributes` assigns `*.umap` to Git LFS (`filter`, `diff`, and `merge` are `lfs`; text is unset).
- Existing `.gitignore` rules exclude actual `DerivedDataCache`, `Intermediate`, and `Saved` output. Those generated/cache/local files remain ignored and unstaged.
- The portable tree has one map and no other Content file. No package or build output exists.

## Validation

- Full frozen regression suite: **65/65 passed** in `154.736s`.
- Brain Admin self-check: **passed**.
- Python compilation, affected Obsidian links, roadmap-canvas structure, Git LFS routing/pointer, generated-file hygiene, whitespace, and exact scoped diff: **passed**.

## Next gate

Phase 1A.1d may package and run this unchanged empty Windows project in a separate scoped phase and record disk, build time, launch time, frame time, and memory. It must not add gameplay, final content, a replay adapter, or permanent engine adoption.
