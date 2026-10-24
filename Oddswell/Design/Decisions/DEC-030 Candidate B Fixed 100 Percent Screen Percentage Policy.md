---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - phase-1l
status: accepted
date: 2026-08-15
---

# DEC-030 Candidate B Fixed-100-Percent Screen-Percentage Policy

## Owner response

The affirmative owner exchange was:

`Which fixed primary screen-percentage policy should Candidate B use for its first later automated 1920x1080 validation?`
`A — Fixed 100% (RECOMMENDED): render at native 1920x1080; TSR supplies AA, not resolution recovery; dynamic resolution disabled for the bounded validation. This gives the clearest, least ambiguous baseline, but is not a performance guarantee.`
> Yes please adopt and continue

## Decision

For the first later authorized Candidate B `MINPC-B_BALANCED_1080P60` automated validation, the owner selected this bounded future custody:

| Validation surface | Selected value |
| --- | --- |
| Output resolution | fixed `1920x1080` |
| Primary screen percentage | fixed `100%` |
| Internal rendering resolution | native `1920x1080` |
| TSR role | AA only; not resolution recovery |
| Dynamic resolution | disabled |

Completion status is `COMPLETE LOCALLY — PROVISIONAL FIXED-100-PERCENT SCREEN POLICY SELECTED; VALIDATION NOT RUN`.

This is future validation policy only. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Bounded DEC-027 supersession

This decision resolves only one ordered item in [[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]]:

1. `screen percentage` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future bounded Candidate B validation uses fixed `100%` primary screen percentage at native internal `1920x1080` and fixed output `1920x1080`.

Exactly three items remain unresolved, in this order:

1. `exact visible Medium scalability CVars`
2. `VSync`
3. `frame cap`

DEC-028 remains unchanged: future Candidate B GI/reflection policy is `Lumen` global illumination plus `Screen Space Reflections` (`SSR`). DEC-029 remains unchanged: future Candidate B uses TSR AA plus the built-in Unreal TSR temporal path with third-party plugin/dependency count `0`; for this fixed-100% validation TSR performs AA, not resolution recovery. DEC-027's compatibility terms remain unchanged: `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

No other DEC-027 term, DEC-026 field, Candidate B field, illustrative hardware example, historical evidence status, or proof requirement changes.

## Default-reference and effective-state boundary

The installed UE5.8 references in [[Development/Reports/Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]] identify `r.ScreenPercentage.Default=100` and make a non-positive `r.ScreenPercentage` delegate to default CVars. That `100` default is rationale/reference only. It does not prove current project selection, current effective internal resolution, visible output, dynamic-resolution state, performance, or Candidate B validation.

The retained off-screen `1280x720` route and saved `sg.ResolutionQuality=0` also remain nonproof. A later authorized representative run must explicitly set and retain fixed output `1920x1080`, primary screen percentage `100%`, internal resolution `1920x1080`, TSR's AA-only role, disabled dynamic resolution, effective CVar custody, visible output, and performance evidence.

## OUT boundary

This decision changes no runtime, source, config, plugin, dependency, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, or machine state. It authorizes no launch, test, representative-system run, measurement, acquisition, compatibility claim, minimum-PC approval, beta or production readiness, release, Notion work, or fresh Phase `5/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, and release remain unauthorized.

The bounded closure report is [[Development/Reports/Phase 1L5i3 Candidate B Fixed 100 Percent Screen Percentage Policy Closure]].
