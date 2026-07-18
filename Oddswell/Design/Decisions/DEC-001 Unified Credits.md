---
tags:
  - decision
  - economy
status: accepted
date: 2026-07-13
---

# DEC-001: Unified Credits

## Decision

OddsWell will use one primary credit currency named **Odds Bucks**. There is no second betting or lifestyle currency. Players may:

- Earn credits through gameplay and work.
- Wager credits to win or lose credits.
- Save credits.
- Spend credits on permitted in-game goods and activities.
- Purchase credits with real money.

Real-money Odds Bucks purchases are explicitly **outside the beta**. They remain a later possibility, not an active implementation phase.

## Consequences

- Credit balances and transactions must be server-authoritative.
- The backend needs an append-only ledger, purchase verification, idempotency, prediction locking, settlement records, and audit tools.
- Payment-provider, storefront, age-rating, regional, and legal requirements must be validated before real-money purchasing is implemented.
- The original concept's separate betting-credit and lifestyle-currency model is superseded by this decision.
- The beta must provide a non-paid recovery path through work or an allowance so a zero balance does not permanently stop play.
