# Phase 1L.5ak — Skip-Build UBT/UBA Marker Semantics Reconciliation

Status: `COMPLETE LOCALLY — UBT_UBA_MARKER_SEMANTICS_RECONCILED; PACKAGE NOT RERUN; PRODUCT NOT MEASURED; FRESH BATCH PHASE 3/6`

## Scope and preserved truth

This docs-only source reconciliation follows Phase 1L.5aj commit `5ae11c645a213bfcde7402e3452aefa32e1ccefe`, exactly two verified Project upserts, and count `2/6`. Phase 1L.5aj remains permanently `PACKAGE_EVIDENCE_LIMITED` / `UBT_UBA_ZERO_PREDICATE_NOT_MET`, with package and custody credits `0`; its successful artifacts remain supplemental only. No source/config edit, build, package rerun, launch, transient-root access, cleanup, Defender action, or product measurement occurred.

## Exact source contract

| # | contract | source-backed observation | current_status |
| ---: | --- | --- | --- |
| 1 | `VALIDATE_MODE_OWNERSHIP` | `ValidatePlatformsMode.cs:14–16` owns the exact mode name and options. | `SOURCE_CONFIRMED` |
| 2 | `VALIDATE_MODE_BEHAVIOR` | Lines `31–92` apply arguments, resolve platforms and SDK readiness, emit PlatformValidate results or captured SDK exception text, and return `0`; neither path dispatches target build, compiler, linker, or action work. | `SOURCE_CONFIRMED` |
| 3 | `TRACE_UBA_GLOBAL_INITIALIZATION` | `UnrealBuildTool.cs:201–233` initializes `Trace.uba` and EpicGames.UBA tracing before ordinary top-level mode execution; path presence is trace custody, not action proof. | `SOURCE_CONFIRMED` |
| 4 | `UBA_HORDE_CONFIG_EMISSION` | `UbaHordeConfig.cpp:354–443` reads configuration and emits enabled details or `Not Enabled`; either branch is configuration custody only. | `SOURCE_CONFIRMED` |
| 5 | `BUILD_MARKER_OWNERSHIP` | `BuildProjectCommand.Automation.cs:60–73` returns before build markers when `Params.Build=false`; STARTED is after the guard and line `270` owns COMPLETED. | `SOURCE_CONFIRMED` |
| 6 | `PHASE2_OBSERVATIONS` | The committed Phase 1L.5aj report records ValidatePlatforms `1`, `Trace.uba` `1`, UBA/Horde config `1`, build markers `0/0`, Candidate compile `0`, game link `0`, and six unchanged outputs; the three strings are `VALIDATION_OR_TRACE_OR_CONFIG_CUSTODY_ONLY`. | `SOURCE_CONFIRMED` |
| 7 | `FUTURE_NEUTRAL_SET` | Exact ValidatePlatforms, Trace.uba, and UBA/Horde configuration are counted separately and never alone or together prove compile/link/build activity or violate skip-build. | `SOURCE_CONFIRMED` |
| 8 | `FUTURE_ACTION_SET` | Build STARTED/COMPLETED, reliable Candidate/compiler or game/editor link/metadata progress, or frozen six-output advance are action evidence; future skip-build requires all exact action counts `0` and outputs unchanged. | `SOURCE_CONFIRMED` |
| 9 | `UNCLASSIFIED_MODE_RULE` | Future UBT modes other than exact `-Mode=ValidatePlatforms`, ambiguous ownership, incomplete transcript, or inability to bind markers to frozen source map to `EVIDENCE_ABSENT` and `PACKAGE_EVIDENCE_LIMITED`; never silently neutral. | `SOURCE_CONFIRMED` |
| 10 | `UNEXPECTED_ACTION_RULE` | Reliable future action evidence or frozen-output drift maps to `PACKAGE_FAIL` with qualifier `UNEXPECTED_BUILD_ACTIVITY_DURING_SKIP_BUILD`; this is skip-build contract failure, not product defect or measurement. | `SOURCE_CONFIRMED` |
| 11 | `NO_RETROACTIVE_CREDIT` | Phase 1L.5aj remains LIMITED/credits0; Phase 1L.5ak performs no package attempt and grants only semantics-contract credit. | `SOURCE_CONFIRMED` |

All `11` rows are `SOURCE_CONFIRMED`; outcome is `UBT_UBA_MARKER_SEMANTICS_RECONCILED`. Missing/unreadable identity or current `EVIDENCE_ABSENT` would be `RECONCILIATION_EVIDENCE_LIMITED`; source contradiction would be `RECONCILIATION_CONFLICT`.

## Decision and boundaries

A `SOURCE_BACKED_ACTION_PREDICATES` is `SELECTED`/recommended/minimal. B `RETAIN_ANY_UBT_UBA_ZERO_PREDICATE` is `NOT_SELECTED`/rejected because UE5.8 emits validation/trace/config custody without proving a build. C `RETROACTIVE_PHASE2_RECLASSIFICATION` is `NOT_SELECTED`/rejected because Phase 1L.5aj remains permanently frozen LIMITED.

`skip_build_marker_semantics_reconciliation_credit=1`. Current build, package, package-custody, launch, runtime, product, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, and readiness credits are `0`. Candidate B remains provisional/unvalidated; product is `NOT_MEASURED`; hands-on and accessibility are deferred, not waived; Brain remains frozen at `0.6N`; Phase 1M, roadmap Phase 2, beta exit, and V1 are unauthorized. The contract reduces false build-evidence classification without relaxing compiler/link/output-drift detection. No Defender-clean or revocation-clean claim is made.

FRESH BATCH PHASE 3/6 CLOSED — NO AUTOMATIC PHASE 4
