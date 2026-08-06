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
| Sport Odds Brain | One per sport | Produces versioned pregame probabilities and odds from the same frozen public snapshot available to every player. It cannot influence games. |
| Wager and Settlement Engine | Shared authoritative service | Locks offered markets and Odds Bucks stakes, then settles exactly once against a sealed sport result. It is deterministic infrastructure, not a sport brain. |
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
- The Basketball Odds Brain receives only a frozen public pregame snapshot and emits a versioned offer; it cannot read future events or mutate the match.
- The Wager and Settlement Engine consumes the versioned offer and sealed result with no path back into the Basketball Brain or Rules and Outcome Engine.

This preserves AI agency while keeping matches testable, replayable, and auditable.

## Athlete Life Brain direction

Fictional athletes will eventually make daily life choices such as training, resting, recovering, socializing, partying, handling relationships, engaging with media, or neglecting responsibilities. Their traits, goals, current state, relationships, and memories influence those choices.

Consequences should form understandable chains. For example:

`late night → less sleep → weaker practice → fatigue or reduced coach trust → possible performance impact`

The system should model tradeoffs rather than label every social choice as bad. It must avoid real-person claims and demographic stereotypes.

## Athlete ability and career persistence

Athletes are not normalized into equal performers. Each fictional athlete keeps a durable career identity built from distinct abilities such as shooting, passing, defense, rebounding, stamina, and future sport-specific skills. Some athletes can be stars, some specialists, some average, and some below league average. A great shooter may remain a weak defender; an elite defender may contribute little scoring.

Game performance combines separate layers:

`durable ability + development/age + current form + health/fatigue + life consequences + decisions + bounded randomness`

- The **Basketball Brain** chooses actions that fit an athlete's ratings, role, situation, and memory. It does not silently equalize talent or rewrite permanent ability after one game.
- The **Athlete Life Brain** later controls habits and personal choices such as practice, rest, partying, relationships, discipline, and responses to fictional legal trouble.
- Life choices can affect sleep, practice quality, coach trust, reputation, stress, availability, consistency, development rate, contracts, suspensions, and career length. Consequences must follow visible causal chains rather than unexplained rating punishment.
- Durable talent normally changes gradually through development, aging, injury, or sustained behavior. Temporary form and fatigue can change quickly.
- A completed career becomes immutable history for statistics, records, replays, and future world memory.

Legal-story events must remain fictional, use neutral rules and due process, and never be generated from demographic stereotypes.

## Phasing

- **Phase 0:** build the smallest basketball rules engine, a strict AI action contract, a simple baseline decision policy, complete decision logging, and one limited LLM pilot.
- **After the basketball loop is stable:** add persistent AI memory and a small Athlete Life Brain pilot using a few choices such as train, rest, recover, and socialize.
- **Later sports:** reuse the shared life, world, memory, and learning layers while adding a new sport brain and rules engine for each sport.
- **Phase 1H:** keep the Basketball Odds Brain and deterministic Wager and Settlement Engine separate under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]].

See [[Visual Maps/Multi-Brain Architecture]] for the system map.
