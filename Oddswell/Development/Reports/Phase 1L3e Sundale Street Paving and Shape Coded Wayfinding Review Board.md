# Phase 1L.3e Sundale Street, Paving, and Shape-Coded Wayfinding Review Board

Date: 2026-08-10
Branch: agent/phase-0d
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE AND PRODUCTION PROMOTION PENDING**
Cost: $0.00

## Outcome first

One deterministic Blender 4.5.5 LTS builder now produces a bounded 64x64 m four-arm intersection vignette containing exactly nine noncanonical street, curb, sidewalk, paver, and wayfinding review identities. The cobalt route marks use three different silhouettes: a straight bar with double chevrons, a right-angle bar with arrowhead, and a concentric ring target.

This is new-art-batch Phase 4/6. Cursor delegation count remains 0. The board is not the canonical 800 m route, its exact route distance is deliberately null, and no review identity is a production catalog ID.

## Scope authority and player-facing risk

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps 1, 2, and 5.
- [[Design/Beta Game Bible#First-hour player journey]] > 2. Enter the first city.
- [[Design/Beta Game Bible#World and city scope]].
- [[Design/Beta Game Bible#Art, music, and storytelling]].
- [[Design/Sundale Production Asset Scope#Streets, paving, and wayfinding]].
- The owner-accepted Phase 1L.3a business-clustered planning baseline.

The phase reduces the risk that Sundale's larger radial city depends on cobalt color alone or receives an inconsistent pedestrian edge language before production modeling. It does not prove route usability, travel distance, collision, navigation, accessibility, traffic behavior, capacity, performance, subjective readability, or final street art.

## Exact review contract

- Board: exactly 64x64 m.
- Composition: one four-arm intersection with a 12 m road width.
- Route authority: canonical=false and exact_distance_m=null.
- Geometry: Blender-native low-poly primitives only.
- Materials: a nonempty subset of the accepted Sundale planning palette; no texture inputs.
- Review instances: exactly one per identity.
- Triangle guard: 2,500 per identity; a validator ceiling, not a production budget.

| Exact noncanonical review identity | Shape or role | Triangles |
| --- | --- | ---: |
| StreetAsphaltModule | four-arm asphalt cross | 24 |
| CurbStraightModule | straight curb segments | 96 |
| CurbCornerModule | L-shaped corner curb | 96 |
| SidewalkStraightModule | straight sidewalk strips | 48 |
| SidewalkCornerModule | square corner aprons | 48 |
| PaverTransitionReference | two bounded paver transition bands | 96 |
| RouteMarkStraight | straight bar plus double chevrons | 60 |
| RouteMarkTurn | right-angle bar plus arrowhead | 25 |
| RouteMarkDestination | concentric ring, target, and four ticks | 428 |

All three route roots carry shape_distinct=true and color_only=false. Their exact shape identities are STRAIGHT_BAR_DOUBLE_CHEVRON, RIGHT_ANGLE_BAR_ARROW, and CONCENTRIC_RING_TARGET.

## Artifact evidence root and exact hashes

The repository evidence root is Oddswell/Art/Reviews/SundaleStreetWayfindingReviewBoard.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| SundaleStreetWayfindingReviewBoard.blend | 989,216 | 3FE950E9E512A675D6F43637120333E1401D8955BF882331DDBEBB78C59B0D4D |
| build_sundale_street_wayfinding.py | 28,856 | BA91C5A237591A58843FB3B8C41C1CE61E2EDBA325E3B6A58D8458F4B2EB5BCB |
| manifest.json | 5,210 | 2D3E7A89DAE7B69DCD2002541EC80544039C34C5B4DE5C6FB92756A9E8A91A51 |
| PROVENANCE.md | 1,118 | 048929276EB9C9A8E08891792AAC4A55BF4B5A3C5F5D0058B9FF35D89B01BDB1 |

The Blend is covered by the existing Git LFS rule. Its prospective pointer is:

    version https://git-lfs.github.com/spec/v1
    oid sha256:3fe950e9e512a675d6f43637120333e1401d8955bf882331ddbebb78c59b0d4d
    size 989216

No .blend1 backup exists.

## Render evidence and visual audit

| Retained review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| renders/Unified_TopDown_StreetWayfinding.png | 1920x1080 | 1,812,939 | 4F33A04700CEDFA3A119232A40D4D1E799C648717E711229E8C480859E405617 |
| renders/Cardinal_North_StreetWayfinding.png | 1600x900 | 977,700 | 6C73ED012F6DB63C7D6F4322AC61869749E2C2CA5B8639C9AB9AF4E71E894510 |
| renders/Cardinal_East_StreetWayfinding.png | 1600x900 | 960,385 | 6ED8B42E24CE9C1C4EB0766985C420EEB7E170CAB9A88BEF10EA2895E31B5449 |
| renders/Cardinal_South_StreetWayfinding.png | 1600x900 | 963,626 | C31475CF55DF8C33C4A74BFAE92F0B751900007D2B921BF11D84AB2B6EEB9C2D |
| renders/Cardinal_West_StreetWayfinding.png | 1600x900 | 983,451 | D13AB4D951AED19605A319CCF7EA1B17DE26F29CA3078207C5F1B0E395AE6622 |

All five retained PNGs were reopened at original resolution. The widened orthographic top retains the complete board and makes the three route-mark silhouettes identifiable without color. The four perspective cameras remain at exact z=1.7 m, sit just outside the board on the four axes at plus or minus 36 m, and use a 12 mm lens with zero shift. Their roads occupy the lower frame while complete curb and sidewalk edges converge into the four-arm intersection; both paver transitions and all three complete route-mark silhouettes remain inside-frame. Planar marks still foreshorten at ground level, so the top remains the primary shape-comparison frame.

The first distant 52 m/24 mm eye-level candidates were rejected because the intersection collapsed into a thin horizon strip above empty foreground. An inside-board 28 m/16 mm candidate improved curb scale but pushed the nearest route symbol against the frame edge; a lens-shift candidate then displaced useful context. The retained outside-board 36 m/12 mm cardinals preserve visible road/curb/sidewalk/paver relationships and complete marks with margin while keeping exact 1.7 m height. A saved-Blend validation failure also exposed that Blender purges an unused seventh palette proxy; the validator was corrected to require a nonempty subset of accepted palette materials rather than require unused datablocks. No correction changes geometry, transforms, IDs, palette, filenames, top camera, scope, or authority.

## Headless build, reopen, and focused evidence

Final phase-local evidence is under C:\tmp\OddsWellPhase1L3e\Evidence.

| Fresh evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| BlenderBuildFinal.log | 8,604 | DB289203148F0CFCE365D3852FCFA16B7336C2A78D38BC9255DDE3A46065A7D7 |
| BlenderBuildFinal.stderr.log | 0 | E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855 |
| BlenderReopenValidate.log | 1,798 | D6A48D4B3541857F4D767256658EF474E5F1CAC0B7C6E82616B0B54E71A14BE5 |
| BlenderReopenValidate.stderr.log | 0 | E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855 |
| BlenderFocusedValidate.log | 1,800 | F58D6178779547D696EC792BC3C121C2D42E823F8B999942CA4A6F16066292F8 |
| BlenderFocusedValidate.stderr.log | 0 | E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855 |

    ODDSWELL_SUNDALE_STREET_WAYFINDING_BUILD|result=PASS|artifacts=9|manual_input=false
    ODDSWELL_SUNDALE_STREET_WAYFINDING_VALIDATION|result=PASS|samples=9|instances=9|board_m=64x64|intersection_arms=4|views=1_top+4_cardinal_1.7m|shape_distinct=true|color_only=false|canonical=false|exact_distance_m=null|engine=eevee|native_geometry=true|external_refs=0|textures=0|interiors=0|brands=0|gameplay=0|traffic=0|vehicles=0|generalized_road_system=0|production_catalog_changed=false|production_map_changed=false|production_route_changed=false|production_collision_changed=false|production_navigation_changed=false|package_changed=false
    ODDSWELL_SUNDALE_STREET_WAYFINDING_REOPEN|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false
    ODDSWELL_SUNDALE_STREET_WAYFINDING_FOCUSED|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false

The validators lock exact roots and IDs, one-instance counts, triangle counts, 64x64 m bounds, four-arm/12 m road metadata, three distinct route-mark silhouettes, accepted-palette-only materials, five camera/render identities and hashes, noncanonical/null-distance authority, and every zero boundary.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, or packaged route run was performed because this diff changes no client, runtime, map, test, config, collision, navigation, or package input. The immediately preceding verified Phase 1L.3d ledger remains applicable.

| Reused gate | Result | Retained evidence | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Full native Unreal automation | PASS 72/72 | C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log | 339,253 | 94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4 |
| Python phase0a | PASS 9/9 | C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log | 882 | A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33 |
| Python phase0b | PASS 2/2 | C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log | 854 | 58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2 |
| Python phase0c | PASS 8/8 | C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log | 880 | D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99 |
| Python phase0d | PASS 46/46 | C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log | 1,010 | 150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A |
| Python phase1h | PASS 40/40 | C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log | 1,008 | 19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811 |
| Brain Admin --check | PASS | C:\tmp\OddsWellPhase1L3aFinal\BrainAdmin.log | 43 | D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44 |

The five repository-pinned Python 3.12.13 logs total 9 + 2 + 8 + 46 + 40 = 105/105. Each retained file above was re-read directly before this report was closed; no brain or simulator input changed.

- Production client diff: 0 paths.
- client/OddsWell/Content/Maps/SundaleGraybox.umap: unchanged SHA-256 180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015.
- Retained package root: C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows, before postlaunch Saved output by recursively excluding every Saved subtree.
- Retained package audit: 50 files, 1,050,423,644 bytes, zero Python artifacts.
- Wrapper C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell.exe: SHA-256 5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD.
- Game executable C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell\Binaries\Win64\OddsWell.exe: SHA-256 0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4.
- UFS container C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows\OddsWell\Content\Paks\OddsWell-Windows.ucas: SHA-256 547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D.

## Preserved boundary

This review does not redraw or measure the canonical 800 m route, import or replace Unreal geometry, add collision or navigation, create a generalized road system, add traffic/transit/moving or drivable vehicles, revise the accepted city counts, or create production catalog IDs. It adds no textures, external references, fonts, brands, interiors, business behavior, economy, service, or gameplay.

The frozen Phase 0 simulation, authoritative event log, equal-information boundary, Basketball Brain, Wager and Settlement Engine, Odds Bucks authority, immutable inventory/history, and current brain maturity remain untouched. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

After commit and verified Notion closure, return to the Scope Director for exactly one new-art-batch Phase 5/6 independent review subphase. Owner acceptance is required before promoting or placing these nine review identities in production. That promotion gate does not authorize roadmap Phase 2.
