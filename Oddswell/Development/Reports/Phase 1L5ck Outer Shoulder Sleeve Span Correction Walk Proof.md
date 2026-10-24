---
tags:
  - development
  - beta
  - character
  - blender
status: complete-targeted-correction-proof
date: 2026-09-28
---

# Phase 1L.5ck Outer Shoulder / Sleeve-Span Correction Walk Proof

## Outcome

Phase 1L.5ck applies only the one smallest measured correction named by the Phase 1L.5cj rejection. It derives from exact repaired Phase 1L.5ci custody and uniformly reduces only `starter_offwhite_top` outer shoulder/sleeve `X` coordinates beyond `|X| = 0.40 m`.

The neutral top/body width ratio falls from `1.481894083` to `1.398999964`, satisfying the `≤1.4` measured gate with float-safe margin. This phase issues no visual-acceptance verdict; the unchanged combined-outfit review must run again.

## Exact custody and coordinate isolation

- Source Phase 1L.5ci semantic identity: `38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD`.
- Accepted body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source waist-tapered top: `BB29047CAB30C3071FD6875A789E93CF275C2E2A44997957CFB85DCDD36FD3AB`.
- Accepted shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Exact walk action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Derived outer-span-corrected top: `4D290EAEF2CDC94F6F68982C0166FF5E7B85C6B36200170FF2B24AFF4F379FBE`.
- Derived semantic identity: `BB7BE19929C7C89270CC39D029FBE21D9D8140E57BB2A91B55DE96DCC75F8F18`.
- Final Blend: `13,905,337` bytes, SHA-256 `5A452DCF36B861D4271D6D9CD1303161330C112BCEBD32AF2548F2C2F35161C7`.

Exactly `152/498` top vertices change, and only their `X` coordinate changes. The other `346` vertex coordinates reproduce exactly under source and derived SHA-256 `F470A8D6AE7B0F22073DA1978EE737770BD05A8C4636D7840685F0EFFF5ACED8`. Every `Y` and `Z` coordinate reproduces exactly under SHA-256 `3DF7DC181777A7ACCCFAE2767A49D12AD89DCC99B2812148A584DD3BA5690FED`. Target/protected overlap, target/depth-taper overlap and target/waist-taper overlap are all `0`.

## Measured span and opening disclosure

- Body width: `0.675352000 m`.
- Source top width: `1.000800133 m`; ratio `1.481894083`.
- Derived top width: `0.944817424 m`; ratio `1.398999964`.
- Uniform target `X` scale: `0.944062073`.
- Maximum target displacement: `0.027991354 m`.
- Exactly `18` source opening-boundary vertices are targeted.
- Left arm opening changes from outer `X = -0.500400` to `-0.472409 m`; right arm opening changes from outer `X = 0.498035` to `0.470176 m`.
- Waist and neckline opening geometry remain exact.
- Topology remains `498` vertices / `464` polygons / one component / exactly four openings / zero other non-manifold edges.
- Item/material/color identity and normalized spine/upper-arm weights remain unchanged.

This is a truthful arm-opening geometry change within the unchanged four-opening contract, not an exact-opening-geometry claim.

## Walk proof and views

- All integer frames `1–21` retain body/top and top/bottom evaluated intersections `0`.
- Sampled body/top minimum separation remains `0.033464938 m`.
- Root and armature translation remain exact zero; frame `21` equals frame `1`.
- Direct before/after neutral front/rear/profile and opposing frames `6`/`16` are retained.
- After-view hashes: front `65B80D7989AFF083B6C7F94235BA57C5EBE22D02DAD3FDE41EC31840C0196CA3`, rear `DB58DB833C78129B41C069EDA1124308FE19E9609ADF637F1AC60A62AF867940`, profile `D6F8C442A8F9D84D198BAF69904FB4A906EDFE2583B6C72C74099A746C216547`, frame-6 extreme `B90A1236DDC0DDF4B100E73A6FF95E9143545433E251179CA7B82487322D7BBD`, frame-16 extreme `9BD4EBD22A593FF1FCFECA429FEB1871F5A0D04E64944011F052CF2357D8F87E`.
- Before/after board identity: `5B5536374D4CA62080A3614722E386642664DF99B328ACBD01665ECAE96346A3`.

## Verification

- Deterministic semantic rebuild and cold saved-source replay: PASS; identity `BB7B...8F18` reproduced.
- Full frozen native automation: `75/75` PASS, non-success results `0`, log SHA-256 `2862F27B0A335C63E0D693D694226026EED9614199715B4AE61BAB6D3CFF4FEB`.
- Isolated frozen Python regression: `105/105` PASS in `120.598s` (`9 + 2 + 8 + 46 + 40`), with Phase 1H under the fixed allowlisted Python `3.12.14`.
- Brain Admin self-check: PASS, exit `0`; 43-byte stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged locomotion/character motion, Studio/prompt presentation, camera, listen-server shared city/appearance/motion and client appearance markers: PASS.
- Retained package: `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

Accepted central depth and waist tapers, every `Y`/`Z` coordinate, every non-target coordinate, body, shorts, topology, four-opening contract, item/material/color identity, weights, DEC-035, action, Unreal/client files and package inputs remain unchanged. This proof makes no visual-acceptance, export/import, runtime-replacement, final-art, performance, Phase 1L exit or beta-readiness claim.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5ck outer shoulder/sleeve-span correction walk proof]], [[Development/Reports/Phase 1L5cj Waist Tapered Combined Starter Outfit Offline Visual Acceptance Review]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
