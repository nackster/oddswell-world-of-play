---
title: Phase 1L.5w Packaged Candidate B Policy Application and Native Renderer Evidence
type: report
status: Complete locally - packaged policy evidence limited
date: 2026-08-18
---

# Phase 1L.5w Packaged Candidate B Policy Application and Native Renderer Evidence

## Result

`COMPLETE LOCALLY — PACKAGED_POLICY_EVIDENCE_LIMITED; TIMEOUT BEFORE CANDIDATE MARKERS; PRODUCT NOT MEASURED; FRESH BATCH PHASE 5/6`

Phase 1L.5w consumed one approved direct packaged-game attempt. The Sundale map loaded and a visible window handle was observed, but the process did not exit naturally and emitted none of the required Candidate B policy START, FIELD, or RESULT markers before the `120 s` cap. The attempt is evidence-limited; it is not a policy result, renderer result, product measurement, or product/source defect demonstration.

## Prior package custody preserved

Phase 1L.5v closed at commit `7fdcba4cfd4b10a9d28758eb6d14f7c11da9b664` with independently verified exactly two canonical Project upserts and counted Phase `4/6`. Its prior `development_package_build_credit=1` and `package_custody_credit=1` remain unchanged. Phase 1L.5u's earlier `package_transcript_contract_credit=1` also remains prior credit only. None of those credits becomes packaged policy, renderer, window, performance, compatibility, or readiness proof.

## Launch custody

| Field | Evidence |
| --- | --- |
| outcome | `PACKAGED_POLICY_EVIDENCE_LIMITED` |
| qualifier | `TIMEOUT_BEFORE_CANDIDATE_MARKERS_AND_WRAPPER_EXIT_CUSTODY_DEFECT` |
| attempt | `1` consumed; attempt number `1`; retry allowed `false` |
| executable | `C:\tmp\OddsWellPhase1L5v\PackageFinal\Windows\OddsWell\Binaries\Win64\OddsWell.exe` |
| executable identity | `341,427,712` bytes; SHA-256 `8E23CD903D0605A60DF36EF5FC05DB3137937A9167EA5A3A98F456189EBB1B89` |
| arguments | `10`; raw `184` characters / `184` UTF-8 bytes; SHA-256 `48C84F9E70186736B9FB1BB1AAAED26417272F4E2946E5A78B872C75C52D2BE6` |
| retained PID / start | `36604`; `2026-08-18T20:53:19.8969870Z` |
| timeout | limit `120 s`; observed elapsed `120.674126 s` |
| natural exit | `false` |
| timeout / exact-PID stop / drain | `true / true / true` |
| cleanup authority | `EXACT_RETAINED_PID_ONLY` |
| window observations | count `2`; MainWindowHandle `855292` |

The process was responsive during both bounded observations. A nonzero handle is not visible-client-size evidence, so the visible-window component remains `INDETERMINATE`.

## Timeout and wrapper custody defect

At the cap, only retained PID `36604` was stopped and drained. The game-process exit code observed after that forced stop is `-1`, with origin `POST_FORCED_STOP`; it is not a natural product exit code.

The wrapper intended timeout code `124`, but its literal statement was `exit124`. PowerShell treated that as `COMMAND_NOT_FOUND`, so timeout code propagation is `false` and `wrapper_terminal_exit_code=NOT_AVAILABLE`. This wrapper-custody defect is independently recorded from the forced game-process exit and does not prove a product failure. No retry occurred and no broader cleanup was performed.

## Immutable direct abslog

`C:\tmp\OddsWellPhase1L5w\Evidence\CandidateBPolicySmoke.log` was created directly by the game process through `-abslog`.

| Field | Value |
| --- | --- |
| bytes | `97,448` |
| SHA-256 | `C4BA95C1BDE495631B17AB020C4A94B8ECA55CADD42283AC6669B225E6361D0B` |
| last write UTC | `2026-08-18T20:53:23.0228379Z` |
| observation 1 | `2026-08-18T20:55:33.6625229Z`; same bytes/SHA |
| observation 2 | `2026-08-18T20:55:40.1947841Z`; same bytes/SHA |
| separation | `6.5322612 s` |
| encoding | strict UTF-8 pass; BOM `true`; NUL `0` |
| line custody | CRLF `1,011`; bare LF `2`; bare CR `0`; LF-split elements `1,014`; final line ending `CRLF` |

The log capture is complete only through the forced stop. Tool return was not evidence and AppData logs did not substitute.

## Escape-aware marker result

The parser honored the source grammar for escaped backslash, pipe, equals, carriage return, and newline. It found Candidate flag echoes `2` and Sundale map-load completion `1`, but Candidate START `0`, FIELD `0`, RESULT `0`, and RequestExit marker `0`.

Selector, child, control, runtime, policy, MATCH, MISMATCH, GAP, MISSING, AMBIGUOUS, and UNAVAILABLE counts are all `0`. `result_fields_emitted=0`; result matches, mismatches, gaps, and known-unavailable names are `NOT_AVAILABLE`. `product_result=NOT_MEASURED`.

Policy application, native renderer, and visible-window components are each `INDETERMINATE`. Fatal and security marker counts are `0`; security count `0` is not a Defender-clean claim.

## Exact-three evidence

| Evidence | Bytes | SHA-256 | Content |
| --- | ---: | --- | --- |
| `CandidateBPolicySmoke.log` | 97,448 | `C4BA95C1BDE495631B17AB020C4A94B8ECA55CADD42283AC6669B225E6361D0B` | immutable direct abslog through forced stop |
| `session_custody.tsv` | 3,613 | `8B9026C5B862F83740DBF5C89320FE1555F1DF54E7DB867D8AE3F3197782CC50` | 107 ordered rows / 107 unique keys |
| `field_ledger.tsv` | 65 | `8BC7ABF07E4DCE1928090D346F7E227B9AC2F380503630486FD8C190BAFC6F33` | header only / data rows `0` |

Exactly one authorized evidence patch created only the two TSV files. The game log, package, project source, config, maps, and repository product state were not mutated. Target process and watched TCP/UDP residue counts are `0`.

## Credits and non-inference

Phase 1L.5w packaged-product-launch, Candidate B policy-application/readback, native-renderer validation, visible-window, performance, compatibility, minimum-PC, accessibility, and readiness credits are all `0`. Product measurement scope is `NOT_MEASURED`; `product_defect_demonstrated=false`; `defender_clean_claim=false`.

Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. This attempt provides no representative product run, policy application, renderer validation, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, or readiness proof.

## Boundary and next gate

Evidence remains preserved. No retry, postflight cleanup, source/package repair, package launch, or additional game launch is authorized. Phase 1L exit remains incomplete; Phase 1M, roadmap Phase 2, Version 1, and release or beta-exit approval remain unauthorized.

Phase `5/6` closes only through the local commit containing this report and later exactly two canonical Project upserts. Tasks remain unchanged, Cursor is `0`, and `next_phase_authorized=false`; no automatic Phase 6 is authorized.
