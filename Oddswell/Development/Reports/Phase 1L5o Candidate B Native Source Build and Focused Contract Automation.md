---
title: Phase 1L.5o Candidate B Native Source Build and Focused Contract Automation
type: report
status: Complete locally - build failed before UBT managed execution
date: 2026-08-16
---

# Phase 1L.5o Candidate B Native Source Build and Focused Contract Automation

## Result

`COMPLETE LOCALLY — BUILD_FAIL (MICROSOFT.NETCORE.APP 10.0.0 X64 MISSING BEFORE UBT MANAGED EXECUTION); AUTOMATION NOT_RUN; PRODUCT NOT_MEASURED`

The single authorized build attempt ended with host exit `1` after `0.028 s`. The signed Epic UnrealBuildTool executable required `Microsoft.NETCore.App` `10.0.0` for `x64`; the dotnet root `C:\Program Files\dotnet\` exposed only `Microsoft.NETCore.App` `8.0.11`. The failure occurred before UBT managed execution. UBT graph generation, compiler execution, linker execution, and Candidate B source compilation therefore did not start.

Outcome is `BUILD_FAIL`. This is not source-compile evidence, automation evidence, product evidence, performance evidence, compatibility evidence, or readiness evidence.

## Frozen attempt custody

| Field | Exact result |
| --- | --- |
| build attempt consumed | `1` |
| direct executable | `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe` |
| invocation mode | signed Epic executable, direct call operator, no wrapper, UAT, helper, or `Start-Process` |
| process exit | `1` |
| elapsed wall time | `0.028 s` |
| failure class | host runtime missing before UBT managed execution |
| required framework | `Microsoft.NETCore.App 10.0.0 (x64)` |
| dotnet root | `C:\Program Files\dotnet\` |
| observed installed framework | `Microsoft.NETCore.App 8.0.11` |
| UBT managed execution | `false` |
| graph generation | `false` |
| compiler execution | `false` |
| linker execution | `false` |
| Candidate B source compile count | `0` |
| build log | `ABSENT_BEFORE_UBT_EXECUTION`; no hash exists |
| retry allowed or performed | `false` |
| repair or framework install | `false` |
| elevation, exclusion, or security allow action | `0` |

The exact ordered eight argument tokens were:

1. `OddsWellEditor`
2. `Win64`
3. `Development`
4. `-Project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
5. `-WaitMutex`
6. `-NoHotReloadFromIDE`
7. `-NoEngineChanges`
8. `-Log=C:\tmp\OddsWellPhase1L5o\build.log`

## Conditional automation custody

The focused automation gate required build exit `0`, a nonempty build log, and a valid updated module DLL. Those predicates were false. The conditional UnrealEditor-Cmd attempt was not invoked.

| Field | Exact result |
| --- | --- |
| automation status | `NOT_RUN` |
| automation attempt consumed | `false` |
| editor or game process started | `false` |
| focused test selected, started, completed, passed, or failed | `0` each |
| Candidate policy START, FIELD, or RESULT marker observed | `0` each |
| automation report or log | absent |
| automation credit | `0` |
| package or game launch | `0` |
| product result | `NOT_MEASURED` |

The authored test and native source remain unexecuted. The pure test was not selected, started, completed, passed, or failed.

## Evidence-root and module custody

The fixed root `C:\tmp\OddsWellPhase1L5o` was absent at preflight and created once without force. After the failed host invocation it remained empty: file count `0`, subdirectory count `0`, `build.log` absent, `automation.log` absent, `AutomationReport` absent, and `User` absent. No retry or cleanup changed that evidence state.

The preexisting `client/OddsWell/Binaries/Win64/UnrealEditor-OddsWell.dll` remained the pre-attempt file: `2,548,224` bytes with last-write display `2026-08-11 21:27` local time. It was not produced or updated by Phase 1L.5o and grants no build credit.

Repository HEAD before the attempt was the clean Phase 1L.5n source commit `a5d6adb1f79acaa63ee4933fed9e699b5b7e4c09`. That phase has independently verified exactly two Notion upserts. No source, config, package, map, or committed product file changed during the attempt.

## Security and truth boundary

The console emitted no Defender or other security-product text and no `0x800700E1`. Security-block status is `false` for the observed console result, and Defender query count is `0`; this does not claim a Defender-clean machine or prove absence of external security state. No Defender command, exclusion, allow action, elevation, install, repair, dependency mutation, source edit, package operation, game launch, Candidate run, or retry occurred.

Source-authored credit remains the prior Phase 1L.5n credit `1`. Phase 1L.5o build, source-compile, automation-run, policy-application, route, product, performance, minimum-PC validation, compatibility, accessibility, and readiness credits are `0`. Candidate B remains provisional and unvalidated; Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived.

## Future gate

A future owner-authorized prerequisite gate may decide whether and how to provide the required .NET `10.0.0` runtime, followed by a separately authorized new build attempt. This report authorizes neither. No automation, package, game, or Phase 4 work may begin from this failure.
