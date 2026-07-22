---
tags:
  - decision
  - beta
  - architecture
  - basketball
  - wagering
  - odds-bucks
status: accepted
date: 2026-07-21
---

# DEC-016 Basketball Odds and Wager Isolation

## Decision

The owner approved a strict separation between basketball simulation, odds generation, and wagering. They are cooperating systems with one-way evidence flow, not one combined gambling brain.

| System | Role | May not do |
| --- | --- | --- |
| Basketball Brain | Chooses legal athlete and team intentions from sport state. | Read wagers, stakes, player wealth, purchases, or displayed odds. |
| Basketball Rules and Outcome Engine | Resolves legal intentions into the authoritative seeded event log and sealed result. | Change a result because of betting activity or presentation. |
| Basketball Odds Brain | Produces a versioned pregame probability and odds offer from the exact public snapshot available to every player. | Read hidden or future state, mutate the game, accept wagers, or settle balances. |
| Wager and Settlement Engine | Validates and locks one offered market and stake, records the immutable request, and settles exactly once against the sealed authoritative result. | Simulate basketball, change odds after lock, or influence either basketball system. |
| Admin Reconciliation | Reads the linked offer, request, ledger entries, lock decision, result, and settlement for audit. | Create, edit, approve, or settle a wager from the current read-only local console. |

## One-way evidence flow

`public pregame snapshot -> Basketball Odds Brain -> versioned odds offer -> Wager and Settlement Engine`

`Basketball Brain -> Basketball Rules and Outcome Engine -> sealed event log/result -> Wager and Settlement Engine -> append-only settlement history`

There is deliberately no path from the Wager and Settlement Engine or Odds Bucks balance back into the Basketball Brain or Rules and Outcome Engine.

## Integrity rules

- Every active player sees the same competitively relevant public snapshot and the same versioned offer.
- An offer identifies its market, source snapshot, odds/payout version, creation time, and lock time.
- A wager identifies the exact offer version and one idempotent request command.
- The stake debit, lock decision, authoritative result, payout or loss, and final balance remain linked in immutable history.
- Settlement consumes the sealed authoritative result; it never asks the Basketball Brain to replay or reinterpret the game.
- A correction or cancellation must use an explicit auditable rule. It cannot silently rewrite an accepted wager.
- Any future Odds Brain change is evaluated and promoted as a named version. It does not self-train or silently alter live offers.

## Current evidence boundary

This decision approves architecture only. The Basketball Brain, authoritative rules engine, public prediction evidence, sealed replay result, Odds Bucks ledger, and read-only Admin reconciliation already exist as separate evidence. A production Basketball Odds Brain, offer record, wager request, stake debit, lock, settlement, and wager Admin view do not yet exist.

The existing public prediction model is not automatically promoted into betting odds by this decision. Its suitability, conversion formula, limits, and calibration require their own evidence.

## Match Winner rule resolution

The owner approved the following Match Winner rules in [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]]:

- displayed odds and payout formula;
- minimum and maximum Odds Bucks stake;
- exact lock time;
- cancellation, void, and correction behavior;
- the equal-public-information snapshot;
- local-only beta safeguards before any external wagering test.

Rules for margin, overtime, points, rebounds, and fouls remain separate later gates. Real-money purchases, cash-out, and a second currency remain outside beta.

## Next gate

Phase 1H.2 now proves the isolated versioned Match Winner offer contract. Phase 1H.3 may accept one exact pre-lock request and persist one idempotent local stake debit without settlement.
