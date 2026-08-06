---
tags:
  - development
  - beta
  - basketball
  - wagering
  - unreal
  - interface
  - phase-1h
status: complete
date: 2026-07-24
---

# Phase 1H.26D Player-Facing Read-Only Canonical Match Winner Offer

## Outcome

Normal local-beta play now reads the exact persisted Phase 1H.26A schedule, Phase 1H.26B public prediction commitment, and Phase 1H.26C Match Winner offer at the Sundale stadium ticket booth.

Before server tipoff, the existing Phase 1H.24 browser shows:

- Mesa Vista Sol at Harbor City Waves;
- the Match Winner market;
- exact integer-backed decimal displays `1.7365` and `2.3577`;
- Odds Bucks stake range `10`–`100`, step `10`;
- gross-return examples and the approved floor-return convention;
- exact server tipoff and `LOCAL BETA`; and
- an explicitly read-only slip.

The cards and slip have no selection, editor, confirmation, request, debit, or mutation route. Existing mouse, keyboard, and controller navigation remains presentation-only.

## Fail-closed boundary

The player-facing loader reconstructs the exact expected H26C offer from validated H26A and H26B inputs, then requires a byte-equivalent persisted H26C identity and canonical JSON. It accepts no caller-provided time; normal play uses the runtime's server-owned UTC observation.

At or after tipoff, or when any input/record is missing, mismatched, or tampered, the booth shows one neutral `MATCH WINNER UNAVAILABLE / LOCKED` panel. That panel exposes no teams, prices, selections, or wager controls.

The older Phase 1H.16 `PublicSeason1` offer reader is not called by the normal ticket-booth path and is not a fallback.

## Ponytail boundary

This phase adds one thin canonical-to-existing-preview adapter and reuses the Phase 1H.24 native HUD, interaction radius, modal input handling, tabs, cards, slip, and QA route. It adds no widget framework, dependency, offer service, repository, generalized market model, backend, repricer, or second persistence record.

The existing H26C integer probability and odds fields are copied directly. Floating-point conversion occurs only when drawing the four-decimal text; no price is recalculated.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused canonical native automation | `1/1` passed |
| Full native OddsWell automation | `20/20` passed |
| Frozen Python regression | `68` tests and `16` subtests passed in `126.97s` |
| Phase 1H odds contracts | `3/3` passed |
| Brain Admin self-check | Passed |
| Python compilation | Passed |
| Unreal editor and standalone game builds | Passed |
| Final explicit-Sundale Windows BuildCookRun | Passed in `65.3s`; `50` files / `1,046,150,414` bytes |
| Fresh packaged ticket-booth QA | Passed; exact canonical teams, e4 odds, step, returns, server tipoff, and local-beta disclosure; archive fallback false |
| Read-only invariance | Ledger entries/balance stayed `0/0`; submission, selection, editor, confirmation, request, debit, and mutation all false |
| Packaged `1280x800` visual inspection | Passed; no overlap or clipping |
| Cold packaged restore | H26A/H26B/H26C all duplicate; all three SaveGame byte lengths, SHA-256 hashes, and UTC mtimes unchanged |
| Deterministic public league export | `30,288` bytes; SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Deterministic replay export | `421` frames; `256,442` bytes; SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`; seal unchanged |
| Cost | `$0.00` |

The retained visual is:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Screenshots\Windows\Phase1H26D_CanonicalMatchWinnerOffer.png`

## Truth boundary and next gate

This proves only read-only player presentation of the exact active canonical offer before server tipoff, plus fail-closed presentation otherwise.

It does not prove or authorize player selection, stake editing, confirmation, request creation, debit, receipt, lock transition, simulation, result, settlement, correction, history, repricing, another market, backend/account authority, payment, real money, retraining, or brain behavior.

The next gate is Scope Director review of the smallest truthful canonical player-action prerequisite. No action path is authorized merely because the canonical offer is now visible.
