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

# Phase 1H.15 Read-Only Exact Canceled-Wager Reconciliation History

## Outcome

Phase 1H.15 extends the existing `oddswell-match-winner-reconciliation-v1` writer, endpoint, independent Brain Admin validator, and single Operations card with one exact void branch. It publishes only from the fully validated noncanonical Season 99, Game 1 H12-to-H14 chain.

The projection binds the accepted request, sequence-`2` `-40` stake debit to balance `60`, game-start lock, cancellation command/evidence/time/schema/version with `game_canceled` and `closed_canceled`, immutable H13 `voided` decision with refund due `40` and `decided_void_pending_refund`, sequence-`3` `+40` `match_winner_refund` to balance `100`, and separate H14 `settled_void` finalization. The final history is exactly three ledger entries, balance `100`, and net `0`.

Brain Admin independently requires the exact QA identity, values, schemas, versions, and request-to-finalization links before displaying `VALIDATED QA FINALIZED VOID`. Missing, partial, stale, malformed, tampered, mixed normal-result, or forbidden invented result evidence fails closed without partial fields. The exact loss and win projections remain byte-equivalent after timestamp normalization.

Ponytail kept this to one early void branch in the existing writer and validator plus one conditional detail line in the existing card. No new framework, dependency, projection schema, endpoint, or card was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Editor build | Passed; `OddsBucksLedger.cpp` compiled and linked, UBT `10.47s` |
| Focused native economy automation | `1/1` passed with exit code `0` |
| Full native OddsWell automation | `11/11` passed with exit code `0` in `51.4s` |
| Focused odds-contract tests | `3/3` passed in `0.042s` under canonical Python 3.12 |
| Frozen simulator regression | Timing-sensitive guard ran first; canonical Python 3.12 passed `65/65` in `145.197s` with exit code `0`. The child process inherited Normal priority; no frozen code or threshold changed. |
| Brain Admin self-check | Passed exact void, tampered-link, wrong-refund, forbidden-result, and no-partial fixtures |
| Exact void history | S99G1; stake `2/-40/60`; cancellation `game_canceled` / `closed_canceled`; H13 pending; refund `3/+40/100`; `settled_void`; count `3`; balance `100`; net `0` |
| Loss/win invariance | Existing exact loss `2/60/-40` and exact win `3/160/+60` writers and projections remain unchanged |
| Live browser/API proof | Operations showed `VALIDATED QA FINALIZED VOID`, exact request-to-finalization and ledger links, zero controls, no overflow, and no winner, score, replay seal, or result command fields |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Compilation and diff hygiene | Python compileall and whitespace validation passed |
| Cost | `$0.00` |

## Truth boundary

This is one machine-local, QA-only, read-only Operations history proof for the exact canceled wager. It adds no SaveGame schema or ledger/gameplay mutation and cannot affect basketball, athlete behavior, predictions, replays, or league outcomes. It invents no result, winner, score, replay, payout, or gross-return evidence.

No player-facing wager history, correction or timeout policy, generalized cancellation/refund service, alternate market, prop, account, trusted backend, deployment, payment, real-money connection, retraining, or brain behavior was added.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. Correction policy and player-facing history/UI remain separate unproved gates. Phase 1H.16 has not begun.
