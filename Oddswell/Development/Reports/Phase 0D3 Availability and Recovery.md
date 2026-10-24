---
tags:
  - development
  - simulation
  - season
  - fatigue
  - availability
  - injuries
status: complete
---

# Phase 0D.3 Availability and Recovery

Deterministic **3-season** run using state schema `oddswell-league-state-v3`, league `phase0d3-v1`, engine `phase0d3-v1`, fatigue model `minutes-workload-v1`, injury model `minor-availability-v1`, and brain `baseline-v2`.

## Season summary

| Season | Seeds | Leader | Record | New injuries | Missed player-games | Replay hashes |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | 13100-13119 | Harbor City Waves | 11-9 | 3 | 7 | 20/20 |
| 2 | 13120-13139 | Mesa Vista Sol | 14-6 | 5 | 10 | 20/20 |
| 3 | 13140-13159 | Harbor City Waves | 13-7 | 2 | 3 | 20/20 |

## Fixed-seed realism guardrails

- **10** new minor injuries across **700** active player-games (**1.43%**). The per-player ceiling is **4%**.
- High-workload player-games above 36 minutes: **9/600** (**1.50%**); lower workload: **1/100** (**1.00%**).
- Unavailable players missed **20** player-games; **20/20** recorded zero minutes.
- Every team retained at least **5** available players. The longest assigned recovery was **7 days**.

## Persistence gate

- JSON stores pregame and postgame availability, recovery days, minutes, fatigue, seeds, and replay hashes.
- Save, load, and resume use the same deterministic simulation path.
- Replay evidence binds the injury-model version, minutes, and pregame/postgame availability.

## Availability model

- Only players who logged minutes can receive a new postgame injury.
- Injury risk rises with authoritative minutes and pregame fatigue, then clamps at 4%.
- Recovery durations are 2, 3, 5, or 7 days and decrease by scheduled rest days.
- Unavailable players are excluded from lineups. The six-player prototype suppresses another injury at five available players.

## Scope

In-game injuries, diagnoses, limited/questionable status, permanent injuries, treatment choices, off-court injuries, credits, wagers, paid model calls, and retraining are outside this gate.

The probabilities are provisional engineering calibration values, not medical claims.
