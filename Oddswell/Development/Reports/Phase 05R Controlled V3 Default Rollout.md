---
tags:
  - development
  - phase-05r
  - athlete-life
  - controlled-rollout
status: complete
date: 2026-07-17
---

# Phase 0.5R: Controlled Athlete Life Brain v3 Default Rollout

## Result

`athlete-life-v3` is now the default for newly generated league and Admin Console decisions. V1, v2, and v3 remain separate immutable policy versions, and old decisions retain the version stored in their replay evidence.

This is a reversible deterministic policy release, not learning, intelligence, improved realism, or a trained model. Cost: **$0.00**.

## Smallest rollout

- `DEFAULT_LIFE_BRAIN_VERSION` changed from v2 to v3.
- League implementation label advanced to `phase05r-v1`; state schema remains `oddswell-league-state-v4`.
- The explicit v3 prediction path now creates one zeroed routine map per season, passes it through the existing life-day transition, updates it from recorded decisions, and resets it at the next season boundary.
- The no-argument historical Phase 0D.4 prediction study remains explicitly pinned to v1.
- Admin league and prediction generation continue sharing the same default-policy constant. Version labels remain derived from executable and stored evidence.
- No database, migration, dependency, model job, or new evaluator was added.

## Fresh default evidence

The regenerated four-season Admin archive contains:

- 80 games and 912/912 v3 decisions.
- 23 recover, 382 rest, 252 socialize, and 255 train choices.
- Only `athlete-life-v3` in new decision records.
- A 13-7 Harbor City Waves first season.
- Exact winner and replay-hash agreement across all 20 first-season Admin prediction records and league games.

An explicit two-season v3 prediction study also matches the authoritative v3 league winner and replay hash game-for-game, proving within-season memory updates and season resets through the shared transition.

## History, replay, and persistence

- A saved v1-plus-v2 history round-trips unchanged. Appending a default-v3 season preserves both old season objects and records only v3 decisions in the new season.
- Explicit v2 and v3 save/load/resume paths remain deterministic.
- Phase 0.5I stays explicit v1.
- Phase 0.5L stays explicit v1/v2 with digest `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`.
- Phase 0.5P stays explicit v2/v3 with digest `eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618`.
- Single-game replay verifies the bound record; the full ordered season remains the routine-memory audit boundary. Midseason persistence remains unsupported.

## Admin and browser validation

- Admin Console reports `athlete-life-v3` as `ACTIVE DEFAULT` and describes its bounded same-season routine variation as deterministic and not learned.
- League Viewer reports `phase05r-v1`.
- Browser QA completed archived Season 1 Game 1 at 78-117, frame 422/422, with `ARCHIVE VERIFIED` and zero console warnings or errors.
- The stale local Admin process found during QA was closed and the current build was restarted; payload caches now reflect v3.

## Automated validation

- Focused rollout, prediction, history, and digest suite: **20/20 passed** in 39.766 seconds.
- Full regression suite: **47/47 passed** in 55.384 seconds.
- Admin Console self-check: **passed**.
- Both affected clean canvases parse as valid JSON; repository whitespace checks pass.

## Rollback

Change only `DEFAULT_LIFE_BRAIN_VERSION` back to `LIFE_BRAIN_V2_VERSION` and restart local Admin/process instances. Do not change schema, delete v3 support, migrate records, or rewrite v3 replay history. Existing v3 seasons remain readable; only newly generated default seasons return to v2.

## Non-goals

No LLM, learning, training, retraining, cross-season memory, midseason save, personality, narrative, misconduct, partying, legal event, durable rating change, economy, credits, purchases, wagering, monetization, deployment, or paid service was added.

## Next gate

Phase 0.5S read-only post-rollout integration review. Observe default-v3 Admin, prediction, replay, persistence, and rollback evidence before defining any additional Athlete Life Brain input.
