# Phase 1L.3k - First-Wager Graphic-Language Review Board

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE AND SEPARATE PRODUCTION PROMOTION/INTEGRATION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Python-standard-library builder produces one unified `1920x1080` SVG and four `1280x720` context SVGs for exactly the current first-wager flow: ticket-booth prompt, Match Winner selection, precommit confirmation, and settled receipt. The board pairs six exact state labels with six distinct silhouettes: `INTERACT` / open circle and dot, `ACTIVE` / triangle, `LOCKED` / barred square, `SELECTED` / diamond, `CONFIRM` / double chevron, and `SETTLED` / ring and check.

The typography contract has exactly four roles: `DISPLAY_TITLE`, `STATE_LABEL`, `PRIMARY_VALUE`, and `INSTRUCTION`. The visible player-world copy is limited to the existing Harbor City Waves and Mesa Vista Sol labels, the current ticket-booth prompt, and the existing first-wager values `40`, `94`, and `154` Odds Bucks. No state, behavior, offer, wager, payout, balance, or production UI was added or changed.

Two clean builds are byte-identical. Reopen XML and focused validation pass with text contrast `9.8641:1` against a `4.5:1` floor, marker contrast `3.8792:1` against a `3.0:1` floor, and forbidden-content count `0`. Independent inspection of all five originals, a true full-board `960x540` compact downscale, and a `1920x1080` grayscale diagnostic found complete framing, visible margins, no observed clipping or overlap, and six recognizable shapes without color. This is new-nightly-batch Phase `4/6`. Cursor is suitable in principle for isolated graphic tooling, but task count is `0` because the bounded objective is already complete and no independent nonredundant task remains.

## Scope authority and boundary

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Beta Game Bible#First-hour player journey|First-hour step: Enter the first city and use the first wager path]].
- [[Design/Beta Game Bible#Basketball and wagering|The existing basketball and wagering presentation contract]].
- [[Design/Beta Game Bible#Art, music, and storytelling|The bounded beta art/storytelling direction]].

The review answers one question: can the current first-wager flow use a coherent state-shape and typography language that remains distinguishable without color? It does not authorize production integration, add a runtime state, redesign the wager flow, change the wager or settlement authority, replace the current UI, reuse the Phase 1L.3j team symbols, or claim accessibility readiness.

## Exact context, state, and typography contract

| Output | Dimensions | Exact context ID | Required states |
| --- | ---: | --- | --- |
| `Unified_FirstWagerGraphicLanguage.svg` | `1920x1080` | `UNIFIED` | all six, once each |
| `Context_TicketBoothPrompt.svg` | `1280x720` | `ticket_booth_prompt` | `INTERACT` |
| `Context_MatchWinnerSelection.svg` | `1280x720` | `match_winner_selection` | `ACTIVE`, `LOCKED`, `SELECTED` |
| `Context_PrecommitConfirmation.svg` | `1280x720` | `precommit_confirmation` | `SELECTED`, `CONFIRM` |
| `Context_SettledReceipt.svg` | `1280x720` | `settled_receipt` | `SETTLED` |

| State ID and written label | Exact shape ID | Color-independent silhouette |
| --- | --- | --- |
| `INTERACT` | `OPEN_CIRCLE_DOT` | open ring with central dot |
| `ACTIVE` | `TRIANGLE` | filled triangle |
| `LOCKED` | `BARRED_SQUARE` | outlined square with diagonal bar |
| `SELECTED` | `DIAMOND` | filled diamond |
| `CONFIRM` | `DOUBLE_CHEVRON` | two forward chevrons |
| `SETTLED` | `RING_CHECK` | ring with check mark |

Every state marker is tagged with its exact state and shape ID. `shape_distinct=true` and `color_only=false`. The Phase 1L.3j wave-symbol, sun-symbol, and symbol-reuse counts are all `0`; the authorized team label Harbor City Waves remains written copy, not reuse of its prior wave geometry.

The exact typography role list is `DISPLAY_TITLE`, `STATE_LABEL`, `PRIMARY_VALUE`, and `INSTRUCTION`. The manifest locks per-output counts. Generic native `Arial, sans-serif` is referenced without an embedded or external font; external font files remain `0`.

## Exact production-palette conversion ledger

Source: `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp`

Source SHA-256: `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298`

The builder converts the exact current linear RGB channels with IEC 61966-2-1 transfer, then rounds each sRGB channel to the nearest 8-bit integer. No sixth color is permitted.

| Role | Source line and expression | Linear RGBA | Converted sRGB hex |
| --- | --- | --- | --- |
| dark navy | `9133`: `FLinearColor(0.025f, 0.055f, 0.08f)` | `(0.025, 0.055, 0.08, 1)` | `#2C4250` |
| teal | `9134`: `FLinearColor(0.08f, 0.45f, 0.42f)` | `(0.08, 0.45, 0.42, 1)` | `#50B3AD` |
| warm gold | `8932`: `FLinearColor(0.96f, 0.78f, 0.30f)` | `(0.96, 0.78, 0.30, 1)` | `#FAE595` |
| muted | `9136`: `FLinearColor(0.32f, 0.34f, 0.36f)` | `(0.32, 0.34, 0.36, 1)` | `#999EA2` |
| white | `9126`: `FLinearColor(0.96f, 0.94f, 0.87f, 1.0f)` | `(0.96, 0.94, 0.87, 1)` | `#FAF8F0` |

Validation reopens the source, checks the exact source SHA, line expressions, tuples, converted hex values, exact five-color set, and every SVG color attribute.

## Final artifact identities

Repository evidence root: `Oddswell/Art/Reviews/FirstWagerGraphicLanguageReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_first_wager_graphic_language.py` | `27,373` | `0A55E0C2719E7348863EA499AADCD58A75C75BBDE1ABB9836439CE3BFE42AD56` |
| `Unified_FirstWagerGraphicLanguage.svg` | `7,111` | `05DFDCA42EACD504F87163BD9599A13B639B7A572095C61C63E31C33079AD363` |
| `Context_TicketBoothPrompt.svg` | `1,662` | `3816C42CB227908FE9A28A5E08E7C50F716A567F570026D852E3ADBC829789F2` |
| `Context_MatchWinnerSelection.svg` | `3,138` | `7300DEF444D195CF16D5304D958460244635FDA1AEFE829076BE18441DDCEDA5` |
| `Context_PrecommitConfirmation.svg` | `2,797` | `8022FDBD2D3C765208AC246D811A2CF30BC4335036284EA9A6EFD64C453B190B` |
| `Context_SettledReceipt.svg` | `2,145` | `0D8962ABD2AB417120C42728603DE6B7AF59CF37D17B0FE0D3602D6E6D9F17A5` |
| `manifest.json` | `6,933` | `949A612B8D4F9DE1035ED49152D3A821C91038B15C89351B58758B8F72BE253F` |
| `PROVENANCE.md` | `1,111` | `6209F079D3C629221965E37B13CBE8AEEF43F232DF36D01471D12AB0AFC88F8C` |

These text and SVG artifacts use normal Git storage. The review root contains exactly these eight files and no raster, `.pyc`, `__pycache__`, external font, texture, image, or downloaded asset.

## Deterministic build and focused XML evidence

Retained evidence root: `C:\tmp\OddsWellPhase1L3k\Evidence`.

| Evidence | Exit | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `VisualRepairCleanBuild1.log` | `0` | `1,718` | `99433D916E6FB4A008DE0D9FAFBC85A0D50C72B53C43366DE8AC21C3DD77E61E` |
| `VisualRepairCleanBuild2.log` | `0` | `1,718` | `99433D916E6FB4A008DE0D9FAFBC85A0D50C72B53C43366DE8AC21C3DD77E61E` |
| `VisualRepairReopenXml.log` | `0` | `336` | `A45FD42A2EFBE676C9DC4018E5B44B4D69C0670EE2D0517C21A9FA52F01DA5F1` |
| `VisualRepairFocused.log` | `0` | `344` | `ED8249EC526ADC619B473346E56050F8E69EA53E1863E1629F47AD0C4FE65539` |

    ODDSWELL_FIRST_WAGER_GRAPHIC_LANGUAGE_BUILD|result=PASS|outputs=5|states=6|type_roles=4|text_contrast_min=9.8641|marker_contrast_min=3.8792|external_refs=0|forbidden=0
    ODDSWELL_FIRST_WAGER_GRAPHIC_LANGUAGE_XML|result=PASS|outputs=5|states=6|type_roles=4|text_contrast_min=9.8641|marker_contrast_min=3.8792|external_refs=0|forbidden=0
    ODDSWELL_FIRST_WAGER_GRAPHIC_LANGUAGE_FOCUSED|result=PASS|outputs=5|states=6|type_roles=4|text_contrast_min=9.8641|marker_contrast_min=3.8792|external_refs=0|forbidden=0

The two clean-build logs are byte-identical, and their generated hash maps are identical. Reopen validation uses the standard-library XML parser and replays manifest byte sizes and SHA-256 values. It also rejects duplicate XML IDs; wrong dimensions, viewBoxes, contexts, state/shape maps, role counts, source colors, contrast, images, scripts, `foreignObject`, embedded style, `href`, URL/data references, Phase 1L.3j symbol tags, and forbidden player-world text.

## Original, compact, grayscale, and rejected visual evidence

The repository retains SVG source only. Chrome headless rendered all five accepted local SVGs at native dimensions, device scale `1`, with hidden scrollbars. Native Windows `System.Drawing` produced the true full-board compact downscale and grayscale diagnostic outside the repository.

| Temporary QA capture | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `Unified_1920x1080.png` | `1920x1080` | `80,277` | `AFBC897DA997550F57550437A8E40E507D21ECCA98722B2D080BC0869A7A9343` |
| `TicketBoothPrompt_1280x720.png` | `1280x720` | `29,251` | `1342F60546F7B01856754AB31EC8F22356AC4B0AB590D59BDA060AB86B9A705B` |
| `MatchWinnerSelection_1280x720.png` | `1280x720` | `35,703` | `0E96706F80DC1AC61BC42A0B7496D235F72D4444E5B23575A7AE0C0FBD2BB57B` |
| `PrecommitConfirmation_1280x720.png` | `1280x720` | `43,944` | `0B3370540232A218AD8B8F3F56450235BD0AEED101E91D6405883500E5852984` |
| `SettledReceipt_1280x720.png` | `1280x720` | `42,486` | `AD3B12CE351F1C3A7B66F6556C07D4A24D189B5044F7384306CF61310070079D` |
| `Unified_Compact_960x540.png` | `960x540` | `79,898` | `0B38EA3AA1058CAD29742277BB2CD09A5CBD468365163388AAE3D022E95F48E1` |
| `Unified_Grayscale_1920x1080.png` | `1920x1080` | `86,634` | `BC286DE270CBE0819A66753AEFBB1A9DCFF735FEBCC15C2E66D9C7333E213CD9` |

Independent original-resolution review confirmed complete panels, exact labels and values, visible margins between the unified match label and adjacent values, both full team labels bounded inside their cards, and no observed clipping or overlap. The grayscale diagnostic preserves all six distinct state silhouettes. The compact diagnostic is a true high-quality full-board downscale rather than a viewport crop; its fixed labels and shapes remain reviewable.

One pre-final visual candidate was rejected before documentation because the unified match label touched the adjacent stake value, Harbor City Waves overran its selection card, and the first compact capture was a viewport crop. A Coordinator-authorized layout-only correction changed only value spacing and font sizing. The rejected candidate is not accepted evidence; all IDs, copy, values, palette, states, shapes, roles, dimensions, filenames, and boundaries remained frozen in the accepted rebuild.

## Reused frozen regression and package evidence

No no-op Unreal build, automation, Python suite, Brain Admin run, cook, import, package, or packaged-route run was performed because this review changes no client, runtime, map, config, test, gameplay, package input, or prior review artifact. The frozen evidence ledger was re-read directly.

| Reused gate | Result | Retained evidence | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Full native Unreal automation | PASS `72/72` | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log` | `339,253` | `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Python phase0a | PASS `9/9` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log` | `882` | `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` |
| Python phase0b | PASS `2/2` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log` | `854` | `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` |
| Python phase0c | PASS `8/8` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log` | `880` | `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` |
| Python phase0d | PASS `46/46` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log` | `1,010` | `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` |
| Python phase1h | PASS `40/40` | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log` | `1,008` | `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` |
| Brain Admin `--check` | PASS | `C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log` | `43` | `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |

Python remains `9/9 + 2/2 + 8/8 + 46/46 + 40/40 = 105/105`. Production client diff remains `0` paths. `client/OddsWell/Content/Maps/SundaleGraybox.umap` remains `83,147` bytes with SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015`.

Retained package root `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows` remains `50` files and `1,050,423,644` bytes excluding `Saved`, with zero Python artifacts. Exact retained package identities are:

| Package artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `OddsWell.exe` wrapper | `171,520` | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| `OddsWell/Binaries/Win64/OddsWell.exe` | `341,390,336` | `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4` |
| `OddsWell/Content/Paks/OddsWell-Windows.ucas` | `208,147,760` | `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D` |

## Boundary and next gate

External references, images, fonts, textures, scripts, brands, new states, gameplay changes, wagering changes, settlement changes, production UI changes, and Phase 1L.3j symbol reuse remain exactly `0`. No Unreal, client, map, runtime, config, test, route, collision, navigation, schedule, offer, wager, settlement, ledger, history, Odds Bucks authority, team identity, production UI, package, prior review artifact, or Phase 1K behavior changed. The frozen Phase 0 simulation, Basketball AI Brain boundary, authoritative event log, equal-information boundary, server-owned settlement and Odds Bucks authority, and immutable inventory/history boundaries remain unchanged.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. Owner acceptance and a separate production promotion/integration gate remain required before any Phase 1L.3k graphic language reaches the product. After local commit and verified Notion closure, return to the Scope Director for exactly one new-nightly-batch Phase `5/6` independent review subphase. This review does not authorize roadmap Phase 2, Version 1, beta readiness, production readiness, final art, or accessibility readiness.
