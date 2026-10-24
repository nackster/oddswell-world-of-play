---
tags:
  - development
  - beta
  - unreal
  - replay
  - stadium
  - phase-1f
status: complete
date: 2026-07-21
---

# Phase 1F.5 Replay-View Result Invariance

## Outcome

Phase 1F.5 is complete, and Phase 1F exits for the current archived-game slice. Full watch, direct skip, mid-watch player skip, late arrival, and seal-validated cold reconnect all terminate at the same authoritative frame `421`, Harbor City `101` - `104` Mesa Vista, and replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

The player may now press `S` during the stadium presentation to jump to the sealed final result. The on-screen instruction is part of the existing replay HUD.

Ponytail kept this inside the existing replay actor. One validated start-frame resolver and one skip-to-final function cover every view path. No second renderer, replay copy, save format, network framework, service, dependency, or resimulation path was added.

## View contract

| Path | Start / transition | Rendered frames | Accepted outcome |
| --- | --- | ---: | --- |
| Full watch | Frame `1` | `421` | Frame `421`, `101-104`, exact seal |
| Direct QA skip | Frame `421` | `1` | Frame `421`, `101-104`, exact seal |
| Late arrival | Frame `211` | `211` | Frame `421`, `101-104`, exact seal |
| Cold reconnect | Frame `211` plus exact replay seal | `211` | Frame `421`, `101-104`, exact seal |
| Mid-watch player skip proof | Watch through `211`, then invoke the same `S` function | `212` | Frame `421`, `101-104`, exact seal |
| Forged reconnect | Frame `211` plus wrong seal | `0` | Rejected before rendering |

Every accepted log states `resimulated=false`. Reconnect cursors outside `1-421`, forged seals, unknown view modes, and invalid QA skip requests fail closed.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 Windows Development editor/game build | Passed |
| Full native `OddsWell` automation | `10/10` passed |
| Final Windows BuildCookRun | Passed in `65.27s` |
| Static final package | `50` files, `1,042,571,204` bytes |
| Six packaged view/boundary runs | Five accepted paths exited `0` with exact result/seal; forged reconnect exited `0` after fail-closed rejection and rendered `0` frames |
| Offscreen reconnect proof | `1280x720`; reconnect cursor, `S` instruction, final score, and exact seal visible |
| Frozen simulator regression | `65/65` passed in `163.106s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged hashes and counts |
| Python compilation | Passed |
| Cost | `$0.00` |

## Truth boundary

The reconnect proof is a cold packaged process reconstructing from an explicit public frame cursor bound to the exact replay seal. It is not an account, backend, live network session, reconnect transport, cursor-delivery service, matchmaking system, or deployment claim. The direct skip mode is QA evidence; the actual player control is the `S` key routed through the same skip-to-final function.

This phase adds no wager, odds, settlement, Odds Bucks, purchase, job, account, hosting, final art, voice commentary, model, training, or retraining behavior.

## Next gate

Phase 1G.1 may add the smallest empty, server-authoritative virtual Odds Bucks ledger with append-only entries and idempotent commands. Starting balance, job fantasy, payout, allowance cadence, recovery floor, prices, and limits remain owner gates and must not be invented in that ledger phase.
