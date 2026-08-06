---
tags:
  - decision
  - beta
  - basketball
  - schedule
  - wagering
status: accepted
date: 2026-07-24
---

# DEC-018 Canonical Local-Beta Schedule Timing

## Decision

The first active local-beta basketball schedule record uses these exact rules:

- schema `oddswell-canonical-scheduled-game-v1`, record version `1`;
- fresh active Season `1`, Game `1`;
- Harbor City Waves at home and Mesa Vista Sol away;
- `season_created_unix` supplied only by the authoritative GameMode transition;
- tipoff exactly `1,800` seconds after season creation;
- Match Winner offer eligibility begins at season creation;
- no offer is created or published by the schedule transition;
- status `scheduled_unplayed`;
- environment `local_beta`, timing authority `server`, and `production_timing = false`.

The first valid creation time is immutable. An exact retry returns the saved record; it does not reschedule the game from the new wall clock.

## Archive boundary

This active local-beta schedule is a separate SaveGame record. It does not modify, replace, relabel, or consume the immutable `PublicSeason1.json` benchmark archive, its Harbor City Waves `101` to Mesa Vista Sol `104` result, or its sealed replay.

The shared numerical Season `1`, Game `1` identity is interpreted inside the explicit active local-beta schedule schema. Later code must use the record schema and status instead of treating the archived benchmark result as the active game's result.

## Fail-closed boundary

An existing valid record is a duplicate. An unsupported schema/version, conflicting team/game identity, invalid timing, published-offer flag, production-timing flag, or status other than `scheduled_unplayed` is rejected without rewrite. Any future result, score, winner, replay link, cancellation, or settlement must use a separately approved immutable record rather than mutating this scheduled-game record.

The record contains no seed, RNG state, score, winner, replay/action tape, private athlete state, Odds Bucks/economy data, or user data.

## Production boundary

The current GameMode clock is server-owned only inside this local executable; it is not a trusted production backend clock. This decision does not authorize an offer, wager request, debit, lock, simulation, result, settlement, correction, account, backend, deployment, payment, real money, or retraining.
