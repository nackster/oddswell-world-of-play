# Phase 1L.3j — Two-Team Color-and-Shape Recognition Review Board

Date: 2026-08-11
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW — OWNER IDENTITY LOCK AND SEPARATE PRODUCTION PROMOTION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Python-standard-library builder produces one unified `1920x1080` SVG and two team `1280x720` SVG closeups for exactly the two existing team labels: Harbor City Waves and Mesa Vista Sol. Harbor uses the exact `#315F79` / `#D8C8A9` palette with a three-band wave. Mesa uses the exact `#A65F47` / `#B9A783` palette with a radial sun composed of one central disc and twelve rays. Charcoal `#20272B` and off-white `#F7F3EA` are the only support colors.

Each team appears in exactly four logical contexts: identity tile, compact matchup row, Match Winner selection card, and score/receipt token, for eight logical contexts total. Every instance pairs the complete written team label with its distinct wave or sun geometry, so the proposed recognition system does not depend on color alone.

Independent inspection of the three original-resolution captures, a `960x540` compact unified diagnostic, and a `1920x1080` grayscale diagnostic found complete framing, no observed clipping or overlap, readable labels at the fixed captured sizes, and unmistakable wave-versus-sun recognition without color. This is new-nightly-batch Phase `3/6`. Cursor is suitable in principle, but Execution completed the bounded scope without a nonredundant delegation, so Cursor task count is `0`.

## Scope authority and boundary

- [[Development/Beta Delivery Roadmap#Phase 1L — Content, presentation, and accessibility|Phase 1L delivery steps 1, 2, and 5]].
- [[Design/Beta Game Bible#Basketball and wagering|The existing two-team basketball and wager context]].
- [[Design/Beta Game Bible#Art, music, and storytelling|The bounded beta art/storytelling direction]].
- [[Design/Sundale Production Asset Scope#Team recognition art is a separate approval track|The isolated team-recognition review boundary]].

The board answers one review question: can the two existing team names remain recognizable across four compact presentation contexts through exact palette plus distinct geometry? It does not lock a final identity, approve a logo, add a team, change a schedule or wager, establish trade dress, create a jersey/mascot/arena/crowd treatment, or authorize production integration.

## Exact identity and context contract

| Order | Review ID | Exact label | Exact palette | Color-independent system |
| ---: | --- | --- | --- | --- |
| 1 | `harbor_city_waves` | Harbor City Waves | `#315F79` / `#D8C8A9` | three parallel wave bands |
| 2 | `mesa_vista_sol` | Mesa Vista Sol | `#A65F47` / `#B9A783` | one central disc with twelve radial rays |

| Context ID | Visible context label | Harbor instances | Mesa instances |
| --- | --- | ---: | ---: |
| `identity_tile` | Identity tile | `1` | `1` |
| `compact_matchup_row` | Compact matchup row | `1` | `1` |
| `match_winner_selection_card` | Match Winner selection card | `1` | `1` |
| `score_receipt_token` | Score / receipt token | `1` | `1` |

The manifest locks exactly two IDs, two labels, two recognition systems, four contexts per team, and eight logical contexts. The unified render contains all eight once; each team closeup contains that team's four once. The generic native `sans-serif` family is used without an embedded or external font. All text is charcoal on off-white or off-white on charcoal; the exact locked pair measures `13.6769:1`, above the required `4.5:1` minimum.

## Final artifact identities

Repository evidence root: `Oddswell/Art/Reviews/TwoTeamRecognitionReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `build_two_team_recognition.py` | `18,975` | `AF708AD547274FA4C01A18A6BFA85759A81314F17E4FCBF5859BBE4118FBB7B1` |
| `TwoTeamRecognitionReviewBoard.svg` | `20,524` | `B1006B99AEC6FC87344CEDDD7ABCB74506294B95DC19E7C9D527B33E73A02BF4` |
| `HarborCityWaves.svg` | `8,238` | `9245A7483F32589C94C2594E25E2DC7905688535198C1A66B1EA9D8D46C0E40B` |
| `MesaVistaSol.svg` | `12,961` | `FA51C6F1A6F69D45578C5215CBED98DB6CAA36222371F0BFE92741065CE9E6CF` |
| `manifest.json` | `3,917` | `B444A243CEB75C516F2E13F6B501ABB194DB963BC5B98056A4DCAEA6D63F9FBA` |
| `PROVENANCE.md` | `981` | `30058F51A3FDC29219E5C252332DD656C3DAB5C347A679967F689249B059C9BF` |

These text/SVG artifacts use normal Git storage; no new LFS pattern or binary artifact is required. The review root contains no `.pyc`, `__pycache__`, image, texture, font, script library, or generated raster.

## Deterministic build and focused XML evidence

Retained evidence root: `C:\tmp\OddsWellPhase1L3j\Evidence`.

| Evidence | Exit | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `CanonicalBuild.log` | `0` | `180` | `3D2D1F47D4704FE995E8185468FBF4B764309FBBF443DE643C3BB72C80EF1130` |
| `CanonicalBuild.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `CleanRebuild.log` | `0` | `180` | `3D2D1F47D4704FE995E8185468FBF4B764309FBBF443DE643C3BB72C80EF1130` |
| `CleanRebuild.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `FocusedValidate.log` | `0` | `182` | `BEA905AC450D2810F422F66DE5793ED8A17E2E6020738DDB72678FF662D6F617` |
| `FocusedValidate.stderr.log` | `0` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

    ODDSWELL_TWO_TEAM_RECOGNITION_BUILD|result=PASS|renders=3|contexts=8|manual_input=false
    ODDSWELL_TWO_TEAM_RECOGNITION_FOCUSED|result=PASS|ids=2|systems=2|contexts=8|forbidden=0

Two separate `--clean` runs removed and recreated all five generated outputs. Every generated SHA-256 remained identical. Focused validation reopened all three SVGs with the Python standard-library XML parser and locked exact viewBoxes, dimensions, team/context occurrence counts, palettes, written labels, three Harbor band paths per context, one Mesa core plus twelve rays per context, generic native font use, and contrast at least `4.5:1`.

Validation rejects SVG `script`, `image`, `foreignObject`, animation and `set` elements; `href`/`src`; event attributes; `url()`; `@font-face`; and JavaScript references. The manifest records zero external assets, images, textures, references, libraries, downloads, fonts, brands, trade dress, jerseys, mascots, arenas, crowds, animation, runtime imports, gameplay changes, and production changes.

## Original, compact, and grayscale visual evidence

The repository retains SVG source only. Chrome headless rendered the accepted local SVGs at device scale `1` with hidden scrollbars to temporary PNGs outside the repository. The compact and grayscale diagnostics derive only from the accepted unified PNG through native Windows `System.Drawing`.

| Temporary QA capture | Method / dimensions | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `TwoTeamRecognitionReviewBoard.png` | Chrome local SVG, `1920x1080` viewport | `156,036` | `4131B089F640E7A3B6C2706DAB1F42EAA2F70AD817DC9B73E3E9B3604C1180F3` |
| `HarborCityWaves.png` | Chrome local SVG, `1280x720` viewport | `67,116` | `8230C1C10C08EC5713706811E1485F4DAB4B799873D8FEF0E99CBD8AE201918A` |
| `MesaVistaSol.png` | Chrome local SVG, `1280x720` viewport | `54,208` | `FFC87BD076AABD2D180EC2B173C1FBA2CFE3741F3504F70A6F4E20ED1F08FC07` |
| `TwoTeamRecognitionReviewBoard_Compact_960x540.png` | high-quality bicubic downscale, `960x540` | `184,680` | `77A0DEEF47B31387550B2145F5BAEF617272F4ECC7A643073482C3FE6A15F747` |
| `TwoTeamRecognitionReviewBoard_Grayscale_1920x1080.png` | luminance matrix `0.299/0.587/0.114`, `1920x1080` | `132,251` | `478D9D482A24B97CCA1421CB60B3E5E6296977A7F044C706D595AEE0AB028FFA` |

Independent review opened all five captures at original pixel size. It confirmed complete framing, complete labels, no observed clipping/overlap, compact readability in that fixed diagnostic, and distinct wave/sun recognition in grayscale. This is bounded visual evidence, not broad accessibility, localization, device, minimum-PC, subjective-usability, or final-identity proof.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, import, Brain, package, or packaged-route run was performed because this phase changes no client, runtime, map, config, test, gameplay, package input, or prior review artifact. The frozen production ledger was re-read directly.

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

No Unreal, client, map, runtime, config, test, schedule, wager, score, receipt, route, collision, navigation, team catalog, production identity, logo, jersey, mascot, arena, crowd, animation, import, package, gameplay, economy, brand, service, or prior review artifact changed. Phase 1L.3a remains authoritative only at its accepted planning level.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived. Owner identity lock and a separate production promotion/integration gate remain required before either Phase 1L.3j system becomes production team art. After local commit and verified Notion closure, return to the Scope Director for exactly one new-nightly-batch Phase `4/6` independent review subphase. This review makes no beta-readiness, production-readiness, final-art, accessibility-readiness, Version 1, or roadmap Phase 2 claim.
