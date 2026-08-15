---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - phase-1l
status: accepted
date: 2026-08-15
---

# DEC-029 Candidate B Native TSR AA and Upscaler Policy

## Owner response

The affirmative owner exchange was:

`Which provisional AA/upscaler pair should Candidate B use for later automated validation?`
`A — TSR native (RECOMMENDED): AA method Temporal Super Resolution (TSR); upscaler built-in Unreal TSR temporal upscaler; no third-party plugin/dependency.`
> Yes please adopt it and continue?

## Decision

For future Candidate B `MINPC-B_BALANCED_1080P60` representative proof, the owner selected:

| Policy surface | Selected value |
| --- | --- |
| AA method | `Temporal Super Resolution` (`TSR`) |
| Upscaler | built-in Unreal `TSR` temporal upscaler |
| Third-party plugin/dependency | none; dependency count `0` |

Completion status is `COMPLETE LOCALLY — PROVISIONAL NATIVE TSR AA/UPSCALER POLICY SELECTED; VALIDATION NOT RUN`.

This is future owner policy only. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Bounded DEC-027 supersession

This decision resolves only two ordered items in [[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]]:

1. `AA method` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future Candidate B policy is `Temporal Super Resolution` (`TSR`).
2. `upscaler` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future Candidate B policy is the built-in Unreal `TSR` temporal upscaler with no third-party plugin or dependency.

Exactly four items remain unresolved, in this order:

1. `screen percentage`
2. `exact visible Medium scalability CVars`
3. `VSync`
4. `frame cap`

DEC-028 remains unchanged: future Candidate B GI/reflection policy is `Lumen` global illumination plus `Screen Space Reflections` (`SSR`), with disposition `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`. DEC-027's six compatibility terms also remain unchanged: `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

No other DEC-027 term, DEC-026 field, Candidate B field, illustrative hardware example, historical evidence status, or proof requirement changes.

## Default-reference and effective-state boundary

The installed UE5.8 engine references in [[Development/Reports/Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]] identify default `r.AntiAliasingMethod=4` as TSR and default `r.TemporalAA.Upscaler=1` as `GTemporalUpscaler`, which may be overridden by a third-party plugin. Those defaults are rationale/reference only. They do not prove project selection, an effective visible method/upscaler, a plugin inventory, performance, or Candidate B validation.

The owner selection is deliberately native: built-in Unreal TSR and third-party plugin/dependency count `0`. A later authorized representative proof must still retain the effective AA method, effective upscaler implementation, plugin/dependency custody, visible output, and performance evidence.

## OUT boundary

This decision changes no runtime, source, config, plugin, dependency, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, or machine state. It authorizes no launch, test, representative-system run, measurement, acquisition, compatibility claim, minimum-PC approval, beta or production readiness, release, Notion work, or fresh Phase `4/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, and release remain unauthorized.

The bounded closure report is [[Development/Reports/Phase 1L5i2 Candidate B Native TSR AA and Upscaler Policy Closure]].
