---
tags:
  - development
  - beta
  - character
  - review
status: complete-review-rejected-visual-correction-required
date: 2026-09-29
---

# Phase 1L.5cp Rounded-Cap Combined Starter-Outfit Offline Visual Acceptance Review

## Outcome

Phase 1L.5cp is complete as an evidence-only review with verdict `REJECTED_VISUAL_CORRECTION_REQUIRED`. Exact Phase 1L.5co custody and numeric/mechanical gates pass, but the retained views fail three unchanged qualitative criteria: neckline/shoulders/sleeves/hem, no rejected silhouettes and stable opposing extremes. The verdict is derived from all seven criterion statuses rather than selected in advance; numeric gates do not override qualitative failures.

This rejection stops export/import preparation. It is not an export, import, runtime replacement, final-art approval, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness determination.

## Exact custody

- Source Blend: `13,907,177` bytes, SHA-256 `7EF2728BF1F091FF5A4DEF57815CCF7159DCE21A19528AA5595E848B07139363`.
- Phase 1L.5co semantic identity: `2384397B3BAB50C3CC01222F8EE9EDE598A430444FC7FEC3C233CA46272CD07A`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Rounded-cap top: `519C4F12ADB179FDA71E1E11B043798018FF344369CCB1AE5799A7040DEF4C47`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Frame-ledger identity: `4DE37C1F83A7E0EAB04E3943DBE3CBB9CDE52FA0AFA242105D54D18D3CC6927C`.
- Topology identity: `64BD03BA4EAB3A529B303860427453B47C2807C8AF25F520329CC2E5078C8FE3`.
- Opening identity: `EB01DC302C225D73C0D44245D773DBDE975488734A6FBE2E7FFC60BB31F28309`.
- Five-view identity: `A3E85B935855F009F01D8C755BD8C98335131A034456573A7BEC754AB0647C33`.

Asset, geometry, weight, topology, material, action, skeleton, export, Unreal/client, package-input and runtime changes are all `0`.

## Unchanged seven-criterion review

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | The exact retained `21`-frame ledger reports body/top, body/bottom and top/bottom evaluated intersections `0`. |
| Neckline / shoulders / sleeves / hem | FAIL | The topology/opening contract passes and the outer caps are rounded, but the neutral shoulder remains a raised planar shelf and the frame-16 right shoulder-to-cap transition ends in a sharp triangular fold rather than one continuous garment arc. |
| Waistband / rise / crotch / legs | PASS | Exact accepted connected shorts retain three openings, zero other non-manifold edges and two readable legs. |
| Proportions | PASS | Neutral top width is `0.930000007 m` versus body width `0.675352 m`, ratio `1.377059677`, within the unchanged `1.4` ceiling. This numeric pass does not override qualitative failures. |
| No rejected silhouettes | FAIL | Width ratio `1.377059677` and waist inset `0.132244272` pass their numeric gates, but front/rear remain broad and box/poncho-like while the profile is slab-like with a detached horizontal mid-torso bulge. |
| No exposure or collision | PASS | All five exact views retain body coverage without visible interpenetration; the ledger also reports zero evaluated intersections. |
| Stable opposing extremes | FAIL | Mechanical loop and translation checks pass, but the rounded cap changes from a bulbous fold at frame `6` to a sharp outward spike at frame `16`; the exact views do not support qualitative garment stability. |

The one smallest next correction is only the top upper shoulder-yoke-to-cap transition within `0.24 m <= |X| < 0.389245 m` and `1.38 m <= Z <= 1.56 m`, including its normalized spine/upper-arm blend, reshaped into one continuous shoulder-to-cap arc while preserving the central torso, waist, neckline, accepted outer cap/openings and all non-target assets.

## Deterministic evidence

- Review identity: `6149951BF5B4DFF12A794C9B68DA96049828099D0CC7729F3FF6139EA9390ED0`.
- Deterministic board: `1,040,751` bytes, SHA-256 `047174A634F6352C8133BCADF077926C7AA4148F066F4D0DCA4BB9C4964D07AF`.
- Exact retained views: front `9B5DB761457F598E8C4E2BC57C210A38D50E1836384528C14F0860BC69AC0BD5`, rear `78CD9CEC3E6D8257380FFCEBCD2792FBD38BE3013A3F8A4DBEFDD1D82E7DA9E6`, profile `DF3C3CF0634AC997E13DC24670F164D92EE76DFBD855A8D6151272CAEDA9CA14`, frame-6 extreme `3182394B2DF865502D688B33F51098CB9DF773FBD961C926DC61BA945B22816F`, frame-16 extreme `763CF6EC0E838EE703E5ECD7BDF848290EA47194AEA9D8AC66DA4644C30693EE`.

## Verification

- Deterministic build and independent validation: PASS; rejection identity `6149...0ED0` and board `0471...07AF` reproduced.
- Full frozen native suite: PASS, `75/75`, with `0` non-success markers; retained log SHA-256 `79DD069C43FDCEE1F4C0B7974041E011B04FEA8A77FAD5040B0DCA62544802E8`.
- Isolated Python regression: PASS, `105/105` (`9 + 2 + 8 + 46 + 40`) in `168.696 s` of reported test time.
- Brain Admin self-check: PASS; exact `43`-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion and character-motion markers passed; Studio and interaction-prompt-presentation markers passed; camera-orbit passed; shared-city server/client, skeletal appearance and skeletal motion markers passed. All processes emitted exit-status `0`, and UDP `17777` was released. Log hashes: locomotion `2499B63B811EE6EB8493A471379E8FDC9FCD796C3A6605A2E21A7A404067B6E6`, Studio `993C7B304C8C32DE0949FA10F5546FFB233C0A891F527ABFB6CE69DA66DD71F4`, camera `F92C1EE439B7814E416364572D64301B216A8A9A575FE1C5442F8D898AA7D66A`, server `4B42517B1EA4C6CECDFD458F6CBB60D397207E6AF4DBCB4EF783EF1FF6DDEEE9`, client `8A55E6F1218B6FFB14ECD55E148A44D8840837685D9582B99F6F322B0E46AA47`.
- Retained package audit: `50` files, `1,038,710,362` bytes, `0` Python files. Final process audit found `0` OddsWell, Unreal Editor or Blender processes.

## Boundary and next gate

Export/import preparation is not eligible. The only bounded next correction is the measured top-only shoulder-yoke-to-cap transition above. This review changes no asset or runtime input. Fabric, production UVs, LODs, final materials, runtime replacement, performance, hands-on usability, Phase 1L exit and beta readiness remain separate unproven gates.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cp rounded-cap combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5co Outer Sleeve Armhole Rounded Cap Correction Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
