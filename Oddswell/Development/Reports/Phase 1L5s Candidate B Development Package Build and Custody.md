---
title: Phase 1L.5s Candidate B Development Package Build and Custody
type: report
status: Complete locally - package build failed before AutomationTool managed execution
date: 2026-08-16
---

# Phase 1L.5s Candidate B Development Package Build and Custody

## Result

`COMPLETE LOCALLY — PACKAGE_BUILD_FAIL; HOST PREREQUISITE MISSING; PRODUCT NOT MEASURED; FRESH BATCH PHASE 1/6 CLOSED`

The first and only authorized direct dotnet/AutomationTool BuildCookRun attempt exited naturally with code `1` after `0.1880994 s`. The host lacked `Microsoft.WindowsDesktop.App 10.0.0 (x64)` and exposed only `Microsoft.WindowsDesktop.App 8.0.11`, so AutomationTool managed execution never began. Build, cook, stage, pak, IoStore, package, archive, and product execution counts are all `0`. This is `PACKAGE_BUILD_FAIL` with cause `HOST_PREREQUISITE_MISSING`; it does not demonstrate a product or source defect.

## Frozen preflight

Repository HEAD was clean at `ad45aca061ed87aa6bf69b7efd9f93130b7fb242`. Phase 1L.5r is closed at that commit with independently verified exactly two Notion upserts. `C:\tmp\OddsWellPhase1L5s` was absent, then the root and its `Evidence` directory were created once with two short native directory commands. Exact-path target processes and watched ports were `0`; unrelated Fortnite CrashReportClient PID `13752` was not touched.

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `CandidateBPolicySmoke.cpp` | `31,204` | `EA600104810B947958DCF0F978ED6B8EB7DBF2D177B72169FA51ABF8E8ADAAA5` |
| `CandidateBPolicySmoke.h` | `231` | `69DF7B6E9805B272A83B5C979FDC56FB09EE6403C12DA76067D63837958884FB` |
| `OddsWell.cpp` | `1,470` | `D39F1888ECA930BBFC34CAA96D14CC51A1CD70F9BACAB55EF4918D4C4313365A` |
| `OddsWell.Build.cs` | `357` | `AD9081D5745E5CE16D41E282A31D74C5FE5E451E6073A4A4A78D7A71E942B692` |
| `OddsWell.Target.cs` | `340` | `BE7D062A6116AA0EA88EB9878167C43E29873E2FE0A8DBA8C22710F5DFB8C7B2` |
| `OddsWell.uproject` | `190` | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18` |
| `DefaultEngine.ini` | `2,755` | `1442E7ADF71B4028993465D95A92C12C9FB8E39D0DA4AC77229C6B920E38F6D1` |
| `DefaultGame.ini` | `675` | `CE966B4DEF240A9F99712BBF79BD1F9832125D4251FCEFB60498458523F86048` |
| `Bootstrap.umap` | `8,422` | `44FC5E531591672E10E3740A780EAFB34326C2EADC7D85A37CFA352541932C16` |
| `SundaleGraybox.umap` | `83,147` | `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| `C:\Program Files\dotnet\dotnet.exe` | `167,208` | `AB1B71FD3DD71062E074C9FAB8312081A81B7F2B3E0327C48C4D249C8D1A3135` |
| `AutomationTool.dll` | `34,232` | `45C62F44B7B17E989BCDFEF26DABD30B5D6975D5300C24936529032B41B20132` |

All identities matched the frozen preconditions before the attempt.

## Exact direct attempt

`C:\Program Files\dotnet\dotnet.exe` was invoked directly once without UAT wrapper, reusable script, retry, repair, package launch, game launch, or Defender action. Its exact ordered twenty OS arguments were:

1. `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\DotNET\AutomationTool\AutomationTool.dll`
2. `BuildCookRun`
3. `-project=C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\OddsWell.uproject`
4. `-nop4`
5. `-utf8output`
6. `-unattended`
7. `-platform=Win64`
8. `-clientconfig=Development`
9. `-build`
10. `-cook`
11. `-map=/Game/Maps/Bootstrap+/Game/Maps/SundaleGraybox`
12. `-stage`
13. `-pak`
14. `-iostore`
15. `-compressed`
16. `-package`
17. `-archive`
18. `-archivedirectory=C:\tmp\OddsWellPhase1L5s\PackageFinal`
19. `-clean`
20. `-NoSign`

| Field | Exact observation |
| --- | --- |
| attempt count | `1` consumed |
| exit | `1`, natural |
| elapsed | `0.1880994 s` |
| missing host framework | `Microsoft.WindowsDesktop.App 10.0.0 (x64)` |
| framework found | `Microsoft.WindowsDesktop.App 8.0.11` |
| AutomationTool managed execution | `0` |
| build / cook / stage | `0 / 0 / 0` |
| pak / IoStore / package / archive | `0 / 0 / 0 / 0` |
| `PackageFinal` | absent |
| security, Defender, virus/threat, or `0x800700E1` text | `0` |
| retry / repair / install | `0 / 0 / 0` |

Security text count `0` is observation custody only and is not a Defender-clean claim.

## Frozen evidence

The complete captured transcript was normalized once, measured, and never rewritten. The second and final non-executable evidence patch recorded its measured identity plus two header-only manifests.

| Evidence artifact | Bytes | SHA-256 | Meaning |
| --- | ---: | --- | --- |
| `Evidence/BuildCookRun.combined.txt` | `616` | `8EE7683548074C76E1EAB8D767369F21F07909FF7F6BB57E0ABEC31B9B3424F5` | complete combined terminal transcript |
| `Evidence/session_custody.tsv` | `554` | `2B63E264A570CA4C104F58C4BDD453EF79F9380E01B029E60053E387445EEA70` | ordered attempt and transcript custody |
| `Evidence/package_manifest.tsv` | `27` | `C6988B2A3D3C63F106C96F3DEB0019C7F0D2A086AEAE684CA8655BE2B88F9D05` | header only; no package files existed |
| `Evidence/saved_manifest.tsv` | `27` | `C6988B2A3D3C63F106C96F3DEB0019C7F0D2A086AEAE684CA8655BE2B88F9D05` | header only; no Saved output was attributed to the attempt |

`PackageFinal` remained absent. The repository remained clean after the attempt and evidence custody. Exact target processes and watched TCP/UDP ports returned to `0`.

## Credits and boundaries

Phase 1L.5s build, cook, stage, pak, IoStore, package, archive, product, policy application, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, beta-exit, and readiness credits are all `0`. Product remains `NOT_MEASURED`; Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Prior Phase 1L.5n source-authored credit, Phase 1L.5q reconciliation credit, and Phase 1L.5r focused-automation/unchanged-module-test credits remain historical and unchanged; none converts this package attempt into package credit.

No product or source defect is demonstrated. No package exists, and no package or game was launched. Phase 1K and hands-on/input/accessibility evidence remain incomplete and not waived. Brains remain frozen; no training, learning, retraining, or readiness claim is made.

Installing `Microsoft.WindowsDesktop.App 10.0.0 (x64)` is a separate owner-gated prerequisite. This phase authorizes no download, installation, elevation, exclusion, Defender action, repair, or retry. Phase `1/6` closes only through this exact-five documentation custody; Phase 2 requires a fresh gate after any separately approved prerequisite decision.
