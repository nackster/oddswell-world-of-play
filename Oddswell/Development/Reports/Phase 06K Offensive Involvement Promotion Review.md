---
tags:
  - development
  - phase-06k
  - athlete-performance
  - offensive-involvement
  - promotion-review
status: complete
date: 2026-07-17
---

# Phase 0.6K: Offensive Involvement Promotion Review

## Decision

Approve `offensive-involvement-v1` for a **separate controlled rollout**. The feature remains opt-in during this review. No runtime, default, schema, parameter, rating, prediction, replay, or Admin behavior changed.

The approval is narrow: the frozen `0.85`/`1.00`/`1.15` weights may redistribute only initial-ballhandler and pass-target opportunity in the baseline Basketball Brain. The truthful scope remains **OPPORTUNITY ONLY**. This does not establish ideal real-world usage, coaching intelligence, confidence, personality, learning, or a player-quality improvement.

## Evidence reviewed

- Phase 0.6I ran 600 Jalen Cross pilot games and 200 omitted controls. Selection opportunity was strictly ordered, every replay and manifest verified, and no involvement field entered the shot formula.
- Phase 0.6J preregistered three distinct controls before measurement: high-passing Micah Vale, lower-rated scorer Cal Brooks, and Jalen. Across 1,800 pilot games and 600 omitted controls, all opportunity, shooting-efficiency, possession, talent, replay, manifest, and formula gates passed.
- Low opportunity was 9.95%-12.17% below standard and featured was 8.89%-11.71% above standard. Field-goal percentage spreads were 0.54-0.98 percentage points and team-possession spreads were 0.220-0.495.
- Cal's featured field-goal percentage remained 39.54%, below Jalen's 44.02% standard control. More opportunity did not erase their frozen shooting-rating difference.
- Score changes ranged from 117/200 to 156/200 and winner changes from 38/200 to 51/200 across the six non-standard comparisons. This is material path sensitivity and must remain visible; it is not evidence that a tier is better.
- Both controlled selection paths respond. Initial possessions and pass targets move in the intended direction for Micah, Cal, and Jalen.

## Saturation and role limits

The resolver has no correction cap or hidden clipping. The nominal 15% weight changes become smaller realized opportunity changes because each athlete competes with teammates in weighted selection. That dilution is expected, not proof of a calibrated real-world usage distribution.

The reviewed roles are sufficient for an engineering rollout decision, not a realism claim. A creator, a lower-rated scorer, and the original higher-rated control passed; defenders, rebound specialists, reserves, retired athletes, replacement athletes, and custom decision policies were not separately calibrated. The current simulator intentionally rejects offensive involvement with a custom decision policy, so the rollout may activate it only for the authoritative baseline Basketball Brain.

## Integration blockers that the rollout must close

1. The authoritative league does not accept an involvement version or snapshot.
2. `SeasonGame` and state schema v5 do not persist involvement evidence. Existing v5 history must load as explicitly disabled history under a new schema.
3. League replay manifests and archived Game Theater reconstruction do not bind or reuse an involvement snapshot.
4. The current prediction study and Admin league do not share an involvement version/snapshot.
5. The Admin live simulation, league, prediction, profile, and archive surfaces still correctly report the pilot as opt-in.
6. No complete production roster tier snapshot exists, including the Roman Voss to Soren Lake transition.
7. Omission is currently the rollback path; the rollout needs one named v1/disabled default switch without changing the frozen weights.

These are rollout tasks, not permission to redesign the resolver.

## Frozen controlled-rollout contract

- Add exactly one explicit default switch between `offensive-involvement-v1` and disabled. V1 may become the default only after every condition below passes.
- Freeze a complete athlete-name/tier/weight snapshot before running rollout evidence. Every active matchup athlete must appear exactly once, including the Season 4 replacement path. Do not infer or tune tiers from rollout results.
- Keep the weights exactly `low = 0.85`, `standard = 1.00`, and `featured = 1.15`.
- Persist the exact version and full snapshot in a new league-state schema. Safely load v5 games as involvement-disabled history.
- Bind the version and snapshot into each new replay manifest. Stored v1 games must reconstruct from their stored snapshot even after rollback.
- Make the current authoritative league, current prediction study, Admin live simulation, athlete profiles, and archived playback agree on the same version. Historical Phase 0D.4 and frozen life-policy evidence must remain explicitly disabled and immutable.
- Keep custom decision-policy/LLM paths disabled for involvement until separately evaluated; do not widen the baseline-only pilot contract during rollout.
- Keep the Admin label **OPPORTUNITY ONLY**. It may say `ACTIVE DEFAULT` only after all integration checks pass.
- Do not change ratings, action weights after possession starts, shot probability, minutes, Consistency v2, Athlete Life behavior, career development, or the three involvement parameters.
- Re-run focused involvement, league persistence/replay, prediction agreement, archive reconstruction, historical digest, full regression, Admin self-check, and rollback checks.

## Stop conditions

Stop without promotion if any complete roster snapshot is missing or changes after evidence begins; v5 migration changes an old replay; stored v1 history cannot replay after rollback; league and prediction versions differ; archived playback differs from stored evidence; historical predictions or life-policy digests move; the shot formula gains an involvement input; custom policies are silently enabled; any frozen weight changes; Admin labels exceed `OPPORTUNITY ONLY`; or the one-switch rollback fails.

## One-switch rollback

Change the single default constant from v1 to disabled and restart. This must affect new games only. Previously stored v1 seasons keep their version and exact snapshot and must continue to replay without reinterpretation. Historical v5 and earlier evidence remains disabled.

## Validation

- Re-inspected the Phase 0.6H selection contract and the complete Phase 0.6I-0.6J paired-seed evidence.
- Traced the simulator selection paths, league transition, v5 persistence loader, prediction study, Admin league/live/archive paths, and replay-manifest boundary.
- 3/3 focused Offensive Involvement tests pass.
- All 62 simulator, league, prediction, career, life-policy, consistency, and involvement regressions pass.
- Admin Console self-check passes.
- The affected roadmap canvas parses with unique identifiers and valid edge endpoints; repository whitespace validation passes.
- External cost: **$0.00**.

## Next gate

Phase 0.6L: a **controlled Offensive Involvement rollout**. Implement only the frozen contract above and stop without promotion if any integration, history, labeling, or one-switch rollback condition fails.
