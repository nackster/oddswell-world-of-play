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

# Phase 1H.21 Immutable Exact Upcoming QA Void Refund Due Decision

## Outcome

Phase 1H.21 records one server-owned `voided` / `decided_void_pending_refund` decision for the exact noncanonical H17 request, H19 lock, and H20 cancellation chain. The fixed parameterless transition owns decision command `qa:h21:match_winner:void-decision:1` and reuses `DecideOddsWellMatchWinnerVoidRefundDue` to derive Sundale Sparks, stake `40`, cancellation reason `game_canceled`, and refund due `40` from the existing immutable evidence.

Ponytail reused the existing SaveGame schema, generic exact void-decision primitive, fixed QA identities, and GameMode QA path. No player-supplied command, link, game identity, team, stake, outcome, refund amount, or status enters the production transition. No result, replay, simulation, settlement, refund application, credit, finalization, UI, service, schema, or dependency was added.

## Exact authority and preservation

The transition independently requires the current SaveGame schema, sequence-`1` `+100` job credit, sequence-`2` `-40` stake debit, balance `60`, job cooldown `2100086400`, and exactly one linked H17 request, H19 lock, and H20 cancellation. It binds the existing offer identity and version, Season `100`, Game `1`, Sparks selection, stake `40`, cancellation command `qa:h20:match_winner:cancellation:1`, evidence ID `qa:h20:match_winner:cancellation:evidence:1`, reason `game_canceled`, and status `closed_canceled`.

Only one immutable void/refund-due decision is added. The request, debit, lock, and cancellation remain field-for-field unchanged. Ledger count remains `2`, balance remains `60`, and the job cooldown remains `2100086400`; the refund is due but not applied. The decided SaveGame is `6,724` bytes with SHA-256 `486876805ac94c6bf0775fcb2fd8c15490c4b45342ca8e2e8573a5bc2dfc705c`.

## Idempotency and fail-closed behavior

A separate cold packaged process retries the same fixed transition and receives `DUPLICATE`. Wrong cancellation links or evidence, conflicting command reuse, a second decision, malformed input, and fabricated normal-result overlap all reject without changing the serialized decided state.

Native mutation coverage additionally proves that a wrong persisted cancellation status, refund amount, decision status, decision link, or normal-result overlap makes the exact H21 transition fail closed. The exact decision bytes restore after every case. The verifier removes the isolated QA save only after the duplicate and full zero-mutation rejection audit pass.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H21 decision | `1/1` passed |
| Full native OddsWell automation | `16/16` passed |
| Focused odds contracts | `3/3` passed in `0.045s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `141.229s` |
| Brain Admin self-check | Passed unchanged |
| Editor target | Final incremental build passed in `10.95s` |
| Game target | Passed in `20.06s` |
| Windows BuildCookRun | Passed in `52.50s` |
| Packaged transition | H17 seed, H19 lock, H20 cancellation, H21 decision, and H21 cold verifier passed in separate processes |
| Pending H17 state | `3,737` bytes, SHA-256 `8d89d7ea1b1b3958a3b269b257972a2598412d2cc3a9905f2ad7a04d2eb1c99a` |
| Locked H19 state | `4,306` bytes, SHA-256 `8b2c3b41aed618b559c6f7c76b27d065e7e42266099c776e3ba09806b48d950b` |
| Canceled H20 state | `5,267` bytes, SHA-256 `c5bff6e8aa0564859abf1ebba5a1994bfe3396593120661f3c75328fe4335012` |
| Decided H21 state | `6,724` bytes, SHA-256 `486876805ac94c6bf0775fcb2fd8c15490c4b45342ca8e2e8573a5bc2dfc705c` |
| Canonical league | Deterministic re-export remained `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | Remained `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| Cost | `$0.00` |

## Truth boundary

This is a refund-due decision for one noncanonical machine-local QA game. It does not apply or finalize the refund, append a ledger credit, settle the wager, publish player/Admin UI, add read-only history, generalize refund policy, alter canonical games or prior exact histories, change the simulator or any brain, add an account/backend, connect real money, deploy, or retrain anything.

## Next candidate gate

Scope Director review should decide whether the smallest next Match Winner requirement is exact refund application/finalization for this H21 decision or a different beta dependency. Read-only history, correction, canonical future-game integration, and broader player history remain separate unproved gates. No later phase has begun.
