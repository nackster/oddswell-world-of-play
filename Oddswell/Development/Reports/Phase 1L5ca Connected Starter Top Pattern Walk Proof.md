---
tags:
  - development
  - beta
  - character
  - blender
status: complete-technical-proof
date: 2026-09-26
---

# Phase 1L.5ca Connected Starter-Top Pattern Walk Proof

## Outcome

Phase 1L.5ca replaces only the Phase 1L.5bz-R3 two-panel technical top with one connected technical shirt mesh. The accepted refined body, R3 starter bottom, exact DEC-035 twelve-bone hierarchy and unchanged `walk_candidate_v1` remain exact.

The new top is one mesh component with exactly four declared boundary openings: neckline, waist hem, left arm and right arm. It has no other non-manifold edges, every vertex has normalized weights on the existing shared skeleton, and every integer frame `1–21` passes evaluated body/top and top/bottom intersection checks at `0`. Root and armature translation remain exact zero and frame `21` equals frame `1`.

This closes the disconnected starter-top topology gate. It does not establish believable tailoring, final clothing, runtime import, performance, Phase 1L exit, beta readiness or production readiness.

## Custody and geometry evidence

- Exact R3 source Blend receipt remains `9EC9404A9C7C394A100C51D30077C6B81D92154A61E7462368D6CB8742132CF0`; R3 semantic identity remains `A78AF6C921EC81F6AB636E235789B91B5173A1343A951B560A4A6F3445A3A14E`.
- Accepted body mesh remains `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Accepted R3 bottom mesh remains `5C0357E1ADDE7B35380222BDF6AD33BFF75A59D28B1AEFDD2404AC8630083618`.
- Accepted `walk_candidate_v1` remains `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- The exact DEC-035 armature remains twelve bones with unchanged names, parents, local heads/tails and deform flags.
- Derived top mesh is `095929FDAE403198912D8BEC21EE0A28EB579AEB5BC2BB9BD2CC25C0A72ED54A`: `1,546` vertices, `1,410` polygons, one component, four boundary loops and zero other non-manifold edges.
- Top weights use only `spine`, `upper_arm.L` and `upper_arm.R`; unweighted and invalid/non-normalized counts are `0`.
- Minimum sampled top/body separation across all 21 frames is `0.026332714 m`. This is bidirectional vertex-to-opposite-surface sampling, not continuous triangle-distance proof.
- Semantic identity `83C813FEAF9D138E689480869C1FDC9E7AE580DFC33D3732C1EBE431044FC803` reproduced across two builds; the latest Blend is custody-locked and cold-validates.

## Verification

- Focused Blender 4.5.5 build/rebuild: **PASS**, one component, four declared openings, `21/21` frames and equal loop endpoints.
- Saved-source cold-open validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`, failure markers `0`; log SHA-256 `7CA7F8879F21CAFAC6413C5B47B8B44E417BC3CF1961C210DE552D464643C7BC`.
- Full frozen Python regression: **105/105 PASS** in `301.826s`, exit `0`.
- Brain Admin self-check: **PASS**, exit `0`.
- Retained packaged character verification: locomotion, Studio, camera, client and listen server **PASS**; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- The packaged helper's first offscreen attempts exposed pre-existing startup timing variation in the unchanged package: one missed idle-state sample and later camera drift while world collision settled. A fresh hidden normal-render run passed every required marker. No client, Unreal or package input changed.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Visual boundary

Front, rear, profile and two opposite walk-extreme reviews show continuous torso, side and shoulder geometry. The new mesh is deliberately a broad beveled technical shirt pattern, not believable final fabric. Its silhouette, neckline, sleeves and hem still need visual tailoring, while the unchanged bottom remains synthetic. Runtime UAsset replacement remains separately gated after offline visual acceptance.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5ca connected starter-top pattern walk proof]], [[Development/Reports/Phase 1L5bz R3 Corrected Technical Starter Outfit Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
