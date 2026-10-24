---
tags:
  - development
  - beta
  - character
  - blender
status: complete-targeted-correction-proof
date: 2026-09-28
---

# Phase 1L.5cg Starter-Top Central Torso-Depth Taper Correction Walk Proof

## Outcome

Phase 1L.5cg applies only the smallest correction named by the Phase 1L.5cf rejection. It derives from exact Phase 1L.5ce custody and changes only central front/rear `starter_offwhite_top` depth coordinates. It issues no acceptance verdict; the corrected combined review remains a separate gate.

The retained before/after neutral front/rear/profile and opposing walk extremes show a more tapered torso-depth profile. This remains coarse offline technical geometry, not finished clothing.

## Exact custody and coordinate isolation

- Source Phase 1L.5ce semantic identity: `7F5D0C4606DF10318372771F7D431AC3884B7858F5304BB22D198BC63301F220`.
- Accepted body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source corrected top: `A9DD780C47AC50F1383BA23F4393167E0EC51C62616D868E421C5CD5C3CAAADB`.
- Accepted shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- Exact walk action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.
- Derived tapered top: `1C7F8649211C44B9039F12902E266C438C5EF6DA4DF224D7FBD1FCF108AEC353`.
- Derived semantic identity: `8B8008D832BFB0D1C1753D24AE2AF99C5CAE6CE24B8ED30439438904A0A55A61`.
- Final Blend: `13,905,337` bytes, SHA-256 `4AE2F2B1E695F1DA7D09EB8D7F862CBADCFEB93D35413326A854A15169F03C35`.

Exactly `114/498` top vertices change, and only their `Y` depth coordinate changes. The other `384` vertex coordinates reproduce exactly under source and derived SHA-256 `15D1B3A270C88170053DB0D51AAB9364E47F552B54A53619B19C22339D7F399E`. The protected ledger includes all `312` prior shoulder/sleeve/side targets and all `48` opening-boundary indices; target/protected overlap is `0`. Topology, four openings, item/material/color identity and weights reproduce exactly.

## Measured taper and walk proof

- Mean depth reduction: lower torso `0.020377081 m`, middle torso `0.006175698 m`, upper torso `0.017112179 m`.
- Maximum target displacement: `0.028001666 m`.
- Topology: `498` vertices / `464` polygons / one component / exactly four openings / zero other non-manifold edges.
- Normalized spine/upper-arm weights retain unweighted and invalid counts `0`.
- All integer frames `1–21` retain body/top and top/bottom evaluated intersections `0`.
- Sampled body/top minimum separation is `0.033464938 m`; observed maximum is `0.045855120 m`.
- Root and armature translation remain exact zero; frame `21` equals frame `1`.

The `Review/BeforeAfter.html` board pairs exact Phase 1L.5ce front/rear/profile and opposing extremes with the tapered derivative. It is correction evidence only.

## Verification

- Deterministic semantic rebuild: PASS; identity `8B80...5A61` reproduced.
- Saved-source cold reopen and all custody assertions: PASS.
- Full frozen native automation: `75/75` PASS, exit `0`, failure markers `0`; log SHA-256 `5CE1ACFA5016C21F5496B8C111C4A6F6C9F1F2C36DFC47C8331BCA996DB7F960`.
- Accepted isolated Python regression: `105/105` PASS in `154.903s` (`9 + 2 + 8 + 46 + 40`). Phase 1H used the fixed allowlisted Python `3.12.14`; a preliminary Python `3.13` Phase 1H diagnostic was rejected by the existing interpreter allowlist and earns no credit.
- Brain Admin self-check: PASS, exit `0`; stdout SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged locomotion, Studio/prompt presentation, camera, listen server and client checks: PASS; final marker `ODDSWELL_PACKAGED_CHARACTER_PASS`.
- Retained package remains `50` files / `1,038,710,362` bytes / Python files `0`.

## Boundary

Corrected shoulders, sleeves and sides plus all openings, body, shorts, topology, weights, materials, Action, skeleton, Unreal/client files and package inputs remain unchanged. This proof makes no visual-acceptance, export/import, runtime-replacement, fabric/UV/material/LOD, performance, final-art, Phase 1L exit or beta-readiness claim.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cg starter-top central torso-depth taper correction walk proof]], [[Development/Reports/Phase 1L5cf Corrected Combined Starter Outfit Offline Visual Acceptance Review]], [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
