---
tags:
  - development
  - phase-06h
  - athlete-performance
  - input-selection
  - offensive-involvement
status: complete
date: 2026-07-17
---

# Phase 0.6H: Next Athlete Performance Input Selection Review

## Decision

Select exactly one candidate input: a durable **offensive involvement tier** with the values `low`, `standard`, and `featured`.

The tier may only redistribute who starts a possession or is selected as a pass target. It must not change ratings, minutes, availability, readiness, shot probability, Consistency v2, action legality, or career development. Its truthful Admin scope is **OPPORTUNITY ONLY**.

This phase is design-only. No simulator, league, schema, replay, prediction, API, Admin, or default behavior changed. Cost: **$0.00**.

## Why this is the smallest justified gap

The current five ratings already distinguish shooting, passing, defense, rebounding, and stamina. Consistency v2 now controls shooting variance without adding talent. Adding another ability or a confidence/clutch score would duplicate those systems or make an unsupported claim.

Opportunity is still mostly implicit. The baseline selects an initial ballhandler from `passing + shooting`, selects pass targets from shooting, and then gives every ballhandler the same four legal action kinds. In the fresh four-season Admin archive:

- Jalen Cross records 24.55 field-goal attempts per 48 minutes and Nico Reyes 23.29.
- Cal Brooks records 22.18 despite a 70 shooting rating, only 4.8% below Nico.
- Kellan Shore records 22.26, while high-passing Micah Vale and Eli Mercer record 19.80 and 19.93.
- Across the active and retired archive, the starter-scale range is compact relative to the visibly different roles and ratings.

These fictional measurements do not prove real-world realism. They show one mechanical gap: durable ability affects efficiency, but the model has no explicit bounded statement of offensive responsibility.

## Candidates not selected

| Candidate | Decision | Reason |
| --- | --- | --- |
| Shot-location or drive/2/3 profile | Defer | More detailed than needed and does not first answer who receives opportunities. |
| Clutch, confidence, hot hand, or mentality | Reject | Unsupported labels overlap Consistency v2 and would imply psychology the simulator does not model. |
| Defensive or rebounding consistency | Defer | No measured failure currently justifies expanding the shooting-only resolver. |
| Another Athlete Life Brain input | Reject here | This gate concerns competitive performance; life consequences remain a separate causal system. |
| No new input | Reject for this gate | The archive exposes a bounded opportunity gap that one small input can test. |

## Frozen pilot contract

- **Input:** one explicit tier per athlete: `low`, `standard`, or `featured`.
- **Bound:** a future opt-in pilot may test weights only within `0.85` to `1.15`, with `standard = 1.00`. The pilot may not tune beyond that range.
- **Scope:** multiply only initial-ballhandler and pass-target selection weights. Do not alter action weights after the athlete has the ball.
- **Talent boundary:** ratings and circumstances continue to define ability and make probability. Involvement changes opportunity only; it cannot turn a low-rated athlete into a star.
- **Chronology:** use one frozen pregame roster snapshot. Do not infer the tier from the current game's score, recent outcomes, hidden future data, or life-policy choices.
- **Replay:** an opt-in game must bind the exact tier/weight snapshot into its audit evidence and reproduce the action tape and result exactly.
- **History:** omission must preserve the current resolver exactly. Phase 0.6F/0.6G, v1-v4 life-policy evidence, stored v2 games, and historical predictions remain immutable.
- **Admin label:** until a separate evaluation and rollout pass, show only `OPT-IN PILOT` and `OPPORTUNITY ONLY`; never `ACTIVE`, learning, confidence, personality, intelligence, or real-world realism.
- **Rollback:** omit the opt-in snapshot and restart. The authoritative league default remains unchanged, and any pilot evidence keeps its stored snapshot.

## Pilot stop conditions

The next phase must stop without promotion if it cannot prove all of the following with paired seeds:

1. Omission reproduces the exact current result, action tape, and event log.
2. A frozen same-athlete comparison creates an ordered but bounded opportunity difference between `low`, `standard`, and `featured`.
3. Shooting percentages and the underlying probability formula remain rating-driven rather than tier-driven.
4. Team possessions, scoring, winner sensitivity, and every tier's shot attempts stay visible; no favorable result may be hidden.
5. Every pilot game replays exactly with its stored tier/weight snapshot.
6. Historical league, prediction, life-policy, Consistency v2, and Admin evidence remains unchanged.

No default rollout, persistence-schema change, prediction change, or full-roster assignment is authorized by this decision.

## Validation

- Reconstructed the committed four-season, 80-game Admin archive and measured field-goal attempts per game and per 48 minutes from authoritative event records.
- Inspected the Player model, baseline possession and pass-target selection, shot resolver, career lifecycle, Consistency v2, and Admin specialty/tier presentation.
- Focused Consistency v2 boundary tests pass 4/4; the Admin Console self-check passes.
- Phase 0.6G's 59/59 runtime regression and Admin self-check evidence remains the unchanged runtime baseline.
- The affected roadmap canvas parses as valid JSON with unique node/edge identifiers and valid edge endpoints; repository whitespace validation passes.

## Next gate

Phase 0.6I: an **opt-in Offensive Involvement pilot**. Implement only the frozen opportunity-only input, run paired-seed calibration and exact replay checks, keep the authoritative league default unchanged, and stop without promotion if any Phase 0.6H condition fails.
