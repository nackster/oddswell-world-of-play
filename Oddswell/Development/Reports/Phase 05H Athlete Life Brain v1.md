---
tags:
  - phase-05h
  - athlete-life
  - simulation
status: complete
date: 2026-07-15
---

# Phase 0.5H: Athlete Life Brain v1

## Outcome

Phase 0.5H adds the first real Athlete Life Brain loop. The basketball-realism agent directed the smallest truthful scope: one deterministic, versioned between-game choice per active fictional athlete, bounded temporary consequences, exact audit/replay evidence, and no mutation of durable ratings. Cost: **$0.00**.

## Choice policy

- Legal choices are `train`, `rest`, `recover`, and `socialize`.
- An unavailable athlete chooses `recover` and shortens recovery by at most one day.
- An athlete at or above the explicit high-fatigue threshold chooses `rest` and reduces carryover fatigue.
- Other active athletes deterministically alternate `train` and `socialize` using stable game and roster context.
- Retired athletes are not on the active roster and receive no further choices. Incoming athletes begin only in their debut season.

Every decision stores the athlete, upcoming game, exact legal choices, selected choice, policy version, reason, bounded before/after temporary state, and a human-readable effect. Invalid choices and invalid state are rejected.

## Temporary consequence boundary

Training adds a `+1.5%` next-game readiness modifier and `+0.02` bounded workload. Socializing adds a `+1.0%` next-game morale/readiness modifier and `+0.01` bounded workload. Rest reduces fatigue by `0.03`. Recover shortens the active recovery timer by one day.

The direct game modifier is capped below the `±2%` policy ceiling and is consumed by the next game. It affects pass security and shot resolution only for that game. Durable shooting, passing, defense, rebounding, stamina, age, specialty, lifecycle progression, and completed history remain unchanged.

## Measured four-season archive

| Evidence | Result |
| --- | ---: |
| Seasons / games | 4 / 80 |
| Total life choices | 912 |
| Rest | 386 |
| Socialize | 252 |
| Train | 251 |
| Recover | 23 |
| Maximum readiness modifier | 1.5% |
| External cost | $0.00 |

Roman Voss records **57** choices across Seasons 1-3 and none after retirement. Soren Lake records **19** choices in Season 4 and none before his debut.

## Persistence, replay, and Admin Console

Life choices, temporary pregame readiness, and consequences are bound into the internal replay manifest. League save/load/resume reproduces the same choices, consequences, seasons, and replays. The Admin Console marks Athlete Life Brain as `ACTIVE PILOT` and shows each profile's choice count, breakdown, and recent choice → reason → effect timeline.

The browser never receives reconstruction seeds, raw fatigue, readiness values, recovery timers, injury-risk internals, or RNG state.

## Explicit exclusions

There is no LLM call, learning, retraining, model promotion, relationship simulation, nightlife story, legal trouble, contract logic, reputation system, permanent rating change, economy, credit, purchase, prediction, wagering, or settlement behavior in this gate.

## Validation

- Focused tests cover deterministic choices, exact legal-action validation, bounds, unavailable/rest policy, replay equality, save/load/resume equality, retirement/debut history, and durable-rating invariance.
- All **38** regression tests, JavaScript syntax validation, both canvas JSON checks, and the Admin Console self-check pass before the phase commit.
- The implementation adds no dependency or external cost.

## Next gate

Phase 0.5I should measure choice distribution and game impact before any personality traits, long-term memory, narrative events, or LLM policy is added.
