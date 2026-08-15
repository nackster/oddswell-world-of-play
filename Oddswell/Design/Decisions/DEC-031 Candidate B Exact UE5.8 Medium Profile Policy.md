---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - phase-1l
status: accepted
date: 2026-08-15
---

# DEC-031 Candidate B Exact UE5.8 Medium-Profile Policy

## Owner response and bounded authority

The owner exchange was:

`Which provisional visible-Medium contract should Candidate B use for later automated validation?`
`A — Exact installed UE5.8 Medium/@1 contract (RECOMMENDED): select all 11 scalability group selectors at level 1; adopt the exact 154 live child-CVar assignments from the 10 present installed @1 sections; set sg.LandscapeQuality=1 as the eleventh observable group selector while assigning zero invented Landscape child CVars because [LandscapeQuality@1] is absent. Later proof must retain all 11 selectors and all 154 effective child values.`
> Continue the next 6 phrases with the 4 agents

That response supplies wording authority only to adopt the immediately preceding bounded Option A. It does not authorize six additional phases, agent work, runtime work, testing, configuration changes, or any action outside this documentation-only decision.

## Decision

For the first later authorized Candidate B `MINPC-B_BALANCED_1080P60` automated validation, the owner selected the exact installed Unreal Engine 5.8 Medium/@1 profile as future custody:

| Ordered observable selector | Selected value |
| --- | --- |
| `sg.ViewDistanceQuality` | `1` |
| `sg.AntiAliasingQuality` | `1` |
| `sg.ShadowQuality` | `1` |
| `sg.GlobalIlluminationQuality` | `1` |
| `sg.ReflectionQuality` | `1` |
| `sg.PostProcessQuality` | `1` |
| `sg.TextureQuality` | `1` |
| `sg.EffectsQuality` | `1` |
| `sg.FoliageQuality` | `1` |
| `sg.ShadingQuality` | `1` |
| `sg.LandscapeQuality` | `1` |

The immutable child contract is the exact `154` live assignments in the `10` present installed `@1` sections recorded verbatim by [[Development/Reports/Phase 1L5i Current AA Upscaling Medium Profile and Frame Control Evidence Inventory]]. The installed source is `C:/Program Files/Epic Games/UE_5.8/Engine/Config/BaseScalability.ini`, SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6`. `[LandscapeQuality@1]` is absent, so `sg.LandscapeQuality=1` remains the eleventh observable selector while its adopted child-assignment count is exactly `0`; invented Landscape child CVars are exactly `0`.

Completion status is `COMPLETE LOCALLY — PROVISIONAL EXACT MEDIUM PROFILE SELECTED; VALIDATION NOT RUN`.

This is future validation policy only. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Bounded DEC-027 supersession

This decision resolves only one ordered item in [[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]]:

1. `exact visible Medium scalability CVars` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future bounded Candidate B validation must select all `11` group selectors at level `1`, retain the exact `154` installed live child assignments, and invent no Landscape child CVar.

Exactly two items remain unresolved, in this order:

1. `VSync`
2. `frame cap`

DEC-028 remains unchanged: future Candidate B GI/reflection policy is `Lumen` global illumination plus `Screen Space Reflections` (`SSR`). DEC-029 remains unchanged: future Candidate B uses TSR AA plus the built-in Unreal TSR temporal path with third-party plugin/dependency count `0`. DEC-030 remains unchanged: fixed output `1920x1080`, fixed primary screen percentage `100%`, native internal `1920x1080`, TSR AA-only, and dynamic resolution disabled. DEC-027's compatibility terms remain unchanged: `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required`.

No other DEC-027 term, DEC-026 field, Candidate B field, illustrative hardware example, historical evidence status, or proof requirement changes.

## Reference and effective-state boundary

The exact `154` child assignments and their group counts are installed UE5.8 reference custody. This decision selects them as a future Candidate B contract; it does not prove that the current product has selected Medium, that the selectors or child values are currently effective, or that a visible representative run can retain them without override. The current retained run used `@3`, not `@1`, and remains current-machine-only nonproof for this decision.

A later separately authorized representative visible Candidate B run must set and retain all `11` selectors at `1`, verify all `154` effective child values against the immutable source-backed contract, confirm zero invented Landscape child values, disclose any DeviceProfile, user, command-line, or runtime overrides, and collect the separately required visible-output and performance evidence. Selector equality alone is not performance, compatibility, minimum-PC, or readiness proof.

## OUT boundary

This decision changes no runtime, source, config, plugin, dependency, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, or machine state. It authorizes no launch, test, representative-system run, measurement, acquisition, compatibility claim, minimum-PC approval, beta or production readiness, release, Notion work, or fresh Phase `6/6`.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, and release remain unauthorized.

The bounded closure report is [[Development/Reports/Phase 1L5i4 Candidate B Exact UE5.8 Medium Profile Policy Closure]].
