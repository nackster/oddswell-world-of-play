---
tags:
  - decision
  - beta
  - basketball
  - wagering
  - odds-bucks
status: accepted
date: 2026-07-21
---

# DEC-017 Match Winner Odds and Stake Defaults

## Decision

The owner approved the first local-beta Match Winner rules:

- Match Winner is the first wager market.
- Odds version `basketball-match-winner-odds-v1` uses the frozen `phase0d4-v1` `public_elo_rotation` probability from an exact `oddswell-public-pregame-v1` commitment.
- There is no house edge in this first local engineering slice.
- Stakes are **10–100 Odds Bucks** in increments of **10**.
- The wager locks exactly when the authoritative game begins.
- A winning gross return includes the returned stake and is `floor(stake / selected win probability)` in whole Odds Bucks.
- The implementation uses probability scaled to `100,000,000`, so the exact integer formula is `floor(stake × 100,000,000 / probability_e8)`.
- A canceled game or a game without a valid sealed result voids the wager and refunds the exact stake through a linked idempotent ledger entry.
- Settled history is never rewritten. Any later authoritative correction uses a separate auditable adjustment.

These are provisional beta engineering rules, not final economy balance or real-world wagering advice.

## Equal public information

The offer may use only the committed public snapshot already visible to every player:

- season and game identity;
- home and away teams;
- public standings;
- equal rest days;
- public fictional roster ratings;
- published availability; and
- projected minutes.

Seeds, RNG state, scores, winners, replay/action tapes, hidden fatigue, injury-risk internals, future games, private athlete-life state, economy data, and user data are forbidden.

The SHA-256 commitment is tamper evidence, not authentication. Only the authoritative server may create and publish an active offer from it.

## Player-prop direction

The owner also approved later evidence-gated threshold markets for:

1. player points;
2. player rebounds; and
3. player fouls.

Rarer thresholds should produce higher potential returns, but every prop requires its own public-history model, probability evaluation, versioned offer, exact authoritative statistic, lock, settlement, replay/history link, and Admin reconciliation. They do not ship together with Match Winner.

Points already have bounded authoritative game totals. Rebound events exist in the recorded event log but need durable per-player aggregation and public prediction evidence. Fouls are not currently modeled as authoritative statistics, so foul props remain blocked until the Basketball Brain and Rules and Outcome Engine record them truthfully.

## Athlete-life boundary

A fictional athlete who reduces harmful nightlife or alcohol use may eventually improve sleep, recovery, practice quality, readiness, form, and career outcomes through visible causal rules. The Odds Brain must never receive the private choice directly. It may react only after an allowed consequence becomes part of the equal public snapshot, such as published availability, established public performance history, or another explicitly approved public form signal.

The current Athlete Life Brain does not model a durable alcohol-use state, so this decision records direction rather than claiming that behavior exists.

## Scope boundary

This decision does not authorize real money, purchases, cash-out, a second currency, live external wagering, or simultaneous implementation of every market. Legal, platform, age-rating, and regional review remains mandatory before any external beta involving wagering mechanics.
