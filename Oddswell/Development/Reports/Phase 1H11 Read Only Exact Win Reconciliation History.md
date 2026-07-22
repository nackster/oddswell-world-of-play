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

# Phase 1H.11 Read-Only Exact-Win Reconciliation History

## Outcome

Phase 1H.11 extends the existing `oddswell-match-winner-reconciliation-v1` projection and existing Brain Admin Operations card to the fully validated Phase 1H.10 win. It does not add a second projection, history framework, SaveGame schema, command, or mutation path.

The server-authored projection binds Mesa Vista Sol selected for stake `40`, probability `40000000`, the approved integer payout formula, the sealed Harbor `101`-`104` Mesa result, `won`, return due/applied `100`, exact stake entry `2/-40/60`, exact payout entry `3/+100/160`, `settled_won`, ledger count `3`, balance `160`, and net `+60`. It writes atomically after exact-win finalization and after a validated cold load. Missing, malformed, tampered, or extra-mutated state removes stale output and publishes nothing.

Brain Admin independently validates every fixed value and identity link before returning or displaying the concise output-only history. Invalid or partial evidence reveals no wager values and no controls. The exact-loss projection and Operations response remain unchanged at ledger count `2`, balance `60`, net `-40`, and `settled_lost`.

Ponytail reused the existing v1 writer, endpoint, validator, card, and native economy automation. No dependency, parallel framework, player UI, refund, void, correction, alternate market, backend, or brain behavior was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed in `8.86s` |
| Focused native economy automation | `1/1` passed |
| Full native OddsWell automation | `11/11` passed with exit code `0` |
| Exact win projection | Mesa; stake `40`; probability `40000000`; approved formula; sealed `101-104`; won/due/applied `100`; settled won |
| Ledger evidence | Stake `2/-40/60`; payout `3/+100/160`; count `3`; balance `160`; net `+60`; exact IDs and reasons |
| Cold and rejection behavior | Finalization and cold load publish atomically; stale, malformed, partial, tampered, and extra-mutated evidence publishes nothing |
| Exact-loss preservation | Existing loss projection/card remains count `2`, balance `60`, net `-40`, `settled_lost` |
| Focused odds-contract tests | `3/3` passed in `0.043s` |
| Frozen Python regression | `65/65` passed in `148.904s`, timing-sensitive test first, process verified at High priority |
| Brain Admin self-check | Passed with exact loss, exact win, tamper, and no-partial fixtures |
| Live browser/DOM inspection | PASS — Operations displayed `VALIDATED QA FINALIZED WIN`, Mesa selected/won, probability `40000000`, the exact formula, score `101-104`, stake `40`, return `100`, net `+60`, entry count `3`, balance `160`, `settled_won`, and the exact replay seal; the command chain showed sequence `2` `-40` to `60` and sequence `3` `+100` to `160`; the exact card exposed `0` controls, and the card, detail, and linkage regions had no horizontal overflow |
| Replay exporter | Unchanged at `421` frames, replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, `29,160` bytes, SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is one machine-local output-only reconciliation/history card for the exact H10 win. It adds no wager control and does not change the saved request, lock, result, decision, finalization, ledger, cooldown, replay, league, or basketball result.

No player wager route/history UI, refund, void, correction, alternate wager, prop market, online account, trusted clock, backend, deployment, payment, real-money connection, or basketball/Athlete Life brain change is implemented.

## Next candidate gate

Scope Director review should now select the smallest remaining Match Winner requirement. Void/refund, correction, and player-facing history/UI remain separate unproved gates.
