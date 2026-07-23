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

# Phase 1H.22 Idempotent Exact Upcoming QA Refund Application and Finalization

## Outcome

Phase 1H.22 atomically applies the exact refund due from H21 and records one separate immutable `settled_void` finalization for the noncanonical H17/H19/H20/H21 QA chain. The fixed parameterless server transition owns command `qa:h22:match_winner:void-finalization:1` and reuses `FinalizeOddsWellMatchWinnerVoidRefund`; no player-supplied command, link, identity, amount, or status enters the path.

The transition appends ledger sequence `3`, delta `+40`, reason `match_winner_refund`, and balance `100`, then records refund due/applied `40`, observed ledger count `3`, observed balance `100`, and exact links to the H21 decision, H20 cancellation/evidence, H19 lock, and H17 request. H21 remains immutable as `decided_void_pending_refund`.

Ponytail reused the existing SaveGame schema, ledger primitive, finalization record, fixed QA identities, and GameMode path. No player/Admin UI, read-only history feature, correction path, canonical result, simulation, generalized service, backend, brain, dependency, payment, real-money connection, deployment, or retraining was added.

## Idempotency and fail-closed behavior

A cold packaged process restores the exact finalized state and returns `DUPLICATE` for the same fixed transition. Wrong decision or chain links, command conflict, a second finalization, tampered status or amount, fabricated normal-result overlap, malformed identity, and unexpected ledger evidence all reject with byte-stable zero mutation. The verifier removes the isolated QA save only after the duplicate and full rejection audit pass.

The exact finalized SaveGame is `8,849` bytes with SHA-256 `8c3d75d80c2da06797338727eb3481d7ba5c424cbfc3cd6eba28aea4703ca2f1`. The pre-finalization H21 state remains `6,724` bytes with SHA-256 `486876805ac94c6bf0775fcb2fd8c15490c4b45342ca8e2e8573a5bc2dfc705c`.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H22 finalization | `1/1` passed |
| Full native OddsWell automation | `17/17` passed, including the prior exact S99 void proof |
| Focused odds contracts | `3/3` passed in `0.045s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `144.229s` |
| Brain Admin self-check | Passed unchanged |
| Editor target | Final incremental build passed in `11.18s` |
| Game target | Passed in `17.46s` inside the accepted package build |
| Windows BuildCookRun | Passed in `66.75s` |
| Packaged chain | H17 seed → H19 lock → H20 cancellation → H21 decision → H22 finalization passed in separate transitions |
| Packaged cold verifier | Exact retry `duplicate`; wrong decision/link, conflict, second, tamper, normal-result overlap, malformed identity, and unexpected ledger rejected; `zero_mutation=true`; cleanup passed |
| Pending H17 state | `3,737` bytes, SHA-256 `8d89d7ea1b1b3958a3b269b257972a2598412d2cc3a9905f2ad7a04d2eb1c99a` |
| Locked H19 state | `4,306` bytes, SHA-256 `8b2c3b41aed618b559c6f7c76b27d065e7e42266099c776e3ba09806b48d950b` |
| Canceled H20 state | `5,267` bytes, SHA-256 `c5bff6e8aa0564859abf1ebba5a1994bfe3396593120661f3c75328fe4335012` |
| Decided H21 state | `6,724` bytes, SHA-256 `486876805ac94c6bf0775fcb2fd8c15490c4b45342ca8e2e8573a5bc2dfc705c` |
| Finalized H22 state | `8,849` bytes, SHA-256 `8c3d75d80c2da06797338727eb3481d7ba5c424cbfc3cd6eba28aea4703ca2f1` |
| Canonical league | `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| Cost | `$0.00` |

## Truth boundary

This completes refund application/finalization for one noncanonical machine-local QA game only. It is not a generalized void policy, player history, correction system, canonical future-game settlement, account/backend, or monetization path. The existing S99 reconciliation proof remains valid; the exact S100 QA chain is validated on cold load without creating a new history projection.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. Read-only history/reconciliation for this chain, correction, canonical future-game integration, and broader player history remain separate unproved gates. No Phase 1H.23 work has begun.
