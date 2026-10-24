---
tags:
  - development
  - phase-1l
  - unreal
  - sundale
  - lighting
status: complete-bounded-pass
date: 2026-08-06
---

# Phase 1L.1c — Sundale Late-Afternoon Atmosphere Pass

## Outcome

**COMPLETE FOR ONE BOUNDED EXISTING-LIGHT ATMOSPHERE PASS.**

The existing Sundale daylight now carries a warmer late-afternoon direction with cool ambient fill and light warm haze. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]] and the approved [[Design/Decisions/DEC-008 Beta First City Direction|DEC-008]] atmosphere without introducing a final lighting rig or time-of-day system.

## Smallest implementation

One existing C++ file applies one fixed spec to the three existing native map actor families during the already-local Sundale presentation build:

- one directional light: intensity `5.0`, temperature enabled at `5000 K`;
- one skylight: intensity `0.8`, slightly cool fill `#D8E4F0`; and
- one exponential height fog: density `0.003`, warm inscattering `#E8C9A5`.

No actor is spawned. No light, sky, or fog transform changes. Dedicated servers still skip the local presentation path. One focused automation contract locks exact actor counts and bounds daylight intensity/temperature, skylight fill intensity, and light warm haze.

## Preserved presentation and gameplay contracts

The exact Phase 1L.1a `31`-part presentation list and marker remain unchanged. The exact Phase 1L.1b seven destinations, `16` identity parts, and marker remain unchanged. All parts remain transient, non-replicated, and collision-disabled.

The authored Sundale map asset, actor transforms, gameplay coordinates, collision, route points and distance, thresholds, prompts, interaction radii, shared-session/replication/authority rules, SaveGames, brains, simulator, league, ledgers, economy, wagers, inventory, housing, interiors, stores, and stadium behavior remain unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleAtmosphere` | PASS `1/1` |
| Full native `OddsWell` | PASS `53/53` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `26.21s` |
| Package audit | PASS `50` files / `1,049,739,180` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `FD5C1E99655558D50C5F3382C0C3E21DAC5AC63CBC78E5718EBE9F9DEEA9B492`.
- UFS manifest SHA-256: `DF7B5F71A7C4E3178D4D4F4E580DD97964377FE26C57D43D323D7CADF1A9F52F`.

## Packaged route and performance evidence

The fresh automated package emitted the new marker exactly once:

`ODDSWELL_SUNDALE_ATMOSPHERE|result=PASS|directional=1|skylight=1|fog=1|temperature_k=5000|directional_intensity=5.00|skylight_intensity=0.80|fog_density=0.0030|local_only=true|existing_native_actors=true|post_process=false|time_of_day=false|weather=false|final_lighting=false`

The retained Phase 1L.1a `31`-part marker and Phase 1L.1b `7`-destination/`16`-part marker each appeared exactly once. The unchanged automated route passed after `154.504s` with `11/11` points, `79,790.6 cm` traveled, exact home return, landed movement, blocking floor collision, and `1.0 cm` vertical range. The packaged process exited with code `0`; no player, keyboard, mouse, or manual input drove this proof.

Forty half-second samples after a six-second warm-up measured:

- working set average/peak: `1,531.8 / 1,534.4 MiB`;
- private bytes average/peak: `3,569.7 / 3,573.9 MiB`.

This is a bounded local-machine sample, not a minimum-PC target or final-art performance promise.

## Rendered evidence and objective comparison

Normal packaged captures:

- Studio/start: `1,136,709` bytes; SHA-256 `424578B96536BE62207564378D89E57B31CDB130D673946FD813CBE7FE2A6CBE`.
- Arena-return: `1,053,959` bytes; SHA-256 `A85C863A9FFE22DC35F2CFBAA1FFAF0CEF0ACA9D09640A1C71E15AD6688E5836`.

The comparison uses the same normal `1280x720` Studio/start and Arena-return viewpoints from Phase 1L.1b and Phase 1L.1c. Pillow `12.2.0` converted each screenshot to 8-bit grayscale for luminance distribution; `R-B` is the difference between full-frame mean red and blue channel values. These are objective image measurements, not calibrated photometry or a readability study.

| View | Phase | Mean luma | P05 / P50 / P95 | Luma <= 5 | Luma >= 250 | Mean R-B |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| Studio/start | 1L.1b | `133.59` | `41 / 125 / 243` | `0.000%` | `0.819%` | `-37.01` |
| Studio/start | 1L.1c | `138.01` | `52 / 128 / 249` | `0.000%` | `4.662%` | `-12.56` |
| Arena-return | 1L.1b | `141.37` | `18 / 167 / 218` | `0.159%` | `0.000%` | `14.50` |
| Arena-return | 1L.1c | `142.41` | `21 / 168 / 226` | `0.044%` | `0.000%` | `40.41` |

Both views shift warmer. The Arena retains zero sampled bright-luma clipping while its dark tail improves slightly. The Studio bright-luma rise is concentrated in the visible sky/horizon, but the close frame cannot establish whether other approaches retain highlight detail. Both screenshots remain close wall-side views and do not prove prompt/UI readability, clothing readability across the commons, all destinations, patterned-shade quality across the route, manual usability, accessibility, subjective atmosphere, or final color grading.

## Boundary and next gate

No external asset, plugin, dependency, post-process framework, weather, time-of-day system, sun animation, music, production texture or mesh, final material, new district, catalog, accessibility baseline, final lighting, or final-art approval was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize a broader lighting system, accessibility-completion, or release-readiness claim.
