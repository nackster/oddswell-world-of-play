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

# Phase 1H.13 Immutable Exact Canceled-Wager Void/Refund-Due Decision

## Outcome

Phase 1H.13 derives one immutable decision from the exact noncanonical Phase 1H.12 Season 99, Game 1 cancellation. The caller supplies only one void-decision command ID plus the exact cancellation command and evidence IDs. Validated saved evidence derives the accepted request, game-start lock, offer identity/schema/version, selected team, stake `40`, neutral reason `game_canceled`, outcome `voided`, refund due `40`, and status `decided_void_pending_refund`.

The separate `oddswell-match-winner-void-decision-v1` record does not change the Phase 1H.12 canceled-game disposition. Exact retry returns the same record. Unknown or mismatched cancellation identity, conflicting command reuse, a second decision, malformed or nonclosed cancellation evidence, wrong persisted values, or a chain with any sealed result, normal win/loss decision, or finalization fails closed.

The canceled chain cannot enter the normal result/settlement path. The canonical Season 1, Game 1 loss and win chains remain exact and unchanged. Schema v9 migrates to v10 with zero invented void decisions and preserves the existing canceled-game evidence.

Ponytail reused the existing SaveGame state, exact cancellation record, decision-validation pattern, and native economy automation. No generalized void service or new dependency was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor builds | Passed in `13.32s`, `9.74s`, and final `9.92s` |
| Focused native economy automation | `1/1` passed with exit code `0` |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Focused odds-contract tests | `3/3` passed in `0.048s` |
| Exact void decision | Season 99, Game 1; stake `40`; `game_canceled`; `voided`; refund due `40`; `decided_void_pending_refund` |
| Idempotency and mutual exclusion | Exact retry is duplicate-safe; conflicts, second decision, normal result/settlement/finalization paths, and identity mismatch reject |
| Migration and cold load | Schema v9 migrates to v10 with zero invented decisions; exact cancellation and decision survive cold load; old loss and win remain exact |
| Tamper rejection | Wrong refund due, malformed decision status, and nonclosed cancellation fail closed without mutation |
| Frozen timing guard | `1/1` passed in `62.332s` under canonical Codex Python 3.12, process verified at High priority |
| Frozen Python regression | `65/65` passed in `148.282s` with the unchanged timing-sensitive test first, process verified at High priority |
| Brain Admin self-check | Passed |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

Refund due `40` is a pending decision value only. No Odds Bucks entry was appended, no balance changed, and no refund was applied or finalized. The isolated ledger remains `2` entries and balance `60`.

No refund application, void finalization, reconciliation projection, Admin surface, player UI, generalized void/cancellation service, timeout policy, correction taxonomy, alternate market, backend, deployment, payment, real-money connection, or basketball/Athlete Life brain behavior was added.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. Applying/finalizing the exact refund, read-only reconciliation, correction, and player-facing history/UI remain separate unproved gates.
