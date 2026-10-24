---
tags:
  - phase-05m
  - athlete-life
  - promotion-review
status: complete
date: 2026-07-16
---

# Phase 0.5M: Athlete Life Brain v2 Promotion Review

## Decision

**Approved for controlled promotion. Not promoted in this review.**

Phase 0.5L passed every frozen integrity and provisional stability gate across ten untouched paired seed blocks: 800 games and 9,120 decisions per policy. V2 can therefore become the default for newly simulated league state in a separate, reversible rollout phase.

This decision does not claim that v2 is intelligent, learned, more realistic, or better at winning. It only establishes that the explicit fictional `practice | social` preference behaves consistently inside the current deterministic simulator and stays within the recorded engineering alarms.

## Evidence accepted

- V2 preference adherence is exact: 4,560 practice-group decisions contain no socialize choice, and 4,560 social-group decisions contain no train choice.
- Policy, version, and roster-tenure violations are zero.
- Readiness, fatigue, availability, workload, injury, missed-game, scoring, and outcome-sensitivity checks all pass their frozen provisional alarms.
- V1 and v2 both remain exactly replayable.
- Phase 0.5L's canonical evidence digest is `0ddabb69ad709380884572a65cff0f9571c617f6e7ab748afd91e698780e2588`.
- External cost remains **$0.00**.

## Why promotion is separate

The current default-policy constant is also used by frozen Phase 0.5I evaluation, the Phase 0D.4 prediction study, the multi-seed comparator, league simulation, tests, and the Admin Console. Changing it inside this review would make historical evidence silently follow the new default.

A separate rollout keeps the migration auditable and makes rollback trivial. The review therefore changes no runtime behavior, schema, archive, or interface.

## Phase 0.5N rollout contract

1. Give v1 and v2 explicit immutable version constants.
2. Pin historical Phase 0.5I, Phase 0.5L, and Phase 0D.4 evidence paths to v1 by name.
3. Make v2 the default only for newly simulated league and Admin Console state.
4. Display the active version truthfully wherever the Athlete Life Brain appears.
5. Preserve old saved decisions and replay manifests without rewriting or reinterpretation.
6. Prove explicit v1 replay, explicit v2 replay, default v2 behavior, save/load/resume, the full regression suite, and the Admin Console self-check.
7. Keep rollback to one reviewed default-version change; no data migration is required.

## Non-goals

No new trait, relationship, narrative, LLM, learning, retraining, economy, credit, wagering, purchase, monetization, deployment, or paid service is authorized by this decision.

## Next gate

Phase 0.5N should perform the controlled v2 default rollout under the contract above. Only after that rollout passes should the project consider another Athlete Life Brain input.
