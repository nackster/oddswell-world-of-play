---
tags:
  - development
  - beta
  - character
  - review
status: complete-review-rejected-visual-correction-required
date: 2026-09-28
---

# Phase 1L.5cl Outer-Span-Corrected Combined Starter-Outfit Offline Visual Acceptance Review

## Outcome

Phase 1L.5cl is complete as an evidence-only review with verdict `REJECTED_VISUAL_CORRECTION_REQUIRED`. The exact custody and numerical geometry gates pass, but the exact retained views fail three unchanged qualitative criteria: neckline/shoulders/sleeves/hem, no rejected silhouettes, and stable opposing extremes. The verdict is derived from the seven criterion statuses rather than fixed in advance.

This rejection stops export/import preparation. It is not an export, import, runtime replacement, final-art approval, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness determination.

## Exact custody

- Source Blend: `13,905,337` bytes, SHA-256 `5A452DCF36B861D4271D6D9CD1303161330C112BCEBD32AF2548F2C2F35161C7`.
- Phase 1L.5ck semantic identity: `BB7BE19929C7C89270CC39D029FBE21D9D8140E57BB2A91B55DE96DCC75F8F18`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Outer-span-corrected top: `4D290EAEF2CDC94F6F68982C0166FF5E7B85C6B36200170FF2B24AFF4F379FBE`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Frame-ledger identity: `26C61ACFE18C84C59836C8EA81D911FA3BC49150859247C3730BB066AF960DC2`.
- Opening-geometry identity: `C90E1A6D9A2F1D9A259281D275EC1922250596BBFE862DC65AC5A8A5EC4D0D95`.
- Opening-boundary identity: `B93835657A71D0088459699AF655B2A329C9AA6C16B5775070A001EE121C171E`.

Geometry, coordinates, weights, topology, materials, action, skeleton, export, Unreal/client files, package inputs and runtime changes are all `0`.

## Unchanged seven-criterion review

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | All `21` retained frames report body/top, body/bottom and top/bottom evaluated intersections `0`. |
| Neckline / shoulders / sleeves / hem | FAIL | The contract and width gate pass, but the exact views show rigid squared shoulder caps, abrupt sleeve blocks and a hem that lifts or folds into disconnected-looking planes at both opposing walk extremes. |
| Waistband / rise / crotch / legs | PASS | Exact accepted connected shorts retain three openings, zero other non-manifold edges and two legs. |
| Proportions | PASS | Neutral top width is `0.944818 m` versus body width `0.675352 m`, ratio `1.399001`. |
| No rejected silhouettes | FAIL | The numeric taper and width gates pass, but the neutral profile remains slab-like and both extremes retain an armor-like, plate-folded top silhouette. |
| No exposure or collision | PASS | All five exact views retain coverage and the frame ledger reports zero evaluated intersections. |
| Stable opposing extremes | FAIL | Mechanical loop and translation checks pass, but frames `6` and `16` do not support qualitative garment stability: shoulder caps rise into plates and the hem collapses unevenly. |

The one smallest next correction is top-only shoulder-cap, sleeve and hem articulation sufficient to produce a continuous garment silhouette without rigid raised plates or hem collapse. Exact custody, accepted width ratio, topology, four openings and every non-target asset remain protected.

## Deterministic evidence

- Review identity: `C45BEE5EEA0A2B709BB0551B9C2CFD2F845F34780EB1FF8AF45663356F777B27`.
- Deterministic board: `1,061,052` bytes, SHA-256 `23A9473E1FED2F920084D508C36AC19FB5B09F05F734B64362DF76C804932623`.
- Exact retained views: front `65B80D7989AFF083B6C7F94235BA57C5EBE22D02DAD3FDE41EC31840C0196CA3`, rear `DB58DB833C78129B41C069EDA1124308FE19E9609ADF637F1AC60A62AF867940`, profile `D6F8C442A8F9D84D198BAF69904FB4A906EDFE2583B6C72C74099A746C216547`, frame-6 extreme `B90A1236DDC0DDF4B100E73A6FF95E9143545433E251179CA7B82487322D7BBD`, frame-16 extreme `9BD4EBD22A593FF1FCFECA429FEB1871F5A0D04E64944011F052CF2357D8F87E`.

## Verification

- Deterministic build and independent validation: PASS; rejection identity `C45B...7B27` and board `23A9...2623` reproduced.
- Full frozen native suite after the fail-closed review repair: PASS, `75/75`, with `0` non-success markers; retained log SHA-256 `E5A34679C36E2B295AB6EC2FF14469966E347FF7359DCB4EC3C0772EAEAF106A`.
- Isolated Python regression after repair: PASS, `105/105` (`9 + 2 + 8 + 46 + 40`) in `167.842 s`.
- Brain Admin self-check: PASS; exact `43`-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion and character-motion markers passed; studio and interaction-prompt-presentation markers passed; camera-orbit passed; shared-city server/client, skeletal appearance and skeletal motion markers passed; every process exited `0` and UDP `17777` was released.
- Retained package audit: `50` files, `1,038,710,362` bytes, `0` Python files. Final process audit found `0` OddsWell, Unreal Editor or Blender processes.

## Boundary and next gate

Export/import preparation is not eligible. The only bounded next correction is top-only shoulder-cap, sleeve and hem articulation while preserving exact custody, the accepted width ratio, topology, four openings and all non-target assets. This review itself changes no asset or runtime input. Fabric, production UVs, LODs, final materials, runtime replacement, performance, hands-on usability, Phase 1L exit and beta readiness remain separate unproven gates.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cl outer-span-corrected combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5ck Outer Shoulder Sleeve Span Correction Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
