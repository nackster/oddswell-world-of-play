---
tags:
  - development
  - phase-1l
  - unreal
  - stadium
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1i — Stadium Public-Viewing Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED STADIUM PUBLIC-VIEWING PRESENTATION PASS.**

The existing authoritative archived game remains watchable through the same fixed-camera Stadium path, while its bare court/public-viewing graybox now receives one small native-primitives presentation layer. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L match-presentation steps 1, 2, and 5]], [[Design/Beta Game Bible#First-hour player journey|First-hour player journey — Place and watch the first wager]], [[Design/Beta Game Bible#Basketball presentation|Basketball presentation]], and [[Design/Beta Game Bible#Art, music, and storytelling|Art, music, and storytelling]] without adding a crowd, team identity, final art, camera system, texture, material family, audio, or external dependency.

## Smallest implementation

The existing Stadium game mode adds exactly eleven native-cube parts across four bounded roles:

- four sand court-perimeter edge marks;
- two burnt-orange viewing-deck front edges;
- two restrained-cobalt aisle marks; and
- one three-part burnt-orange/cobalt public-viewing frame.

The parts reuse the existing Engine cube, BasicShape material, and approved Sundale planning palette. Every part uses the existing transient spawn parameters, is local-only, non-replicated, collision-disabled, physics-disabled, overlap-disabled, and absent on dedicated servers. They have their own presentation tag and do not count as Stadium structure or zones.

One opt-in `-StadiumPresentationQa` branch places the automated character at one fixed south-side view, faces the existing court/public-viewing area, clears QA screen messages, and requests a screenshot before the unchanged five-waypoint Stadium QA continues. It creates no camera, player input, production interaction, or runtime framework.

One focused automation contract locks all eleven exact unique IDs, four role counts, positive scale, approved neutral palette, bounded room placement, separation from the archived replay origin, and unchanged Stadium surface/zone/waypoint counts, radius, prompts, replay origin, and replay scale.

## Stadium and replay contract preserved

The Stadium still contains exactly `8` blocking structural surfaces and `5` zone labels. Entry/exit prompts, `350 cm` radius, transition, city-side return, zone waypoints, and exact return behavior are unchanged. The archived replay remains anchored at `(350, 0, 0)` at scale `0.15`, sourced from `Season1Game1`, and marked `resimulated=false`.

The fixed camera, approximately three-minute full-watch presentation, `S` skip, sealed result, result invariance, event log, game identity, score, athlete decisions, wager placement, settlement, ledgers, saves, authority, session, brains, simulator, city, Ticket Booth, stores, and housing are unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.StadiumPublicViewingPresentation` | PASS `1/1` |
| Full native `OddsWell` | PASS `59/59` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `25.94s` |
| Package audit | PASS `50` files / `1,049,996,716` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `6B2A2B5F054B0A5CB5D5088B7F557632B7792961599F8337DA9DE7A71C1D17C5`.
- UFS manifest SHA-256: `FAD320266DFB89AF1E2A9CBDC6C0052C4C7FB4413BF67AFEE501921B3979E1C6`.

## Packaged Stadium journey evidence

The fresh-profile packaged run exited with code `0`. The presentation marker appeared exactly once:

`ODDSWELL_STADIUM_PUBLIC_VIEWING_PRESENTATION|result=PASS|parts=11|roles=4|materials=11|local_only=true|replicated=false|collision=false|native_assets=true|team_neutral=true|unbranded=true|crowd=0|final_art=false`

The independent Stadium QA counted exactly `11` presentation parts with `0` collision and `0` replication while retaining `8` blocking surfaces and `5` zones. Construction, readiness, presentation QA, and archived replay-consumer markers each passed once. The replay consumer retained `source=Season1Game1`, `mode=authoritative_archived`, `resimulated=false`, and `scale=0.15`.

All `5/5` zone waypoints passed. The viewing marker retained `ARCHIVED_MATCH_PRESENTATION`, archived replay, and no resimulation. The automated character exited to Sundale at the exact saved city-side position with `return_distance=0.0`; Sportsbook remained separate and wagering remained false. The accepted log contains zero OddsWell failure, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove this proof.

## Rendered evidence and objective limits

The accepted automated fixed-view PNG is `1280x720`, `1,257,308` bytes, with SHA-256 `F295185EED73F81B67B60A565AB9DA580F74882F1D7E7F706F1AF2D84212B259`. Pillow `12.2.0` and NumPy `2.3.5` measured its 8-bit RGB image without calibrated photometry:

- mean RGB: `0.5645 / 0.5601 / 0.5558`;
- mean luminance: `0.5610`;
- pixels below luminance `0.10`: `6.311%`;
- pixels above luminance `0.90`: `0.194%`;
- mean saturation: `0.0355`; and
- all-channel clipping: `0.000%`.

The view documents the court-perimeter treatment and part of the upper public-viewing treatment around the unchanged illustrative replay. It has no same-view pre-phase baseline. The fixed view does not independently show all eleven parts or prove the full viewing frame, every angle, normal player approach, zone-label or replay-text readability, replay comprehension, accessibility, subjective usability, final athlete/team/court/crowd art, final materials/lighting/audio, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The packaged Stadium entry, fixed-view capture, five-zone walk, exit, and return supplied `126` quarter-second whole-process samples:

- all-run working set average/peak: `1,412.8 / 1,612.8 MiB`;
- all-run private bytes average/peak: `3,386.2 / 3,782.0 MiB`; and
- `121` post-initialization samples at or above `500 MiB` working set averaged/peaked at `1,460.1 / 1,612.8 MiB` working set and `3,518.9 / 3,782.0 MiB` private bytes.

This includes cold startup, two level transitions, automated movement, and the archived replay consumer. It is not a steady-state, representative-population, minimum-PC, final-art, or optimization promise.

## Boundary and final batch gate

No crowd system, athlete/team/final art, final court, camera cut, new camera, texture, material family, audio, music, external asset, plugin, dependency, gameplay interaction, replay change, accessibility baseline, owner/manual test, or release-readiness claim was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit.

This is new-batch phase `6/6`. After Coordinator, Notion, and independent re-fetch closure, the next action is a read-only six-phase audit and owner-facing status summary. Do not begin a seventh implementation phase from this batch.
