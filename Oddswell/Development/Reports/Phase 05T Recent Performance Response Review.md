---
tags:
  - development
  - phase-05t
  - athlete-life
  - performance-response
status: complete
date: 2026-07-17
---

# Phase 0.5T: Recent Performance Response Review

## Decision

Define exactly one future Athlete Life Brain v4 input:

```text
recent_scoring_form: below | typical | above
```

The input compares one athlete's points in the immediately previous completed game with that same athlete's average points across earlier appearances in the same season. It is a bounded, chronology-safe scoring response—not overall performance, talent, personality, confidence, discipline, intelligence, learning, or a real-world behavioral claim.

Phase 0.5T is design-only. Athlete Life Brain v3 remains the active default; no simulator, policy, schema, archive, replay, Admin Console, or game outcome changed. Cost: **$0.00**.

## Frozen information boundary

For the between-game decision before Game `n`:

1. Read only the athlete's authoritative points and minutes from completed Game `n-1`.
2. Build the baseline only from that athlete's earlier same-season appearances in Games `1..n-2`.
3. Require at least three earlier appearances and positive minutes in Game `n-1`.
4. Classify `above` when previous-game points are more than 2 above the prior average, `below` when more than 2 below it, and `typical` otherwise.
5. Use `typical` when the athlete did not play or has fewer than three earlier appearances.

The signal expires after that one between-game decision. It never crosses a season, survives retirement, or carries from Roman Voss to Soren Lake. It excludes the current/future game, future season average, scores by other athletes, team result, ratings, fatigue, readiness, injury risk, seeds, RNG state, predictions, user data, economy data, and narratives.

The existing Admin form label cannot be reused directly: it compares the last five games with a completed full-season average, which is valid retrospective display evidence but would expose future games if used during a season.

## Proposed opt-in v4 precedence

1. Unavailable athlete -> `recover`.
2. Fatigue at or above `0.24` -> `rest`.
3. V3 `routine_streak == +2` -> `socialize`.
4. V3 `routine_streak == -2` -> `train`.
5. `recent_scoring_form == below` -> `train`.
6. `recent_scoring_form == above` -> `socialize`.
7. `recent_scoring_form == typical` -> existing practice/social preference.

Routine variation remains above performance response so no elective-action run exceeds two. Existing action consequences and the signed routine transition remain unchanged. A future v4 decision must record an exact performance-response reason when priorities 5 or 6 select the action.

## Frozen-archive diagnostic

A read-only scan classified the 912 current v3 decisions without changing or resimulating history:

| Signal | Decisions |
| --- | ---: |
| Below | 342 |
| Typical | 343 |
| Above | 227 |

Of the 343 `typical` values, 144 default because fewer than three earlier appearances exist and 13 default because the athlete did not play in the previous game. The remaining **755/912** decisions have enough prior evidence for comparison.

After preserving recover, rest, and routine precedence, a performance response would be reached in **211** stored states: 127 below and 84 above. A one-step counterfactual changes **93/912** recorded choices: 59 socialize-to-train and 34 train-to-socialize. It reaches 102 practice-group and 109 social-group states.

This diagnostic does not update the routine streak after a counterfactual action or resimulate fatigue, availability, injuries, RNG, scores, winners, or later choices. It is evidence that the proposed input is computable and bounded, not a sequential v4 forecast or promotion decision.

## Version, persistence, replay, and rollback contract

- Any implementation must use explicit opt-in `athlete-life-v4`; v1, v2, and v3 remain immutable and v3 remains the default.
- Reconstruct the input from ordered same-season authoritative game records. Do not add a database, model, durable trait, or state-schema revision for the pilot.
- Preserve each stored policy version and exact decision reason in replay evidence; validation must dispatch by stored version.
- Completed historical reports and their digests remain pinned to their named versions.
- Rollback is omission of the opt-in v4 argument. V4 must not become the default during implementation or evaluation.

## Future v4 pilot gate

Phase 0.5U may implement v4 as opt-in only and compare v3 versus v4 on ten untouched paired seed blocks: `50000 + 80*i`, for `i = 0..9`.

Hard integrity gates:

- Exactly 9,120 decisions per policy across 800 games.
- Zero policy, version, tenure, chronology, input-classification, precedence, routine-transition, ordering, or replay violations.
- `typical` for every no-appearance or insufficient-history state; no future-game or cross-season input.
- Recovery, high-fatigue rest, and the two-choice routine ceiling retain precedence.
- V1/v2/v3 tests, Phase 0.5L and 0.5P digests, Phase 0D.4 evidence, default v3 behavior, save/load/resume, and Admin self-check remain exact.

Reuse Phase 0.5P's provisional fatigue, minutes, workload, injury, missed-game, readiness, scoring, win-rate, winner-disagreement, and margin alarms without loosening them. Report signal coverage and response rates by practice/social group, but do not tune on the ten final blocks. Passing makes v4 eligible for a later review only; it must never promote itself.

## Validation

- Focused Athlete Life Brain and routine suite: **7/7 passed** in 18.872 seconds.
- Full regression suite: **47/47 passed** in 58.522 seconds.
- Admin Console self-check: **passed**.
- Both affected clean canvases parse as valid JSON with unique node/edge identifiers and valid edge endpoints; repository whitespace checks pass.

## Non-goals

No runtime v4, broad performance score, defense/rebounding response, personality or morality inference, durable rating change, cross-season memory, narrative event, relationship, partying, legal trouble, LLM, learning, training, retraining, economy, credits, wagering, purchase, monetization, deployment, dependency, or paid API is added.

## Next gate

Phase 0.5U opt-in Athlete Life Brain v4 recent-scoring-response pilot and fresh paired evaluation under the frozen contract above.
