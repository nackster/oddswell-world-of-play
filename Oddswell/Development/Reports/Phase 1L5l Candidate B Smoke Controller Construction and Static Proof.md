# Phase 1L.5l Candidate B Smoke Controller Construction and Static Proof

## Status

`CONTROLLER_STATIC_FAIL`

`PRE-LAUNCH_PASS = false`

Phase 1L.5l constructed and externally audited one native PowerShell Candidate B policy-smoke controller, then consumed the one authorized `-PreflightOnly` invocation. That invocation terminated under strict mode before it wrote any controller-owned static result. No repair, second invocation, game launch, manifest, seal, product measurement, or product credit followed.

This is the local Phase 2/6 failure closure for the contract in [[Phase 1L5k Candidate B Packaged Policy Smoke Controller Contract]]. It does not change the provisional policies in [[DEC-027 Candidate B Compatibility First Direct3D Policy]], [[DEC-028 Candidate B Balanced Medium GI and Reflection Policy]], [[DEC-029 Candidate B Native TSR AA and Upscaler Policy]], [[DEC-030 Candidate B Fixed 100 Percent Screen Percentage Policy]], [[DEC-031 Candidate B Exact UE5.8 Medium Profile Policy]], or [[DEC-032 Candidate B Frame Control and Bounded Planning Authority]].

## Frozen transient custody

The transient root remains `C:\tmp\OddsWellPhase1L5l-20260816T033812Z`. Its final file set is exactly four files:

| Artifact | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `Controller/candidate_b_policy_smoke.ps1` | 76,480 | 1,135 | `2AD756D1C78284B712B4E598518B354CC50AB10EDA99CB47BC921926D6AEEE3A` |
| `StaticEvidence/source_ast.json` | 1,235 | 43 | `D8E077402650E33D5E481204C2BE984E5E4D2D9E44FEBBE98FD2FB4C77808E73` |
| `StaticEvidence/defender_before.json` | 392 | 12 | `CDA65DB24D67C4CF937F1F0FBED2CD3FB8A1ADC8BD2B8C182B48268F93E2C181` |
| `StaticEvidence/defender_after.json` | 560 | 15 | `0649D35CBC0A1EDC77084EE1E11D76F7C9E91563305BC795B3E205B1FBFFA08D` |

All four transient artifacts remain outside the repository. Their bytes were not repaired, rewritten, imported, moved, deleted, manifested, or sealed after the sole invocation.

## Construction and external source proof

The controller was authored from a blank file with native PowerShell facilities. Phase 1L.5j controller sources were not opened, read, diffed, copied, or imported.

The final external parser audit bound `source_ast.json` to the controller's exact SHA-256, byte count, line count, and mandatory parameters `Root`, `ExpectedControllerSha256`, `ExpectedRepoHead`, and `PreflightOnly`. It recorded:

- parser errors `0`;
- `Start-Process` AST sites `1`, nested under `if (-not $PreflightOnly)`;
- alternate launchers, Defender commands, `System.Diagnostics.Process.Start`, call operators, dot sourcing, dynamic invocation, launcher helpers, member `Start`, Process type aliases, `New-Object` Process, and reflection launch sites `0` each;
- bounded `WaitForExit` sites `1` and unbounded sites `0`;
- renderer mutation fixtures: exact acceptable `PASS`, exact lower feature/shader values `PRODUCT_FAIL`, and absent, multiple, conflicting, or malformed evidence `EVIDENCE_LIMITED`;
- the combined PID-true, log-false, manifest-mismatch fixture `EVIDENCE_LIMITED`.

Those source-only checks did not emit `CONTROLLER_STATIC_PASS`, did not constitute Coordinator `PRE-LAUNCH_PASS`, and did not authorize a game run.

## Sole preflight invocation

The frozen resolved controller call was:

```powershell
& 'C:\tmp\OddsWellPhase1L5l-20260816T033812Z\Controller\candidate_b_policy_smoke.ps1' -Root 'C:\tmp\OddsWellPhase1L5l-20260816T033812Z' -ExpectedControllerSha256 '2AD756D1C78284B712B4E598518B354CC50AB10EDA99CB47BC921926D6AEEE3A' -ExpectedRepoHead '0458af918d8e962a0b9b36e491738bcd87102951' -PreflightOnly
```

Invocation count is exactly `1`. The controller SHA was verified immediately before the call. Standard output contained `0` controller result rows. The outer shell captured the terminating PowerShell error; its shell status was not a controller pass or a valid controller exit result. No stdout or stderr capture file was added to the transient root, so the exact error custody is the execution transcript frozen by this report and the source line below.

Exact terminating error:

```text
The variable '$_' cannot be retrieved because it has not been set.
```

Exact source custody is controller line `132`, inside `Get-NetstatCount` and inside `foreach ($Line in $Lines)`:

```powershell
$Columns = @($_.Trim() -split '\s+' | Where-Object { $_ })
```

The first `$_` is outside a pipeline script block and is unset under `Set-StrictMode -Version Latest`; the loop variable was `$Line`. This report records the defect only. Phase 1L.5l did not repair it and did not invoke the controller again.

## Required outputs and launch custody

After the failed invocation:

| Required state | Observed |
| --- | --- |
| `StaticEvidence/preflight.json` | absent |
| `StaticEvidence/contract_registry.json` | absent |
| `StaticEvidence/no_launch.json` | absent |
| `StaticEvidence/controller_result.json` | absent |
| `StaticEvidence/static_manifest.tsv` | absent |
| `StaticEvidence/candidate_seal.json` | absent |
| `Profile/` | absent |
| `Evidence/` | absent |
| Game or helper launch | `0` |
| `OddsWell` / `UnrealEditor` processes | `0` |
| watched TCP/UDP endpoints on `17777`, `1985`, `7810` | `0` |

There is no sealed candidate, no review acceptance, and no separate Coordinator `PRE-LAUNCH_PASS`. No game PID existed, no route ran, and no policy readback, renderer, window, native-TSR, route, economy, or postflight product evidence was collected.

## Defender before and after observations

The root-owned read-only before snapshot was captured at `2026-08-16T03:38:41.7988628Z`. It recorded threat ID `2147840094`, initial detection time `2026-08-15 22:10:01`, last status change `2026-08-15 22:10:30`, `action_success=true`, `current_threat_execution_status_id=0`, `active=false`, and `did_threat_execute=false`.

The root-owned read-only after snapshot was captured at `2026-08-16T12:58:07.4359388Z`. It recorded the same threat ID, initial detection time `2026-08-16 07:38:51`, last status change `2026-08-16 07:39:05`, `action_success=true`, `current_threat_execution_status_id=0`, `active=false`, `did_threat_execute=false`, `delta_from_before=NEWER_DETECTION`, `resource_summary=CmdLine PowerShell external controller source audit`, and `phase_disposition=CONTROLLER_STATIC_FAIL`.

The newer detection is an observed security signal. Its inactive/remediated state does not prove that it was harmless, does not prove which exact command caused it, and does not waive security review. No Defender exclusion, preference mutation, remediation command, installation, or elevated query was performed by the controller.

## Repository, package, and product custody

Repository HEAD remained `0458af918d8e962a0b9b36e491738bcd87102951`, with worktree rows `0` and index rows `0` before this docs-only report. Independent custody checks found no change to repository product, source, config, package, map, profile, or runtime state.

The accepted package root remained `C:\tmp\OddsWellPhase1L4b\PackageFinal\Windows` with canonical files `50`, canonical bytes `1,051,962,028`, Python files `0`, separate Saved files `12`, and separate Saved bytes `101,332`. Current identity checks retained:

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| wrapper `OddsWell.exe` | 171,520 | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| game `OddsWell/Binaries/Win64/OddsWell.exe` | 341,401,600 | `4A437A5F83B87A857B463CE6E0A37D432114A4657CE7C6665DA3C918A6461C5A` |
| UFS `OddsWell/Content/Paks/OddsWell-Windows.ucas` | 208,199,024 | `9CB5864C890F5AF33FDB751739CBBF46BABD3DC17C40A1119377353BDD514356` |
| `SundaleGraybox.umap` | 83,147 | `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| `OddsWell.uproject` | 190 | `020234D58303E8D98C9E1D83B683F4F8F7889383932F069640E3284EBD2FEE18` |
| `OddsWell.Build.cs` | 350 | `157CC02E09784B95D4C176446CE1D8BD558CC9261E9E1B1C696FDDACC0AACAE0` |

These are custody facts, not a new package validation, compatibility result, minimum-PC result, or readiness result.

## Verdict and credit boundary

The exact product matrix remains:

| Field | Value |
| --- | --- |
| `attempt_consumed` | `false` |
| `valid_attempt_started` | `false` |
| `product_measured` | `false` |
| `product_result` | `NOT_MEASURED` |
| `credit_application` | `0` |
| `credit_route` | `0` |
| `cleanup_performed` | `false` |
| `retry_allowed` | `false` |

Controller construction credit, source-review credit, product application credit, route credit, compatibility credit, performance credit, minimum-PC validation credit, compliance credit, and readiness credit are all `0`. The Candidate B target and all policy selections remain provisional and unvalidated. Phase 1L.5l authorizes no repair, retry, seal, launch, import, runtime test, configuration change, Notion update, or next-phase execution.
