---
title: Phase 1L.5ab Packaged Candidate B Activation-Diagnostic Marker Evidence
type: report
status: Complete locally - activation evidence limited
date: 2026-08-20
---

# Phase 1L.5ab — Packaged Candidate B Activation-Diagnostic Marker Evidence

## Result

`COMPLETE LOCALLY — ACTIVATION_EVIDENCE_LIMITED; TIMEOUT AFTER WORLD_BOUND BEFORE BEGIN_PLAY MARKER; PRODUCT NOT MEASURED; OWNER-REQUESTED SINGLE PHASE CLOSED`

One owner-requested packaged attempt reached its `90 s` cap after the FLAG_ACCEPTED and WORLD_BOUND diagnostics but before any BEGIN_PLAY marker. The revalidated retained PID alone was stopped and drained. This is bounded activation evidence, not a completed product run, a product-defect finding, policy-application proof, route proof, or readiness evidence.

## Prior phase truth

Phase 1L.5aa closed at commit `10b6c66f97691c150f5cfd581c9575500f5a65f5` with independently verified exactly two canonical Project upserts and counted Phase `3/6` in its prior batch. The current heartbeat new-phase count remains `0`. Phase 1L.5aa diagnostic-marker package-build and package-custody credits remain prior credits only.

## Attempt custody

| Field | Evidence |
| --- | --- |
| outcome | `ACTIVATION_EVIDENCE_LIMITED` |
| qualifier | `TIMEOUT_AFTER_WORLD_BOUND_BEFORE_BEGIN_PLAY_MARKER` |
| attempt consumed / valid | `true / true` |
| attempt / retry | `1 / false` |
| executable | `C:\tmp\OddsWellPhase1L5aa\PackageFinal\Windows\OddsWell\Binaries\Win64\OddsWell.exe` |
| executable identity | `341,428,224` bytes / SHA-256 `A668E6334794A60B18D895276BB1B8B23DD034022CDFD9AB77AC15B9D5321226` |
| arguments | exact `9`; `215` characters / UTF-8 bytes; SHA-256 `0AF0B6165E4DDAA42B713E56480329B13B62AD1CD1FCEFD4CFBBEECBDDBF5C21` |
| retained PID / start | `57476` / `2026-08-20T14:13:45.8062988Z` |
| cap / elapsed | `90 s / 90.4752791 s` |
| natural exit / timeout | `false / true` |
| exact-PID stop / drain | `true / true` |
| exit / origin | `-1 / POST_FORCED_STOP` |
| cleanup scope | `EXACT_RETAINED_PID_ONLY` |

No retry, broad cleanup, player input, route flag, Defender action, or package mutation occurred.

## Exact-three evidence

| Evidence file | Bytes | SHA-256 |
| --- | ---: | --- |
| `CandidateBActivation.log` | `97,749` | `0CA9B4CC8BAB356480229483772FB70080B6210D73EA7D0C0C1C48FAD5FFB4D5` |
| `session_custody.tsv` | `2,464` | `807D2D89A578DAE653A0E2B37AB240A108D1C42CC645E8C513E543F18A399FC1` |
| `marker_ledger.tsv` | `336` | `CC4AF7B769A789A945C8C242BA727C3161EA495A55CF86CC967F9DB762F18E3D` |

The direct process-created log remained unchanged across two identical observations `21.8353506 s` apart. It is strict UTF-8 with BOM, NUL count `0`, CRLF count `1,013`, bare LF count `2`, bare CR count `0`, split-LF element count `1,016`, and final CRLF. Session custody replays as `74` unique ordered rows; the marker ledger replays as seven unique ordered rows. The one authorized evidence patch created only the two TSVs.

## Activation boundary

| Ordinal | Stage | Expected | Actual | First line | Status |
| ---: | --- | ---: | ---: | --- | --- |
| 1 | `FLAG_ACCEPTED` | `1` | `1` | `843` | `MATCH` |
| 2 | `WORLD_BOUND` | `1` | `1` | `892` | `MATCH` |
| 3 | `BEGIN_PLAY` | `1` | `0` | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 4 | `NEXT_TICK_DISPATCHED` | `1` | `0` | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 5 | `START` | `1` | `0` | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 6 | `FIELD` | `184` | `0` | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 7 | `RESULT` | `1` | `0` | `NOT_AVAILABLE` | `NOT_OBSERVED` |

Candidate-argument echoes count `2`, Sundale map-load completion counts `1`, and RequestExit counts `0`. The first absent diagnostic milestone is BEGIN_PLAY after observed WORLD_BOUND. Because no finer runtime marker exists between those observations, this does not localize a causal failure or demonstrate a product defect. Activation and policy-application components remain `INDETERMINATE`; route is `NOT_RUN`; product is `NOT_MEASURED`.

## Credits and boundaries

- `activation_credit=0`, `packaged_candidate_source_execution_credit=0`, `policy_application_credit=0`, and `route_credit=0`.
- Native-renderer, visible-window, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain maturity, and readiness credits remain `0`.
- Prior Phase 1L.5aa package-build and package-custody credits remain prior only; this phase does not add to them.
- Candidate B remains owner-selected, provisional, and unvalidated; Phase 1L exit remains incomplete.
- Fatal and security marker counts are `0`; this is not a Defender-clean claim.
- PackageFinal remains `50` files / `1,052,111,532` bytes, package Saved-segment files remain `0`, Profile files are `5`, and target-process plus retained-PID TCP/UDP residue counts are `0/0/0`.
- The repository remained clean at `10b6c66f97691c150f5cfd581c9575500f5a65f5`; the package executable and marker-bearing sources retained their frozen identities.
- Start-of-phase task custody was shared `33`, external PermitWatchdog `28`, OddsWell relation `1` unchanged, OddsWell new `0`, and Cursor `0`. No task mutation occurred, and later live drift was not chased.
- No retry, source/config/package/profile mutation, follow-on phase, product claim, beta-exit, or readiness authority follows from this closure.

## Boundary and stop

OWNER-REQUESTED SINGLE PHASE CLOSED — NO AUTOMATIC FOLLOW-ON
