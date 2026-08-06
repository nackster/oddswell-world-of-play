---
tags:
  - decision
  - beta
  - economy
  - odds-bucks
  - job
status: accepted
date: 2026-07-21
---

# DEC-014 Phase 1G.3 Provisional First Job Payout

## Decision

The owner approved a provisional first-job payout of **100 Odds Bucks once per local saved profile**. The existing server-validated placeholder shift issues one stable idempotent command. Repeating the shift, including after a cold process restart, must not create another credit.

This amount is a testable beta placeholder, not final economy balance. The owner may cycle back after later pricing and recovery evidence exists.

## Integrity rules

- The authoritative server owns the command and ledger.
- The ledger save must succeed before the live balance changes.
- The first accepted command creates exactly one `+100` entry.
- Every exact retry is a duplicate with no balance or history change.
- Invalid or corrupt local persistence fails closed and awards nothing.
- The current persistence identity is one local saved profile, not an online account.

## Boundary

This decision does not approve repeat job income, a daily allowance, a recovery floor, starting balance, prices, wagers, settlement, purchases, inventory, trading, real-money connection, a backend, deployment, or a second currency. Those remain separate roadmap gates.
