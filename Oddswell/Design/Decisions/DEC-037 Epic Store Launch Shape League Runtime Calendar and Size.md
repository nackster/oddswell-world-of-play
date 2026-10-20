---
tags:
  - decision
  - launch
  - league
status: owner-decision
date: 2026-10-20
---

# DEC-037 Epic Store Launch Shape, League Runtime, Calendar and Size

## Context and authority

On 2026-10-20 the owner set the release goal: sell OddsWell on the Epic Games Store for $9.99 on Windows PC. [[Development/Epic Store Launch Plan]] then set out the blocking decisions, and the owner chose the recommended option for each of the first four.

These choices change some items the [[Design/Beta Game Bible]] previously marked LOCKED. The owner's newest explicit decision takes precedence under the Bible's authority order.

## Decisions

1. **Launch shape: single-player first.** The paid launch is a single-player city. The shared online city becomes a later free update and is not a launch requirement. This supersedes, for launch scope, the Bible's LOCKED "the beta city is multiplayer" and "players can walk around the city together".
2. **League runtime: port the simulator into the game.** The basketball simulator moves from Python into the Unreal C++ game. Each save gets its own seeded league. The existing Python implementation and tests are the reference the port is checked against.
3. **Time: in-game calendar.** Jobs, game schedules and progression run on in-game days, which the player advances by playing and by sleeping at the apartment. This replaces the real-world rolling 24-hour job cooldown (DEC-015) and the real-time tipoff timing (DEC-018) for the player path.
4. **League size: 8 fictional teams, about 28 regular-season games per team, plus playoffs, with repeatable seasons.** This resolves Bible open item 6. An 82-game "full season" may return later as an option.

## Preserved boundaries

These rules remain in force inside the single-player game:

- The append-only Odds Bucks ledger and idempotent settlement.
- Wagers, purchases and appearance never influence simulated outcomes.
- Odds come only from equal public pregame information.
- Watching or skipping never changes a sealed result.
- Odds Bucks have no real-money purchase or cash-out.

All teams, athletes and identities remain fictional.

## Not decided here

Not decided here: the character system (plan D5), launch wager markets (D6), the content target (D7), rating and wording (D8), process (D9) and the name check (D10).
