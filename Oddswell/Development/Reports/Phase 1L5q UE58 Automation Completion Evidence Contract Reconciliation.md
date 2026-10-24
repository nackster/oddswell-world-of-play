---
title: Phase 1L.5q UE5.8 Automation Completion-Evidence Contract Reconciliation
type: report
status: Complete locally - future no-quit automation contract selected
date: 2026-08-16
---

# Phase 1L.5q UE5.8 Automation Completion-Evidence Contract Reconciliation

## Result

`COMPLETE LOCALLY — UE5.8 AUTOMATION COMPLETION CONTRACT RECONCILED; FUTURE NO-QUIT COMMAND SELECTED; AUTOMATION NOT RERUN; PRODUCT NOT MEASURED`

Phase 1L.5q reconciles the future focused-automation completion contract against installed UE5.8 source. It selects a no-`;Quit` command shape for a separately authorized future attempt. No source, test, build, package, game, transient evidence, Defender, or product operation occurred. Phase 1L.5p remains `BUILD_PASS_AUTOMATION_EVIDENCE_LIMITED`; it is not retroactively passed or credited.

## Authoritative source custody

| Source | Installed SHA-256 | Relevant ownership |
| --- | --- | --- |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Developer\AutomationController\Private\AutomationCommandline.cpp` | `A040ADEE46CDECDCBE5C8148C6203211FD59559EA0A73CE748D5725399B899B3` | `IsTestingComplete` / emitted Queue Empty lines `117–126`; Found lines `344–359`; completion state lines `421–430`; command, Quit, TEST COMPLETE, RequestExit, and final completion check lines `474–519`; parser/queues lines `610–743` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Developer\AutomationController\Private\AutomationControllerManager.cpp` | `FA7C0485912A80E9B47E26D5ED066D7A300008DB59FAD4C214280D807ABA54B1` | Started/Completed formats and emitters from lines `42–46`; result counters `145–180`; JSON write `725–760`; report export `1097–1181` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Developer\AutomationController\Private\AutomationControllerManager.h` | `1C54688ECC9D280FD5A2D1251F85477934E086D22872EE36BF261C58E35FB91D` | serialized row fields `22–79`; summary counters and Tests collection `113–170` |
| `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Launch\Private\LaunchEngineLoop.cpp` | `C45991A136185130235E507C9BB9EC6E926D4F2006A384B2F61E7E6227742C6F` | `FOutputDeviceTestExit` lines `397–425`; setup lines `1928–1929`; later phrase-driven exit lines `5590–5593` |

All four installed files rehashed to the accepted identities before this report was written.

## Corrected ownership matrix

| Evidence | UE5.8 owner and condition | Contract meaning |
| --- | --- | --- |
| `Found 1 automation tests based on ...` | `AutomationCommandline.cpp` emits Found after filtering the requested tests | require exact literal count `1` |
| `Test Started...` / `Test Completed. Result={Success}...` | `AutomationControllerManager.cpp` owns these controller lines | require each exact full path count `1` |
| report summary and sole test row | `AutomationControllerManager.cpp` updates counters and writes/exports JSON; `AutomationControllerManager.h` defines full path, state, errors, warnings, summary counters, and Tests | require exact successful one-row index |
| `...Automation Test Queue Empty 1 tests performed.` | `AutomationCommandline.cpp::IsTestingComplete` emits only when controller is not Running, test state is Complete, and command queue count is `0` | required emitted count `1`; this phrase can miss if exit is requested before the final completion check |
| `**** TEST COMPLETE. EXIT CODE: 0 ****` | `AutomationCommandline.cpp` emits inside the explicit Quit/SoftQuit branch immediately before RequestExit and before setting the state Complete | expected count `0` for selected no-`;Quit` future contract |
| command-line / `-TestExit` echoes | launch text only | never count as emitted queue-empty evidence |
| `**** TestExit: Automation Test Queue Empty ****` | `LaunchEngineLoop.cpp` ignores the actual `-testexit=` command-line echo, recognizes a later emitted matching phrase, and then emits this marker before requesting exit | require exact count `1` |

The source establishes conditions and ownership, not inevitability. Removing `;Quit` can allow the final `IsTestingComplete` queue-empty emission and later TestExit marker to occur; it does not make either marker always present, impossible to miss, or evidence of a source defect when absent.

## Phase 1L.5p reconciliation

The retained Phase 1L.5p truth remains unchanged:

- build attempt `1` passed;
- focused automation process exited `0`;
- exact Found / Started / Completed Success counts were `1 / 1 / 1`;
- required emitted Queue Empty count was `0`;
- command-line / `-TestExit` Queue Empty echoes were `2` and were custody only;
- separate TEST COMPLETE exit-0 count was `1`;
- report index was one exact successful row with errors `0` and warnings `0`;
- Candidate markers, fatal markers, and security markers were `0`.

Therefore Phase 1L.5p remains automation-evidence-limited. This reconciliation does not convert those observations into a Phase 4 pass, add build/compile/automation credits, infer a test failure, or infer a source defect.

## Exactly three future options

| Option | Enum | Disposition | Contract |
| --- | --- | --- | --- |
| A | `AUTOMATION_RUN_TESTS_PLUS_TESTEXIT_NO_QUIT` | `SELECTED/RECOMMENDED` | future ExecCmds value exactly `Automation RunTests OddsWell.CandidateBPolicySmoke.CommandLinePredicate`, with no `;Quit`; retain `-TestExit=Automation Test Queue Empty` |
| B | `QUIT_PLUS_TEST_COMPLETE_AND_INDEX` | `NOT_SELECTED` | retain explicit Quit and use TEST COMPLETE plus index rather than require emitted Queue Empty |
| C | `REQUIRE_QUIT_TEST_COMPLETE_AND_QUEUEEMPTY` | `NOT_SELECTED` | require both Quit-owned TEST COMPLETE and emitted Queue Empty despite the observed ordering risk |

Only Option A is selected. Selection is documentation custody for a future separately authorized attempt, not launch authority.

## Future exact predicates

A future focused attempt can pass only when all of these agree:

1. direct EditorCmd exit is `0`;
2. exact Found count is `1`;
3. exact Started full-path count is `1`;
4. exact Completed `Result={Success}` full-path count is `1`;
5. emitted `...Automation Test Queue Empty 1 tests performed.` count is `1`;
6. `**** TestExit: Automation Test Queue Empty ****` count is `1`;
7. `**** TEST COMPLETE. EXIT CODE: 0 ****` count is `0`;
8. index has `Succeeded=1`, `SucceededWithWarnings=0`, `Failed=0`, `NotRun=0`, `InProcess=0`, `Tests=1`, and one row with the exact full path, `State=Success`, `Errors=0`, and `Warnings=0`;
9. Candidate START, FIELD, and RESULT marker counts are each `0`;
10. fatal and security marker counts are `0`;
11. exact process drain is complete.

Security evidence takes precedence. An exact identified failure is fail. Missing, ambiguous, or conflicting required evidence is limited. Only complete exact agreement is pass.

## Credits and boundary

`completion_contract_reconciliation_credit=1`

Prior Phase 1L.5n source-authored credit remains `1`. Phase 1L.5q build, Candidate-compile, automation-run, package, product, policy-application, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, and readiness credits are `0`. Phase 1L.5p credits remain `0`; Candidate B remains provisional/unvalidated and product remains `NOT_MEASURED`. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived.

Phase 1L.5p closed at commit `1a4a580d93db48eb03986f276ca6af85bd190bc2` with independently verified exactly two Notion upserts. Phase `5/6` closes only after this exact-five documentation commit and later exactly two canonical Project upserts. No automation rerun, package, game, Candidate runtime, or Phase 6 is authorized here.
