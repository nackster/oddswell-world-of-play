---
tags:
  - development
  - phase-1l
  - unreal
  - city
  - arena
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1f — Sundale Arena Entrance Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED ARENA-ENTRANCE PRESENTATION PASS.**

The existing Sundale Arena entrance now has one intentional native-primitives exterior treatment instead of relying only on its broad facade, awning, and destination-identity portal. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#First-hour player journey|First-hour player journey — Find work and the sports location]], and [[Design/Beta Game Bible#Required beta locations|Basketball stadium or simplified arena]] without inventing final architecture, signage, text, or brand.

## Smallest implementation

The existing local Sundale presentation builder adds exactly five native-cube parts around the canonical Arena threshold at `(7000, 18000)`:

- two charcoal portal piers;
- one burnt-orange portal cap;
- one sand threshold inset; and
- one restrained-cobalt approach band.

The five unique IDs cover exactly four bounded roles. They reuse the approved Phase 1L.1a palette, Engine cube, BasicShape material, and existing presentation spawn helper. Every part is transient, local-only, non-replicated, collision-disabled, and absent on dedicated servers. The exact Phase 1L.1a `31`-part, Phase 1L.1b `7`-destination/`16`-part, Phase 1L.1c atmosphere, Phase 1L.1d Studio, and Phase 1L.1e Job-frontage contracts remain unchanged.

One opt-in `-ArenaPresentationQa` branch stages the existing character at one fixed exterior view, clears prior QA-only screen messages, requests a screenshot, and then lets the unchanged Stadium QA continue. It creates no camera, framework, production interaction, or manual-input path.

One focused automation contract locks the five exact unique IDs, role counts, positive scales, approved palette, bounded distance and height around the existing threshold, and unchanged route waypoint, `350 cm` radius, enter/exit prompts, city-side return offset, Sportsbook separation, archived replay origin, and replay scale.

## Arena, transition, and replay contract preserved

The city prompt remains exactly `Press E to enter the public viewing graybox`; the interior prompt remains exactly `Press E to exit the public viewing graybox`. The E transition, canonical entrance coordinate, `350 cm` radius, exact city return, eight blocking interior surfaces, five zones, archived replay consumer, presentation duration, player skip, sealed result, and score are unchanged.

The Sportsbook/Ticket Booth remains a separate city location and UI. No authored map transform, collision, route, shared session, replication, authority, save, ledger, economy, wager, inventory, brain, simulator, store, housing, Job, Stadium interior, replay, or result behavior changed.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleArenaEntrance` | PASS `1/1` |
| Full native `OddsWell` | PASS `56/56` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `32.85s` |
| Package audit | PASS `50` files / `1,049,872,300` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `A27272E99F805B83B8BB858A1C5B612E7CE8AE88B4997373B7FF079B3D0BD274`.
- UFS manifest SHA-256: `B67C4151F5187C7674CA3559400F16A83808D58ACE0AC7757D1FD54EEDEA6880`.

## Packaged Arena journey evidence

The final direct packaged run exited with code `0`. On both the initial Sundale load and the required exact-return Sundale load, the new marker appeared once:

`ODDSWELL_SUNDALE_ARENA_ENTRANCE|result=PASS|parts=5|roles=4|threshold_x=7000|threshold_y=18000|local_only=true|replicated=false|collision=false|native_assets=true|text=false|architecture_final=false|final_art=false`

The retained Phase 1L.1a `31`-part, Phase 1L.1b `7`-destination/`16`-part, Phase 1L.1c atmosphere, and Phase 1L.1e Job markers followed the same once-per-Sundale-world pattern. This is two world constructions around one intentional Stadium transition and return, not duplicate construction within one world.

The unchanged automated Stadium QA entered from threshold `(7000, 18000)`, independently counted `8` blocking interior surfaces and `5` zones, visited all `5/5` zone waypoints, reached the archived-match viewing marker with `resimulated=false`, exited, and returned to the exact saved city-side location with `return_distance=0.0`. Its final marker retained `sportsbook=separate`, `replay=archived`, `resimulated=false`, and `wagering=false`. The accepted log contains zero OddsWell failure, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove this proof.

## Rendered evidence and objective limits

The accepted automated packaged fixed view is `1280x720`, `1,424,282` bytes, with SHA-256 `01E97E6EA3DCD1E90E77503F7BAF494303C81B563AB2C831D7A9C1BC21C884B0`. It documents the bounded native approach band, threshold, and nested portal composition from one centered exterior view.

Pillow `12.2.0` measured the 8-bit RGB image without calibrated photometry: mean luminance `152.411`; P01/P50/P99 luminance `26.757 / 143.771 / 241.618`; pixels below luminance `16` at `0.017%`; pixels above luminance `239` at `2.318%`; pixels with all channels at or above `253` at `0.000%`; mean saturation `0.4035`; and mean `R-B` `66.317`.

The image has no same-view pre-phase baseline. It does not prove the normal player approach, interaction prompt, every exterior angle, interior, color or text readability, player understanding, accessibility, subjective usability, final architecture, final material, final lighting, final brand, or beta readiness.

## Performance evidence and limits

The packaged Arena entry, five-zone interior walk, exit, and return supplied `110` quarter-second whole-process samples:

- all-run working set average/peak: `1,405.3 / 1,586.4 MiB`;
- all-run private bytes average/peak: `3,369.6 / 3,666.1 MiB`; and
- `106` post-initialization samples above `500 MiB` working set averaged/peaked at `1,445.8 / 1,586.4 MiB` working set and `3,486.8 / 3,666.1 MiB` private bytes.

This includes cold startup, two level transitions, and automated interior movement. It is not a steady-state, representative-population, minimum-PC, final-art, or optimization promise.

## Boundary and next gate

No external asset, plugin, dependency, final architecture, signage, text, brand, ticket-booth change, new location, district, post-process framework, time-of-day/weather system, music, final material, final lighting, accessibility baseline, owner/manual test, or release-readiness claim was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize Stadium content expansion or release-readiness claims.
