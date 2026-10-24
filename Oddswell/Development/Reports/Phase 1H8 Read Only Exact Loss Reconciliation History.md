---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-21
---

# Phase 1H.8 Read-Only Exact-Loss Reconciliation History

## Outcome

Phase 1H.8 publishes one separate machine-local, server-authored `oddswell-match-winner-reconciliation-v1` JSON projection from the fully validated Phase 1H.7 state. The file is replaced atomically after the exact loss finalizes and after a validated cold load containing that finalization. Missing finalization removes stale output; malformed saved evidence cannot publish a partial chain.

The projection binds the exact offer/version, request and Harbor City Waves selection, `match_winner_stake` debit command at sequence `2` with delta `-40` and balance-after `60`, lock and game start, sealed Harbor `101`–`104` Mesa result, exact replay seal, immutable `decided_pending_apply`/`lost` decision with gross return due `0`, separate `settled_lost` finalization with gross return applied `0`, ledger count `2`, final balance `60`, and `server` / `machine_local` / `read_only` / QA labels.

Brain Admin independently validates the complete command and evidence chain before showing one immutable Operations card. The accepted card reads Harbor selected, Mesa won, stake `40`, return `0`, net `-40`, balance `60`, and `settled_lost`, followed by the exact replay and command linkage. Missing, malformed, tampered, or partial projections show unavailable and reveal no partial wager fields. The card has no mutation controls.

Ponytail reused the existing native atomic JSON-write pattern, Operations page, and self-check. The generic `oddswell-odds-bucks-reconciliation-v1` projection remains unchanged. No SaveGame schema bump or new dependency was added.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed |
| Focused native economy automation | `1/1` passed |
| Full native OddsWell automation | `11/11` passed with zero failures |
| Focused odds-contract tests | `3/3` passed in `0.048s` |
| Python regression | `68/68` passed in `143.296s`: `65` frozen plus `3` focused odds tests |
| Brain Admin self-check | Passed, including valid, missing, tampered, and partial projection cases |
| Live Operations card | Harbor selected; Mesa won; stake `40`; return `0`; net `-40`; balance `60`; `settled_lost`; exact seal and command chain; zero controls; no overflow |
| Ledger invariance | Entry count `2`, balance `60`, and job cooldown remain unchanged; no entry is added |
| Decision/finalization boundary | Prior decision remains immutable as `decided_pending_apply`; separate finalization remains `settled_lost` |
| Replay exporter | Unchanged at `421` frames, exact replay seal, `256,442` bytes, and fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| League exporter | Unchanged at `2` teams, `12` athletes, `20` games, and SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is an output-only Operations reconciliation/history card for one exact machine-local finalized loss. It is not a player wager-history screen and cannot create, alter, apply, finalize, refund, void, correct, or delete any wager or ledger entry.

No winning-return or payout proof, alternate wager, refund, void, correction, player UI/history, prop market, account, trusted clock, backend, deployment, payment, real-money connection, or brain change is implemented. The two-entry Odds Bucks ledger, balance `60`, cooldown, generic Odds Bucks projection v1, replay, league, and basketball behavior remain unchanged.

## Next candidate gate

Scope Director review only: select the smallest remaining Phase 1H evidence gate from the Match Winner requirements. Winning return/payout, void/refund, correction, player-facing history/UI, and later markets remain unproved and unauthorized by this report.
