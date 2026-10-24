# Phase 1H.26B - Immutable Equal-Public Pregame Prediction Commitment

**Status:** COMPLETE
**Date:** July 24, 2026
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The authoritative Unreal GameMode now creates or cold-restores one immutable prediction commitment after validating the separate Phase 1H.26A scheduled-game record. The new record binds fresh Season `1`, Game `1`, Harbor City Waves home versus Mesa Vista Sol away to:

- snapshot version `oddswell-public-pregame-v1`;
- prediction version `phase0d4-v1`;
- input class `public_elo_rotation`; and
- SHA-256 `898e89ef142f884fe2514bc55a65b91c80a5bf25d068467b2ddbfe25569ea98f`.

The canonical UTF-8 JSON is `2,072` bytes. Its established probabilities are `0.50000000` for `coin`, `0.57849675` for `public_elo`, and `0.57586693` for the selected `public_elo_rotation` input class.

## Independent fresh-opening source

The commitment was reconstructed directly from the existing simulation source, without reading the completed `PublicSeason1` archive:

- `default_teams()` supplies the existing public fictional rosters and ratings;
- a fresh Season `1`, Game `1` scheduled fixture supplies Harbor home and Mesa away;
- every team begins at public standings `0-0`;
- both teams have equal season-opening rest of `7` days;
- existing public availability marks all twelve athletes available; and
- existing public projected minutes are used unchanged.

The resulting canonical JSON and SHA-256 are deterministic. They happen to match the older archived pregame commitment because the public opening inputs and frozen version are identical; the new canonical commitment does not read, copy, or mutate the completed archive.

## Persistence and rejection proof

- First valid creation writes one dedicated schema `oddswell-canonical-pregame-commitment-v1`, version `1` SaveGame.
- Creation is allowed only after the separate H26A schedule validates exactly.
- Exact retry and a separate cold process return `Duplicate` with every first-written field unchanged.
- A malformed schema, schedule link, version, input class, JSON, SHA-256, status, or environment rejects without rewrite.
- The H26A schedule object is serialized before and after commitment creation in native automation and remains byte-for-byte identical.

The record contains no seed/RNG, hidden fatigue, private athlete state, score, winner, replay/action tape, result, offer, odds, economy, or user data. It creates no offer and exposes no UI.

## Archive, QA, and deterministic-export invariance

`PublicSeason1.json`, the completed Harbor `101` to Mesa `104` archive, every Season `100` QA wager record, the Odds Bucks ledger, existing reconciliation histories, player/Admin UI, simulator behavior, and brain behavior remain unchanged.

The deterministic public league fixture remains `30,288` bytes with SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`. The replay remains `421` frames and `256,442` bytes with SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` and seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

## Retained clean two-process package evidence

The clean first packaged process retained:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26B_Retained_Created.log`

It records H26A `transition=created`, H26B `transition=created`, creation time `1784910186`, tipoff `1784911986`, exact snapshot/prediction/input versions, exact commitment SHA-256, standings `0-0,0-0`, rest `7,7`, public availability/projected minutes, and `offer=false`, `odds=false`, `ui=false`, `wager=false`, `simulation=false`, and `result_state=false`.

The separate cold process retained:

`C:\Users\reali\Documents\SaaS\Oddswell\client\OddsWell\Saved\Logs\Phase1H26B_Retained_Duplicate.log`

It records both H26A and H26B as `transition=duplicate` with exact values unchanged.

The isolated H26A file remained `2,771` bytes, SHA-256 `5e6ec42d9109ce77c4b615b405539cf6c7121250c7829aa43686cc9720fb0482`, and UTC mtime `2026-07-24T16:23:06.3208316Z`. The isolated H26B file remained `5,153` bytes, SHA-256 `9b12bf5fbfb14b951a861db1d55f0bdcbf204184747df46a6da2058711d41451`, and UTC mtime `2026-07-24T16:23:06.3327716Z`. Both files retained their byte hashes and mtimes through the cold duplicate process.

The isolated SaveGames were then deleted and verified absent. Both retained logs remain, with zero OddsWell test, Unreal automation, or Zen processes left running.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused canonical commitment automation | `1/1` passed |
| Full native OddsWell automation | `19/19` passed |
| Frozen simulation and odds contracts | `68/68` passed across five groups |
| Brain Admin self-check | Passed |
| Editor / game builds | Passed |
| Fresh Windows Development BuildCookRun | Passed in `50.39s`; `50` files / `1,045,915,742` bytes before runtime saves |
| Clean first packaged process | H26A and H26B `transition=created`; exact fresh-opening public commitment |
| Separate cold packaged process | H26A and H26B `transition=duplicate`; every field identical |
| Packaged SaveGame invariance | Both byte hashes and UTC mtimes unchanged |
| Deterministic exporters | Exact league and replay lengths, hashes, and replay seal unchanged |
| Isolated cleanup | Both SaveGames absent; retained logs present; zero matching processes |
| Python compilation / canvas parse / diff hygiene | Passed |

## Ponytail boundary

The phase adds one direct SaveGame type, one read-only reuse of the H26A validator, and one GameMode call. It does not add a prediction service, offer framework, database, dependency, scheduler, UI, or new model.

## Truth boundary and next gate

This proves only one immutable equal-public pregame prediction commitment linked to the active local-beta schedule. It is not an offer, price, player request, debit, lock, simulation, result, settlement, correction, backend, deployment, or production clock.

The next gate is Scope Director review of the smallest versioned offer record that consumes both the immutable H26A schedule and H26B public commitment without mutating either. No offer is authorized by this phase alone.

See [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]] and [[Design/Decisions/DEC-018 Canonical Local Beta Schedule Timing]].
