---
tags:
  - development
  - phase-05p
  - athlete-life
  - evaluation
status: complete
date: 2026-07-17
---

# Phase 0.5P: Opt-In Routine Memory Pilot

## Result

The deterministic `athlete-life-v3` routine-memory pilot passes its frozen integrity and provisional stability gates and is **ELIGIBLE FOR LATER REVIEW**. It is not promoted. `athlete-life-v2` remains the default for new league and Admin decisions.

Cost: **$0.00**.

## Smallest implementation

- One signed per-athlete `routine_streak` stays within `-2..+2` during a season.
- Two consecutive train choices trigger one socialize choice; two consecutive socialize choices trigger one train choice.
- Recovery and fatigue-rest precedence are unchanged. Rest and recover reset the streak.
- The streak is reconstructed from ordered same-season decisions and expires at the season boundary. No field, database, state-schema revision, dependency, or durable rating effect was added.
- V1 and v2 decisions remain immutable. V3 is available only through an explicit policy argument.

This is short deterministic choice history, not learned memory, personality, discipline, intelligence, or neural-network training.

## Fresh paired evidence

Ten untouched seed blocks use `40000 + 80*i`, with four 20-game seasons in each block:

- 800 games and 9,120 decisions per policy.
- Zero policy, version, tenure, transition, ordering, or streak-reconstruction violations.
- 1,208 v3 routine variations across 5,091 eligible elective decisions.
- Practice-group variation rate: 22.8084%; social-group rate: 24.6304%; gap: 1.8220 percentage points.
- Maximum absolute streak: 2. Maximum identical elective-action run: 2.
- V2/v3 actions differ 2,899 times; winners differ in 130/800 games (16.25%).
- Mean absolute margin difference: 5.8438 points.
- Team scoring shift: -0.1031 point per team-game. Harbor City win-rate shift: +1.0 percentage point.
- Overall injury-rate change: +0.0002 percentage point. Missed-game-rate change: +0.0104 percentage point.

All frozen alarms pass. Phase 0.5P adds an explicit aggregate margin-MAE alarm of at most 8 points; it does not retroactively alter Phase 0.5L evidence.

Canonical evaluation digest:

```text
eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618
```

## Validation

- Focused Athlete Life Brain and routine evaluator tests: **7/7 passed** in 18.203 seconds.
- Full regression suite: **46/46 passed** in 56.253 seconds.
- Admin Console self-check: **passed**.
- Existing Phase 0.5L digest remains locked by its regression test.
- Both affected clean canvases parse as valid JSON; repository whitespace checks pass.

## Truth and scope boundary

The paired results measure stability inside the fictional deterministic simulator. They do not show real-world accuracy, learning, improved judgment, overtraining, misconduct, partying, legal trouble, a trained model, or an LLM. V3 remains invisible in the Admin Console until a separate deliberate rollout decision.

No paid API, model training, retraining, economy, credits, purchases, wagering, monetization, deployment, narrative event, cross-season memory, or persistent trait was added.

## Next gate

Phase 0.5Q deliberate v3 review: interpret the fresh evidence, verify the version-safe rollout and rollback boundary, and decide whether v3 should remain opt-in or become eligible for a controlled rollout. The review itself must not change the default.
