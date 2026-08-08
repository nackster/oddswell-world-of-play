---
tags:
  - development
  - phase-1l
  - unreal
  - furniture-store
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1k — Sundale Furniture Store Frontage Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED FURNITURE-STORE FRONTAGE PRESENTATION PASS.**

The first apartment-item purchase destination now has one small native-primitives storefront frame around the existing physical Furniture Store. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L presentation steps 1, 2, and 5]], [[Design/Beta Game Bible#Beta win condition|Beta win condition]], [[Design/Beta Game Bible#World and city scope|Required beta location — Basic furniture store]], [[Design/Beta Game Bible#Housing and furniture|Housing and furniture]], [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture|DEC-009]], [[Design/Decisions/DEC-011 Empty Starter Studio|DEC-011]], and [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults|DEC-012]] without adding a catalog item, snap point, placement control, final Store fiction, sign, brand, final art, or external dependency.

## Smallest implementation

The existing Sundale presentation builder adds exactly five native-cube parts across four bounded roles:

- two charcoal framing posts;
- one sage header;
- one warm-limestone display sill; and
- one burnt-orange approach band.

The parts reuse the existing Engine cube, BasicShape material, approved planning palette, and transient spawn helper. Every part is local-only, non-replicated, collision-disabled, and absent on dedicated servers. No authored map asset or production interaction actor changed.

One opt-in `-FurnitureStorePresentationQa` branch is contained inside the existing Modular Chair purchase QA. Before the unchanged purchase sequence, it places the automated character at one fixed east-side exterior view, faces the Store, clears QA screen messages, requests one screenshot, and returns to the existing QA stages on the next tick. It adds no production input, camera, interaction, persistence, or framework.

One focused automation contract locks the five exact unique IDs, four role counts, positive scales, approved palette, bounded placement, canonical route waypoint, exact `350 cm` radius, exact `sundale_modular_chair` item id, `100` price, exact three-part chair, zero fresh snap points, one complete-owned-chair snap point, exact `studio_primary` id, and distinct gray/teal colors.

## Furniture Store, chair, and Studio contracts preserved

The Furniture Store remains at `(-9500, 5000)` with the same `350 cm` interaction radius and E-driven review/confirm/purchase path. The only item remains the Sundale-origin Sundale Modular Chair at exactly `100` Odds Bucks. Purchase still requires two confirmations, records one immutable debit, and establishes ownership.

The chair remains exactly three native gray/teal parts and only appears in an owned Studio at the fixed `studio_primary` point. A fresh Studio remains exactly `structure=6,furniture=0,furniture_parts=0,decorations=0,snap_points=0`. No new item, snap point, placement, rotation, storage, refund, trading, catalog, or pre-purchase furniture path was added.

The ledger, save schema/slot/index, authority, shared session, economy, wagering, inventory, brains, simulator, Clothing Store, Job, Ticket Booth, Arena, other housing behavior, city, and all Phase 1L.1a-j layers are unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleFurnitureStoreFrontage` | PASS `1/1` |
| Full native `OddsWell` | PASS `61/61` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `27.12s` |
| Package audit | PASS `50` files / `1,050,071,468` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `C4D1DC65AA7AFED96597D7CA64FAC49B1B8B5D147049279F4DDAD83E6A6F1B5F`.
- UFS manifest SHA-256: `7FA60AF1C88ABF3D3E0E662BAEF7D3C9F8B48EF9FD498D811BAFD18CD4922058`.

The accepted evidence root is `C:\tmp\OddsWellPhase1L1k\Evidence`; the package root is `C:\tmp\OddsWellPhase1L1k\Package\Windows`.

## Packaged Store and Studio evidence

The fresh Store process exited `0`. The retained `31`-part Sundale presentation, `7`-destination/`16`-part identity, Job frontage, Arena entrance, Ticket Booth frontage, Clothing Store frontage, new Furniture Store frontage, and fixed-view QA markers each appeared exactly once. The new marker was:

`ODDSWELL_SUNDALE_FURNITURE_STORE_FRONTAGE|result=PASS|parts=5|roles=4|anchor_x=-9500|anchor_y=5000|local_only=true|replicated=false|collision=false|native_assets=true|text=false|catalog_added=false|snap_points_added=false|placement=false|store_fiction=false|final_art=false`

The existing physical-Store E path then used two confirmations to move the QA ledger from one `+100` Job entry to two entries/balance `0`. The automated character entered the existing private Studio, where independent runtime markers reported the exact owned `sundale_modular_chair`, one item, three parts, `studio_primary`, gray/teal placeholder appearance, and no free placement or rotation.

A fully separate cold Studio process exited `0`, restored exactly two entries/balance `0`, retained ownership, independently rebuilt the same one-item/three-part/one-snap-point display, and removed both the Odds Bucks and Studio QA saves during cleanup.

A third process used a separate fresh user directory and exited `0`. Its READY and interior markers independently retained `structure=6,furniture=0,furniture_parts=0,decorations=0,snap_points=0`; automated entry, a `201.0 cm` walk, exit, and Sundale return passed. The three accepted packaged logs contain zero OddsWell error/result-fail, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove any accepted proof.

## Rendered evidence and objective limits

All three accepted automated PNGs are `1280x720`:

| View | Bytes | SHA-256 | Mean RGB | Mean luminance | `<0.10` | `>0.90` | Mean saturation | All-channel clipping |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Furniture Store exterior | `1,418,105` | `D5F76048B76CD4B67972C5421BF42A98A9428812F2BDA60908EA1925A57CAFC4` | `0.7196 / 0.6196 / 0.4871` | `0.6313` | `0.307%` | `8.812%` | `0.2391` | `0.000%` |
| Fresh chair Studio | `1,246,679` | `623A601E11BA26CAED83040153A98CFA129887D79A7F49F530F63F35E0048B20` | `0.6931 / 0.5982 / 0.4555` | `0.6081` | `0.212%` | `6.482%` | `0.2527` | `0.067%` |
| Cold chair Studio | `1,251,830` | `BC536F18EDD0E59EC09A605783DF4878DA85C71EBA6B460DAD6799C6D437D280` | `0.6953 / 0.5995 / 0.4577` | `0.6096` | `0.192%` | `6.621%` | `0.2518` | `0.067%` |

Pillow `12.2.0` and NumPy `2.3.5` measured the current 8-bit RGB images without calibrated photometry. The exterior frame documents the posts, header, display sill, and retained identity treatment, but strong late-afternoon shadow crosses the frontage and the placeholder character occludes its centerline. The fresh and cold Studio frames independently show the same exact three-part chair, but do not prove subpixel or perceptual equivalence. There is no same-view pre-phase baseline. The images do not prove the Store prompt, normal approach, every angle, color/text readability, comprehension, accessibility, subjective usability, final architecture/furniture/materials/lighting/brand, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The fresh packaged Store startup, fixed-view capture, purchase, Studio transition, and chair display supplied `39` quarter-second whole-process samples:

- all-run working set average/peak: `1,259.9 / 1,591.4 MiB`;
- all-run private bytes average/peak: `2,807.2 / 3,633.6 MiB`; and
- `34` samples at or above `500 MiB` working set averaged/peaked at `1,405.8 / 1,591.4 MiB` working set and `3,189.7 / 3,633.6 MiB` private bytes.

This is a short cold-start QA process with one level transition, not steady-state, representative-population, minimum-PC, final-art, or optimization evidence.

## Boundary and next gate

No catalog item, snap point, placement, rotation, storage, refund, trading, store fiction, sign, brand, final architecture, final furniture, final art, external asset, plugin, dependency, production QA shortcut, economy change, ownership change, save change, or brain/simulator change was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit.

This is new-batch phase `2/6`. After Coordinator, Notion, and independent re-fetch closure, stop for the Scope Director to choose exactly one smallest next phase.
