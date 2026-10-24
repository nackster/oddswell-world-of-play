---
tags:
  - development
  - beta
  - character
  - blender
status: complete-technical-proof
date: 2026-09-27
---

# Phase 1L.5cb Believable Starter-Shorts Panel Walk Proof

## Outcome

Phase 1L.5cb derives additively from exact Phase 1L.5ca custody and replaces only `starter_offwhite_bottom`. The accepted refined body, connected starter top, exact DEC-035 twelve-bone hierarchy and unchanged `walk_candidate_v1` remain exact.

The replacement is one connected technical shorts mesh with exactly three declared openings: waist, left leg and right leg. Its front/rear leg panels, tapered rise, connected crotch/gusset, waistband, hems, inseam and outseams are visible in retained front/rear/profile and opposing walk-extreme reviews. It has no pockets, fly, logos, extras or cloth physics. This closes the synthetic shell/saddle/skirt blocker at technical-proof fidelity; it does not establish final tailoring, runtime import, performance, Phase 1L exit, beta readiness or production readiness.

## Custody and geometry evidence

- Exact Phase 1L.5ca semantic identity remains `83C813FEAF9D138E689480869C1FDC9E7AE580DFC33D3732C1EBE431044FC803`.
- Accepted body mesh remains `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Accepted connected top remains `095929FDAE403198912D8BEC21EE0A28EB579AEB5BC2BB9BD2CC25C0A72ED54A`.
- Accepted `walk_candidate_v1` remains `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- The exact DEC-035 armature remains twelve bones with unchanged names, parents, local heads/tails and deform flags.
- Derived bottom mesh is `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`: `5,862` vertices, `7,157` polygons, one component, three boundary loops and zero other non-manifold edges.
- Required panel-role evidence is nonempty: front `3,584`, rear `3,573`, waistband `593`, hem `499`, inseam `639` and outseam `59` faces.
- Bottom weights use only the required `root`, `thigh.L` and `thigh.R` groups; unweighted and invalid/non-normalized counts are `0`.
- All integer frames `1–21` record body/bottom and top/bottom evaluated intersection pairs `0`. Sampled body/bottom minimum separation is `0.018486369 m`; the observed maximum is `0.040899202 m`. Sampling is bidirectional vertex-to-opposite-surface evidence, not continuous triangle distance.
- Root and armature translation remain exact zero and frame `21` equals frame `1`.
- Semantic identity `3D1E437BB1FAEDD41008A158D8EEBA652FDAC00515E68296D7B4F6B14441AC8F` reproduced across two builds; Blend SHA-256 is `3A83B5F7A6D631CB8B4F6FD5A1E04922F69461FA4A51E02CF613B6F6E5A35C3F` and a separate cold-open validation passes.

## Verification

- Focused Blender 4.5.5 build/rebuild: **PASS**, one component, exactly three declared openings, `21/21` frames and equal loop endpoints.
- Saved-source cold-open validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`, failure markers `0`; log SHA-256 `0780A8321A98980B91087437BB093F1BE780981F548B1EF171EF4A28688C231F`.
- Full frozen Python regression: **105/105 PASS** in `160.997s`, exit `0`.
- Brain Admin self-check: **PASS**, exit `0`.
- Retained packaged character verification: locomotion, Studio, camera, client and listen server **PASS**; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Visual boundary

The proof is intentionally simple and faceless. It demonstrates a connected shorts pattern, explicit garment openings and stable shared-skeleton deformation, not final cloth folds, fabric, UV/material production, LODs, runtime assets or human realism. The connected top remains the broad Phase 1L.5ca technical proxy. Runtime UAsset replacement remains separately gated after offline visual acceptance.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cb believable starter-shorts panel walk proof]], [[Development/Reports/Phase 1L5ca Connected Starter Top Pattern Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
