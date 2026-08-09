# Phase 1L.3a Sundale Citywide Blender Massing Review Board

Date: 2026-08-08
Branch: `agent/phase-0d`
Status: REVIEW ARTIFACT COMPLETE; OWNER MASSING DECISION OPEN
Cost: `$0.00`

## Outcome first

OddsWell now has one bounded, noncanonical citywide Blender board for reviewing Sundale's composition before detailed production modeling begins. It includes exactly one top-down and three true eye-level views. Nothing was imported into the production Unreal map or runtime.

This completes new-art-batch Phase `1/6` only. It does not approve the proposed scenic placements or authorize Phase 2.

## Scope authority

- [[Development/Beta Delivery Roadmap]] Phase 1L delivery steps `1`, `2`, and `5`.
- [[Design/Beta Game Bible]]: `First-hour player journey > 2. Enter the first city`, `World and city scope`, and `Art, music, and storytelling`.
- [[Design/Sundale Art Direction and Core Loop]].
- [[Design/Sundale Production Asset Scope]].

The reduced player-facing risk is expensive detailed modeling against an unreviewed whole-city composition.

## Delivered review artifact

The phase-local directory [[Art/Reviews/SundaleCitywideMassing/PROVENANCE|Sundale massing provenance]] contains:

- one original noncanonical `SundaleCitywideMassing.blend` source;
- one standard-library-plus-`bpy` build/validation script;
- one machine-readable manifest with source and render hashes;
- exactly four RGB PNG outputs: one `1280x900` top-down and three wide `1280x480` eye-level views;
- separate `EXISTING_AUTHORIZED`, `PROPOSED_SCENIC`, and `REVIEW_GUIDES` collections.

The script reconstructs these exact authorized review facts:

- district: `340x280 m`;
- commons: `140x90 m`;
- route: `800 m`, `12` ordered points, and four perimeter segments;
- shortcuts: `2`;
- required destination anchors: `7` — Studio, Job, Clothing Store, Arena, Ticket Booth, Public Court, and Furniture Store;
- source authored-map count recorded for provenance: `45` actors.

The proposal is capped at exactly ten nonenterable scenic shells:

| Family | Count | Height band |
| --- | ---: | --- |
| Warm limestone | 4 | 4-6 stories |
| Muted terracotta | 3 | 4-6 stories |
| Charcoal / neutral | 3 | 3-5 stories |
| **Total** | **10** | **3-6 stories** |

Every proposed footprint stays inside the district and outside the authorized route plus the script's `2 m` review clearance. This is composition-only massing, not a production collision or navigation proof.

## Focused Blender validation

Headless build and saved-Blend reopen both passed:

```text
ODDSWELL_SUNDALE_MASSING_VALIDATION|result=PASS|district=340x280m|commons=140x90m|route=800m|route_points=12|route_segments=4|shortcuts=2|destinations=7|scenic=10|families=4,3,3|views=1_top+3_eye|eye_height_m=1.7|engine=eevee|cycles=false|external_refs=0
ODDSWELL_SUNDALE_MASSING_FOCUSED|result=PASS|manifest=true|render_hashes=4|manual_input=false
```

The focused validator also locks exactly one top-down view, exactly three eye-level cameras at `1.7 m`, exactly one Blend output, four exact render names, Eevee, no Cycles, no external Blender libraries/images, and no production-character geometry.

## Render evidence

| Review view | Bytes | SHA-256 |
| --- | ---: | --- |
| `TopDown_AuthorizedAndProposed.png` | 807,175 | `B0C1E87F2F2A8CF1868EF03435B5F2C5EA2B562747303CB4BAAABAFB8B20A704` |
| `EyeLevel_SouthArrival.png` | 434,762 | `C2727EB46A534794BF39BCC3E00045548333E1FEF2D9B999A40E5DC21AAA6949` |
| `EyeLevel_CommonsArenaAxis.png` | 436,115 | `EBD7BBCE9F605675D623739F70471E1610D60C3890C15AC31E46956627FFBB92` |
| `EyeLevel_CourtToArena.png` | 455,331 | `1A8CAA83B185E397AB3F977A753DEF95A1AF8A6F74226B582B40A94991D629D2` |

All four final images were inspected at original resolution. The top-down frame shows the full district, authorized route/commons/destinations, proposed perimeter shells, title, and existing/proposed legend. The wide eye-level frames show the south-arrival, commons-to-arena, and court-to-arena route horizons plus multiple existing/proposed masses at an actual `1.7 m` observer height.

Earlier close, dark, elevated, and facade-heavy drafts were rejected before evidence freeze. The final wide-camera and review-light correction changed no geometry, roles, counts, routes, or production files.

## Regression and non-mutation evidence

| Gate | Result |
| --- | --- |
| Full native Unreal automation | PASS `72/72`, exit `0`, failures `0` |
| Repository-pinned Python `3.12.13` | PASS `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| Production client diff from approved parent `e6f30c6` | PASS `0` paths |
| `SundaleGraybox.umap` SHA-256 | PASS `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Blend Git attribute | PASS existing `filter=lfs`, `diff=lfs`, `merge=lfs`, `text=unset` |
| Render count | PASS exactly `4` PNGs |
| External references / paid services | PASS `0` / `$0.00` |

No no-op BuildCookRun was performed because the production client, map, config, and runtime diff is empty. The retained canonical Phase 1L.2 package remains exact:

- files: `50`;
- bytes: `1,050,423,644`;
- Python artifacts: `0`;
- wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable SHA-256: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS SHA-256: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary

This phase adds no Unreal asset, map change, route change, collision, gameplay coordinate, character, apartment interior, production material/texture, prop, foliage asset, detailed facade, authority, save, economy, brain, wager, inventory, networking, or catalog behavior.

The board is not evidence of approved scenic placement/rooflines, production modeling, final art, collision, detailed architecture, materials, lighting, readability, accessibility, subjective usability, minimum-PC performance, or beta readiness. The small top-down labels and primitive eye-level silhouettes are review aids, not final presentation.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

The owner reviews the one top-down and three eye-level frames and chooses one of three truthful outcomes: accept the massing direction for a smallest production asset phase, request bounded placement/height revisions, or reject the proposal. No Phase 2 detailed modeling begins until that decision and a new Scope Director gate.
