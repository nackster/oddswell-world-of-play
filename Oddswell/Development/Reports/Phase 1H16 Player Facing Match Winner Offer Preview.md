---
tags:
  - development
  - beta
  - basketball
  - wagering
  - odds-bucks
  - phase-1h
status: complete
date: 2026-07-22
---

# Phase 1H.16 Player-Facing Match Winner Offer Preview

## Outcome

Phase 1H.16 gives the separate Sundale Sportsbook frontage one player-facing, read-only Match Winner preview. At that location only, `E` opens the exact verified Season 1, Game 1 `basketball-match-winner-odds-v1` offer. Leaving the frontage closes it, and the same action is unavailable elsewhere.

The preview names Harbor City Waves and Mesa Vista Sol, exact probabilities `57586693` and `42413307`, display odds `1.7365x` and `2.3577x`, the `10`–`100` Odds Bucks rule in increments of `10`, game-start lock, offer ID, source versions, commitment, and exact gross-return examples: stake `10` returns `17` or `23`; stake `100` returns `173` or `235`.

Ponytail reused the existing public league exporter, `PublicSeason1.json`, Sportsbook route waypoint, `E` polling pattern, and native on-screen reader. No new framework, dependency, service, account path, or generalized market UI was added.

## Public evidence and fail-closed boundary

The existing league exporter now attaches the immutable Phase 1H.2 offer produced from the same verified Season 1, Game 1 public prediction commitment. Unreal independently requires the exact public envelope, schema, offer ID `29d3ab7c4fd2858b4cfa80f1f413a77aaa30fbdde1ca593b477d82f2e726617e`, source commitment `898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f`, versions, teams, game, lock, stake limits, probabilities, odds formula, selection order, and link back to the public Game 1 prediction evidence.

Malformed data, a stale version, a changed probability, an extra hidden field, or a mismatched public evidence link yields no preview values. The normal public league reader remains independent, so an unavailable offer does not invent or partially expose wager evidence.

The league fixture is now `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`. Removing the new `match_winner_offer` field produces an object exactly equal to the previously committed fixture: both standings, both teams, all 12 athletes, all 20 results, Game 1 score `104`–`101`, prediction commitment, and every replay seal are unchanged.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native offer reader | `1/1` passed, including exact values plus stale, tampered, malformed, and hidden-field rejection |
| Full native OddsWell automation | `11/11` passed with no failures |
| Focused odds contracts | `3/3` passed in `0.044s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `134.983s` under bundled Python `3.12.13`; the environment did not grant the attempted priority query/change, so no priority claim is made and no frozen threshold changed |
| Brain Admin self-check | Passed unchanged |
| Final editor/game builds | Passed with four-way bounded compilation after the redundant clean packaging build was stopped at repeated machine-memory retries |
| Windows BuildCookRun | Passed in `86.52s`; Bootstrap and Sundale only; pak, IoStore, compression, package, and archive succeeded |
| Packaged player proof | Rendered Sundale launch passed and exited cleanly; QA first rejected the interaction away from the frontage, then opened it at Sportsbook |
| Read-only invariant | Ledger entries remained `0` to `0`; balance remained `0` to `0`; no wager-submission, team-selection, or stake controls were present; `E` only opens or closes the preview |
| Visual proof | `Phase1H16_SportsbookOfferPreview.png`, `1,784,719` bytes, visibly contains teams, probabilities, odds, return examples, stake rule, lock, full offer ID, source versions, commitment, and read-only warning |
| Package | `55` files totaling `1,046,488,974` bytes |
| Replay exporter | Unchanged at `421` frames, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| Cost | `$0.00` |

## Truth boundary

This is a build-time, player-facing preview of one exact archived public offer. It does not submit a wager, debit or credit the ledger, create a request or history entry, correct evidence, add a live clock, or connect an account/backend. It adds no alternate market, prop, payment, real-money purchase, deployment, retraining, model behavior, basketball result, athlete behavior, or Admin mutation control.

The older native ledger QA fixture remains isolated and intentionally noncanonical. The player preview uses only the exact current public prediction evidence and does not reuse the artificial native `60/40` test offer.

## Next candidate gate

Scope Director review should choose the smallest remaining Match Winner requirement. A player wager-submission route, player-facing wager history, and correction policy remain separate unproved gates. Phase 1H.17 has not begun.
