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

# DEC-015 Phase 1G.4 Rolling Job Recovery Defaults

## Decision

The owner approved these provisional local-beta recovery defaults:

- A new local saved profile starts with **0 Odds Bucks**.
- The existing server-validated placeholder shift pays **100 Odds Bucks**.
- The first successful payout counts as period one.
- Another payout becomes eligible on a rolling **24-hour** cooldown after the last accepted payout.
- Unspent Odds Bucks accumulate.
- There is no separate allowance and no catch-up payment for missed periods.

These values are testable beta defaults, not final economy balance. Later price, wager, and recovery-floor evidence may justify a separately approved revision.

## Integrity rules

- The authoritative GameMode owns eligibility, command creation, and ledger mutation.
- The local save must accept both the candidate ledger and next-eligible timestamp before live state changes.
- An ineligible shift creates no ledger entry and changes no balance.
- Every eligible period produces at most one idempotent command.
- Eligibility advances from the accepted payout time; missed periods do not stack.
- Invalid or inconsistent persistence fails closed and awards nothing.
- The first Phase 1G.3 credit is period one when an older valid save migrates.

## Truth boundary

The beta slice uses one local saved profile and the machine's UTC clock. It is not a trusted production time source and does not prove anti-clock-tampering, online account identity, backend reconnect, cloud or multi-device recovery, an allowance, prices, purchases, wagers, settlement, trading, real-money connection, deployment, or a second currency.
