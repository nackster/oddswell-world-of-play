---
tags:
  - phase-05j
  - athlete-life
  - policy-review
status: complete
date: 2026-07-16
---

# Phase 0.5J: Life Preference Policy Review

## Outcome

Phase 0.5J defines one small fictional input for a future Athlete Life Brain v2: `off_day_preference`, with the only allowed values `practice` and `social`. This is a design-only gate. Runtime policy remains `athlete-life-v1`; no code, schema, archive, replay, Admin Console behavior, or game outcome changed. Cost: **$0.00**.

## Proposed preference table

| Practice preference | Social preference |
| --- | --- |
| Jalen Cross | Micah Vale |
| Dorian Pike | Kellan Shore |
| Malik Frost | Andre North |
| Nico Reyes | Tariq Stone |
| Eli Mercer | Roman Voss |
| Cal Brooks | Mateo Cruz |
|  | Soren Lake |

The mapping is fictional, version-owned, and resolved only from stable athlete identity. Each active six-player team has three athletes in each group in Seasons 1-4; Roman's social preference is replaced by Soren's social preference in Season 4. The trait does not derive from ratings, age, performance, injury, demographics, or user data.

## Proposed v2 decision precedence

| Priority | State | Proposed choice |
| ---: | --- | --- |
| 1 | `recovery_days > 0` | `recover` |
| 2 | `fatigue >= 0.24` | `rest` |
| 3 | healthy, below threshold, `practice` preference | `train` |
| 3 | healthy, below threshold, `social` preference | `socialize` |

The existing v1 consequences and bounds would remain unchanged: recover removes one recovery day, rest removes `0.03` fatigue, train adds `0.02` fatigue and `+0.015` next-game readiness, and socialize adds `0.01` fatigue and `+0.01` next-game readiness.

Boundary examples are exact: recovery overrides preference even at fatigue `0.30`; fatigue `0.24` produces rest; healthy fatigue `0.2399` produces the elective action associated with the athlete's preference.

## Frozen-state counterfactual

Applying the proposed choice table once to the 912 stored v1 before-states—without changing or resimulating history—produces this diagnostic:

| Group | Stored states | Proposed elective action | Rest | Recover | Choices different from stored v1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Practice | 456 | 259 train | 184 | 13 | 124 |
| Social | 456 | 244 socialize | 202 | 10 | 116 |
| Total | 912 | 503 elective | 386 | 23 | 240 |

This is a one-step counterfactual only. Sequential v2 choices would change fatigue and readiness, which can change later choices, injury exposure, RNG consumption, and outcomes. These counts are not a forecast, balance target, or realism result.

## Version and history contract

- `athlete-life-v1` and its 912 archived decisions remain immutable.
- A future v2 would start only for newly generated decisions and reuse the existing `LifeDecision.policy_version`, `reason`, selected action, and consequence fields; no trait field is required in persisted state.
- Validation must dispatch by the stored policy version. It must never reinterpret a v1 decision with v2 rules.
- Mixed-policy evaluation must group evidence by version. Completed v1 reports and replay evidence remain historical truth.
- The preference is a narrow routine choice, not personality, discipline, morality, mental health, intelligence, or a demographic inference.

## Explicit exclusions

No runtime v2, LLM, learning, retraining, long-term memory, relationships, partying, legal trouble, narrative generation, durable-rating change, economy, credits, wagering, purchases, or monetization was added.

## Validation

The two bounded agent audits agreed on one binary fictional preference and no persistence-schema change. A read-only counterfactual verifies all 13 identities, a 3/3 active-team split in every season, 912/912 stored states, and exact recovery/rest precedence. The unchanged 39-test suite and Admin Console self-check pass before the phase commit.

## Next gate

Phase 0.5K may implement the versioned preference pilot beside immutable v1, add policy-version-aware validation, generate a fresh v2 archive, and compare preference groups without rewriting Phase 0.5I evidence.
