---
tags:
  - development
  - beta
  - character
  - clothing
status: complete-targeted-offline-proof
date: 2026-09-29
---

# Phase 1L.5co Outer Sleeve / Armhole Rounded-Cap Correction Walk Proof

## Outcome

Phase 1L.5co is complete as one targeted offline correction proof. It derives from exact Phase 1L.5cm custody and changes only top source coordinates satisfying `|X| >= 0.389245 m` and `1.20 m <= Z <= 1.40 m`. The correction draws the outer sleeve and armhole blocks into continuous rounded caps while retaining the accepted articulation weights.

This phase deliberately issues no visual-acceptance verdict. The unchanged seven-criterion combined review remains the next gate. Export/import preparation remains stopped; there is no runtime replacement, final-art, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness claim.

## Exact source custody

- Phase 1L.5cm Blend: `13,907,177` bytes, SHA-256 `10315DEC1E2F1EAB3F3D7DDA6828AB5B9867957B9D108C5A2F462201D3E059FC`.
- Phase 1L.5cm semantic identity: `6E219986ED018BFF27BB61AD308346C33217795B5C883893806E661D589579B0`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source articulated top: `9ED01AAA3F060F237D2CCADCD5ED7E15F65E864F013DC0BCB51266A31A34FA58`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.

## Explicit coordinate and weight ledger

- Approved source-coordinate target: `155` vertices matching the exact `|X|`/`Z` bounds; `130` change after the rounded-cap function.
- Protected coordinates: all other `343` vertices, reproduced exactly. Target/protected overlap is `0`.
- Maximum changed-coordinate displacement: `0.064228857 m`.
- All articulation weights reproduce exactly; weight changes are `0`.
- Torso, depth taper, waist taper, waist boundary, neckline boundary, topology, item/material/color identity, body, shorts, skeleton and action remain protected.
- Derived top: `519C4F12ADB179FDA71E1E11B043798018FF344369CCB1AE5799A7040DEF4C47`.
- Derived semantic identity: `2384397B3BAB50C3CC01222F8EE9EDE598A430444FC7FEC3C233CA46272CD07A`.
- Derived Blend: `13,907,177` bytes, SHA-256 `7EF2728BF1F091FF5A4DEF57815CCF7159DCE21A19528AA5595E848B07139363`.

## Arm-opening boundary disclosure

The approved coordinate target contains `21` arm-opening boundary vertices; `20` change and the exact threshold vertex remains unchanged. Their indices are `2, 3, 4, 5, 104, 105, 115, 116, 125, 126, 135, 137, 154, 155, 328, 329, 346, 347, 358, 375, 379`.

- Source targeted arm-opening coordinates: SHA-256 `EE73376E4A878AB4FE5F3F5648BA65BD7C9DFBB5516E692CC680E279CAA6012F`.
- Derived targeted arm-opening coordinates: SHA-256 `B2A64A744121CFC38298563FE4336847FF5B62FDBE18690F03AB571E8FB04BA2`.
- All `48` waist/neckline boundary vertices are protected exactly with target overlap `0`.
- The top remains one connected component with exactly four openings and zero other non-manifold edges. Accepted shorts remain one component with three openings and zero other non-manifold edges.

## Measured walk proof

- Top width changes from `0.944817424 m` to `0.930000007 m`; against body width `0.675352 m`, the ratio is `1.377059677`, below the unchanged `1.4` ceiling.
- Every integer frame `1–21` reports body/top, body/bottom and top/bottom evaluated intersections `0`.
- Minimum sampled body/garment clearance is `0.018486369 m`; the bounded-clearance ceiling remains satisfied.
- Root-bone and armature translations remain exact zero on every frame; frame `21` equals frame `1`.
- Retained frame-ledger identity: `4DE37C1F83A7E0EAB04E3943DBE3CBB9CDE52FA0AFA242105D54D18D3CC6927C`.

## Review evidence

Direct before/after neutral front, rear and profile views plus opposing walk extremes are retained. The after-view SHA-256 receipts are front `9B5DB761457F598E8C4E2BC57C210A38D50E1836384528C14F0860BC69AC0BD5`, rear `78CD9CEC3E6D8257380FFCEBCD2792FBD38BE3013A3F8A4DBEFDD1D82E7DA9E6`, profile `DF3C3CF0634AC997E13DC24670F164D92EE76DFBD855A8D6151272CAEDA9CA14`, frame-6 extreme `3182394B2DF865502D688B33F51098CB9DF773FBD961C926DC61BA945B22816F` and frame-16 extreme `763CF6EC0E838EE703E5ECD7BDF848290EA47194AEA9D8AC66DA4644C30693EE`.

These views prove only the bounded correction and retained deformation. They do not constitute the next combined visual-acceptance verdict.

## Verification

- Deterministic build and cold-open validation: PASS; semantic identity `2384...D07A`, derived top `519C...4C47` and ratio `1.377059677` reproduce.
- Full frozen native suite: PASS, `75/75`, with `0` non-success markers; retained log SHA-256 `548D73BDFC0A58F2D5400B6EEC07890EBFCD10DD03034372AEE98FE92432D169`.
- Isolated Python regression: PASS, `105/105` (`9 + 2 + 8 + 46 + 40`) in `168.162 s` of reported test time.
- Brain Admin self-check: PASS; exact `43`-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion and character-motion markers passed; Studio and interaction-prompt-presentation markers passed; camera-orbit passed; shared-city server/client, skeletal appearance and skeletal motion markers passed. All processes emitted exit-status `0`, and UDP `17777` was released. Log hashes: locomotion `FED1C0478890A222C97C065E1D6D3BD5D5A0558961F1BDDC7843126472CE21B7`, Studio `9880D9B866407111BFFEC73D78D9469ED67E65CDDC70437CB0CCAEBD64484DCA`, camera `7A419ED46218AA5A8614FADE1DEED05E8E3440C389DF4CCFA438F26BEC5EFC8D`, server `84E69DF21EB9B508185FDDCD61EE339C23AC47A58A94F7FD0DD921CFA17AC0B1`, client `3398301DD399B666BD86501DCABF005C1B9EC09B55A360289DE2DD78CCC27BFB`.
- Retained package audit: `50` files, `1,038,710,362` bytes, `0` Python files. Final process audit found `0` OddsWell, Unreal Editor or Blender processes.

## Boundary and next gate

The exact unchanged seven-criterion combined outfit review must run next against this custody. Export/import preparation remains stopped. No geometry outside the approved coordinate ledger, articulation weight, runtime input or authority boundary changes here.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5co outer sleeve armhole rounded-cap correction walk proof]], [[Development/Reports/Phase 1L5cn Articulated Combined Starter Outfit Offline Visual Acceptance Review]], [[Development/Reports/Phase 1L5cm Shoulder Cap Sleeve Hem Articulation Correction Walk Proof]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
