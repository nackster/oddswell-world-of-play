---
tags:
  - development
  - phase-06i
  - athlete-performance
  - offensive-involvement
status: complete
date: 2026-07-17
---

# Phase 0.6I: Opt-In Offensive Involvement Pilot

## Result

The bounded `offensive-involvement-v1` pilot passes its frozen engineering gates and is eligible for a separate multi-athlete review. It remains opt-in. The authoritative league default, prediction path, state schema, ratings, minutes, Consistency v2, Athlete Life decisions, and career progression did not change.

The pilot uses only three frozen selection weights: `low = 0.85`, `standard = 1.00`, and `featured = 1.15`. They multiply only the existing initial-ballhandler and pass-target selection weights. Once an athlete has the ball, the legal actions and their weights are unchanged.

## Paired-seed evidence

Jalen Cross kept the same ratings, team, matchup, minutes model, Life Brain boundary, and active shooting-only Consistency v2 settings across 200 paired seeds per tier (`76000`-`76199`).

| Tier | Weight | Initial possessions | Pass targets | Selection opportunities | Shot attempts | FG% | Points | Team possessions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Low | 0.85 | 17.850 | 7.525 | 25.375 | 19.180 | 45.26% | 19.495 | 103.165 |
| Standard | 1.00 | 20.165 | 7.920 | 28.085 | 20.990 | 45.21% | 21.280 | 103.495 |
| Featured | 1.15 | 22.520 | 8.565 | 31.085 | 23.290 | 45.38% | 23.760 | 103.330 |

Selection opportunity is strictly ordered: low is 9.65% below standard and featured is 10.68% above standard. This is opportunity redistribution, not added ability. Field-goal percentage stays nearly level while attempts and points move with opportunity.

## Sensitivity and integrity

- Low versus standard changes 157/200 final scores and 54/200 winners.
- Featured versus standard changes 146/200 final scores and 43/200 winners.
- All 600 opt-in games replay exactly from their action tapes and frozen weight snapshots.
- All 600 replay manifests verify; changing the stored tier/weight snapshot invalidates the seal.
- All 200 omitted-control games replay exactly. An all-standard snapshot preserves the current action tape and score while adding only the explicit pilot audit field.
- Every covered shot retains the existing rating, matchup, fatigue, readiness, and Consistency v2 probability fields. Involvement adds no shot-probability input; formula violations are 0.
- Team possessions, every tier's shot attempts, scoring, score changes, and winner changes are reported above rather than filtered for favorable results.

Winner changes are path sensitivity, not evidence that a tier is better, more accurate, intelligent, learned, or realistic.

## Admin and history boundary

Athlete Profiles and the Basketball Brain status label the feature `OPT-IN PILOT` with `OPPORTUNITY ONLY` scope. No production tier is assigned to the full roster, and the current league does not pass an involvement snapshot.

Omitting the snapshot keeps the current resolver and event log path unchanged. Frozen life-policy digests, v5 consistency history, current predictions, archived replays, and the authoritative Admin league retain their existing behavior.

## Validation

- 3 focused involvement tests pass.
- All 62 simulator, league, prediction, career, life-policy, consistency, and involvement regressions pass.
- Admin Console self-check passes.
- Replay-manifest tamper detection, Python compilation, whitespace validation, and the affected clean canvas validation pass.
- External cost: **$0.00**. No provider, dependency, retraining, deployment, credit, purchase, monetization, or wagering work was added.

## Truth boundary

This is a deterministic fictional opportunity-selection weight. It does not model confidence, personality, mentality, coaching intelligence, neural-network training, learning, or real-world basketball.

## Next gate

Phase 0.6J: a read-only **multi-athlete Offensive Involvement calibration**. Test the frozen weights across at least one high-passing creator, one lower-rated scorer, and Jalen's current control before any promotion review.
