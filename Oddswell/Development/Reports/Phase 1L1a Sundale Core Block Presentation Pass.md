---
tags:
  - development
  - phase-1l
  - unreal
  - sundale
  - presentation
status: complete-bounded-pass
date: 2026-08-06
---

# Phase 1L.1a — Sundale Core-Block Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED NATIVE-PRIMITIVE CITY PRESENTATION PASS.**

The existing `SundaleGraybox` now reads as the approved warm civic-commons direction at its proven first-hour locations instead of remaining entirely gray. This is a presentation layer over the validated map, not a map rebuild or final-art claim.

## Smallest implementation

One existing C++ file adds `31` transient Unreal built-in cube parts:

- `6` route-facing facade accents;
- `6` repeated awnings;
- `5` restrained-cobalt south-route marks;
- `2` public-court bands aligned to the authored court;
- `2` three-part planter/trunk/canopy clusters aligned to existing trees; and
- `6` warm facade details supporting the approved late-afternoon direction.

The exact planning palette is warm limestone `#D8C8A9`, muted terracotta `#A65F47`, sand concrete `#B9A783`, sage green `#6D7F62`, restrained cobalt `#315F79`, burnt orange `#C46D3B`, and charcoal gray `#4D5051`.

Each process builds the layer once in its own Sundale world. Standalone and shared-city clients therefore receive the same dynamic material colors without decorative replication. Dedicated servers skip it. Every part is transient, non-replicated, and collision-disabled. One focused automation contract locks the part count, unique IDs, positive scales, six presentation roles, and exact approved palette.

## Preserved authority and gameplay

The authored `83,147`-byte `SundaleGraybox.umap` and all `45` existing actors remain byte-unchanged. No existing actor or component transform, scale, material, light, fog, collision profile, threshold, prompt, waypoint, route distance, interaction radius, gameplay rule, network authority, SaveGame, brain, simulator, league, ledger, economy, inventory, wager, or store behavior changed.

Existing native directional light, sky, atmosphere, and fog remain unchanged. The warm details and palette support the approved direction, but this phase does not claim a new or calibrated late-afternoon lighting implementation.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleCoreBlockPresentation` | PASS `1/1` |
| Full native `OddsWell` | PASS `51/51` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `30.26s` |
| Package audit | PASS `50` files / `1,049,588,652` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `E114806B3E46398A851E85CE0A815DB785A85FA3649173713C4EB3B2B9C3B026`.
- UFS manifest SHA-256: `99B6D6F1A5BFD667A1C6964CE730E5967F78B3A9BF64D14BD6A1369FFC4FEC07`.

## Packaged route and performance evidence

The fresh automated packaged run emitted:

`ODDSWELL_SUNDALE_PRESENTATION|result=PASS|parts=31|local_only=true|collision=false|native_assets=true|final_art=false`

The unchanged run-route automation then passed after `154.518s` with `11/11` points, `79,788.9 cm` traveled, exact home return, grounded movement, blocking floor collision, and `1.0 cm` vertical range. It exited with code `0`; no player, keyboard, mouse, teleport, transform, or developer intervention was used.

After a six-second warm-up, `40` half-second process samples measured:

- working set average/peak: `1,539.9 / 1,545.7 MiB`;
- private bytes average/peak: `3,585.3 / 3,591.0 MiB`.

This is a bounded local machine sample, not a minimum-PC target or final-art performance promise.

## Rendered evidence and limitation

- Studio/start capture: `1,165,244` bytes; SHA-256 `9004A75BCD95E365A2ADFAFCB4520C8F0227756FEEDAAB816A9A880E61A0447F`.
- Arena-return capture: `1,070,712` bytes; SHA-256 `84A60CD4AA3FEC926BC64718B9D4CD9A4B3B415BDFD732A528A926E6860EE0FA`.

Both screenshots were created automatically by packaged `HighResShot`; no player input was sent. They visibly show the new native facade/awning treatment, but both are close wall-side viewpoints. They do not prove whole-city visual coherence, entrance-prompt readability at every location, manual usability, accessibility, or subjective owner approval.

## Boundary and next gate

No external asset, plugin, dependency, texture, production mesh, final material, final lighting system, music, new district, catalog, accessibility baseline, final city name, or final-art approval was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That does not waive the evidence; it remains required before beta exit. The Scope Director should inspect this bounded result and select only the next smallest placeholder already visible in the proven first-hour path.
