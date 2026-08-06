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

# Phase 1F.3 Direct Archived Replay Consumption in Stadium

## Outcome

Phase 1F.3 is complete. Entering the stadium now creates one compact instance of the existing verified archived-replay actor on the primitive court. The stadium consumes Season 1 Game 1 directly; it does not run or call the basketball simulator.

Ponytail kept this phase to the existing native path. No second parser, renderer, fixture, service, plugin, dependency, map, or presentation framework was added.

## Authoritative input and client boundary

The unchanged fixture remains `oddswell-public-replay-v1` with:

- `421` frames;
- Harbor City Waves `101` — `104` Mesa Vista Sol;
- fixture SHA-1 `a3b56bf84557babcd58c96acd40f94198b6c8c81`;
- fixture SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`; and
- authoritative replay seal `00e4f82c2bb4da5d9ad53d75bf76ece7b97ed9b05ca2f7a8a2628d396c779b75`.

The stadium scales the existing symbolic renderer to `0.15` and anchors it on the primitive court. Its fixed positions remain explicitly illustrative. The renderer still validates the exact public fixture and displays public score, clock, event, actor, target, and final seal.

## Packaged evidence

| Check | Accepted result |
| --- | --- |
| UE 5.8 Windows Development game build | Passed |
| UE 5.8 Windows Development editor build | Passed |
| Native `OddsWell.Character` automation | `9/9` passed |
| Windows BuildCookRun | Passed in `50.18s` |
| Static final package | `50` files, `1,042,508,438` bytes |
| Direct packaged stadium replay | Exit `0`; `421/421` frames; final `101-104`; exact replay seal; zero replay/fatal/ensure errors |
| Sundale → stadium → Sundale proof | All `421` frames; canonical trace matched; `0.0 cm` city return; exit `0` in `18.043s` |
| Canonical replay-frame trace SHA-256 | `12fb61d032a93e667451c364f77907e68e53b934c46f765b6f32eefe9316dbbe`, identical to Phase 1A.2b |
| Packaged replay fixture | `256,442` bytes and byte-identical SHA-256 |
| Offscreen visual proof | Two `1280x720` midpoint/final captures; final seal visible; zero replay errors |
| Frozen simulator regression | `65/65` passed in `153.004s` |
| Brain Admin self-check | Passed |
| Replay and league exporters | Passed with unchanged hashes and counts |
| Python compilation | Passed |
| Cost | `$0.00` |

The ignored local accepted logs are `Phase1F3-Packaged-NullRHI.log`, `Phase1F3-Packaged-Visual.log`, and `Phase1F3-Packaged-CityToStadium.log`. The unchanged renderer retained its earlier ignored midpoint/final screenshot filenames.

## Truth boundary

This phase proves direct consumption only. It does not claim a readable two-to-five-minute final presentation, selected camera language, commentary, replay cuts, skip/condensed behavior, crowd, team branding, final 3D animation, wager interaction, odds, settlement, backend, service, purchase, or deployment. The client still cannot change the recorded score, clock, actors, events, or seal.

## Next owner gate

Phase 1F.4 needs the owner to freeze the presentation defaults. The current recommendation is:

- symbolic 3D placeholders for this beta step;
- one fixed broadcast camera;
- text event callouts without voice commentary;
- approximately three minutes per game; and
- no skip yet, until Phase 1F step 5 proves watch/skip/late-arrival/reconnect result invariance.
