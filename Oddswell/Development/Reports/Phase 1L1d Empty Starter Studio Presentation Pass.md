---
tags:
  - development
  - phase-1l
  - unreal
  - housing
  - studio
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1d — Empty Starter Studio Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED EMPTY-STUDIO PRESENTATION PASS.**

The mandatory private Starter Studio now reads as a modest home-progression anchor instead of one undifferentiated test room. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#First-hour player journey|First-hour player journey — Discover the starter home]], and [[Design/Beta Game Bible#Apartment progression|Apartment progression]] without furnishing the empty home or adding a decorating system.

## Smallest implementation

One existing Studio construction path now adds exactly ten native-cube presentation pieces:

- two non-colliding floor/ceiling insets for surface hierarchy;
- four non-colliding perimeter trim rails;
- one bounded wall accent; and
- three non-colliding return-frame pieces that distinguish the existing exit wall.

The pieces reuse the approved Sundale planning palette and the existing Engine cube/material only. They are transient, local-only, non-replicated, collision-disabled, and absent on dedicated servers. The existing Studio point light retains its original actor, position, `5000` intensity, and `1000` attenuation radius; only its native temperature setting is enabled at a bounded `4500 K`. An opt-in `-StudioPresentationQa` hook requests one screenshot from the existing fixed Studio QA start. It creates no camera or testing framework.

One focused automation contract locks the exact ten unique IDs, four bounded architectural roles, approved colors, positive scales, Studio bounds, light-temperature range, six structural surfaces, fresh zero snap points, three conditional chair parts, and the complete owned-chair single snap point.

## Empty-home and gameplay contract preserved

The fresh production Studio remains exactly:

`structure=6,furniture=0,furniture_parts=0,decorations=0,snap_points=0`

Presentation pieces carry their own tag and are excluded from structure, furniture, decoration, and snap-point counts. They do not create an item, furniture actor, prop, purchase, catalog, placement control, ownership record, schema field, SaveGame slot, or user-index change. The existing owned Modular Chair still appears conditionally as exactly three furniture parts at `studio_primary`; the One-bedroom partition path is unchanged.

Network Studio entry/return authority, shared-session behavior, exact-return storage, authored maps, route coordinates, collision, prompts, thresholds, interactions, ledgers, economy, wagers, inventory, brains, simulator, stores, stadium, and the exact Phase 1L.1a–c contracts remain unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.EmptyStudioPresentation` | PASS `1/1` |
| Full native `OddsWell` | PASS `54/54` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `33.46s` |
| Package audit | PASS `50` files / `1,049,806,764` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `A6CA3361F767886F00383C9F3AAD70AEF2A067187007E8238A9A6AFDF6F54DD4`.
- UFS manifest SHA-256: `5831FC463D972A58DA6B1810DEC8AD231040917F8A81A1FB37354F88E6E29532`.

## Packaged Studio journey and performance evidence

The fresh packaged run emitted the new marker once:

`ODDSWELL_STUDIO_PRESENTATION|result=PASS|parts=10|roles=4|empty_contract=6/0/0/0|owned_chair_conditional=true|presentation_excluded_from_contents=true|local_only=true|replicated=false|collision=false|native_assets=true|final_art=false`

The existing production marker then reported the exact fresh Studio truth:

`ODDSWELL_STUDIO_READY|result=PASS|private=true|visits=false|active_tier=studio|structure=6|upgrade_surfaces=0|furniture=0|furniture_parts=0|decorations=0|snap_points=0`

The unchanged automated Studio QA entered from Sundale, independently counted `structure=6,furniture=0,decorations=0,snap_points=0`, walked `200.2 cm` on the interior floor, exited, returned to `SundaleGraybox`, and reported `entered=true|empty=true|walkable=true|exited=true|returned=SundaleGraybox`. The final direct packaged capture/performance run exited with code `0`; its accepted log contains zero OddsWell failure, fatal-error, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove this proof.

The short direct packaged journey supplied `27` quarter-second whole-process samples:

- all-run working set average/peak: `1,207.6 / 1,596.2 MiB`;
- all-run private bytes average/peak: `2,673.8 / 3,634.0 MiB`; and
- `23` post-initialization samples above `500 MiB` working set averaged/peaked at `1,359.9 / 1,596.2 MiB` working set and `3,100.1 / 3,634.0 MiB` private bytes.

This includes cold startup and two level transitions, lasts only the bounded QA journey, and is not a steady-state, minimum-PC, or final-art performance promise.

## Rendered evidence and objective limits

The automated packaged fixed-start capture is `1280x720`, `964,452` bytes, with SHA-256 `6DF2723497B3F1764074E33718A368DA1F7472FA0900ADE721106E66B155698D`.

Pillow `12.2.0` measured the 8-bit RGB image without calibrated photometry: mean luminance `176.32`; P01/P50/P99 luminance `81.30 / 175.08 / 254.78`; pixels below luminance `16` at `0.008%`; pixels above luminance `239` at `7.810%`; pixels with all channels at or above `253` at `0.844%`; mean saturation `0.325`; and mean `R-B` `62.18`. The bright tail is concentrated mainly in the ceiling/lighted surface region and is disclosed rather than treated as proof of global highlight safety.

The single normal third-person frame visibly contains the empty-room treatment, return-frame cue, and existing leave prompt. It does not cover every approach or corner, compare against a same-view pre-phase empty-Studio capture, prove prompt or color readability, validate player understanding, establish accessibility or subjective usability, approve final materials or lighting, or prove beta readiness.

## Boundary and next gate

No external asset, plugin, dependency, furniture, decoration, catalog, purchase, placement control, new room, One-bedroom change, post-process framework, time-of-day/weather system, music, final material, final lighting, accessibility baseline, final-art approval, or owner/manual test was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize broader housing content or release-readiness claims.
