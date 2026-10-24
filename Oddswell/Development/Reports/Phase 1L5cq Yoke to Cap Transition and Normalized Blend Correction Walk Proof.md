---
tags:
  - development
  - beta
  - character
  - clothing
status: complete-targeted-offline-proof
date: 2026-09-29
---

# Phase 1L.5cq Yoke-to-Cap Transition and Normalized Blend Correction Walk Proof

## Outcome

Phase 1L.5cq is complete as one targeted offline correction proof. It derives from exact Phase 1L.5co custody and changes only coordinates and normalized `spine`/matching `upper_arm` weights on source vertices satisfying `0.24 m <= |X| < 0.389245 m` and `1.38 m <= Z <= 1.56 m`. No vertex group is added and every corrected weight sum remains `1`.

This phase deliberately issues no visual-acceptance verdict. The unchanged seven-criterion combined review remains next. Export/import preparation remains stopped; there is no runtime replacement, final-art, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness claim.

## Exact source custody

- Phase 1L.5co Blend: `13,907,177` bytes, SHA-256 `7EF2728BF1F091FF5A4DEF57815CCF7159DCE21A19528AA5595E848B07139363`.
- Phase 1L.5co semantic identity: `2384397B3BAB50C3CC01222F8EE9EDE598A430444FC7FEC3C233CA46272CD07A`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source rounded-cap top: `519C4F12ADB179FDA71E1E11B043798018FF344369CCB1AE5799A7040DEF4C47`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.

## Explicit coordinate and weight ledger

- Target: exactly `66` source-window vertices; all `66` coordinates and all `66` normalized weight records change.
- Protected: all other `432` coordinates and weight records reproduce exactly. Target/protected overlap is `0`.
- Target overlap with accepted depth taper, waist taper, outer rounded-cap and all opening-boundary vertices is `0`.
- No vertex group is added. Every target has only `spine` plus the matching `upper_arm.L` or `upper_arm.R`, with sum `1`.
- Source target-coordinate SHA-256: `B2301C394B430D82B5C73C84953998B9643C2769C201B56500277F64E6AB69B9`; derived: `0141340706F60B94554B8AE77269D91FC4455758331D29708C09C94E1389CC63`.
- Source target-weight SHA-256: `3403BAB3296723D1BFE058F5F0B1D3235410FC1745D43D963CD6E859FBD61F48`; derived: `B1FE3A2957DFBDE92F404B7021F00498FBA4D2C12F78BEF005B043E5317FCEF1`.
- Maximum coordinate displacement: `0.029610131 m`; maximum influence delta: `0.014341176`.
- Derived top: `EAB37355BDA56874B10BCA2BEE45BD4FDAFAE9F0B7B7826BFDBA85C1BB9807E8`.
- Derived semantic identity: `D9ABDAF676F2352EA8629EE4FC375A1F5567830AD5D721093669D942CB91F78A`.
- Derived Blend: `13,907,177` bytes, SHA-256 `A256E5F7B1B0750623A9B9F9B5085A45850AE1E525B0CD32F07447C791568A1E`.

Torso/depth/waist taper coordinates, waist and neckline boundaries, accepted outer caps/openings, topology, item/material/color identity, body, shorts, skeleton and action remain exact.

## Measured walk proof

- Top width remains exactly `0.930000007 m`; against body width `0.675352 m`, ratio remains exactly `1.377059677`.
- The top remains one connected component with exactly four openings and zero other non-manifold edges. Accepted shorts remain one component with three openings and zero other non-manifold edges.
- Every integer frame `1–21` reports body/top, body/bottom and top/bottom evaluated intersections `0`.
- Minimum sampled body/garment clearance remains `0.018486369 m`.
- Root-bone and armature translations remain exact zero on every frame; frame `21` equals frame `1`.
- Retained frame-ledger identity: `4DE37C1F83A7E0EAB04E3943DBE3CBB9CDE52FA0AFA242105D54D18D3CC6927C`.

## Review evidence

Direct before/after neutral front, rear and profile views plus opposing walk extremes are retained. After-view SHA-256 receipts are front `33FD17FD1A3FC8DF4E6A8EFC888B124AA4B9B44283BA67ADDCD159809FF0B0C2`, rear `C235759869446145DC3197FAF8F43BE4C66CBECE9647D09C4886BB6FB3C2F81B`, profile `1A43404BB5C4C87F702E83E4066A0009A5FBF9CC2CC3B818C0F5CA4C4F2832F5`, frame-6 extreme `74FCAC96B2EE845DC6B22694887F2F30A6AE78B69634EC8126D9040B1902DDC4` and frame-16 extreme `0EA6A6088897CAC14394B74D720DDF2EC1F178E27CE402C8B8D266FBF18F8B19`.

These views prove only the bounded correction and retained deformation. They do not constitute the next combined visual-acceptance verdict.

## Verification

- Deterministic build and cold-open validation: PASS; semantic identity `D9AB...F78A`, derived top `EAB3...07E8` and ratio `1.377059677` reproduce.
- Full frozen native suite: PASS, `75/75`, zero non-success results; log SHA-256 `243C948582461C67D9246BD56FCF93E6DF14290ED3CC4A5C05AF022EBFEB0EFA`.
- Isolated Python regression: PASS, `105/105` (`9` Phase 0A, `2` Phase 0B, `8` Phase 0C, `46` Phase 0D and `40` Phase 1H) in `168.294 s`.
- Brain Admin self-check: PASS; exact `43`-byte output SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion plus character motion, studio plus interaction-prompt presentation, camera orbit and the local server/client shared-city skeletal appearance/motion checks all emitted their required PASS markers and exited `0`. Log SHA-256 receipts are locomotion `0F64CAB710F834EC5D4FFEEF40467B8771786F126A1AD3E48576DF5F9A4D92D8`, studio `9B6B849A946FE28DBF797EC53624A5834E1A3D6207D42A4054B57D7916F96812`, camera `2C33C1A82E1A22175865DDA2EBCC166F93EF6ECE3D87D6EA3415ED4A84CC3575`, server `483C7B3D8B48BB2F222BEB1E1559EF33163A8166A37F1B4C52583ED584F6C055` and client `5A9A04AEE7F95E50604F86DD1ECA54C2B285ABF2D35B3AB0749866BD01371A89`.
- Package/process audit: retained package remains `50` files / `1,038,710,362` bytes / zero Python files; packaged executable SHA-256 `87399C0938F0B4EAA9F076E9E7406F42CFAEC2A7D4891FEE74D99599B864A071`. After verification there are zero `OddsWell`, `UnrealEditor-Cmd`, `UnrealEditor` or `blender` processes and UDP port `17777` is free.

## Boundary and next gate

The exact unchanged seven-criterion combined outfit review must run next against this custody. Export/import preparation remains stopped. No coordinate or weight outside the approved source window, runtime input or authority boundary changes here.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cq yoke-to-cap transition and normalized blend correction walk proof]], [[Development/Reports/Phase 1L5cp Rounded Cap Combined Starter Outfit Offline Visual Acceptance Review]], [[Development/Reports/Phase 1L5co Outer Sleeve Armhole Rounded Cap Correction Walk Proof]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
