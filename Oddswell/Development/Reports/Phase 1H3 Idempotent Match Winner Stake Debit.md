---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-21
---

# Phase 1H.3 Idempotent Match Winner Stake Debit

## Outcome

Phase 1H.3 adds the smallest server-owned wager mutation behind the Phase 1H.2 offer contract. One machine-local request can accept an exact, verified Match Winner offer before its lock time and persist an `accepted_pending_lock` record together with one append-only `match_winner_stake` Odds Bucks debit.

The request command ID is idempotent. An exact retry restores the original record without a second debit, while reuse with changed offer, team, or stake data fails closed. Invalid offers, unsupported teams, stakes outside `10`-`100` or off the `10`-credit increment, at-lock requests, insufficient balances, and malformed persisted links are rejected without changing saved state.

Ponytail kept this inside the existing native Odds Bucks SaveGame and ledger rather than adding a service, database, wager framework, or client screen. Schema v3 migrates the existing v1/v2 local saves without inventing a wager.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed after the bounded ledger change |
| Focused native Odds Bucks automation | `1/1` passed |
| Full native OddsWell automation | `11/11` passed with zero failures |
| Exact Phase 1H.2 offer identity | Native canonical SHA-256 matches the Python offer ID |
| Accepted request | One `40`-Odds-Bucks stake moves the job-funded balance from `100` to `60` |
| Durable reload | Disk reload preserves one request, one debit, balance `60`, and the job cooldown |
| Idempotency | Exact retry returns the saved request with no second debit |
| Rejection boundary | Tamper, conflicting command reuse, invalid stake/team, at-lock request, and insufficient balance add no record or ledger entry |
| Focused odds-contract tests | `3/3` passed |
| Frozen simulator regression | `65/65` passed in `144.957s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Unchanged at `421` frames, `2` teams, `12` athletes, and `20` games |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is a machine-local server-owned persistence primitive, not a player-facing wager flow or production account system. The accepted timestamp still comes from the local authoritative caller; no trusted backend clock, online identity, network request route, runtime offer publication, Unreal wager UI, or Admin wager view exists.

The debit is a pending stake only. No lock transition, cancellation, void/refund, sealed-result consumption, settlement, payout credit, correction, history screen, player prop, payment, real-money connection, or second currency is implemented. The Basketball Brain and frozen authoritative event log remain unchanged, and wager state has no path back into game outcomes.

## Next gate

Phase 1H.4 should prove one idempotent Match Winner lock transition at authoritative game start while preserving the accepted offer and stake exactly. It must not settle, refund, or credit a payout yet.
