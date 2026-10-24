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

# Phase 1H.20 Immutable Authoritative Upcoming QA Cancellation Evidence

## Outcome

Phase 1H.20 records one server-owned canceled-game disposition for the exact noncanonical H17 request and H19 lock. At authoritative QA time `2100086700`, five minutes after game-start lock, the server writes fixed cancellation command `qa:h20:match_winner:cancellation:1` and fixed evidence ID `qa:h20:match_winner:cancellation:evidence:1` for Season `100`, Game `1`, reason `game_canceled`, and status `closed_canceled`.

Ponytail reused `RecordOddsWellMatchWinnerCanceledGame`, the existing SaveGame schema, the exact H17/H19 chain, and the GameMode QA clock. The parameterless production transition accepts no player command, evidence ID, request/lock identity, game identity, reason, status, or timestamp. It adds no result, replay, simulation, settlement, refund decision, credit, finalization, UI, service, schema, or dependency.

## Exact authority and preservation

The transition independently requires the current SaveGame schema, sequence-`1` `+100` job credit, sequence-`2` `-40` stake debit, balance `60`, job cooldown `2100086400`, one exact H17 request, one exact H19 lock, and no result, settlement, finalization, cancellation, or void evidence. The request must still bind the exact offer/version and teams, Sparks selection, stake `40`, accepted time `2100000000`, and lock time `2100086400`. The lock must still bind fixed command `qa:h19:match_winner:lock:1`, exact Season `100`, Game `1`, and decision `locked`.

Only one immutable cancellation record is added. The H17 request/debit and H19 lock remain field-for-field unchanged. Ledger count remains `2`, balance remains `60`, and the job cooldown remains `2100086400`. The canceled SaveGame is `5,267` bytes with SHA-256 `c5bff6e8aa0564859abf1ebba5a1994bfe3396593120661f3c75328fe4335012`.

## Idempotency and fail-closed behavior

A separate cold packaged process retries the same fixed transition and receives `DUPLICATE`. Wrong request or lock links, wrong game or time, wrong evidence, conflicting command reuse, a second cancellation, malformed input, a fabricated normal result, and completed-H16 identity all reject without changing the serialized canceled state.

Native mutation coverage also proves malformed H17 request, H19 lock, H20 cancellation, and invented persisted result evidence fail closed. The verifier removes the isolated QA save only after the exact retry and full zero-mutation rejection audit pass.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H20 cancellation | `1/1` passed |
| Full native OddsWell automation | `15/15` passed |
| Focused odds contracts | `3/3` passed in `0.045s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `140.932s` |
| Brain Admin self-check | Passed unchanged |
| Editor target | Passed in `14.42s` |
| Game target | Passed in `19.39s` |
| Windows BuildCookRun | Passed in `52.26s` |
| Packaged transition | H17 seed, H19 lock, H20 cancellation, and H20 cold verifier passed in separate processes |
| Pending H17 state | `3,737` bytes, SHA-256 `8d89d7ea1b1b3958a3b269b257972a2598412d2cc3a9905f2ad7a04d2eb1c99a` |
| Locked H19 state | `4,306` bytes, SHA-256 `8b2c3b41aed618b559c6f7c76b27d065e7e42266099c776e3ba09806b48d950b` |
| Canceled H20 state | `5,267` bytes, SHA-256 `c5bff6e8aa0564859abf1ebba5a1994bfe3396593120661f3c75328fe4335012` |
| Canonical league | Deterministic re-export remained `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | Remained `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| Cost | `$0.00` |

## Truth boundary

This is authoritative cancellation evidence for one noncanonical machine-local QA game. It deliberately records no normal result. It does not decide whether a refund is due, add a credit, apply or finalize a refund, settle the wager, publish player/Admin UI, generalize cancellation policy, alter canonical games or prior exact histories, change the simulator or any brain, add an account/backend, connect real money, deploy, or retrain anything.

## Next candidate gate

Scope Director review should decide whether the smallest next Match Winner requirement is an exact void/refund-due decision for this H20 chain or a different beta dependency. Refund application/finalization, read-only history, correction, canonical future-game integration, and broader player history remain separate unproved gates. No later phase has begun.
