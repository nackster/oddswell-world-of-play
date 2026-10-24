---
tags:
  - development
  - phase-06b
  - athlete-performance
  - consistency
  - calibration
status: complete
date: 2026-07-17
---

# Phase 0.6B: Athlete Game Consistency Calibration

## Result

`athlete-consistency-v1` is **not eligible for rollout**. The pilot preserves mean talent, team balance, and exact replay, but it does not materially reduce bad nights or raise the performance floor for an elite-consistency athlete.

The factor remains explicit and opt-in. The authoritative league, Athlete Life Brain v4, Admin archive, predictions, and historical replay evidence remain unchanged. Cost: **$0.00**.

## Controlled comparison

Tariq Stone's ratings, role, team, matchup, decision policy, and healthy/rested state remain identical. Only his consistency tier changes. Every other athlete receives zero game form.

Each tier uses the same 1,000 seeds, equivalent to fifty 20-game seasons of healthy-game evidence:

- 1,000 volatile games and 1,000 exact replays.
- 1,000 normal games and 1,000 exact replays.
- 1,000 steady games and 1,000 exact replays.
- 1,000 elite games and 1,000 exact replays.

This removes talent, role, usage, fatigue, injury, and Life Brain differences from the tier comparison.

## Evidence

| Tier | Mean points | Point deviation | Games below 14 points | 20th-percentile floor | Team win rate |
|---|---:|---:|---:|---:|---:|
| Volatile | 18.978 | 6.3590 | 19.3% | 14 | 49.5% |
| Normal | 18.982 | 6.3476 | 19.1% | 14 | 49.3% |
| Steady | 18.936 | 6.2973 | 19.3% | 14 | 50.0% |
| Elite | 18.993 | 6.3128 | 19.2% | 14 | 50.1% |

Replay violations: **0/4,000**.

## Gate result

Passed:

- Mean talent remains within the frozen 0.5-point band across every tier.
- Team win-rate spread is 0.8 percentage points, below the 5-point balance ceiling.
- Every game replays exactly.

Failed:

- Elite point deviation is only 0.73% lower than volatile, not the required 10%.
- Elite bad-night rate is 19.2% versus volatile's 19.3%, not the required 20% relative reduction.
- Elite and volatile 20th-percentile floors are both 14 points; the required one-point improvement is absent.

## Decision

Do not roll out or promote the current pilot. A small zero-centered game-level probability modifier is drowned out by possession selection, shot attempts, and individual outcome randomness. Increasing its magnitude without redesign would be unsafe because the Phase 0.6A pilot already changed 12/80 winners.

This negative result is useful: it prevents a cosmetic consistency label from being mistaken for real simulator behavior.

## Validation

- Full regression suite: **54/54 passed** in 121.266 seconds.
- The calibration is deterministic and its 100-game evidence lock runs twice identically.
- Admin Console self-check remains **passed**.
- Both affected clean canvases parse as valid JSON with unique identifiers and valid edge endpoints; repository whitespace checks pass.

## Next gate

Phase 0.6C design-only **Consistency Resolver Redesign Review**. Define the smallest replayable mechanism that narrows a high-consistency athlete's within-game result variance while preserving ratings, mean performance, usage, team balance, historical evidence, and bad-night possibility. Prefer bounded expected-execution tracking over a larger probability bonus. Do not implement or promote a replacement until that contract is frozen.
