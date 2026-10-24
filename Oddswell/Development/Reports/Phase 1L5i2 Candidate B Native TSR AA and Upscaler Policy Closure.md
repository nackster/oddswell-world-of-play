# Phase 1L.5i.2 Candidate B Native TSR AA and Upscaler Policy Closure

- Date: 2026-08-15
- Branch: `agent/phase-0d`
- Baseline commit: `b35c4c55716e418f9dbc03f36349c3f23f9f7586`
- Status: **COMPLETE LOCALLY — PROVISIONAL NATIVE TSR AA/UPSCALER POLICY SELECTED; VALIDATION NOT RUN**
- Batch position: fresh Phase `3/6`, committed at `757b82ff77e82b3cfb023e3c42a2fd17b6476099` with verified exactly two Notion upserts
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-029 Candidate B Native TSR AA and Upscaler Policy]] records this future Candidate B policy:

| Policy surface | Selected value |
| --- | --- |
| AA method | `Temporal Super Resolution` (`TSR`) |
| Upscaler | built-in Unreal `TSR` temporal upscaler |
| Third-party plugin/dependency | none; dependency count `0` |

Only two DEC-027 items are resolved:

1. `AA method` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`.
2. `upscaler` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`.

The remaining four stay exact and ordered:

1. `screen percentage`
2. `exact visible Medium scalability CVars`
3. `VSync`
4. `frame cap`

DEC-028 remains unchanged at future Candidate B `Lumen` global illumination plus `Screen Space Reflections` (`SSR`). DEC-027's compatibility terms remain `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; historical evidence remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Evidence and non-inference

Installed UE5.8 defaults identify AA raw `4` as TSR and `r.TemporalAA.Upscaler=1` as the default temporal-upscaler selector that may be overridden by a third-party plugin. These are rationale/reference only. They do not prove project selection, effective visible AA/upscaling, plugin custody, performance, or Candidate B validation.

The future policy uses built-in Unreal TSR with third-party plugin/dependency count `0`. A later authorized representative proof must retain effective method/upscaler, dependency custody, visible output, and performance evidence.

## Documentation-only boundary

This fresh Phase `3/6` creates only DEC-029 and this closure report. It performs no runtime launch, test, source or config change, plugin or dependency change, package or map operation, product change, representative-system proof, procurement, hardware selection, performance measurement, minimum-PC validation, compatibility or readiness finding, DEC-026/027/028 rewrite, Notion work, or fresh Phase `4/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen with no training, learning, retraining, or readiness claim. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, readiness, and release remain unauthorized.
