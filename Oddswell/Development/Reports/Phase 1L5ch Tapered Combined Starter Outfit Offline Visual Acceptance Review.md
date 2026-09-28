---
tags:
  - development
  - beta
  - character
  - review
status: rejected-visual-correction-required
date: 2026-09-28
---

# Phase 1L.5ch Tapered Combined Starter-Outfit Offline Visual Acceptance Review

## Verdict

`REJECTED_VISUAL_CORRECTION_REQUIRED`

The Phase 1L.5cg central torso-depth taper is present, but the exact unchanged seven criteria do not all pass. Front, rear and both walk extremes still show a top that substantially overpowers the body and shorts in lateral width, with a rigid torso-to-sleeve transition and straight hem. Technical export/import preparation remains stopped.

The one smallest next correction is to reshape only the top central front/rear lateral silhouette into a waist-tapered panel while preserving shoulders, sleeves, the accepted depth taper, openings and every other accepted identity.

## Exact custody

- Source tapered Blend: `13,905,337` bytes, SHA-256 `4AE2F2B1E695F1DA7D09EB8D7F862CBADCFEB93D35413326A854A15169F03C35`.
- Source semantic identity: `8B8008D832BFB0D1C1753D24AE2AF99C5CAE6CE24B8ED30439438904A0A55A61`.
- Body mesh: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Tapered starter top: `1C7F8649211C44B9039F12902E266C438C5EF6DA4DF224D7FBD1FCF108AEC353`.
- Starter shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Armature: exact DEC-035 twelve-bone hierarchy.
- Action: `walk_candidate_v1` identity `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Retained 21-frame ledger identity: `7CA68167E035D763AF96FF7607178161C182C0908781CEC6373E887B1E4B1592`.
- Review identity: `8C592DD18048263EDB4D95CF9C24E49A376D62C234862FAF8FAC5379DA4E9637`.
- Deterministic board: `1,057,787` bytes, SHA-256 `279E0868974C9CFD91E13CBFBF1C0EB2BB7E78E8D430C80436EDA432BB4172F9`.

Geometry, weights, topology, materials, Action, skeleton, export, Unreal/client files and package inputs changed `0`.

## Exact unchanged criterion ledger

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | The retained 21-frame ledger reports zero body/top, body/bottom and top/bottom evaluated intersections. |
| Neckline / shoulders / sleeves / hem | FAIL | Rounded shoulders remain, but the torso-to-sleeve width transition and rigid straight hem still read as an oversized rectangular slab. |
| Waistband / rise / crotch / legs | PASS | Neutral views retain the accepted waistband, balanced rise/crotch split and two tapered shorts legs. |
| Proportions | FAIL | Front/rear and both walk extremes show the top still substantially overpowering the body and shorts in lateral width. |
| No rejected silhouettes | FAIL | The depth taper is visible in profile, but front/rear and opposing extremes still read as a broad box/poncho torso. |
| No exposure or collision | PASS | All five tapered views retain coverage and the 21-frame ledger reports zero evaluated intersections. |
| Stable opposing extremes | PASS | Frames `6` and `16` retain coverage; root/armature translation is zero and frame `21` equals frame `1`. |

The machine-readable ledger is `tapered_starter_outfit_visual_acceptance.json`. It ties every criterion to exact tapered-view hashes and the retained frame ledger, restricts the verdict to the two allowed states, and rejects when any criterion fails.

## Verification

- Deterministic build/rebuild and `--validate`: PASS; review identity and board hash reproduce.
- Exact 1L.5cg custody and all five retained view hashes: PASS.
- Full frozen native automation: `75/75` PASS, exit `0`, failure markers `0`; log SHA-256 `B419964F15BA6125E677E5F25312BB0BD9E51A7FB84A1AC4907F9BF670A3BF0A`.
- Isolated frozen Python regression: `105/105` PASS in `148.995s` (`9 + 2 + 8 + 46 + 40`), with Phase 1H under the fixed allowlisted Python `3.12.14`.
- Brain Admin self-check: PASS, exit `0`; stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged locomotion, Studio/prompt presentation, camera, listen server and client checks: PASS; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

This is an evidence-only offline review, not an asset change. Because the verdict is rejected, it authorizes no technical export/import preparation. It also makes no runtime replacement, fabric/UV/material/LOD, performance, final-art, Phase 1L exit or beta-readiness claim.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5ch tapered combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5cg Starter Top Central Torso Depth Taper Correction Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
