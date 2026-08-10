# Phase 1L.3c Sundale Central Commons Landscape Kit Review

Date: 2026-08-10
Branch: `agent/phase-0d`
Status: **COMPLETE FOR BOUNDED NONCANONICAL OWNER REVIEW - OWNER ACCEPTANCE AND PRODUCTION PROMOTION PENDING**
Cost: `$0.00`

## Outcome first

One deterministic Blender `4.5.5 LTS` builder now produces a noncanonical landscape-kit review inside the owner-accepted `600x420 m` Central Commons planning footprint. The board locks exactly nine review IDs, four lawn quadrants, two broad step-free cross-paths, bounded landscape-instance counts, and one unified top plus four cardinal review views.

This is new-art-batch Phase `2/6`. Cursor delegation count remains `0`. The review IDs are not production catalog IDs, and no asset is approved for production use until the owner accepts and separately authorizes promotion.

## Scope authority and player-facing risk

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps `1`, `2`, and `5`.
- [[Design/Beta Game Bible]] sections `First-hour player journey > 2. Enter the first city`, `World and city scope`, and `Art, music, and storytelling`.
- [[Design/Sundale Art Direction and Core Loop]].
- [[Design/Sundale Production Asset Scope]].
- The owner-accepted Phase 1L.3a business-clustered planning baseline recorded in [[Development/Reports/Phase 1L3a Sundale Business Clustered Mega City Replacement Preview]].

The bounded review reduces the risk that the huge central park remains an unreadable empty placeholder or that later production work invents an oversized prop catalog before circulation and visual rhythm are approved. It does not prove accessibility, density, collision, navigation, performance, subjective usability, or final landscaping.

## Exact planning and sample contract

- Footprint: exactly `600x420 m`.
- Lawn structure: exactly four rectangular lawn quadrants.
- Circulation: exactly two `48 m`-wide cross-paths, one east-west and one north-south.
- Step-free planning condition: both path tops and all lawn tops share elevation `0.30 m` in the review source.
- Bollard demonstration: eight short edge bollards, all tagged nonblocking and placed outside the two cross-paths.
- Geometry: Blender-native low-poly primitives only.
- Materials: only the seven accepted Sundale planning colors.

| Exact noncanonical review ID | Instances | Bound | Triangles |
| --- | ---: | ---: | ---: |
| `CommonsPaverBrick` | `2` | exactly two cross-path regions | `24` |
| `CommonsShadeTreeRound` | `4` | tree total `12/12` | `624` |
| `CommonsShadeTreeWide` | `4` | tree total `12/12` | `1,104` |
| `CommonsShadeTreeColumnar` | `4` | tree total `12/12` | `624` |
| `CommonsLowPlanter` | `8` | `8/10` | `192` |
| `CommonsBench` | `8` | `8/8` | `192` |
| `CommonsPedestrianLamp` | `12` | `12/12` | `1,392` |
| `CommonsLitterBin` | `4` | `4/6` | `352` |
| `CommonsBollardEdge` | `8` | short nonblocking demonstration | `288` |

Every category remains below the phase-local `8,000`-triangle ceiling. This ceiling is a validator guard for the review board, not a production performance budget.

## Artifact evidence root and exact hashes

The repository evidence root is `Oddswell/Art/Reviews/SundaleCentralCommonsLandscapeKit`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleCentralCommonsLandscapeKit.blend` | `1,536,482` | `70C4345782CA9BCFA46190228D2B2F360BF90CF726AE47ABF5BA94EABC9CB115` |
| `build_sundale_central_commons.py` | `29,439` | `F328F393418913BDA265CE27D53F6ED0A0B6405ED64F659E26DF78834C780CF7` |
| `manifest.json` | `4,219` | `F56E0833F4375779D8C59D7A2DEA3ED2FBAFB59F465187CF1D94A187EC59094F` |
| `PROVENANCE.md` | `931` | `183D38816F6B31638E2D51FFD052E560F85F896459F4D07F4C87B581A70F25EC` |

The Blend is covered by the existing Git LFS rule. Its exact prospective pointer is:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:70c4345782ca9bcfa46190228d2b2f360bf90cf726ae47abf5ba94eabc9cb115
size 1536482
```

No `.blend1` backup exists.

## Render evidence and visual audit

| Retained review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `renders/Unified_TopDown_CentralCommons.png` | `1920x1080` | `1,842,790` | `44E3CBB70F54714EEA10029850846CB618E7BFD0568CDEBD43F2254E76CA3270` |
| `renders/Cardinal_North_CentralCommons.png` | `1600x900` | `1,092,308` | `4090D175D59B135FBCCF78192132C9EB08A2E8C1E3ABB6B9DD9EFF480EA3EBC1` |
| `renders/Cardinal_East_CentralCommons.png` | `1600x900` | `1,102,018` | `84DDA96DC71EC2A591578DF28C2C5DC21144A04E0EAB4E35985E2C757D18F6C0` |
| `renders/Cardinal_South_CentralCommons.png` | `1600x900` | `1,084,582` | `F6A2FF7DD600C35361BFEF4E365638C0D6C372CA03CE1673207B68F426E43EB0` |
| `renders/Cardinal_West_CentralCommons.png` | `1600x900` | `1,113,006` | `6431A99F66C8D3D99F261875C6C70582C5312827161AFFD8BE75A0B6A8411D7C` |

All five refreshed PNGs were reopened at original resolution after the final build. The unified top uses an `800 m` orthographic framing scale and contains the complete `600x420 m` footprint. The four cardinal cameras use exact `1.7 m` eye height, deterministic perspective framing, and measured `1.4 m` minimum three-dimensional clearance from every review-sample AABB. North is `(0, 50, 1.7) m` at `35 mm`; East is `(50, 0, 1.7) m` at `28 mm`; South is `(0, -50, 1.7) m` at `35 mm`; West is `(-50, 0, 1.7) m` at `28 mm`. East/West use the wider lens to retain visible margin around the deliberately featured lamps, tree profiles, bin, planter, bench, and path edges. Each pedestrian frame shows a broad unobstructed path segment and a reviewable mix of complete landscape silhouettes.

Three candidate generations are explicitly rejected and excluded from canonical evidence: the initial elevated cardinal board views duplicated the top plan; the first straight-path `1.7 m` views left the kit horizon-small with excessive empty foreground/sky; and the first diagonal East/West views clipped nearby foreground lamp/tree silhouettes. Their outputs and any earlier machine-local build logs are superseded and must not be used for approval.

## Headless build, reopen, and focused evidence

The final headless build, saved-Blend reopen, and focused pass were executed from repository root `C:\Users\reali\Documents\SaaS\Oddswell`. Their machine-local evidence root is `C:\tmp\OddsWellPhase1L3c\Evidence`. Only the six exact paths below are retained phase evidence; earlier candidate build logs in that directory are noncanonical and superseded.

| Fresh phase-local evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `BlenderBuildFinal.log` | `7,418` | `DBE9F40148D41640AF0FC9BD80A8BEA590D3323183D4663D56FDD06782BBCB74` |
| `BlenderBuildFinal.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderReopenValidate.log` | `1,396` | `A0BE8DECFA0B1E6D97B9B578BD65A01C1A6DF36B7D662DBE693AEE3985B30A86` |
| `BlenderReopenValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |
| `BlenderFocusedValidate.log` | `1,398` | `0FA7F748241271C83343781FCB672F07E11C9E57307AA25CA1B6AD4347D0088E` |
| `BlenderFocusedValidate.stderr.log` | `0` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` |

```text
ODDSWELL_SUNDALE_COMMONS_BUILD|result=PASS|artifacts=9|manual_input=false
ODDSWELL_SUNDALE_COMMONS_VALIDATION|result=PASS|samples=9|lawns=4|paths=2_step_free|trees=12/12|planters=8/10|benches=8/8|lamps=12/12|bins=4/6|bollards=8_nonblocking|views=1_top+4_cardinal|footprint_m=600x420|engine=eevee|external_refs=0|interiors=0|gameplay=0|production_catalog_changed=false|production_map_changed=false|production_route_changed=false
ODDSWELL_SUNDALE_COMMONS_REOPEN|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false
ODDSWELL_SUNDALE_COMMONS_FOCUSED|result=PASS|manifest=true|artifact_hashes=8|render_hashes=5|manual_input=false
```

The validators lock exact review roots and IDs, instance counts, triangle counts, `600x420 m` bounds, four lawns, two broad step-free cross-paths, nonblocking bollard metadata, accepted palette-only materials, five camera/render identities and hashes, and zero external libraries, source images, textures, interiors, catalogs, armatures, volumes, or gameplay additions.

## Concrete reused production-evidence ledger

No no-op Unreal build, production test, or package rerun was performed because this phase changes no production client, runtime, map, test, or config path. The proportional regression evidence remains retained under `C:\tmp\OddsWellPhase1L3aFinal`; the canonical package evidence root remains `C:\tmp\OddsWellPhase1L2Final\PackageFinal\Windows`.

| Gate | Retained evidence | Result |
| --- | --- | --- |
| Full native Unreal automation | `FullNativeFinal.log`, `339,253` bytes, SHA-256 `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` | REUSED PASS `72/72`, exit `0`, failures `0` |
| Python phase0a | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0a.log`, `882` bytes, SHA-256 `A4BCEFFC06B3887DF5C1D3D420724A3367108822CF31FF53FBD19EB3A2914E33` | REUSED PASS `9/9` |
| Python phase0b | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0b.log`, `854` bytes, SHA-256 `58A72D8E01A514EDDF3F324BD738FD13AEE2E6561FF60C6FAB06AC5ABE77EBF2` | REUSED PASS `2/2` |
| Python phase0c | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0c.log`, `880` bytes, SHA-256 `D02E0C94D4EC980F65884B364D7AE49DC09CD41DB2D3B84257C01D2A7045AF99` | REUSED PASS `8/8` |
| Python phase0d | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase0d.log`, `1,010` bytes, SHA-256 `150CAE3A2A8638682932475570FFC455C108C151849C66D7845D570559BBFD8A` | REUSED PASS `46/46` |
| Python phase1h | `C:\tmp\OddsWellPhase1L3aFinal\Python_phase1h.log`, `1,008` bytes, SHA-256 `19A7E63E549F64B5B1FF2D1BAE507A2701DD8E2D0FE4FDEFD792D757562C7811` | REUSED PASS `40/40` |
| Repository-pinned Python `3.12.13` aggregate | the exact five retained logs immediately above | REUSED PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | `BrainAdmin.log`, `43` bytes, SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` | REUSED PASS |
| Production client diff | current Phase 1L.3c scope contains `0` `client/` paths | PASS |
| `client/OddsWell/Content/Maps/SundaleGraybox.umap` | direct file hash | PASS SHA-256 `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |

The retained canonical Phase 1L.2 package remains exact before any postlaunch `Saved` output:

- files: `50`;
- bytes: `1,050,423,644`;
- Python artifacts: `0`;
- wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable SHA-256: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS container SHA-256: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary

This review does not import or replace Unreal geometry, revise the accepted Phase 1L.3a city composition, change district/building/tower counts, change the production `800 m` route, create a production asset catalog, or add park gameplay. It makes no final-art, production placement, collision, navigation, accessibility, capacity, performance, density, vegetation, lighting, interaction, or beta-readiness claim.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

After commit and verified Notion closure, return to the Scope Director for exactly one new-art-batch Phase `3/6` independent review subphase. Owner acceptance is required before promoting or expanding these nine review samples into a production landscape family. That promotion gate does not approve roadmap Phase 2 or block a later independent noncanonical review subphase.
