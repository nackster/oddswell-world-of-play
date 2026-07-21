---
tags:
  - development
  - beta
  - unreal
  - economy
  - odds-bucks
  - job
  - phase-1g
status: complete
date: 2026-07-21
---

# Phase 1G.4 Rolling 24-Hour Job Recovery

## Outcome

Phase 1G.4 is complete for one local saved profile. A new profile starts at **0 Odds Bucks**, the existing validated placeholder shift pays **100**, and the next shift becomes eligible after a rolling **24-hour** cooldown. The first payout counts as period one, balances accumulate, and there is no separate allowance or missed-period catch-up.

The existing Unreal SaveGame schema now stores one next-eligible UTC timestamp beside the validated append-only ledger. An eligible shift creates a stable scheduled command, saves the candidate ledger and new timestamp before replacing live state, and schedules the next opportunity from the accepted time. The prior schema migrates without inventing a second payout.

Ponytail kept the change inside the existing ledger, SaveGame, GameMode, and server-RPC path. No service, database, account layer, general scheduler, dependency, allowance system, or second economy was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 editor compilation | Passed in `11.30s` |
| UE 5.8 game compilation | Passed in `18.37s` |
| Focused ledger persistence and migration automation | `1/1` passed |
| Full native `OddsWell` automation | `11/11` passed |
| Clean Windows BuildCookRun | Passed in `102.16s` |
| Static Windows package | `54` files, `1,042,817,855` bytes |
| Packaged authority rejection | Outside-location request rejected; no credit |
| First eligible completion | One `+100` entry; balance `100` |
| Immediate retry | Blocked by cooldown; still `1` entry and balance `100` |
| Second eligible completion | After `86,400` QA seconds, one new `+100`; `2` entries and balance `200` |
| Same-process second retry | Blocked; still `2` entries and balance `200` |
| Cold second process | Restored `2` entries, balance `200`, and exact next-eligible timestamp from disk |
| Restart-boundary proof | Blocked one second before eligibility; credited at eligibility for `3` entries and balance `300` |
| QA save cleanup | Passed; isolated save absent from workspace and packaged local-save paths |
| Frozen simulator regression | `65/65` passed in `157.595s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged `421` frames, `2` teams, `12` athletes, and `20` games |
| Python compilation | Passed |
| Cost | `$0.00` |

Packaging used Unreal's already-installed signed local Zen helper on loopback port `8558`. No external service or paid dependency was introduced.

## Truth boundary

This proves deterministic recovery behavior for one machine-local saved profile across cold packaged processes. Production eligibility still needs trusted server time and account authority. A player who changes the local machine clock can influence this placeholder, so this is not anti-cheat, backend persistence, online reconnect, cloud sync, or multi-device recovery evidence.

No separate allowance, catch-up payout, recovery-floor behavior after wagering, price, purchase, wager, settlement, Admin reconciliation, deployment, real-money connection, or second currency is implemented.

## Next gate

Phase 1G.5 should expose the existing authoritative ledger entries, current balance, and next-job eligibility as truthful read-only Brain Admin reconciliation. It must not add credit commands or claim backend/account authority. Phase 1H wagering does not begin yet.
