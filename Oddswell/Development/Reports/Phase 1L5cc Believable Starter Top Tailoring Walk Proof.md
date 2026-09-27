---
tags:
  - development
  - beta
  - character
  - blender
status: complete-technical-proof
date: 2026-09-27
---

# Phase 1L.5cc Believable Starter-Top Tailoring Walk Proof

## Outcome

Phase 1L.5cc derives additively from exact Phase 1L.5cb custody and replaces only `starter_offwhite_top`. The accepted refined body, connected starter shorts, exact DEC-035 twelve-bone hierarchy and unchanged `walk_candidate_v1` remain exact.

The replacement is one connected technical T-shirt mesh built from explicit front/rear panels, bridged shoulders and side seams, a separate neckline, a waist hem and two arms-down sleeve openings. Its retained front/rear/profile and opposing walk-extreme reviews show a rounded short-sleeve silhouette rather than the rejected broad cube/tube/poncho proxy. This is deliberately coarse technical tailoring, not finished cloth, human realism, runtime art or beta readiness.

## Custody and geometry evidence

- Exact Phase 1L.5cb semantic identity remains `3D1E437BB1FAEDD41008A158D8EEBA652FDAC00515E68296D7B4F6B14441AC8F`.
- Accepted body mesh remains `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Accepted connected shorts remain `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Accepted `walk_candidate_v1` remains `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- The exact DEC-035 armature remains twelve bones with unchanged names, parents, local heads/tails and deform flags.
- Derived top mesh is `20DEC799B15A77DC97EB4CCE521A84362AB952725ACD38C028918AABEC29C73C`: `498` vertices, `464` polygons, one component, exactly four boundary loops and zero other non-manifold edges.
- Required panel-role evidence is nonempty: front `232`, rear `232`, left sleeve `140`, right sleeve `140`, neckline `36`, side seam `40` and hem `28` faces.
- Top weights use only the required `spine`, `upper_arm.L` and `upper_arm.R` groups; unweighted and invalid/non-normalized counts are `0`.
- All integer frames `1–21` record body/top and top/bottom evaluated intersection pairs `0`. Sampled body/top minimum separation is `0.051936742 m`; the observed maximum is `0.051936913 m`. Sampling is bidirectional vertex-to-opposite-surface evidence, not continuous triangle distance.
- Root and armature translation remain exact zero and frame `21` equals frame `1`.
- Semantic identity `E56486E7D7DCB87586E6AFC9EF07E8FB85008D78F9231F75D9019B32D1D0E0C4` reproduced across two builds; Blend SHA-256 is `253E2680478A30133A0DC49614D9C997FEC06B70B42C470372CD0AF0CF44D7EA` and a separate cold-open validation passes.

## Verification

- Focused Blender 4.5.5 build/rebuild: **PASS**, one component, exactly four declared openings, `21/21` frames and equal loop endpoints.
- Saved-source cold-open validation: **PASS**.
- Full frozen native automation: **75/75 PASS**, exit `0`, failure markers `0`; log SHA-256 `D7B1639CA77EA0E92BC4BCACA19E86543EFD9C7D129E8BBCFC9E2ADB5AB31785`.
- Full frozen Python regression: **105/105 PASS** in `216.987s` on an isolated rerun after the first concurrent run exceeded the existing `120s` performance assertion under native/package load; no code changed for the rerun.
- Brain Admin self-check: **PASS**, exit `0`.
- Retained packaged character verification: locomotion, Studio, camera, client and listen server **PASS**; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Visual boundary

The proof is intentionally simple and faceless. It demonstrates connected panel topology, explicit shirt openings, coarse shoulder/sleeve/torso/hem shaping and stable shared-skeleton deformation. It does not establish fabric folds, production textures or UVs, LODs, runtime UAssets, player-view performance, final character art, Phase 1L exit or beta readiness. The accepted shorts also remain technical rather than final clothing. Runtime replacement stays separately gated after offline visual acceptance.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cc believable starter-top tailoring walk proof]], [[Development/Reports/Phase 1L5cb Believable Starter Shorts Panel Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
