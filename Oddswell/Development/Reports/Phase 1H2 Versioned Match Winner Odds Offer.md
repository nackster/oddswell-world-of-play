---
tags:
  - development
  - beta
  - basketball
  - odds
  - wagering
  - phase-1h
status: complete
date: 2026-07-21
---

# Phase 1H.2 Versioned Match Winner Odds Offer

## Outcome

Phase 1H.2 implements the first isolated Basketball Odds Brain contract. Given a verified public pregame prediction commitment and a positive lock timestamp, it deterministically emits one `basketball-match-winner-odds-v1` offer for both teams.

The offer binds its public commitment, prediction/snapshot/model versions, game identity, lock time, approved Odds Bucks stake range, zero-house-edge rule, exact integer payout formula, selection probabilities, display odds, and a SHA-256 offer ID. Identical inputs produce the identical offer. Tampered commitments fail closed.

Ponytail kept this as one standard-library module plus one focused test module. It reuses the existing public prediction commitment and does not modify the frozen Basketball Brain, prediction study, event log, Odds Bucks ledger, Unreal client, or Admin Console.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused Match Winner odds tests | `3/3` passed in `0.054s` |
| Determinism | Identical commitment and lock produce the identical offer ID and payload |
| Tamper boundary | Changed commitment or invalid lock fails closed |
| Probability integrity | Home and away `probability_e8` sum exactly to `100,000,000` |
| Approved stake rules | `10`, `50`, and `100` pass; Boolean, `0`, `9`, `11`, and `101` fail |
| Exact payout | Whole-Odds-Bucks gross return uses integer floor division with no house edge |
| Leakage check | Offer contains no replay hash, score, seed, RNG, hidden fatigue, or athlete-life state |
| Current public-read-model range | Home probabilities `0.48177812`–`0.69374446`; all selection probabilities remain roughly `0.3063`–`0.6937` |
| Frozen simulator regression | `65/65` passed in `139.785s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Unchanged at `421` frames, `2` teams, `12` athletes, and `20` games |
| Python compilation and diff hygiene | Passed |
| Cost | `$0.00` |

## Truth boundary

This is an offer-calculation contract, not an open player wager. The commitment hash detects changes after creation but is not a signature or proof of who created it; the later runtime caller must remain server-owned. No runtime offer publication, scheduled-game clock authority, stake reservation, balance debit, request ID, lock transition, cancellation, refund, settlement, payout credit, player history, Admin wager view, or Unreal UI exists yet.

The source model is engineering evidence from fictional simulator data. It is not a claim of real-world predictive power, final calibration, or production-safe economy balance.

## Later player props

Player points, rebounds, and fouls are recorded as separate future gates under [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]]. Odds may respond to publicly observable performance consequences but never to private Athlete Life Brain choices. Rebounds need durable per-player aggregation; fouls need an authoritative foul model before either can become an offer.

## Next gate

Phase 1H.3 should accept one local Match Winner wager request against an exact offer, validate the approved stake and pre-lock timing, and persist one idempotent stake debit in the existing authoritative Odds Bucks ledger. It must not settle the wager yet.
