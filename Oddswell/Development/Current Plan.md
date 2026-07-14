---
tags:
  - development
  - plan
status: active
---

# Current Plan

## Phase 0: Simulation foundation

1. Define two teams and a minimal athlete attribute model.
2. Build a deterministic possession-based rules and outcome engine.
3. Define one strict structured-action contract for the Basketball AI Brain.
4. Validate the loop with a simple baseline policy, then pilot one LLM policy through the same contract.
5. Record the AI model/version, decision inputs and outputs, simulation seed, and auditable match event log.
6. Run automated games and seasons.
7. Validate team strength, athlete statistics, upsets, fatigue, injuries, AI decision quality, cost, and latency.
8. Test whether public information supports meaningful predictions.

## Phase 0.5: Functional sports loop

1. Display teams, athletes, schedules, standings, and public information.
2. Place and lock match-winner predictions.
3. Simulate and settle matches server-side.
4. Replay event logs through a simple interface.
5. Record credit transactions and prediction history.

## Phase 1: 3D vertical slice

Build the one-city scope defined in [[Design/Decisions/DEC-002 First Playable Scope]].

## Future shared simulation layer

After the basketball loop is stable, pilot the shared Athlete Life Brain with a few daily choices: train, rest, recover, and socialize. Expand into relationships, nightlife, media, discipline, career decisions, and other sports only after the smaller loop produces believable, auditable consequences.

The shared life, world, memory, and learning layers will support every sport. Each new sport receives its own AI decision brain and authoritative rules engine. See [[Design/Decisions/DEC-003 Multi-Brain AI Architecture]].

## Next unresolved decisions

- Engine selection.
- First city identity.
- First two team identities.
- Minimal athlete attributes.
- Initial LLM provider/model and cost/latency budget.
- Minimal Athlete Life Brain traits and daily choices.
- AI evaluation criteria and model-update cadence.
- Ranked competition scoring.
- Match schedule and season length.
