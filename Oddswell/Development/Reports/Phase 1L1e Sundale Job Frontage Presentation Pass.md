---
tags:
  - development
  - phase-1l
  - unreal
  - city
  - job
status: complete-bounded-pass
date: 2026-08-07
---

# Phase 1L.1e — Sundale Job Frontage Presentation Pass

## Outcome

**COMPLETE FOR ONE BOUNDED JOB-FRONTAGE PRESENTATION PASS.**

The existing Sundale Job destination now has one intentional native-primitives frontage treatment instead of relying only on its waypoint and prior destination marker. This advances [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]] and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey — Find work and the sports location]] without inventing final Job fiction, signage, text, or brand.

## Smallest implementation

The existing local Sundale presentation builder adds exactly five native-cube parts around the canonical Job anchor at `(9500, 0)`:

- two charcoal frontage piers;
- one burnt-orange header;
- one sand landing; and
- one restrained-cobalt approach cue.

The five unique IDs cover exactly four bounded roles. They reuse the approved Phase 1L.1a palette, Engine cube, BasicShape material, and existing presentation spawn helper. Every part is transient, local-only, non-replicated, collision-disabled, and absent on dedicated servers. The exact Phase 1L.1a `31`-part, Phase 1L.1b `7`-destination/`16`-part, Phase 1L.1c atmosphere, and Phase 1L.1d Studio contracts remain unchanged.

One opt-in `-JobPresentationQa` hook stages the existing character at one fixed frontage view, clears prior QA-only screen messages, requests a screenshot, and then lets the existing automated Job QA continue. It creates no camera, framework, production interaction, or manual-input path.

One focused automation contract locks the five exact unique IDs, role counts, positive scales, approved palette, bounded distance and height around the existing Job anchor, and unchanged canonical Job coordinate, `350 cm` radius, `100` Odds Bucks payout, and `86,400`-second rolling interval.

## Job and gameplay contract preserved

The existing interaction remains `Press E to complete a shift (100 Odds Bucks once every 24 hours)` at the exact authored Job location. Server authority, outside-radius rejection, `100` Odds Bucks first payout, local ledger append, immediate retry cooldown, rolling `24`-hour interval, SaveGame/schema/slot/user index, and player-visible feedback are unchanged.

No authored map transform, gameplay coordinate, collision, prompt, interaction radius, route, shared session, replication, authority, ledger, economy, wager, inventory, brain, simulator, store, housing, interior, purchase, catalog, or save behavior changed.

## Automated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused native `OddsWell.Character.SundaleJobFrontage` | PASS `1/1` |
| Full native `OddsWell` | PASS `55/55` |
| Repository-pinned Python `3.12.13` frozen suites | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS |
| Windows Development game build | PASS |
| Explicit `Bootstrap + SundaleGraybox` BuildCookRun | PASS in `28.50s` |
| Package audit | PASS `50` files / `1,049,831,340` bytes / `0` Python files |

Package hashes:

- Wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`.
- Game SHA-256: `8A0209F38E0BBAD1575A29A7F5C0D9A28637B7FF409D9744741BAC2816EFBDCC`.
- UFS manifest SHA-256: `30833CF6AD26FBDCD571918291E5DBFA7D3217DA57A94924B4D38CF49762BC31`.

## Packaged Job evidence

The final direct packaged run exited with code `0` and emitted the new marker exactly once:

`ODDSWELL_SUNDALE_JOB_FRONTAGE|result=PASS|parts=5|roles=4|anchor_x=9500|anchor_y=0|local_only=true|replicated=false|collision=false|native_assets=true|text=false|job_fiction=false|final_art=false`

The retained Phase 1L.1a `31`-part, Phase 1L.1b `7`-destination/`16`-part, and Phase 1L.1c atmosphere markers also appeared exactly once. The unchanged Job QA first rejected an outside request with zero award, then completed the existing exact-location shift with `odds_bucks_awarded=100`, `ledger_entries=1`, and `ledger_balance=100`. Its immediate retry awarded zero and reported the full nominal `retry_after_seconds=86400`. The final QA marker reported outside rejection, first credit, ledger persistence, and immediate retry block as PASS. The accepted log contains zero OddsWell failure, fatal-error, assertion, or ensure markers. No player, keyboard, mouse, or manual input drove this proof.

## Rendered evidence and objective limits

The accepted automated packaged fixed view is `1280x720`, `1,381,563` bytes, with SHA-256 `20E763C1607023A415E7513EB456E43D15B847878A219C4AA46E916E290C5B31`. It documents the bounded native frontage composition from one centered approach view.

Pillow `12.2.0` measured the 8-bit RGB image without calibrated photometry: mean luminance `152.397`; P01/P50/P99 luminance `41.617 / 150.634 / 239.787`; pixels below luminance `16` at `0.000%`; pixels above luminance `239` at `1.401%`; pixels with all channels at or above `253` at `0.000%`; mean saturation `0.1823`; and mean `R-B` `10.342`.

Two preliminary diagnostic captures were rejected and are not accepted evidence: one faced the wrong side/retained stale QA feedback, and one was too close to frame the bounded frontage. The accepted image is still only one staged automated view. It has no same-view pre-phase baseline and does not prove the Job prompt, normal player approach, every angle, color or text readability, player understanding, accessibility, subjective usability, final material, final lighting, final brand, or beta readiness.

## Performance evidence and limits

The short packaged Job journey supplied `23` quarter-second whole-process samples:

- all-run working set average/peak: `1,155.4 / 1,546.6 MiB`;
- all-run private bytes average/peak: `2,504.3 / 3,583.1 MiB`; and
- `19` post-initialization samples above `500 MiB` working set averaged/peaked at `1,327.7 / 1,546.6 MiB` working set and `2,976.7 / 3,583.1 MiB` private bytes.

This includes cold startup and lasts only the bounded Job QA. It is not a steady-state, representative-population, minimum-PC, final-art, or optimization promise.

## Boundary and next gate

No external asset, plugin, dependency, final Job fiction, commercial text, signage, brand, purchase, catalog, new location, district, post-process framework, time-of-day/weather system, music, final material, final lighting, accessibility baseline, owner/manual test, or release-readiness claim was added. Cost was `$0.00`; no push was performed.

Phase 1K remains incomplete. The owner has deferred hands-on held-control and route usability validation until the MVP playtest. That evidence is not waived and remains required before beta exit. The Scope Director should select only the next smallest first-hour presentation slice; this phase does not authorize broader Job systems or release-readiness claims.
