# Phase 1L.5ap — Candidate B World-Candidate Activation Diagnostic Source Authoring

Status: `COMPLETE LOCALLY — WORLD_CANDIDATE_DIAGNOSTIC_SOURCE_AUTHORED; BUILD AND RUNTIME NOT RUN; FRESH BATCH PHASE 2/6`

## Authority and boundary

Phase 1L.5ao observed Candidate flag acceptance and Sundale map-load completion but no world-bound or later Candidate marker; that result is an evidence gap, not a defect. This phase authors the smallest Development-only source diagnostic at the next relevant callback seam. It performs no build, automation, package, launch, runtime test, Defender action, product measurement, or roadmap expansion.

Phase 1L.5ao is truth-repaired to full commit `59f0d864a4332812dcf9077a229d8d2ea6f8b7fc`, with independently verified exactly two canonical Project upserts and count `1/6`.

## Selection

- A `ONE_WORLD_CANDIDATE_MARKER_BEFORE_EXISTING_GUARD` is `SELECTED`/recommended: emit one existing-category Display diagnostic for every game-world callback before exact-target/claim rejection.
- B `MULTI_SITE_MODULE_ENGINE_INSTRUMENTATION` is `NOT_SELECTED`/rejected because it expands mutation and evidence surfaces without first testing the bounded seam.
- C `UNCHANGED_RERUN` is `NOT_SELECTED`/rejected because the prior evidence cannot distinguish callback absence from non-target or already-claimed rejection.

## Exact source delta

Only `client/OddsWell/Source/OddsWell/CandidateBPolicySmoke.cpp` changed. The compound opening rejection in `OddsWellCandidateBPolicySmoke::BindToWorld` is split so null or non-game worlds still return first. For a game world, source captures `WorldPackageName`, computes `bIsTargetWorld` once with the unchanged exact case-sensitive Sundale predicate, and emits exactly one:

`ODDSWELL_CANDIDATE_B_POLICY_SMOKE|stage=WORLD_CANDIDATE|schema=1|package=%s|target=%s|claimed=%s`

The package uses existing `EscapeMarkerValue`; target and claimed values are lowercase `true`/`false`. The unchanged target-or-claimed return follows the marker. Existing claim assignment, weak BeginPlay binding, next-tick dispatch, policy smoke, and `WORLD_BOUND` marker retain their order and text. No include, helper, state, callback, timer, dependency, setting, log category, flag, header, test file, module file, config, or map was added or changed.

## Static audit

The source delta is `16` insertions and `1` deletion. Post identity is `32,586` bytes, SHA `9365824C3C75D65DA3D98D5C012EAB6A256F575C18B2358F1ACF5FBAE00AE4AD`, blob `340601c114e4674c6b776deddf24e8a715f8b662`. The new full format, stage, escape call, target boolean, claimed boolean, target computation, and target/claim guard each occur exactly once.

Static order is first null/game-world guard at line `629`, package capture and target computation at `634–635`, marker format at `639`, target/claim guard at `644`, claim assignment at `649`, then `WORLD_BOUND` at `666`. Existing `FLAG_ACCEPTED`, `WORLD_BOUND`, `BEGIN_PLAY`, `NEXT_TICK_DISPATCHED`, `START`, `FIELD` emitter, `RESULT`, claim assignment, and `RequestExit(false)` counts remain one each at their respective module/source surfaces. The outer `UE_BUILD_DEVELOPMENT` guard, three existing automation-test blocks, and exact empty/Bootstrap/Sundale target-predicate tests remain intact. Diff check is clear; protected module, config, and map identities are unchanged.

## Credits and nonclaims

`world_candidate_diagnostic_source_authoring_credit=1`. Current compile, build, automation, package, launch, runtime activation, policy application, renderer, window, route, gameplay, performance, minimum-PC, compatibility, accessibility, hands-on, beta-exit, Brain, readiness, and broad-product credits are `0`. Product is `NOT_MEASURED`; Candidate B remains provisional/unvalidated. The source marker does not prove callback arrival, activation, policy application, or a causal failure. No source-compile, runtime, product, defect, security, Defender-clean, or readiness claim is made.

FRESH BATCH PHASE 2/6 CLOSED — NO AUTOMATIC PHASE 3
