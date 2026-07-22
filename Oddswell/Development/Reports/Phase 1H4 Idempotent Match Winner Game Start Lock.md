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

# Phase 1H.4 Idempotent Match Winner Game-Start Lock

## Outcome

Phase 1H.4 adds one immutable, server-owned game-start lock decision for an existing `accepted_pending_lock` Match Winner request. The lock record is stored separately from the accepted request and links one lock command to the exact request, season, game, and previously approved lock timestamp.

The operation succeeds only when the supplied authoritative game-start timestamp exactly equals the request's lock time. An exact retry returns the original lock record without adding another record. Unknown requests, wrong games, pre-start or post-start timestamps, reused commands with changed data, a second lock command for the same request, and malformed persisted links fail closed.

Ponytail kept this in the existing native SaveGame state. Schema v4 migrates v1-v3 saves with zero invented lock records. The operation writes no Odds Bucks entry and does not change the accepted request, balance, or job cooldown.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Native editor build | Passed in `8.80s` |
| Focused native economy automation | `1/1` passed in `49.7s` |
| Full native OddsWell automation | `11/11` passed with zero failures in `50.2s` |
| Accept then lock | Exact game-start command creates one linked `locked` decision |
| Durable reload | One request, one stake debit, and one lock decision reload exactly |
| Ledger invariance | Entry count, balance `60`, and job cooldown remain unchanged by lock |
| Request invariance | Offer, team, stake, accepted time, and lock time remain unchanged |
| Idempotency | Exact retry adds no second lock; conflicting reuse fails closed |
| Rejection boundary | Unknown request, wrong game, wrong timestamp, second lock, and malformed persisted record are rejected |
| Migration | v1-v3 saves migrate to v4 with zero fabricated locks |
| Focused odds-contract tests | `3/3` passed |
| Frozen simulator regression | `65/65` passed in `143.229s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Unchanged at `421` frames, `2` teams, `12` athletes, and `20` games |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This proves a machine-local lock persistence primitive. The caller supplies the local authoritative game-start timestamp; no trusted backend clock, online account, network command route, player UI, runtime offer publication, or Admin wager view exists.

Locking consumes no score or result and makes no win/loss decision. No settlement, payout, lost-stake finalization, void/refund, cancellation, correction, new ledger credit/debit, history screen, player prop, payment, real-money connection, or second currency is implemented. Wager state still has no path into the Basketball Brain, Athlete Life Brain, public pregame snapshot, or authoritative game outcome.

## Next candidate gate

The Scope Director should evaluate the smallest immutable sealed-result linkage after this lock, without changing the ledger or paying a winner yet. Settlement remains a separate evidence gate.
