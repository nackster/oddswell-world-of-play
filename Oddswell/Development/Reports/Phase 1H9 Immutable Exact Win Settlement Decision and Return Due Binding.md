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

# Phase 1H.9 Immutable Exact-Win Settlement Decision and Return-Due Binding

## Outcome

Phase 1H.9 proves one isolated machine-local winning decision for the existing Season 1, Game 1 Match Winner offer. The QA profile selects Mesa Vista Sol for `40` Odds Bucks, revalidates the exact offer with `WinProbabilityE8 = 40000000` and `floor(stake*100000000/win_probability_e8)`, consumes the existing request, game-start lock, and sealed Harbor `101`-`104` Mesa result, then persists `won`, `GrossReturnDue = 100`, and `decided_pending_apply`.

The decision binds the selected probability and approved payout formula. Exact retries return the same record. A missing exact offer, tampered probability or formula, mismatched chain, conflicting command reuse, second decision, malformed saved evidence, or wrong return fails closed without rewriting state.

Ponytail reused the existing decision record, persistence path, validator, and native economy automation. No dependency, SaveGame schema bump, finalization type, projection, Admin surface, or ledger command was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed |
| Focused native economy automation | `1/1` passed |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Exact win decision | Mesa selected; stake `40`; probability `40000000`; approved formula; `won`; return due `100`; `decided_pending_apply` |
| Retry and rejection behavior | Exact retry is idempotent; conflicts, tamper, malformed data, missing offer, and mismatches fail closed |
| Cold persistence | Exactly one winning decision reloads; no finalization is invented |
| Loss-chain preservation | The exact Phase 1H.6-1H.8 loss chain restores with `lost`, return due `0`, and `settled_lost` unchanged |
| Ledger invariance | Entry count `2`, balance `60`, and job cooldown remain unchanged; no entry is added |
| Focused odds-contract tests | `3/3` passed in `0.073s` |
| Frozen Python regression | `65/65` passed in `311.250s` with the unchanged time-sensitive life-performance test first and the test process verified at High priority; its isolated idle check also passed in `117.386s` |
| Brain Admin self-check | Passed unchanged |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, and fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, and SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

`GrossReturnDue = 100` is an immutable decision value only. It is not applied, credited, paid, finalized, reconciled, or shown to a player or Admin operator. No ledger entry is added, balance remains `60`, and the separate exact-loss finalization/history chain remains unchanged.

No winning payout/finalization, refund, void, correction, player route/history/UI, alternate wager, prop market, account, trusted clock, backend, deployment, payment, real-money connection, or brain change is implemented.

## Next candidate gate

Scope Director review only: select the smallest remaining Match Winner evidence requirement after exact win return-due binding. Winning return application/finalization, reconciliation/history, void/refund, correction, and player-facing history/UI remain separate unproved gates.
