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

# Phase 1F.4 Readable Three-Minute Stadium Presentation

## Outcome

Phase 1F.4 is complete. The stadium's existing authoritative replay renderer now presents the accepted 421-frame game using the owner-approved current-beta defaults: symbolic 3D athletes, one fixed broadcast camera, text callouts, no voice commentary, a three-minute default cadence, and no skip control before the result-invariance phase.

Ponytail kept the implementation inside the existing replay actor. No second parser, replay system, fixture, UI framework, camera framework, audio system, dependency, service, or resimulation path was added.

## Player-visible presentation

The fixed camera now frames all twelve symbolic athletes closely enough to read their labels. The persistent HUD shows frame progress, game clock, Harbor and Mesa score, event kind and label, offense, actor, target, and `Overtime: NO` for this verified regulation archive. The final frame adds the exact authoritative replay seal.

The renderer uses `180 / 421` seconds per archived frame by default. A command-line interval override remains QA-only so automated evidence can run quickly; runtime logs distinguish overridden and default cadence.

## Authoritative boundary

The unchanged public fixture still contains:

- `421` frames;
- Harbor City Waves `101` - `104` Mesa Vista Sol;
- fixture SHA-1 `a3b56bf84557babcd58c96acd40f94198b6c8c81`;
- fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`;
- replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`; and
- canonical replay-frame trace SHA-256 `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe`.

The client still cannot change the score, clock, actors, events, result, or seal.

## Accepted evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 Windows Development editor/game build | Passed |
| Focused presentation automation | `1/1` passed |
| Full native `OddsWell` automation | `10/10` passed |
| Final Windows BuildCookRun | Passed in `64.83s` |
| Static final package | `50` files, `1,042,530,244` bytes |
| Accelerated packaged replay | `421/421`; final `101-104`; exact seal and canonical trace; zero replay errors |
| Rendered default-cadence replay | `180.016s` from ready to final frame; game elapsed `180.006s`; `421/421`; final `101-104`; exact seal and canonical trace |
| Offscreen visual proof | Two `1280x720` midpoint/final captures; athletes, labels, HUD, regulation status, and final seal visible |
| Frozen simulator regression | `65/65` passed in `166.190s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged hashes and counts |
| Python compilation | Passed |
| Cost | `$0.00` |

An unrendered NullRHI run advanced Unreal game time faster than wall time, so it was retained only as headless correctness evidence and was not accepted as player-duration proof. The rendered packaged run is the duration authority.

## Boundary and next gate

This phase does not add skip behavior, late-arrival reconstruction, reconnect reconstruction, voice commentary, camera cuts, replay cuts, crowd, final athlete or team art, wager interaction, odds, settlement, backend, hosting, purchase, or deployment.

The next gate is **Phase 1F.5 result invariance**: prove that full watch, skip, late arrival, and reconnect paths all terminate at the same recorded `101-104` result and exact replay seal without resimulation.
