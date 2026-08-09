# Phase 1L.3a Sundale Citywide Blender Massing Review Board

Date: 2026-08-08; owner-requested label repair verified 2026-08-09
Branch: `agent/phase-0d`
Status: REVIEW ARTIFACT COMPLETE; OWNER MASSING DECISION OPEN
Cost: `$0.00`

## Outcome first

OddsWell now has one bounded, noncanonical citywide Blender board for reviewing Sundale's composition before detailed production modeling begins. It includes exactly one top-down and three true eye-level views. The owner-requested repair makes all seven authorized destination labels and all ten proposed scenic-shell labels legible at the original `1280x900` top-down resolution. Nothing was imported into the production Unreal map or runtime.

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

## Owner-requested label visibility repair

The original top-down labels were too small and low-contrast to support owner review. The repaired shared label path now produces exactly `17` top-down-only native Blender text labels and `17` simple dark plates:

- authorized: `7` short `A | NAME` labels at `6.5 m` font size in teal;
- proposed: `10` short `P | FAMILY-ID STORIES` labels at `6.0 m` font size in orange;
- plate: `10.0 m` high, `0.2 m` deep, width derived deterministically from the short label;
- source-color contrast against the dark plate: at least `5.0:1`.

The repair changed no city geometry, transform, height, palette-family identity, route, commons, shortcut, destination anchor, scenic-shell count, camera, resolution, filename, or production file. Labels and plates are hidden from all three eye-level renders; an RGB pixel comparison against canonical commit `77fba35` found zero changed pixels in each eye-level view. The superseded `807,175`-byte top-down render at SHA-256 `B0C1E87F2F2A8CF1868EF03435B5F2C5EA2B562747303CB4BAAABAFB8B20A704` is rejected because its labels were not sufficiently visible.

## Focused Blender validation

Headless build and saved-Blend reopen both passed:

```text
ODDSWELL_SUNDALE_MASSING_VALIDATION|result=PASS|district=340x280m|commons=140x90m|route=800m|route_points=12|route_segments=4|shortcuts=2|destinations=7|scenic=10|families=4,3,3|labels=17|plates=17|contrast_min=5.0|top_down_only=true|views=1_top+3_eye|eye_height_m=1.7|engine=eevee|cycles=false|external_refs=0
ODDSWELL_SUNDALE_MASSING_FOCUSED|result=PASS|manifest=true|render_hashes=4|labels=17|plates=17|contrast_min=5.0|top_down_only=true|manual_input=false
```

The focused validator also locks all `17` label IDs, roles, short bodies, font sizes, text colors, deterministic plate dimensions, plate positions, top-down-only visibility, and minimum contrast. It retains exactly one top-down view, exactly three eye-level cameras at `1.7 m`, exactly one Blend output, four exact render names, Eevee, no Cycles, no external Blender libraries/images, and no production-character geometry.

| Focused artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleCitywideMassing.blend` | 1,189,404 | `FD26DD24B103D31DC69AA6C79D024CF121B7964CC9E4201B753FC4F7DAEA0C0A` |
| `build_sundale_massing_board.py` | 26,415 | `DFB4573990223315E1B48B857921880F4BA45F2BACBC08B7F8F72CE6CD32AE42` |
| `manifest.json` | 8,736 | `F46897D1783870BA6339CED9224C5343D0602B0E405BD2A8F60BDF706CB5D8DB` |
| `PROVENANCE.md` | 1,390 | `9EE9EC4552C5B4668AEFEC99F18750675FB608EBCC4676156C4B5AD851FE90D8` |
| headless build log | 4,642 | `8C22286AC47D232A2017AC0CB08CB3EC8582C745482780E0207DAE2A1789F0BF` |
| saved-Blend reopen/focused log | 1,344 | `F0FE72AFF30A6C872D791BF9399D60357F4C1B197126D864E04BB26FE03A8F43` |

Both Blender stderr files are zero bytes. The regenerated Blend remains covered by the existing Git LFS rule; its prospective pointer is OID `fd26dd24b103d31dc69aa6c79d024cf121b7964cc9e4201b753fc4f7daea0c0a`, size `1,189,404`.

An AST-level comparison against canonical Phase 1L.3a proves `RENDER_SIZE`, `EYE_RENDER_HEIGHT`, the full palette, route points/segments, shortcuts, destinations, authorized massing, scenic shells, and all four view definitions are unchanged. That `1,632`-byte source-contract log has SHA-256 `855B9AB16C72D977CB848AA19EFDFC29AEFD2C714B091E1E8E32CA7BD05C54DB`.

## Render evidence

| Review view | Bytes | SHA-256 |
| --- | ---: | --- |
| `TopDown_AuthorizedAndProposed.png` | 829,106 | `8BF4846763E34262EFFEC060136D820F5C5B8E3C3A3E733CC034D2C9D21BBB79` |
| `EyeLevel_SouthArrival.png` | 434,762 | `90F7D36A1400C9C9B483DE6576D661669A2E2E9A33E6E055E700986104B08A20` |
| `EyeLevel_CommonsArenaAxis.png` | 436,115 | `29E31766249BAF3A8E18824CF46F05CAE6FCC6F7A014CF71DF2276890D1B0D30` |
| `EyeLevel_CourtToArena.png` | 455,331 | `68C5C4186B6FC5901D6532F434FFAF7304509EDC92147705EBBE9A7BCEFC4A56` |

All four final images were inspected at original resolution. The top-down frame shows the full district and every short authorized/proposed label on a high-contrast plate without observed label-to-label overlap or frame clipping. The wide eye-level frames show the south-arrival, commons-to-arena, and court-to-arena route horizons plus multiple existing/proposed masses at an actual `1.7 m` observer height. Their file hashes refreshed during the Blender rebuild, while their decoded RGB pixels remain exactly equal to the pre-repair images. The three-view pixel-invariance log is `694` bytes at SHA-256 `8EAAF8DBD720E6C43F124104040D4E0009C6D1D9990FBE0129CD59F4CDC395FB`.

Earlier close, dark, elevated, and facade-heavy drafts were rejected before evidence freeze. The final wide-camera and review-light correction changed no geometry, roles, counts, routes, or production files.

## Regression and non-mutation evidence

| Gate | Result |
| --- | --- |
| Full native Unreal automation | REUSED PASS `72/72`, exit `0`, failures `0`; retained log SHA-256 `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Repository-pinned Python `3.12.13` | REUSED PASS `9 + 2 + 8 + 46 + 40 = 105/105`; production source/tests unchanged |
| Brain Admin `--check` | REUSED PASS; retained log SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |
| Production client diff from approved parent `e6f30c6` | PASS `0` paths |
| `SundaleGraybox.umap` SHA-256 | PASS `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Blend Git attribute | PASS existing `filter=lfs`, `diff=lfs`, `merge=lfs`, `text=unset` |
| Render count | PASS exactly `4` PNGs |
| External references / paid services | PASS `0` / `$0.00` |

The frozen native, Python, and Brain Admin results are proportionately reused because the diff from canonical Phase 1L.3a contains no production client or test path. No no-op BuildCookRun was performed. The retained canonical Phase 1L.2 package was re-audited and remains exact:

- files: `50`;
- bytes: `1,050,423,644`;
- Python artifacts: `0`;
- wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable SHA-256: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS SHA-256: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary

This phase adds no Unreal asset, map change, route change, collision, gameplay coordinate, character, apartment interior, production material/texture, prop, foliage asset, detailed facade, authority, save, economy, brain, wager, inventory, networking, or catalog behavior.

The board is not evidence of approved scenic placement/rooflines, production modeling, final art, collision, detailed architecture, materials, lighting, accessibility, subjective usability, minimum-PC performance, or beta readiness. The repaired labels prove only that the exact short identifiers are visibly distinguishable in this one top-down review image; they do not prove production-game text readability. The plates and primitive eye-level silhouettes remain review aids, not final presentation.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

The owner reviews the one top-down and three eye-level frames and chooses one of three truthful outcomes: accept the massing direction for a smallest production asset phase, request bounded placement/height revisions, or reject the proposal. No Phase 2 detailed modeling begins until that decision and a new Scope Director gate.
