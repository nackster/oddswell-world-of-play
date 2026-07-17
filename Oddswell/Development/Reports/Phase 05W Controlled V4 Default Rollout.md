---
tags:
  - development
  - phase-05w
  - athlete-life
  - controlled-rollout
status: complete
date: 2026-07-17
---

# Phase 0.5W: Controlled Athlete Life Brain v4 Default Rollout

## Result

`athlete-life-v4` is now the default for newly generated league and Admin Console decisions. V1, v2, v3, and v4 remain separate immutable policy versions, and old decisions retain the version stored in their replay evidence.

This is a reversible deterministic policy release, not learning, intelligence, improved realism, confidence, personality, or a trained model. Cost: **$0.00**.

## Smallest rollout

- The explicit v4 prediction path now uses the same zeroed season-local routine map and chronological same-season scoring history as the authoritative league.
- Each between-game form reads only completed earlier games. Player points and minutes are appended after the authoritative game finishes, and both maps reset at the next season boundary.
- `DEFAULT_LIFE_BRAIN_VERSION` changed from v3 to v4 only after the explicit prediction compatibility gate passed.
- League implementation label advanced to `phase05w-v1`; state schema remains `oddswell-league-state-v4`.
- The no-argument historical Phase 0D.4 prediction study remains explicitly pinned to v1.
- Admin league and prediction generation continue sharing the same default-policy constant. No database, migration, dependency, model job, or new evaluator was added.

## Prediction chronology gate

While v3 was still the default, an explicit two-season v4 study matched the authoritative v4 league on **8/8 winners and replay hashes**:

- First replay SHA-256: `54b7bb7995ccf6ef06d7f82b68cf424fe39ed3efb8efebd76715077aff021dd4`
- Last replay SHA-256: `1cb4acea5a156b6c04922d62c0ef78998fabd34efdf8726cf0fbbd17dd1b14a7`

The rollout stopped at this gate until the equality check passed. The default and explicit v4 paths then remained equal in the rollout regression suite.

## Fresh default evidence

The regenerated four-season Admin archive contains:

- 80 games and 912/912 v4 decisions.
- 24 recover, 386 rest, 234 socialize, and 268 train choices.
- Only `athlete-life-v4` in new decision records.
- 204 reached recent-scoring response reasons; the first is Jalen Cross socializing before Season 1 Game 5 after an above-typical scoring signal.
- A 12-8 Harbor City Waves first season.
- Exact winner and replay-hash agreement across all **20/20** first-season Admin prediction records and league games.

## History, replay, and persistence

- Saved v1, v2, and v3 seasons round-trip unchanged. Appending a default-v4 Season 4 preserves all three old season objects and records only v4 decisions in the new season.
- Explicit v4 save/load/resume and replay remain deterministic; season-local routine and scoring history reset rather than crossing the offseason.
- Phase 0.5I remains explicit v1.
- Phase 0.5L remains explicit v1/v2 with digest `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`.
- Phase 0.5P remains explicit v2/v3 with digest `eb30329a6b9dee868e5980805284bec1b98fd3919e98e705548c73dac4eab618`.
- Phase 0.5U remains explicit v3/v4 with digest `a7b61128668fce26c392a52fac4425324ec41fdfead3b261e57535ff83fc4f60`.
- Single-game replay verifies its bound record; the full ordered season remains the routine and scoring-history audit boundary. Midseason persistence remains unsupported.

## Admin and browser validation

- Admin Console reports `athlete-life-v4` as `ACTIVE DEFAULT` and truthfully describes bounded same-season routine variation plus a one-decision recent-scoring response as deterministic and not learned.
- League Viewer reports `phase05w-v1`.
- Browser QA completed archived Season 1 Game 1 at 78-117, frame 422/422, replay SHA-256 `fb93c5a295cc6dbf333635d8767d3544e73c23facc44872ca4ad3d079627b193`, with `ARCHIVE VERIFIED` and no console warnings or errors.

## Automated validation

- Focused rollout, prediction, history, and rollback suite: **17/17 passed** in 2.319 seconds.
- Full regression suite, including all historical digest locks: **50/50 passed** in 112.504 seconds.
- Admin Console self-check: **passed**.
- Both affected clean canvases parse as valid JSON with unique node/edge identifiers and valid edge endpoints; repository whitespace checks pass.

## Rollback

Change only `DEFAULT_LIFE_BRAIN_VERSION` back to `LIFE_BRAIN_V3_VERSION` and restart local Admin/process instances. Do not change schema, delete v4 support, migrate records, or rewrite v4 replay history. Existing v4 seasons remain readable; only newly generated default seasons return to v3.

## Non-goals

No LLM, learning, training, retraining, broad performance score, cross-season memory, midseason save, personality, confidence, narrative, misconduct, partying, legal event, durable rating change, economy, credits, purchases, wagering, monetization, deployment, or paid service was added.

## Next gate

Phase 0.5X read-only v4 post-rollout integration review. Observe the new default archive, its first reached scoring-response transition, prediction chronology, persistence, historical digest locks, exact replay, Admin labels, and rollback evidence before defining another Athlete Life Brain input.
