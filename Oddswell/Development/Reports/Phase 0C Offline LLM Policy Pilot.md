---
tags:
  - development
  - simulation
  - ai
  - validation
status: active
---

# Phase 0C Offline LLM Policy Pilot

The provider-neutral LLM boundary is implemented and exercised across **10 games** using a deterministic local fixture. The fixture proves integration, validation, fallback, telemetry, and replay without an API key or paid call. **It is not a live LLM and is not evidence that model decisions are intelligent.**

## Pilot result

| Measure | Result |
| --- | ---: |
| Structured decisions | 8,140 |
| Invalid provider outputs | 0 |
| Deterministic fallbacks | 0 |
| Exact action-tape replay | Yes |
| Estimated paid API cost | $0.00 |

**Action mix:** defend: 4070; drive: 554; pass: 2443; shoot_2: 688; shoot_3: 385

## Baseline-v2 realism calibration

The opportunity changes were rerun across **1,000 seeded games**. **9/9 engineering guardrails passed.**

| Measure | Result |
| --- | ---: |
| Average team score | 97.83 |
| Total possessions | 206.92 |
| Field-goal percentage | 40.5% |
| Three-point attempt share | 26.9% |
| Turnovers per team | 8.41 |
| Home win rate | 49.9% |
| Overtime rate | 4.0% |
| Maximum player attempts | 23.47 |
| Maximum player rebounds | 16.19 |

## Guardrails now enforced

- The provider receives an exact-key sports snapshot: clock, score, possession, fatigue, ratings, ballhandler, and the complete legal-action list.
- The provider never receives the seed, outcome probabilities, credits, wagers, wallet, purchase, or payment data.
- Output must be one exact `Action` object already present in `legal_actions`.
- Timeout, provider, JSON, schema, actor, target, and legality failures use the seeded baseline fallback and are recorded by category.
- The rules engine remains authoritative; replay uses the recorded action tape and never asks the provider again.
- Policy traces capture provider/model, policy version, sanitized request, request hash, raw response, parsed action, fallback, latency, tokens, and cost. Chain-of-thought is never requested or stored.

## Realism correction included

Initial ballhandlers are now weighted by existing passing and shooting ratings, and defenders are distributed by defense rating instead of assigning the single best defender to every possession.

## Live pilot gate

Choose a provider/model and approve a small cost/latency budget before any live call. Start with fixed scenarios or one team's offense for 5-10 games, compare paired seeds and swapped home assignments, and promote a named policy version only if legality, replay, realism, cost, and latency pass.

Before persisted public matches or any wagering feature, bind the engine, seed, matchup, roster, policy, action tape, and event log into a canonical SHA-256 replay manifest so later mutation is detected.
