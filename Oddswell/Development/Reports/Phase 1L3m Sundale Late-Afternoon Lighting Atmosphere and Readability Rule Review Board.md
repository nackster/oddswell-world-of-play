# Phase 1L.3m - Sundale Late-Afternoon Lighting, Atmosphere, and Readability-Rule Review Board

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONPRODUCTION OWNER REVIEW - OWNER ACCEPTANCE AND SEPARATE PRODUCTION PROMOTION/INTEGRATION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Python-standard-library builder presents the single source-locked weather contract `SUNDALE_DRY_LATE_AFTERNOON` across exactly three review scenarios: `COMMONS_OPEN_SUN`, `AWNING_PATTERNED_SHADE`, and `ROUTE_LONG_VIEW_WARM_HAZE`. Every scenario contains exactly five target reads: `STARTER_OFFWHITE_READ`, `SIGNAL_JACKET_READ`, `COBALT_ROUTE_MARK_READ`, `BURNT_ORANGE_THRESHOLD_READ`, and `LIMESTONE_TERRACOTTA_SURFACE_READ`.

The exact atmosphere values are directional intensity `5.0` at `5000 K`, skylight intensity `0.8` with color `#D8E4F0`, and fog density `0.003` with color `#E8C9A5`. Exactly one directional light, one skylight, and one exponential height fog are expected. These are source-bound current presentation values, not new authored values, a photometric calibration, or a weather/time-of-day system.

The frozen repository review root contains exactly seven files: one builder, one manifest, one provenance record, one unified `1920x1080` SVG, and three `1280x720` scenario SVGs. Fresh canonical temp-mirror verification passed two byte-identical clean builds, read-only XML reopen, focused validation, source binding, manifest replay, and exact artifact-hash comparison. Independent Coordinator inspection of all four originals, one true full-board `960x540` compact downscale, and one `1920x1080` grayscale diagnostic accepted complete framing, all five target reads in every scenario, no observed clipping or overlap, and preserved distinctions without color.

One stale early shared-Chrome Awning capture exposed only a partial board and was rejected. It is not accepted evidence and did not change the frozen review artifacts.

This is new-nightly-batch Phase `6/6`. Cursor is suitable in principle for isolated graphic tooling, but created task count is `0` because Execution completed the bounded objective and no independent nonredundant task remains.

## Scope authority and boundary

- [[Development/Beta Delivery Roadmap#Phase 1L - Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Development/Reports/Phase 1L1c Sundale Late Afternoon Atmosphere Pass|The current bounded Sundale late-afternoon atmosphere contract]].
- `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` as direct source authority.

This board answers one question: can the existing dry late-afternoon lighting/atmosphere contract retain the five selected readability targets across open sun, patterned shade, and long-view warm haze using bounded source-locked geometric review proxies? It does not change lighting, select final art, establish photometric accuracy, add a weather or time-of-day system, claim broad accessibility, prove runtime performance, or authorize production integration.

The exact claim flags are `production_claim=false`, `photometric_claim=false`, `lighting_change=false`, `weather_system=false`, `weather_variants=0`, `time_of_day_system=false`, `accessibility_ready=false`, `gameplay_change=false`, and `gameplay_additions=0`.

## Direct source and atmosphere facts

| Authority | Exact identity |
| --- | --- |
| Source | `client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp` |
| Source SHA-256 | `22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298` |
| Weather ID | `SUNDALE_DRY_LATE_AFTERNOON` |
| Directional light | intensity `5.0`; temperature `5000 K`; expected count `1` |
| Skylight | intensity `0.8`; color `#D8E4F0`; expected count `1` |
| Exponential height fog | density `0.003`; color `#E8C9A5`; expected count `1` |

Validation reopens the source file, requires its exact SHA-256 identity, and checks the exact material and `FSundaleAtmosphereSpec` source literals retained in `manifest.json`. The exact source palette is `#D8C8A9`, `#A65F47`, `#B9A783`, `#6D7F62`, `#315F79`, `#C46D3B`, and `#4D5051`; starter off-white and Signal Jacket slate/teal remain bound to source RGBA values `(0.92,0.90,0.82,1)`, `(0.12,0.18,0.22,1)`, and `(0.08,0.72,0.68,1)`.

## Exact scenario and target contract

| Output | Dimensions | Exact scenario | Required targets |
| --- | ---: | --- | ---: |
| `Unified.svg` | `1920x1080` | all three scenarios | all five per scenario |
| `COMMONS_OPEN_SUN.svg` | `1280x720` | `COMMONS_OPEN_SUN` | `5` |
| `AWNING_PATTERNED_SHADE.svg` | `1280x720` | `AWNING_PATTERNED_SHADE` | `5` |
| `ROUTE_LONG_VIEW_WARM_HAZE.svg` | `1280x720` | `ROUTE_LONG_VIEW_WARM_HAZE` | `5` |

| Target ID | Review read | Foreground / background | Contrast |
| --- | --- | --- | ---: |
| `STARTER_OFFWHITE_READ` | starter off-white against open-sky blue | `#EBE6D1` / `#315F79` | `5.5106:1` |
| `SIGNAL_JACKET_READ` | Signal Jacket teal against slate | `#14B8AD` / `#1F2E38` | `5.6364:1` |
| `COBALT_ROUTE_MARK_READ` | cobalt route mark against warm limestone | `#315F79` / `#D8C8A9` | `4.1906:1` |
| `BURNT_ORANGE_THRESHOLD_READ` | burnt-orange threshold against slate | `#C46D3B` / `#1F2E38` | `3.7166:1` |
| `LIMESTONE_TERRACOTTA_SURFACE_READ` | limestone/terracotta surface against charcoal | `#B9A783` / `#4D5051` | `3.4542:1` |

Every target/background pair exceeds the exact `3.0:1` review floor. Text/background contrast must remain at or above `4.5:1`. Clipping failures, containment failures, overlap failures, external references, and forbidden content remain `0`.

The SVGs use native geometry and generic native `sans-serif` text. They contain no image, raster, external font, texture, brand, script, `foreignObject`, animation, `href`, `src`, event attribute, URL/data reference, runtime import, or downloaded asset.

## Final artifact identities

Repository evidence root: `Oddswell/Art/Reviews/SundaleLateAfternoonLightingAtmosphereReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_review_board.py` | `18,068` | `547EAEF1D75CFA7B355D1D97EBA6BA633CBF1F70CD6D9961D16D4956F2200EEA` |
| `manifest.json` | `8,139` | `F7C8849E1C532B71BDFFB7777E133128CDB11A6E5922934CD7E332C22E8F6F8A` |
| `PROVENANCE.md` | `4,720` | `6D8AA11E218CB50D70F656E0AEFE92D4374C3EB239DAA6CA11A3584C8C7B7213` |
| `Unified.svg` | `6,471` | `877F553B6DAA52BA2417B89F92E0FC5CBE04984073ACF6413750C7BE59B42FB8` |
| `COMMONS_OPEN_SUN.svg` | `5,913` | `4EB2A0CED69DCCD1D5CA059E40AA86A604F9F1F7875635A8EBEC3C1F32894CF8` |
| `AWNING_PATTERNED_SHADE.svg` | `6,133` | `5F9487B2F16CBE46B164D878497995908E4BFE100D175129593737E78B656D98` |
| `ROUTE_LONG_VIEW_WARM_HAZE.svg` | `5,988` | `49FB44EE3604E3735A3C329A3D6EE31D268B8D70133D7E7E52D01091F5289882` |

The review root contains exactly these seven normal Git files and no raster, `.pyc`, `__pycache__`, external font, texture, image, or downloaded asset.

## Deterministic build, reopen, focused, source, and manifest evidence

Retained evidence root: `C:\tmp\OddsWellPhase1L3m\Evidence`.

To preserve the frozen repository board, both clean builds ran against `C:\tmp\OddsWellPhase1L3m\CanonicalMirror`, containing exact copies of the accepted builder and direct source file. The mirror builder and source identities equal the repository identities above. Both clean builds generated all seven expected mirror files, and every generated file was byte-identical to its frozen repository counterpart. Reopen and focused validation then ran directly against the frozen repository builder; both preserved the byte, SHA-256, and nanosecond-mtime identity of all seven repository files.

| Run | Exit | Exact stdout evidence | Exact stderr evidence |
| --- | ---: | --- | --- |
| Clean build 1 | `0` | `C:\tmp\OddsWellPhase1L3m\Evidence\CleanBuild01.stdout.log`; `260` bytes; SHA-256 `9FAB5F5E02E543262F364F93C85871B420D2E7DD9CA72653560EF4907EC75B34` | `C:\tmp\OddsWellPhase1L3m\Evidence\CleanBuild01.stderr.log`; `0` bytes; SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| Clean build 2 | `0` | `C:\tmp\OddsWellPhase1L3m\Evidence\CleanBuild02.stdout.log`; `260` bytes; SHA-256 `9FAB5F5E02E543262F364F93C85871B420D2E7DD9CA72653560EF4907EC75B34` | `C:\tmp\OddsWellPhase1L3m\Evidence\CleanBuild02.stderr.log`; `0` bytes; SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| Reopen | `0` | `C:\tmp\OddsWellPhase1L3m\Evidence\Reopen.stdout.log`; `250` bytes; SHA-256 `380AB7FB724855E1963F0C5C18337EFE37892A69E66E8D502B82EEE7DCEE3974` | `C:\tmp\OddsWellPhase1L3m\Evidence\Reopen.stderr.log`; `0` bytes; SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| Focused | `0` | `C:\tmp\OddsWellPhase1L3m\Evidence\Focused.stdout.log`; `252` bytes; SHA-256 `16DE63E2B13014B4877E51C1D9570B83A38A6CDF81907AE11E479F355DF59093` | `C:\tmp\OddsWellPhase1L3m\Evidence\Focused.stderr.log`; `0` bytes; SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

The two clean-build stdout logs are byte-identical. Exact marker lines are:

    OK mode=clean-build files=7 builder_bytes=18068 builder_sha256=547EAEF1D75CFA7B355D1D97EBA6BA633CBF1F70CD6D9961D16D4956F2200EEA
    OK mode=reopen files=7 builder_bytes=18068 builder_sha256=547EAEF1D75CFA7B355D1D97EBA6BA633CBF1F70CD6D9961D16D4956F2200EEA
    OK mode=focused files=7 builder_bytes=18068 builder_sha256=547EAEF1D75CFA7B355D1D97EBA6BA633CBF1F70CD6D9961D16D4956F2200EEA

Reopen and focused validation replay the exact source SHA, manifest data, embedded file sizes/hashes, weather/scenario/target IDs, dimensions/viewBoxes, atmosphere values, palette, contrasts, containment/overlap constraints, generic-font requirement, and forbidden tag/attribute/reference checks.

## Original, compact, grayscale, and rejected visual evidence

Temporary-only diagnostic root: `C:\tmp\OddsWellPhase1L3m\DiagnosticsFinal`.

| Temporary QA capture | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `Unified_Original_1920x1080.png` | `1920x1080` | `65,705` | `EE5DC31D1BEC06F8CCDFC0A691C172E7916609C6E8FE777F0C3A2563C30553F4` |
| `COMMONS_OPEN_SUN_Original_1280x720.png` | `1280x720` | `38,445` | `38BEDA42A313A3786C799FE2FEFCF175415484DA7EAE0F96B8146C88748ABB9F` |
| `AWNING_PATTERNED_SHADE_Original_1280x720.png` | `1280x720` | `48,964` | `35F7028BA6F05CD4E18474C17C238A866D9C9C50B1DA24E669A23BBBC0CC55D6` |
| `ROUTE_LONG_VIEW_WARM_HAZE_Original_1280x720.png` | `1280x720` | `39,510` | `BC81BE7D5880BE7801915A578C019B71F3725B2F24F36B19CF7B8372C0F79A1C` |
| `Unified_Compact_960x540.png` | `960x540` | `71,038` | `6D29CD29B85FDA51B4A9E4F575BE89C201BA07D5D840370B35F1395649247544` |
| `Unified_Grayscale_1920x1080.png` | `1920x1080` | `70,219` | `ECE4AD6053DA8A02A60F1D52818C58E167733D7673D867F3D2CE2A06CE9C6DE6` |

Independent inspection accepted all four originals, the true full-board compact downscale, and the grayscale diagnostic. All scenario plates, exact labels, atmosphere values, and five target cards were fully framed with no observed clipping or overlap. The three lighting contexts remain visually distinct, the five target reads remain separable in every scenario, and the grayscale diagnostic retains target distinctions without color.

An early stale shared-Chrome `AWNING_PATTERNED_SHADE` capture showed only a partial board. It was rejected and superseded by the accepted fresh native-dimension capture above. The rejected partial capture is not accepted evidence, does not support any claim, and did not alter repository art.

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

## Boundary and final gate

External references, images, external fonts, textures, brands, scripts, `foreignObject`, animation, URLs, runtime imports, weather variants, time-of-day behavior, gameplay additions, production changes, and photometric claims remain exactly `0`. No Unreal, client, map, runtime, config, test, route, collision, navigation, production lighting, weather, time-of-day, material, UI, package, prior review artifact, or Phase 1K behavior changed.

The Phase 0 simulation foundation, Basketball AI Brain boundary, authoritative event log, equal-information boundary, server-owned settlement and Odds Bucks authority, and immutable inventory/history boundaries remain frozen. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

Owner acceptance and a separate production promotion/integration gate remain required before any Phase 1L.3m lighting, atmosphere, or readability direction reaches the product. After local commit and verified Notion closure, perform only the read-only final Phase 1L.3h-m audit. No Phase 1L.3n or seventh new-nightly implementation is authorized. This review does not authorize roadmap Phase 2, Version 1, beta readiness, production readiness, final art or lighting, a weather/time-of-day system, a photometric claim, or accessibility readiness.
