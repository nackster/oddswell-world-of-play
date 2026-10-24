# Phase 1L.4b.1 — Single In-Place Façade Candidate Acceptance Closure

Date: 2026-08-12
Branch: `agent/phase-0d`
Status: **COMPLETE — OWNER ACCEPTED OPTION A FOR ONE EXACT CANDIDATE**
Cost: `$0.00`

## Outcome first

The owner selected exactly:

> A — Approve this single in-place façade candidate.

[[Design/Decisions/DEC-024 Single In-Place Facade Candidate Acceptance]] records that this approval applies only to `SM_Sundale_ResidentialFacade_A` at the existing transient, bounded Starter-Studio presentation seam proven by Phase 1L.4b. Future bounded tweaks to this one candidate remain allowed.

The original implementation, screenshots, route, collision, resource, cook, package, import, LFS, and regression evidence remain unchanged in [[Development/Reports/Phase 1L4b One-Candidate Starter-Studio Unreal In-Place Proof]]. This closure does not reinterpret or replace that evidence.

## Exact accepted candidate

| Contract | Accepted value |
| --- | --- |
| Mesh | `SM_Sundale_ResidentialFacade_A` |
| Presentation seam | Existing transient `StudioFacade` slot |
| Transform | `(0,-156,0) cm`, `(pitch=0,yaw=180,roll=0)`, scale `1.0` |
| Imported bounds | `520 x 410 x 500 cm` |
| Geometry | `96` triangles, one UV channel, one material slot |
| Material | Existing `M_Sundale_ResidentialFacade_VertexColor` contract |
| Runtime safety | Local-only, non-replicated, non-colliding, non-overlapping, non-physical, dedicated-server excluded |
| Authored map | Unchanged; presentation remains outside the map asset |

Approval means this single candidate may remain the accepted in-place façade candidate at that seam. It is not an approval of final art or a reusable production family.

## Fresh proportional verification

Only the explicitly requested frozen checks were rerun because this closure changes documentation and one clean canvas only:

| Gate | Result |
| --- | --- |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `python -B -m brain_admin.server --check` | PASS; `88`-byte stdout SHA-256 `259EF12021009C4EEDFC9873BBE5C135CA8BE3FF36B0A2D607FFC2480068A26D`; stderr `0` |
| Production client/runtime/config/test diff | PASS `0` paths |
| Protected `SundaleGraybox.umap` | Unchanged SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Retained canonical package | Unchanged `50` files / `1,051,962,028` bytes / zero Python |
| Original Phase 1L.4b report/evidence | Preserved unchanged |

Fresh Python evidence is retained under `C:\tmp\OddsWellPhase1L4b1`. No Unreal editor, native automation, build, cook, packaged runtime, or visual process was launched because no production input changed.

## Truth boundary

This decision does not authorize production-batch Phase `3/6`, Phase 1L.4c, a second façade, tower, reusable family, collision or LOD expansion, authored-map placement, citywide implementation, roadmap Phase 2, Version 1, deployment, final art, beta readiness, or production readiness.

It changes no runtime, source, configuration, test, asset, map, package, canonical `800 m` route, gameplay, business, economy, authority, save, network, brain, simulator, or Phase 1K behavior. Phase 1K remains incomplete and deferred to the MVP playtest, not waived.

Execution creates no Notion or Cursor task, and Cursor tasks created remain `0`. After Coordinator post-commit verification, the separate Notion role must perform exactly two duplicate-checked upserts: the canonical milestone closure and the owner decision.

## Next gate

Stop after this documentation closure. Any bounded tweak to the accepted candidate or any new asset, family, integration, Phase 1L.4c, or production-batch Phase `3/6` requires a fresh Scope Director gate.
