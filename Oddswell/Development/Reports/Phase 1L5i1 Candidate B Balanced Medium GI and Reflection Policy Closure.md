# Phase 1L.5i.1 Candidate B Balanced-Medium GI and Reflection Policy Closure

- Date: 2026-08-15
- Branch: `agent/phase-0d`
- Baseline commit: `1b04d82e678bc5cb761c338de012945a42e8d8da`
- Status: **COMPLETE LOCALLY — PROVISIONAL GI/REFLECTION POLICY SELECTED; VALIDATION NOT RUN**
- Batch position: fresh Phase `2/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-028 Candidate B Balanced Medium GI and Reflection Policy]] records two future Candidate B policy values:

| Policy surface | Selected value |
| --- | --- |
| Global illumination | `Lumen` |
| Reflections | `Screen Space Reflections` (`SSR`) |

This resolves only two DEC-027 items as future Candidate B owner policy:

1. `GI method/raw mapping` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`.
2. `reflection method/raw mapping` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`.

DEC-027's six compatibility terms remain `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

The remaining six unresolved items stay exact and ordered:

1. `AA method`
2. `upscaler`
3. `screen percentage`
4. `exact visible Medium scalability CVars`
5. `VSync`
6. `frame cap`

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; historical evidence remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Evidence and non-inference

The historical current project configuration remains `Lumen` GI / `Lumen` reflections. No config is changed, and no current effective visible result is inferred. The new future Candidate B reflection policy is SSR, not a claim that the current project already uses SSR.

Installed UE5.8 Medium/@1 reference values `r.SSR.Quality=2`, `r.SSR.HalfResSceneColor=1`, and `r.Lumen.Reflections.Allow=0` provide rationale only. They do not select effective CVars, complete the visible Medium contract, measure performance, or validate Candidate B. The exact visible Medium scalability CVars remain unresolved.

## Documentation-only boundary

This fresh Phase `2/6` creates only DEC-028 and this closure report. It performs no runtime launch, test, source or config change, package or map operation, product change, representative-system proof, procurement, hardware selection, performance measurement, minimum-PC validation, compatibility or readiness finding, DEC-026 rewrite, Notion work, or fresh Phase `3/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen with no training, learning, retraining, or readiness claim. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, readiness, and release remain unauthorized.
