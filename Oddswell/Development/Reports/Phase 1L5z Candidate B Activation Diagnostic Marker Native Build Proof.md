---
title: Phase 1L.5z Candidate B Activation Diagnostic-Marker Native Build Proof
type: report
status: Complete locally - diagnostic marker native build pass
date: 2026-08-18
---

# Phase 1L.5z — Candidate B Activation Diagnostic-Marker Native Build Proof

## Result

`COMPLETE LOCALLY — DIAGNOSTIC MARKER NATIVE BUILD PASS; PACKAGE AND LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 2/6`

One authorized direct UnrealBuildTool attempt compiled both marker-bearing translation units and linked an advanced OddsWell editor module DLL. This is native build proof only. No automation, package, packaged launch, marker observation, policy application, renderer validation, product measurement, or readiness proof occurred.

## Prior phase truth

Phase 1L.5y closed at commit `c6c3e6df5e981e184fbf56d152827d361b4906e6` with independently verified exactly two canonical Project upserts and counted Phase `1/6`. Its `activation_diagnostic_marker_source_authoring_credit=1` remains prior credit.

## Attempt custody

| Field | Evidence |
| --- | --- |
| outcome | `DIAGNOSTIC MARKER NATIVE BUILD PASS` |
| attempts / retry | `1 / 0` |
| tool | signed Epic UnrealBuildTool, `173,496` bytes, SHA-256 `F2BF049446BC1500EF9BC6F28DAA158FB87F49E86CF53276B03A057D4C194571` |
| target | `OddsWellEditor Win64 Development` |
| exit | natural `0`; no timeout or forced cleanup |
| duration | tool wall `10.9228903 s`; UBT-reported `10.34 s` |
| console | complete, not truncated; `Result: Succeeded` |

The exact eight UBT arguments retained the project path, wait mutex, no-hot-reload, no-engine-changes, and direct Phase 1L.5z log path. No wrapper, UAT, repair, or retry was used.

## Stable build evidence

| Artifact | Custody |
| --- | --- |
| `C:\tmp\OddsWellPhase1L5z\build.log` | `7,324` bytes; mtime `2026-08-19T04:23:24.7036400Z`; SHA-256 `87C192548153918DFC5223578ECE127BF512490E90A6E89509610F3755DD77C1` |
| `C:\tmp\OddsWellPhase1L5z\build.json` | `23,697` bytes; mtime `2026-08-19T04:23:24.7036400Z`; SHA-256 `77341977138546DA80533C6FF0D8119E6C4BC6AB903834B30D2ADF48C4B33B9D` |

The log passed two identical nonzero size/SHA/mtime observations at `2026-08-19T04:23:34.8322750Z` and `2026-08-19T04:23:50.9621004Z`, `16.1298254 s` apart. Both files remain preserved outside the repository and uncommitted.

## Direct compile and link proof

- Build-log line `52`: direct `[1/5] Compile [x64] OddsWell.cpp`.
- Build-log line `53`: direct `[2/5] Compile [x64] CandidateBPolicySmoke.cpp`.
- Build-log lines `54–55`: module library and DLL links.
- Build-log line `107`: `Result: Succeeded`.
- Action-graph lines `49–50` corroborate Candidate compilation and DLL-link dependencies. Unity fallback was not needed.

The module DLL advanced from `2,591,232` bytes, mtime `2026-08-18T20:01:57.0957020Z`, SHA-256 `9AE6914DEE022AA67DC5CFCDC76EA97E173F366CF1D5FCBA706C799351B69BC6` to `2,592,256` bytes, mtime `2026-08-19T04:23:23.7610282Z`, SHA-256 `2157ADFE99E90CDD05A3309DAB8ED4AAF330940BE49B530671DBB5F1EFBFAC21`. The generated DLL remains uncommitted.

## Source and postflight custody

- `OddsWell.cpp` stayed SHA-256 `D7F7EE196395CA9500B5EA50B8ADAC2BEB010972A08FAEACE6DE1536FE5FE778`, blob `090e0d6c18c2584d17eae67825fba1867f2cf2db`.
- `CandidateBPolicySmoke.cpp` stayed SHA-256 `DE732410F08B3ADA7D7E373EEF894B38252B0C07F8D6050D7FC7E676B75DFC32`, blob `a448a4cf29db60cfd5c4f5527c1dbefa079802d4`.
- Repository HEAD stayed `c6c3e6df5e981e184fbf56d152827d361b4906e6` and clean after the attempt; target processes and watched TCP/UDP ports were `0` after drain.
- Engine-change refusal, compiler error, fatal, security, and `0x800700E1` marker counts were `0`. This is not a Defender-clean claim.

## Credits, work truth, and gate

- `native_build_credit=1` and `source_compile_credit=1`.
- Prior `activation_diagnostic_marker_source_authoring_credit=1` remains unchanged.
- Automation, package, launch, runtime activation, policy/readback, renderer, visible-window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, and readiness credits are `0`.
- Product remains `NOT_MEASURED`; Candidate B remains owner-selected, provisional, and unvalidated; Phase 1L exit remains incomplete.
- Current task truth is shared `20`, external PermitWatchdog `15`, OddsWell relation `1`, old/new `0/0`, Cursor `0`; global `5` is historical only.
- A later package or launch requires a separate gate. Phase 3/6 is not automatically authorized.
