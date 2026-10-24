---
tags:
  - development
  - beta
  - character
  - blender
status: complete-targeted-correction-proof
date: 2026-09-28
---

# Phase 1L.5ci Central Front / Rear Lateral Waist-Taper Correction Walk Proof

## Outcome

Phase 1L.5ci applies only the smallest correction named by the Phase 1L.5ch rejection. It derives from exact Phase 1L.5cg custody and changes only central front/rear `starter_offwhite_top` lateral `X` coordinates toward the waist. It issues no acceptance verdict; the next gate must rerun the combined outfit review.

The retained neutral front/rear/profile and opposing walk extremes show a monotonic lateral taper from the preserved upper torso toward the waist. This remains coarse offline technical geometry, not finished clothing.

## Exact custody and coordinate isolation

- Source Phase 1L.5cg semantic identity: `8B8008D832BFB0D1C1753D24AE2AF99C5CAE6CE24B8ED30439438904A0A55A61`.
- Accepted body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source depth-tapered top: `1C7F8649211C44B9039F12902E266C438C5EF6DA4DF224D7FBD1FCF108AEC353`.
- Accepted shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Exact walk action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Derived waist-tapered top: `BB29047CAB30C3071FD6875A789E93CF275C2E2A44997957CFB85DCDD36FD3AB`.
- Derived semantic identity: `38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD`.
- Final Blend: `13,905,337` bytes, SHA-256 `5A9ED444693F30AABE68E55B29C2DA588423ED256BEDE94472FA349D48E1543B`.

Exactly `108/498` top vertices change, and only their `X` coordinate changes. The other `390` vertex coordinates reproduce exactly under source and derived SHA-256 `9436B1815572DD0FBD55ECD596F1B9C03FD59F439E92E8890329D076C5D15DEA`. Every `Y` and `Z` coordinate reproduces exactly under SHA-256 `3DF7DC181777A7ACCCFAE2767A49D12AD89DCC99B2812148A584DD3BA5690FED`. The protected ledger includes every shoulder/sleeve vertex and all `72` exact source opening-boundary vertices. All `48` protected opening-boundary indices inherited from Phase 1L.5cg are present; target/full-opening and target/inherited-opening overlaps are both `0`. Source and derived four-opening geometry are exactly equal. Topology, item/material/color identity and weights remain unchanged.

## Measured taper and walk proof

| Band | Source half-width | Derived half-width | Reduction |
|---|---:|---:|---:|
| Lower | `0.386880010 m` | `0.335717112 m` | `0.051162898 m` |
| Middle | `0.387668341 m` | `0.376908571 m` | `0.010759770 m` |
| Upper | `0.387668371 m` | `0.386879742 m` | `0.000788629 m` |

- Maximum target displacement: `0.051162899 m`.
- Topology: `498` vertices / `464` polygons / one component / exactly four openings / zero other non-manifold edges.
- Normalized spine/upper-arm weights retain unweighted and invalid counts `0`.
- All integer frames `1–21` retain body/top and top/bottom evaluated intersections `0`.
- Sampled body/top minimum separation is `0.033464938 m`; observed maximum is `0.040899202 m`.
- Root and armature translation remain exact zero; frame `21` equals frame `1`.

The `Review/BeforeAfter.html` board pairs exact Phase 1L.5cg front/rear/profile and opposing extremes with the waist-tapered derivative. It is correction evidence only.

## Verification

- Deterministic semantic rebuild: PASS; derived mesh `BB29...D3AB` and identity `38F7...39FD` reproduced across two clean builds.
- Saved-source cold reopen and all custody assertions: PASS.
- Full frozen native automation: `75/75` PASS, exit `0`, failure markers `0`; log SHA-256 `4F7E8FBDE776EBD7E267612EDCEEE0676E51230108A4A223759C98D22C8173EE`.
- Isolated frozen Python regression: `105/105` PASS in `150.608s` (`9 + 2 + 8 + 46 + 40`), with Phase 1H under the fixed allowlisted Python `3.12.14`.
- Brain Admin self-check: PASS, exit `0`; stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged locomotion/character motion, Studio/prompt presentation, camera, listen-server shared city/appearance/motion and client appearance markers: PASS.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

Shoulders, sleeves, accepted `Y` depth taper, every `Z` coordinate, all non-target coordinates, body, shorts, topology, weights, materials, Action, skeleton, Unreal/client files and package inputs remain unchanged. This proof makes no visual-acceptance, export/import, runtime-replacement, fabric/UV/material/LOD, performance, final-art, Phase 1L exit or beta-readiness claim.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5ci central front/rear lateral waist-taper correction walk proof]], [[Development/Reports/Phase 1L5ch Tapered Combined Starter Outfit Offline Visual Acceptance Review]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
