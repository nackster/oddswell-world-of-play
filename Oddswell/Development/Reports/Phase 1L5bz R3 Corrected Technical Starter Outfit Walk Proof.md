---
tags:
  - development
  - beta
  - character
  - blender
status: complete-technical-proof
date: 2026-09-26
---

# Phase 1L.5bz-R3 Corrected Technical Starter Outfit Walk Proof

## Outcome

Phase 1L.5bz now has a bounded technical walk-deformation proof. The accepted refined body, twelve-bone skeleton, DEC-035 mapping and unchanged `walk_candidate_v1` remain exact. Additive derivatives replace only the failing technical garment geometry: a compact three-opening starter-bottom shell and a narrowed two-panel starter-top drape.

Every integer frame `1–21` at `28 fps` passes evaluated-mesh BVH checks with body/top, body/bottom and top/bottom intersection pairs all `0`. Root and armature translation remain exact zero, frame `21` equals frame `1`, and a cold-open validator reproduces the complete deformation record.

This closes the measured garment-intersection blocker. It does not establish a connected finished shirt, believable shorts tailoring, final character art, Unreal import, runtime replacement, performance, beta readiness or production readiness.

## Geometry and deformation evidence

- Accepted body mesh SHA-256 remains `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Accepted source top/bottom identities remain separately recorded and unmodified.
- Derived top: `8` vertices / `2` polygons, two front/rear technical panels, two components, two boundary loops, normalized `spine` weights, and no non-manifold edge outside its panel boundaries.
- Derived bottom: `2,280` vertices / `2,711` polygons, one connected component, exactly three boundary loops (waist plus two leg openings), and no non-manifold edge outside those openings.
- All bottom vertices have normalized weights across `root`, `thigh.L` and `thigh.R`; unweighted and invalid/non-normalized counts are `0`.
- Minimum sampled clearance across all frames is `0.001980603 m` for the top and `0.018012507 m` for the bottom. This is bidirectional vertex-to-opposite-surface sampling, not continuous triangle-distance proof.
- Semantic identity `A78AF6C921EC81F6AB636E235789B91B5173A1343A951B560A4A6F3445A3A14E` reproduced across two builds. Blender rewrote container metadata, so byte-identical `.blend` output is not claimed; the latest saved Blend is custody-locked and cold-validates.

## Verification

- Focused Blender 4.5.5 build: **PASS**, `21/21` frames and loop endpoint equality.
- Saved-source cold-open validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`, failure markers `0`; log SHA-256 `71DE1FE7615C90108310D6D3364487090F27753F35B78FD2997D6F4FFB8F0FB2`.
- Full frozen Python regression: **105/105 PASS**, exit `0`.
- Brain Admin self-check: **PASS**, exit `0`.
- Retained packaged character smoke: locomotion, Studio, camera, client and listen server all **PASS**; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained Windows package remains `50` files / `1,038,710,362` bytes / Python files `0`. No package input changed.
- Post-run OddsWell, Unreal Editor/commandlet, AutomationTool, CrashReportClient and gameplay-port residues are `0`.

## Visual boundary and next gate

The three retained review angles are deliberately evidence, not approval. The technical bottom is still soft and synthetic, and the top is explicitly two disconnected drape panels. The player-facing visual-quality goal therefore remains active.

The smallest truthful next character gate is a connected starter-top pattern and more believable shorts panel construction around this already proven walk, followed by the same `21/21` intersection and review checks. Runtime UAsset replacement remains separately gated after an offline visual candidate passes.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5bz refined starter-outfit walk deformation proof]], [[Development/Reports/Phase 1L5bz R2 Starter Bottom Topology Redesign Failure]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
