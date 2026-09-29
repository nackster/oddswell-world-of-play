---
tags:
  - development
  - beta
  - character
  - correction
status: complete-targeted-offline-proof
date: 2026-09-29
---

# Phase 1L.5cm Shoulder-Cap / Sleeve / Hem Articulation Correction Walk Proof

## Outcome

Phase 1L.5cm is complete as a targeted offline correction proof. It derives additively from exact Phase 1L.5ck custody and changes only selected `starter_offwhite_top` coordinates and normalized spine/upper-arm weights. The retained neutral and opposing-extreme views no longer show the large raised shoulder plates or the earlier uneven hem collapse. This proof deliberately issues no visual-acceptance verdict; the exact unchanged combined review must run next.

Export/import preparation remains stopped. This phase is not runtime integration, final art, Phase 1L exit, beta readiness, Version 1 readiness or production readiness.

## Exact source custody

- Source Blend: `13,905,337` bytes, SHA-256 `5A452DCF36B861D4271D6D9CD1303161330C112BCEBD32AF2548F2C2F35161C7`.
- Source semantic identity: `BB7BE19929C7C89270CC39D029FBE21D9D8140E57BB2A91B55DE96DCC75F8F18`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source top: `4D290EAEF2CDC94F6F68982C0166FF5E7B85C6B36200170FF2B24AFF4F379FBE`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.

## Bounded correction ledger

- Derived top: `9ED01AAA3F060F237D2CCADCD5ED7E15F65E864F013DC0BCB51266A31A34FA58`.
- Derived semantic identity: `6E219986ED018BFF27BB61AD308346C33217795B5C883893806E661D589579B0`.
- Derived Blend: `13,907,177` bytes, SHA-256 `47028E717DEFFD5CE3D90BBE8F06DAB7B1957B6D49DA53CC714632011E1AD80B`.
- Coordinate target: `113` outer cap/sleeve vertices; protected coordinates: `385`; target/protected overlap: `0`.
- Weight target: `268` shoulder/sleeve/hem vertices; protected weights: `230`; target/protected overlap: `0`.
- Central depth- and waist-taper coordinate overlap: `0`; every non-target coordinate and weight reproduces exactly.
- Maximum targeted coordinate displacement: `0.098202807 m`.
- Top/body width ratio remains `1.398999964`, below the unchanged `1.400000` ceiling.
- Item identity, material/color, body, shorts, topology, four-opening contract, skeleton and action remain unchanged.

## Walk proof and visual evidence

- All integer frames `1–21` retain body/top, body/bottom and top/bottom evaluated intersections `0`.
- Minimum sampled body/top clearance is `0.021611767 m`; minimum body/bottom clearance is `0.018486369 m`.
- Root-bone and armature translations remain exact zero; frame `21` equals frame `1`.
- Direct before/after evidence retains neutral front/rear/profile plus frames `6` and `16`. The corrected extremes keep the shoulder line near the neutral silhouette and keep the lower hem substantially level instead of lifting into the prior rigid plates and collapsed planes.
- One connected top, four intentional openings and zero other non-manifold edges remain proven.

## Verification

- Deterministic build and fresh cold-open validation: PASS; identity `6E21...79B0` reproduced.
- Full frozen native suite: PASS, `75/75`, with `0` non-success results; log SHA-256 `7FFA6480DBF3D88F0463C8ED5538A92299A48E12E304E9F6202439BDD942C0DA`.
- Isolated Python regression: PASS, `105/105` (`9 + 2 + 8 + 46 + 40`) in `167.421 s`.
- Brain Admin self-check: PASS; exact `43`-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion and character-motion markers passed; studio and interaction-prompt-presentation markers passed; camera-orbit passed; shared-city server/client, skeletal appearance and skeletal motion markers passed; every process exited `0` and UDP `17777` was released.
- Retained package audit: `50` files, `1,038,710,362` bytes, `0` Python files. Final process audit found `0` OddsWell, Unreal Editor or Blender processes.

## Boundary and next gate

The next gate is the exact unchanged fail-closed combined outfit review. Phase 1L.5cm does not provide a visual-acceptance verdict and does not make export/import preparation eligible.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cm shoulder-cap sleeve and hem articulation correction walk proof]], [[Development/Reports/Phase 1L5cl Outer Span Corrected Combined Starter Outfit Offline Visual Acceptance Review]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
