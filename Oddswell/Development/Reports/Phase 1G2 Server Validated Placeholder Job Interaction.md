---
tags:
  - development
  - beta
  - unreal
  - economy
  - job
  - phase-1g
status: complete
date: 2026-07-21
---

# Phase 1G.2 Server-Validated Placeholder Job Interaction

## Outcome

Phase 1G.2 is complete. At Sundale's existing `Job` route marker, the player sees a clear prompt and may press `E` to complete the owner-approved placeholder shift. The owning server verifies the authoritative city and player position before accepting the request, then sends visible success or rejection feedback to that player.

The shift intentionally awards `0` Odds Bucks. The server logs the unchanged `0` balance and `0` ledger entries, and it never issues a ledger command. This keeps the approved interaction testable without inventing the still-open payout or recovery rules.

Ponytail reused the existing route marker, character input polling, server RPC pattern, and on-screen message path. No job actor, widget framework, mission system, timer, database, service, dependency, or second economy was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 editor and game compilation | Passed |
| Focused locomotion automation | `1/1` passed |
| Full native `OddsWell` automation | `11/11` passed |
| Final Windows BuildCookRun | Passed in `58.11s` |
| Final static package | `53` files, `1,042,682,240` bytes |
| Packaged outside-location request | Rejected by the server with no ledger command |
| Packaged in-location request | Completed at `Job`; client-visible feedback confirmed |
| Packaged economy boundary | `odds_bucks_awarded=0`, `ledger_entries=0`, `ledger_balance=0`, `payout_rules=false` |
| Frozen simulator regression | `65/65` passed in `119.209s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged hashes and counts |
| Python compilation | Passed |
| Cost | `$0.00` |

## Truth boundary

This is a generic placeholder shift, not final job fiction or content. Completion is session-local and is not yet a durable job-history record. There is no payout, command ID, account identity, persistence, restart/reconnect recovery, eligibility rule, cooldown, daily cadence, allowance, recovery floor, starting balance, price, purchase, wager, settlement, animation, final art, deployment, real-money connection, or second currency.

## Next owner gate

Phase 1G.3 needs a provisional job payout and a limit for its first persistent proof. The smallest recommendation is **100 Odds Bucks once per local saved profile**: one verified completion creates one idempotent credit, and a second process restores the exact ledger. Repeat and daily recovery rules can remain disabled until Phase 1G.4.
