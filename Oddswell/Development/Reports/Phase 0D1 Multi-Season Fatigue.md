---
tags:
  - development
  - simulation
  - season
  - fatigue
status: complete
---

# Phase 0D.1 Multi-Season Persistence and Fatigue

Deterministic **3-season** run using state schema `oddswell-league-state-v1`, league `phase0d1-v1`, engine `phase0d1-v1`, fatigue model `between-games-v1`, and brain `baseline-v2`.

## Season summary

| Season | Seeds | Leader | Record | Start fatigue | Final fatigue | Replay hashes |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | 11000-11019 | Harbor City Waves | 11-9 | 0.000 | 0.350 | 20/20 |
| 2 | 11020-11039 | Mesa Vista Sol | 11-9 | 0.070 | 0.350 | 20/20 |
| 3 | 11040-11059 | Harbor City Waves | 10-10 | 0.070 | 0.350 | 20/20 |

## Measured progression

- Season 1 average pregame fatigue: **0.000** in game 1, **0.238** in game 10, and **0.310** in game 20.
- Seven offseason rest days reduced the next season's starting average to **0.070**.

## Persistence gate

- JSON stores every season result, standing, replay hash, seed, and player fatigue snapshot.
- Save, load, and resume use the same deterministic simulation path.
- Automated equality tests compare uninterrupted play with save-and-resume play.

## Fatigue model

- Carryover fatigue is bounded at **0.35**.
- Players recover **0.04 per rest day**, with one day between games and seven between seasons.
- Game load uses duration and stamina. Pregame fatigue is passed into the authoritative simulator and replay record.
- The current ten-player prototype has no bench, so every player receives full-game workload.

## Scope

No injuries, credits, wagers, purchases, paid model calls, or retraining jobs are part of this gate.
