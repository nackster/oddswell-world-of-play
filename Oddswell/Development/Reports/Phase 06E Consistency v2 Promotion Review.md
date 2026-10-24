---
tags:
  - development
  - phase-06e
  - athlete-performance
  - consistency
  - promotion-review
status: complete
date: 2026-07-17
---

# Phase 0.6E: Consistency v2 Promotion Review

## Decision

Approve `athlete-consistency-v2` for a separate controlled rollout, but do not promote it during this review. Phase 0.6D passed every frozen reliability and integrity gate; the authoritative league continues to omit consistency settings.

The approval is limited to the current shooting-only resolver. It is not approval for passing, defense, rebounding, confidence, personality, learning, or real-world player claims.

## Paired path-sensitivity audit

The volatile control and elite candidate use identical seeds, rosters, ratings, teams, policy, fatigue, readiness, and availability. Only the evaluated athlete's v2 tier changes.

| Athlete | Paired games | Scores changed | Winners changed | Mean team-score difference | Mean athlete-point difference |
|---|---:|---:|---:|---:|---:|
| Tariq Stone | 1,000 | 815 (81.5%) | 231 (23.1%) | 5.7725 | 3.655 |
| Jalen Cross | 1,000 | 816 (81.6%) | 238 (23.8%) | 5.5495 | 3.695 |

This is material outcome sensitivity, not a cosmetic label. It does not invalidate Phase 0.6D because mean talent, attempts, high games, team balance, and replay remained inside their frozen gates. It does require a controlled, reversible rollout rather than an unversioned default change.

## Audit-field review

| Athlete | Covered shots | Nonzero corrections | Cap hits | Mean absolute correction | Maximum | Violations |
|---|---:|---:|---:|---:|---:|---:|
| Tariq Stone | 20,312 | 19,311 (95.07%) | 16,200 (79.76%) | 0.086816 | 0.10 | 0 |
| Jalen Cross | 20,912 | 19,909 (95.20%) | 16,799 (80.33%) | 0.086724 | 0.10 | 0 |

Positive and negative corrections both occur: Tariq records 9,370 positive and 9,941 negative corrections; Jalen records 10,230 positive and 9,679 negative corrections.

The high cap-hit rate is a visible limitation. The candidate behaves largely as a bounded 10-percentage-point correction after the first shot rather than a finely graduated adjustment. Do not retune it during rollout: the untouched Phase 0.6D evidence belongs to these exact parameters. A later version may compare a smoother resolver under new preregistered gates.

## Current integration blocker

The candidate cannot become the league default yet:

- `simulate_scheduled_game` does not pass shooting-consistency settings to the simulator.
- Replay-manifest audit metadata does not bind a consistency version, tier snapshot, or parameters.
- Stored season games do not retain the consistency version needed for future archive reconstruction.
- `run_prediction_study` does not select the same consistency policy as the league transition.
- Admin archived replay reconstruction omits the settings and would not reproduce a v2 season.

The correct response is not to bypass these blockers. Phase 0.6F must satisfy them together.

## Frozen controlled-rollout contract

Phase 0.6F may change the default only after all of these pass:

1. Introduce one explicit default consistency-version constant with `disabled` as the one-switch rollback target.
2. Preserve `athlete-consistency-v1` and all pre-v2 evidence as immutable historical paths.
3. Pass one full-roster v2 tier/parameter snapshot through every authoritative league game.
4. Bind the consistency version and snapshot into the replay manifest.
5. Store enough versioned metadata to reconstruct every v2 archive; use a new state schema and retain safe loading for existing v4 history.
6. Make new prediction studies select the same consistency version as their league games while historical Phase 0D.4 remains explicitly disabled.
7. Make Admin league, prediction, and archived Game Theater paths agree on scores, winners, minutes, and replay hashes.
8. Keep v2 parameters exactly frozen; do not react to the cap-saturation evidence by tuning during rollout.
9. Keep the Admin label `SHOOTING ONLY` and expose the active or disabled state truthfully.
10. Prove full replay, persistence, historical regression, prediction, Admin self-check, and one-constant rollback before promotion.

If any requirement fails, stop with the candidate opt-in and preserve the current authoritative league.

## Rollback

Rollback must change one default constant from v2 to `disabled` and restart the local Admin process. Stored v2 seasons retain their version and must continue to replay with v2 after rollback; rollback affects only newly generated games.

## Validation and truth boundary

- Phase 0.6D's 8,000-game, 8,000-replay evidence remains unchanged.
- The paired audit adds 4,000 read-only game executions with zero audit-field or cap violations.
- Four focused consistency tests, the Admin Console self-check, both clean canvas checks, and whitespace validation pass. Phase 0.6D's unchanged runtime retains its 56/56 full regression result.
- No runtime, default, schema, league, prediction, Admin behavior, model, dependency, paid API, economy, credit, or wagering change occurred.
- Cost: **$0.00**.

This is deterministic fictional scoring-variance control, not intelligence, learning, mentality, confidence, or real-world validation.

## Next gate

Phase 0.6F controlled v2 rollout. Stop without changing the default if league, prediction, persistence, archived replay, historical evidence, truthful Admin labeling, or rollback cannot be satisfied together.
