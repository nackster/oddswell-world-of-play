# Phase 1L.3f Sundale Destination Entrance and Threshold Treatment Review Board

Date: 2026-08-10
Branch: agent/phase-0d
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE, PRODUCTION CLEARANCE, PROMOTION, AND PLACEMENT PENDING**
Cost: $0.00

## Outcome first

One deterministic Blender 4.5.5 LTS builder now produces exactly six native low-poly destination entrance treatments on one review board. Each treatment uses non-text geometric cues, retains one open review passage, and records `collision_claim=false`. One unified frame and six complete closeups were visually inspected.

This is new-art-batch Phase 5/6. Cursor delegation count remains 0. The review does not change production assets or claim clearance, collision, accessibility, placement, final art, or beta readiness.

## Scope authority and player-facing risk

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps 1, 2, and 5.
- [[Design/Beta Game Bible#First-hour player journey]] > 2. Enter the first city.
- [[Design/Beta Game Bible#World and city scope]].
- [[Design/Beta Game Bible#Art, music, and storytelling]].
- [[Design/Sundale Production Asset Scope#Streets, paving, and wayfinding]].
- [[Design/Sundale Production Asset Scope#Recommended production order]] > replace the gameplay-building exteriors in route order.

The phase reduces the risk that six required interaction destinations receive visually interchangeable entrances or that later production modeling drifts away from the proven anchors and frontage envelopes. It does not prove that a passage works with the production player capsule, collision, navigation, prompts, or first-hour route.

## Exact review contract

| Exact noncanonical ID | Geometric identity | Triangles | Scope boundary |
| --- | --- | ---: | --- |
| `ThresholdStudioApartment` | residential frame, balcony band, modest awning | 72 | Shared Studio/owned One-bedroom exterior entrance; Apartment Management excluded |
| `ThresholdJob` | practical canopy piers, header, structural slats | 84 | Exterior-only Job frontage |
| `ThresholdClothingStore` | asymmetric retail fins and display bays | 72 | Exterior-only Clothing Store frontage |
| `ThresholdFurnitureStore` | broad sage showroom frame and deep canopy | 72 | Exterior-only Furniture Store frontage |
| `ThresholdArena` | broad multi-bay portal and cobalt canopy | 84 | Arena entry portal only |
| `ThresholdTicketBooth` | compact frame, split counters, offset bar | 84 | Exterior-only Ticket Booth frontage |

Each ID has exactly one root, one instance, native mesh geometry, and one `open_passage_proxy=true` object. The per-sample triangle ceiling is 2,500. Every object records `collision_claim=false`; the openings are review proportions, not production-clearance assertions.

## Frozen production references

The builder and manifest freeze the following values from `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` at pre-phase HEAD `6df1351`. Frontage bounds are exact axis-aligned unions of the cited current 100 cm native-cube presentation specs.

| Review ID | Existing anchor cm | Radius cm | Existing frontage bounds cm (x; y; z) |
| --- | --- | ---: | --- |
| `ThresholdStudioApartment` | `(0, 0, 220)` | 350 | `-1100..1100; 1..450; 325..975` |
| `ThresholdJob` | `(9500, 0, 0)` | 350 | `8875..10125; -20..342.5; 0..940` |
| `ThresholdClothingStore` | `(12500, 9000, 0)` | 350 | `11275..12147.5; 8472.5..9527.5; 0..840` |
| `ThresholdFurnitureStore` | `(-9500, 5000, 0)` | 350 | `-10147.5..-9275; 4472.5..5527.5; 0..840` |
| `ThresholdArena` | `(7000, 18000, 0)` | 350 | `6572.5..7427.5; 16610..17645; 0..822.5` |
| `ThresholdTicketBooth` | `(1000, 18000, 0)` | 350 | `710..1290; 16775..17645; 0..630` |

The current Arena/Ticket-Booth separation test retains a 6,000 cm anchor distance, 700 cm summed interaction radii, and 5,300 cm edge clearance. No other clearance is invented. The manifest records exact source lines and part IDs for every extraction.

## Artifact and render evidence

Evidence root: `Oddswell/Art/Reviews/SundaleDestinationThresholdReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleDestinationThresholdReviewBoard.blend` | 975,000 | `5A70767F4378CF301363BEE751C37159500F76F4615B5C7C1498CF2F01B10530` |
| `build_sundale_destination_thresholds.py` | 28,719 | `E47C9CD46B5C7313A902019C537E78B796EB98A54B6A82E508B7F88A0912C828` |
| `PROVENANCE.md` | 1,183 | `2DD5EF566ECCD161758EB2B5F188FEB790D6609DC746248451F94EAA124083E9` |
| `manifest.json` | 11,443 | `64DCDB4931ABD5EB2399F6EAC57F9129E8E27E901AAA1DD06276F102A5CD5742` |

The Blend is covered by the existing Git LFS rule. Its prospective pointer is:

    version https://git-lfs.github.com/spec/v1
    oid sha256:5a70767f4378cf301363bee751c37159500f76f4615b5c7c1498cf2f01b10530
    size 975000

No `.blend1` backup exists.

| Retained review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_SundaleDestinationThresholds.png` | 1920x1080 | 1,868,059 | `028CDC5E3BC0595E1C3D1635F61E92197F74724AEBC4B0FBDFC48670BDB093DE` |
| `renders/Closeup_ThresholdStudioApartment.png` | 1280x720 | 699,137 | `AB4AF31401F7B7212AA7262F1BA2E665DC0725DCD37BBA9EF049C17A4EDF5987` |
| `renders/Closeup_ThresholdJob.png` | 1280x720 | 676,907 | `16C253BD092FDF7E898688E3344EAB735A30BCFBA478CAAC00A130DBDC872744` |
| `renders/Closeup_ThresholdClothingStore.png` | 1280x720 | 686,446 | `CAC1B5844D7647AFAB664F918FAB3925FE5475A5A33DC7A449AF9FE7321263C2` |
| `renders/Closeup_ThresholdFurnitureStore.png` | 1280x720 | 690,196 | `80F0852E574B3D15C168A15E94497A701304238B713915B1C4DFEBB56DCD6644` |
| `renders/Closeup_ThresholdArena.png` | 1280x720 | 718,684 | `B7D13C16E5ADEDDA63B7628A127EBA5102D107888E5AA1DB9E0EA63985B0B761` |
| `renders/Closeup_ThresholdTicketBooth.png` | 1280x720 | 681,875 | `BA1BA6EE67A660D1A6CB62FF3CC8725B5E5A8A7E067DDF6A29026EFCA44A2372` |

All seven PNGs were reopened at their original resolution. Every frame retains the complete entrance silhouette and approach apron with visible margin. The unified board supports side-by-side differentiation; the closeups are the primary passage and threshold framing evidence. There were no rejected retained renders after the first candidate because all required geometry was complete and readable.

## Headless build, reopen, and focused evidence

Final phase-local evidence is under `C:\tmp\OddsWellPhase1L3f\Evidence`.

| Fresh evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `BlenderBuildFinal.log` | 10,014 | `A5D35CA6D318100815311F8CD4B3B9148F07022ABC45F39D74598CF3A4E3D3B0` |
| `BlenderReopenValidate.log` | 1,592 | `FA9AAD74A6DD88FEF8E99DC8A351841334F8A702F596E3BB48764D024F00FBC0` |
| `BlenderFocusedValidate.log` | 1,594 | `B191CAFB375C234AC032C487008140936EE463BD5F2BBDBBD79D60CC1E4FDCF1` |

    ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_BUILD|result=PASS|artifacts=10|manual_input=false
    ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_REOPEN|result=PASS|manifest=true|render_hashes=7|manual_input=false
    ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_FOCUSED|result=PASS|manifest=true|render_hashes=7|manual_input=false

The validators lock the exact six IDs, one-instance counts, roots, roles, triangle counts and ceilings, board bounds, accepted-palette-only materials, seven cameras/renders and hashes, production reference extraction, six open-passage proxies, `collision_claim=false`, and every zero boundary.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, or packaged route run was performed because this diff changes no client, runtime, map, test, config, interaction, collision, navigation, route, or package input. The previously verified frozen ledger remains applicable; every retained file below was re-read directly before report closure.

| Reused gate | Result | Retained evidence | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Full native Unreal automation | PASS 72/72 | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log` | 339,253 | `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Python phase0a | PASS 9/9 | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log` | 882 | `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` |
| Python phase0b | PASS 2/2 | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log` | 854 | `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` |
| Python phase0c | PASS 8/8 | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log` | 880 | `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` |
| Python phase0d | PASS 46/46 | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log` | 1,010 | `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` |
| Python phase1h | PASS 40/40 | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log` | 1,008 | `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` |
| Brain Admin `--check` | PASS | `C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log` | 43 | `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |

The five repository-pinned Python 3.12.13 logs total `9 + 2 + 8 + 46 + 40 = 105/105`.
- Production client diff: 0 paths.
- `client/OddsWell/Content/Maps/SundaleGraybox.umap`: unchanged SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.
- Retained package root: `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows`; 50 files, 1,050,423,644 bytes excluding every `Saved` subtree, zero Python artifacts.
- Wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game executable SHA-256 `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`; UFS container SHA-256 `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary and next gate

This review changes no Unreal, client, map, runtime, config, test, prompt, E-input, latch, transition, interaction radius, collision, navigation, canonical 800 m route, package, production catalog, business/economy/housing/wager behavior, or Apartment Management exterior. It adds no external references, textures, interiors, text signs, brands, or gameplay.

The frozen Phase 0 simulation, authoritative event log, equal-information boundary, Basketball Brain, Wager and Settlement Engine, Odds Bucks authority, immutable inventory/history, and current brain maturity remain untouched. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

After commit and verified Notion closure, return to the Scope Director for exactly one new-art-batch Phase 6/6 independent review subphase. Owner acceptance, production clearance, promotion, and placement are required before any production use; this does not authorize roadmap Phase 2.
