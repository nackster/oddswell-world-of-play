---
tags:
  - decision
  - minimum-pc
  - rendering-policy
  - planning-authority
  - phase-1l
status: accepted
date: 2026-08-15
---

# DEC-032 Candidate B Frame Control and Bounded Planning Authority

## Owner response and bounded authority

The owner exchange was:

`Which provisional VSync/frame-cap pair should Candidate B use for its later automated performance validation?`
`A — Measurement-neutral (RECOMMENDED): VSync off; frame cap uncapped (t.MaxFPS=0) for the bounded validation. This exposes measured headroom and frame-time behavior; it is not a shipping/player-facing settings decision.`
> Yes adopt and you don't need my permission from now on to adopt

The response adopts the immediately preceding Option A and grants standing authority only for an explicitly identified recommended option that is reversible, non-destructive, `$0`, and solely a documentation/planning-policy choice inside the already authorized Beta Roadmap. The evidence and alternatives must be documented, and the choice must cause zero product, runtime, config, source, package, or external-state change and grant zero implementation, validation, compliance, compatibility, performance, or readiness credit. Authority applies to one smallest gate/phase at a time. It is not retroactive or blanket authority, and it does not cover a non-recommended or materially expanded option.

Explicit owner approval remains required for purchases; installations or dependencies; deployment, push, or release; irreversible or destructive actions; external communications or accounts; paid APIs; real money; Odds Bucks or economy decisions; wagering or monetization; legal, platform, age, or region decisions; networking or safety scope; art-family, music, or license expansion; beta or core-loop scope expansion; beta-exit approval; roadmap Phase 2; Phase 1M release; Version 1 scope freeze; and hands-on, player, or accessibility evidence. No agents, phases, batches, or seventh phase are authorized automatically. This authority cannot waive an owner gate expressly required by an existing decision, convert a provisional policy into validation or approval, or override the owner. Each execution action and each materially different scope still requires its own applicable gate.

## Decision

For the first later separately authorized Candidate B `MINPC-B_BALANCED_1080P60` automated performance validation, the selected future frame-control custody is:

| Control | Selected future value | Meaning |
| --- | --- | --- |
| VSync | off; `r.VSync=0` | do not synchronize the bounded validation to display refresh |
| Frame cap | uncapped; `t.MaxFPS=0` | do not impose the engine maximum-FPS cap during the bounded validation |

Completion status is `COMPLETE LOCALLY — FRAME-CONTROL POLICY SELECTED; PLANNING AUTHORITY BOUNDED; VALIDATION NOT RUN; SIX-PHASE BATCH CLOSED`.

The phrase “measurement-neutral” names the selected custody, not a proof claim. It does not establish current effective settings, remove other timing constraints, guarantee unbiased measurements, validate performance, select a shipping or player-facing setting, or approve Candidate B. A later authorized representative run must retain the effective values and disclose every DeviceProfile, user, command-line, runtime, display, presentation, or platform override before any metric is interpreted.

Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; its historical evidence status remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## DEC-027 closure

This decision resolves only the final two ordered items in [[Design/Decisions/DEC-027 Candidate B Compatibility First Direct3D Policy]]:

1. `VSync` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future bounded validation uses VSync off through `r.VSync=0`.
2. `frame cap` — `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`; future bounded validation is uncapped through `t.MaxFPS=0`.

DEC-027 remaining unresolved-item count is exactly `0`. This is policy closure only; effective-state, representative-test, performance, minimum-PC, compatibility, and readiness proof remain absent.

## Frozen Candidate B policy ledger

| Decision | Unchanged provisional future custody |
| --- | --- |
| DEC-027 | `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required` |
| DEC-028 | `Lumen` global illumination plus `Screen Space Reflections` (`SSR`) |
| DEC-029 | TSR AA plus the built-in Unreal TSR temporal upscaler; third-party plugin/dependency count `0` |
| DEC-030 | fixed output `1920x1080`; primary screen percentage `100%`; native internal `1920x1080`; TSR AA-only; dynamic resolution disabled |
| DEC-031 | all `11` scalability selectors at `1`; immutable installed `154` child assignments from `10` present sections; `sg.LandscapeQuality=1`; Landscape child/invented counts `0/0`; installed source SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6` |
| DEC-032 | VSync off through `r.VSync=0`; uncapped through `t.MaxFPS=0` |

No earlier policy, source-custody boundary, historical config observation, Candidate B field, illustrative hardware example, evidence status, or proof requirement changes.

## Final six-phase ledger

| Fresh phase | Bounded closure | Local commit and canonical documentation custody |
| ---: | --- | --- |
| `1/6` | Phase 1L.5i evidence inventory | `1b04d82e678bc5cb761c338de012945a42e8d8da`; verified exactly two Notion upserts |
| `2/6` | Phase 1L.5i.1 GI/reflection policy | `b35c4c55716e418f9dbc03f36349c3f23f9f7586`; verified exactly two Notion upserts |
| `3/6` | Phase 1L.5i.2 native TSR AA/upscaler policy | `757b82ff77e82b3cfb023e3c42a2fd17b6476099`; verified exactly two Notion upserts |
| `4/6` | Phase 1L.5i.3 fixed-100-percent screen policy | `eb2059888a9a0ac66cfd4a571aa3eaf38d893429`; verified exactly two Notion upserts |
| `5/6` | Phase 1L.5i.4 exact UE5.8 Medium-profile policy | `5a5a4a23c3e36710b72737be17c286087663899f`; verified exactly two Notion upserts |
| `6/6` | Phase 1L.5i.5 frame-control policy and batch closeout | the local commit containing this report |

## Final boundary

This decision changes no runtime, source, config, plugin, dependency, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, account, external system, or machine state. It performs and authorizes no current launch, test, representative-system run, measurement, compatibility finding, minimum-PC validation or approval, shipping-setting selection, beta or production readiness, release, Notion work, or roadmap Phase 2 work.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen; no training, learning, retraining, or readiness claim follows. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, and release remain unauthorized.

**NO SEVENTH PHASE — BATCH STOPPED.** The standing planning authority above does not reopen, extend, or replace this hard stop.

The bounded closure report is [[Development/Reports/Phase 1L5i5 Candidate B Frame Control Policy and Six Phase Batch Closeout Audit]].
