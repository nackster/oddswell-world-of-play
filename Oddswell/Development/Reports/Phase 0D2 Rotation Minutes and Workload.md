---
tags:
  - development
  - simulation
  - season
  - fatigue
  - rotation
status: complete
---

# Phase 0D.2 Rotation Minutes and Workload

Deterministic rotation gate using league `phase0d2-v1`, engine `phase0d2-v1`, state schema `oddswell-league-state-v2`, fatigue model `minutes-workload-v1`, and brain `baseline-v2`.

## Fixed-seed comparison

Seed `12000` was run normally, repeated, and replayed from its exact action tape. All three results matched.

| Team | Team minutes | Starter average | Reserve | Starter carryover load | Reserve carryover load |
| --- | ---: | ---: | ---: | ---: | ---: |
| Harbor City Waves | 240.0 | 43.16 | Malik Frost: 24.20 | 0.0601 | 0.0343 |
| Mesa Vista Sol | 240.0 | 43.16 | Mateo Cruz: 24.20 | 0.0596 | 0.0338 |

The same-roster full-game counterfactual produced `0.0667` average carryover load. Using actual minutes reduced it to `0.0555` while keeping heavier starter workloads above reserve workloads.

## Rotation model

- Each team has five starters and one reserve.
- Regulation is split into ten deterministic time segments.
- The reserve plays the five alternating segments and rests one different starter in each.
- Overtime uses the five starters.
- Every lineup change is recorded, and every active player receives the exact elapsed possession time.
- In-game fatigue and between-game load now increase only from minutes actually played.

This is the smallest rotation that creates a real minutes difference. Tactical substitutions, foul trouble, player positions, and coach-controlled rotations are deferred until a measured need exists.

## Season evidence

A 20-game run using seeds `12000`-`12019` finished with Harbor City Waves at 11-9 and Mesa Vista Sol at 9-11. All 20 replay manifests verified, and final average carryover fatigue was `0.2962`.

## Replay and persistence gate

- Seeded lineup timing, actions, results, minutes, and fatigue replay exactly.
- Each game persists its player-minute snapshot alongside pregame and postgame fatigue.
- The hashed event log includes lineup changes and final minutes.
- Uninterrupted simulation equals save/load/resume simulation.
- State schema v1 is rejected clearly; prototype migration code is deferred.

## Verification and cost

- All 18 prior Phase 0A-0D.1 tests pass.
- Two focused D.2 tests verify exact rotation replay, team-minute totals, reserve workload, minutes-driven carryover, and persistence.
- **20/20 tests pass.**
- External cost: **$0.00**. No paid API, credits, wagering, purchases, or retraining jobs were used.

## Next gate

Use authoritative D.2 minutes and fatigue to add deterministic availability, minor injuries, and recovery. In-game injury detail and medical simulation remain later work.
