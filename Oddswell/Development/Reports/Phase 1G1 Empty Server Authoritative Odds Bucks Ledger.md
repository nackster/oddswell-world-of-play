---
tags:
  - development
  - beta
  - unreal
  - economy
  - odds-bucks
  - phase-1g
status: complete
date: 2026-07-21
---

# Phase 1G.1 Empty Server-Authoritative Odds Bucks Ledger

## Outcome

Phase 1G.1 is complete. Sundale now owns one empty virtual Odds Bucks ledger inside its authoritative Unreal `GameMode`. A packaged Windows process starts that authority with exactly `0` entries and a `0` balance.

The ledger accepts only non-empty server commands with a non-zero delta and reason. Entries receive an increasing sequence number and preserve the balance after each append. An exact command retry is idempotent and cannot double-apply; conflicting reuse of a command ID, overflow, overspend, blank commands, missing reasons, and zero deltas are rejected without appending.

Ponytail kept this to one small ledger type owned by the existing server-only game mode. No database, service, framework, plugin, dependency, client RPC, replicated balance, account layer, or speculative economy abstraction was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 editor and game compilation | Passed |
| Focused ledger automation | `1/1` passed |
| Full native `OddsWell` automation | `11/11` passed |
| Final Windows BuildCookRun | Passed in `65.02s` |
| Final static package | `53` files, `1,042,651,904` bytes |
| Packaged Sundale authority | `entries=0`, `balance=0`, append-only and idempotent, client commands/real money/wagering disabled |
| Frozen simulator regression | `65/65` passed in `121.038s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged hashes and counts |
| Python compilation | Passed |
| Cost | `$0.00` |

## Truth boundary

This phase proves an in-memory, server-owned ledger primitive and its command rules. It does not yet prove player/account identity, disk or backend persistence, restart/reconnect recovery, a job, earning, starting balance, allowance, recovery floor, price, purchase, wager, payout, settlement, Admin reconciliation, deployment, real-money connection, or second currency.

The positive and negative amounts used by the native automation are test fixtures, not approved game-economy values. Runtime starts empty and issues no currency command.

## Next owner gate

Phase 1G.2 needs one job fantasy and one interaction. The smallest recommendation is to reuse Sundale's existing `Job` location and let the player press `E` to complete one clearly labeled placeholder shift. No Odds Bucks should be credited until the owner separately freezes the payout and recovery rules.
