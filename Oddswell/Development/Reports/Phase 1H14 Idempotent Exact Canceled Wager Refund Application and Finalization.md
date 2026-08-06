---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-22
---

# Phase 1H.14 Idempotent Exact Canceled-Wager Refund Application and Finalization

## Outcome

Phase 1H.14 atomically applies and finalizes the exact noncanonical Phase 1H.13 Season 99, Game 1 canceled-wager refund. The caller supplies only one finalization/refund command ID plus the exact void-decision ID. Validated saved evidence derives the full cancellation, request, lock, offer, selection, stake, reason, outcome, and refund chain.

One SaveGame write appends exactly one sequence-`3` `+40` `match_winner_refund` ledger entry and one separate immutable `settled_void` finalization. The isolated ledger changes from `2` entries / balance `60` to `3` entries / balance `100`. The Phase 1H.13 decision remains immutable as `decided_void_pending_refund`.

Exact retry returns the same finalization without another credit. Conflicting command reuse, a second finalization, unknown or mismatched evidence, normal-result overlap, tampered finalization values, malformed status, wrong refund ledger evidence, unexpected extra ledger mutation, and malformed persisted state fail closed without rewrite. Schema v10 migrates to v11 with zero invented finalizations and preserves the pending H13 decision.

Ponytail reused the existing exact-win atomic finalization pattern, SaveGame state, ledger append primitive, and native economy automation. No generalized refund service, dependency, reconciliation path, or UI was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor builds | Passed in `14.2s` and final `11.2s` |
| Focused native economy automation | `1/1` passed with exit code `0` |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Focused odds-contract tests | `3/3` passed in `0.046s` |
| Exact void refund | Sequence `3`; `+40`; `match_winner_refund`; balance `100`; one `settled_void` finalization |
| Idempotency and mutual exclusion | Exact retry is duplicate-safe; conflicts, second finalization, unknown decision, identity overlap, and normal outcome paths reject |
| Migration and cold load | Schema v10 migrates to v11 with zero invented finalizations; H13 remains pending; exact H14 finalization survives cold load |
| Tamper and mutation rejection | Wrong applied value, malformed status, wrong refund reason, and extra ledger mutation fail closed without rewrite |
| Frozen timing guard | `1/1` passed in `54.531s` under canonical Codex Python 3.12, PID `42460` verified at High priority |
| Frozen Python regression | The unchanged frozen `65/65` set passed inside an ordered `68/68` run in `131.613s`; the timing-sensitive test ran first and PID `38408` was verified at High priority |
| Brain Admin self-check | Passed unchanged |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is one isolated machine-local exact refund application/finalization proof. It does not add refund reconciliation, an Admin card, player history or controls, generalized cancellation/refund handling, correction or timeout policy, prop markets, an online account/backend, deployment, payment, real-money connection, or any Basketball Brain, Athlete Life Brain, replay, prediction, or league behavior.

The canonical Season 1, Game 1 result is unchanged. The old exact loss remains `2/60`, the old exact win remains `3/160`, and the new noncanonical canceled-wager proof is exactly `3/100`.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. Read-only void reconciliation, correction policy, and player-facing history/UI remain separate unproved gates. Phase 1H.15 has not begun.
