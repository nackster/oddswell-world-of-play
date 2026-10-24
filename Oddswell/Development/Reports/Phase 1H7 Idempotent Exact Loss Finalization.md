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

# Phase 1H.7 Idempotent Exact-Loss Finalization

## Outcome

Phase 1H.7 adds one separate immutable finalization record for the exact Phase 1H.6 losing decision. The server-owned operation accepts only a finalization command ID and the exact saved decision ID, then derives the request, lock, sealed result, offer, selected team, winner, stake, outcome, and return from the stored evidence chain.

Only the exact Harbor City Waves selection against the Mesa Vista Sol winner can finalize: stake `40`, outcome `lost`, `GrossReturnDue = 0`, and prior status `decided_pending_apply`. The new record stores `settled_lost`, gross return applied `0`, observed ledger entry count `2`, and observed balance `60`.

The Phase 1H.6 decision remains immutable and retains `decided_pending_apply`; finalization is a separate record rather than a rewrite. An exact retry returns the original finalization. Conflicting command reuse, a second finalization, missing or mismatched evidence, tampering, malformed records, a nonloss decision, or a nonzero return fail closed without mutation.

Ponytail kept the change inside the existing native SaveGame path. Schema v7 migrates v1-v6 saves with zero invented finalizations. The candidate ledger, request, lock, result, decision, and finalization are validated and saved together.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed |
| Focused native economy automation | `1/1` passed; exact finalization, reload, retry, rejection, tamper, and invariance assertions passed |
| Full native OddsWell automation | `11/11` passed with zero failures |
| Exact loss finalization | Harbor City Waves selected; Mesa Vista Sol won; stake `40`; `lost`; gross return applied `0`; status `settled_lost` |
| Separate immutable records | Phase 1H.6 decision remains `decided_pending_apply`; one separate finalization reloads exactly |
| Ledger invariance | Entry count `2`, balance `60`, and job cooldown remain unchanged; no zero-value entry exists |
| Idempotency | Exact retry returns the original record; conflicting reuse and a second command fail closed |
| Rejection boundary | Missing, mismatched, tampered, malformed, nonloss, and nonzero-return chains are rejected without mutation |
| Migration | v1-v6 saves migrate to v7 with zero fabricated finalizations |
| Focused odds-contract tests | `3/3` passed in `0.049s` |
| Frozen simulator regression | `65/65` passed in `143.619s` |
| Brain Admin self-check | Passed unchanged |
| Replay exporter | Unchanged at `421` frames with seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| League exporter | Unchanged at `2` teams, `12` athletes, and `20` games |
| Compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This proves one machine-local exact-loss finalization. A lost stake was already debited in Phase 1H.3, so finalizing this loss correctly adds no ledger entry, including no zero-value entry, and changes neither the balance nor the job cooldown.

This is not winning-return or payout proof. It adds no alternate wager, winning application, refund, void, correction, player route, Unreal UI, wager history, Admin wager view, prop market, backend, payment, real-money connection, or brain change. It cannot influence basketball outcomes.

## Next candidate gate

Scope Director candidate only: evaluate a read-only reconciliation/history view of this finalized exact loss against the remaining Phase 1H evidence requirements, or select another smaller required Phase 1H gate if it has higher dependency value. This report does not authorize either candidate.
