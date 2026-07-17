---
tags:
  - phase-05l
  - athlete-life
  - multi-seed-evaluation
status: complete
date: 2026-07-16
---

# Phase 0.5L: Multi-Seed Life Preference Evaluation

## Outcome

Phase 0.5L adds one read-only standard-library evaluator for the opt-in Athlete Life Brain v2 pilot. It compares v1 and v2 across ten untouched paired seed blocks: `30000 + 80*i`, for `i = 0..9`. Each policy runs four 20-game seasons per block, totaling **800 games** and **9,120 decisions** per policy. Cost: **$0.00**.

All integrity and provisional stability guardrails pass. V2 is **eligible for later review**, not promoted. Default gameplay, v1 history, the state schema, Admin Console, and durable ratings remain unchanged.

## Aggregate policy evidence

| Evidence | v1 | v2 |
| --- | ---: | ---: |
| Games / decisions | 800 / 9,120 | 800 / 9,120 |
| Rest | 3,864 | 3,857 |
| Recover | 199 | 202 |
| Train | 2,598 | 2,406 |
| Socialize | 2,459 | 2,655 |
| Readiness exposures | 5,057 | 5,061 |
| Mean / maximum readiness | 0.6969% / 1.5% | 0.6868% / 1.5% |
| Net choice-fatigue change | -39.37 | -41.04 |
| Injuries / active player-games | 175 / 9,482 | 177 / 9,478 |
| Injury rate | 1.8456% | 1.8675% |
| Missed / scheduled player-games | 118 / 9,600 | 122 / 9,600 |
| Missed-game rate | 1.2292% | 1.2708% |
| Mean team points | 94.8075 | 94.8006 |
| Harbor City win rate | 51.50% | 48.625% |
| Policy / tenure / version violations | 0 / 0 / 0 | 0 / 0 / 0 |

Every inactive athlete records zero minutes, and every team keeps at least five available athletes. V2's overall injury-rate change is **+0.0219 percentage point** and its missed-game-rate change is **+0.0416 percentage point** versus paired v1.

## Preference-adjusted evidence

The practice and social groups contain different fixed athletes, roles, and ratings. Raw group differences are therefore confounded. The evaluator uses difference-in-differences: `(v2 practice - v2 social) - (v1 practice - v1 social)`.

| Metric | V1-adjusted v2 difference | Provisional alarm | Result |
| --- | ---: | ---: | --- |
| Mean pregame fatigue | +0.022788 | 0.03 | Pass |
| Minutes per active player-game | -0.0044 | 2.0 | Pass |
| High-workload share | +0.0289 pp | 5.0 pp | Pass |
| Injury rate | +0.1280 pp | 0.5 pp | Pass |
| Missed-game rate | +0.0833 pp | 0.5 pp | Pass |
| Mean readiness | +0.001478 | 0.0025 | Pass |
| Readiness-exposure share | -9.4736 pp | 10.0 pp | Pass |

Both v2 groups contain exactly **4,560 decisions**. The practice group has zero socialize choices; the social group has zero train choices. The raw v2 injury-rate gap is 0.4431 percentage point and the raw missed-game-rate gap is zero, but adjusted results—not raw gaps—are the appropriate evidence.

## Paired outcome sensitivity

- Sequential actions differ in **3,707/9,120** positions.
- Winners differ in **147/800 games (18.375%)**.
- Mean absolute game-margin difference is **6.4212 points**.
- Mean team scoring changes by **-0.0069 point per game**.
- Harbor City's win rate changes by **-2.875 percentage points**.

These are path-sensitive fictional simulator results, not accuracy, quality, intelligence, real-world realism, or evidence that one preference is better.

## Per-block evidence

| Start seed | Action differences | Winner differences | Margin MAE | Injuries v1 / v2 | Missed v1 / v2 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 30000 | 368 | 15 | 5.7000 | 22 / 22 | 10 / 10 |
| 30080 | 373 | 15 | 7.1625 | 19 / 20 | 13 / 16 |
| 30160 | 395 | 14 | 7.3375 | 14 / 15 | 8 / 9 |
| 30240 | 364 | 12 | 5.7875 | 21 / 21 | 17 / 17 |
| 30320 | 366 | 17 | 6.2250 | 17 / 15 | 12 / 12 |
| 30400 | 376 | 18 | 7.3250 | 14 / 14 | 6 / 6 |
| 30480 | 367 | 13 | 5.8250 | 14 / 16 | 6 / 6 |
| 30560 | 354 | 15 | 5.8375 | 17 / 17 | 21 / 21 |
| 30640 | 370 | 11 | 6.4375 | 19 / 19 | 14 / 14 |
| 30720 | 374 | 17 | 6.5750 | 18 / 18 | 11 / 11 |

## Integrity and scope

- Canonical evaluation SHA-256: `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`.
- Focused runtime on this machine: **46.758 seconds**, under the 60-second ceiling.
- All **42** regression tests completed in **84.274 seconds**, under the 120-second full-suite ceiling; the Admin Console self-check and both clean canvas checks pass.
- Guardrails are provisional engineering stability alarms frozen before the final seed blocks. They are not medical, statistical, or real-world targets.
- No schema, gameplay, default policy, UI, historical archive, LLM, learning, retraining, memory, narrative, economy, credits, wagering, purchase, or monetization behavior changed.

## Next gate

Phase 0.5M should perform a deliberate v2 promotion review. Passing Phase 0.5L makes v2 eligible for review only; it must not become the default automatically.
