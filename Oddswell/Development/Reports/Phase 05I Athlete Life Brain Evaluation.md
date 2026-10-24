---
tags:
  - phase-05i
  - athlete-life
  - evaluation
status: complete
date: 2026-07-16
---

# Phase 0.5I: Athlete Life Brain Evaluation

## Outcome

Phase 0.5I adds a read-only, standard-library evaluator for the fixed four-season Athlete Life Brain archive. It measures choice distribution, policy compliance, roster tenure, temporary readiness exposure, fatigue/recovery changes, and a fixed-seed zero-readiness sensitivity comparison. It changes no policy, probability, schema, gameplay rule, or Admin Console behavior. Cost: **$0.00**.

## Fixed archive evidence

| Evidence | Result |
| --- | ---: |
| Seasons / games | 4 / 80 |
| Reconstructed archived games | 80 / 80 |
| Life choices | 912 / 912 expected |
| Policy violations | 0 |
| Roster-tenure violations | 0 |
| Rest | 386 (42.32%) |
| Socialize | 252 (27.63%) |
| Train | 251 (27.52%) |
| Recover | 23 (2.52%) |
| Readiness exposures | 503 (55.15%) |
| Mean readiness / active mean / maximum | 0.6891% / 1.2495% / 1.5% |
| Net fatigue change from choices | -4.04 |
| Recovery days removed | 23 |

Roman Voss has **57** choices across Seasons 1-3 and none after retirement. Soren Lake has **19** choices in Season 4 and none before his debut.

## Fixed-seed sensitivity

The evaluator replays the same 80 matchups, seeds, pregame fatigue, and availability twice: once with archived readiness and once with readiness set to zero. Archived readiness changed the replayed sample by **+1.4125 points per team-game**, **+0.6654 field-goal percentage points**, and **-0.275 turnovers per team-game**. It produced **22/80 winner flips** and a **6.275-point mean absolute change in game margin**.

These are path-sensitive simulator effects, not real-world estimates. A `+1.5%` or `+1.0%` readiness value is an absolute internal probability-point adjustment, not a relative improvement in athlete ability.

## Interpretation boundary

- Rest is the largest choice because the explicit fatigue threshold routes athletes there.
- Training and socializing are nearly equal because the v1 policy alternates them by stable context; this does not demonstrate intelligence or personality.
- The zero-readiness comparison measures the current mechanic's influence on this fictional fixed-seed archive. It does not prove realism, predictive power, causality outside the simulator, or learned behavior.
- No traits, long-term memory, narrative events, LLM calls, training, retraining, economy, credits, wagering, or monetization were added.

## Validation

The focused evaluator test locks archive size, exact choice counts, policy and tenure compliance, complete replay reconstruction, readiness bounds, and retirement/debut choice history. The full regression suite and Admin Console self-check pass before the phase commit.

## Next gate

Phase 0.5J should review the v1 policy against this evidence and define the smallest fictional trait input that can produce testable athlete differences without changing durable ratings or adding an LLM.
