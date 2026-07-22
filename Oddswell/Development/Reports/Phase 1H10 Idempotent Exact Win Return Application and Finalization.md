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

# Phase 1H.10 Idempotent Exact-Win Return Application and Finalization

## Outcome

Phase 1H.10 applies the already-bound Phase 1H.9 return exactly once for the isolated Mesa-selected winning QA chain. A caller supplies only a new finalization/application command ID and the exact decision ID. Saved evidence derives and revalidates the request, lock, sealed result, offer, selected probability, approved formula, stake, winner, and return.

One atomic SaveGame write appends exactly one `match_winner_payout` ledger entry for `+100` and one separate immutable `settled_won` finalization. The ledger moves from `2` entries / balance `60` to `3` entries / balance `160`. The job cooldown and prior `decided_pending_apply` decision remain unchanged; there is no separate stake-return entry.

Exact retry returns the same finalization without another credit. Conflicting command reuse, a second finalization, wrong or missing chain evidence, a non-winning decision, wrong probability/formula/return, malformed persistence, tamper, or an extra ledger mutation fails closed without rewriting state. Schema v7 loss history migrates intact and no migration invents a winning finalization.

Ponytail reused the existing ledger, SaveGame, decision chain, and native economy automation. No dependency, projection, Admin surface, UI, refund, void, correction, alternate market, backend, or brain behavior was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed |
| Focused native economy automation | `1/1` passed |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Exact win application | One `+100` `match_winner_payout`; ledger `2/60 -> 3/160`; cooldown unchanged |
| Separate immutable finalization | `settled_won`, return applied `100`, observed ledger count `3`, observed balance `160` |
| Retry and rejection behavior | Exact retry is idempotent; conflicts, second finalization, loss, wrong chain/formula, malformed data, tamper, and extra mutation fail closed |
| Cold persistence | Exact decision, payout entry, and finalization reload together; decision remains `decided_pending_apply` |
| Migration and loss preservation | Schema v7 preserves the exact loss chain/history and invents no win finalization; pending-win migration also invents none |
| Focused odds-contract tests | `3/3` passed in `0.048s` |
| Frozen Python regression | `65/65` passed in `152.531s` under the accepted Codex Python 3.12 runtime, with the timing-sensitive test first and the process verified at High priority |
| Timing guard | Isolated High-priority run passed in `59.125s` |
| Brain Admin self-check | Passed unchanged |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, and fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, and SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is one isolated machine-local exact-win application and finalization proof. It is not shown in Brain Admin or player history. The existing exact-loss reconciliation remains the only wager Operations card.

No winning reconciliation/history, player route/UI, refund, void, correction, alternate wager, prop market, online account, trusted clock, backend, deployment, payment, real-money connection, or basketball/Athlete Life brain change is implemented.

## Next candidate gate

Scope Director review only: select the smallest remaining Match Winner evidence requirement after exact win application/finalization. Winning read-only reconciliation/history is the nearest evidence gap; void/refund, correction, and player-facing history/UI remain separate unproved gates.
