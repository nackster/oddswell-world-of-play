---
tags:
  - development
  - phase-1d
  - multiplayer
  - unreal
status: complete
date: 2026-07-20
---

# Phase 1D.1 — Local Two-Client Shared City Presence

## Outcome

Two playable local processes join the same packaged Sundale graybox through Unreal Engine 5.8's native listen-server path. Both receive server-assigned temporary labels, can occupy the same space without blocking, and observe one another. The server receives and measures the joining client's normal character movement.

This is the first local presence proof, not production multiplayer. The approved boundary is recorded in [[Design/Decisions/DEC-010 Phase 1D Shared City Defaults]] and the order remains controlled by [[Development/Beta Delivery Roadmap]].

## Smallest implementation

- The existing `ACharacter` explicitly enables native actor and movement replication.
- The server assigns one replicated integer identity at spawn. A built-in text-render component displays `Player 1` or `Player 2`; no account, permanent username, or identity service exists.
- Networked players spawn `200 cm` apart.
- Player capsules ignore only Unreal's Pawn collision channel, so players pass through one another while existing world and blocking-floor collision remain intact.
- An opt-in `-SharedCityQa` trace uses ordinary `AddMovementInput` on the joining client. The authoritative server records the resulting displacement.
- No plugin, framework, online subsystem, external host, account service, chat, voice, matchmaking, or new dependency was added.

## Packaged evidence

The Windows Development package was cooked explicitly with `/Game/Maps/SundaleGraybox`. The final BuildCookRun succeeded in `53.07s`; the archive contains `53` files totaling `1,041,716,034` bytes.

One packaged listen-server process bound only to `127.0.0.1:7787`. One second packaged process connected to that loopback address and was welcomed into `/Game/Maps/SundaleGraybox` with `OddsWellLocomotionGameMode`.

Accepted trace:

| Evidence | Result |
| --- | --- |
| Server join count | `2` local playable clients |
| Server world | `SundaleGraybox` |
| Spawn spacing | `200 cm` |
| Listen address | `127.0.0.1:7787` |
| Server visibility | `Player 1` saw `Player 2`; 2 labeled actors |
| Client visibility | `Player 2` saw `Player 1`; 2 labeled actors |
| Authoritative movement | server measured `Player 2` moving `300.2 cm` |
| Player collision | Pawn channel ignored; world collision unchanged |
| Process exits | server `0`, client `0` |

No fatal error or Unreal ensure was found in the native automation, server, or client logs. The missing local appearance save warnings are the already-approved Phase 1B fallback behavior and do not affect this presence gate.

## Regression and integrity

- UE 5.8 editor build: passed.
- UE 5.8 game build: passed.
- Native `OddsWell.Character` automation: `5/5` passed.
- Frozen Python regressions: `65/65` passed in `159.452s`.
- Brain Admin self-check: passed.
- Python compilation: passed.
- Generated builds, cooked content, logs, and runtime output remain ignored.
- Cost: `$0.00`.

## Scope boundary

Appearance and clothing are not yet synchronized. Each process can still resolve the existing local fallback appearance for replicated actors, so Phase 1D.1 makes no cross-client appearance claim. It also adds no reconnect, persistence service, capacity ceiling, external hosting, region, account, login, matchmaking, invitation, friend, chat, voice, blocking/reporting control, moderation, ownership transfer, trading, store, Odds Bucks, wager, final art, model, training, or retraining behavior.

## Next gate

Phase 1D.2 sends each player's selected placeholder preset plus equipped starter top/bottom through the same native server-authoritative character path. Both clients must agree on both players' visible state before reconnect work begins.
