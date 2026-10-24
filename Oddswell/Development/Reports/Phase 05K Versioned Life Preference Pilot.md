---
tags:
  - phase-05k
  - athlete-life
  - preference-pilot
status: complete
date: 2026-07-16
---

# Phase 0.5K: Versioned Life Preference Pilot

## Outcome

Phase 0.5K implements `athlete-life-v2` as an explicit opt-in pilot beside immutable `athlete-life-v1`. Every existing call still defaults to v1. The pilot reuses the existing life-decision record, replay manifest, save/load path, and `oddswell-league-state-v4` schema. Cost: **$0.00**.

## Pilot policy

The fictional preference table approved in Phase 0.5J is now version-owned code. Unavailable athletes still recover first; fatigue at or above `0.24` still forces rest. Only a healthy, below-threshold elective choice differs: practice-preferring athletes train and social-preferring athletes socialize.

Policy selection is keyword-only. Unknown versions and unmapped v2 identities are rejected. Every stored decision records its policy version and preference reason, and replay creation rejects a decision whose version disagrees with its replay metadata. Temporary consequences and all existing readiness, fatigue, and recovery bounds are unchanged.

## Fresh four-season pilot

The v2 pilot uses the same fixed seeds and fictional rosters as the frozen v1 archive for comparison, but generates a separate fresh history.

| Evidence | v1 archive | v2 pilot |
| --- | ---: | ---: |
| Seasons / games | 4 / 80 | 4 / 80 |
| Decisions | 912 | 912 |
| Rest | 386 | 379 |
| Recover | 23 | 23 |
| Train | 251 | 239 |
| Socialize | 252 | 271 |
| Readiness exposures | 503 | 510 |
| Mean readiness | 0.6891% | 0.6902% |
| Maximum readiness | 1.5% | 1.5% |
| Net fatigue change from choices | -4.04 | -3.88 |
| New injuries / missed player-games | 20 / 14 | 20 / 14 |
| Policy / tenure violations | 0 / 0 | 0 / 0 |
| Reconstructed games | 80 / 80 | 80 / 80 |

Preference adherence is exact. The 456 practice-group decisions contain 239 train, 204 rest, and 13 recover choices, with no socialize choices. The 456 social-group decisions contain 271 socialize, 175 rest, and 10 recover choices, with no train choices.

## Same-seed comparison

Sequential v1 and v2 histories differ on **381/912** choices. They produce **15/80** different winners and a **5.725-point** mean absolute game-margin change. In the v2 zero-readiness sensitivity replay, readiness changes scoring by **+0.8562 points per team-game**, field-goal percentage by **+0.5979 percentage points**, and turnovers by **-0.3438 per team-game**; 19/80 winners change and mean absolute margin movement is 7.237 points.

These are path-sensitive fictional simulator results. Changing an early choice can change fatigue, availability, RNG consumption, and later outcomes. They are not real-world estimates, proof of intelligence, a balance target, or evidence that either preference is better.

## Compatibility boundary

- Default simulations, the Admin Console, prediction study, and Phase 0.5I evaluator remain v1.
- V2 requires an explicit keyword at each simulation boundary and starts a fresh archive.
- V1 decisions are validated with v1 rules; v2 decisions are validated with v2 rules.
- Save/load/resume needs no new persisted field because the pilot version is supplied explicitly when continuing the pilot.
- Durable ratings, specialties, ages, retirement, debut, and completed history do not change.
- No UI, LLM, learning, retraining, memory, narrative, economy, credits, wagering, purchases, or monetization was added.

## Validation

Focused tests cover the 13-identity preference map, 3/3 active-team split, recovery/rest precedence, elective preference adherence, unsupported replay-version mismatch, immutable v1 metrics, 912 fresh v2 decisions, exact reconstruction, and v2 save/load/resume. All **41** regression tests and the Admin Console self-check pass before the phase commit.

## Next gate

Phase 0.5L should run a read-only multi-seed evaluation of v1 versus v2 preference-group workload, injuries, readiness, and outcomes before any promotion, added trait, narrative, or long-term consequence.
