# Phase 1H.26C - Immutable Canonical Match Winner Offer Record

**Status:** COMPLETE
**Date:** July 24, 2026
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The authoritative Unreal GameMode now creates or cold-restores one immutable canonical Match Winner offer record only after exact H26A schedule and H26B equal-public commitment validation succeeds and the server-observed time is still before tipoff.

The record uses the existing Phase 1H odds contract:

- schema `oddswell-basketball-odds-offer-v1`;
- version `basketball-match-winner-odds-v1`;
- market `match_winner`;
- currency `odds_bucks`;
- source `phase0d4-v1` / `oddswell-public-pregame-v1` / `public_elo_rotation`;
- H26B SHA-256 `898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f`;
- lock time equal to the H26A tipoff;
- stakes `10` through `100` in increments of `10`;
- house edge `0`;
- payout `floor(stake*100000000/win_probability_e8)`;
- Harbor probability/decimal odds `57586693` / `17365`; and
- Mesa probability/decimal odds `42413307` / `23577`.

The offer ID is the SHA-256 of the exact sorted, condensed canonical offer JSON without the ID field. The frozen Python contract and native serializer produce the same QA identity `354679a800e9a8ed31eccd04591310defc8ec6413d81891bb5b595e9d9d88606` for lock `2200001800`.

## Minimal persistence boundary

The dedicated SaveGame persists only:

1. the canonical offer ID; and
2. the exact canonical offer JSON.

Every contract field is inside that JSON. On load, Unreal rebuilds the expected offer from the validated upstream records, recomputes its canonical identity through the existing Odds Bucks offer serializer/validator, recursively audits every nested field name, and requires both persisted strings to match exactly.

The recursive public-field audit rejects seed, RNG, fatigue, life/private inputs, score, winner, replay, result, simulation, request, debit, settlement, economy, and user fields. The H26C source does not read `PublicSeason1`.

## Time, conflict, and retry behavior

- Creation rejects before the H26A creation time or at/after the H26A tipoff.
- Wrong H26A identity/timing/state or wrong H26B identity/version/hash rejects.
- A malformed or conflicting persisted offer rejects without rewrite.
- Exact retry and a separate cold process return `Duplicate` with the first bytes and mtime unchanged.
- H26A remains `offer_published=false`; H26C does not rewrite that immutable schedule-creation field.

This phase creates a separate canonical offer record. It does not expose that record through the existing archived ticket-booth UI.

## Upstream and system invariance

H26C never calls an offer UI, wager request, debit, lock transition, simulation, result, settlement, correction, or later-market path. The existing Odds Bucks ledger and the older archived H16 read-only preview remain unchanged.

The deterministic public league fixture remains `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`. The replay remains `421` frames and `256,442` bytes with SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` and seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

## Retained clean two-process package evidence

The clean packaged GameMode-only create run retained:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26C_Retained_Created.log`

It records:

- H26A `transition=created`, creation `1784912799`, tipoff `1784914599`, and `offer_published=false`;
- H26B `transition=created` with the exact public commitment; and
- H26C `transition=created` before tipoff with offer ID `b27d926cdeab30d305149e7130162c645ae8b13ec98d92023e47e3f24e467074` and every exact contract value above.

The separate cold process retained:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26C_Retained_Duplicate.log`

It records H26A, H26B, and H26C as `transition=duplicate` with the same values.

Across the cold process:

| Record | Bytes | SHA-256 | UTC mtime |
| --- | ---: | --- | --- |
| H26A schedule | `2,771` | `8727ab30b601034ce6a980d5b54f434f2c97e6bcb0f852f1ed77dbb02771beb1` | `2026-07-24T17:06:39.4687840Z` |
| H26B commitment | `5,153` | `591d350c9e787a73746d9a166387a993e2f0c2cf2e8a07583117ba43d87b3a88` | `2026-07-24T17:06:39.4757810Z` |
| H26C offer | `2,960` | `04186b017ff210877d1bddc9a256fc1c7856366ccc5cce2113bdfedb9992f128` | `2026-07-24T17:06:39.4867184Z` |

Every byte length, SHA-256, and UTC mtime remained unchanged. The isolated files were then deleted and verified absent. Both retained logs remain, with zero OddsWell, Unreal automation, AutomationTool, or Zen processes left running.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused canonical offer automation | `1/1` passed |
| Full native OddsWell automation | `20/20` passed |
| Frozen simulation and odds contracts | `68/68` passed across five groups |
| Phase 1H Python odds contract | `3/3` passed |
| Brain Admin self-check | Passed |
| Python compilation | Passed |
| Final editor build | Passed in `5.65s` |
| Final game build | Passed in `13.77s` |
| Fresh final Windows Development BuildCookRun | Passed in `47.14s`; `50` files / `1,046,103,100` bytes before runtime saves |
| Clean packaged create process | H26A/H26B/H26C created before tipoff; exact canonical offer |
| Separate cold packaged process | All three duplicate; exact values, bytes, hashes, and mtimes unchanged |
| Deterministic exporters | Exact league and replay lengths, hashes, and replay seal unchanged |
| Isolated cleanup | All three SaveGames absent; retained logs present; zero matching processes |

## Ponytail boundary

H26C reuses `FOddsWellMatchWinnerOffer` and the existing canonical JSON/SHA/contract validator through one thin exported wrapper. The new persistent surface is one two-field SaveGame and one direct GameMode call. No offer service, repository, database, UI adapter, dependency, or generalized market framework was added.

## Truth boundary and next gate

This proves only one immutable canonical Match Winner offer record created from H26A and H26B before tipoff. It does not prove player-facing canonical presentation, selection, slip, request, debit, accepted wager, lock transition, simulation, result, settlement, correction, backend, account, deployment, payment, real money, or any later market.

The next gate is Scope Director review of the smallest read-only consumer of this exact canonical record. Existing archived preview evidence does not automatically satisfy that gate.

See [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]] and [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]].
