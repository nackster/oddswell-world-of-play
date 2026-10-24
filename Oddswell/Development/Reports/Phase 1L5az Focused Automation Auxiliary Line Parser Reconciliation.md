# Phase 1L.5az Focused Automation Auxiliary-Line Parser Reconciliation

## Status

`COMPLETE LOCALLY — FOCUSED_AUTOMATION_PARSER_RECONCILED; CANONICAL CATEGORY AND MESSAGE-PREFIX MALFORMED SCOPE SELECTED; AUTOMATION NOT RERUN; PRODUCT NOT MEASURED; NEW NIGHTLY BATCH PHASE 6/6; SIX-PHASE BATCH CLOSED`

Phase 1L.5az is the selected `FOCUSED_AUTOMATION_AUXILIARY_LINE_PARSER_RECONCILIATION`, a docs-only, read-only installed-source reconciliation. It resolves the prospective malformed-marker scope that treated four native auxiliary automation lines as malformed while preserving Phase 1L.5ay's frozen LIMITED verdict and credits `0`.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `CANONICAL_CATEGORY_AND_MESSAGE_PREFIX_MALFORMED_SCOPE` | `SELECTED` | `RECOMMENDED` | It limits malformed accounting to source-owned canonical emitters while retaining all fail-closed checks. |
| B | `RETROACTIVE_FOCUSED_AUTOMATION_CREDIT` | `NOT_SELECTED` | `REJECTED` | Reconciliation cannot rescore the committed Phase 1L.5ay evidence. |
| C | `RERUN_OR_IGNORE_ALL_AUXILIARY_ROWS` | `NOT_SELECTED` | `REJECTED` | A rerun is unnecessary and blanket ignoring would weaken evidence custody. |

## Frozen inputs

Baseline HEAD is `ec2c9a85f6020502f4b0d506fb6b0b8512ebd787`, clean with index `0`. Phase 1L.5ay remains `FOCUSED_AUTOMATION_EVIDENCE_LIMITED` / `STRUCTURED_MARKER_MALFORMED_COUNT_NONZERO`, with focused automation and predicate credits `0`. Its report is `Oddswell/Development/Reports/Phase 1L5ay Candidate B Exact World Package Predicate Focused Native Automation.md`, `5,286` bytes, SHA `3577FEE69FF495E6BA7168BCAACC6DD683CB396170EB56604A4C0005C4B86527`, blob `aeaee5b021aaebf4cf9acb4a074fd8f76a0d5b75`.

| Installed UE5.8 source | Bytes | SHA-256 |
| --- | ---: | --- |
| `AutomationController/Private/AutomationCommandline.cpp` | 29,813 | `A040ADEE46CDECDCBE5C8148C6203211FD59559EA0A73CE748D5725399B899B3` |
| `AutomationController/Private/AutomationControllerManager.cpp` | 64,122 | `FA7C0485912A80E9B47E26D5ED066D7A300008DB59FAD4C214280D807ABA54B1` |
| `Launch/Private/LaunchEngineLoop.cpp` | 244,123 | `C45991A136185130235E507C9BB9EC6E926D4F2006A384B2F61E7E6227742C6F` |

## Exact reconciliation table

| row | subject | authority/evidence | status |
| ---: | --- | --- | --- |
| 1 | `PHASE5_COMMITTED_FACTS` | The committed report records natural exit `0`, five canonical success/lifecycle counts `1`, failure/fatal/security `0`, exact index Success `1`, broad malformed rows `1800/1832/1845/1846`, and Phase 1L.5ay LIMITED with credits `0`. | `SOURCE_CONFIRMED` |
| 2 | `RUNTESTS_QUEUED_IS_NATIVE_AUXILIARY` | `AutomationCommandline.cpp` lines 623–628 own `Automation: RunTests='%s' Queued.` before queueing command-line tests. | `SOURCE_CONFIRMED` |
| 3 | `EXACT_PATH_DISPLAY_IS_NATIVE_ENUMERATION` | `AutomationCommandline.cpp` lines 359–365 emit Found, then separately enumerate each exact path with a tab prefix. | `SOURCE_CONFIRMED` |
| 4 | `BEGIN_EVENTS_IS_NATIVE_BRACKET` | `AutomationControllerManager.cpp` lines 41–46, 60–63, and 1682–1684 own `BeginEvents: %s`, distinct from canonical Started/Completed rows. | `SOURCE_CONFIRMED` |
| 5 | `END_EVENTS_IS_NATIVE_BRACKET` | `AutomationControllerManager.cpp` lines 41–46, 65–68, and 1712–1714 own `EndEvents: %s`, distinct from canonical rows. | `SOURCE_CONFIRMED` |
| 6 | `COMMANDLINE_CANONICAL_EMITTERS` | `AutomationCommandline.cpp` lines 119–126, 356–360, and 500–506 own Queue Empty, Found, and TEST COMPLETE prefixes. | `SOURCE_CONFIRMED` |
| 7 | `CONTROLLER_CANONICAL_EMITTERS` | `AutomationControllerManager.cpp` lines 41–57 own Test Started and Test Completed prefixes; bracket formats are separate. | `SOURCE_CONFIRMED` |
| 8 | `TESTEXIT_CANONICAL_EMITTER` | `LaunchEngineLoop.cpp` lines 5589–5594 own `**** TestExit: ` before requesting exit. | `SOURCE_CONFIRMED` |
| 9 | `MALFORMED_SCOPE` | Eligibility is restricted to the six exact category/message-prefix pairs after the existing prefix parser and argv exclusions; only an eligible row that fails its applicable full regex increments malformed. | `SOURCE_CONFIRMED` |
| 10 | `FUTURE_FAIL_CLOSED_SEPARATION` | Canonical counters and index stay unchanged; canonical gaps remain LIMITED, explicit failure remains FAIL, and auxiliary rows cannot satisfy canonical counts or hide fatal/security evidence. No Phase 1L.5ay rescore occurs. | `SOURCE_CONFIRMED` |

All ten rows are `SOURCE_CONFIRMED`; the outcome is `FOCUSED_AUTOMATION_PARSER_RECONCILED` with qualifier `NONE`.

## Prospective parser contract

After the inherited exact structured UE-prefix parse and raw launch/argv echo exclusions, only these case-sensitive ordinal category/message-prefix pairs are eligible:

1. `LogAutomationCommandLine` + `Found `
2. `LogAutomationCommandLine` + `...Automation Test Queue Empty `
3. `LogAutomationCommandLine` + `**** TEST COMPLETE. EXIT CODE: `
4. `LogAutomationController` + `Test Started. `
5. `LogAutomationController` + `Test Completed. `
6. `LogExit` + `**** TestExit: `

Each unique eligible physical line increments malformed once only when it fails its existing applicable full canonical regex. The unstructured queued row, exact-path-only enumeration, BeginEvents, and EndEvents are ineligible auxiliary custody, not accepted canonical markers. No unescape or rewrite occurs. Canonical counters and the structured index remain mandatory; missing or malformed canonical evidence is LIMITED, explicit test failure is FAIL, and auxiliary lines cannot satisfy canonical counts or hide fatal/security evidence.

## Credits, ledger, and boundary

`focused_automation_parser_reconciliation_credit=1`. `candidate_world_package_predicate_focused_automation_credit=0` and `focused_native_automation_credit=0` remain permanent for Phase 1L.5ay. Every current build, automation execution, package, launch, runtime, activation, policy, renderer, visible-client, route, gameplay, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, validation, and readiness credit is `0`. Product is `NOT_MEASURED`; Candidate B remains provisional/unvalidated. There is no source, product, or security defect and no Defender-clean claim.

Phase 1L.5ay is truth-repaired to full commit `ec2c9a85f6020502f4b0d506fb6b0b8512ebd787`, independently verified exactly two canonical Project upserts and count `5/6`. The six-commit ledger is Phase `1/6` `00c90144ffd8c71ba7bbb521761e9112c72bffb3`; `2/6` `e34781bd92507ec8eed2a7d38dc3c7ed5256d368`; `3/6` `bf5c64c011e14ac6f864312fe95fa4705d76a2d6`; `4/6` `accd2f454ede4baa55c511963aa2ee4bca7114a4`; `5/6` `ec2c9a85f6020502f4b0d506fb6b0b8512ebd787`; and `6/6` pending this local documentation commit. No Tasks or Cursor artifact is created.

NO SEVENTH PHASE — SIX-PHASE BATCH STOPPED.
