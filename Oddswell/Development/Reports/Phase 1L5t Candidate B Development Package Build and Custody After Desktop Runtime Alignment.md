---
title: Phase 1L.5t Candidate B Development Package Build and Custody After Desktop Runtime Alignment
type: report
status: Complete locally - package evidence limited
date: 2026-08-18
---

# Phase 1L.5t Candidate B Development Package Build and Custody After Desktop Runtime Alignment

## Result

`COMPLETE LOCALLY — PACKAGE_EVIDENCE_LIMITED; TOOL-OWNED STDOUT/STDERR TRUNCATED AND UNAVAILABLE; EVIDENCE FILES 0; PRODUCT NOT MEASURED; FRESH BATCH PHASE 2/6 CLOSED`

After the separately owner-approved, noncounting Windows Desktop Runtime `10.0.11 x64` installation passed, Phase 1L.5t consumed one direct dotnet/AutomationTool BuildCookRun attempt. The process exited naturally `0` and AutomationTool reported successful build, cook, stage, package, and archive operations. However, the tool-owned combined stdout/stderr return was truncated and the exact visible subset became unavailable after its execution cell closed. The required evidence transcript and manifests therefore were not written. Terminal disposition is `PACKAGE_EVIDENCE_LIMITED / TOOL_OWNED_STDOUT_STDERR_TRUNCATED_AND_UNAVAILABLE`, not package evidence pass.

## Frozen preflight and prerequisite

Repository HEAD was clean at `8de19ea25c744e5dce144e01c27d08ddbcdfed52`. Phase 1L.5s is closed at that commit with independently verified exactly two Notion upserts. The noncounting Windows Desktop Runtime prerequisite separately reached `INSTALL_PASS`: `Microsoft.WindowsDesktop.App 10.0.11` and the preserved `8.0.11` runtime were both present, and the dotnet host was `10.0.11 x64`. This installation is not Phase 2 evidence credit.

All frozen source, project, config, map, dotnet, AutomationTool, and installed-runtime hashes matched before the attempt. Dotnet Authenticode was `Valid` with Microsoft subject, AutomationTool Authenticode was `Valid` with Epic Games subject, the root `C:\tmp\OddsWellPhase1L5t` was absent, and exact-path target processes plus watched TCP/UDP ports were `0`.

## Exact attempt custody

The direct dotnet process used the frozen exact twenty-token BuildCookRun vector with both maps, Development/Win64, build, cook, stage, pak, IoStore, compression, package, archive, clean, and no-sign options. It used archive root `C:\tmp\OddsWellPhase1L5t\PackageFinal`.

| Field | Exact observation |
| --- | --- |
| attempt count | `1` |
| retained PID / start UTC | `46240` / `2026-08-18T18:56:06.0647904Z` |
| process result | natural exit `0` |
| tool-owned wall time | `198.3 s` |
| AutomationTool BuildCookRun time | `196.08 s` |
| AutomationTool elapsed statement | `0h 3m 17s` |
| build / cook / stage / package / archive completed markers | `1 / 1 / 1 / 1 / 1` |
| `BUILD SUCCESSFUL` / AutomationTool exit-0 success | `1 / 1` |
| non-argument `HasMapsToCook` / `Params.HasMapsToCook` exact map markers | `1 / 1` |
| retry / timeout stop / cleanup / packaged-game launch | `0 / 0 / 0 / 0` |

Security, Defender, virus, threat, and `0x800700E1` text counts were `0`; that observation is not a Defender-clean claim. No game was launched and no product behavior was measured.

## Required evidence failure

The required evidence state is exact and fail-closed:

| Required evidence file | Status |
| --- | --- |
| `Evidence/BuildCookRun.combined.txt` | `ABSENT` |
| `Evidence/session_custody.tsv` | `ABSENT` |
| `Evidence/package_manifest.tsv` | `ABSENT` |
| `Evidence/saved_manifest.tsv` | `ABSENT` |

- evidence patch 1 count: `0`
- evidence patch 2 count: `0`
- evidence file count: `0`
- tool-owned returned stdout/stderr line count reported by the tool: `941`
- literal truncation notice: `10859 tokens truncated`
- exact returned stdout/stderr byte count: `NOT_AVAILABLE`
- exact returned stdout/stderr SHA-256: `NOT_AVAILABLE`
- exact visible subset after the completed cell closed: `UNAVAILABLE / UNPROVEN`

The closed execution cell could not be reopened (`exec cell 12 not found`). The rendered conversation excerpt was not a byte-addressable source, so no manual reconstruction was allowed. No internal log was substituted and no partial transcript was promoted into complete evidence.

## Supplemental internal-log custody

These retained AutomationTool-owned logs are supplemental only. They were not copied into the empty Phase 1L.5t evidence directory and cannot replace the missing combined transcript.

| Supplemental file | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `C:\Users\reali\AppData\Roaming\Unreal Engine\AutomationTool\Logs\C+Program+Files+Epic+Games+UE_5.8\Log.txt` | `255,300` | `2,260` | `EAD466E79BA9451C40CED5B7253C7EF48972075B564D8AE25FD132E78F62DFA0` |
| `C:\Users\reali\AppData\Roaming\Unreal Engine\AutomationTool\Logs\C+Program+Files+Epic+Games+UE_5.8\Log.json` | `796,098` | `2,193` | `A54891069773F676A4D127A33CE2F8FD1C7F9C07C3F2A2CFF7134397A83C3CA0` |

The logs contain one each of the build/cook/stage/package/archive completed markers, `BUILD SUCCESSFUL`, and AutomationTool exit `0`; failure/security markers were `0`. These observations corroborate operations but do not cure the required evidence-file absence.

## Supplemental package custody

`PackageFinal` existed with `50` files totaling `1,052,111,020` bytes. Project `Saved/StagedBuilds/Windows`, outside PackageFinal, also contained `50` files totaling the same bytes. A read-only path/size/SHA-256 comparison between `PackageFinal/Windows` and the project staged mirror found mismatches `0`.

Selected supplemental identities were:

| File | SHA-256 |
| --- | --- |
| launcher `Windows/OddsWell.exe` | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| game binary `Windows/OddsWell/Binaries/Win64/OddsWell.exe` | `77FB256EA51225C466235A58DF59DB69C3B468333E1A16B3C01D8F4567215D8A` |
| `OddsWell-Windows.pak` | `7ADF7168C8093E982C44BE5021D8AD7D4A03ABB422AC6912956613511B98D0FB` |
| `global.ucas` | `D241B270B82F75C30830EB3AD818CAE41E30DBF01A0D676558AFF7E6AA2DD2F0` |
| `global.utoc` | `068C4318FA12F557CAB56C03E7A15AEFA81D99092139F13E5B14C8865CDB97A5` |
| `OddsWell-Windows.ucas` | `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356` |
| `OddsWell-Windows.utoc` | `FD7187F5B8B7C01202F584AF038775C13C070BD73F5CF71A0BFB69241E789ED3` |

These files and the project staged mirror remain preserved. No cleanup was performed. Because both required manifests are absent, the supplemental inventory is not a persisted Phase 1L.5t evidence manifest and grants no package credit.

## Credits and boundaries

Phase 1L.5t build, cook, stage, pak, IoStore, package, archive, evidence, product, policy application, route, gameplay, economy, performance, minimum-PC validation, compatibility, accessibility, hands-on, beta-exit, and readiness credits are all `0`. Product remains `NOT_MEASURED`; Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. The limited result demonstrates neither a product defect nor a source defect.

Source, project, config, and map hashes remained unchanged; repository HEAD remained clean; exact target processes and watched ports drained to `0`. No retry, cleanup, package/game launch, Defender action, evidence rewrite, Notion action, or Phase 3 occurred. Phase `2/6` closes through this exact-five documentation custody. A further phase requires a fresh gate and cannot retroactively repair this evidence record.
