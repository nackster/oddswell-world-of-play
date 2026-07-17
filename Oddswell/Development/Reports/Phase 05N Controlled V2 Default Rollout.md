---
tags:
  - phase-05n
  - athlete-life
  - controlled-rollout
status: complete
date: 2026-07-16
---

# Phase 0.5N: Controlled Athlete Life Brain v2 Default Rollout

## Outcome

`athlete-life-v2` is now the default for newly generated league and Admin Console decisions. V1 and v2 have separate immutable constants, and the active default has its own explicit name. Rollback is one default-constant change followed by a process restart.

No saved decision, replay manifest, schema, or historical report was rewritten. Cost: **$0.00**.

## Implemented

- New life choices and league seasons use `DEFAULT_LIFE_BRAIN_VERSION`, currently v2.
- The active league version is `phase05n-v1`; the engine and state schema remain unchanged.
- Phase 0.5I evaluation and every v1 side of Phase 0.5L use the explicit v1 constant.
- The no-argument Phase 0D.4 prediction study remains explicitly v1.
- The Admin Console explicitly uses v2 for both its career league and matching prediction study, preserving winner and replay-hash agreement.
- Admin status now reports `ACTIVE DEFAULT` and `athlete-life-v2`.
- League and athlete payloads derive their displayed version from stored season decisions rather than a hardcoded label.
- Athlete profile headings render the stored season version dynamically.

## Fresh default evidence

The four-season Admin career archive contains 80 games and **912/912 v2 decisions**:

| Choice | Count |
| --- | ---: |
| Rest | 379 |
| Recover | 23 |
| Train | 239 |
| Socialize | 271 |

The Admin league payload reports `athlete-life-v2`. Its prediction commitments were generated through the same policy version, and every winner and replay hash agrees with the league archive.

## History and persistence evidence

- The frozen Phase 0.5I evaluator still runs `athlete-life-v1` and retains its exact 912-choice distribution: 386 rest, 23 recover, 251 train, and 252 socialize.
- The Phase 0.5L comparison remains explicitly v1 versus v2 and retains canonical digest `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`.
- The historical prediction-study default equals an explicit v1 run.
- A saved v1 season round-trips exactly. Appending a new default season preserves every old v1 game and decision while recording only v2 decisions in the new season.
- Default-v2 and explicit-v2 save/load/resume paths remain deterministic.

Saved league state does not need a migration because every life decision and every replay manifest already records its own policy version. A caller that intentionally continues an old v1 simulation must request v1 explicitly.

## Validation

- Focused life, life-evaluation, and prediction suite: **16/16 passed** in 4.702 seconds.
- Full regression suite: **44/44 passed** in 38.405 seconds.
- Admin Console self-check: **passed**.
- Edited canvas JSON and repository whitespace checks: passed.

## Truth and scope

This is a deterministic policy release, not model training, learning, personality inference, or evidence of real-world realism. No new trait, relationship, narrative, LLM, retraining, economy, credit, wagering, purchase, monetization, deployment, dependency, or paid API was added.

## Next gate

Phase 0.5O should review one bounded short-term Athlete Life Brain memory input before any implementation. It must define the smallest auditable state, consequence, expiry, history contract, and evaluation gate without changing durable ratings or adding narrative events.
