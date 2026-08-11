# Phase 1L.3h — Sundale Shared Material-Family Review Board

Date: 2026-08-11
Branch: agent/phase-0d
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW — OWNER ACCEPTANCE AND SEPARATE PRODUCTION PROMOTION/EXPANSION PENDING**
Cost: $0.00

Canonical source identity is frozen at `38,794` bytes and SHA-256 `28F4433ED68B49D5B5AE8CF686E3A9A64B550D96029FCF344A577F24DF8BA09B`; the manifest records that exact identity.

## Outcome first

One deterministic Blender 4.5.5 LTS builder produces exactly ten standardized native `2x2x0.2 m` swatches, one for each accepted Sundale shared material family. Every cube is `12` triangles against a `256`-triangle per-sample ceiling and uses only the accepted seven-color planning anchors and Blender-native procedural/material nodes.

One `1920x1080` horizontal five-column-by-two-row unified board and five `1280x720` paired closeups were opened at original resolution. Exact high-contrast family labels are complete in the unified board; each paired view materially fills its frame with its exact two swatches side by side and both labels complete. Deterministic projected checks lock frame safety, centered pair occupancy, side-by-side balance, label containment, label/label overlap `0`, and label/swatch overlap `0`.

This is new-nightly-batch Phase `1/6`. Cursor is suitable in principle, but the Execution Agent completed the bounded work without a nonredundant delegation, so Cursor task count is `0`.

## Scope authority and review boundary

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Sundale Production Asset Scope#Material families|Sundale production material-family boundary]].
- [[Design/Sundale Art Direction and Core Loop|Accepted Sundale art direction and palette]].
- [[Development/Reports/Phase 1L3a Sundale Business Clustered Mega City Replacement Preview|Owner-accepted Phase 1L.3a planning baseline]].

The board narrows one review decision before production material work expands. It does not import or place a material in Unreal, change any production geometry, approve texture/UV/trim-sheet execution, prove performance or accessibility, or establish final art.

## Exact ten-family contract

| Order | Exact review ID | Accepted family | Palette anchor | Accent | Native procedural pattern | Tris |
| ---: | --- | --- | --- | --- | --- | ---: |
| 1 | `MATERIAL_FAMILY__WARM_LIMESTONE_STUCCO` | warm limestone stucco | `#D8C8A9` | none | `NOISE` | `12` |
| 2 | `MATERIAL_FAMILY__MUTED_TERRACOTTA_STUCCO` | muted terracotta stucco | `#A65F47` | none | `NOISE` | `12` |
| 3 | `MATERIAL_FAMILY__TEXTURED_CONCRETE` | textured concrete | `#D8C8A9` | `#4D5051` | `NOISE` | `12` |
| 4 | `MATERIAL_FAMILY__SAND_CONCRETE` | sand concrete | `#B9A783` | none | `NOISE` | `12` |
| 5 | `MATERIAL_FAMILY__BRICK_PAVERS` | brick pavers | `#A65F47` | `#C46D3B` | `BRICK` | `12` |
| 6 | `MATERIAL_FAMILY__CHARCOAL_ASPHALT_SERVICE_SURFACE` | charcoal asphalt/service surface | `#4D5051` | none | `NOISE` | `12` |
| 7 | `MATERIAL_FAMILY__PAINTED_METAL` | painted metal | `#C46D3B` | none | `WAVE` | `12` |
| 8 | `MATERIAL_FAMILY__STOREFRONT_GLASS` | storefront glass | `#315F79` | none | `NOISE` | `12` |
| 9 | `MATERIAL_FAMILY__COURT_SURFACE_LINES` | court surface/lines | `#315F79` | `#D8C8A9` | `WAVE` | `12` |
| 10 | `MATERIAL_FAMILY__FOLIAGE_TRUNK` | foliage/trunk | `#6D7F62` | `#B9A783` | `NOISE` | `12` |

The exact accepted palette is `#315F79`, `#4D5051`, `#6D7F62`, `#A65F47`, `#B9A783`, `#C46D3B`, and `#D8C8A9`. Each family owns one mesh, one material slot, and exact applied dimensions `2.0x2.0x0.2 m`. Board bounds are `x=-11.41..11.41 m`, `y=-3.81..3.81 m`, and `z=-0.21..0.31 m`.

The material-node allowlist is exactly `ShaderNodeBsdfPrincipled`, `ShaderNodeBump`, `ShaderNodeOutputMaterial`, `ShaderNodeTexBrick`, `ShaderNodeTexNoise`, `ShaderNodeTexWave`, and `ShaderNodeValToRGB`. External libraries/references, source images, image textures, external fonts, brands, catalogs, interiors, armatures, gameplay additions, and paid inputs are all `0`.

## Final render evidence

Evidence root: `Oddswell/Art/Reviews/SundaleMaterialFamilyReviewBoard`.

| Retained view | Exact pair | Dimensions | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `renders/Unified_MaterialFamilyBoard.png` | all ten families | `1920x1080` | `1,741,891` | `F97B9E98E358CE09354E250E740455FEFE41692B1DE84F484C239264A7A79348` |
| `renders/Pair_01_Stucco.png` | limestone / terracotta stucco | `1280x720` | `878,144` | `9DCEE004C1F0251222936F70A3147D97E5047DA173F739FA39AD3BC071FEE96E` |
| `renders/Pair_02_Concrete.png` | textured / sand concrete | `1280x720` | `896,341` | `37B91A1D7C7C076EBF987740E65E70894D2CCB8DF6A677635914D5A62413E601` |
| `renders/Pair_03_Ground.png` | brick pavers / asphalt-service | `1280x720` | `926,669` | `D9B0A0643820FD836AA6CF32E92FEB90472132AF05C5D4E12DE4B8453D3F964E` |
| `renders/Pair_04_Facade.png` | painted metal / storefront glass | `1280x720` | `948,943` | `1CC9318BD14184ADE3BC76FECAB9430E8DEE297BA5F9679C8956E24B27285C60` |
| `renders/Pair_05_CourtLandscape.png` | court surface-lines / foliage-trunk | `1280x720` | `900,388` | `68596595FD9478992CDBF992278C55C542B26B0284642389C4650A3DB0EF5552` |

The exact label mapping is `LIMESTONE / STUCCO`, `TERRACOTTA / STUCCO`, `TEXTURED / CONCRETE`, `SAND / CONCRETE`, `BRICK / PAVERS`, `ASPHALT / SERVICE`, `PAINTED / METAL`, `STOREFRONT / GLASS`, `COURT SURFACE / LINES`, and `FOLIAGE / TRUNK`. Blender built-in text is review metadata, not production signage or a brand.

## Artifacts and provenance

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleMaterialFamilyReviewBoard.blend` | `1,131,810` | `4C64829B2D5645AB6BE0D5C975856F77AB566C7876FFF675359C65F957DF873D` |
| `build_sundale_material_family_review.py` | `38,794` | `28F4433ED68B49D5B5AE8CF686E3A9A64B550D96029FCF344A577F24DF8BA09B` |
| `manifest.json` | `21,725` | `1290254266AFC6F0B9F77626CA01F75129F55F66B8A23CBEAAB2BB72F823C5E8` |
| `PROVENANCE.md` | `866` | `365AF8DD9F3A39F910C0344152FAEA98B99B1735418C06106F28C6A4B0F7B7AC` |

The Blend is covered by the existing Git LFS rule. Its prospective pointer is:

    version https://git-lfs.github.com/spec/v1
    oid sha256:4c64829b2d5645ab6be0d5c975856f77ab566c7876fff675359c65f957df873d
    size 1131810

No `.blend1`, `.pyc`, or `__pycache__` artifact is retained.

## Canonical headless build, reopen, and focused validation

Canonical evidence root: `C:\tmp\OddsWellPhase1L3h\Evidence`.

| Evidence | Exit | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `BlenderBuild.log` | `0` | `8,106` | `4C97A98D3CFAD4EA20714E95CF9A6D317F0BFFB220B6A7AD91DC71B2C592FBD7` |
| `BlenderBuild.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderReopenValidate.log` | `0` | `1,356` | `9D2F9983583948B1DC8FB0690B68736458C82815F6BE611FEAB88B9A95A20A4F` |
| `BlenderReopenValidate.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderFocusedValidate.log` | `0` | `1,358` | `1AA90863043070443F3B52735D54552A4C0EB593AA2B6DE9D4C05B9AEA82FAB9` |
| `BlenderFocusedValidate.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

    ODDSWELL_SUNDALE_MATERIAL_FAMILY_BUILD|result=PASS|artifacts=10|manual_input=false
    ODDSWELL_SUNDALE_MATERIAL_FAMILY_REOPEN|result=PASS|manifest=true|render_hashes=6|full_framing=true|manual_input=false
    ODDSWELL_SUNDALE_MATERIAL_FAMILY_FOCUSED|result=PASS|manifest=true|render_hashes=6|full_framing=true|manual_input=false

Saved-Blend reopen and focused replay both retain explicit one-byte exit-code files containing `0`, SHA-256 `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9`. The final source bytes/hash equal the script identity recorded in the manifest.

## Rejected candidates and diagnostics

The following candidates are explicitly rejected and noncanonical:

1. **Unlabeled, narrow-board visual candidate.** The board did not visibly identify the ten families and did not use the horizontal frame materially. Builder `9F8E29FC023D53D07F9C785E383F32D206CA0D235BD8C6DC4D27D4C30D56A269`; Blend `421481DC052944930152A1E73EEA51776494DD36DD00689571554F6A97C0FFCB`; manifest `527435138D84E16C8D286ED7E399CB9FC1DEDBE04682057AB9EDEF9C630DD9B1`; provenance `42BE9183D4F737575DDA4B3C99C6F0E3E4CE3CB246C582E5F3F9C09547EED339`. Rejected render hashes were Pair01 `609BE50EA07128D3F4A985FB47E764B96A575E1232747A279C920A935623F035`, Pair02 `144C84BB8D763533C5A686A39C4849F7030647D930B1BF74B177A18E3D9D9FD3`, Pair03 `488D8D6FE292D5A309B607F230C0B033EDEE6BFCD817A9716AEE9EB1099D1BA8`, Pair04 `9AFB98D0C920F33BEA36D4767AC2FB8E9D2D74C7672D0943D373F58214CE3C4F`, Pair05 `C89EE6443A2BAFBA21FB51D3B5EA958C93F9C81181EB23CF767ED738E6D72ABF`, and Unified `5DAD2414FBDE97603B8E0C33C0D5257143F30A2849AC7C285596E42081159A5A`. Retained rejected logs are `RejectedUnlabeledBuild.log`, `4,007` bytes, SHA-256 `1311713FEF283F27D2BF242685D0BF9944C815A1A2A9B881A8E4B9B944E7FC3E`; `RejectedUnlabeledReopenValidate.log`, `673` bytes, `E338B2597B473000833E769FD03CCFA0BB0A3C34799C007B4F58D05C989A015C`; and `RejectedUnlabeledFocusedValidate.log`, `674` bytes, `41D370D7AC5526DC5FEC8FA2E7C1BA295F376D4E7883AB5E29652089143419E0`.
2. **Labeled but vertically stacked/unbalanced paired-view candidate.** Unified labels were reviewable, but the five closeups left roughly half or more of each frame empty and were not useful paired comparisons. Builder `2A6AB24DE9CF52BB0B495CED0E1140EF70CD3CE2E4AE8A398EB0B96048C94B79`; Blend `898252FA2E298E9614FE99F922CDBC54CC387F5D6682784EF8387B85ACE46EEA`; manifest `FD51FFEE15DCADE3DB9F7D3F1DFCC50436BF7687663A9BA3C2AE781192343570`; provenance `365AF8DD9F3A39F910C0344152FAEA98B99B1735418C06106F28C6A4B0F7B7AC`. Rejected render hashes were Pair01 `03282AA498930A7CA70A6E6F3D47EECC1A87F83E284356816C43A57CD8EF1A0D`, Pair02 `E004102D962BD95FF7FC6C516F4789ED79121453EFE053CE34D61B2199B150CA`, Pair03 `0598969F0437726121D482765E33E4BAA50AD9228F1DAF561925A117B45B42B9`, Pair04 `CA7FA2F1FB118017F5C3080A40F73A644BB4E94F72BA9F8C8D1089FEF503E3EF`, Pair05 `BBB670FAA1C2B369CB97621445F67C45071A40F68E1F6AB133B32FC90F0CFF11`, and Unified `E438B03323E062C95E5AC9E3D1F5A854172D07E55FCA7944E48F0D6335BABD99`. Retained rejected logs are `RejectedUnbalancedBuild.log`, `4,007` bytes, SHA-256 `21C0074CBD2876CF24C74601ECB4DCF92EBA38FD354593A69D3CD77079BADE91`; `RejectedUnbalancedReopenValidate.log`, `673` bytes, `E338B2597B473000833E769FD03CCFA0BB0A3C34799C007B4F58D05C989A015C`; and `RejectedUnbalancedFocusedValidate.log`, `674` bytes, `41D370D7AC5526DC5FEC8FA2E7C1BA295F376D4E7883AB5E29652089143419E0`.
3. **Balanced visual but precanonical validator-state candidate.** Its accepted-looking pixels were not canonical because validation reused the inner element-role variable and therefore failed to restore pair layout before the final unified assertion. The failed `BlenderBuild.stderr.log` was `709` bytes and reported `Unified_MaterialFamilyBoard.png overlaps family label plates`; it was superseded by the retained clean canonical build evidence and is not cited as a passing artifact. The retained saved-Blend probe also rejected source/manifest drift: `PairOverlapProbe.log`, `553` bytes, SHA-256 `2B4DD773F976C32A2DF35EE4BD98D262249A7883CC0908C65C565588E45AE14D`; `PairOverlapProbe.stderr.log`, `734` bytes, SHA-256 `4096F48B5AD4227024F8EF8991D64BD5EFF806BABD10C6493926FA7BEB2ACB7B`, reporting `artifact identity differs: build_sundale_material_family_review.py`. The final one-line variable correction changed validation state only; swatch geometry, material graphs, unified layout, pair presentation, and cameras were not redesigned.

Only the final hashes in the artifact/render tables and clean canonical logs are accepted evidence.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, or packaged route run was performed because this phase changes no client, runtime, map, config, test, gameplay, or package input. The frozen ledger was re-read directly.

| Reused gate | Result | Retained evidence | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Full native Unreal automation | PASS `72/72` | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log` | `339,253` | `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Python phase0a | PASS `9/9` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log` | `882` | `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` |
| Python phase0b | PASS `2/2` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log` | `854` | `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` |
| Python phase0c | PASS `8/8` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log` | `880` | `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` |
| Python phase0d | PASS `46/46` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log` | `1,010` | `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` |
| Python phase1h | PASS `40/40` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log` | `1,008` | `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` |
| Brain Admin `--check` | PASS | `C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log` | `43` | `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |

Python remains `105/105`. Production client diff is `0` paths. `client/OddsWell/Content/Maps/SundaleGraybox.umap` remains SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

Retained package root `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows` remains `50` files and `1,050,423,644` bytes excluding `Saved`, with zero Python artifacts. Wrapper SHA-256 is `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game executable SHA-256 is `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`; UFS container SHA-256 is `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Boundary and next gate

No Unreal, client, map, runtime, config, test, canonical route, collision, navigation, production material, texture, UV, trim sheet, placement, package, gameplay, business, catalog, brand, interior, service, or prior review artifact changed. Phase 1L.3a remains authoritative only at its accepted planning level.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. After local commit and verified Notion closure, return to the Scope Director for exactly one new-nightly-batch Phase `2/6` independent review subphase. Owner acceptance and a separate promotion/expansion gate apply only before these Phase 1L.3h samples become a production material family; that gate neither blocks later independent review subphases nor authorizes roadmap Phase 2. This review makes no beta-readiness, production-readiness, final-art, Version 1, or roadmap Phase 2 claim.
