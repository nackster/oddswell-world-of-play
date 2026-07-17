---
tags:
  - development
  - phase-05q
  - athlete-life
  - promotion-review
status: complete
date: 2026-07-17
---

# Phase 0.5Q: Athlete Life Brain v3 Promotion Review

## Decision

**Approved for a later controlled rollout. Not promoted in this review.**

Phase 0.5P passed every frozen aggregate integrity and provisional stability gate across ten fresh paired seed blocks. V3 may therefore enter a separate, reversible rollout phase for newly generated state. V2 remains the active default throughout Phase 0.5Q.

This approval covers bounded deterministic simulator behavior only. It is not evidence that v3 learns, is intelligent, is more realistic, represents real people fairly, improves winning, or should control longer-term life outcomes.

Cost: **$0.00**.

## Evidence accepted

- 800 games and 9,120 decisions per policy with zero policy, version, tenure, order, transition, or streak-reconstruction violations.
- 1,208 routine variations across 5,091 eligible choices; practice/social variation rates differ by 1.8220 percentage points.
- Streak magnitude and identical elective-action runs never exceed two.
- V2/v3 injury counts are 164/164; missed-player-game counts are 99/100.
- Team scoring shifts by -0.1031 point per team-game, Harbor City's win rate shifts by +1.0 percentage point, winner disagreement is 130/800, and aggregate margin MAE is 5.8438.
- Phase 0.5P digest remains `eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618`.

## Risks retained

- V2 and v3 differ on 2,899/9,120 actions and 130/800 winners. These are path-sensitive changes, not evidence of better outcomes.
- Seed block `40560` records an 8.3875 margin MAE. The frozen alarm is aggregate, so this is not a failure, but the tail must remain visible.
- The two-plus-one cadence is mechanical, while train and socialize have different temporary consequences.
- Preference-group comparisons remain tied to the current fictional identities despite difference-in-differences checks.
- The evidence does not cover midseason persistence, cross-season memory, narratives, career effects, other sports, real users, or a live model.

## Required rollout blocker

The explicit v3 league path is complete, but `run_prediction_study` does not yet maintain season-local routine streaks. If the shared default changed now, the Admin prediction path would fail on its first between-game v3 decision and could not agree with the v3 league archive.

Phase 0.5R must add one zeroed per-season routine mapping to the explicit v3 prediction path, pass it through the existing life-day transition, update it from stored decisions, and reset it at each season boundary. The no-argument historical prediction study must remain explicitly v1.

## Phase 0.5R controlled-rollout contract

1. Keep Phase 0.5I explicit v1, Phase 0.5L explicit v1/v2, Phase 0.5P explicit v2/v3, and Phase 0D.4's no-argument study explicit v1.
2. Add season-local v3 routine reconstruction to the prediction-study path before changing the default.
3. Change only `DEFAULT_LIFE_BRAIN_VERSION` from v2 to v3 for new league and Admin state; bump the league implementation version without changing state schema v4.
4. Keep all old v1/v2 decisions and replay manifests immutable. New seasons start v3 streaks at zero; completed-season save/load needs no migration.
5. Make the Admin label v3 truthfully, regenerate its league and prediction caches under the same version, and verify winners and replay hashes agree.
6. Prove default and explicit v3 equality, mixed v2-to-v3 append behavior, explicit v2/v3 replay, save/load/resume, both locked evaluation digests, the full regression suite, Admin self-check, and one browser archive replay.
7. Roll back through the single default constant, followed by an Admin process restart. Never migrate or delete stored v3 history.

Single-game replay verifies its bound record; the full ordered season remains the v3 memory-policy audit boundary. Midseason saves remain unsupported.

## Validation

- Focused Phase 0.5P evidence lock: **1/1 passed** in 17.614 seconds.
- Full regression suite: **46/46 passed** in 55.417 seconds.
- Admin Console self-check: **passed**.
- Both bounded read-only audits approve a later controlled rollout and no automatic promotion.
- Both affected clean canvases parse as valid JSON; repository whitespace checks pass.

## Non-goals

No runtime behavior, default, schema, archive, interface, LLM, learning, training, retraining, narrative, personality, durable rating, economy, credits, purchases, wagering, monetization, deployment, dependency, or paid service changed.

## Next gate

Phase 0.5R controlled v3 rollout under the frozen contract above. The rollout must stop rather than change the default if prediction-version agreement, historical evidence, replay, persistence, or rollback checks fail.
