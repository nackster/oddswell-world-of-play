---
tags:
  - development
  - beta
  - basketball
  - wagering
  - unreal
  - phase-1h
status: complete
date: 2026-07-23
---

# Phase 1H.23 Player-Facing Ticket Booth Odds Presentation Cleanup

## Outcome

The existing Sundale sportsbook route point is now presented to the player as the stadium ticket booth. When the player enters its interaction radius, the normal play prompt is exactly:

`Press E to open betting odds`

Pressing `E` opens a concise read-only basketball-odds panel with the matchup, both teams' decimal odds, the approved `10`–`100` Odds Bucks stake range, the game-start lock rule, and one `[E] CLOSE` instruction. Leaving the radius still closes the panel.

The always-on `Press L to open the public basketball league` hint was removed from normal play. Offer IDs, source versions, commitments, Unix timestamps, probabilities, gross-return tables, and QA wording remain available to validation/logging but no longer appear in this normal ticket-booth view.

## Ponytail boundary

This phase reuses the existing location radius, `E` interaction, validated public Match Winner offer, and native on-screen presentation. It adds one small display formatter and focused assertions. It does not add a widget framework, menu system, new map asset, ticket-booth art, wager submission, ledger mutation, offer formula, market, backend, payment, real-money path, simulator change, or brain change.

The native text panel is still a development placeholder. A production HUD, Escape menu, controls screen, and final stadium/ticket-booth art remain later presentation work.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Unreal editor target | Passed in `11.65s` |
| Windows Development BuildCookRun | Passed in `119.32s` |
| Focused native stadium/booth automation | `1/1` passed |
| Full native OddsWell automation | `17/17` passed |
| Frozen simulator and odds contracts | `68/68` passed in `242.746s` (`65` frozen plus `3` odds) |
| Timing-sensitive life-performance guard | `1/1` passed in `102.513s` before the full suite |
| Brain Admin self-check | Passed |
| Python compilation | Passed |
| Rendered ticket-booth QA | Passed; location and `E` path valid, view read-only, no submission or controls, ledger entries/balance unchanged at `0/0` |
| Visual inspection | One concise panel, one close instruction, no technical offer identity, commitment, or Unix timestamp |
| Cost | `$0.00` |

## Truth boundary and next gate

This proves the current normal-play presentation at one placeholder route point. It does not prove a finished betting menu, final booth model, canonical player wager submission, new-chain history, correction, broader player history, or production readiness.

The next Scope Director review should choose between the remaining Match Winner evidence gates and a separately scoped production-menu presentation gate according to the earliest beta dependency and owner priorities.
