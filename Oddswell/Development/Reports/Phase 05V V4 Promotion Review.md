---
tags:
  - development
  - phase-05v
  - athlete-life
  - promotion-review
status: complete
date: 2026-07-17
---

# Phase 0.5V: Athlete Life Brain v4 Promotion Review

## Decision

**Approved for a later controlled rollout. Not promoted in this review.**

Phase 0.5U passed every frozen integrity and provisional stability gate across ten fresh paired seed blocks. V4 may therefore enter a separate, reversible rollout phase for newly generated state. V3 remains the active default throughout Phase 0.5V.

This approval covers bounded deterministic simulator behavior only. It is not evidence that v4 learns, is intelligent, is more realistic, makes better life decisions, or improves outcomes. Cost: **$0.00**.

## Evidence accepted

- 800 games and 9,120 decisions per policy with zero policy, version, tenure, chronology, classification, precedence, transition, ordering, or replay violations.
- 7,564 v4 decisions had enough chronological appearance evidence, and all 2,089/2,089 reached response opportunities used the frozen response.
- Routine-streak magnitude and identical elective-action runs never exceed two.
- Mean team scoring shifts by +0.1906 point per team-game; Harbor City's win rate shifts by +1.0 percentage point; injury-rate change is +0.0113 percentage point; missed-game-rate change is +0.0417 percentage point.
- Phase 0.5U's canonical digest remains `a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60`.

## Path sensitivity retained

V3 and v4 differ on **2,529/9,120 actions** and **130/800 winners**, with a 5.4813-point aggregate margin MAE. These are material path changes even though the frozen provisional alarms pass. They justify strict version labels, historical pins, replay evidence, and one-step rollback; they do not demonstrate better decisions, outcomes, realism, intelligence, or learning.

## Required rollout blocker

The authoritative league reconstructs v4's season-local routine streaks and scoring history, but `run_prediction_study` initializes routine memory only for exact v3 and carries no chronological per-athlete scoring history. An explicit v4 prediction probe therefore fails at the first between-game transition with `v3/v4 routine streaks require the exact active roster`.

Phase 0.5W must align the explicit v4 prediction path before changing the default: create zeroed routine and scoring-history mappings for every season, derive each form only from completed earlier same-season points and minutes, pass both inputs through the existing life-day transition, update them from the authoritative completed game, and reset them at the season boundary. The no-argument historical Phase 0D.4 study must remain explicitly v1.

## Phase 0.5W controlled-rollout contract

1. Keep Phase 0.5I explicit v1, Phase 0.5L explicit v1/v2, Phase 0.5P explicit v2/v3, Phase 0.5U explicit v3/v4, and Phase 0D.4's no-argument study explicit v1.
2. Preserve the Phase 0.5L digest `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`, Phase 0.5P digest `eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618`, and Phase 0.5U digest above.
3. Add chronology-safe v4 routine and scoring reconstruction to the explicit prediction path before changing the default. Prediction and league winners and replay hashes must agree game-for-game.
4. Change only `DEFAULT_LIFE_BRAIN_VERSION` from v3 to v4 for new league and Admin state, then bump the league implementation label without changing state schema v4.
5. Keep all old v1-v4 decisions, seasons, and replay manifests immutable. New seasons start with zero streaks and empty scoring history; completed-season save/load needs no migration.
6. Make the Admin label truthfully show v4 as the active deterministic default, regenerate league and prediction caches under the same version, and never describe the scoring response as training, confidence, personality, intelligence, or learning.
7. Prove default/explicit v4 equality, season-boundary resets, mixed-history append behavior, replay, save/load/resume, all historical digests, the full regression suite, Admin self-check, and one exact browser archive replay.
8. Roll back through the single default constant followed by an Admin process restart. Never migrate, delete, or rewrite stored v4 history.

Single-game replay verifies its bound record; the full ordered season remains the v4 chronology and memory audit boundary. Midseason persistence remains unsupported.

## Validation

- Explicit v4 prediction compatibility probe: **blocked as expected** at the first between-game transition while v3 remains the default.
- Focused Phase 0.5U evaluator and digest lock: **2/2 passed** in 66.161 seconds.
- Full regression suite: **49/49 passed** in 138.124 seconds.
- Admin Console self-check: **passed**.
- Both affected clean canvases parse as valid JSON with unique identifiers and valid edge endpoints; repository whitespace checks pass.

## Non-goals

No runtime behavior, default, schema, archive, interface, LLM, learning, training, retraining, narrative, personality, confidence, durable rating, economy, credits, purchases, wagering, monetization, deployment, dependency, or paid service changed.

## Next gate

Phase 0.5W controlled v4 rollout under the frozen contract above. Stop without changing the default if prediction chronology, historical evidence, replay, persistence, Admin labeling, or rollback checks fail.
