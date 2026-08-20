---
title: Phase 1L.5aa Candidate B Activation-Diagnostic Development Package Build and Custody
type: report
status: Complete locally - diagnostic marker package build pass
date: 2026-08-19
---

# Phase 1L.5aa — Candidate B Activation-Diagnostic Development Package Build and Custody

## Result

`COMPLETE LOCALLY — DIAGNOSTIC MARKER PACKAGE_BUILD_PASS; PRODUCT NOT MEASURED; FRESH BATCH PHASE 3/6`

This was the held Phase 3/6 started in the prior nightly batch; its recovery closure counts only there. Current heartbeat new-phase count: 0.

One authorized direct signed-cmd/dotnet BuildCookRun attempt exited naturally `0`, completed build/cook/stage/package/archive, and produced an exact development-package custody set. No package or game was launched. This is package build and custody proof only; it is not runtime diagnostic-marker, policy-application, renderer, gameplay, performance, compatibility, accessibility, beta-exit, or readiness evidence.

## Prior phase truth

Phase 1L.5z closed at commit `c97bb111ecab1b2af89cec00d9aa20d04454276f` with independently verified exactly two canonical Project upserts and counted Phase `2/6`. Its native-build, source-compile, and earlier marker-source-authoring credits remain prior credits only.

## Attempt custody

| Field | Evidence |
| --- | --- |
| outcome | `PACKAGE_BUILD_PASS` |
| attempt / retry | `1 / 0` |
| cmd PID / start | `25544` / `2026-08-19T04:44:12.0863010Z` |
| exit / elapsed | natural `0` / `270.6580234 s` |
| timeout / forced cleanup | `false / false` |
| raw argument identity | `614` characters / `614` UTF-8 bytes / SHA-256 `3E1069D4A085A73D9DF8D5ED871AAC86F6087AF5366D7586B7A968079285AF65` |
| logical cmd / dotnet child arguments | `6 / 20` |

The process-created transcript was the direct combined stdout/stderr evidence; tool return and internal logs were not substituted. The unrelated pre-existing `cmd.exe` PID `26944` remained untouched. No retry, package launch, game launch, Defender action, or cleanup occurred.

## Exact-four evidence

| Evidence file | Bytes | SHA-256 |
| --- | ---: | --- |
| `BuildCookRun.combined.txt` | `83,007` | `1F3FB8FD30DD615EC4A39FB7F18E3A71C9421373CA11CFACAE7D2F4DCD4718BE` |
| `session_custody.tsv` | `3,667` | `A03934A7C27731615D3A1F065A235477E52E6F4DBEB0B9317DA78BF0AB09D507` |
| `package_manifest.tsv` | `6,266` | `BE0DFA48AC51AB9FB94D2C2CD411108FA274D1D9EB5EAF6711E30AE39D4C7871` |
| `saved_manifest.tsv` | `6,266` | `BE0DFA48AC51AB9FB94D2C2CD411108FA274D1D9EB5EAF6711E30AE39D4C7871` |

The transcript stayed immutable across two identical observations `15.0387208 s` apart. It is strict UTF-8 without BOM or NULs, contains `931` CRLF records, no bare LF/CR, and ends in CRLF. Session custody has exactly `96` unique keys and no placeholders. The single authorized evidence patch created only the three TSV files.

## Build and marker custody

- Build, cook, stage, package, and archive start/completion markers each appear exactly once.
- `BUILD SUCCESSFUL` and AutomationTool exit-success markers each appear exactly once.
- Exact non-argv `HasMapsToCook` and `Params.HasMapsToCook` markers each appear once.
- Direct progress compiled `CandidateBPolicySmoke.cpp` twice and `OddsWell.cpp` twice across the required targets, then linked the game executable once.
- Named missing-package failure, fatal, security, engine-change, and `0x800700E1` marker counts are `0`. This is not a Defender-clean claim.

## Package and staged-mirror custody

PackageFinal `Windows` and the separately labeled project `Saved/StagedBuilds/Windows` mirror each contain exactly `50` files totaling `1,052,111,532` bytes. Their case-sensitive ordinal manifests each contain `50` unique rows and share the same exact identity. Fresh replay against both live roots reports missing/mismatch/unexpected `0/0/0`; normalized cross-root mismatch is `0`.

Custody includes wrapper executable `1`, direct game executable `1`, required named `.pak/.utoc/.ucas` `1/1/1`, case-variant container duplicates `0`, Saved-segment files inside PackageFinal `0`, and Python-family files `0`. The package and staged roots remain preserved and uncommitted.

## Credits, nonclaims, and external task drift

- `diagnostic_marker_package_build_credit=1` and `diagnostic_marker_package_custody_credit=1`.
- Prior native-build, source-compile, and marker-source-authoring credits remain prior only.
- Launch, runtime activation, marker observation, product measurement, policy/readback, renderer, visible-window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits are `0`.
- Product remains `NOT_MEASURED`; Candidate B remains owner-selected, provisional, and unvalidated; Phase 1L exit remains incomplete.
- The released task snapshot was shared `20` and external PermitWatchdog `15`; an external drift later reported shared `25` and PermitWatchdog `20`. OddsWell relation `1` remained unchanged, OddsWell new tasks stayed `0`, and Cursor stayed `0`. This recovery performed no task mutation.
- No new phase, source/config/package/evidence mutation, launch, cleanup, or automatic continuation is authorized by this documentation closure.
