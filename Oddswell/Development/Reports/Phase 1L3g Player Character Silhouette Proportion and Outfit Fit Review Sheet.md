# Phase 1L.3g — Player-Character Silhouette, Proportion, and Outfit-Fit Review Sheet

Date: 2026-08-10
Branch: agent/phase-0d
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW — OWNER ACCEPTANCE, PRODUCTION PROMOTION, MODELING, AND RIGGING PENDING**
Cost: $0.00

## Outcome first

One deterministic Blender 4.5.5 LTS builder now produces exactly eight faceless primitive mannequin displays: the current four skin tones across each of the two approved presentation bases. All eight share one `1.80 m` review stature, the same eight joint-landmark heights, gameplay-identical status, and one shared-skeleton compatibility target. The existing starter outfit proxy is visible on every display, and the existing Signal Jacket proxy is fitted once to each base with identical local dimensions and transforms.

One `1920x1080` unified lineup plus complete `1600x900` front, side, back, and three-quarter views were inspected at original resolution. Ten dedicated high-contrast header plates keep both exact base IDs and all eight exact `preset_id | tone_id` labels clear of silhouettes, rails, and frame edges. This is new-art-batch Phase `6/6`; Cursor delegation remains `0`. It does not create a production person, skeletal mesh, rig, animation, face, hair catalog, new character option, or final character art.

## Scope authority and player-facing risk

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Beta Game Bible#1. Choose a default character|First-hour player journey — Choose a default character]].
- [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]].
- [[Design/Beta Game Bible#Art, music, and storytelling|Art, music, and storytelling]].
- [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]].
- [[Design/Sundale Production Asset Scope#Player-character art is a separate approval track|Player-character art separate approval track]].

The review reduces the risk that later character modeling gives the minimum onboarding presets unequal visible stature or incompatible clothing fit. It also prevents production rigging from starting before the owner can inspect a bounded silhouette and outfit-fit target. It does not prove deformation, locomotion compatibility, accessibility, subjective appeal, or production readiness.

## Exact production-source extraction

The builder reads no runtime data and changes no production source. It freezes the following exact current values from pre-phase HEAD `bf8ccbbf0a185aa61f73a806fb672953f56f2991`.

| Frozen source | Exact lines | SHA-256 | Extracted contract |
| --- | --- | --- | --- |
| `client/OddsWell/Source/OddsWell/CharacterPresetCatalog.cpp` | `9-10`, `16-23` | `C78132F21C303838BA7F0C0ED75E5A8B81260747F688760DF7E0A7C1E281AB1F` | starter item IDs, exact eight preset IDs/order, four shared RGB tones |
| `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` | `80-82` | `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298` | off-white, Signal Jacket slate, and Signal Jacket teal colors |

The exact preserved catalog order and mapping is:

| Order | Preset ID | Presentation base | Tone ID | RGBA8 | Review outfit state |
| ---: | --- | --- | --- | --- | --- |
| 1 | `masculine_tone_1` | `CharacterPresentationMasculine` | `tone_1` | `246,218,194,255` | starter off-white |
| 2 | `masculine_tone_2` | `CharacterPresentationMasculine` | `tone_2` | `210,160,120,255` | starter off-white |
| 3 | `masculine_tone_3` | `CharacterPresentationMasculine` | `tone_3` | `145,96,68,255` | starter off-white |
| 4 | `masculine_tone_4` | `CharacterPresentationMasculine` | `tone_4` | `82,52,38,255` | Signal Jacket over starter bottom |
| 5 | `feminine_tone_1` | `CharacterPresentationFeminine` | `tone_1` | `246,218,194,255` | starter off-white |
| 6 | `feminine_tone_2` | `CharacterPresentationFeminine` | `tone_2` | `210,160,120,255` | starter off-white |
| 7 | `feminine_tone_3` | `CharacterPresentationFeminine` | `tone_3` | `145,96,68,255` | starter off-white |
| 8 | `feminine_tone_4` | `CharacterPresentationFeminine` | `tone_4` | `82,52,38,255` | Signal Jacket over starter bottom |

The clothing contract remains the exact existing `starter_offwhite_top`, `starter_offwhite_bottom`, and `sundale_signal_jacket`. No item or catalog entry was added. Review colors remain starter `(0.92,0.90,0.82,1)`, jacket slate `(0.12,0.18,0.22,1)`, and jacket teal `(0.08,0.72,0.68,1)`.

## Shared silhouette and fit contract

Both bases use one `1.80 m` review stature and exact shared landmark heights: ankle `0.10`, knee `0.53`, hip `0.94`, wrist `0.78`, elbow `1.12`, shoulder `1.45`, head center `1.66`, and crown `1.80 m`. These are empty review markers, not bones or an armature.

The neutral primitive bodies vary only in bounded torso/hip silhouette. They do not change gameplay and do not infer ability, wealth, intelligence, behavior, age, ethnicity, pronouns, person names, or athlete outcomes. All eight are modestly clothed and faceless.

The starter top, starter-bottom shell/two leg pieces, jacket shell, and jacket accent use identical local dimensions, locations, and rotations on both bases. The manifest stores the exact transform signatures. The starter design count is `1`, reused on all eight displays. The Signal Jacket design count is `1`, reused once per base. This is fit-review reuse, not a new outfit or production clothing catalog.

| Display triangle result | Count |
| --- | ---: |
| Each starter display | `620 / 1500` ceiling |
| Each Signal Jacket display | `644 / 1500` ceiling |

## Label and complete-view evidence

The final sheet has exactly two base labels and eight exact `preset_id | tone_id` labels. Every label owns a dedicated charcoal plate with a presentation-colored accent and off-white text. The validator projects the plate and complete silhouette AABBs through the retained orthographic camera at all five rotations. It locks frame safety, label-plate overlap `0`, label/silhouette overlap `0`, and silhouette/silhouette overlap `0` in every view.

| Retained review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_EightPresetLineup.png` | `1920x1080` | `1,612,657` | `0CC5BC228B5CAE307F058C6F0C60A87764AAEA871657FBC8CB8F071A45BA8881` |
| `renders/Review_Front.png` | `1600x900` | `1,125,065` | `C273F37734B6E3C7DB6E19DB1AFD1183C974C083978DD344DE67FDE829EE3FB8` |
| `renders/Review_Side.png` | `1600x900` | `1,108,952` | `6242D7E3A8032BD4C9028C249DDE5EF87B048D6A4B3D2E29C8505A319434E507` |
| `renders/Review_Back.png` | `1600x900` | `1,124,124` | `EA2806FD5497D159BDEFD36EA901C7453CFA2BAC96ED9E5ED553D304185D8C9D` |
| `renders/Review_ThreeQuarter.png` | `1600x900` | `1,134,062` | `497C45FB1293FA4A7F9290A9299653DFAB78DB9B16ADFAEF5385232105E36468` |

All five originals show the complete eight-preset lineup and both outfit states. The side view is intentionally thin because the mannequins are low-poly silhouette proxies, not volumetric production bodies.

## Artifacts and provenance

Evidence root: `Oddswell/Art/Reviews/PlayerCharacterSilhouetteReviewSheet`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `PlayerCharacterSilhouetteReviewSheet.blend` | `3,121,166` | `F909E54EBDC9B73B3044F8412D16BFB5229A741B981D827A9ED5642A1470A190` |
| `build_player_character_silhouettes.py` | `42,208` | `9F877E2D764D32C9A4A63AC34104FE8C70D6AD982069D1830D72CAD3A085EA9A` |
| `PROVENANCE.md` | `1,117` | `D0D194EA54BBD91585D49DF0DE4BBCF7C725916FAC5A4C6A6EC0C49127645616` |
| `manifest.json` | `12,060` | `CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A` |

The source uses only Blender-native cubes, eight-sided cylinders, icospheres, empties, and built-in text. There is no external human model, library, texture, source image, font, download, or paid input. The Blend is covered by the existing Git LFS rule; its prospective pointer is:

    version https://git-lfs.github.com/spec/v1
    oid sha256:f909e54ebdc9b73b3044f8412d16bfb5229a741b981d827a9ed5642a1470a190
    size 3121166

No `.blend1` backup exists.

## Headless build, reopen, and focused validation

Canonical evidence is under `C:\tmp\OddsWellPhase1L3g\Evidence`.

| Fresh evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `BlenderBuildFinal.log` | `7,884` | `CAADB91CF5674E6A9B5CCC7885554E6A209E54320DEBFB57A1F288B00CB18C65` |
| `BlenderReopenValidate.log` | `1,550` | `9C3A31F05B490AB1DE52CE74B57969A1A0BD2FCCB38CB74FE88D17AFA1225BA4` |
| `BlenderFocusedValidate.log` | `1,552` | `0E782F8BE9D37A7CC06FBC1CA3184D583C7FAF0F97BA3655B72A384FB2216E93` |

    ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_BUILD|result=PASS|artifacts=8|manual_input=false
    ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_REOPEN|result=PASS|manifest=true|render_hashes=5|manual_input=false
    ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_FOCUSED|result=PASS|manifest=true|render_hashes=5|manual_input=false

The validation marker additionally locks `bases=2`, `tones=4`, `displays=8`, `stature_m=1.8`, shared landmarks/skeleton target, `label_plates=10`, label overlaps `0`, silhouette overlaps `0`, demographic inferences `0`, and every armature/rig/animation/face/hair/name/pronoun/deep-creator/extra-outfit/external-reference/texture/gameplay count at `0`.

## Rejected diagnostics

- The first Blender candidate failed before rendering because direct comparison of a Blender ID-property array to a Python list rejected the exact tone RGBA check. Retained `BlenderBuild.log`: `2,310` bytes, SHA-256 `3D639118AF999FA5F0DD8B007249B12A66C6502E3A4120F55C251C2EFF31B985`. The comparison now normalizes the ID-property array; the production tone data did not change.
- Early perspective/orthographic framing drafts were visually rejected because edge displays were clipped or the row/tone labels were occluded. Those images were overwritten by the deterministic render path and are not evidence.
- The first dedicated-plate candidate was validator-rejected for projected label/silhouette overlap. Retained `BlenderBuildLabelCandidate.log`: `2,798` bytes, SHA-256 `DDBBCD268850BF4E83959AF318D05EBD2126665758EDF04FB22349D62F7EE1CE`.
- The first stacked-header candidate projected toward the camera and remained over the silhouettes. Retained `BlenderBuildLabelCandidate2.log`: `8,056` bytes, SHA-256 `A8CA25A9ECD6333FD85DE4F5E9316B13F66A13285962ABAFF2C897C390571C15`.
- The first separated-row candidate still had top/bottom silhouette AABB contact. Retained `BlenderBuildLabelCandidate4.log`: `2,658` bytes, SHA-256 `7174086DE17CE8EDA969267194CB8E33B43F090A0C8E93EFAA2235240347A2F4`.

The retained final moves only the review layout and dedicated label headers. It does not change body geometry, outfit geometry, production IDs, colors, gameplay, or runtime behavior.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, or packaged route run was performed because this diff changes no client, runtime, map, config, test, preset catalog/order, save, handoff, appearance replication, camera, locomotion, authority, or package input. The previously verified frozen ledger was re-read directly.

| Reused gate | Result | Retained evidence | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Full native Unreal automation | PASS `72/72` | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log` | `339,253` | `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Python phase0a | PASS `9/9` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log` | `882` | `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` |
| Python phase0b | PASS `2/2` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log` | `854` | `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` |
| Python phase0c | PASS `8/8` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log` | `880` | `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` |
| Python phase0d | PASS `46/46` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log` | `1,010` | `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` |
| Python phase1h | PASS `40/40` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log` | `1,008` | `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` |
| Brain Admin `--check` | PASS | `C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log` | `43` | `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |

The Python total remains `105/105`. Production client diff is `0` paths. `client/OddsWell/Content/Maps/SundaleGraybox.umap` remains SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

Retained package root `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows` still contains `50` files and `1,050,423,644` bytes excluding every `Saved` subtree, with zero Python artifacts. Wrapper SHA-256 is `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game executable SHA-256 is `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`; UFS container SHA-256 is `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Boundary and next gate

This review changes no Unreal/client/runtime/config/test/preset catalog/order/save/handoff/appearance replication/camera/locomotion/authority, and it creates no production character, skeleton, rig, animation, face, hair, name, pronoun, deep creator, or additional outfit. The frozen Phase 0 simulation, authoritative event log, equal-information boundary, server-owned settlement, Odds Bucks authority, immutable inventory/history, and current brain maturity remain untouched.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. New-art-batch Phase `6/6` is complete only after Coordinator verification and Notion sync. Do not start a seventh implementation. Owner acceptance and a separate promotion/modeling/rigging gate are required before any production character work, and this review does not authorize roadmap Phase 2, beta readiness, Version 1, or production readiness.
