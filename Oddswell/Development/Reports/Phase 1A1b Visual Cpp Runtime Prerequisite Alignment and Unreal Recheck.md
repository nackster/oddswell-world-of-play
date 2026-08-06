---
tags:
  - development
  - phase-1a1b
  - unreal-engine
  - visual-cpp
  - prerequisite
status: complete
date: 2026-07-19
---

# Phase 1A.1b: Visual C++ Runtime Prerequisite Alignment and Unreal Recheck

## Outcome

**READY FOR THE SEPARATE MINIMAL-PROJECT BOOTSTRAP.** The owner-approved official Microsoft Visual C++ 2015–2022 x64 Redistributable updated the registered runtime from `v14.44.35211.00` to `v14.51.36247.00`. After the required manual reboot, Unreal Engine 5.8 reached its no-project Project Browser without repeating the earlier runtime warning, logged no fatal startup failure, and closed normally without an Unreal 5.8 process left behind.

This phase created no Unreal project, package, game adapter, asset, runtime feature, economy, credit, wagering, deployment, paid API call, or model job. It changed no x86 runtime, Visual Studio workload, compiler, or Windows SDK. Cost was **$0.00**.

## Verified Microsoft package

| Evidence | Verified result |
| --- | --- |
| Microsoft Learn source | `https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170` |
| Official x64 permalink | `https://aka.ms/vc14/vc_redist.x64.exe` |
| Resolved Microsoft source | `download.visualstudio.microsoft.com/.../843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C/VC_redist.x64.exe` |
| Downloaded package | `C:\Users\reali\AppData\Local\Temp\OddsWell\Phase1A1b-20260718-205744\vc_redist.x64.exe` |
| Size | `18,731,856` bytes |
| SHA-256 | `843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C` |
| File/product version | `14.51.36247.0` |
| Authenticode | `Valid`; signer `Microsoft Corporation`; issuer `Microsoft Code Signing PCA 2024` |

The signature, publisher, hash, size, and version were checked before execution. The installer ran only after action-time owner confirmation; the owner manually approved UAC. Automation did not act on any security or privacy prompt.

## Installation and reboot evidence

- Pre-install registry state: `HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64` reported installed version `v14.44.35211.00`.
- Microsoft Setup displayed **Setup Successful** and required a restart. The separate **Close** action was used; **Restart** was not automated.
- Main setup log `C:\Users\reali\AppData\Local\Temp\dd_vcredist_amd64_20260718205808.log` recorded minimum and additional packages with result `0x0`, overall apply result `0x0`, restart `Required`, bootstrapper restart `No`, and exit `0xbc2` (`3010`, success with reboot required).
- The minimum-runtime MSI log recorded successful installation, restart required, and restart deferred. The additional-runtime MSI also completed successfully.
- The owner rebooted manually. Windows Event Log service startup at `2026-07-18 21:13:52` and workstation statistics since `21:13:53` provide independent reboot evidence.
- Immediately after reboot, Component Based Servicing, Windows Update, and `PendingFileRenameOperations` reboot indicators were all clear.
- Post-reboot registry state: installed x64 runtime `v14.51.36247.00` (`Major 14`, `Minor 51`, `Bld 36247`, `Rbld 0`).

On the later verification morning, `PendingFileRenameOperations` contained only Brave Browser `old_chrome.exe` temporary cleanup paths. That generic, later browser-maintenance entry is not attributed to the Visual C++ update; the two Windows servicing indicators remained clear.

## Unreal Engine recheck

- The post-reboot Unreal Editor process started at `2026-07-18 21:20:22` America/Mexico_City from `C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe`.
- A fresh, uniquely targeted window observation showed **Unreal Engine 5.8**, Home/Getting Started, **New Project**, and **My Projects**. No project was opened or created.
- No Visual C++ prerequisite warning, security prompt, privacy prompt, or authentication prompt appeared in the verified window state.
- `Unreal.log` reported build `++UE5+Release-5.8-CL-55116800`, engine `5.8.0-55116800+++UE5+Release-5.8`, and `Startup complete`.
- Runtime-warning audit: zero `14.44`, `14.50`, `Redistributable`, or `prerequisite` matches. The sole `Visual C++` line identifies the compiler used to build Unreal and is not a runtime warning.
- Fatal audit: zero `Fatal error`, `Critical error`, `Unhandled Exception`, or `Assertion failed` matches.

## Normal exit and repository safety

The editor was closed from the freshly verified Project Browser with `Alt+F4`. The log records `CloseEditor`, `Editor shut down`, `Exiting`, and log close at `2026-07-19 11:13:09`. Afterward, there were zero windows and zero processes whose executable path was under `C:\Program Files\Epic Games\UE_5.8`. The repository contains no `.uproject` file.

## Validation

- Full frozen regression suite: **65/65 passed** in `126.344s`.
- Brain Admin self-check: **passed**.
- Python compilation: **passed** for `phase0a`, `phase0b`, `phase0c`, `phase0d`, and `brain_admin`.
- Affected Obsidian links: **passed**.
- Updated beta-roadmap canvas: **passed** JSON parsing, unique node IDs, and edge-reference validation (`22` nodes, `0` edges).
- Repository hygiene: **passed** whitespace and exact six-file scoped-diff checks; no repository `.uproject` or UE 5.8 process exists.

## Next gate

Phase 1A.1c may create and reopen the smallest empty local UE 5.8 Windows project in a separate scoped phase. Packaging, permanent engine adoption, final art, and the one-block recorded-replay benchmark remain inactive.
