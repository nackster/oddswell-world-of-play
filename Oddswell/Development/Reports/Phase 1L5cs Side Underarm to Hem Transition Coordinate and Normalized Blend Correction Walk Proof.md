---
tags:
  - development
  - beta
  - character
  - clothing
status: complete-targeted-offline-proof
date: 2026-09-30
---

# Phase 1L.5cs Side / Underarm-to-Hem Transition Coordinate and Normalized Blend Correction Walk Proof

## Outcome

Phase 1L.5cs is complete as one targeted offline correction proof. It derives from exact Phase 1L.5cq custody and changes only `starter_offwhite_top`: `48` vertices on a fixed `24`-pair bilateral side/underarm strip change coordinates and normalized weights, while `16` waist-opening vertices on eight declared bilateral pairs change weights only. The measured neutral-profile target depth, frame-6 left target extent, frame-16 right target extent and both extreme-frame hem-height ranges all decrease.

This phase deliberately issues no visual-acceptance verdict. The exact unchanged seven-criterion combined review remains next. Export/import preparation remains stopped; there is no runtime replacement, final-art, Phase 1L exit, beta-readiness, Version 1 readiness or production-readiness claim.

## Exact source custody

- Phase 1L.5cq Blend: `13,907,177` bytes, SHA-256 `A256E5F7B1B0750623A9B9F9B5085A45850AE1E525B0CD32F07447C791568A1E`.
- Phase 1L.5cq semantic identity: `D9ABDAF676F2352EA8629EE4FC375A1F5567830AD5D721093669D942CB91F78A`.
- Body: `F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD`.
- Source top: `EAB37355BDA56874B10BCA2BEE45BD4FDAFAE9F0B7B7826BFDBA85C1BB9807E8`.
- Shorts: `E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170`.
- DEC-035 armature: `12` bones; action: `7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020`.

## Bounded coordinate and weight ledger

- Coordinate target: exactly `48` vertices in `24` predeclared left/right pairs. All `48` change only `X/Y`; their `Z` values remain exact. The other `450` coordinate records reproduce exactly.
- Weight target: exactly `64` vertices. The same `48` side-strip vertices plus `16` paired waist-opening hem anchors receive normalized `spine` plus matching `upper_arm.L` or `upper_arm.R` influence; the other `434` weight records reproduce exactly.
- Coordinate-target overlap with the accepted central depth taper, outer rounded caps, yoke blend and all opening boundaries is `0`. All `48` coordinate targets belong to the accepted waist-taper region, but every move is inward, so outward waist-taper regressions remain `0`.
- The `16` opening-boundary targets change weights only. Opening coordinates, topology, one-component/four-opening identity and zero-other-non-manifold contract remain exact.
- Source/derived target coordinate SHA-256: `C7A1036B5D65F3C7F2834A4DC660B0F1BBC6D42FA9982B03DEBE53CE611EC6E8` / `C6F061650C4EA25B7A3FA3550AFE1AAB23FAE5AA462B7C9BCC87B347ED9E2BD1`.
- Source/derived target weight SHA-256: `E9BA913171CBB73A85A8914BB3B2FAEA0B71B6B1F36F758115CE3E57C0C82E79` / `F61238873D27B7A4221F12F7751ED943FB9CFD188E5BFCE234C173F1DCD37EEB`.
- Maximum coordinate displacement: `0.031072533 m`; maximum influence delta: `0.973717943`.
- Derived top: `AF724E26CA5CEF052FDFC209FE4B26E2F10642B700B907A9BDC519DEA6DD9BD8`.
- Derived semantic identity: `37257F8E8066BD5E1BAD5C6C92884275B8E56B54D73F497775674761F0C21839`.
- Derived Blend: `13,907,409` bytes, SHA-256 `C86ABAA84AB42AF1BA2C402AA2D0B6C3A89B6CFEB8AE54DB8B294463D708A78D`.

Neckline, yoke, rounded sleeve caps, central pattern, accepted central depth coordinates, target `Z`, all non-target coordinates and weights, item/material/color identity, body, shorts, skeleton and action remain exact.

## Named issue metrics

| Measure | Source 1L.5cq | Derived 1L.5cs |
|---|---:|---:|
| neutral-profile target depth span | `0.616801232 m` | `0.584710002 m` |
| frame-6 left target extent | `0.387268066 m` | `0.359232068 m` |
| frame-16 right target extent | `0.387268066 m` | `0.359232068 m` |
| frame-6 waist-hem Z range | `0.016934097 m` | `0.003166914 m` |
| frame-16 waist-hem Z range | `0.016874254 m` | `0.003271818 m` |

These are bounded geometric/deformation reductions, not a qualitative acceptance verdict. The retained five before/after views remain subject to the separate unchanged combined review.

## Walk proof

- Top width remains `0.930000007 m`; against body width `0.675352 m`, ratio remains `1.377059677`.
- The top remains `498` vertices / `464` polygons, one connected component, exactly four openings and zero other non-manifold edges. Accepted shorts remain one component with three openings and zero other non-manifold edges.
- Every integer frame `1–21` reports body/top, body/bottom and top/bottom evaluated intersections `0`.
- Minimum sampled body/garment clearance is `0.015969807 m`.
- Root-bone and armature translations remain exact zero on every frame; frame `21` equals frame `1`.

## Review evidence

Five direct before/after views are retained: neutral front, rear and profile plus frames `6` and `16`. After-view SHA-256 receipts are front `3EBB2D0866BAD2AF4455573AEA1B75ECA12F4028F07D550567FD53726112DC76`, rear `7C11D975B07350D46FEF48E49905ECC3646637240EC311E6D9EA557D117007E1`, profile `0B9A7782DD79E08D0DEEE7993C565833EE0679A95760EEE79E34DCA0C163B834`, frame-6 extreme `147D85ED64CA89BD3F82165CEADB6047C7653FA4142123F96C54E5918A05B0B0` and frame-16 extreme `59AC0AC041D159F130ADC8D09348D05149B8D48DD07D45D3206F71C060FC53BA`.

## Verification

- Two deterministic builds and fresh cold-open validation: PASS; semantic identity `3725...1839`, top `AF72...9BD8` and ratio `1.377059677` reproduce.
- Full frozen native suite: PASS, `75/75`, zero non-success results; log SHA-256 `3C9676B079FB856E11E45A66D50ED50FFAAFDE0B3C2D425B6CD0E7E35BD81333`.
- Isolated Python regression: PASS, `105/105` (`9` Phase 0A, `2` Phase 0B, `8` Phase 0C, `46` Phase 0D and `40` Phase 1H) in `211.999 s`; log SHA-256 `CCA44BE75DC0F660094D114CB1A966CCA97B24A46622E7ABACE6B5BFC78C66F8`.
- Brain Admin self-check: PASS; exact `43`-byte output SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44`.
- Retained packaged Windows verification: PASS. Locomotion, character motion, Studio, interaction-prompt presentation, camera orbit and local server/client shared-city skeletal appearance/motion checks emitted their required PASS markers and exited `0`. Evidence-log SHA-256 receipts: locomotion `93F25977E9E24C342E4342CA6D7B0C2A2EE0D8991745254969971D54E79EFFE2`, Studio `877B4DF67F54C753CE34571E489DD649403249E8DF9B526E042D601E049D1E8`, camera `C3FAEB86DB13306612F3F10812627D47EBF0C3AAFEAE723617D236AF17DBE6FA`, client `5AA18AA39D9F5355346BB67C73C4AE6B4EB7C8098886BABD5BA489345F5113D`, server `AE4D9D3D40BEB695BF77C18FFB46DD028973596402E0A2692B14F7CFD3EF796`.
- Retained package audit: `50` files / `1,038,710,362` bytes / zero Python files. Final process audit found zero OddsWell, Unreal Editor, AutomationTool or CrashReportClient processes, and UDP port `17777` was free.

## Boundary and next gate

The exact unchanged seven-criterion combined outfit review must run next against this custody. Export/import preparation remains stopped. No runtime input, authority boundary, final-art or readiness claim changes here.

See [[Design/Beta Game Bible#Player character]], [[Development/Beta Delivery Roadmap#Phase 1L.5cs side underarm-to-hem transition coordinate and normalized blend correction walk proof]], [[Development/Reports/Phase 1L5cr Yoke Blended Combined Starter Outfit Offline Visual Acceptance Review]], [[Development/Reports/Phase 1L5cq Yoke to Cap Transition and Normalized Blend Correction Walk Proof]], and [[Design/Decisions/DEC-035 Character Unreal Bone Name Mapping]].
