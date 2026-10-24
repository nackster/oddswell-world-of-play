---
tags:
  - development
  - beta
  - unreal
  - economy
  - odds-bucks
  - admin
  - phase-1g
status: complete
date: 2026-07-21
---

# Phase 1G.5 Read-Only Odds Bucks Admin Reconciliation

## Outcome

Phase 1G.5 is complete for the current machine-local profile. Unreal now publishes a validated read-only JSON projection after loading the Odds Bucks ledger and after each accepted job payout. Brain Admin independently validates the projection before showing its balance, entry count, next-job eligibility, and complete append-only entry list on the Operations page.

The Unreal SaveGame ledger remains authoritative. The JSON file is output-only evidence: the game never reads it back, Brain Admin exposes no economy mutation route or button, and a missing or inconsistent projection fails closed without displaying a balance.

Ponytail kept the change within the existing ledger, GameMode, local Admin server, and Operations page. No service, database, account system, framework, dependency, payment path, wager, or second currency was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 editor compilation | Passed in `12.71s` |
| UE 5.8 game compilation | Passed in `20.61s` |
| Focused ledger/projection automation | `1/1` passed |
| Full native `OddsWell` automation | `11/11` passed |
| Clean Windows BuildCookRun | Passed in `100.75s` |
| Static Windows package | `56` files, `1,042,923,557` bytes |
| First packaged QA process | Projection advanced from `0` entries to `2`, balance `200`, with `86,400` seconds remaining |
| Python consumption of Unreal QA output | Validated `2` exact entries, balance `200`, and the exact cooldown |
| Cold second packaged process | Restored `2` entries and balance `200`, then projected `3` entries and balance `300` at eligibility |
| QA cleanup | Isolated QA save and QA projection removed |
| Normal packaged launch | Published a valid normal empty-profile projection with balance `0` and first shift available |
| Admin fail-closed check | Accepted the valid projection and rejected a corrupted projection without showing a balance |
| Browser visual check | Operations rendered at `1280x720` with four readable metrics, no horizontal overflow, no mutation controls, and zero console errors |
| Frozen simulator regression | `65/65` passed in `140.036s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Unchanged at `421` frames, `2` teams, `12` athletes, and `20` games |
| Runtime-log audit | Five Phase 1G.5 logs contain no fail, stale-projection, automation-failure, or fatal marker |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is local operator reconciliation, not a production economy console. The projection identifies its scope as `machine_local`, its time source as `local_machine_utc`, and itself as read only. It is regenerated from the validated Unreal ledger, written atomically, and validated again by Brain Admin, but it is not cryptographically signed or protected by authenticated server transport.

No account identity, trusted backend clock, cloud or multi-device recovery, authorization roles, economy command, price, purchase, wager, settlement, payment, deployment, real-money connection, or second currency is implemented. Production financial or wagering operations still require authentication, least privilege, confirmations, audit records, and legal/platform review.

## Phase 1G exit

Phase 1G exits for the current local-profile beta dependency: the player can earn, retain, cold-restore, and locally audit Odds Bucks through one non-paid job path. This does not claim an online or production economy.

## Next owner gate

Before Phase 1H begins, the owner must confirm the first wager market and its rules. The smallest recommendation is **Phase 1H.1 Match Winner owner decision**: keep Match Winner first, then freeze its displayed odds and payout formula, minimum and maximum stake, lock time, cancellation/correction behavior, and equal-public-information boundary. No wagering implementation is authorized by this report alone.
