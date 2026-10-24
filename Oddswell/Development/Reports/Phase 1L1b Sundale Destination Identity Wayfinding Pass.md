---
tags:
  - development
  - phase-1l
  - unreal
  - sundale
  - wayfinding
status: complete-bounded-pass
date: 2026-08-06
---

# Phase 1L.1b — Sundale Destination-Identity Wayfinding Pass

## Outcome

**COMPLETE FOR ONE BOUNDED PRESENTATION-ONLY DESTINATION PASS.**

The seven required first-hour destinations now have distinct geometric entrance identities layered over the existing Sundale graybox. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]] without introducing final brands, readable commercial text, or new gameplay.

## Smallest implementation

One existing C++ file reuses the Phase 1L.1a transient native-cube and built-in material path. It adds `16` parts:

- Starter Studio: two contrasting doorway posts;
- Job: a post-and-cap silhouette;
- Clothing Store: two asymmetric vertical panels;
- Arena: two pylons and a broad crown;
- Sportsbook/Ticket Booth: two offset horizontal slabs;
- Public Court: two posts and a colored gateway cap; and
- Furniture Store: two stacked shelf-like slabs.

Every ID is unique. Exactly seven destination roles are represented. Each part stays inside the bounded Sundale presentation area, has positive scale, and uses the approved warm limestone, muted terracotta, sand concrete, sage green, restrained cobalt, burnt orange, or charcoal palette. No text is required to distinguish the silhouettes.

## Preserved presentation and gameplay contracts

The original `31` Phase 1L.1a parts and exact `ODDSWELL_SUNDALE_PRESENTATION` marker remain intact. The shared spawn path still uses only Unreal's built-in Cube and BasicShapeMaterial. Each process builds the presentation once in its local Sundale world; dedicated servers skip it. Every part is transient, non-replicated, and collision-disabled at actor and component level.

No authored map actor, component, transform, material, light, fog, collision profile, gameplay coordinate, route point, distance, threshold, prompt, interaction radius, shared-session or authority rule, SaveGame, brain, simulator, league, ledger, economy, wager, inventory, housing, interior, store, or stadium behavior changed.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleDestinationIdentity` | PASS `1/1` |
| Full native `OddsWell` | PASS `52/52` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `26.10s` |
| Package audit | PASS `50` files / `1,049,648,556` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `AD4826C670A265E9FBB93DCC0DDDF43AE435EF5DE119B9391EB3A9CB06D3E8FF`.
- UFS manifest SHA-256: `8CF0FD7B051EE503776F1032A7FCBC5E042726F5143EE58824EE0E4D4E84E00D`.

## Packaged route and performance evidence

The fresh automated package emitted each marker exactly once:

`ODDSWELL_SUNDALE_PRESENTATION|result=PASS|parts=31|local_only=true|collision=false|native_assets=true|final_art=false`

`ODDSWELL_SUNDALE_DESTINATION_IDENTITY|result=PASS|destinations=7|parts=16|local_only=true|collision=false|native_assets=true|text_required=false|final_art=false`

The unchanged automated run route passed after `154.583s` with `11/11` points, `79,790.8 cm` traveled, exact home return, landed movement, blocking floor collision, and `1.0 cm` vertical range. The packaged process exited with code `0`. No player, keyboard, mouse, or manual input drove this proof.

Forty half-second samples after a six-second warm-up measured:

- working set average/peak: `1,532.8 / 1,538.3 MiB`;
- private bytes average/peak: `3,565.9 / 3,571.6 MiB`.

This is a bounded local-machine sample, not a minimum-PC target or final-art performance promise.

## Rendered evidence and limitation

- Normal Studio/start capture: `1,163,928` bytes; SHA-256 `FEB97A9383A513DF8F76266C69D37973600E9B29B7727D126DFACFCD953F0EA5`.
- Normal Arena-return capture: `1,073,665` bytes; SHA-256 `43328EF05F249A1FA08BCBCAC0C03990ACC46FA577CF010AFB42D0BB04A3CA7B`.

Both captures were created automatically by packaged `HighResShot`; no player input was sent. Both remain close wall-side views. They retain presentation evidence at the normal start and Arena return but do not establish that all seven cues are visible, that prompts or entrances are unobscured from every approach, or that players understand the wayfinding. No subjective usability, accessibility, whole-city coherence, or owner approval is claimed.

Two later automated camera-staging diagnostics are explicitly rejected: one combined `BugItGo` with locomotion QA and invalidated that diagnostic's movement/floor start, while one capture-only attempt emitted no PNG. Neither diagnostic log nor any output from them is accepted or cited as phase evidence. Their processes were stopped and final process/port cleanup passed.

## Boundary and next gate

No external asset, plugin, dependency, texture, production mesh, final material, readable commercial text, final brand, final lighting system, music, district, catalog, accessibility baseline, or final-art approval was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize a broader district, catalog, accessibility-completion, or release-readiness claim.
