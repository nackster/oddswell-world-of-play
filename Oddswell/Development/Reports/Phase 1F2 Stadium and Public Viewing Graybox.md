---
tags:
  - development
  - beta
  - unreal
  - stadium
  - phase-1f
status: complete
date: 2026-07-21
---

# Phase 1F.2 Stadium and Public Viewing Graybox

## Outcome

Phase 1F.2 is complete. The packaged Unreal client now has a reversible, team-neutral stadium graybox connected to Sundale's existing Arena threshold.

The venue contains only the smallest structural proof needed for the next dependency:

- eight blocking primitive surfaces covering the room, court, viewing deck, viewing row, and walls;
- five labeled zones: entry/concourse, court floor, public viewing, future match presentation, and exit;
- one `E` interaction to enter from the Arena and one `E` interaction to return;
- restoration of the player's actual safe city entry position; and
- the existing read-only public league overlay.

## Truth boundary

The future presentation zone is a marker, not a replay screen. The stadium has no replay consumption, basketball simulation, resimulation, live result, crowd, camera sequence, commentary, team branding, final art, wager interaction, odds, settlement, economy mutation, backend, external service, purchase, or deployment behavior.

The sportsbook remains a separate Sundale waypoint. Phase 1F.2 does not imply that wagering is available.

## Corrective evidence

Two preliminary packaged return checks were rejected because Sundale's Arena marker lies on a blocking line. Unreal correctly displaced the player capsule by `42.1 cm`, proving that the marker center was not a safe spawn location.

The accepted implementation stores the player's actual walkable city position when entering the stadium and restores that position on exit. The deterministic QA route uses a valid point beside the threshold. Its final packaged measurement was `0.0 cm` of horizontal return error; the threshold was not weakened to hide the collision.

## Accepted validation

| Check | Accepted result |
| --- | --- |
| UE 5.8 Windows Development game build | Passed |
| UE 5.8 Windows Development editor build | Passed |
| Native `OddsWell.Character` automation | `9/9` passed, including `StadiumGraybox` |
| Windows BuildCookRun | Passed in `45.14s` |
| Final package | `55` files, `1,042,633,653` bytes |
| Packaged NullRHI stadium route | Exit `0`; all `5/5` zones; presentation marker reached; `0.0 cm` return; zero fatal, ensure, or stadium-failure markers |
| Packaged offscreen visual route | Exit `0`; QA pass; one `1280x720` screenshot, `123,846` bytes |
| Frozen simulator regression | `65/65` passed in `129.803s` |
| Brain Admin self-check | Passed |
| Deterministic public league export | `2` teams, `12` athletes, `20` games; SHA-256 `621e8eab5a779e000cd69b83d307fc99931e2809a2cb620e96cef6eeada160b5` |
| Python compilation | Passed |
| Cost | `$0.00` |

The accepted packaged runtime evidence is in the ignored local logs `Phase1F2-Packaged-NullRHI-Final2.log` and `Phase1F2-Packaged-Visual.log`. The ignored local visual proof is `Phase1F2_StadiumGraybox.png` inside the final package's Saved screenshots directory.

## Next gate

Phase 1F.3 should consume one already verified archived replay directly inside this stadium. It must preserve the authoritative event-log boundary and must not resimulate basketball. Presentation duration, cameras, commentary, skip rules, and 82-game variety remain later owner gates.
