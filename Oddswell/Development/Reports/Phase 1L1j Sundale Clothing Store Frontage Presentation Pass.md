---
tags:
  - development
  - phase-1l
  - unreal
  - clothing-store
  - presentation
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1j — Sundale Clothing Store Frontage Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED CLOTHING-STORE FRONTAGE PRESENTATION PASS.**

The first visible clothing-upgrade destination now has one small native-primitives storefront frame around the existing physical Store. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L presentation steps 1, 2, and 5]], [[Design/Beta Game Bible#Beta win condition|Beta win condition — buy or save toward a visible upgrade]], [[Design/Beta Game Bible#World and city scope|Required beta location — Basic clothing store]], [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]], and [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture|DEC-009]] without adding a catalog item, changing room, final Store fiction, sign, brand, final art, or external dependency.

## Smallest implementation

The existing Sundale presentation builder adds exactly five native-cube parts across four bounded roles:

- two charcoal framing posts;
- one burnt-orange header;
- one warm-limestone display sill; and
- one restrained-cobalt approach band.

The parts reuse the existing Engine cube, BasicShape material, approved planning palette, and transient spawn helper. Every part is local-only, non-replicated, collision-disabled, and absent on dedicated servers. No authored map asset or production interaction actor changed.

One opt-in `-ClothingStorePresentationQa` branch is contained inside the existing Signal Jacket purchase QA. Before the unchanged purchase sequence, it places the automated character at one fixed west-side exterior view, faces the Store, clears QA screen messages, requests one screenshot, and returns to the existing QA stages on the next tick. It adds no production input, camera, interaction, persistence, or framework.

One focused automation contract locks the five exact unique IDs, four role counts, positive scales, approved palette, bounded placement, canonical route waypoint, exact `350 cm` radius, exact `sundale_signal_jacket` item id, `60` price, and distinct slate/teal appearance colors.

## Store and Signal Jacket contract preserved

The Clothing Store remains at `(12500, 9000)` with the same `350 cm` interaction radius and E-driven review/confirm/purchase/equip path. The only item remains the Sundale-origin Sundale Signal Jacket at exactly `60` Odds Bucks. Purchase still requires two confirmations, records one immutable debit, establishes ownership, and does not auto-equip. Equip remains a later explicit Store action, adds no ledger entry or second debit, uses the outfit slot, and publishes the same slate/teal shared-city appearance.

The ledger, save schema/slot/index, authority, shared session, economy, wagering, inventory, brains, simulator, Job, Ticket Booth, Arena, other Store, housing, city, and all Phase 1L.1a-i layers are unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleClothingStoreFrontage` | PASS `1/1` |
| Full native `OddsWell` | PASS `60/60` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `26.10s` |
| Package audit | PASS `50` files / `1,050,046,892` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `7509F86985B2C21ABAE52412A351DBB4DD1E7006B0E608B58D66B7ED1425EA4C`.
- UFS manifest SHA-256: `DCA6044CCCD5E07C1D31F03B3352D7F4F7EDD5A9ECF7AB2971AA8EB48079B996`.

The accepted evidence root is `C:\tmp\OddsWellPhase1L1j\Evidence`; the package root is `C:\tmp\OddsWellPhase1L1j\Package\Windows`.

## Packaged Store evidence

The fresh Store process exited `0`. The retained `31`-part Sundale presentation, `7`-destination/`16`-part identity, Job frontage, Arena entrance, Ticket Booth frontage, new Clothing Store frontage, and fixed-view QA markers each appeared exactly once. The new marker was:

`ODDSWELL_SUNDALE_CLOTHING_STORE_FRONTAGE|result=PASS|parts=5|roles=4|anchor_x=12500|anchor_y=9000|local_only=true|replicated=false|collision=false|native_assets=true|text=false|catalog_added=false|changing_room=false|store_fiction=false|final_art=false`

The existing physical-Store E path then used two confirmations to move the QA ledger from one `+100` Job entry to two entries/balance `40`. The purchase marker reported ownership true, duplicate debit false, and auto-equip false.

A fully separate cold process exited `0`, restored exactly two entries/balance `40`, exercised the unchanged two-confirm path against the owned item, retained the same two entries/balance, reported `duplicate_debit=false`, and removed the QA save during cleanup.

A separate packaged listen-server/client pair both exited `0`. The server seeded the existing owned-jacket state at two entries/balance `40`; the owner explicitly equipped it at the physical Store with no further debit. The observer client received `equipped=true`, `slot=outfit`, `slate_teal_graybox=true`, and `other_client_visible=true`. The server cleanup removed its QA save. The four accepted packaged logs contain zero OddsWell error/result-fail, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove any accepted proof.

## Rendered evidence and objective limits

The accepted automated PNG is `1280x720`, `1,393,632` bytes, with SHA-256 `71D5D654C6744DA7A697E1C935F8E858BBD7FC78CB38B683792668ADA0CBD582`. Pillow `12.2.0` and NumPy `2.3.5` measured the current 8-bit RGB image without calibrated photometry:

- mean RGB: `0.6125 / 0.6117 / 0.6156`;
- mean luminance: `0.6122`;
- pixels below luminance `0.10`: `0.000%`;
- pixels above luminance `0.90`: `10.767%`;
- mean saturation: `0.0798`; and
- all-channel clipping: `0.002%`.

The frame documents the two posts, header, display sill, approach band, and retained identity pieces. The placeholder character occludes the storefront centerline. There is no same-view pre-phase baseline, and the bright-pixel share is not a calibrated lighting or global highlight-safety study. This one frame does not prove the interaction prompt, normal approach, every angle, color or text readability, player comprehension, accessibility, subjective usability, final architecture/materials/lighting/brand, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The fresh packaged Store startup, fixed-view capture, and two-confirm purchase supplied `20` quarter-second whole-process samples:

- all-run working set average/peak: `1,032.3 / 1,604.4 MiB`;
- all-run private bytes average/peak: `2,159.0 / 3,642.4 MiB`; and
- `15` samples at or above `500 MiB` working set averaged/peaked at `1,290.5 / 1,604.4 MiB` working set and `2,823.7 / 3,642.4 MiB` private bytes.

This is a short cold-start QA process, not steady-state, representative-population, minimum-PC, final-art, or optimization evidence.

## Boundary and next gate

No catalog item, changing room, store fiction, sign, brand, final architecture, final art, external asset, plugin, dependency, production QA shortcut, economy change, ownership change, save change, or brain/simulator change was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit.

This is new-batch phase `1/6`. After Coordinator, Notion, and independent re-fetch closure, stop for the Scope Director to choose exactly one smallest next phase.
