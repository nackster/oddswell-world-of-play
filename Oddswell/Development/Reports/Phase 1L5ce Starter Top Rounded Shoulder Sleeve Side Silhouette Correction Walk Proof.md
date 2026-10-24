---
tags:
  - development
  - beta
  - character
  - blender
status: complete-targeted-correction-proof
date: 2026-09-27
---

# Phase 1L.5ce Starter-Top Rounded Shoulder / Sleeve / Side Silhouette Correction Walk Proof

## Outcome

Phase 1L.5ce applies only the smallest correction named by the Phase 1L.5cd rejection. It derives from exact Phase 1L.5cc custody and moves only targeted `starter_offwhite_top` shoulder, sleeve and side coordinates. No acceptance verdict is issued here; the next gate must rerun the combined outfit review.

The retained neutral front/rear/profile and opposing walk extremes show a narrower top with rounded shoulder transitions, shorter lateral sleeve span and removed armor-like outer corners. This remains coarse technical geometry, not finished clothing.

## Exact custody and target isolation

- Source Phase 1L.5cc semantic identity: `E56486E7D7DCB87586E6AFC9EF07E8FB85008D78F9231F75D9019B32D1D0E0C4`.
- Accepted body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source top: `20DEC799B15A77DC97EB4CCE521A84362AB952725ACD38C028918AABEC29C73C`.
- Accepted shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Exact walk action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Derived corrected top: `A9DD780C47AC50F1383BA23F4393167E0EC51C62616D868E421C5CD5C3CAAADB`.
- Corrected semantic identity: `7F5D0C4606DF10318372771F7D431AC3884B7858F5304BB22D198BC63301F220`.
- Final Blend: `13,905,337` bytes, SHA-256 `5E4C42EA159EAA4777B3A9D087D1FDAB0AF417C27F3129B022F31E9A2D26F788`.

Exactly `312/498` top vertices are targeted. The remaining `186` vertex coordinates reproduce exactly. Neckline and waist-hem boundary vertex positions, the central front/rear pattern, vertex/edge/polygon topology, material slots/colors, `item_id`, all vertex-group assignments/weights, body, shorts, armature and Action reproduce exactly.

## Measured correction and walk proof

- Lateral span: `1.320000172 m` before, `1.000800133 m` after.
- Maximum targeted vertex displacement: `0.194568373 m`.
- Topology: `498` vertices / `464` polygons / one component / exactly four openings / zero other non-manifold edges.
- Role counts remain nonempty and exact: front `232`, rear `232`, left sleeve `140`, right sleeve `140`, neckline `36`, side seam `40`, hem `28`.
- Weights remain normalized with unweighted and invalid counts `0`.
- All integer frames `1–21` retain body/top and top/bottom evaluated intersections `0`.
- Sampled body/top minimum separation is `0.045855001 m`; observed maximum is `0.045855120 m`.
- Root and armature translation remain exact zero; frame `21` equals frame `1`.

The `Review/BeforeAfter.html` board directly pairs all five exact source views with corrected views. It is comparison evidence only and does not substitute for the next fail-closed acceptance review.

## Verification

- Deterministic semantic rebuild: PASS; identity `7F5D...F220` reproduced.
- Saved-source cold reopen and all custody assertions: PASS.
- Full frozen native automation: `75/75` PASS, exit `0`, failure markers `0`; log SHA-256 `D4E5F9972AEF9740339E72948363AD57A55EB8DE99513A2A5AF3A3FC5B4D7FE0`.
- Isolated frozen Python regression: `105/105` PASS in `146.259s` (`9 + 2 + 8 + 46 + 40`).
- Brain Admin self-check: PASS.
- Retained packaged locomotion, Studio/prompt presentation, camera, listen server and client checks: PASS; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

No neckline, waist hem, shorts, body, Action, skeleton, material, color, detail, Unreal/client or package input changes exist. This proof does not claim final visual acceptance, export/import approval, runtime replacement, fabric behavior, UV/material/LOD production, performance, final art, Phase 1L exit or beta readiness.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5ce starter-top rounded shoulder/sleeve/side silhouette correction walk proof]], [[Development/Reports/Phase 1L5cd Combined Starter Outfit Offline Visual Acceptance Review]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
