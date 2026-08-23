# Phase 1L.5ao — Corrected Packaged Candidate B Activation and Policy Evidence

Status: `COMPLETE LOCALLY — PACKAGED_ACTIVATION_EVIDENCE_LIMITED; TIMEOUT_AFTER_FLAG_ACCEPTED_BEFORE_WORLD_BOUND; BROAD PRODUCT NOT MEASURED; FRESH BATCH PHASE 1/6`

## Scope and authority

This phase performed one bounded direct launch of the already proven Phase 1L.5an Development package to observe corrected exact-Sundale Candidate B activation and the frozen `184`-field policy harness. It did not build, package, edit source/config/maps, run route or gameplay flags, simulate input, query or change Defender, measure performance, or authorize Phase 1M, roadmap Phase 2, Version 1, or beta exit. Candidate B remains provisional and unvalidated.

Phase 1L.5an closed the prior six-phase batch at full commit `71e8e2d9c14fb802bd6e75d4ae75cc5db672fe1f`; its exactly twelve canonical Project entries were independently verified. Its package proof and credits remain prior-only.

## Attempt and terminal disposition

The sole raw-argument launch used the exact `9`-token, `215`-byte argument string with SHA `90E4DD5F1E46D3164F99D5F60E93907294CCAD2C84C1E0F49408418EE26F30A4`. Retained PID `25160` started at `2026-08-23T04:21:10.9065051Z`. At the `120`-second cap its exact PID/path/start identity was revalidated, that PID alone was stopped, and process drain was observed. Elapsed time was `120.4311477 s`; natural exit was `false`, post-forced-stop exit code was `-1`, cleanup was limited to `EXACT_RETAINED_PID_ONLY`, and retry remained forbidden.

The terminal outcome is `PACKAGED_ACTIVATION_EVIDENCE_LIMITED`; qualifier `TIMEOUT_AFTER_FLAG_ACCEPTED_BEFORE_WORLD_BOUND`. This is an evidence boundary, not a causal failure location or product/source defect.

## Immutable exact-four evidence

| artifact | bytes | SHA-256 | custody |
|---|---:|---|---|
| `CandidateBActivation.log` | 97,623 | `FD19A5086E94DC8C8F23171885685ECCBD0D18F282B511D030A2309DA27B6B07` | process-created, immutable |
| `session_custody.tsv` | 4,523 | `888ABFA61C509824D29B22C736B8E44590757645565C58BB9AC4858BA5C2B614` | exact 126 ordered rows |
| `marker_ledger.tsv` | 353 | `C79E6C669D61EF125570476BC9581D900AF0D248D1DFF8643BAF0D11735783A1` | exact seven marker rows |
| `field_ledger.tsv` | 66 | `FEB49659C06C62C27C378C0CABEC67E0650DAA918F7D362336685FEA405AF917` | exact header, zero data rows |

The log remained byte/hash/mtime-identical after two strict-UTF-8 stable observations separated by `276.9352316 s`. It contains a BOM, no NUL, `1012` CRLF records, `2` bare LF records, no bare CR, and a final CRLF. Exact-four postwrite replay mismatch is `0`.

## Activation boundary

| ordinal | stage | expected | actual | first line | status |
|---:|---|---:|---:|---:|---|
| 1 | `FLAG_ACCEPTED` | 1 | 1 | 843 | `MATCH` |
| 2 | `WORLD_BOUND` | 1 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 3 | `BEGIN_PLAY` | 1 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 4 | `NEXT_TICK_DISPATCHED` | 1 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 5 | `START` | 1 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 6 | `FIELD` | 184 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |
| 7 | `RESULT` | 1 | 0 | `NOT_AVAILABLE` | `NOT_OBSERVED` |

Candidate argument echoes are exactly `2`, Sundale map-load completion is exactly `1`, and the project request-exit marker is `0`. Map-load completion occurred in the retained log but does not identify the claimed world or establish why `WORLD_BOUND` was not observed. With no `START`, `FIELD`, or `RESULT`, no field parsing or policy comparison was available; the field ledger therefore truthfully has zero data rows.

## Custody and nonclaims

The source Candidate/module hashes remain `45C98916986422AB7AD55A83CA882D344AE2C4076E171AB698024C58FC0960F0` and `D7F7EE196395CA9500B5EA50B8ADAC2BEB010972A08FAEACE6DE1536FE5FE778`. Repository HEAD stayed `71e8e2d9c14fb802bd6e75d4ae75cc5db672fe1f` and clean. The package stayed unchanged at `50` files / `1,052,104,364` bytes with manifest SHA `510E795A170243B979D99317367B5EC040384B90C70167D134DD6F1ACC636180`; the game-created Profile contains `5` files. Target-process residue, unreadable watched processes, retained-PID TCP/UDP residue, and TCP/UDP cells for `17777`, `1985`, and `7810` are all `0`.

Activation and policy-application components are `INDETERMINATE`; route is `NOT_RUN`; broad product is `NOT_MEASURED`. `activation_credit=0`, `packaged_candidate_source_execution_credit=0`, `policy_application_credit=0`, `route_credit=0`, `package_launch_credit=0`, and `policy_full_validation_credit=0`. No runtime policy pass/fail, product, renderer, window, route, gameplay, economy, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, security, Defender-clean, or readiness claim is made. Fatal and security marker counts are `0`, which is only a scan result. No retry, broad cleanup, source/config/package mutation, or automatic successor is authorized.

FRESH BATCH PHASE 1/6 CLOSED — NO AUTOMATIC PHASE 2
