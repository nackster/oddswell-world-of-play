# Phase 1L.3d Sundale Public Court Review Board

Date: 2026-08-10
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE AND PRODUCTION PROMOTION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Blender `4.5.5 LTS` builder now produces a bounded environmental-art review of Sundale's current public basketball court. The source preserves the authored `28.7x15.3 m` surface authority, locks exactly twelve noncanonical review identities, and renders one unified top plus four original `1.7 m` compass views.

This is new-art-batch Phase `3/6`. Cursor delegation count remains `0`. The review identities are not production catalog IDs, and no sample is approved for Unreal import or production use until the owner accepts and separately authorizes promotion.

## Scope authority and player-facing risk

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps `1`, `2`, and `5`.
- [[Design/Beta Game Bible#First-hour player journey]] > `2. Enter the first city`.
- [[Design/Beta Game Bible#World and city scope]].
- [[Design/Beta Game Bible#Art, music, and storytelling]].
- [[Design/Sundale Art Direction and Core Loop]].
- [[Design/Sundale Production Asset Scope#Public basketball court]].
- The owner-accepted Phase 1L.3a business-clustered planning baseline recorded in [[Development/Reports/Phase 1L3a Sundale Business Clustered Mega City Replacement Preview]].

The phase reduces the risk that the public-court landmark remains a generic rectangle or that later production work invents incompatible court pieces before its surface, edge, hoop, fence, and seating language can be reviewed together. It does not prove playability, collision, route clearance, accessibility, capacity, performance, interaction, subjective appeal, or final court art.

## Current court authority and exact review contract

- Production center: exactly `(-79, 150) m`, derived from the current authored Sundale court bands.
- Production surface: exactly `28.7x15.3 m`.
- Review-local center: exactly `(0, 0)` with bounds `x=-14.35..14.35 m`, `y=-7.65..7.65 m`.
- Geometry: Blender-native low-poly primitives only.
- Materials: only the seven accepted Sundale planning colors.
- Review instances: exactly one per identity.
- Triangle guard: `6,000` per identity; this is a review validator ceiling, not a production performance budget.

| Exact noncanonical review identity | Instances | Triangles |
| --- | ---: | ---: |
| `CourtSurface` | `1` | `12` |
| `CourtLineSet` | `1` | `84` |
| `CourtEdgeNorth` | `1` | `12` |
| `CourtEdgeSouth` | `1` | `12` |
| `CourtEdgeEast` | `1` | `12` |
| `CourtEdgeWest` | `1` | `12` |
| `CourtCenterTreatment` | `1` | `216` |
| `CourtHoopNorth` | `1` | `468` |
| `CourtHoopSouth` | `1` | `468` |
| `CourtFenceModule` | `1` | `144` |
| `CourtBenchClusterNorth` | `1` | `48` |
| `CourtBenchClusterSouth` | `1` | `48` |

The hoop identities require one explicit clarification. `CourtHoopNorth` and `CourtHoopSouth` retain their approved exact names, but the physical assemblies occupy the west/east ends of the `28.7 m` long axis. Both roots carry `orientation_role=LONG_AXIS_END`, their exact physical-end value, and `geographic_side_claim=false`. The review does not relabel production sides or assert false geography.

## Artifact evidence root and exact hashes

The repository evidence root is `Oddswell/Art/Reviews/SundalePublicCourtReviewBoard`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundalePublicCourtReviewBoard.blend` | `1,040,029` | `34383EBE8B1D3F4CCC1777CA3958897BC5C3C3F749CF470FE7640F496B317805` |
| `build_sundale_public_court.py` | `29,455` | `182D3E8329D8DBBAE97A31E132AE8616D964E8D62AE195D57750F84172B23301` |
| `manifest.json` | `4,975` | `EC6F76BA88347639A41E94686A6DB6122E306E3B35404A393AE3FB57CA298B3B` |
| `PROVENANCE.md` | `1,137` | `5F03B44A7074A83B36B0C854271090C33CF9BD580A9CD567DD1F8DFA1BB55C82` |

The Blend is covered by the existing Git LFS rule. Its prospective pointer is:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:34383ebe8b1d3f4ccc1777ca3958897bc5c3c3f749cf470fe7640f496b317805
size 1040029
```

No `.blend1` backup exists.

## Render evidence and visual audit

| Retained review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_TopDown_PublicCourt.png` | `1920x1080` | `2,047,194` | `9B9269C8A6802D1E36D3EAE4582241A615A462375F35D34D0C1EDF936F461091` |
| `renders/Cardinal_North_PublicCourt.png` | `1600x900` | `899,077` | `ACB9A44C88B9AE4C14EA6FC662C69E53FD4B223E63B50B3766C2CE5B57296B47` |
| `renders/Cardinal_East_PublicCourt.png` | `1600x900` | `946,364` | `5609C0C4EFB43CC57A00694942CC02CFBD82BBD21A8ABD5B71B7FE0F7D06B6D1` |
| `renders/Cardinal_South_PublicCourt.png` | `1600x900` | `896,850` | `75916D383E856CD30471A4BA56597B7F8F916A42D20679B1E4BE9DB9718FF264` |
| `renders/Cardinal_West_PublicCourt.png` | `1600x900` | `945,475` | `CFD19DD611DE172F0E5E2805A6A37CE7A5FE068562CBC39995715EB95C3EAC42` |

All five final PNGs were reopened at original resolution. The top view contains the complete `44x30 m` bounded review board and the exact `28.7x15.3 m` court. Every compass camera remains at `1.7 m`: North `(11,-32,1.7)` at `24 mm`, East `(-34,-10,1.7)` at `28 mm`, South `(-11,32,1.7)` at `24 mm`, and West `(34,10,1.7)` at `28 mm`. North/South show both hoop profiles and the two bench clusters with visible margin; East/West deliberately expose the open fence silhouette and long-axis court relationship. No retained frame clips the bounded court treatment.

Two candidate generations are explicitly rejected and excluded from canonical evidence. The first straight-axis cardinals let a near bench or fence dominate and left excessive sky. The first offset North/South candidates then clipped the far-right fence/support at the frame edge. The retained North/South pullback and `24 mm` lens change framing only; exact geometry, sample identities, transforms, surface authority, palette, top camera, East/West cameras, and scope boundaries are unchanged. The superseded local logs `BlenderBuildRejectedStraightAxis.log` and `BlenderBuildRejectedNSClip.log` are not approval evidence.

## Headless build, reopen, and focused evidence

The final headless build, saved-Blend reopen, and focused pass were executed from repository root `C:\Users\reali\Documents\SaaS\Oddswell`. Their machine-local evidence root is `C:\tmp\OddsWellPhase1L3d\Evidence`.

| Fresh phase-local evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `BlenderBuildFinal.log` | `3,867` | `EB624F7867F2CF9A33A958832908A1F294AD476119691AFF2F107674FDDF9509` |
| `BlenderBuildFinal.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderReopenValidate.log` | `767` | `C875963DA6FABB63E5E81C38A3D8DF3FE97D2F360E8C97CF65BE09771D6F40A0` |
| `BlenderReopenValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderFocusedValidate.log` | `768` | `738A76E1FB1A6875E63674F23889CD47D972C362070D6ED938097293BB2A9609` |
| `BlenderFocusedValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

```text
ODDSWELL_SUNDALE_PUBLIC_COURT_BUILD|result=PASS|artifacts=9|manual_input=false
ODDSWELL_SUNDALE_PUBLIC_COURT_VALIDATION|result=PASS|samples=12|instances=12|views=1_top+4_cardinal_1.7m|court_m=28.7x15.3|production_center_m=-79,150|hoop_ids_geographic_claim=false|engine=eevee|native_geometry=true|external_refs=0|textures=0|interiors=0|gameplay=0|production_catalog_changed=false|production_map_changed=false|production_route_changed=false|production_collision_changed=false|production_navigation_changed=false
ODDSWELL_SUNDALE_PUBLIC_COURT_REOPEN|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false
ODDSWELL_SUNDALE_PUBLIC_COURT_FOCUSED|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false
```

The validators lock exact review roots and identities, one-instance counts, triangle counts, current surface size/center/bounds, hoop identity-versus-orientation metadata, accepted palette-only materials, bounded native geometry, five camera/render names/dimensions/hashes, and zero external libraries, source images, textures, interiors, catalogs, armatures, volumes, gameplay, collision, or navigation additions.

## Reused frozen regression and package evidence

No no-op Unreal build, test, cook, or packaged route run was performed because the scoped diff changes no production client, runtime, map, test, config, collision, navigation, or package input. The immediately preceding verified Phase 1L.3c ledger remains applicable and its relevant production inputs are unchanged.

| Gate | Retained evidence | Result |
| --- | --- | --- |
| Full native Unreal automation | `C:\tmp\OddsWellPhase1L3aFinal\FullNativeFinal.log`, `339,253` bytes, SHA-256 `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` | REUSED PASS `72/72` |
| Python phase0a | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log`, `882` bytes, SHA-256 `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` | REUSED PASS `9/9` |
| Python phase0b | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log`, `854` bytes, SHA-256 `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` | REUSED PASS `2/2` |
| Python phase0c | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log`, `880` bytes, SHA-256 `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` | REUSED PASS `8/8` |
| Python phase0d | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log`, `1,010` bytes, SHA-256 `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` | REUSED PASS `46/46` |
| Python phase1h | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log`, `1,008` bytes, SHA-256 `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` | REUSED PASS `40/40` |
| Repository-pinned Python `3.12.13` frozen aggregate | the exact five retained logs immediately above | REUSED PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | `BrainAdmin.log`, `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` | REUSED PASS |
| Production client diff | current Phase 1L.3d scope contains `0` `client/` paths | PASS |
| `client/OddsWell/Content/Maps/SundaleGraybox.umap` | direct current file hash | PASS SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |

The retained canonical Phase 1L.2 package remains exact before postlaunch `Saved` output: `50` files, `1,050,423,644` bytes, zero Python artifacts, wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`, game executable SHA-256 `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`, and UFS container SHA-256 `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary

This review does not import or replace Unreal geometry, revise the accepted Phase 1L.3a city composition, change district/building/tower counts, alter the canonical `800 m` route, collision, or navigation, create a production asset catalog, or add basketball gameplay. It makes no final-art, production-placement, accessibility, capacity, performance, interaction, second-game-mode, or beta-readiness claim.

The frozen Phase 0 simulation, authoritative event log, equal-information boundary, Basketball Brain, Wager and Settlement Engine, Odds Bucks authority, immutable inventory/history, and current brain maturity remain untouched. Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

After commit and verified Notion closure, return to the Scope Director for exactly one new-art-batch Phase `4/6` independent review subphase. Owner acceptance is required before promoting or expanding these twelve samples into production. That promotion gate does not approve roadmap Phase 2 or block a later independent noncanonical review subphase.
