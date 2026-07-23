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

# Phase 1H.17 Player-Facing Upcoming QA Match Winner Request

## Outcome

Phase 1H.17 adds one explicitly noncanonical, machine-local, upcoming Match Winner request at the existing Sundale Sportsbook frontage. In QA mode, the player can choose either Sundale Sparks or Red Mesa Rivals, choose `10`–`100` Odds Bucks in increments of `10`, review the exact integer gross return, and press Enter a second time to confirm.

The server rebuilds the exact isolated offer instead of trusting offer data from the player. One confirmed `40`-Odds-Bucks Sundale selection atomically persists exactly one `accepted_pending_lock` request and one linked `-40` `match_winner_stake` ledger entry. The existing job path funds the isolated profile with `100`, so the accepted screen truthfully shows request ID `qa:h17:match_winner:request:1`, Sundale Sparks, stake `40`, and resulting balance `60`.

Ponytail reused the existing H16 frontage and interaction pattern, H2 offer contract, H3 request API, Odds Bucks SaveGame, job-funded ledger, and native on-screen reader. No framework, dependency, market abstraction, account, service, or new persistence schema was added.

## Exact QA boundary

The QA offer is Season `100`, Game `1`, ID `4a30feca21ab8dfb8a3f64ca642aadcdb33743b07a7cedf49b6b743f1c6f2f31`, accepted at fixed QA time `2100000000`, and locked at `2100086400`. Its public envelope contains teams, prices, limits, source commitment, source versions, and lock only. It contains no score, winner, replay, result link, settlement, refund, correction, or hidden result state.

The fixed acceptance time is strictly before lock. Exact cold retry returns the saved request without a second debit. Stale or tampered offers, invalid team or stake, a late request, conflicting command reuse, the completed H16 canonical offer, and insufficient balance all reject with zero persisted mutation.

The normal H16 canonical Season 1, Game 1 preview remains read-only. `PublicSeason1.json`, the canonical calendar and results, the 421-frame replay, replay seal, league exporter, Basketball Brain, prediction study, old exact loss/win/void chains, and Brain Admin behavior are unchanged.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native H17 request | `1/1` passed |
| Full native OddsWell automation | `12/12` passed |
| Focused odds contracts | `3/3` passed in `0.048s` under bundled Python `3.12.13` |
| Frozen simulator regression | Timing-sensitive guard ran first; `65/65` passed in `132.613s` |
| Brain Admin self-check | Passed unchanged |
| Editor and game targets | Passed with four-way bounded compilation |
| Windows BuildCookRun | Final source-state run passed in `50.87s`; Bootstrap and Sundale only; pak, IoStore, compression, package, and archive succeeded |
| Packaged accepted request | Player QA exercised both teams, the `10`/`100` bounds, review then confirm, one request, one linked debit, and balance `60` |
| Packaged cold process | Exact retry returned `DUPLICATE`; all eight rejection classes preserved `2` ledger entries, `1` request, and balance `60`; cleanup passed |
| Visual proof | `Phase1H17_SportsbookWagerAccepted.png`, `1,585,586` bytes, visibly shows request ID, selected team, stake, resulting balance, pending-lock status, and the no-result boundary |
| Canonical league | Deterministic re-export stayed `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Canonical replay | Unchanged at `421` frames, seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| Cost | `$0.00` |

## Truth boundary

This is one isolated machine-local QA request, not a canonical production wager or live service. It does not lock, simulate, settle, refund, correct, create player history, generalize markets, modify Admin, add accounts or a backend, connect real money, deploy, retrain, or change any brain. The player cannot submit the already completed H16 offer.

## Next candidate gate

Scope Director review should select the smallest remaining Phase 1H requirement from evidence. A player-facing pending-request/history view, a canonical future-game route, lock/settlement integration, and correction policy remain separate unproved gates. Phase 1H.18 has not begun.
