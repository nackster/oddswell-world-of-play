---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-23
---

# Phase 1H.19 Exact Upcoming QA Game-Start Lock

## Outcome

Phase 1H.19 adds one server-owned game-start transition for the exact noncanonical Phase 1H.17 QA request. At authoritative QA time `2100086400`, the server issues fixed command `qa:h19:match_winner:lock:1` for request `qa:h17:match_winner:request:1`, Season `100`, Game `1`, and persists exactly one immutable `locked` record.

Ponytail reused `LockOddsWellMatchWinnerRequest`, the existing SaveGame, the H17 request and offer, and the GameMode QA clock. The production transition accepts no player command ID, request ID, game identity, or timestamp. It adds no UI, framework, dependency, schema, result, replay, simulation, or settlement path.

## Exact authority and preservation

The GameMode starts the isolated QA proof one second before lock. Its server clock advances to the exact accepted game start before the parameterless H19 transition can run. The transition independently requires the exact current SaveGame schema, sequence-`1` `+100` job credit, sequence-`2` `-40` stake debit, one H17 request, exact offer ID/version and teams, Sparks selection, stake `40`, accepted time `2100000000`, lock time and job cooldown `2100086400`, balance `60`, and no result, settlement, finalization, cancellation, or void evidence.

The lock adds one record only. The H17 request, offer link, selection, stake, accepted time, debit sequence/delta/reason/balance, job cooldown, two-entry ledger, and balance `60` remain byte-for-value. The locked SaveGame is `4,306` bytes with SHA-256 `8b2c3b41aed618b559c6f7c76b27d065e7e42266099c776e3ba09806b48d950b`.

## Idempotency and fail-closed behavior

A separate cold packaged process retries the same fixed transition and receives `DUPLICATE` with the same record. Unknown request, wrong game, early or late time, conflicting command reuse, a second lock command, completed-H16 identity, and invented time all reject without changing the serialized locked state.

Native mutation coverage also proves malformed request, debit, or offer evidence rejects the exact H19 transition. No partial or replacement lock is written. The cold verifier removes the isolated QA save after all checks pass.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H19 lock | `1/1` passed |
| Full native OddsWell automation | `14/14` passed |
| Focused odds contracts | `3/3` passed in `0.047s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `146.516s` |
| Brain Admin self-check | Passed unchanged |
| Editor and game targets | Initial and final source-state builds passed |
| Windows BuildCookRun | Successful package passes in `50.98s`, `47.45s`, and final `38.57s`; an earlier attempt stopped only because the local Zen service was unavailable |
| Packaged transition | Separate H17 seed, H19 lock, and H19 cold-verifier processes passed |
| Pending state before lock | `3,737` bytes, SHA-256 `8d89d7ea1b1b3958a3b269b257972a2598412d2cc3a9905f2ad7a04d2eb1c99a` |
| Locked state | `4,306` bytes, SHA-256 `8b2c3b41aed618b559c6f7c76b27d065e7e42266099c776e3ba09806b48d950b` |
| Canonical league | Deterministic re-export remained `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | Remained `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| Cost | `$0.00` |

## Truth boundary

This is one exact lock for one noncanonical machine-local QA request. It does not prove a canonical future-game request, production scheduler or trusted clock, player lock control, result link, replay, simulation, settlement, refund, correction, generalized history, account, backend, deployment, payment, real-money connection, retraining, or brain/model change.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement from the new locked H17 chain. Authoritative result integration, settlement integration, correction policy, and broader player history remain separate unproved gates. No Phase 1H.20 work has begun.
