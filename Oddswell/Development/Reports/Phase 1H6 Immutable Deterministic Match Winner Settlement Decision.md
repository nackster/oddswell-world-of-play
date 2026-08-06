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

# Phase 1H.6 Immutable Deterministic Match Winner Settlement Decision

## Outcome

Phase 1H.6 adds one separate immutable decision record for the exact accepted request, game-start lock, and sealed-result link. The server-owned operation accepts only the decision command and exact chain IDs, then derives the decision from saved authoritative evidence: Harbor City Waves was selected, Mesa Vista Sol won, so the result is `lost`, `GrossReturnDue` is `0`, and status remains `decided_pending_apply`.

The decision succeeds only when every request, lock, and result-link identity matches. An exact retry returns the original record. Unknown or mismatched chain IDs, reused commands with changed data, a second decision for the request, and malformed persisted decisions fail closed without mutation.

Ponytail kept the change in the existing native SaveGame state. Schema v6 migrates v1-v5 saves with zero invented decisions. Decision creation adds no Odds Bucks entry and preserves the two-entry ledger, balance `60`, job cooldown, request, lock, result link, replay, and basketball evidence exactly.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed in `8.85s` |
| Focused native economy automation | `1/1` passed in `49.9s` |
| Full native OddsWell automation | `11/11` passed with zero failures in `50.3s` |
| Exact chain decision | Harbor City Waves selected; Mesa Vista Sol authoritative winner; derived outcome `lost` |
| Pending amount | `GrossReturnDue = 0`; status `decided_pending_apply` |
| Durable reload | One request, stake debit, lock, result link, and decision reload exactly |
| Ledger invariance | Entry count `2`, balance `60`, and job cooldown remain unchanged |
| Prior-evidence invariance | Request, lock, exact Game 1 result, and replay seal remain unchanged |
| Idempotency | Exact retry adds no second decision; conflicting reuse and a second command fail closed |
| Rejection boundary | Missing, mismatched, tampered, and malformed decision chains are rejected |
| Migration | v1-v5 saves migrate to v6 with zero fabricated decisions |
| Focused odds-contract tests | `3/3` passed in `0.051s` |
| Frozen simulator regression | `65/65` passed in `143.773s` |
| Brain Admin self-check | Passed |
| Replay exporter | Unchanged at `421` frames with seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75` |
| League exporter | Unchanged at `2` teams, `12` athletes, and `20` games |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This proves one machine-local deterministic decision for the exact archived losing selection. It does not add an alternate winning wager or result, and Phase 1H.2 remains the isolated evidence for pure winning-return math.

`decided_pending_apply` is not settled or finalized. No loss application, settled status, payout, refund, void, correction, new ledger entry, balance change, player route, Unreal UI, Admin wager view, prop market, backend, payment, real-money connection, or brain change is implemented. The decision cannot influence basketball outcomes.

## Next candidate gate

Scope Director candidate only: evaluate an idempotent application/finalization gate for this exact loss decision that creates no ledger entry and changes no balance. This report does not authorize that gate, a settled status, payout, refund, void, correction, or any broader settlement behavior.
