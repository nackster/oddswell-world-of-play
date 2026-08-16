---
title: Phase 1L.5p Candidate B Native Build and Focused Contract Automation After Runtime Alignment
type: report
status: Complete locally - build passed, automation evidence limited
date: 2026-08-16
---

# Phase 1L.5p Candidate B Native Build and Focused Contract Automation After Runtime Alignment

## Result

`COMPLETE LOCALLY — BUILD_PASS_AUTOMATION_EVIDENCE_LIMITED (REQUIRED EMITTED QUEUE-EMPTY PREDICATE ABSENT); PRODUCT NOT_MEASURED; NO RERUN`

After the separately authorized .NET `10.0.11` runtime alignment, Phase 1L.5p consumed exactly one native Editor build attempt and, because that build passed with an advanced module DLL, exactly one focused automation attempt. The build passed. The focused test completed with `Success` and the report index agreed, but the required emitted queue-empty predicate was absent, so automation evidence is limited. No package or game was launched, the Candidate policy flag was absent, and no policy application or product behavior was measured. No rerun is authorized.

## Frozen preflight

Repository HEAD was clean at `62525eff6e4196b2a01c1caa80c69a5d57ea1a57`. Phase 1L.5o is closed at that commit with independently verified exactly two Notion upserts. The fixed root `C:\tmp\OddsWellPhase1L5p` was absent and created once without force. Epic signatures for UnrealBuildTool and UnrealEditor-Cmd were `Valid`; target processes and watched ports were clear.

| Input | SHA-256 |
| --- | --- |
| `CandidateBPolicySmoke.cpp` | `EA600104810B947958DCF0F978ED6B8EB7DBF2D177B72169FA51ABF8E8ADAAA5` |
| `CandidateBPolicySmoke.h` | `69DF7B6E9805B272A83B5C979FDC56FB09EE6403C12DA76067D63837958884FB` |
| `OddsWell.cpp` | `D39F1888ECA930BBFC34CAA96D14CC51A1CD70F9BACAB55EF4918D4C4313365A` |
| `OddsWell.Build.cs` | `AD9081D5745E5CE16D41E282A31D74C5FE5E451E6073A4A4A78D7A71E942B692` |
| `OddsWell.uproject` | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18` |

The prebuild `UnrealEditor-OddsWell.dll` was `2,548,224` bytes, SHA-256 `39DD72185771951C77BEDAD0959025AC0E6B936CB4BC2F068997DD30407CF9AA`, and last-written `2026-08-12T02:27:33Z`.

## Native build attempt

The signed Epic UnrealBuildTool executable was invoked directly once, without UAT, wrapper, helper, retry, or repair. Its exact ordered eight argument tokens were:

1. `OddsWellEditor`
2. `Win64`
3. `Development`
4. `-Project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
5. `-WaitMutex`
6. `-NoHotReloadFromIDE`
7. `-NoEngineChanges`
8. `-Log=C:\tmp\OddsWellPhase1L5p\build.log`

| Field | Exact result |
| --- | --- |
| build attempt | `1` |
| exit | `0` |
| UBT-reported elapsed | `89.81 s` |
| UBT result | `Succeeded` |
| actions | `20/20` completed |
| Candidate source compile | `[1/20] Compile [x64] CandidateBPolicySmoke.cpp` |
| module link | `[19/20] Link [x64] UnrealEditor-OddsWell.dll` |
| engine-change refusal / `FailedDueToEngineChange` | `0` |
| compiler, linker, fatal, or security failure | `0` |
| build log | `20,503` bytes; SHA-256 `77C61FDFA55A1AF89E28CC4E4554CFDD852BCD950AB12395DCB39840025A2578` |

Unreal Build Accelerator reported low-memory compile-process restarts during the attempt, but all actions ultimately completed and UBT returned `Succeeded`. The warning that Visual Studio SDK editor integration was unavailable did not prevent project compilation or linking. Neither observation is hidden or promoted into a performance claim.

The postbuild module DLL advanced to `2,591,232` bytes, SHA-256 `F89FA386CCE4639122C638775A826DF1DD83F75C95BD9D33AB404937125B9E3C`, and last-write `2026-08-16T19:02:24.0838434Z`. This preserves truthful build output custody, but Phase 1L.5p build and Candidate-compile credits remain `0` under the limited terminal verdict.

## Focused automation attempt

Because build exit, nonempty-log, and advanced-DLL predicates all passed, signed Epic UnrealEditor-Cmd was invoked directly once. Its exact ordered eleven argument tokens were:

1. `C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
2. `-unattended`
3. `-nop4`
4. `-NullRHI`
5. `-NoSplash`
6. `-NoSound`
7. `-UserDir=C:\tmp\OddsWellPhase1L5p\User`
8. `-abslog=C:\tmp\OddsWellPhase1L5p\automation.log`
9. `-ReportExportPath=C:\tmp\OddsWellPhase1L5p\AutomationReport`
10. `-ExecCmds=Automation RunTests OddsWell.CandidateBPolicySmoke.CommandLinePredicate;Quit`
11. `-TestExit=Automation Test Queue Empty`

The exact Candidate opt-in `-CandidateBPolicySmokeQa` was absent. `elapsed_seconds=NOT_RECORDED`; no approximate elapsed value is promoted into evidence.

| Predicate | Exact count/result |
| --- | --- |
| automation attempt | `1` |
| process exit | `0` |
| exact Found literal | `1` |
| exact Started path | `1` |
| exact Completed `Result={Success}` path | `1` |
| required emitted `Automation Test Queue Empty 1 tests performed.` predicate | `0` |
| command-line / `-TestExit` Queue Empty echoes | `2`; launch custody only, not emitted-completion proof |
| `**** TEST COMPLETE. EXIT CODE: 0 ****` | `1`; separate observed terminal marker |
| Candidate START / FIELD / RESULT markers | `0` |
| fatal markers | `0` |
| security markers, Defender text, or `0x800700E1` | `0` |
| `automation.log` | `253,731` bytes; SHA-256 `E5562C08AEAD2D80BFCCE39C80B4929B2706A3603F8C1631B5BD85FF9F679479` |
| `AutomationReport/index.json` | `1,114` bytes; SHA-256 `DAC835D19A4FC25DD604D10CD8ABCF78F9625195D56285162439368E1000C7AB` |

The parsed report index agreed with the log: `Succeeded=1`, `SucceededWithWarnings=0`, `Failed=0`, `NotRun=0`, `InProcess=0`, and `Tests=1`. Its sole row had `fullTestPath=OddsWell.CandidateBPolicySmoke.CommandLinePredicate`, `state=Success`, `errors=0`, and `warnings=0`.

The exact test row succeeded, but focused automation credit remains `0` because the required emitted queue-empty predicate is absent. The two Queue Empty occurrences are only command-line and `-TestExit` echoes; they cannot substitute for the missing emitted predicate. The separate terminal marker `**** TEST COMPLETE. EXIT CODE: 0 ****` occurs once. This is an automation evidence-custody gap, not a test failure or source-defect inference. Marker count `0` is required and confirms the Candidate policy application path did not run.

## Custody and nonclaims

The evidence root is preserved. Repository source and committed files remained clean after both attempts. UnrealBuildTool, UnrealEditor, OddsWell, AutomationTool, CrashReportClient, and UBA process residues were `0`; watched TCP/UDP ports were `0`. No Defender query or action, source edit, retry, package, packaged game, Candidate policy application, route, performance sampler, or player-facing run occurred.

Prior Phase 1L.5n source-authored credit remains `1`. Phase 1L.5p build, Candidate-compile, focused-automation, policy-application, runtime-renderer proof, native-TSR proof, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, and readiness credits are `0`. Product remains `NOT_MEASURED`; Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived.

## Future gate

Phase `4/6` closes only after this exact-five documentation commit and later exactly two canonical Project upserts. A Candidate-enabled runtime policy application, package, game launch, or Phase 5 requires a separate fresh gate; none is authorized here.
