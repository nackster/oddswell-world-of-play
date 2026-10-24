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

# Phase 1L.1m — One-Bedroom Interior Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED OWNED-ONE-BEDROOM PRESENTATION PASS.**

The existing purchased One-bedroom now has one small ownership-gated native presentation layer inside the unchanged private Studio footprint. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L housing presentation steps 1, 2, and 5]], [[Design/Beta Game Bible#Housing and furniture|Apartment progression]], [[Design/Beta Game Bible#6. Experience the consequence|Experience consequence]], and [[Design/Decisions/DEC-020 First One Bedroom Apartment Upgrade|DEC-020]] without adding a room, layout, area, furniture item, decoration, snap point, placement control, storage, refund, trading, final material, final art, or external dependency.

## Smallest implementation

One ownership-gated part list returns no elements for a fresh Studio and exactly five native-cube elements for a valid One-bedroom owner:

- one sage bedroom-zone floor inset;
- two burnt-orange doorway-frame sides;
- one cobalt doorway-frame cap; and
- one terracotta bedroom-wall accent.

The four roles reuse the Engine cube, BasicShape material, approved planning palette, transient spawn parameters, and existing Studio presentation block. Every part is local-only, non-replicated, collision-disabled, native-only, absent on dedicated servers, and tagged as presentation rather than structure, furniture, decoration, or snap points.

One focused automation contract locks the ownership gate at fresh `0` versus owned `5`, the five exact unique IDs, four role counts, positive scales, approved palette, existing Studio bounds, retained `10`-part Studio presentation, three partition surfaces, exact `500` price, and `studio_primary` chair point. No new QA camera or input path was necessary: the existing fresh/cold One-bedroom QA already supplies the correct fixed interior view.

## Housing and Studio contracts preserved

The One-bedroom remains an in-place upgrade inside the same six-surface Studio. It costs exactly `500` Odds Bucks, requires Studio ownership, uses two E confirmations at Apartment Management, and records one immutable debit as durable ownership evidence. The existing structure remains six Studio surfaces plus three partition surfaces and one open doorway.

The prior `10` Studio presentation parts remain exact. The point light retains its actor, position, intensity, radius, and `4500 K` presentation temperature. An owned Modular Chair remains exactly three furniture parts at `studio_primary`; no chair appears without its purchase record. The four later tiers remain locked and unbuilt with no prices or layouts. A fresh Studio remains exactly `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0` and now also proves One-bedroom presentation `owned=false,parts=0,roles=0`.

Entry, exit, Sundale return, ledger, save schema/slot/index, authority, shared session, economy, wagering, inventory, brains, simulator, stores, city, and all Phase 1L.1a-l layers are unchanged.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.OneBedroomInteriorPresentation` | PASS `1/1` |
| Full native `OddsWell` | PASS `63/63` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `31.28s` |
| Package audit | PASS `50` files / `1,050,147,756` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `B55766790BAE11F11186FA38ABAFDD3F435FD26D457457AA010E519BC897CCCC`.
- UFS manifest SHA-256: `EAABA936CA775A316C93A08EF66BF37520930619D035E139CF55C93B96C34C99`.

The accepted evidence root is `C:\tmp\OddsWellPhase1L1m\Evidence`; the package root is `C:\tmp\OddsWellPhase1L1m\Package\Windows`.

## Packaged ownership, persistence, and fresh-Studio evidence

The fresh owned process exited `0`. The existing physical E path bought the exact `100`-Odds-Bucks chair and exact `500`-Odds-Bucks One-bedroom after the same two confirmations each, ending at three immutable entries/balance `0`. Inside the existing private home, runtime evidence reported:

`ODDSWELL_ONE_BEDROOM_PRESENTATION|result=PASS|owned=true|parts=5|roles=4|existing_studio_parts=10|structure_excluded=true|furniture_excluded=true|decorations_excluded=true|snap_points_added=false|local_only=true|replicated=false|collision=false|native_assets=true|layout_added=false|final_art=false`

The same process independently retained Studio presentation `10/4`, structure `9`, upgrade surfaces `3`, the open doorway, one three-part chair at `studio_primary`, zero decorations, one active snap point, and the exact purchase/ownership result.

A separate cold process exited `0`, restored exactly three entries/balance `0`, retained both ownership records, rebuilt the same `10/4` Studio presentation plus owned `5/4` One-bedroom presentation, partition/open doorway, and chair, then removed both QA saves during cleanup.

A third process used a separate fresh user directory and exited `0`. It independently reported One-bedroom presentation `owned=false,parts=0,roles=0`, retained Studio presentation `10/4`, and retained exact READY truth `structure=6,upgrade_surfaces=0,furniture=0,furniture_parts=0,decorations=0,snap_points=0`. Automated entry, a `201.2 cm` walk, exit, and Sundale return passed. The three accepted packaged logs contain zero OddsWell result-fail, fatal-error, assertion, ensure, or unhandled-exception markers. No keyboard, mouse, or manual input drove any accepted proof.

Accepted log hashes:

- Fresh owned One-bedroom: `AD1C3574B25F9DD04E7B37147815AACFE2256A769BBAE697AB8CF3A14BB09337`.
- Cold owned One-bedroom: `284EADA06BB368791B83E987D594FABCA5A4D0DE74F4D2BEEAB34941114B27C8`.
- Fresh empty Studio: `ED81B56270636A4665A4CB3AE1A8B606C5C365384D979B5CC9343A4C4D66B5A0`.

## Rendered evidence and objective limits

The accepted owned frames are `1280x720`:

| View | Bytes | SHA-256 | Mean RGB | Mean luminance | `<0.10` | `>0.90` | Mean saturation | All-channel clipping |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Fresh One-bedroom | `1,177,861` | `92F0F38E8430405EAB604FE1CEF3A231573454E43D317C9AFFC31ECD4D7B9635` | `0.6377 / 0.6097 / 0.4763` | `0.6060` | `0.188%` | `12.769%` | `0.4102` | `0.090%` |
| Cold One-bedroom | `1,162,619` | `67962FBB4888AD0EC4EACEE90675B5C67053D3FA3C27E39A3CAFD8F7EF7CDE75` | `0.6404 / 0.6097 / 0.4779` | `0.6067` | `0.148%` | `12.771%` | `0.4088` | `0.057%` |

Pillow `12.2.0` and NumPy `2.3.5` measured the current 8-bit RGB images without calibrated photometry. Visual inspection shows the new doorway frame, bedroom-zone floor inset, and wall accent within the unchanged room; the chair remains partially visible in the right foreground. Against Phase 1L.1l's prior fresh frame from the same fixed view, the current fresh frame has mean absolute RGB difference `0.0106`; `5.525%` of pixels exceed maximum-channel difference `0.05` and `2.060%` exceed `0.20`. Capture timing/noise contributes, so those differences are not attributed exclusively to the new presentation pieces. Fresh and cold frames do not prove subpixel or perceptual equivalence.

The images do not prove every angle, prompts or text readability, comprehension, accessibility, subjective usability, final layout/architecture/apartment/furniture/materials/lighting, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The fresh packaged purchases, Studio transition, and owned presentation supplied `37` quarter-second samples from the current OddsWell game process:

- all-run working set average/peak: `1,174.6 / 1,587.6 MiB`;
- all-run private bytes average/peak: `2,590.6 / 3,627.0 MiB`; and
- `31` samples at or above `500 MiB` working set averaged/peaked at `1,355.0 / 1,587.6 MiB` working set and `3,057.9 / 3,627.0 MiB` private bytes.

This is a short cold-start QA process with one level transition, not steady-state, representative-population, minimum-PC, final-art, or optimization evidence.

## Boundary and next gate

No room, layout, area, housing tier, furniture item, decoration, snap point, placement, storage, refund, trading, final material, final architecture, final apartment, final furniture, final art, external asset, plugin, dependency, production QA shortcut, economy change, ownership change, save change, or brain/simulator change was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit.

This is new-batch phase `4/6`. After Coordinator, Notion, and independent re-fetch closure, stop for the Scope Director to choose exactly one smallest next phase.
