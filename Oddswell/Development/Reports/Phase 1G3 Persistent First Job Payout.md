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

# Phase 1G.3 Persistent First Job Payout

## Outcome

Phase 1G.3 is complete for the approved local-profile slice. The server-validated Sundale placeholder shift now credits **100 Odds Bucks exactly once per local saved profile**. The player sees the credited balance after the first shift and an already-claimed message after later shifts.

The existing append-only ledger now serializes through Unreal SaveGame. Every saved entry is reconstructed through the same validation path, including sequence, command identity, delta, reason, and running balance. A candidate ledger is saved before it replaces the live ledger, so save failure cannot create an unsaved in-memory credit. Corrupt loads leave payouts disabled.

Ponytail kept the change inside the existing ledger, GameMode, server RPC, and SaveGame pattern. No database, account layer, service, dependency, generalized job system, timer, or second economy was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 editor compilation | Passed in `17.98s` |
| UE 5.8 game compilation | Passed in `17.00s` |
| Focused ledger persistence automation | `1/1` passed |
| Full native `OddsWell` automation | `11/11` passed |
| Windows BuildCookRun | Passed in `48.65s` after local Zen restart |
| Static Windows package | `54` files, `1,042,785,087` bytes |
| Packaged authority rejection | Outside-location request rejected; no command or credit |
| Packaged first completion | One `+100` command; `1` entry; balance `100` |
| Same-process retry | Duplicate; still `1` entry and balance `100` |
| Cold second process | Restored `1` entry and balance `100` from the isolated local save |
| Post-restart retry | Duplicate; still `1` entry and balance `100` |
| QA save cleanup | Passed and verified absent |
| Frozen simulator regression | `65/65` passed in `141.263s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged `421` frames, `2` teams, `12` athletes, and `20` games |
| Python compilation | Passed |
| Cost | `$0.00` |

The first clean packaging attempt encountered a transient refusal from Unreal's installed local Zen cache on loopback port `8558`. Starting that existing signed local helper and rerunning the unchanged package succeeded. This was a local tool-state issue, not a code or network-service dependency.

## Truth boundary

The proof covers one machine-local saved profile and a cold packaged process restart. It does not prove online account identity, production backend persistence, network-session reconnect, multi-device recovery, cloud sync, durable job-completion history beyond the ledger command, repeat income, cooldowns, daily cadence, allowance, zero-balance recovery, starting balance, prices, purchases, wagers, settlement, Admin reconciliation, deployment, real-money connection, or a second currency.

The `100` amount and once-per-local-profile limit are explicitly provisional under [[Design/Decisions/DEC-014 Phase 1G3 Provisional First Job Payout]].

## Next owner gate

Phase 1G.4 needs the smallest zero-balance recovery rule: starting balance, repeat or daily recovery amount, cadence, and eligibility. Those values must be owner-approved before another runtime credit path is built. Phase 1H wagering does not begin yet.
