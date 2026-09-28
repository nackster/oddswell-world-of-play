---
tags:
  - development
  - beta
  - character
  - review
status: complete-review-rejected
date: 2026-09-28
---

# Phase 1L.5cj Waist-Tapered Combined Starter-Outfit Offline Visual Acceptance Review

## Outcome

Phase 1L.5cj is complete as an evidence-only review with verdict `REJECTED_VISUAL_CORRECTION_REQUIRED`. It changes no asset or runtime input. The exact repaired Phase 1L.5ci custody, five views, opening identities and 21-frame ledger are retained.

The unchanged seven criteria pass separation, shorts construction, no exposure/collision and stable opposing extremes. They fail neckline/shoulder/sleeve/hem continuity, proportions and no rejected silhouettes. The waist inset now passes its measured floor, but the preserved outer shoulder/sleeve span remains too broad relative to the body.

## Exact custody

- Source Blend: `13,905,337` bytes, SHA-256 `5A9ED444693F30AABE68E55B29C2DA588423ED256BEDE94472FA349D48E1543B`.
- Phase 1L.5ci semantic identity: `38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Waist-tapered top: `BB29047CAB30C3071FD6875A789E93CF275C2E2A44997957CFB85DCDD36FD3AB`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Frame-ledger identity: `41DFFB238D49EB5675FD9F1EAFC49F5731826E14685F7CC1D8BE1DC47E06BD0E`.
- Opening-geometry identity: `94A266B45D30762DC5B000230D7F2897C01D128F7206597372A629CB96D55FD3`.
- Opening-boundary identity: `B93835657A71D0088459699AF655B2A329C9AA6C16B5775070A001EE121C171E`.

Geometry, coordinates, weights, topology, materials, action, skeleton, export, Unreal/client files, package inputs and runtime changes are all `0`.

## Unchanged seven-criterion review

| Criterion | Result | Evidence |
|---|---|---|
| Separation | PASS | All `21` retained frames report body/top, body/bottom and top/bottom evaluated intersections `0`. |
| Neckline / shoulders / sleeves / hem | FAIL | The connected four-opening contract and all named roles remain intact, but outer width ratio is `1.481894` against the `1.400000` review ceiling. |
| Waistband / rise / crotch / legs | PASS | Exact accepted connected shorts retain three openings, zero other non-manifold edges and two legs. |
| Proportions | FAIL | Neutral top width is `1.000800 m` versus body width `0.675352 m`, ratio `1.481894`. |
| No rejected silhouettes | FAIL | Waist inset ratio `0.132244` passes the `0.080000` floor, but neutral and opposing extremes retain the broad box/poncho outer span. |
| No exposure or collision | PASS | All exact views retain coverage and the retained frame ledger reports zero evaluated intersections. |
| Stable opposing extremes | PASS | Frames `6` and `16` retain coverage, translations remain zero and frame `21` equals frame `1`. |

The verdict is derived from these seven statuses. It is not hard-coded.

## Deterministic evidence

- Review identity: `EA35D9D160E659D8494D5C2A34ED883504EE030DA0D6F4F3881E2303ECB613BD`.
- Deterministic board: `1,066,720` bytes, SHA-256 `803EA49B3D04211B909A3CA6F7A31C1E2CF4E05EA093AF1FF41FA7049E33FF25`.
- Exact retained views: front `101526459A07C42F0D667AF3218A824C529F2B6B15F1D970CAD6EEDD3614A90E`, rear `D977D324212D412D81A5EAA0C13224CA6214B94D56FA4401341D5E6A73FF8FC8`, profile `331A4B76808A77FCC342BE97C187A72D281269B27F6981ED51B3C23E2F31F4ED`, frame-6 extreme `C04573ACA61AAF3C7667ACB3C628BF18C119341D76175D5E038F0E321CF63C7A`, frame-16 extreme `30C5068E86E58C3D10E182160646C230C4C9563F74BB963B4EBB804361FF2942`.

## Smallest next correction and boundary

Exactly one smallest measured correction is named: reduce only the preserved outer shoulder/sleeve span, currently `1.000800 m` versus `0.675352 m` body width (`1.481894×`, above the `1.400000×` review ceiling), while preserving the central depth/waist taper and every non-target identity.

Export/import preparation remains stopped. This review makes no runtime, final-art, performance, Phase 1L exit, beta-readiness, Version 1 or production-readiness claim.

## Verification

- Deterministic build and independent validation: PASS; identity `EA35...13BD` and board `803E...FF25` reproduced.
- Full frozen native automation: `75/75` PASS, non-success results `0`, log SHA-256 `CFEF4130F0FB3F08386EBE851F10C7A96EBBB4293FFABCF177EC7AF970911563`.
- Isolated frozen Python regression: `105/105` PASS in `147.610s` (`9 + 2 + 8 + 46 + 40`), with Phase 1H under the fixed allowlisted Python `3.12.14`.
- Brain Admin self-check: PASS, exit `0`; 43-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged locomotion/character motion, Studio/prompt presentation, camera, listen-server shared city/appearance/motion and client appearance markers: PASS.
- Retained package: `50` files / `1,038,710,362` bytes / Python files `0`.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cj waist-tapered combined starter-outfit offline visual acceptance review]], [[Development/Reports/Phase 1L5ci Central Front Rear Lateral Waist Taper Correction Walk Proof]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
