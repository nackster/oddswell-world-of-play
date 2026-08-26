# Phase 1L.5bf Candidate B Exact D3D12 SM6 Name Source Correction

## Status

`COMPLETE LOCALLY — RHI_NAME_SOURCE_CORRECTION_VERIFICATION_FAIL; FULL_NATIVE_REGRESSION_FAILED; PACKAGE LAUNCH NOT RUN; PRODUCT NOT MEASURED; AUGUST 26 NIGHTLY BATCH PHASE 6/6`

## Scope and authority

Phase 1L.5bf performs the smallest source correction selected by the Phase 1L.5be reconciliation, then runs the mandatory verification sequence fail-fast. Baseline HEAD was `3ee081f2ca3c0131b05ea4e9a18be989e0328ba8`, clean with index `0`. Candidate source was `32,733` bytes/SHA `DAECEA4380544ADE59B701461739C2B75B41A449C72FCCCF43D96EDC58E95434`/blob `ba49c5bcaf69bd1e37ecb5c6770b9db29b128f67`.

No helper, abstraction, include, dependency, test, fallback, broad match, configuration change, package launch, runtime policy rerun, route, performance run, cleanup, or retry was authorized.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `CHANGE_ONLY_EXPECTED_AND_COMPARATOR_TO_EXACT_D3D12_SM6` | `SELECTED` | `RECOMMENDED` | Changes only the two exact evidence-contract operands established by installed UE5.8 source and retained evidence. |
| B | `ADD_RHI_NAME_HELPER_OR_BROAD_MATCH` | `NOT_SELECTED` | `REJECTED` | Adds unnecessary structure or accepts names broader than exact `D3D12 (SM6)`. |
| C | `RERUN_WITHOUT_SOURCE_CORRECTION` | `NOT_SELECTED` | `REJECTED` | Repeats the already reconciled bare-`D3D12` mismatch without correcting its earliest dependency. |

## Exact static acceptance

| Ordinal | Subject | Evidence | Status |
| ---: | --- | --- | --- |
| 1 | Preidentity | Source matched `32,733` bytes and SHA `DAECEA4380544ADE59B701461739C2B75B41A449C72FCCCF43D96EDC58E95434` before patch | `MATCH` |
| 2 | Patch custody | Sole patch succeeded and changed only Candidate source | `MATCH` |
| 3 | Expected expression | Exact `D3D12 (SM6)` emitted expectation occurs once | `MATCH` |
| 4 | Comparator expression | Exact case-insensitive `D3D12 (SM6)` comparator occurs once | `MATCH` |
| 5 | Exact literal cardinality | `D3D12 (SM6)` literal occurs twice | `MATCH` |
| 6 | Bare literal absence | Bare `D3D12` literal occurs zero times | `MATCH` |
| 7 | RHI read structure | `GetGraphicsRHI`, trim, empty-to-unavailable, and case-insensitive exact comparison remain unchanged | `MATCH` |
| 8 | Adjacent runtime fields | `SM6`, `PCD3D_SM6`, feature-level, and SM6.6 unavailable rows remain unchanged | `MATCH` |
| 9 | Invariants | Includes remain `14`; no helper, dependency, test, registry, expected-184, or fail-closed result change | `MATCH` |
| 10 | Diff custody | Pre-document diff is one source path, one hunk, `2+/2-`, with no other token change | `MATCH` |

Post-source identity is `32,745` bytes, mtime `2026-08-26T15:18:21.3694857Z`, SHA `82B899C07D8A21E070743407F1D1DAA17E3582841288EDD79539CE9E36A4AEBC`, blob `01929ff911f1f2b97735e09eac6e5b98c9e3d325`.

## Verification result

The editor build exited naturally `0`, recorded exact compile/link/success counts `1/1/1`, advanced the Candidate object and editor DLL, and retained a valid receipt. Focused native automation exited naturally `0`; its canonical vector was `1/1/1/1/1/0/0/0/0`, malformed count `0`, and index `1/1` with no warning or failure.

The full native suite exited naturally `0`, emitted Found `1`, Started `74`, Completed Success `74`, Queue Empty `1`, TestExit `1`, TEST COMPLETE `0`, explicit failure `0`, fatal `0`, security `0`, and malformed `0`. Its registered path projection was exactly `74` unique rows, `3,446` bytes, SHA `1594287D0F3AF0A2ECDED9CBF7891CBD29349CD39864EB5CE9C85B0F9B6FC950`.

The authoritative report index nevertheless recorded `74` tests as `57` succeeded, `17` succeeded-with-warnings, `0` failed, `0` not run, `0` in process, `0` errors, and `25` warnings. That contradicts the frozen `74 succeeded / 0 succeeded-with-warnings` contract and controls `FULL_NATIVE_REGRESSION_FAILED`. It does not prove that the two-literal correction caused any warning, and it is not a product defect inference.

| Warning-bearing test | Warnings |
| --- | ---: |
| `OddsWell.Economy.ModularChairPurchase` | 1 |
| `OddsWell.Economy.OddsBucksLedger` | 4 |
| `OddsWell.Economy.OneBedroomUpgradePurchase` | 1 |
| `OddsWell.Economy.PendingQaMatchWinnerReceipt` | 1 |
| `OddsWell.Economy.SignalJacketPurchase` | 1 |
| `OddsWell.Economy.UpcomingQaMatchWinnerCancellation` | 1 |
| `OddsWell.Economy.UpcomingQaMatchWinnerLock` | 1 |
| `OddsWell.Economy.UpcomingQaMatchWinnerRequest` | 1 |
| `OddsWell.Economy.UpcomingQaMatchWinnerVoidDecision` | 1 |
| `OddsWell.Economy.UpcomingQaMatchWinnerVoidFinalization` | 1 |
| `OddsWell.League.CanonicalMatchWinnerCurrentMesaWinDecision` | 1 |
| `OddsWell.League.CanonicalMatchWinnerCurrentMesaWinFinalization` | 1 |
| `OddsWell.League.CanonicalMatchWinnerLock` | 2 |
| `OddsWell.League.CanonicalMatchWinnerLossDecision` | 1 |
| `OddsWell.League.CanonicalMatchWinnerLossFinalization` | 1 |
| `OddsWell.League.CanonicalMatchWinnerRequest` | 3 |
| `OddsWell.League.CanonicalPendingMatchWinnerReceipt` | 3 |

Fail-fast stopped the five Python suites, Brain Admin self-check, game build, and skip-build package audit before attempt. They are `NOT_RUN`, and package/staged manifests are absent.

## Evidence custody

The exact162 verification ledger is `5,306` bytes/SHA `CD43BD1788B1FB5394E03F85DB3D0B98207089C70011472889EA78C6A49F01B4`, UTF-8 without BOM, LF-final, with `162` unique keys. Evidence contains exactly `5` files and the fresh root exactly `9` regular files. Native identities are:

- Editor log `8,390` bytes/SHA `FA7FCD77738E532A4665F373B98632243F96D351BC350E1DB565B1042B147F11` and JSON `25,879` bytes/SHA `D2F8A30DF590576D28FC522D2FECA210D9B51F580A95362F8A01B3B677700663`.
- Focused log `254,655` bytes/SHA `3E7FA90F8ACFF8D236B49BC6DBF64995AA3796CEF06BC2B896D915773918B0FB` and index `1,114` bytes/SHA `14F610960EB81DD310BEB0F203249010C71D4162432C9D015973116D5D7BFFBE`.
- Full log `336,194` bytes/SHA `5918FFE8BC7CAAA32544FA9984DDB6F14DD628FB6813A3DA09C546B652C15306` and index `40,523` bytes/SHA `AC8F6D2FE7B982AB77DA8402F4FFFE4DEC1187E90444A968BE989B0AFA2FCD05`.

Post-run watched-process, unreadable-process, retained-PID TCP/UDP, and TCP/UDP `17777`, `1985`, and `7810` counts are all `0`.

## Credits and nonclaims

`rhi_name_source_correction_credit=1`; `rhi_name_source_compile_credit=1`; `editor_build_credit=1`; `focused_native_automation_credit=1`.

`full_native_regression_credit=0`; `frozen_python_regression_credit=0`; `brain_admin_self_check_credit=0`; `game_build_credit=0`; `package_build_credit=0`; `package_custody_credit=0`; `package_launch_credit=0`; `runtime_policy_credit=0`; `policy_full_validation_credit=0`; `route_credit=0`; `visible_client_credit=0`; `product_measurement_credit=0`; `performance_credit=0`; `minimum_pc_credit=0`; `compatibility_credit=0`; `accessibility_credit=0`; `hands_on_credit=0`; `beta_exit_credit=0`; `brain_maturity_credit=0`; `readiness_credit=0`.

The prior `rhi_name_evidence_contract_reconciliation_credit=1` remains prior-only. There is no package launch, runtime policy rescore, route, gameplay, visible-client, performance, compatibility, accessibility, hands-on, minimum-PC, beta-exit, Brain-maturity, readiness, or product evidence. No warning causation, product/source/security defect, Defender-clean state, or SM6.6 support is inferred. Candidate B remains provisional/unvalidated and product remains `NOT_MEASURED`.

## Prior truth

Phase 1L.5be remains closed at full commit `3ee081f2ca3c0131b05ea4e9a18be989e0328ba8`, independently verified exactly two canonical Project upserts and August 26 nightly count `5/6`. Its report is `Oddswell/Development/Reports/Phase 1L5be Candidate B RHI Name Evidence Contract Reconciliation.md`, `6,068` bytes, SHA `F94E53C06ABF94FAAAB2AB1C96DC243068E038A41489B96B68EB6A0A4AF0DE15`, blob `409f47d76e2e351fe5bca32c271bcdc4d994b955`.

Phase 1L.5bd remains permanently `PACKAGED_POLICY_FAIL/RHI_NAME_EXACT_VALUE_MISMATCH` and is not rescored. The six-phase ledger is `fb041232b9e8a8cd09a9dd76b9831c4e7e415004`, `8cc71e1da84abd58281996bad52287196b224582`, `f6eb506bd6635c142fbcafa6c48b79088972bf90`, `7f0cfdd0bf4b16624c0728db3e755539230df6cf`, `3ee081f2ca3c0131b05ea4e9a18be989e0328ba8`, and the pending local Phase 1L.5bf commit.

## Boundary and stop

Phase 1L exit remains incomplete. Phase 1M, Roadmap Phase 2, Version 1, release, successor work, and automatic continuation remain unauthorized.

NO SEVENTH PHASE — SIX-PHASE BATCH STOPPED.
