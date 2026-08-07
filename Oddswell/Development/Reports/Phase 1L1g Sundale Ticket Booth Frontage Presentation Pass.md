---
tags:
  - development
  - phase-1l
  - unreal
  - city
  - ticket-booth
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1g — Sundale Ticket Booth Frontage Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED TICKET-BOOTH FRONTAGE PRESENTATION PASS.**

The existing physical Sportsbook/Ticket Booth now has one intentional native-primitives exterior treatment instead of relying only on its destination marker. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]], [[Design/Beta Game Bible#First-hour player journey|First-hour player journey — Find work and the sports location]], and [[Design/Beta Game Bible#Required beta locations|Physical wagering location associated with basketball]] without inventing final architecture, signage, text, brand, or markets.

## Smallest implementation

The existing local Sundale presentation builder adds exactly five native-cube parts around the canonical Sportsbook anchor at `(1000, 18000)`:

- two charcoal framing posts;
- one burnt-orange header;
- one sand counter; and
- one restrained-cobalt approach band.

The five unique IDs cover exactly four bounded roles. They reuse the approved Phase 1L.1a palette, Engine cube, BasicShape material, and existing presentation spawn helper. Every part is transient, local-only, non-replicated, collision-disabled, and absent on dedicated servers. The exact Phase 1L.1a `31`-part, Phase 1L.1b `7`-destination/`16`-part, Phase 1L.1c atmosphere, Phase 1L.1d Studio, Phase 1L.1e Job frontage, and Phase 1L.1f Arena entrance contracts remain unchanged.

One opt-in `-TicketBoothPresentationQa` branch stages three automated captures around the existing Sportsbook-offer QA: one exterior view, one exact prompt view, and the existing canonical menu-open view. It adds no production camera, interaction path, market, mutation, framework, or manual input.

One focused automation contract locks the five exact unique IDs, role counts, positive scales, approved palette, bounded distance and height around the existing anchor, route waypoint, `350 cm` radius, exact prompt, four existing market-page labels, one published page, three locked pages, and Arena separation.

## Ticket Booth and wagering contract preserved

The anchor remains exactly `(1000, 18000)`, the radius remains `350 cm`, and the prompt remains exactly `Press E to open betting odds`. The existing E interaction still opens and closes the same read-only Game Lines preview. Page navigation, labels, locked states, canonical teams, probabilities, decimal odds, stake limits, possible returns, tipoff lock, wager placement, receipts, settlement, ledgers, schedule, server authority, equal-information boundary, saves, brains, and simulator are unchanged.

The Arena threshold/transition/interior/replay, Job, stores, housing, shared session, and all earlier presentation layers are unchanged. No authored map transform, market, offer, wager, receipt, settlement, ledger, balance, save, authority, route, collision, inventory, or gameplay behavior changed.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleTicketBoothFrontage` | PASS `1/1` |
| Full native `OddsWell` | PASS `57/57` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `31.83s` |
| Package audit | PASS `50` files / `1,049,908,140` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `798D3B5FDA8B52A5FB42A6D8372598A508F92B6B609694BE42DAEF995EE1E337`.
- UFS manifest SHA-256: `DCEF5BD373068DAA975422FBB4896EEA9A866982E4F0E5F93CC89761A637A98F`.

## Packaged Ticket Booth evidence

The accepted fresh-profile packaged run exited with code `0`. The retained Phase 1L presentation markers appeared exactly once, including:

`ODDSWELL_SUNDALE_TICKET_BOOTH_FRONTAGE|result=PASS|parts=5|roles=4|anchor_x=1000|anchor_y=18000|local_only=true|replicated=false|collision=false|native_assets=true|text=false|markets_added=false|architecture_final=false|final_art=false`

The opt-in presentation QA independently retained the exact anchor, radius, prompt, existing E path, visible Game Lines page, four labels, one published page, three locked pages, outside rejection, and no ledger mutation. The unchanged canonical-offer QA retained Harbor City Waves versus Mesa Vista Sol, probabilities `57586693/42413307` e8, decimal odds `17365/23577` e4, stakes `10–100` in increments of `10`, possible returns `10:17,23` and `100:173,235`, server-tipoff lock, zero starting/ending balance, zero ledger entries, and all submission/selection/confirmation/request/debit/mutation flags false. The canonical offer marker appeared twice—initial load and menu open—not as two offers or mutations.

The accepted log contains zero OddsWell failure, fatal-error, assertion, ensure, or unhandled-exception markers. No player, keyboard, mouse, or manual input drove this proof.

## Rendered evidence and objective limits

The accepted process launched at requested `1280x800`; Unreal saved each PNG at `888x500`.

| Automated capture | Bytes | SHA-256 | Mean luma | Dark `<0.10` | Bright `>0.90` | Mean saturation |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Exterior frontage | `653,855` | `B83A54A770E5D80F6BCFE42DE3B5E9532EFEFA1A937497CAD1BD1FD579FFE0B2` | `0.6172` | `0.320%` | `3.846%` | `0.4083` |
| Exact prompt | `286,995` | `F71DEC1682D226B85C28918BD620B2069383AF1DC115C62A397BE42699A6FFD2` | `0.2829` | `59.449%` | `3.807%` | `0.4770` |
| Existing menu open | `170,005` | `62BDA333783E94A1D9A03B5D1FF0B2DD43B551F135FA5CC2CF00FFB7AE9A9359` | `0.4344` | `0.000%` | `14.023%` | `0.3322` |

Pillow `12.2.0` and NumPy `2.3.5` measured 8-bit RGB current images without calibrated photometry. The exterior image documents the bounded frontage from one fixed view, but the placeholder player stack occludes part of its centerline. The prompt image proves the exact on-screen prompt but is a close, dark wall/sky view. The menu image proves the menu is open, Game Lines is selected, four tabs exist, and the canonical offer is shown; its lower bet-slip text still overlaps/clips at this captured size. An earlier requested `1280x720` diagnostic was rejected because that overlap was more severe.

There is no same-view pre-phase baseline. These images do not prove a normal player approach, every exterior angle, color/text/prompt/menu readability, unclipped responsive UI, player understanding, accessibility, subjective usability, final architecture, final materials, final lighting, final brand, minimum-PC behavior, or beta readiness.

## Performance evidence and limits

The accepted packaged frontage/prompt/menu sequence supplied `26` quarter-second whole-process samples:

- all-run working set average/peak: `1,208.6 / 1,557.1 MiB`;
- all-run private bytes average/peak: `2,566.1 / 3,388.4 MiB`; and
- `23` post-initialization samples at or above `500 MiB` working set averaged/peaked at `1,328.3 / 1,557.1 MiB` working set and `2,875.7 / 3,388.4 MiB` private bytes.

This short sample includes cold startup and automated fixed-view staging. It is not a steady-state, representative-population, minimum-PC, final-art, or optimization promise.

## Boundary and next gate

No external asset, plugin, dependency, new market, wager, settlement, final architecture, signage, text, brand, new location, district, post-process framework, weather/time-of-day system, music, final material, final lighting, accessibility baseline, owner/manual test, or release-readiness claim was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize wagering expansion, Ticket Booth UI redesign, or release-readiness claims.
