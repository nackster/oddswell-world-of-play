---
tags:
  - development
  - phase-06d
  - athlete-performance
  - consistency
  - evaluation
status: complete
date: 2026-07-17
---

# Phase 0.6D: Opt-In Consistency Resolver v2 Pilot

## Result

`athlete-consistency-v2` passes every frozen Phase 0.6C reliability and integrity gate and is **eligible for a separate promotion review**. It is not promoted and does not run in the authoritative league.

The v2 shooting ledger narrows scoring variance around each athlete's existing rating-based expectation. It does not change ratings, roles, shot selection, career state, Life Brain behavior, persistence, or historical evidence. Cost: **$0.00**.

## Implementation

- One explicit full-roster shooting-consistency input supplies a strength and probability cap for each athlete.
- Volatile, normal, steady, and elite use the frozen `0/0`, `0.15/0.03`, `0.30/0.06`, and `0.50/0.10` strength/cap pairs.
- Each game tracks cumulative unmodified expected shot points and actual shot points per athlete.
- Before a shot, the frozen bounded correction moves the effective probability toward the rating-based expectation.
- Every covered shot records base probability, correction, effective probability, and pre-shot residual.
- The ledger resets each game and reconstructs exactly from the seed, action tape, and opt-in settings.
- V1 game form and v2 shooting consistency cannot run together.
- Omitting v2 preserves the existing game path exactly.

## Frozen evaluation

Each athlete keeps identical ratings, team, matchup, policy, and healthy/rested state across 1,000 games per tier. This produces 8,000 pilot games and 8,000 exact replays.

### Tariq Stone — seeds 70,000-70,999; bad night below 14 points

| Tier | Mean points | Deviation | Bad nights | P20 floor | P90 high | Attempts | Team wins |
|---|---:|---:|---:|---:|---:|---:|---:|
| Volatile | 18.936 | 6.3003 | 19.3% | 14 | 27 | 20.229 | 50.5% |
| Normal | 18.860 | 5.7726 | 17.4% | 14 | 26 | 20.238 | 49.2% |
| Steady | 18.902 | 5.1948 | 14.5% | 15 | 26 | 20.239 | 48.5% |
| Elite | 18.913 | 4.6535 | 11.4% | 15 | 25 | 20.312 | 49.2% |

Elite versus volatile:

- point deviation falls **26.14%**;
- bad nights fall **40.93%** relative;
- the 20th-percentile floor rises one point;
- the 90th-percentile high falls exactly two points, within the frozen ceiling;
- tier means span 0.076 points and attempts span 0.083;
- team win rates span 2.0 percentage points.

### Jalen Cross — seeds 72,000-72,999; bad night below 16 points

| Tier | Mean points | Deviation | Bad nights | P20 floor | P90 high | Attempts | Team wins |
|---|---:|---:|---:|---:|---:|---:|---:|
| Volatile | 20.565 | 6.5109 | 20.7% | 15 | 29 | 20.869 | 50.0% |
| Normal | 20.454 | 5.8913 | 18.8% | 16 | 28 | 20.807 | 48.0% |
| Steady | 20.683 | 5.4864 | 17.0% | 16 | 28 | 20.929 | 49.0% |
| Elite | 20.700 | 5.1161 | 14.8% | 16 | 27 | 20.912 | 50.2% |

Elite versus volatile:

- point deviation falls **21.42%**;
- bad nights fall **28.50%** relative;
- the 20th-percentile floor rises one point;
- the 90th-percentile high falls exactly two points;
- tier means span 0.246 points and attempts span 0.122;
- team win rates span 2.2 percentage points.

## Gate result

Passed for both athletes:

- at least 10% lower elite point deviation;
- at least 20% fewer elite bad nights;
- at least one-point higher elite 20th-percentile floor;
- bad nights remain possible;
- mean points stay within 0.5 across tiers;
- attempts stay within 0.5 across tiers;
- exceptional-game preservation stays within the two-point limit;
- team win-rate spread stays within five percentage points;
- **0/8,000 replay violations**;
- existing league and historical paths remain unchanged.

## Admin and truth boundary

Athlete profiles now identify v2 as an `OPT-IN CANDIDATE` with `SHOOTING ONLY` scope. That label is evidence status, not active league behavior. The interface must not imply that passing, defense, rebounding, confidence, personality, learning, or neural weights are covered.

V2 is deterministic fictional variance control. The two-athlete simulator result is not real-world validation and does not prove generational-player realism.

## Validation

- Focused simulator and consistency suite: **13/13 passed**.
- Full historical regression suite: **56/56 passed** in 118.900 seconds.
- Admin Console self-check: **passed**.
- Frozen calibration: 8,000 games, 8,000 exact replays, and zero failed gates.
- No dependency, model call, paid API, schema, economy, credit, or wagering change.

## Next gate

Phase 0.6E deliberate **Consistency v2 Promotion Review**. Review path sensitivity, audit evidence, rollback, league/prediction integration requirements, and the shooting-only limitation. Do not change the default during that review.
