---
tags:
  - development
  - phase-1l
  - unreal
  - housing
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1l — Sundale Apartment Management Kiosk Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED APARTMENT-MANAGEMENT PRESENTATION PASS.**

The physical One-bedroom upgrade point now has one small native-primitives presentation frame around the existing functional Apartment Management kiosk beside the Studio. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L presentation steps 1, 2, and 5]], [[Design/Beta Game Bible#First-hour player journey|Discover the starter home]], [[Design/Beta Game Bible#6. Experience the consequence|Experience consequence]], [[Design/Beta Game Bible#Housing and furniture|Apartment progression]], and [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade|DEC-020]] without adding a housing tier, layout, snap point, decorating control, storage, refund, trading, final kiosk fiction, sign, brand, final art, or external dependency.

## Smallest implementation

The existing Sundale presentation builder adds exactly five native-cube parts across four bounded roles:

- two charcoal framing posts;
- one sage header;
- one warm-limestone threshold; and
- one burnt-orange approach band.

The parts reuse the existing Engine cube, BasicShape material, approved planning palette, and transient spawn helper. Every part is local-only, non-replicated, collision-disabled, and absent on dedicated servers. The separate two-part functional kiosk remains unchanged and is not counted as presentation. No authored map asset or production interaction actor changed.

One opt-in `-ApartmentManagementPresentationQa` branch is contained inside the existing One-bedroom upgrade QA. Before the unchanged chair and apartment purchase sequence, it places the automated character at one fixed south-side exterior view, faces the kiosk, clears QA screen messages, requests one screenshot, and returns to the existing QA stages on the next tick. It adds no production input, camera, housing, persistence, or framework.

One focused automation contract locks the five exact unique IDs, four role counts, positive scales, approved palette, bounded placement, exact `(0, 800)` anchor, exact `350 cm` radius, unchanged two-part functional kiosk, exact `one_bedroom` id, exact `500` price, three partition surfaces, and retained `studio_primary` chair point.

## Kiosk, apartment, and Studio contracts preserved

Apartment Management remains at `(0, 800)` with the same `350 cm` interaction radius and E-driven review/confirm/purchase path. The One-bedroom remains the only purchasable upgrade, costs exactly `500` Odds Bucks, requires Studio ownership, and records one immutable debit as durable ownership evidence after two confirmations.

The existing Studio still upgrades in place with exactly three partition surfaces and one open doorway. An owned three-part Sundale Modular Chair remains at `studio_primary`. The four later tiers remain locked and unbuilt with no prices or layouts. A fresh Studio remains exactly `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0`.

The ledger, save schema/slot/index, authority, shared session, economy, wagering, inventory, brains, simulator, stores, city, and all Phase 1L.1a-k layers are unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleApartmentManagementPresentation` | PASS `1/1` |
| Full native `OddsWell` | PASS `62/62` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `27.14s` |
| Package audit | PASS `50` files / `1,050,113,452` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `A6B67E25699764E27C16C681626A28E611B4381AB65903A5C0A8BB8E3D71022B`.
- UFS manifest SHA-256: `979EDB72FC62D72A1E5E36366077269087B6A7657F88F0B76B97D1089A7A6CCE`.

The accepted evidence root is `C:\tmp\OddsWellPhase1L1l\Evidence`; the package root is `C:\tmp\OddsWellPhase1L1l\Package\Windows`.

## Packaged purchase, persistence, and empty-home evidence

The accepted fresh process exited `0`. The retained `31`-part Sundale presentation, `7`-destination/`16`-part identity, Job, Arena, Ticket Booth, Clothing Store, and Furniture Store treatments, existing two-part functional Apartment Management kiosk, new five-part treatment, and fixed-view QA markers passed. The new marker was:

`ODDSWELL_SUNDALE_APARTMENT_MANAGEMENT_PRESENTATION|result=PASS|parts=5|roles=4|anchor_x=0|anchor_y=800|local_only=true|replicated=false|collision=false|native_assets=true|text=false|tiers_added=false|layouts_added=false|snap_points_added=false|final_art=false`

The unchanged physical E path then used two confirmations to buy the exact `100`-Odds-Bucks Modular Chair and two more confirmations to buy the exact `500`-Odds-Bucks One-bedroom. The QA ledger moved from one `+600` setup entry to three entries/balance `0`. Inside the existing private home, independent markers reported six tiers with only Studio and One-bedroom built, four later tiers locked, exact three-surface partition/open doorway, one three-part chair at `studio_primary`, and READY truth `structure=9,upgrade_surfaces=3,furniture=1,furniture_parts=3,decorations=0,snap_points=1`.

A separate cold process exited `0`, restored exactly three entries/balance `0`, retained both ownership records, rebuilt the same partition/open doorway and three-part chair, and removed both Odds Bucks and Studio QA saves during cleanup.

A third process used a separate fresh user directory and exited `0`. Its READY marker independently retained `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0`; automated entry, a `201.3 cm` walk, exit, and Sundale return passed. The three accepted packaged logs contain zero OddsWell result-fail, fatal-error, assertion, ensure, or unhandled-exception markers. No keyboard, mouse, or manual input drove any accepted proof.

Accepted log hashes:

- Fresh purchase/interior: `C6D6F85A1F0834DA64FF78A422289049230FD11FC1B3A3E1BD580F3B358697E1`.
- Cold restore/interior: `2CC974B8C35EA1CA03158EECC9DD277C76AE4A68611DEAE7FA8E9004E3C03686`.
- Fresh empty Studio: `7ADB0D614A0EBC3C42E819125CEBC19002BBC36FEC56CC35E1B9DCFB3FB46EF5`.

## Rendered evidence and objective limits

All three accepted automated PNGs are `1280x720`:

| View | Bytes | SHA-256 | Mean RGB | Mean luminance | `<0.10` | `>0.90` | Mean saturation | All-channel clipping |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Apartment Management exterior | `1,062,175` | `20FC3099C74B4BED991579D89573AB58A615808597708071D22DB8DEFD2CE2BB` | `0.3534 / 0.3459 / 0.3405` | `0.3471` | `12.524%` | `10.897%` | `0.3300` | `0.000%` |
| Fresh One-bedroom | `1,174,665` | `AB3E53DD79DDF5E4D8EB7C0726DBE5B49E23C91BB6291E34389C9E9BBBD4E557` | `0.6357 / 0.6130 / 0.4839` | `0.6085` | `0.187%` | `13.031%` | `0.4004` | `0.090%` |
| Cold One-bedroom | `1,164,340` | `D8CB900096BDDDD23EC05EAA9B24FE875973A55EEAD61ACB787F1995C5398ECB` | `0.6384 / 0.6130 / 0.4855` | `0.6092` | `0.148%` | `13.032%` | `0.3988` | `0.057%` |

Pillow `12.2.0` and NumPy `2.3.5` measured the current 8-bit RGB images without calibrated photometry. The exterior frame documents the posts, header, threshold, and approach, but nearby overhead geometry occupies and darkens much of the upper frame while the distant horizon is bright. The fresh and cold interior frames independently show the same open doorway/partition composition and retained chair, but do not prove subpixel or perceptual equivalence. There is no same-view pre-phase baseline. The images do not prove the kiosk prompt, normal approach, every angle, color/text readability, comprehension, accessibility, subjective usability, final architecture/apartment/furniture/materials/lighting/brand, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The accepted fresh packaged kiosk capture, chair purchase, One-bedroom purchase, Studio transition, and interior supplied `36` quarter-second samples from the current OddsWell game process:

- all-run working set average/peak: `1,191.0 / 1,550.9 MiB`;
- all-run private bytes average/peak: `2,668.9 / 3,679.5 MiB`; and
- `31` samples at or above `500 MiB` working set averaged/peaked at `1,343.7 / 1,550.9 MiB` working set and `3,076.1 / 3,679.5 MiB` private bytes.

One preliminary sampler measured only the small wrapper process and was rejected. The accepted rerun sampled the largest current OddsWell process and repeated the exact automated evidence without a code or configuration change. This is a short cold-start QA process with one level transition, not steady-state, representative-population, minimum-PC, final-art, or optimization evidence.

## Boundary and next gate

No housing tier, layout, snap point, decorating control, storage, refund, trading, kiosk fiction, sign, brand, final architecture, final apartment, final furniture, final art, external asset, plugin, dependency, production QA shortcut, economy change, ownership change, save change, or brain/simulator change was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit.

This is new-batch phase `3/6`. After Coordinator, Notion, and independent re-fetch closure, stop for the Scope Director to choose exactly one smallest next phase.
