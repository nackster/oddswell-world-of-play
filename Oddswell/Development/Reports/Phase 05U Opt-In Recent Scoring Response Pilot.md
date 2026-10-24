---
tags:
  - development
  - phase-05u
  - athlete-life
  - evaluation
status: complete
date: 2026-07-17
---

# Phase 0.5U: Opt-In Recent Scoring Response Pilot

## Result

The deterministic `athlete-life-v4` recent-scoring-response pilot passes its frozen integrity and provisional stability gates and is **ELIGIBLE FOR LATER REVIEW**. It is not promoted. `athlete-life-v3` remains the default for new league and Admin decisions.

Cost: **$0.00**.

## Smallest implementation

- V4 adds only the three-value `recent_scoring_form` input frozen in Phase 0.5T.
- The immediately previous completed game's points are compared with that athlete's earlier same-season appearance average. At least three earlier appearances are required; a missed previous game defaults to `typical`.
- Recovery, high-fatigue rest, and the v3 two-choice routine ceiling retain priority. A reached `below` signal chooses train; a reached `above` signal chooses socialize.
- The input is rebuilt from chronological in-memory game evidence, expires after one decision and every season, and adds no database, state-schema revision, dependency, or durable trait.
- V1-v3 decisions remain immutable. V4 is available only through an explicit `athlete-life-v4` policy argument; omission rolls back to the default v3 path.

This is a bounded deterministic scoring response, not learning, confidence, personality, discipline, intelligence, or real-world behavior.

## Fresh paired evidence

Ten untouched seed blocks use `50000 + 80*i`, with four 20-game seasons in each block. `50000` is the first seed namespace, not a game count:

- **800 games and 9,120 decisions per policy**.
- V4 classified 3,150 below, 3,565 typical, and 2,405 above decisions; 7,564 decisions had enough chronological appearance evidence.
- All **2,089/2,089** reached performance-response opportunities used the specified response.
- Practice group: 3,789/4,560 covered (83.0921%), 1,097/1,097 responses. Social group: 3,775/4,560 covered (82.7851%), 992/992 responses.
- Zero policy, version, tenure, chronology, classification, precedence, transition, ordering, or replay violations.
- Maximum absolute routine streak: 2. Maximum identical elective-action run: 2.
- V3/v4 actions differ 2,529 times; winners differ in 130/800 games (16.25%). Mean absolute margin difference is 5.4813 points.
- Mean team scoring shifts +0.1906 point per team-game. Harbor City win rate shifts +1.0 percentage point.
- Overall injury-rate change is +0.0113 percentage point; missed-game-rate change is +0.0417 percentage point.

All Phase 0.5P fatigue, minutes, workload, injury, missed-game, readiness, scoring, win-rate, winner-disagreement, and margin alarms pass. No final-block tuning occurred.

Canonical evaluation digest:

```text
a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60
```

## Version, history, and rollback evidence

- `DEFAULT_LIFE_BRAIN_VERSION` remains exactly `athlete-life-v3`.
- Phase 0.5L and Phase 0.5P canonical digests remain pinned by their regression tests.
- Explicit v4 save/load/resume is identical, and every v4 archive reconstructs its score, minutes, decisions, and replay hash exactly.
- The existing state schema remains `oddswell-league-state-v4`; the existing league default remains `phase05r-v1`.
- Rollback is omission of the explicit v4 argument. No default or Admin process setting changed.

## Validation

- Focused Athlete Life Brain and paired-evaluator suite: **12/12 passed** in 114.143 seconds.
- Full regression suite: **49/49 passed** in 130.440 seconds.
- Admin Console self-check: **passed**.
- Both affected clean canvases parse as valid JSON with unique identifiers and valid edge endpoints; repository whitespace checks pass.

## Truth and scope boundary

The paired results measure deterministic behavior inside the fictional simulator. They do not show improved real-world judgment, learning, a neural network, a trained model, personality, morality, partying, legal trouble, or player development.

No paid API, model training, retraining, economy, credits, purchases, wagering, monetization, deployment, narrative event, cross-season performance memory, permanent rating effect, or dependency was added.

## Next gate

Phase 0.5V deliberate v4 promotion review. It may interpret this frozen evidence and verify rollout/rollback boundaries, but it must not change the default.
