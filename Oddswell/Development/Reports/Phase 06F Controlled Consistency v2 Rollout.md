---
tags:
  - development
  - phase-06f
  - athlete-performance
  - consistency
  - controlled-rollout
status: complete
date: 2026-07-17
---

# Phase 0.6F: Controlled Consistency v2 Rollout

## Outcome

`athlete-consistency-v2` is now the default for newly generated authoritative games. The rollout passed every frozen Phase 0.6E stop condition without changing the approved tier parameters.

The active scope remains **SHOOTING ONLY**. Ratings, matchup, fatigue, readiness, and opportunity still define talent and circumstances; v2 only narrows shooting variance around the existing rating-based expectation.

## Versioned integration

- One constant, `DEFAULT_CONSISTENCY_VERSION`, selects v2 for new games. Changing it to `athlete-consistency-disabled` and restarting is the rollback.
- League implementation is `phase06f-v1` and new state uses `oddswell-league-state-v5`.
- Every new v2 game stores its consistency version plus the exact athlete/tier/strength/cap snapshot used for that matchup.
- V2 replay manifests bind the same version and snapshot. Disabled games retain the legacy manifest shape so pre-v2 replay hashes do not change.
- Existing v4 league files load safely as v5 history with consistency explicitly disabled and an empty snapshot.
- The v5 loader accepts the known active 12-athlete roster across the Roman Voss to Soren Lake transition; four-season save/load is exact.

## League, prediction, and Admin agreement

- The authoritative league passes the stored v2 snapshot into every game transition.
- Historical Phase 0D.4 prediction studies default explicitly to disabled consistency.
- The current Admin prediction study explicitly selects the same v2 version as its league archive and verifies winner and replay-hash agreement.
- Live Admin simulations use v2. Athlete profiles show `ACTIVE DEFAULT` and retain the truthful `SHOOTING ONLY` scope.
- Archived Game Theater reconstruction uses each stored game's version and snapshot, so an old v2 season remains replayable after a future rollback.

## Historical boundary

The Phase 0.5 life-policy studies remain pinned to disabled consistency and their canonical evidence stays unchanged. No v1 or pre-v2 result is reinterpreted under v2. No tuning occurred during rollout: volatile `(0.0, 0.0)`, normal `(0.15, 0.03)`, steady `(0.30, 0.06)`, and elite `(0.50, 0.10)` remain frozen.

## Validation

- League and prediction rollout checks: **23/23 passed**.
- Frozen multi-seed life-policy studies: **4/4 passed**, including all historical digest locks.
- Full regression suite: **59/59 passed** in 137.913 seconds.
- Admin Console self-check: passed.
- Python compilation, JSON canvas validation, and whitespace validation: passed before commit.
- External cost: **$0.00**.

This is deterministic fictional scoring-variance control. It is not training, learning, confidence, mentality, personality, intelligence, or real-world validation.

## Rollback

Change `DEFAULT_CONSISTENCY_VERSION` from `athlete-consistency-v2` to `athlete-consistency-disabled`, then restart the local Admin process. The switch affects newly generated games only. Stored v2 seasons keep their snapshots and continue to replay under v2.

## Next gate

Phase 0.6G read-only post-rollout integration review. Recheck a fresh Admin archive, prediction agreement, stored replay reconstruction, v4 migration, historical digests, and rollback evidence before adding another athlete-performance input.
