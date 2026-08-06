---
tags:
  - development
  - beta
  - basketball
  - wagering
  - unreal
  - phase-1h
status: complete
date: 2026-07-24
---

# Phase 1H.26E Server-Authoritative Canonical Match Winner Request and Atomic Stake Debit

## Outcome

OddsWell now accepts one exact Match Winner request for the active local-beta opener through a server-owned wrapper.

The caller supplies only:

- the exact Phase 1H.26C offer ID;
- one team published by that offer; and
- one whole Odds Bucks stake allowed by the existing `10`–`100`, step-`10` contract.

The wrapper reloads and independently validates the exact Phase 1H.26A schedule, Phase 1H.26B public prediction commitment, and Phase 1H.26C persisted offer. It obtains acceptance time from server UTC, derives one stable server request command from the offer ID, and then calls the existing atomic request/debit primitive once.

The accepted `40`-credit proof reused the existing local job credit:

| Evidence | Exact value |
| --- | --- |
| Job credit | sequence `1`, `+100` |
| Stake debit | sequence `2`, `-40`, `match_winner_stake` |
| Final balance | `60` |
| Requests | `1` |
| Status | `accepted_pending_lock` |
| Selected team | Harbor City Waves |
| Probability | `57586693` |
| Decimal odds | `17365` |
| Gross return | `69` |

## Immutable request evidence

Odds Bucks SaveGame schema `12` adds versioned request evidence for newly accepted requests:

- offer schema, ID, version, market, and currency;
- source prediction version, snapshot version, model, and commitment SHA-256;
- season, game, home team, away team, and selected team;
- selected integer probability and integer decimal odds;
- stake, payout formula, and exact floor gross return;
- server acceptance time, offer lock, command links, and status.

Legacy records remain readable with evidence version `0`. New records require evidence version `1` and exact internal consistency. Exact cold retry returns `Duplicate` without changing the first server time or persisted bytes. Reusing the server command with a changed team or stake rejects.

## Fail-closed and atomic boundary

Wrong offer ID, unapproved team, bad stake, changed valid stake, before-creation time, at-tipoff time, tampered Phase 1H.26A input, tampered Phase 1H.26B input, tampered Phase 1H.26C record, and insufficient funds all reject with zero ledger/request mutation.

The focused native test also made the funded QA SaveGame read-only immediately before the final atomic write. Native persistence failed, the request returned `Rejected`, the SaveGame stayed byte-identical, balance remained `100`, and zero requests persisted.

The normal Phase 1H.26D ticket-booth cards and slip remain read-only. No selection control, stake editor, confirmation control, or automatic normal-play submission path was connected. The packaged request route is an explicit isolated command-line QA path only.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| Focused native automation | `OddsWell.League.CanonicalMatchWinnerRequest` passed `1/1` |
| Full native automation | `21/21` passed |
| Phase 1H odds contracts | `3/3` passed in `0.045s` |
| Frozen Python regressions | `68/68` passed in `122.362s` |
| Brain Admin self-check | Passed |
| Python compilation | Passed |
| Unreal editor build | Passed |
| Unreal game build | Passed |
| Final Windows BuildCookRun | Passed in `68.62s`; `50` files / `1,046,248,718` bytes |
| Packaged first process | Accepted; sequence `2`, delta `-40`, entries `2`, requests `1`, balance `60` |
| Separate cold process | Exact duplicate; bad offer/team/stake rejection audit; zero mutation; QA cleanup |
| Deterministic league export | `30,288` bytes; SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff` |
| Deterministic replay export | `256,442` bytes; SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f` |
| Cost | `$0.00` |

Retained packaged logs:

- `client/OddsWell/Saved/Logs/Phase1H26E_PackagedAccepted.log`
- `client/OddsWell/Saved/Logs/Phase1H26E_PackagedColdDuplicate.log`

After the cold verifier, the isolated QA ledger was absent. The exact upstream files retained their first-process UTC mtimes and ended with these hashes:

- schedule: `cc2222a65669e5493fe59c941550da7ad2e32ab1b4dce88ecd539a44d2fafcdc`;
- commitment: `e96ecfb6d47aa6fab844d55fa83e240b9179cca48240b81ec36f45d05339552e`; and
- offer: `dcf0dc1689162c4d8b53729681dbb93e75511f4be926e32e0282934384c35bcf`.

## Truth boundary and next gate

This phase proves request acceptance and atomic stake debit only. It does not prove a normal player input flow, receipt, game-start lock, canonical result, settlement, history, multiple requests, another market, backend account, payment, real-money path, deployment, retraining, simulator change, or brain change.

The smallest next candidate is a read-only canonical pending receipt for the exact Phase 1H.26E request. Scope review must confirm that gate before implementation.
