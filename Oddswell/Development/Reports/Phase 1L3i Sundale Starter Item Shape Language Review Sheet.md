# Phase 1L.3i — Sundale Starter-Item Shape-Language Review Sheet

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW — OWNER ACCEPTANCE AND SEPARATE PRODUCTION PROMOTION/IMPORT PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Blender 4.5.5 LTS builder produces exactly two recognizable native low-poly review proxies for the existing Sundale starter catalog: the Sundale Signal Jacket and Sundale Modular Chair. Each proxy is `96` triangles under the `1500`-triangle ceiling, owns exactly two native material slots and one UV channel, and preserves the exact production identity, metadata, and colors without importing or changing either item in Unreal.

One `1920x1080` unified sheet and two `1920x1080` item contact sheets were opened at original resolution. The unified sheet completely frames both proxies, both Jacket fit displays, title, exact item IDs, prices, and noncanonical status. Each item sheet uses six explicit, nonoverlapping cells for front, rear, left, right, top, and perspective, with the complete silhouette and complete dimensions/triangles/slots/UV/status metadata inside each cell. Independent visual review found no clipping or overlap in the three final originals.

This is new-nightly-batch Phase `2/6`. Cursor is suitable in principle, but Execution completed the bounded work without a nonredundant delegation, so Cursor task count is `0`.

## Scope authority and review boundary

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Beta Game Bible#Avatar and clothing|The exact first beta clothing identity]] and [[Design/Beta Game Bible#Housing and furniture|the exact first beta furniture identity]].
- [[Design/Sundale Production Asset Scope#Furniture and clothing art|The minimum Sundale clothing/furniture art boundary]].
- [[Development/Reports/Phase 1L3g Player Character Silhouette Proportion and Outfit Fit Review Sheet|The two existing presentation-envelope IDs]].

The sheet narrows one shape-language decision before either item advances to production modeling/import. It does not add an item, expand a catalog, produce a skeletal garment, prove deformation or fit, place the Chair, change the `studio_primary` snap point, alter pricing/economy/inventory/equip behavior, or establish final art.

## Exact two-item contract

| Order | Exact item ID | Display name | Category / origin | Existing gameplay metadata | Exact production RGBA | Proxy bounds | Tris / ceiling | Slots / UV |
| ---: | --- | --- | --- | --- | --- | --- | ---: | ---: |
| 1 | `sundale_signal_jacket` | Sundale Signal Jacket | clothing / Sundale | `outfit`; `60` Odds Bucks | slate `(0.12,0.18,0.22,1)`; teal `(0.08,0.72,0.68,1)` | `0.72x0.24x0.84 m` | `96 / 1500` | `2 / 1` |
| 2 | `sundale_modular_chair` | Sundale Modular Chair | furniture / Sundale | `studio_primary`; `100` Odds Bucks | gray `(0.22,0.25,0.28,1)`; teal `(0.08,0.72,0.68,1)` | `0.72x0.72x1.00 m` | `96 / 1500` | `2 / 1` |

The Signal Jacket fit displays reuse only the exact existing Phase 1L.3g base IDs `CharacterPresentationMasculine` and `CharacterPresentationFeminine`. Both linked instances use the identical new review-fit local dimensions `[0.72,0.24,0.84] m`, location `[0,0,1.21] m`, and rotation `[0,0,0]` degrees. The manifest explicitly records `preexisting_garment_transform_claimed=false`; the display transform is new review metadata, not a claim about an existing production garment transform, rig, deformation envelope, or approved body fit.

## Authoritative production-source lock

| Source | Bytes | SHA-256 | Exact locked lines |
| --- | ---: | --- | --- |
| `client/OddsWell/Source/OddsWell/OddsBucksLedger.cpp` | `497,852` | `4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7` | `31`, `32`, `47`, `49`: prices `60`/`100`; exact IDs `sundale_signal_jacket`/`sundale_modular_chair` |
| `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` | `618,514` | `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298` | `81`, `82`, `123-125`: Jacket slate/teal, `studio_primary`, Chair gray/teal |

The builder fails closed if either full source hash or any exact locked line differs.

## Final artifact identities

Repository evidence root: `Oddswell/Art/Reviews/SundaleStarterItemShapeLanguageReviewSheet`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_sundale_starter_item_shape_language.py` | `35,828` | `18E7B3790E45B0C39E43A2ED7D7FAEF7987D4368270B8AF4F1A009DD3C665973` |
| `SundaleStarterItemShapeLanguageReviewSheet.blend` | `860,857` | `1F9113B1F19A1AA0A145A9EB14E09AFA7DC55CDF341184BF548623A029C64283` |
| `manifest.json` | `6,444` | `9968422C0521088F1F38E8F561C3A9818004AF0A45E9049CA4EF3E07B7FDF91A` |
| `PROVENANCE.md` | `982` | `68F55E0556FB28EEF1FF4DEB5DCB065C40127B13872BAA53AE1576BB4DE35A95` |

The Blend is covered by the existing Git LFS rule. Its exact prospective pointer is:

    version https://git-lfs.github.com/spec/v1
    oid sha256:1f9113b1f19a1aa0a145a9eb14e09afa7dc55cdf341184bf548623a029c64283
    size 860857

No `.blend1`, `.pyc`, or `__pycache__` artifact is retained.

## Final render evidence

| Retained view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_StarterItemShapeLanguage.png` | `1920x1080` | `1,958,941` | `1F215D30A01FBDCFCF042A3ECC140E6F1BCADF5A268B5A65AFA348E8025B9DC9` |
| `renders/ContactSheet_SundaleSignalJacket.png` | `1920x1080` | `1,994,001` | `D5EC7F6095CE0B34FA434C50B653B51F53B9B31473AE1771C70C32E44660DD8E` |
| `renders/ContactSheet_SundaleModularChair.png` | `1920x1080` | `1,997,960` | `7E2CC667641D015D40E9B1DCF50C199AFE550290B1F50732E2C356202B87A3C4` |

Projected validation locks one unified plus two contact-sheet cameras, six exact cells per item, full board framing, complete item and metadata containment within every cell, item/label overlap `0`, cell overlap `0`, and text/cell contrast at least `4.5:1`. Every contact label includes the exact view name, dimensions, triangle count, `2 SLOTS`, `1 UV`, and `NONCANONICAL REVIEW`.

## Canonical build, reopen, and focused evidence

Canonical evidence root: `C:\tmp\OddsWellPhase1L3i\Evidence`.

| Evidence | Exit | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `BlenderBuild.log` | `0` | `2,075` | `0DBB6BA25E83068FF00E47E713A5D97C681EE514896A24C7051E91E62566C29A` |
| `BlenderBuild.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderReopenValidate.log` | `0` | `523` | `B008D06B81DDA34C12600B3B922A1FA6918A86AB9AD5827E317D50C6E02A120A` |
| `BlenderReopenValidate.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderFocusedValidate.log` | `0` | `524` | `9A22818164963D1B66737A2A9BDA0774F12ED4349B7181A7F98BBD58EC278135` |
| `BlenderFocusedValidate.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

    ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_BUILD|result=PASS|artifacts=7|manual_input=false
    ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_REOPEN|result=PASS|manifest=true|render_hashes=3|manual_input=false
    ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_FOCUSED|result=PASS|manifest=true|render_hashes=3|manual_input=false

Build, saved-Blend reopen, and focused validation each returned exit `0` with empty stderr. Reopen and focused validation rechecked source/manifest parity, artifact hashes, all three render hashes and dimensions, exact IDs/metadata/colors, two `96`-triangle ceilings, two actual material slots, one actual UV layer, fit-envelope IDs/new-transform truth, native-node allowlist, framing/overlap/contrast, and all zero boundaries.

## Rejected initial visual candidate

The first internally passing candidate is explicitly rejected and noncanonical. Original-resolution inspection found near-black presentation, top clipping on the unified sheet, generic box-like item silhouettes, contact-cell clipping, low-contrast/overlapping metadata, and unusable frame margins. It is retained machine-locally under `C:\tmp\OddsWellPhase1L3i\Evidence\RejectedCandidate` and is not accepted evidence.

| Rejected identity | Bytes | SHA-256 |
| --- | ---: | --- |
| builder identity recorded by rejected manifest | `26,411` | `547DC33DA1F4211CC1D72684D1A4B8393C20A01D55DC4293626FB52001F3DF38` |
| `SundaleStarterItemShapeLanguageReviewSheet.blend` | `731,373` | `9C627709606D6684E649C75793B1C1E10C577B5F8359FFC1E7F29739D2B7F3E1` |
| `manifest.json` | `6,238` | `DFEA46A82607F4DCCDB0ECC01C5393D5E26523A28BBE70CF3F62EBC52980B987` |
| `PROVENANCE.md` | `982` | `68F55E0556FB28EEF1FF4DEB5DCB065C40127B13872BAA53AE1576BB4DE35A95` |
| `Unified_StarterItemShapeLanguage.png` | `1,981,552` | `150F912E73291B68E2C0B3A73BCAEBE9398A905004FF59A03BC5E88016959561` |
| `ContactSheet_SundaleSignalJacket.png` | `2,117,135` | `59DE788BE71392F214212B56984D47C1598646A0E81E88D1F0B182E23AF53E70` |
| `ContactSheet_SundaleModularChair.png` | `2,052,034` | `63AC1F2BAF40D96E33F24B5B3F3AE09599CCC07E4EA20C9F9D33587BC178A447` |
| `BlenderBuild.log` | `2,075` | `D10768FF836F30BA90899BAB564DE28DFEC31078FA140CBF5EB373EEA0C68629` |
| `BlenderBuild.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

The accepted correction replaces all rejected builder/Blend/manifest/render identities. It keeps the exact two item IDs, production metadata/colors, material-slot/UV ceilings, and fit truth boundary while providing recognizable native shapes, explicit nonoverlapping `3x2` cells, brighter readable presentation, wider frame margins, and executable projected validation. Intermediate pre-render diagnostics are not passing or canonical evidence.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, import, or packaged route run was performed because this phase changes no client, runtime, map, config, test, gameplay, package input, or prior review artifact. The frozen ledger was re-read directly.

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

No Unreal, client, map, runtime, config, test, canonical route, collision, navigation, production clothing/furniture, texture, rig, deformation, placement, import, package, gameplay, economy, inventory, catalog, brand, interior, service, or prior review artifact changed. External references, source images, image textures, external fonts, brands, catalog additions, interiors, gameplay additions, libraries, textures, armatures, and animations remain `0`. Phase 1L.3a remains authoritative only at its accepted planning level.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. After local commit and verified Notion closure, return to the Scope Director for exactly one new-nightly-batch Phase `3/6` independent review subphase. Owner acceptance and a separate production promotion/import gate apply only before these Phase 1L.3i samples become production art; that gate neither blocks later independent review subphases nor authorizes roadmap Phase 2. This review makes no beta-readiness, production-readiness, final-art, Version 1, or roadmap Phase 2 claim.
