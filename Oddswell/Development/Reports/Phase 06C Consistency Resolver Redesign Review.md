---
tags:
  - development
  - phase-06c
  - athlete-performance
  - consistency
  - design
status: complete
date: 2026-07-17
---

# Phase 0.6C: Consistency Resolver Redesign Review

## Decision

Approve one opt-in `athlete-consistency-v2` design for implementation testing. Replace the ineffective nightly probability spread with a bounded, per-game shooting-execution ledger. Do not change the authoritative league or promote either consistency version during this review.

Ratings still determine expected performance. Consistency controls how closely actual shot points track that rating-based expectation within one game. A superstar therefore requires both rare top-tier ability and elite consistency; consistency alone never adds talent.

## Smallest resolver

For each athlete, the opt-in game stores two temporary values:

- cumulative expected shot points from the unmodified rating, matchup, fatigue, and readiness probability;
- cumulative actual shot points.

Before each shot after the first, the resolver compares those values. Running below expectation produces a bounded positive correction; running above expectation produces a bounded negative correction. The correction changes only that shot's make probability and is recorded with the shot event.

Candidate calculation:

`correction = clamp(((expected_points - actual_points) / 2) * strength, -cap, cap)`

| Tier | Strength | Maximum correction |
|---|---:|---:|
| Volatile | 0.00 | 0 percentage points |
| Normal | 0.15 | 3 percentage points |
| Steady | 0.30 | 6 percentage points |
| Elite | 0.50 | 10 percentage points |

The existing shot-probability floor and ceiling still apply. After the outcome, the ledger adds the unmodified expected points and actual made points. It resets at game end and is reconstructed deterministically during replay.

## Frozen boundaries

- `athlete-consistency-v1` remains available only as blocked historical pilot evidence.
- V2 must be explicit and opt-in; omitting it must reproduce the current game exactly.
- Do not combine v1 game form with v2 correction in the same game.
- Do not change ratings, roles, lineups, ballhandler or shot selection, fatigue, readiness, Life Brain choices, career state, or persistence schemas.
- Record base probability, correction, effective probability, and the pre-shot ledger residual for audit.
- Keep correction bounded so bad games and exceptional games remain possible.
- Start with shooting only. Passing, defense, rebounding, opportunity smoothing, personality, confidence, and cross-game memory wait until this smaller mechanism proves useful.

This narrow scope is deliberate. It tests the scoring-reliability requirement without pretending that defensive specialists or playmakers already receive equivalent consistency behavior.

## Phase 0.6D evidence plan

Use the same seeds and athlete ratings under every tier. Re-run Tariq Stone for direct Phase 0.6B comparison, then repeat the frozen comparison with current leading scorer Jalen Cross. Do not introduce a fabricated 99-rated athlete.

Promotion requires all of the following:

- elite point deviation at least 10% lower than volatile;
- elite bad-night rate at least 20% lower relative to volatile;
- elite 20th-percentile floor at least one point higher;
- elite bad-night rate remains above zero;
- mean points remain within 0.5 points across tiers;
- mean shot attempts remain within 0.5 attempts across tiers;
- elite 90th-percentile scoring is no more than two points below volatile, preserving exceptional games;
- team win-rate spread stays within five percentage points;
- exact replay has zero violations;
- omission reproduces legacy behavior and all historical regressions remain green.

For direct continuity, Tariq's existing fewer-than-14-point bad-night threshold remains frozen. An untouched 1,000-game Jalen control using seeds 72,000-72,999 averaged 20.565 points; 75% is 15.4238, so Jalen's bad night is frozen as fewer than 16 points before v2 exists. It must not be tuned afterward.

Passing these gates makes V2 eligible for a separate review only. It does not authorize rollout.

## Rarity rule

The one elite tier in the twelve-athlete engineering roster remains a calibration fixture, not a production population. At scale, the initial target is that no more than about 1% of established athletes combine elite consistency with top-tier ability. Final rarity belongs to roster-generation and career-balancing work after the resolver itself passes.

## Truth boundary

This is a deterministic variance-control design, not learning, confidence, mentality, personality, neural-network training, or real-world player modeling. Cost: **$0.00**.

## Next gate

Phase 0.6D: implement the opt-in v2 shooting ledger, run the frozen same-athlete comparisons, and stop without promotion if any reliability, talent, usage, balance, replay, or historical-evidence gate fails.
