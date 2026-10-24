# Phase 1L.5ag — Candidate B Single-Action Non-Detoured Game Build Proof

## Status

`COMPLETE LOCALLY — SINGLE_ACTION_NONDETOURED_GAME_BUILD_PASS; PACKAGE AND LAUNCH NOT RUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 5/6`

- Outcome: `SINGLE_ACTION_NONDETOURED_GAME_BUILD_PASS`.
- Qualifier: `NONE`.
- Attempt consumed: `1`; attempt number: `1`; retry allowed: `false`.
- Product measured: `false`.

## Prior phase custody

Phase 1L.5af closed at commit `43a0af690ad8dd92a1f58e7d97b1c73a368e0532` with independently verified exactly two canonical Project upserts and counted Phase `4/6`.

Its `PACKAGE_EVIDENCE_LIMITED` outcome, `TIMEOUT_IN_UBA_LOW_MEMORY_LOOP` qualifier, absent Phase 1L.5af package, and `exact_sundale_claim_package_build_credit=0` / `exact_sundale_claim_package_custody_credit=0` remain unchanged. This phase is a new native game-target build proof, not a retroactive Phase 1L.5af package pass.

## Build contract

The one direct attempt invoked signed `C:\Windows\System32\cmd.exe` with a single pre-serialized argument string of `379` characters and UTF-8 bytes, SHA-256 `DEABBF48DB2421EB827181902299EF00D0FC9F277BC79BF766F23153651D7B2C`. Its child is the signed UE 5.8 `UnrealBuildTool.exe` with exactly `10` arguments.

| argument invariant | observed |
|---|---:|
| logical cmd argument count | `6` |
| UBT child argument count | `10` |
| `-NoUBA` count | `1` |
| `-MaxParallelActions=1` value | `1` |
| `-DisableUnity` count | `1` |
| clean argument count | `0` |

This is the frozen single-action, non-detoured proof configuration: only one native compile/link action is scheduled at a time, unity is disabled so the Candidate translation unit remains individually observable, and every action row is marked `[NoUba]`. The transcript also records UBA infrastructure initialization and remote-execution disablement; those lines do not replace or contradict the direct `[NoUba]` action evidence.

## Attempt custody

| field | observed |
|---|---|
| cmd PID | `61572` |
| start UTC | `2026-08-21T14:47:41.2756308Z` |
| exit | `0` |
| exit origin | `NATURAL_CHILD_PROPAGATED` |
| elapsed | `98.709134 s` |
| natural exit | `true` |
| timed out | `false` |
| forced cleanup | `false` |
| taskkill invoked | `false` |
| process drain observed | `true` |

No retry, repair, package, game launch, Defender query, or cleanup occurred.

## Exact evidence

| artifact | bytes | SHA-256 | role |
|---|---:|---|---|
| `C:\tmp\OddsWellPhase1L5ag\Evidence\build.combined.txt` | `2548` | `44E8101D8893335B6C8AED2E52CEF4DF8D0996BC631AE2D53241DA0F6C9B951D` | process-created combined build transcript |
| `C:\tmp\OddsWellPhase1L5ag\Evidence\session_custody.tsv` | `2947` | `4000A5568C5ADB85D171EBE425C3C743092EC903F4A2BA9324177000DF69EA32` | exact `74`-row session custody |

The transcript last-write time is `2026-08-21T14:49:19.9050829Z`. Stable observations at `2026-08-21T14:49:31.0286416Z` and `2026-08-21T14:49:39.8108027Z` were `8.7821611 s` apart and returned identical size and SHA. The file is strict UTF-8 without BOM, contains `0` NUL bytes, was created by the process redirect, is complete through drain, and was never rewritten.

The exact-two replay passes. The session has the exact header plus `74` ordered unique nonblank rows, UTF-8 without BOM or NUL, LF-only line endings, and final LF. The evidence directory contains exactly two files.

## Build result

| predicate | count |
|---|---:|
| `Result: Succeeded` | `1` |
| `Compile [x64] CandidateBPolicySmoke.cpp [NoUba]` | `1` |
| `Link [x64] OddsWell.exe [NoUba]` | `1` |
| BUILD FAILED | `0` |
| engine-change refusal | `0` |
| compiler error | `0` |
| linker error | `0` |
| fatal marker | `0` |
| security marker | `0` |
| low-memory marker | `0` |

Every one of the `21` compile/copy/link/metadata action rows is marked `[NoUba]`, and the executor reports a maximum of one action. The Candidate compile and game link are therefore direct, separately visible source/build facts rather than unity or multi-action ambiguity.

## Generated output identities

Both target outputs were absent before the attempt and present afterward:

| output | post bytes | post SHA-256 | post mtime UTC |
|---|---:|---|---|
| `CandidateBPolicySmoke.cpp.obj` | `895842` | `3256AAFB7AA302363185A646F8076DC92E793C72D16702EA485D7838EF72A733` | `2026-08-21T14:48:15.5947822Z` |
| `client/OddsWell/Binaries/Win64/OddsWell.exe` | `341429248` | `FB214D41A75E86C99F8ACD68632A389D535FAFCF71ACFDED5D48E53F5A75E3C7` | `2026-08-21T14:49:18.7641919Z` |

Repository HEAD remained `43a0af690ad8dd92a1f58e7d97b1c73a368e0532`; tracked repository and source mutation counts were `0`. Watched process residue, unreadable-path ambiguity, watched TCP/UDP port residue, and netstat parse failures were all `0`.

## Credits and boundaries

- `single_action_game_build_credit=1`
- `exact_sundale_game_source_compile_credit=1`
- package build/custody, package launch, game launch, runtime activation, policy application/readback, renderer, visible window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits: `0`
- product result: `NOT_MEASURED`

The build proves only the exact non-detoured game-target source compilation and linked output. It does not create or validate a package, launch a game, observe Candidate runtime activation or policy fields, measure product behavior, or demonstrate compatibility/readiness. No Defender-clean claim is made. Evidence and generated outputs remain preserved and uncommitted.

## Boundary and stop

Phase 1L remains incomplete. Phase 6/6 requires a separate owner-approved gate.

FRESH BATCH PHASE 5/6 CLOSED — NO AUTOMATIC PHASE 6
