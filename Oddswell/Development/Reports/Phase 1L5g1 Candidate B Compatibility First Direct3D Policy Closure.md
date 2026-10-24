# Phase 1L.5g.1 Candidate B Compatibility-First Direct3D Policy Closure

- Date: 2026-08-14
- Branch: `agent/phase-0d`
- Baseline commit: `ca32072e92fe699304c6fe3dece4f432d7bc196c`
- Status: **COMPLETE LOCALLY — POLICY SELECTED; REPRESENTATIVE VALIDATION NOT RUN**
- Batch position: fresh Phase `5/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]] records one owner-selected compatibility-first policy for future candidate-B proof:

| Policy term | Selected value |
|---|---|
| Rendering API | `D3D12` |
| Direct3D feature level | `12_0+` (`FL12_0+`) |
| Shader Model | `6.6+` (`SM6.6+`) |
| Virtual Shadow Maps | `on` (`VSM on`) |
| Hardware ray tracing | `off` (`HWRT off`) |
| Nanite | `not required` (`Nanite not required`) |

Policy-selection count is `1`. Tests and runs are `0`; representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

Candidate B `MINPC-B_BALANCED_1080P60` remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`. Its historical evidence status remains `CANDIDATE_NOT_APPROVED`; overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`.

## Bounded supersession

DEC-027 supersedes only DEC-026 field 6's future owner-policy placeholder. The committed historical field-6 text and `OWNER_UNSET / UNVERIFIED` snapshot remain frozen evidence; fields 1-5 and 7-25 remain unchanged. The new six terms govern a later proof only and do not retroactively validate current config or current-machine evidence.

The AMD Radeon RX 6600 remains an eligible illustrative candidate-B example with the unchanged `8 GB` VRAM example. This is not hardware selection, acquisition, compatibility proof, or performance evidence.

## Unresolved policy and custody

Exactly eight items remain unresolved:

1. `GI method/raw mapping`
2. `reflection method/raw mapping`
3. `AA method`
4. `upscaler`
5. `screen percentage`
6. `exact visible Medium scalability CVars`
7. `VSync`
8. `frame cap`

The Phase 1L.5g inventory remains exact at `16` rows and its config/current-machine classifications remain unchanged. Current D3D12, RTX 4070 Laptop, maximum feature level `12_2`, shader model `6.7`, and `1280x720` off-screen markers are context only. They supply no candidate-B, illustrative-RX6600, visible-Medium, FPS, GPU/VRAM performance, compatibility, minimum-PC, or readiness result.

## Documentation-only boundary

This fresh Phase `5/6` adds only DEC-027 and this report. It performs no source refetch, runtime launch, test, config change, package or map operation, representative-system proof, procurement, product change, DEC-026 rewrite, or Notion work.

Phase 1K remains incomplete and not waived. Music and Phase 1L exit remain incomplete. Phase 1M, roadmap Phase 2, Version 1, minimum-PC approval, beta readiness, production readiness, release, Notion work, and Phase `6/6` remain unauthorized.
