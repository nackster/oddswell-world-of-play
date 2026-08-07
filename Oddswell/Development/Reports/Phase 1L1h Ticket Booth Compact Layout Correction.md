---
tags:
  - development
  - phase-1l
  - unreal
  - ui
  - ticket-booth
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1h — Ticket Booth Compact Layout Correction

## Outcome

**COMPLETE FOR ONE BOUNDED FIXED-VIEW COMPACT-LAYOUT CORRECTION.**

Phase 1L.1g measured lower bet-slip text overlap and clipping in the actual `888x500` packaged PNG produced by the requested `1280x800` run. The same fixed packaged view now separates the existing Ticket Booth content into bounded non-overlapping bands. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 4 and 5]], [[Design/Beta Game Bible#Beta wager markets|Beta wager markets — Current interface direction]], and the first wager flow without adding a widget framework, dependency, market, or behavior.

## Smallest implementation

The existing native `AHUD` draw path now selects one compact geometry branch only when the live Canvas is at or below `900` pixels wide or `540` pixels high. The measured `888x500` path uses:

- `16 px` outer margin;
- `72 px` header and `48 px` market tabs;
- content start `148` and content height `320`;
- a `290 px` bet-slip panel; and
- fixed separated bands for market cards, instructions, validation footer, selection, stake, potential return, balance, confirmation, and status.

The branch reuses the existing `DrawRect`, `DrawText`, and `AddHitBox` path. It moves the two existing team/confirm input hints into unused lower market-panel space and compresses the same bet-slip and accepted-receipt wording. Standard `1280x720` Canvas dimensions retain the pre-existing full layout. No new UI class, widget tree, scaling framework, font, asset, plugin, or dependency was added.

One focused automation contract computes the exact `888x500` geometry and locks positive panels, horizontal containment, ordered vertical bands, confirmation containment, the unchanged `350 cm` interaction radius, exact prompt, and four market pages.

## Wager and interaction contract preserved

The prompt remains exactly `Press E to open betting odds`; the radius remains `350 cm`. Open/close behavior, modal/input mode, mouse/controller/keyboard navigation, four tab labels, Game Lines active state, three locked pages, teams, probabilities, odds, stake range/increment, gross returns, current balance, confirmation wording, receipts, data precedence, wager command, settlement, ledger, schedule, tipoff lock, server authority, equal-information boundary, saves, brains, and simulator are unchanged.

The Phase 1L.1a-g city, atmosphere, Studio, Job, Arena, and Ticket Booth exterior layers are unchanged. No authored map, gameplay coordinate, collision, route, shared session, save, ledger, balance, wager, receipt, settlement, inventory, brain, simulator, store, housing, or presentation primitive changed.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.TicketBoothCompactLayout` | PASS `1/1` |
| Full native `OddsWell` | PASS `58/58` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `25.96s` |
| Package audit | PASS `50` files / `1,049,936,300` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `4D39AB47A277CFF93D4457658050AB6CFA000EB52710962BDAEFF66FCE6D15DA`.
- UFS manifest SHA-256: `CE49282DA45DED0F94FFBCF8F3E0CA0D4E92072B871FD60252B4BCBA82CDBB97`.

## Packaged fixed-view evidence

The fresh-profile packaged run exited with code `0`. The compact marker reported:

`ODDSWELL_TICKET_BOOTH_COMPACT_LAYOUT|result=PASS|canvas=888x500|content_y=148|content_height=320|card_bottom=314|help_y=326|return_y=348|team_input_y=376|confirm_input_y=394|footer_y=440|stake_bottom=353|gross_y=360|confirm_bottom=460|layout_bounds_clipped=false|layout_bounds_overlap=false|native_hud=true|behavior_changed=false|final_ui=false`

The retained Phase 1L presentation markers appeared exactly once. The canonical Ticket Booth marker appeared twice—initial load and menu open—without duplicate offer creation or mutation. The existing presentation QA retained the exact anchor, radius, prompt, Game Lines page, four pages, one published page, three locked pages, outside rejection, and no ledger mutation. The existing canonical-offer QA retained Harbor City Waves versus Mesa Vista Sol, probabilities `57586693/42413307` e8, decimal odds `17365/23577` e4, stakes `10–100` in increments of `10`, possible returns `10:17,23` and `100:173,235`, zero ledger entries/balance before and after, and all submission/selection/confirmation/request/debit/mutation flags false.

The accepted log contains zero OddsWell failure, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove this proof.

## Before/after visual evidence and limits

Both menu PNGs are actual `888x500` captures from the same fixed automated view and the same no-selection state:

| Capture | Bytes | SHA-256 | Mean luma | Bright `>0.90` | Mean saturation |
| --- | ---: | --- | ---: | ---: | ---: |
| Phase 1L.1g before | `170,005` | `62BDA333783E94A1D9A03B5D1FF0B2DD43B551F135FA5CC2CF00FFB7AE9A9359` | `0.4344` | `14.023%` | `0.3322` |
| Phase 1L.1h after | `128,424` | `7D6337638DB9B3DBC22170E6952ACB9968C236DC1D40E00C48ED8339FCF2BA0B` | `0.4582` | `17.893%` | `0.3025` |

Pillow `12.2.0` and NumPy `2.3.5` measured the 8-bit RGB images without calibrated photometry. Direct visual inspection plus the emitted layout bounds show no measured overlap or clipping in the accepted Phase 1L.1h fixed frame. The same tabs, team cards, exact odds, no-selection status, stake `10`, potential-return placeholder, balance `0`, unavailable-confirmation wording, lock/wager status, and input hints remain present.

This is not a text-readability, comprehension, accessibility, subjective-usability, general responsive-design, every-state, every-resolution, every-language, accepted-receipt visual, final-UI, minimum-PC, or beta-readiness proof. The before/after luminance and saturation values describe whole images, not UI quality or contrast compliance.

## Performance evidence and limits

The accepted packaged prompt/menu sequence supplied `28` quarter-second whole-process samples:

- all-run working set average/peak: `1,152.7 / 1,558.5 MiB`;
- all-run private bytes average/peak: `2,365.1 / 3,363.6 MiB`; and
- `23` post-initialization samples at or above `500 MiB` working set averaged/peaked at `1,343.7 / 1,558.5 MiB` working set and `2,841.1 / 3,363.6 MiB` private bytes.

This short sample includes cold startup and automated view staging. It is not a steady-state, representative-population, minimum-PC, final-UI, or optimization promise.

## Boundary and next gate

No external asset, widget framework, plugin, dependency, market, odds, wager behavior, receipt behavior, final UI, general responsive system, accessibility baseline, owner/manual test, or release-readiness claim was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest measured first-hour presentation slice; this phase does not authorize Ticket Booth feature expansion or release-readiness claims.
