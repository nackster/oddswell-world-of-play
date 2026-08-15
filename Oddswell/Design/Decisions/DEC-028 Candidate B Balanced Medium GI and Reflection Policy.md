---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - phase-1l
status: accepted
date: 2026-08-15
---

# DEC-028 Candidate B Balanced-Medium GI and Reflection Policy

## Owner response

The exact prompt context and immediately adjacent owner response were:

`may I adopt the recommended Candidate B policy: Lumen global illumination with Screen Space Reflections?`
> Let's begin the next phase?

## Decision

For future Candidate B `MINPC-B_BALANCED_1080P60` representative proof, the owner selected:

| Policy surface | Selected value |
| --- | --- |
| Global illumination | `Lumen` |
| Reflections | `Screen Space Reflections` (`SSR`) |

This is an owner-selected policy only. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Bounded DEC-027 supersession

This decision resolves only the first two ordered policy items in [[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]]:

1. `GI method/raw mapping` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future Candidate B policy is `Lumen` global illumination.
2. `reflection method/raw mapping` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future Candidate B policy is `Screen Space Reflections` (`SSR`).

DEC-027's six compatibility terms remain unchanged: `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

Exactly six items remain unresolved, in this order:

1. `AA method`
2. `upscaler`
3. `screen percentage`
4. `exact visible Medium scalability CVars`
5. `VSync`
6. `frame cap`

No other DEC-027 term, DEC-026 field, Candidate B field, illustrative hardware example, historical evidence status, or proof requirement changes.

## Historical config and rationale boundary

The current project configuration remains the historical `Lumen` GI / `Lumen` reflection configuration mapped in [[Development/Reports/Phase 1L5h Current GI and Reflection Raw Value Decode and Six Phase Batch Closeout Audit]]. This decision does not edit, reinterpret, or claim effective visible output from that `Lumen` / `Lumen` configuration. The new future Candidate B reflection policy is `SSR`; it is not a claim that the current project already uses SSR.

The installed UE5.8 Medium/@1 reflection reference in [[Development/Reports/Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]] records `r.SSR.Quality=2`, `r.SSR.HalfResSceneColor=1`, and `r.Lumen.Reflections.Allow=0`. Those values are rationale/reference only. They are not selected effective CVars, a final visible Medium contract, measured performance, or Candidate B validation. The final exact Medium CVar set remains one of the six unresolved items.

## OUT boundary

This decision changes no runtime, source, config, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, or machine state. It authorizes no launch, test, representative-system run, measurement, acquisition, compatibility claim, minimum-PC approval, beta or production readiness, release, Notion work, or fresh Phase `3/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, and release remain unauthorized.

The bounded closure report is [[Development/Reports/Phase 1L5i1 Candidate B Balanced Medium GI and Reflection Policy Closure]].
