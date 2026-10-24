# Phase 1L.5be Candidate B RHI Name Evidence Contract Reconciliation

## Status

`COMPLETE LOCALLY — RHI_NAME_EVIDENCE_CONTRACT_RECONCILED; EXACT ENGINE-EMITTED D3D12 (SM6) CONTRACT SELECTED; SOURCE/BUILD/PACKAGE/LAUNCH NOT RUN; PRODUCT NOT MEASURED; AUGUST 26 NIGHTLY BATCH PHASE 5/6`

## Scope and authority

Phase 1L.5be reconciles one project predicate, one installed UE5.8 construction, and the retained Phase 1L.5bd observation. It is documentation-only. No project or engine source, configuration, test, build, automation, package, launch, route, performance, or product action occurs.

Baseline HEAD is `7f0cfdd0bf4b16624c0728db3e755539230df6cf`, clean with index `0`. Candidate source is `32,733` bytes/SHA `DAECEA4380544ADE59B701461739C2B75B41A449C72FCCCF43D96EDC58E95434`/blob `ba49c5bcaf69bd1e37ecb5c6770b9db29b128f67`. Installed `WindowsDynamicRHI.cpp` is `49,985` bytes/SHA `AE011151291E149D44DBD85C5942C5D80D6807BCED51D2D08C2CB69FF68AB01E`.

## Exact source reconciliation

| Ordinal | Subject | Authority/evidence | Status |
| ---: | --- | --- | --- |
| 1 | Candidate runtime RHI read | `CandidateBPolicySmoke.cpp:515 reads FApp::GetGraphicsRHI()` | `SOURCE_CONFIRMED` |
| 2 | Candidate RHI normalization | `CandidateBPolicySmoke.cpp:516 trims outer whitespace with TrimStartAndEndInline()` | `SOURCE_CONFIRMED` |
| 3 | Current displayed expectation | `CandidateBPolicySmoke.cpp:517 records expected literal D3D12` | `SOURCE_CONFIRMED` |
| 4 | Current match predicate | `CandidateBPolicySmoke.cpp:519 uses case-insensitive exact equality with D3D12` | `SOURCE_CONFIRMED` |
| 5 | Windows D3D12 log token | `WindowsDynamicRHI.cpp:67-77 maps EWindowsRHI::D3D12 to exact D3D12` | `SOURCE_CONFIRMED` |
| 6 | Windows SM6 feature token | `WindowsDynamicRHI.cpp:93-101 maps ERHIFeatureLevel::SM6 to exact SM6` | `SOURCE_CONFIRMED` |
| 7 | Windows D3D12 presentation grammar | `WindowsDynamicRHI.cpp:188-198 formats D3D12 as exact %s (%s) using the RHI and feature tokens` | `SOURCE_CONFIRMED` |
| 8 | FApp RHI storage | `WindowsDynamicRHI.cpp:1365-1366 passes that formatted value to FApp::SetGraphicsRHI` | `SOURCE_CONFIRMED` |
| 9 | Retained packaged observation | `committed 1L5bd report lines46-48 records expected D3D12, actual D3D12 (SM6), MISMATCH, as the sole mismatch` | `EVIDENCE_CONFIRMED` |
| 10 | Approved policy authority | `DEC-027 lines27 and29 separately require rendering API D3D12 and Shader Model 6.6+ (SM6.6+)` | `AUTHORITY_CONFIRMED` |
| 11 | Current execution boundary | `no source correction, build, automation, package, launch, rerun, policy rescore, route, performance, or product validation occurs in Phase1L.5be` | `EVIDENCE_ABSENT` |

Rows 1–8 are `SOURCE_CONFIRMED`, row 9 is `EVIDENCE_CONFIRMED`, row 10 is `AUTHORITY_CONFIRMED`, and row 11 is `EVIDENCE_ABSENT`. This exact cardinality and order reconcile to `RHI_NAME_EVIDENCE_CONTRACT_RECONCILED / NONE`.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `EXACT_ENGINE_EMITTED_D3D12_SM6_NAME` | `SELECTED` | `RECOMMENDED` | Installed UE5.8 source constructs the Windows D3D12 SM6 FApp value as D3D12 (SM6), and retained packaged evidence observes that exact value; a future bounded correction can change only the displayed expected literal and exact case-insensitive comparator operand to D3D12 (SM6), with no helper, include, abstraction, fallback, or dependency. |
| B | `KEEP_BARE_D3D12_EQUALITY` | `NOT_SELECTED` | `REJECTED` | Bare D3D12 exact equality contradicts the installed UE5.8 construction and the retained packaged observation. |
| C | `BROAD_D3D12_PREFIX_OR_SUBSTRING` | `NOT_SELECTED` | `REJECTED` | A prefix or substring predicate accepts values broader than the exact approved D3D12 plus SM6 contract. |

The selection is prospective only. It authorizes no implementation and proves no Shader Model 6.6 version. Phase 1L.5bd remains permanently `PACKAGED_POLICY_FAIL/RHI_NAME_EXACT_VALUE_MISMATCH` and is not rescored.

## Credits and nonclaims

`rhi_name_evidence_contract_reconciliation_credit=1`.

`rhi_name_source_correction_credit=0`; `native_build_credit=0`; `source_compile_credit=0`; `focused_automation_credit=0`; `package_build_credit=0`; `package_custody_credit=0`; `package_launch_credit=0`; `policy_application_credit=0`; `policy_full_validation_credit=0`; `route_credit=0`; `visible_client_credit=0`; `product_measurement_credit=0`; `performance_credit=0`; `minimum_pc_credit=0`; `compatibility_credit=0`; `accessibility_credit=0`; `hands_on_credit=0`; `beta_exit_credit=0`; `brain_maturity_credit=0`; `readiness_credit=0`.

Phase 1L.5bd's `activation_credit=1`, `packaged_candidate_source_execution_credit=1`, and `package_launch_credit=1` are historical/prior-only, not new Phase 1L.5be credits. There is no source/config/test change; build, automation, package, launch, route, gameplay, visible-client, performance, compatibility, accessibility, hands-on, minimum-PC, beta-exit, Brain, readiness, and product measurement are not run. There is no runtime rerun, policy rescore, product/source/security defect inference, or Defender-clean inference. Candidate B remains provisional/unvalidated and product remains `NOT_MEASURED`.

## Prior truth

Phase 1L.5bd remains closed at full commit `7f0cfdd0bf4b16624c0728db3e755539230df6cf`, independently verified exactly two canonical Project upserts and August 26 nightly count `4/6`. Its report is `Oddswell/Development/Reports/Phase 1L5bd Candidate B Corrected Packaged Activation and Policy Evidence.md`, `6,277` bytes, SHA `B99A52B2F3787C418BB0874E984337656B933398A664C14D2D26AD289DE4D440`, blob `cc65684e3bde77a16a43b0bd430a0815df4ae5e1`. Its policy failure remains permanent.

## Boundary and stop

Phase 1L exit remains incomplete. Phase 1M, Roadmap Phase 2, Version 1, release, readiness, and successor execution remain unauthorized. Cursor suitability is `NOT_SUITABLE`: this authority-sensitive reconciliation needs no independent implementation task.

AUGUST 26 NIGHTLY BATCH PHASE 5/6 CLOSED — NO AUTOMATIC PHASE 6
