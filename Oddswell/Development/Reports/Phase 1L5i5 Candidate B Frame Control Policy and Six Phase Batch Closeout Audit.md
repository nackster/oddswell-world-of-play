# Phase 1L.5i.5 Candidate B Frame-Control Policy and Six-Phase Batch Closeout Audit

- Date: 2026-08-15
- Branch: `agent/phase-0d`
- Baseline commit: `5a5a4a23c3e36710b72737be17c286087663899f`
- Status: **COMPLETE LOCALLY — FRAME-CONTROL POLICY SELECTED; PLANNING AUTHORITY BOUNDED; VALIDATION NOT RUN; SIX-PHASE BATCH CLOSED**
- Batch position: final fresh Phase `6/6`
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-032 Candidate B Frame Control and Bounded Planning Authority]] records this future custody for a later separately authorized Candidate B `MINPC-B_BALANCED_1080P60` automated performance validation:

| Control | Selected future value |
| --- | --- |
| VSync | off; `r.VSync=0` |
| Frame cap | uncapped; `t.MaxFPS=0` |

The selection is a measurement-custody policy, not a shipping or player-facing settings decision. It does not prove current effective state, remove every timing constraint, guarantee performance or measurement neutrality, validate Candidate B, or grant minimum-PC, compatibility, or readiness credit.

The final two DEC-027 items are resolved with disposition `OWNER_SELECTED_PROVISIONAL_UNVALIDATED_POLICY`:

1. `VSync` — future bounded validation uses `r.VSync=0`.
2. `frame cap` — future bounded validation uses `t.MaxFPS=0`.

DEC-027 remaining unresolved-item count is exactly `0`. Candidate B remains `OWNER_SELECTED_PROVISIONAL_UNVALIDATED`; historical evidence remains `CANDIDATE_NOT_APPROVED`, and overall minimum-PC status remains `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Tests, representative validation, measured performance, minimum-PC validation, compatibility, and readiness credits remain `0`.

## Bounded standing planning authority

The owner response recorded once in DEC-032 authorizes adoption without a repeated response only for an explicitly identified recommended option that is reversible, non-destructive, `$0`, and solely a documentation/planning-policy choice inside the already authorized Beta Roadmap. Evidence and alternatives must be documented. The choice must create zero product, runtime, config, source, package, or external-state change and grant zero implementation, validation, compliance, compatibility, performance, or readiness credit. Authority applies to one smallest gate/phase at a time; it is not retroactive or blanket and does not cover a non-recommended or materially expanded option.

Explicit owner approval remains required for purchases; installations or dependencies; deployment, push, or release; irreversible or destructive actions; external communications or accounts; paid APIs; real money; Odds Bucks or economy decisions; wagering or monetization; legal, platform, age, or region decisions; networking or safety scope; art-family, music, or license expansion; beta or core-loop scope expansion; beta-exit approval; roadmap Phase 2; Phase 1M release; Version 1 scope freeze; and hands-on, player, or accessibility evidence. No agents, phases, batches, or seventh phase are authorized automatically. Express owner and execution gates remain in force; the authority does not validate a policy or prevent owner override.

## Frozen Candidate B policy ledger

| Decision | Preserved policy |
| --- | --- |
| DEC-027 | `D3D12`; `FL12_0+`; `SM6.6+`; `VSM on`; `HWRT off`; `Nanite not required` |
| DEC-028 | Lumen GI plus SSR |
| DEC-029 | TSR AA plus built-in Unreal TSR; third-party plugin/dependency count `0` |
| DEC-030 | output/internal `1920x1080`; fixed primary `100%`; TSR AA-only; dynamic resolution disabled |
| DEC-031 | selectors `11` all at `1`; present sections `10`; immutable assignments `154`; `sg.LandscapeQuality=1`; Landscape child/invented `0/0`; source SHA-256 `579039219A363C16936D7913FBA7656DAC4BDBF12BBE180CA99536BAFB7AF0A6` |
| DEC-032 | VSync off through `r.VSync=0`; uncapped through `t.MaxFPS=0` |

Current project selection and effective settings remain unproven. The retained current-machine/off-screen evidence, engine defaults, source mappings, installed Medium references, and policy selections are not representative performance, compatibility, minimum-PC, or readiness proof.

## Final six-phase ledger

| Fresh phase | Closure | Custody |
| ---: | --- | --- |
| `1/6` | Phase 1L.5i inventory | `1b04d82e678bc5cb761c338de012945a42e8d8da`; verified exactly two Notion upserts |
| `2/6` | Phase 1L.5i.1 GI/reflection | `b35c4c55716e418f9dbc03f36349c3f23f9f7586`; verified exactly two Notion upserts |
| `3/6` | Phase 1L.5i.2 AA/upscaler | `757b82ff77e82b3cfb023e3c42a2fd17b6476099`; verified exactly two Notion upserts |
| `4/6` | Phase 1L.5i.3 screen percentage | `eb2059888a9a0ac66cfd4a571aa3eaf38d893429`; verified exactly two Notion upserts |
| `5/6` | Phase 1L.5i.4 Medium profile | `5a5a4a23c3e36710b72737be17c286087663899f`; verified exactly two Notion upserts |
| `6/6` | Phase 1L.5i.5 frame control and closeout | the local commit containing this report |

## Documentation-only closeout boundary

This final fresh Phase `6/6` creates only DEC-032 and this report. It changes no runtime, source, config, plugin, dependency, package, map, product, gameplay, art, input, accessibility, brain, economy, procurement, account, external system, or machine state. It performs no launch, test, representative-system run, measurement, compatibility finding, minimum-PC validation or approval, shipping-setting selection, beta or production readiness, release, Notion work, or roadmap Phase 2 work.

Phase 1K and hands-on/input/accessibility evidence remain incomplete, deferred, and not waived. Brain maturity remains frozen with no training, learning, retraining, or readiness claim. Music and Phase 1L exit remain incomplete; Phase 1M, roadmap Phase 2, Version 1, readiness, and release remain unauthorized.

**NO SEVENTH PHASE — BATCH STOPPED.** The bounded standing planning authority does not authorize another phase or batch.
