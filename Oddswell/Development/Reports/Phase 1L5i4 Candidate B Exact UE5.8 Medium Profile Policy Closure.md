# Phase 1L.5i.4 Candidate B Exact UE5.8 Medium-Profile Policy Closure

- Date: 2026-08-15
- Branch: `agent/phase-0d`
- Baseline commit: `eb2059888a9a0ac66cfd4a571aa3eaf38d893429`
- Status: **COMPLETE LOCALLY — PROVISIONAL EXACT MEDIUM PROFILE SELECTED; VALIDATION NOT RUN**
- Batch position: fresh Phase `5/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-031 Candidate B Exact UE5.8 Medium Profile Policy]] records the exact installed UE5.8 Medium/@1 contract for the first later authorized Candidate B validation.

| Contract fact | Frozen value |
| --- | --- |
| Observable scalability selectors | `11`, each selected at level `1` |
| Present installed `@1` sections | `10` |
| Immutable installed live child assignments | `154` |
| `sg.LandscapeQuality` selector | `1` |
| `[LandscapeQuality@1]` section | absent |
| Landscape child assignments adopted | `0` |
| Landscape child CVars invented | `0` |

The ordered selectors are `sg.ViewDistanceQuality=1`, `sg.AntiAliasingQuality=1`, `sg.ShadowQuality=1`, `sg.GlobalIlluminationQuality=1`, `sg.ReflectionQuality=1`, `sg.PostProcessQuality=1`, `sg.TextureQuality=1`, `sg.EffectsQuality=1`, `sg.FoliageQuality=1`, `sg.ShadingQuality=1`, and `sg.LandscapeQuality=1`.

The exact immutable `154`-assignment child contract is recorded verbatim, with source line ranges and per-group counts, in [[Development/Reports/Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]]. Source custody is installed `C:/Program Files/Epic Games/UE_5.8/Engine/Config/BaseScalability.ini`, SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6`. A deterministic read-only recount before this decision confirmed `11` selectors, `10` present sections, `154` live assignments, and `0` Landscape child assignments.

Only one DEC-027 item is resolved:

1. `exact visible Medium scalability CVars` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`.

The remaining two stay exact and ordered:

1. `VSync`
2. `frame cap`

DEC-028 remains unchanged at future Candidate B Lumen GI plus SSR. DEC-029 remains unchanged at TSR AA plus the built-in Unreal TSR temporal path and third-party plugin/dependency count `0`. DEC-030 remains unchanged at fixed output `1920x1080`, fixed primary screen percentage `100%`, native internal `1920x1080`, TSR AA-only, and dynamic resolution disabled. DEC-027's compatibility terms remain `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; historical evidence remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Evidence and non-inference

The installed Medium/@1 source is authoritative reference custody for the selected future contract. It is not current project-selection proof, current effective-state proof, or visible output. The retained current-machine run used `@3`, not `@1`, and cannot validate this policy.

A later separately authorized representative visible Candidate B run must set all `11` selectors to `1`, retain and compare all `154` effective child values, prove zero invented Landscape children, disclose every override path, and retain visible-output and performance evidence. Selection, selector equality, and source custody grant no performance, minimum-PC, compatibility, or readiness credit.

## Documentation-only boundary

This fresh Phase `5/6` creates only DEC-031 and this closure report. It performs no runtime launch, test, source or config change, plugin or dependency change, package or map operation, product change, representative-system proof, procurement, hardware selection, performance measurement, minimum-PC validation, compatibility or readiness finding, DEC-026/027/028/029/030 rewrite, Notion work, or fresh Phase `6/6`.

The owner wording recorded in DEC-031 authorizes only the bounded Medium-profile policy presented immediately before it; it does not authorize additional phases, agents, or implementation.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen with no training, learning, retraining, or readiness claim. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, readiness, and release remain unauthorized.
