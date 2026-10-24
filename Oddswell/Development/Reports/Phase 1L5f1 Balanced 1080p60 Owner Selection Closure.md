# Phase 1L.5f.1 Balanced 1080p60 Owner-Selection Closure

- Date: 2026-08-14
- Branch: `agent/phase-0d`
- Baseline commit: `5e821a3adf8ab07a33131ec011639d1d071fcc50`
- Status: **COMPLETE LOCALLY — PROVISIONAL B SELECTION RECORDED; VALIDATION OPEN**
- Batch position: fresh Phase `3/6`, pending local commit
- Cost: `$0`
- Cursor tasks: `0`

## Outcome

[[Design/Decisions/DEC-026 Provisional Balanced 1080p60 Minimum PC Target]] preserves the owner's literal confirmation once and records this exact disposition:

| Candidate | Selection status | Candidate evidence status |
|---|---|---|
| `MINPC-A_REACH_1080P30` | `NOT_SELECTED` | `CANDIDATE_NOT_APPROVED` |
| `MINPC-B_BALANCED_1080P60` | `OWNER_SELECTED_PROVISIONAL_UNVALIDATED` | `CANDIDATE_NOT_APPROVED` |
| `MINPC-C_QUALITY_1440P60` | `NOT_SELECTED` | `CANDIDATE_NOT_APPROVED` |

Overall minimum-PC decision status is `PARTIALLY_RESOLVED — PROVISIONAL TARGET SELECTED, VALIDATION INCOMPLETE`. Provisional owner-selection authority and count are `1` for B. Final approval, validation, representative testing, measured performance, minimum-PC validation, compatibility, readiness, and release credits remain `0`.

## Frozen contract custody

DEC-026 copies all 25 candidate-B fields unchanged from the committed [[Development/Reports/Phase 1L5f Candidate Minimum PC Specification Decision Packet]]. The copied contract retains:

- exact ID `MINPC-B_BALANCED_1080P60`, name Balanced 1080p60, candidate status `CANDIDATE_NOT_APPROVED`, and marker `RECOMMENDED_FOR_OWNER_REVIEW`;
- supported Windows 11 Home/Pro 64-bit lifecycle boundary, DX12 Ultimate-class GPU, WDDM 2.0, and `Direct3D feature level: OWNER_UNSET / UNVERIFIED`;
- AMD Ryzen 5 5600 example, 6 cores / 12 threads and 3.50 GHz base rule, 16 GB RAM, AMD Radeon RX 6600 8 GB example, and the SSD / 20 GB free editorial hypothesis;
- `1920x1080` Medium, average and median `60 FPS`, average and median `16.67 ms`, P95 `25.00 ms`, the exact stutter and load hypotheses, common future scene envelope, audience/tradeoff, evidence status, known unknowns, future proof, and the frozen historical authority/result field.

That frozen field records selection `0` only at the prior candidate-packet snapshot. This closure separately records current provisional owner-selection authority and count `1`; it grants no final approval or validation credit.

The prior candidate packet closed at commit `5e821a3adf8ab07a33131ec011639d1d071fcc50` with verified two Notion upserts. This closure does not refetch or reinterpret its official primary sources and does not rerun Phase 1L.5e. That retained resource baseline remains `CURRENT_MACHINE_ONLY` and noncomparative.

## Validation still required

The provisional target has not been tested. Before any minimum-PC approval, a separate owner gate must approve the exact Direct3D feature level and field-24 proof, then authorize representative-system evidence for average and median FPS, average and median frame time, P95 frame time, stutter, loads, VRAM, RAM, CPU, thermals, power, compatibility, and failures. No partial result may become a pass.

## Documentation-only boundary

This fresh Phase `3/6` changes only two new decision/report files and four existing planning/canvas files. It changes no product, client, map, package, runtime, config, test, route, gameplay, art, music, accessibility, input, brain, economy, wager, procurement, or machine state.

Phase 1K and input/accessibility evidence remain incomplete and not waived. Music and Phase 1L exit remain incomplete. Phase 1M, roadmap Phase 2, Version 1, minimum-PC approval, beta readiness, production readiness, release, Notion work, and Phase `4/6` remain unauthorized.
