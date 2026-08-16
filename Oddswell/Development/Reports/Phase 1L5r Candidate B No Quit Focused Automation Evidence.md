---
title: Phase 1L.5r Candidate B No-Quit Focused Automation Evidence
type: report
status: Complete locally - focused automation passed
date: 2026-08-16
---

# Phase 1L.5r Candidate B No-Quit Focused Automation Evidence

## Result

`COMPLETE LOCALLY — FOCUSED_AUTOMATION_PASS; PRODUCT NOT MEASURED; SIX-PHASE BATCH CLOSED`

One direct signed UnrealEditor-Cmd attempt exercised the unchanged focused command-line predicate with the Phase 1L.5q no-`;Quit` contract. The process exited naturally with code `0`; every required emitted-log and report-index predicate agreed. The Candidate opt-in flag was absent, so the Candidate policy-application path did not run and product behavior was not measured. No retry, timeout stop, build, package, packaged game, Defender query, or source change occurred.

## Frozen preflight

Repository HEAD was clean at `610fe61c7a608c0894db73bdab915ed321f851fc`. Phase 1L.5q is closed at that commit with independently verified exactly two Notion upserts. The fixed evidence root `C:\tmp\OddsWellPhase1L5r` was absent and created once without force. The signed Epic UnrealEditor-Cmd executable was `512,952` bytes, SHA-256 `327209AA83F741C91E32E3B61B3A6744B18CF0ADAEFD89586E62F2C743F2394B`, with a `Valid` Epic signature. Target processes and watched ports were clear.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `CandidateBPolicySmoke.cpp` | `31,204` | `EA600104810B947958DCF0F978ED6B8EB7DBF2D177B72169FA51ABF8E8ADAAA5` |
| `CandidateBPolicySmoke.h` | `231` | `69DF7B6E9805B272A83B5C979FDC56FB09EE6403C12DA76067D63837958884FB` |
| `OddsWell.cpp` | `1,470` | `D39F1888ECA930BBFC34CAA96D14CC51A1CD70F9BACAB55EF4918D4C4313365A` |
| `OddsWell.Build.cs` | `357` | `AD9081D5745E5CE16D41E282A31D74C5FE5E451E6073A4A4A78D7A71E942B692` |
| `OddsWell.uproject` | `190` | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18` |
| `UnrealEditor-OddsWell.dll` | `2,591,232` | `F89FA386CCE4639122C638775A826DF1DD83F75C95BD9D33AB404937125B9E3C` |

The module DLL last-write remained `2026-08-16T19:02:24.0838434Z`. Its unchanged bytes and all five unchanged source/project identities prove that this phase reused the already-built module; they do not add a build credit.

## Exact focused attempt

Signed Epic UnrealEditor-Cmd was invoked directly once. Its exact ordered eleven argument tokens were:

1. `C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
2. `-unattended`
3. `-nop4`
4. `-NullRHI`
5. `-NoSplash`
6. `-NoSound`
7. `-UserDir=C:\tmp\OddsWellPhase1L5r\User`
8. `-abslog=C:\tmp\OddsWellPhase1L5r\automation.log`
9. `-ReportExportPath=C:\tmp\OddsWellPhase1L5r\AutomationReport`
10. `-ExecCmds=Automation RunTests OddsWell.CandidateBPolicySmoke.CommandLinePredicate`
11. `-TestExit=Automation Test Queue Empty`

Token 10 contained no `;Quit`. The exact Candidate opt-in `-CandidateBPolicySmokeQa` was absent. The attempt exited naturally with code `0` after `15.9104682 s`; timeout, exact-PID stop, and retry counts were `0`.

## Exact emitted-log proof

| Predicate | Exact observed count |
| --- | ---: |
| Found one exact test | `1` |
| Started exact full test path | `1` |
| Completed `Result={Success}` exact full test path | `1` |
| emitted `...Automation Test Queue Empty 1 tests performed.` | `1` |
| emitted `**** TestExit: Automation Test Queue Empty ****` | `1` |
| `**** TEST COMPLETE. EXIT CODE:` | `0` |
| Candidate START / FIELD / RESULT markers | `0 / 0 / 0` |
| fatal markers | `0` |
| security markers, Defender text, virus/threat text, or `0x800700E1` | `0` |

Command-line and `-TestExit` echoes were retained only as argument custody and were not counted as emitted completion proof. The absence of Candidate markers is required because the opt-in flag was absent.

## Report-index proof

`AutomationReport/index.json` recorded `Succeeded=1`, `SucceededWithWarnings=0`, `Failed=0`, `NotRun=0`, `InProcess=0`, and `Tests=1`. Its sole row had `fullTestPath=OddsWell.CandidateBPolicySmoke.CommandLinePredicate`, `state=Success`, `errors=0`, and `warnings=0`.

| Artifact | Bytes | Last write UTC | SHA-256 |
| --- | ---: | --- | --- |
| `C:\tmp\OddsWellPhase1L5r\automation.log` | `253,879` | `2026-08-16T19:49:18.9829573Z` | `211FCC801D52A1546E5DE2F763CDE9F5AC9BC8F796D3CC13BBC06B84064EEB33` |
| `C:\tmp\OddsWellPhase1L5r\AutomationReport\index.json` | `1,114` | `2026-08-16T19:49:18.9758439Z` | `308AA53103255F578BCD25EE7D77249A9E868EB95FDE3EB8020659E922933F4A` |

The log and index agree completely. Under the Phase 1L.5q precedence, security evidence would take priority, an exact failure would fail, and a missing or conflicting required field would limit the result. None occurred, so the focused attempt is `FOCUSED_AUTOMATION_PASS`.

## Credits and nonclaims

- `focused_automation_credit=1`
- `unchanged_module_test_execution_credit=1`
- prior `completion_contract_reconciliation_credit=1` remains unchanged
- prior `source_authored_credit=1` remains unchanged
- Phase 1L.5p build, Candidate-compile, and focused-automation credits remain `0`
- current-phase build, Candidate compile, package, product, policy application, renderer/native-TSR, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, and readiness credits are `0`

Product remains `NOT_MEASURED`; Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. This NullRHI predicate test did not apply Candidate settings, execute the route, prove renderer policy, measure performance, validate the minimum-PC target, or establish compatibility/readiness. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived. Brains remain frozen; no training, learning, retraining, or brain-readiness claim is made.

The evidence root is preserved. Repository and client source/project bytes remained unchanged and clean. UnrealEditor-Cmd, UnrealEditor, OddsWell, UnrealBuildTool, and dotnet process residues were `0`; watched TCP and UDP ports were `0`.

## Six-phase closeout

`FRESH SIX-PHASE BATCH — 6/6 COUNTED AND CLOSED LOCALLY; NO PUSH.`

`Phase 1/6 d4f4e010; Phase 2/6 a5d6adb1; Phase 3/6 62525eff; Phase 4/6 1a4a580d; Phase 5/6 610fe61c; Phase 6/6 the local commit containing this report.`

Full committed ancestry through Phase 5 is `d4f4e0100545f663acdaf5aff3de051a56c67cbc`, `a5d6adb1f79acaa63ee4933fed9e699b5b7e4c09`, `62525eff6e4196b2a01c1caa80c69a5d57ea1a57`, `1a4a580d93db48eb03986f276ca6af85bd190bc2`, and `610fe61c7a608c0894db73bdab915ed321f851fc`. Phase 6 is self-referentially identified by the local commit containing this report; its full identity belongs in postcommit custody rather than in its own filesystem bytes.

The owner-approved .NET `10.0.11` prerequisite is noncounting and is not a seventh phase.

Final audit: exact-five documentation custody; exact-two canonical Project upserts; Tasks unchanged; Cursor 0; repository clean; local branch not pushed; canvas 22/0/22; frozen source, DLL, and tool identities reconciled; target processes and watched TCP/UDP ports 0; product NOT MEASURED; all package, cook, route, gameplay, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, and readiness credits remain 0.

After the local documentation commit passes independent postcommit custody, the only planned canonical documentation writes are exactly two Project upserts headed `Phase 1L.5r — Candidate B No-Quit Focused Automation Evidence` and `Phase 1L.5r Evidence — FOCUSED_AUTOMATION_PASS`. They remain pending until separately authorized.

`NO SEVENTH PHASE — SIX-PHASE BATCH STOPPED.`

This exact-five documentation closure may later receive exactly two canonical Project upserts under separate authorization. It does not authorize another phase, launch, package, game run, source change, product validation, or release decision.
