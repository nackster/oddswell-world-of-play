# Phase 1L.5bd Candidate B Corrected Packaged Activation and Policy Evidence

## Status

`COMPLETE LOCALLY — PACKAGED_POLICY_FAIL; RHI_NAME_EXACT_VALUE_MISMATCH; ACTIVATION PASS; BROAD PRODUCT NOT MEASURED; AUGUST 26 NIGHTLY BATCH PHASE 4/6`

Phase 1L.5bd performed one direct Candidate-only launch of the corrected, receipt-backed package. Exact Sundale selection and the complete activation chain passed. The scoped policy result failed one exact-value comparison; this is not broad product measurement or readiness evidence.

## Decision

| Option | Identifier | Disposition | Recommendation | Reason |
| --- | --- | --- | --- | --- |
| A | `ONE_CORRECTED_PACKAGE_CANDIDATE_ONLY_ACTIVATION_ATTEMPT` | `SELECTED` | `RECOMMENDED` | It is the smallest direct runtime proof for the newly corrected packaged world-selection seam. |
| B | `REBUILD_REPACKAGE_OR_REPEAT_STATIC_PROOF` | `NOT_SELECTED` | `REJECTED` | Build, package, and source custody were already proven and cannot replace runtime activation evidence. |
| C | `ADD_ROUTE_GAMEPLAY_OR_PERFORMANCE_FLAGS` | `NOT_SELECTED` | `REJECTED` | Route, gameplay, and performance flags expand authority and confound the earliest activation and policy seam. |

## Baseline and attempt

Baseline and post HEAD are `f6eb506bd6635c142fbcafa6c48b79088972bf90`, clean with index `0`. The corrected package contains exactly `50` files totaling `1,052,121,260` bytes. Its direct game executable is `341,429,760` bytes/SHA `8D90D8D5A02C05FB2967C305D8EAAC1A16C10726714FBA52A42B6CD8259A0FBC`. Package, source, module, configuration, maps, repository, watched processes, and TCP/UDP ports `17777`, `1985`, and `7810` retained their frozen identities.

The exact one-string argument value was `215` UTF-8 bytes, SHA `949BCAE2FEF7ABDD06274CBC07018155D752FE66AA4C108F3C62A729F15DD2CE`. The sole retained packaged process was PID `54152`, started `2026-08-26T14:01:26.6789620Z`, and exited naturally `0` after `4.1829764` seconds. Timeout, exact-PID stop, retry, and cleanup were not used; the process drained.

## Activation chain

| Stage | Count | First line | Result |
| --- | ---: | ---: | --- |
| FLAG_ACCEPTED | 1 | 843 | MATCH |
| WORLD_CANDIDATE | 2 | 892 | exact target and non-target membership MATCH |
| WORLD_BOUND | 1 | 911 | MATCH |
| BEGIN_PLAY | 1 | 940 | MATCH |
| NEXT_TICK_DISPATCHED | 1 | 950 | MATCH |
| START | 1 | 951 | MATCH |
| FIELD | 184 | 1082 | MATCH |
| RESULT | 1 | 1266 | MATCH |

The first world candidate was `/Temp/Untitled_0`, `target=false`, `claimed=false`. The exact target row was `/Game/Maps/SundaleGraybox`, `target=true`, `claimed=false`, before WORLD_BOUND. The target count was `1`, non-target count `1`, malformed and duplicate-target counts `0`. Sundale map completion occurred once. Activation and packaged-source execution therefore pass independently of the later policy result.

## Policy result

The exact RESULT is `POLICY_FAIL` with `fields_expected=184`, `fields_emitted=184`, `matches=174`, `mismatches=1`, and `gaps=9`. Registry/control aggregation is `173 / 168 / 0 / 5`; runtime is `10 / 5 / 1 / 4`; policy metadata is `1 / 1 / 0 / 0`.

The sole reliable mismatch is:

| Kind | Name | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| RUNTIME | `rhi_name` | `D3D12` | `D3D12 (SM6)` | MISMATCH |

The ordered unavailable gaps are `r.MegaLights.FrontLayerTranslucency.Allow`, `r.MegaLights.FrontLayerTranslucency.SpecularOnly`, `r.MegaLights.FrontLayerTranslucency.SoftShadows`, `r.MegaLights.FrontLayerTranslucency.TexturedRectLights`, `r.MegaLights.Spatial.UseHistorySpatialVariance`, `viewport_size`, `d3d_feature_level_12_0`, `shader_model_6_6`, and `native_tsr_identity`. The exact mismatch controls `PACKAGED_POLICY_FAIL / RHI_NAME_EXACT_VALUE_MISMATCH`; it is not hidden by the unavailable fields.

## Evidence custody

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `Evidence/CandidateBActivation.log` | 146,700 | `4C94B9FE42B1016C24DE26F357857385037A49A4A5EE66D0F20DEB85704B1546` |
| `Evidence/session_custody.tsv` | 6,176 | `8E3FE42CED7C15769560739063F2C69507887F8A2FC5833FFFC7384BE5649CD0` |
| `Evidence/marker_ledger.tsv` | 1,316 | `35FF87EE0BB45E1CD3434B580896EBF20B295B2701AAB4716566FCF0839564BD` |
| `Evidence/field_ledger.tsv` | 11,123 | `053026ACA2C1976B851B7FD435FA8B6133D2A639FB58F6FC5DB3B64504D09AEC` |

The session has exactly `155` unique ordered rows; the marker ledger has exact eight ordered MATCH rows; the field ledger has exact `184` rows in source order with kind counts `165/8/10/1`. All TSVs are strict UTF-8 without BOM, LF/final LF, and replayed byte-exactly. The immutable log is strict UTF-8 with BOM and NUL count `0`, stable twice over `13.9594358` seconds, and complete through process drain. Candidate argument echoes count `2`, map completion `1`, RequestExit `1`, fatal `0`, and security `0`.

## Credits and boundary

`activation_credit=1`; `packaged_candidate_source_execution_credit=1`; `package_launch_credit=1`. `policy_application_credit=0`; `policy_full_validation_credit=0`; route and OS-visible-client credits are `0`. Current gameplay, broad-product, renderer, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, validation, and readiness credits remain `0`. Activation is `PASS`; policy and runtime-feature components are `FAIL`; route is `NOT_RUN`; broad product and OS-visible client are `NOT_MEASURED`. Candidate B remains provisional/unvalidated.

Phase 1L.5bc is truth-repaired to full commit `f6eb506bd6635c142fbcafa6c48b79088972bf90`, independently verified exactly two canonical Project upserts and August 26 nightly count `3/6`. Its report is `Oddswell/Development/Reports/Phase 1L5bc Candidate B Exact World Package Correction Receipt Backed Two Layer Skip Build Package Proof.md`, `6,594` bytes, SHA `A7FC9AAA626FD0F6B11AA717D208655CE504E1581A1DB5C15FFF396CBC8FC798`, blob `a6b55d5a8119512658a8101a0d641e4c5e920210`. Its package credits remain prior-only.

No route/gameplay/performance execution, broad product measurement, full policy validation, product or security defect, Defender-clean state, rerun, rebuild, repackage, cleanup, Tasks mutation, Cursor artifact, or automatic successor is claimed.

AUGUST 26 NIGHTLY BATCH PHASE 4/6 CLOSED — NO AUTOMATIC PHASE 5
