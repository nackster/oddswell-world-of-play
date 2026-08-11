# Phase 1L.3l - Current Beta Camera Composition Review Board

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONPRODUCTION OWNER REVIEW - OWNER ACCEPTANCE AND SEPARATE PRODUCTION PROMOTION/INTEGRATION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Python-standard-library builder produces exactly one unified `1920x1080` SVG, one city `1280x720` SVG, one stadium `1280x720` SVG, `manifest.json`, and `PROVENANCE.md`. Together with the builder, the review root contains exactly six files. Native SVG geometry presents four exact composition scenarios against two source-locked current camera contracts. It does not change either camera.

The city contract is `CITY_THIRD_PERSON_TRAILING`: boom `420`, attachment `+65`, collision `true`, pitch `-65..65`, continuous yaw, and FOV literal `ENGINE_DEFAULT_UNSET`. The stadium contract is `STADIUM_FIXED_BROADCAST`: location `(2400,-3000,1800)`, rotation `(-25,129,0)`, and fixed FOV `55`. The exact scenarios are `CITY_AVATAR_CLOTHING_READ`, `CITY_DESTINATION_LANDMARK_READ`, `STADIUM_FULL_COURT_ACTION_READ`, and `STADIUM_SCORE_EVENT_SAFE_AREA`.

Two clean builds are byte-identical. Standard-library XML reopen and focused validation pass without changing artifact bytes, sizes, or nanosecond mtimes. The validators lock a `5%` outer content margin, the stadium top `18%` reserved HUD band, complete proxy and label containment, proxy-label overlap `0`, text contrast `9.8641:1` against a `4.5:1` floor, graphic contrast `3.8792:1` against a `3.0:1` floor, and forbidden content `0`. Independent inspection of all three originals, one true full-board `960x540` compact downscale, and one `1920x1080` grayscale diagnostic found complete framing, visible margins, no observed clipping or overlap, and preserved silhouette/action separation without color.

This is new-nightly-batch Phase `5/6`. Cursor is suitable in principle for isolated graphic tooling, but task count is `0` because Execution completed the bounded objective and no independent nonredundant task remains.

## Scope authority and boundary

- [[Development/Beta Delivery Roadmap#Phase 1L - Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Decisions/DEC-007 Phase 1B Character Defaults|Approved third-person city camera and movement direction]].
- The current fixed stadium replay camera in `ReplayBenchmarkActor.cpp`.

This review answers one question: do the current city and stadium camera contracts support four bounded composition reads using simple source-locked proxies? It does not select or change a camera, invent a city FOV, lock a new lens, claim production placement, add gameplay, establish accessibility readiness, or authorize integration.

The exact claim flags are `production_claim=false`, `camera_change=false`, `lens_lock=false`, `accessibility_ready=false`, and `gameplay_change=false`. The explicit boundary ledger also retains `gameplay_additions=0`.

## Direct source facts

| Contract | Direct source | Source SHA-256 | Locked facts |
| --- | --- | --- | --- |
| `CITY_THIRD_PERSON_TRAILING` | `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` | `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298` | boom `420`; attachment `+65`; collision `true`; pitch `-65..65`; continuous yaw; FOV `ENGINE_DEFAULT_UNSET` |
| `STADIUM_FIXED_BROADCAST` | `client/OddsWell/Source/OddsWell/ReplayBenchmarkActor.cpp` | `CE070D7EC2EF7D94093B5CD943C271426BCF8A10B7D31D287BC32235FD8F3116` | location `(2400,-3000,1800)`; rotation `(-25,129,0)`; FOV `55`; fixed |

The city source sets no `FollowCamera` field of view, so the review records the literal `ENGINE_DEFAULT_UNSET`; it does not infer, display, or claim a numeric city FOV. Validation reopens both source files, requires the exact SHA-256 identities, and checks the exact source literals.

## Exact scenario, palette, and geometry contract

| Output | Dimensions | Exact scenarios |
| --- | ---: | --- |
| `Unified_CurrentBetaCameraComposition.svg` | `1920x1080` | all four |
| `City_CurrentBetaCameraComposition.svg` | `1280x720` | `CITY_AVATAR_CLOTHING_READ`, `CITY_DESTINATION_LANDMARK_READ` |
| `Stadium_CurrentBetaCameraComposition.svg` | `1280x720` | `STADIUM_FULL_COURT_ACTION_READ`, `STADIUM_SCORE_EVENT_SAFE_AREA` |

The exact palette is `#2C4250`, `#50B3AD`, `#FAE595`, `#999EA2`, and `#FAF8F0`. The SVGs use native `rect`, `circle`, `line`, `path`, and `polygon` proxies with generic native `sans-serif` text. They contain no image, external font, texture, brand, interior, script, `foreignObject`, animation, `href`, `src`, event attribute, URL/data reference, or external reference.

## Final artifact identities

Repository evidence root: `Oddswell/Art/Reviews/CurrentBetaCameraCompositionReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_current_camera_composition.py` | `19,825` | `FC4725CFBF8CE626A0936A40D24D39DDAA255783EFBC5C8BCCCFB9B7C4F11620` |
| `manifest.json` | `2,927` | `341BB7C7205FD777F404159EFE713711BCC6D6517D8F3355CF546904F97E0EA8` |
| `PROVENANCE.md` | `1,678` | `06B8C268AD076491A44A49BE42A0F9E34F50DEF74C65D735AF514A4CA301BD66` |
| `Unified_CurrentBetaCameraComposition.svg` | `6,398` | `8B35FC83A96AD9DA1EBD3E55EE560AD10CED4B728C798539C04A5DB8D4A933EA` |
| `City_CurrentBetaCameraComposition.svg` | `3,301` | `4D6DDE25C183E9BDF93AC1DAAA10B848D46DEDB8FF0FE6D694BFD4BA2F55CFE1` |
| `Stadium_CurrentBetaCameraComposition.svg` | `3,042` | `C06A6BACF6E5D09F1FAAADC37BD38F40831FCBC0730230EC3E5BADFCF86CA81D` |

The review root contains exactly these six normal Git files and no raster, `.pyc`, `__pycache__`, external font, texture, image, or downloaded asset.

## Deterministic build, reopen, and focused evidence

Retained evidence root: `C:\tmp\OddsWellPhase1L3l\Evidence`.

| Evidence | Exit | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `Syntax.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `CleanBuild01.log` | `0` | `446` | `0D5FE995235631696AA2F2D6216F1B3CF9D413AF06AE33022FCD04BBE724B10D` |
| `CleanBuild02.log` | `0` | `626` | `5636D3F3B70FBFF9E94D487C7228E4C7F8297C2B2D8995C160791511F3B490DE` |
| `ReopenXml.log` | `0` | `456` | `56824A762C4A33978A6787799E8C71C51EB00D7675C0F5EFC62498252AB5F621` |
| `FocusedValidation.log` | `0` | `450` | `92FF7BBB776CFBE6D144D6293F15378C14E462E57FE1838BF17D6F126D18926B` |
| `VisualDiagnostics.log` | `0` | `733` | `ED06BD0F06CC9DE795C4E16AA80629D16C6A974B962539B57BACF20DF9BE4FF5` |

    ODDSWELL_CURRENT_CAMERA_COMPOSITION_BUILD|result=PASS|files=6|renders=3|scenarios=4|text_contrast_min=9.8641|graphic_contrast_min=3.8792|outer_margin_percent=5|stadium_hud_top_percent=18|proxy_label_overlap=0|forbidden=0
    ODDSWELL_CURRENT_CAMERA_COMPOSITION_DETERMINISM|result=PASS|builds=2|byte_identical=true
    ODDSWELL_CURRENT_CAMERA_COMPOSITION_REOPEN_XML|result=PASS|files=6|renders=3|scenarios=4|text_contrast_min=9.8641|graphic_contrast_min=3.8792|outer_margin_percent=5|stadium_hud_top_percent=18|proxy_label_overlap=0|forbidden=0
    ODDSWELL_CURRENT_CAMERA_COMPOSITION_FOCUSED|result=PASS|files=6|renders=3|scenarios=4|text_contrast_min=9.8641|graphic_contrast_min=3.8792|outer_margin_percent=5|stadium_hud_top_percent=18|proxy_label_overlap=0|forbidden=0

## Original, compact, grayscale, and rejected evidence

Temporary-only diagnostic root: `C:\tmp\OddsWellPhase1L3l\Diagnostics`.

| Temporary QA capture | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `Unified_Original_1920x1080.png` | `1920x1080` | `74,337` | `6D26699C430F75152B9F11DB50D56508DC00BF2D876E06C95603CA0821F9C076` |
| `City_Original_1280x720.png` | `1280x720` | `34,312` | `F75A7954C79286236D6D32DC1344C99628D3D5A49ABBA0BDB7B85C20D9E9FA61` |
| `Stadium_Original_1280x720.png` | `1280x720` | `30,490` | `D5C5B98E49C0D6D2502FE4DFE9048D0BA508F8791CFD7EA8BE3E41FFE808DA43` |
| `Unified_Compact_960x540.png` | `960x540` | `96,443` | `171D9726BF5F85149D4FBDD9BB98B518DECC75D536530D050AA6048084E97E90` |
| `Unified_Grayscale_1920x1080.png` | `1920x1080` | `43,312` | `28330D6940C16ABD79BEBD0B2D818AFF2775F198AB157186CDDD07076EB8A542` |

Microsoft Edge headless rendered all three accepted local SVGs at native dimensions, device scale `1`, with hidden scrollbars. FFmpeg produced the true high-quality full-board compact downscale and grayscale diagnostic outside the repository. Original-resolution inspection confirmed complete proxies and labels, visible five-percent margins, a clear top-eighteen-percent stadium HUD band, and no observed clipping or overlap. The compact diagnostic retains the complete board. Grayscale retains distinct avatar, landmark, court, and action-marker shapes.

The pre-existing untracked builder skeleton was rejected before this execution. It parsed only a mode argument and exited with `builder expansion in progress`; it generated and validated nothing and is not retained evidence. Execution replaced it immediately with the accepted source-locked builder. An initial temp-only `960x540` browser viewport capture was also rejected because fixed-width SVG viewport behavior cropped the right and lower board; it was overwritten by the accepted true full-board raster downscale. Neither rejection changed accepted art.

## Reused frozen regression, package, and map evidence

No no-op Unreal build, automation, Python suite, Brain Admin run, cook, import, package, or packaged-route run was performed because this review changes no client, runtime, map, config, test, gameplay, package input, or prior review artifact. The frozen ledger was re-read directly.

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

Retained package root `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows` remains `50` files and `1,050,423,644` bytes excluding `Saved`, with zero Python artifacts.

| Package artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `OddsWell.exe` wrapper | `171,520` | `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD` |
| `OddsWell/Binaries/Win64/OddsWell.exe` | `341,390,336` | `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4` |
| `OddsWell/Content/Paks/OddsWell-Windows.ucas` | `208,147,760` | `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D` |

## Boundary and next gate

`gameplay_additions=0`. External references, images, external fonts, textures, brands, interiors, scripts, `foreignObject`, animation, URLs, and runtime changes remain exactly `0`. No Unreal, client, map, runtime, config, test, route, collision, navigation, camera, lens, production art, HUD, package, prior review artifact, or Phase 1K behavior changed.

The Phase 0 simulation foundation, Basketball AI Brain boundary, authoritative event log, equal-information boundary, server-owned settlement and Odds Bucks authority, and immutable inventory/history boundaries remain frozen. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

Owner acceptance and a separate production promotion/integration gate remain required before any Phase 1L.3l composition direction reaches the product. After local commit and verified Notion closure, return to the Scope Director for exactly one new-nightly-batch Phase `6/6` independent review subphase. This review does not authorize roadmap Phase 2, Version 1, beta readiness, production readiness, final art, a camera or lens change, or accessibility readiness.
