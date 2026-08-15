---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - phase-1l
status: accepted
date: 2026-08-14
---

# DEC-027 Candidate B Compatibility-First Direct3D Policy

## Owner response

The exact prompt context was:

`To continue, may I adopt the recommended compatibility-first policy: D3D12, feature level 12_0+, Shader Model 6.6+, VSM enabled, hardware ray tracing disabled, and Nanite not required?`

> Yes please continue

## Decision

The owner selected this six-term compatibility-first policy for future candidate-B proof:

| # | Policy term | Selected value |
|---:|---|---|
| 1 | Rendering API | `D3D12` |
| 2 | Direct3D feature level | `12_0+` (`FL12_0+`) |
| 3 | Shader Model | `6.6+` (`SM6.6+`) |
| 4 | Virtual Shadow Maps | `on` (`VSM on`) |
| 5 | Hardware ray tracing | `off` (`HWRT off`) |
| 6 | Nanite | `not required` (`Nanite not required`) |

Policy-selection count is `1`. Test count is `0`; representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`.

## Bounded DEC-026 supersession

This decision supersedes only the future owner-policy placeholder in field 6 of [[Design/Decisions/DEC-026 Provisional Balanced 1080p60 Minimum PC Target]]. It resolves that future validation policy to the six terms above. It does not rewrite DEC-026's frozen historical field-6 text, its historical `OWNER_UNSET / UNVERIFIED` evidence snapshot, or fields 1-5 and 7-25.

The AMD Radeon RX 6600 remains an eligible illustrative candidate-B example, and its `8 GB` VRAM example remains unchanged. Eligibility is not selection, acquisition, testing, compatibility proof, measured performance, minimum-PC validation, or approval.

## Eight unresolved items

The following remain unresolved in this exact order:

1. `GI method/raw mapping`
2. `reflection method/raw mapping`
3. `AA method`
4. `upscaler`
5. `screen percentage`
6. `exact visible Medium scalability CVars`
7. `VSync`
8. `frame cap`

These items require a later owner policy and evidence gate. No default, absence, current-machine marker, or off-screen route is promoted into a selection.

## Evidence boundary

The read-only [[Development/Reports/Phase 1L5g Current Packaged Rendering API and Feature Evidence Inventory]] remains the evidence basis. It records current config and current-machine facts only: current D3D12/RTX 4070 Laptop/feature-level `12_2`/shader-model `6.7` markers cannot validate candidate B or its illustrative RX 6600 example. The retained `1280x720` off-screen route proves no visible Medium preset, FPS, GPU/VRAM performance, compatibility, or readiness.

This decision changes no runtime, config, source, package, map, test, route, gameplay, art, accessibility, input, brain, economy, procurement, or machine state. It authorizes no representative run, performance promise, minimum-PC approval, beta readiness, production readiness, Phase `6/6`, roadmap Phase 2, Version 1, release, or Notion work. Phase 1K remains incomplete and not waived.

The bounded closure report is [[Development/Reports/Phase 1L5g1 Candidate B Compatibility First Direct3D Policy Closure]].
