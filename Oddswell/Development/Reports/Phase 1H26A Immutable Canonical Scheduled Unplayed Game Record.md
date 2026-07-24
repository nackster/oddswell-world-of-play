# Phase 1H.26A — Immutable Canonical Scheduled-Unplayed Game Record

**Status:** COMPLETE
**Date:** July 24, 2026
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The authoritative Unreal GameMode now performs one no-input transition that creates or cold-restores one separate canonical local-beta schedule record. The record is schema `oddswell-canonical-scheduled-game-v1`, version `1`, fresh Season `1`, Game `1`, Harbor City Waves home, Mesa Vista Sol away, and `scheduled_unplayed`.

The server supplies `season_created_unix`. Tipoff is exactly `+1,800` seconds. Offer eligibility starts at creation, while `offer_published` remains false. The record explicitly says `local_beta`, `server`, and `production_timing = false`.

## Persistence and rejection proof

- First valid creation writes one `USaveGame` object to a dedicated slot.
- Exact retry returns `Duplicate` and every original field, including the first creation time.
- A cold disk load independently validates and restores every field.
- Conflicting identity or a preexisting result-like `completed` status returns `Rejected`.
- Rejected evidence is not rewritten.

The record has no score, winner, seed, RNG state, replay, action tape, private athlete state, economy data, or user data. No offer, request, debit, lock, simulation, result, settlement, cancellation, or correction is created.

## Archive and QA invariance

`PublicSeason1.json`, its completed Harbor `101` to Mesa `104` archive, the 421-frame replay, every Season `100` QA wager chain, the Odds Bucks ledger, existing reconciliation histories, and player/Admin UI remain separate and unchanged.

The deterministic public league fixture remains `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`. The replay remains `421` frames and `256,442` bytes with SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` and seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused canonical schedule automation | `1/1` passed |
| Full native OddsWell automation | `18/18` passed |
| Frozen simulation and odds contracts | `68/68` passed across five groups |
| Brain Admin self-check | Passed |
| Editor / game builds | Passed |
| Fresh Windows Development BuildCookRun | Passed in `93.41s`; `50` files / `1,045,759,406` bytes |
| Packaged cold retry | `transition=duplicate`; original creation `1784908399`; tipoff `1784910199`; no offer |
| Packaged SaveGame invariance | `2,771` bytes; SHA-256 `7ac280032125484cd78dd84e96cafaddd7fbca1e54f3d2f2486d30c23ac7c2df`; timestamp unchanged |
| Python compilation / canvas parse / diff hygiene | Passed |

## Ponytail boundary

The phase adds one dedicated SaveGame type and one direct GameMode call. It does not add a scheduler framework, service, database, offer abstraction, new dependency, or UI.

## Truth boundary and next gate

This proves only the immutable scheduled-game prerequisite. The timestamp is server-owned in the local beta, not a trusted production backend time. A versioned canonical offer, player submission, lock, authoritative simulation/result, settlement, correction, and broader history each remain separate unproved gates.

See [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]].
