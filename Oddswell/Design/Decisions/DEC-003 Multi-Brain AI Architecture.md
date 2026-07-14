---
tags:
  - decision
  - ai
  - simulation
  - architecture
status: approved-direction
date: 2026-07-13
---

# DEC-003: Multi-Brain AI Architecture

## Decision

OddsWell will use several cooperating brains instead of one system controlling everything:

| Brain or layer | Scope | Responsibility |
| --- | --- | --- |
| Project Brain | Development only | Obsidian stores plans, decisions, standards, and research. |
| Athlete Life Brain | Shared by every sport | Personalities, relationships, habits, training, rest, social choices, stress, morale, and off-field consequences. |
| World and League Brain | Shared by every sport | Schedules, teams, careers, news, history, social context, and persistent world state. |
| Sport Brain | One per sport | AI decisions for athletes and coaches. Basketball begins with play calls, positioning intent, passing, shooting, substitutions, and strategy. |
| Rules and Outcome Engine | One per sport | Validates legal actions and resolves their consequences using versioned rules and seeded randomness. |
| Learning Loop | Shared infrastructure | Stores decision data, evaluates behavior, maintains memory, and promotes tested policy or model updates. |

The sport brain is genuinely AI-driven: an LLM may choose what athletes and coaches attempt. The rules engine remains authoritative about what is legal and what actually happens.

## What “keeps learning” means

1. **Immediate memory:** every important choice, context, and consequence becomes structured history the AI can retrieve later.
2. **Measured improvement:** recorded data is evaluated for realism, variety, balance, latency, cost, and failure cases.
3. **Versioned updates:** prompts, policies, retrieval rules, fine-tunes, or models are tested and promoted as named versions.

The production model will not silently rewrite its own code or weights during live games. A candidate update must pass evaluation before it becomes the active version.

## Match authority and replay

- The AI produces schema-validated, legal action intents.
- The deterministic engine resolves those actions and records the outcome.
- Every match stores the AI model/version, policy version, structured decisions, simulation seed, and event log.
- A replay uses the recorded decision tape and event log; it does not ask the LLM to invent the game again.
- Purchased credits, wagers, and player spending never influence AI choices or match resolution.

This preserves AI agency while keeping matches testable, replayable, and auditable.

## Athlete Life Brain direction

Fictional athletes will eventually make daily life choices such as training, resting, recovering, socializing, partying, handling relationships, engaging with media, or neglecting responsibilities. Their traits, goals, current state, relationships, and memories influence those choices.

Consequences should form understandable chains. For example:

`late night → less sleep → weaker practice → fatigue or reduced coach trust → possible performance impact`

The system should model tradeoffs rather than label every social choice as bad. It must avoid real-person claims and demographic stereotypes.

## Phasing

- **Phase 0:** build the smallest basketball rules engine, a strict AI action contract, a simple baseline decision policy, complete decision logging, and one limited LLM pilot.
- **After the basketball loop is stable:** add persistent AI memory and a small Athlete Life Brain pilot using a few choices such as train, rest, recover, and socialize.
- **Later sports:** reuse the shared life, world, memory, and learning layers while adding a new sport brain and rules engine for each sport.

See [[Visual Maps/Multi-Brain Architecture]] for the system map.
