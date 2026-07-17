---
tags:
  - phase-05o
  - athlete-life
  - short-term-memory
status: complete
date: 2026-07-16
---

# Phase 0.5O: Short-Term Routine Memory Review

## Decision

Define exactly one future Athlete Life Brain v3 memory input:

```text
routine_streak: integer from -2 through +2
```

Positive values count consecutive `train` choices. Negative values count consecutive `socialize` choices. Zero means no active routine. This is a bounded deterministic recent-choice signal, not learned memory, personality, discipline, morality, or a diagnosis.

Phase 0.5O is design-only. V2 remains the active default and runtime behavior is unchanged. Cost: **$0.00**.

## Proposed opt-in v3 policy

Decision precedence:

1. Unavailable athlete → `recover`.
2. Fatigue at or above `0.24` → `rest`.
3. `routine_streak == +2` → `socialize` for routine variation.
4. `routine_streak == -2` → `train` for routine variation.
5. Otherwise use the existing v2 practice/social preference.

The selected action updates the next streak:

- `train`: add one to a positive streak, capped at `+2`; otherwise start at `+1`.
- `socialize`: subtract one from a negative streak, capped at `-2`; otherwise start at `-1`.
- `rest` or `recover`: reset to `0`.
- New season, offseason, or debut: start at `0`.
- Retirement: remove the active state while preserving history.

Existing train, socialize, rest, and recover consequences remain unchanged. The rule prevents more than two identical elective choices in sequence; it adds no new penalty or rating effect.

## Frozen-state diagnostic

A read-only scan applied the proposed action rule to the current 912-decision v2 archive without resimulating fatigue, injuries, RNG, or game outcomes.

- 120/912 stored choices reach the proposed routine-variation gate.
- Practice group: 52/239 eligible states, or 21.76%.
- Social group: 68/271 eligible states, or 25.09%.
- Trigger-rate gap: 3.33 percentage points.
- One-step counterfactual totals: 255 train, 255 socialize, 379 rest, and 23 recover.

This is design evidence only. It is not a sequential v3 forecast, a promotion decision, or a claim about real people.

## History, persistence, and replay contract

- A future implementation must use a new explicit `athlete-life-v3` policy. V1 and v2 remain immutable; v2 remains the default.
- Reconstruct the streak from ordered same-season v3 decisions already stored in the league archive. Do not add a database, durable memory field, or state-schema revision for this pilot.
- The current save boundary is a completed season, where this memory expires. Save/load/resume therefore needs no additional persisted state.
- The routine-variation reason must be recorded in the v3 decision, and the existing replay manifest must continue binding the ordered decisions.
- A v3 evaluator must reconstruct every transition and reject any policy, version, tenure, or streak mismatch.
- If midseason saves or cross-offseason memory are later approved, persist one explicit per-athlete snapshot then—not now.

## Future v3 pilot gate

Phase 0.5P should implement v3 as opt-in only and compare v2 versus v3 on ten untouched paired seed blocks: `40000 + 80*i`, for `i = 0..9`.

Hard integrity gates:

- Exactly 9,120 decisions per policy across 800 games.
- Zero policy, version, tenure, transition, or streak-reconstruction violations.
- Streak always remains within `-2..+2`.
- Recovery and high-fatigue rest keep precedence.
- No elective-action run exceeds two; every rest/recover and season boundary resets memory.
- V1 evaluation, Phase 0.5L digest, Phase 0D.4 evidence, default v2 behavior, replay, and save/load/resume remain exact.

Provisional comparison alarms:

- Routine-variation rate gap between preference groups: at most 5 percentage points.
- Reuse Phase 0.5L's fatigue, minutes, workload, injury, missed-game, readiness, scoring, win-rate, winner-disagreement, and margin alarms without loosening them.

Passing makes v3 eligible for a later review only. It must never promote itself.

## Validation

- Focused Athlete Life Brain suite: **5/5 passed** in 0.648 seconds.
- Full regression suite: **44/44 passed** in 38.308 seconds.
- Admin Console self-check: **passed**.
- Both edited canvases parse as valid JSON; repository whitespace checks pass.

## Non-goals and risks

No cross-season memory, game-result reaction, durable rating change, trait inference, relationships, partying or misconduct event, legal event, narrative, randomness, LLM, training, retraining, economy, credits, wagering, purchase, monetization, deployment, dependency, or paid API is added.

The two-choice ceiling and 2+1 cadence are provisional mechanical pilot values. Train and socialize have different temporary effects, so a symmetric rule can still produce asymmetric outcomes; fresh paired evidence is mandatory.

## Next gate

Phase 0.5P opt-in Athlete Life Brain v3 routine-memory pilot and paired evaluation under the frozen contract above.
