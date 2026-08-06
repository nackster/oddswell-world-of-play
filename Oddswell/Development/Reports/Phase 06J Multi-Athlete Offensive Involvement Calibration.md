---
tags:
  - development
  - phase-06j
  - athlete-performance
  - offensive-involvement
  - calibration
status: complete
date: 2026-07-17
---

# Phase 0.6J: Multi-Athlete Offensive Involvement Calibration

## Preregistered review contract

This is a read-only calibration of the committed `offensive-involvement-v1` opt-in pilot. Runtime behavior, authoritative league defaults, prediction behavior, state schema, ratings, minutes, Consistency v2, Athlete Life decisions, career progression, tier names, and the frozen `0.85`/`1.00`/`1.15` weights may not change during this phase.

The review uses 200 paired seeds per tier (`77000`-`77199`) for exactly three athletes:

- **Micah Vale**, the high-passing creator control: 72 shooting, 86 passing.
- **Cal Brooks**, the lower-rated scorer control: 70 shooting, 63 passing.
- **Jalen Cross**, the original Phase 0.6I control: 84 shooting, 78 passing.

All other athletes remain `standard`. Each athlete keeps the same matchup, ratings, circumstances, active shooting-only Consistency v2 settings, and seed under low, standard, and featured.

### Frozen pass/fail gates

1. For every athlete, mean selection opportunity must be strictly ordered `low < standard < featured`.
2. For every athlete, low must be 5%-20% below standard and featured must be 5%-20% above standard. This bounds the effect without claiming an ideal real-world rate.
3. Each athlete's field-goal percentage spread across tiers must be no greater than 3 percentage points.
4. Each athlete's mean team-possession spread across tiers must be no greater than 2 possessions.
5. Cal's featured field-goal percentage must remain below Jalen's standard field-goal percentage; opportunity may not erase their frozen shooting-rating difference.
6. Every opt-in game and omitted control must replay exactly. Every pilot manifest must verify, the stored snapshot tamper check must fail verification, and shot-formula violations must remain zero.
7. Score and winner changes must be reported for both non-standard tiers even though they are not promotion-quality metrics.
8. The authoritative league must remain snapshot-free and Admin must continue to say `OPT-IN PILOT` and `OPPORTUNITY ONLY`.

Passing every gate permits only a separate promotion review. It does not authorize rollout, roster-wide tier assignment, parameter tuning, a schema change, or a realism, intelligence, learning, coaching, personality, or confidence claim. Any failure keeps the feature opt-in and sends the failed boundary back to design.

## Results

All frozen gates pass. The same three weights create ordered, bounded selection-opportunity changes across all three athlete roles without changing the shot formula or erasing the frozen shooting-rating difference.

| Athlete | Tier | Opportunity | vs standard | Shot attempts | FG% | Points | Team possessions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Micah Vale | Low | 23.900 | -11.00% | 15.780 | 39.16% | 13.640 | 103.385 |
| Micah Vale | Standard | 26.855 | — | 17.600 | 40.14% | 15.540 | 103.165 |
| Micah Vale | Featured | 30.000 | +11.71% | 19.510 | 40.11% | 17.220 | 103.385 |
| Cal Brooks | Low | 21.335 | -12.17% | 18.315 | 40.08% | 15.990 | 103.110 |
| Cal Brooks | Standard | 24.290 | — | 20.480 | 39.55% | 17.575 | 103.165 |
| Cal Brooks | Featured | 26.750 | +10.13% | 22.380 | 39.54% | 19.185 | 103.440 |
| Jalen Cross | Low | 26.245 | -9.95% | 19.460 | 43.68% | 19.075 | 103.660 |
| Jalen Cross | Standard | 29.145 | — | 21.685 | 44.02% | 21.450 | 103.165 |
| Jalen Cross | Featured | 31.735 | +8.89% | 23.350 | 43.32% | 22.860 | 103.220 |

Micah's opportunity is composed of 17.785/20.035/22.550 initial possessions and 6.115/6.820/7.450 pass targets. Cal records 14.690/16.940/18.850 initial possessions and 6.645/7.350/7.900 pass targets. Jalen records 18.540/20.900/23.015 initial possessions and 7.705/8.245/8.720 pass targets. Both selection paths therefore move in the intended direction; the pilot does not silently depend on only one path.

### Frozen-gate evaluation

| Gate | Evidence | Result |
| --- | --- | --- |
| Ordered opportunity | Low < standard < featured for Micah, Cal, and Jalen | Pass |
| Bounded opportunity | Low is 9.95%-12.17% below; featured is 8.89%-11.71% above | Pass |
| Stable FG% | Tier spreads are 0.98, 0.54, and 0.70 percentage points | Pass |
| Stable team possessions | Tier spreads are 0.220, 0.330, and 0.495 | Pass |
| Talent boundary | Cal featured FG% 39.54% < Jalen standard FG% 44.02% | Pass |
| Replay and audit | 1,800/1,800 pilot replays, 600/600 omitted-control checks, 1,800/1,800 manifests, three tamper checks, zero formula violations | Pass |
| Sensitivity visible | All six non-standard score/winner comparisons reported below | Pass |
| Default and Admin boundary | League remains snapshot-free; Admin remains `OPT-IN PILOT` / `OPPORTUNITY ONLY` | Pass |

### Score and winner sensitivity

| Athlete | Low score changes | Low winner changes | Featured score changes | Featured winner changes |
| --- | ---: | ---: | ---: | ---: |
| Micah Vale | 117/200 | 43/200 | 126/200 | 38/200 |
| Cal Brooks | 151/200 | 40/200 | 156/200 | 42/200 |
| Jalen Cross | 146/200 | 51/200 | 146/200 | 43/200 |

These path changes are visible side effects of opportunity redistribution. They do not show that any tier is better, smarter, more accurate, learned, or more realistic.

## Decision

The frozen weights are **eligible for a separate promotion review**. They remain an opt-in pilot. This phase makes no runtime, default, schema, parameter, roster-assignment, prediction, or Admin behavior change.

The multi-athlete evidence supports only the narrow claim that the committed selection weights behave consistently across the reviewed fictional roles while ratings continue to govern shooting efficiency. Three athletes and 200 paired seeds per tier do not establish real-world realism or the correct production distribution of low, standard, and featured roles.

## Validation

- The review contract, athletes, seed window, and numeric gates above were written before measurement.
- 1,800 pilot games and 600 omitted-control checks were measured at external cost **$0.00**.
- 3/3 focused Offensive Involvement tests pass.
- All 62 simulator, league, prediction, career, life-policy, consistency, and involvement regressions pass.
- Admin Console self-check passes.
- Runtime, defaults, schema, tier weights, and implementation are unchanged.
- The affected roadmap canvas parses with unique identifiers and valid edge endpoints; repository whitespace validation passes.

## Next gate

Phase 0.6K: a read-only **Offensive Involvement Promotion Review**. Decide whether the frozen multi-athlete evidence is sufficient for a separately controlled rollout, or retain the opt-in pilot; do not implement a rollout in the review phase.
