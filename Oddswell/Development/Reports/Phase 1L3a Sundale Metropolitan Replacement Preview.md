# Phase 1L.3a Sundale Metropolitan Replacement Preview

Date: 2026-08-09
Branch: `agent/phase-0d`
Status: OWNER-APPROVED REPLACEMENT PREVIEW COMPLETE; METROPOLITAN COMPOSITION DECISION OPEN
Cost: `$0.00`

## Outcome first

OddsWell now has one larger noncanonical Sundale review preview matching the owner's metropolitan direction: an exact `800x600 m` playable boundary, three connected districts, `36` street-level masses, and ten skyscrapers. It replaces the rejected small-city review proposal without changing the production Unreal map, proven `800 m` route, collision, runtime, or gameplay.

This remains new-art-batch Phase `1/6`. It is a replacement of the Phase 1L.3a review artifact, not Phase 2 and not production approval.

## Owner decision and supersession

The owner rejected the earlier `340x280 m`, ten-shell small-city board, including its later label-visibility repair, because it did not communicate the intended metropolitan scale. Git history and [[Development/Reports/Phase 1L3a Sundale Citywide Blender Massing Review Board]] retain that earlier bounded work, but it is superseded as the active review direction.

[[Design/Sundale Production Asset Scope]] now records the expanded preview ceiling while preserving the smaller production graybox and route as current runtime authority.

## Exact replacement-preview contract

| Element | Exact review value |
| --- | ---: |
| Proposed playable boundary | `800x600 m` |
| Districts | `3` |
| Street-level masses | `36` (`12` per district) |
| Skyscrapers | `10` |
| Playable-core tower landmarks | `4`, each on a counted street-level base |
| Background skyline towers | `6`, wholly outside the proposed playable/collision boundary |
| Required landmark labels | `9` |
| Proposed boulevard segments | `6` |
| Proposed shortcuts | `2`, top-down-only review guides |
| Canonical preview-route distance | none |
| Top-down labels / plates | `24 / 24` |
| Vehicles / modeled interiors | `0 / 0` |

The districts are:

1. South Residential/Retail;
2. Central Civic Commons;
3. North Arena/Entertainment.

The required landmarks are the Studio/apartment frontage, attached Apartment Management kiosk, Job, Clothing, Furniture, Arena, Ticket Booth, Public Court, and central Commons/Park. The Studio and kiosk blockouts share an exact touching edge in the preview.

Only gameplay-relevant ground floors are contemplated initially. Generic street masses and all skyline towers remain exterior blockouts with no interior promise.

## Circulation boundary

Six boulevard segments connect the three districts through west/east spines and district cross streets. Two shortcut guides connect the Studio side toward Commons and Commons toward Arena. They are composition guides only:

- no distance field exists on a boulevard or shortcut;
- the manifest records `exact_distance_m: null` and `canonical: false`;
- no `canonical_route` object exists in the Blend;
- the production `800 m` route is referenced only as unchanged authority.

This preview does not create traffic, vehicles, transit, World Partition, navigation, or a production road system.

## Focused Blender validation

Blender `4.5.5 LTS` headless build and saved-Blend reopen both pass:

```text
ODDSWELL_SUNDALE_METRO_VALIDATION|result=PASS|playable=800x600m|districts=3|street_masses=36|street_per_district=12|towers=10|core_towers=4|background_towers=6|required_landmarks=9|boulevards=6|shortcuts=2|canonical_route_distance=false|labels=24|plates=24|views=1_top+3_eye|eye_height_m=1.7|engine=eevee|cycles=false|external_refs=0
ODDSWELL_SUNDALE_METRO_FOCUSED|result=PASS|manifest=true|render_hashes=4|districts=3|street_masses=36|towers=10|core=4|background=6|landmarks=9|labels=24|plates=24|canonical_route_distance=false|manual_input=false
```

The focused validator locks the exact boundary, district identities/counts, street-mass totals, tower split, counted core bases, wholly outside background towers, attached kiosk, landmark presence, proposed circulation/no-distance rule, no vehicles/interiors, label bodies/roles/size/contrast/plates, camera count/height/resolution, Eevee/no Cycles, four render names/hashes, and zero external references.

| Focused artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleCitywideMassing.blend` | 1,418,475 | `D45D740737ED34BC9E54EC0596A8EC70F3DD15417FADBE46746A6BB86F9715B6` |
| `build_sundale_massing_board.py` | 34,440 | `F167F6B0C72C558A19E329A5D3784C3B06D3A1DB747F72B04B11BED139ACC31E` |
| `manifest.json` | 6,093 | `45D0780EE118FC1BE5F963311E28DDF01A73304FC59AB12F0BE671888D36133A` |
| `PROVENANCE.md` | 1,866 | `0330DA15D55290BB21426B054DED161343AD032992B85410BDAB4DB35EC1EB9F` |
| headless build log | 4,762 | `29E038EEC0A9483E4EDD670F0ACF30028557D7BAF72B70BD197940A28F417F74` |
| saved-Blend reopen/focused log | 1,518 | `D3229C75A736FDFC7CC77E9913461CFC081229C054A1182358F490CDA91F3D5F` |

Both Blender stderr files are zero bytes. The Blend retains the existing Git LFS rule; its prospective pointer is OID `d45d740737ed34bc9e54ec0596a8ec70f3dd15417fadbe46746a6bb86f9715b6`, size `1,418,475`.

## Render evidence

| Review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `TopDown_MetropolitanPreview.png` | `1920x1440` | 1,976,443 | `8E1E52B1522286EF3E013BEEFEB15D128310A8313E7C9DB8AE826EDF4F84AF11` |
| `EyeLevel_SouthResidentialRetail.png` | `1280x720` | 694,889 | `C4CE97E1F827B2252D2E3DAB51FD266508253DE71864101F32AFCB2FB83A14D8` |
| `EyeLevel_CentralCommonsCivicSkyline.png` | `1280x720` | 589,074 | `7F6FD04BBD096B06BE583B8559CE267EAA81CAD2BA437C9BFEC26356E3736370` |
| `EyeLevel_NorthArenaEntertainment.png` | `1280x720` | 683,146 | `F964AF0971C176143EC40A4E978350105527C08E37EA74EC618F14357F4B115F` |

All four accepted images were inspected at original resolution. The top-down board visibly includes the title/legend, all three districts, all nine required landmarks, all four core-tower labels, and all six background-tower labels without observed label-to-label overlap or frame clipping. The district eye views are intentionally distinct:

- South: a residential/retail boulevard framed by street masses and tower skyline;
- Central: an open Commons/Park foreground with civic masses and core/background skyline;
- North: the Arena/entertainment approach with low street masses and tower landmarks.

Earlier near-facade and inside-mass camera diagnostics were rejected before the evidence freeze and are not accepted renders.

## Production and package invariance

| Gate | Result |
| --- | --- |
| Production client diff from canonical parent | PASS `0` paths |
| `SundaleGraybox.umap` SHA-256 | PASS `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Full native Unreal automation | REUSED PASS `72/72`; production source/tests unchanged |
| Repository-pinned Python `3.12.13` | REUSED PASS `105/105`; production source/tests unchanged |
| Brain Admin `--check` | REUSED PASS; production source/tests unchanged |
| External references / paid services | PASS `0` / `$0.00` |

No no-op BuildCookRun was performed because the production client, map, config, runtime, and test diff is empty. The retained canonical Phase 1L.2 package was re-audited and remains exact:

- files: `50`;
- bytes: `1,050,423,644`;
- Python artifacts: `0`;
- wrapper SHA-256: `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`;
- game executable SHA-256: `0AD3156D2E2E7522B7FA11B1A7D107A3D260AF62223B57B0D7B9626A40B4EFF4`;
- UFS SHA-256: `547E4D4968398F2683F1C89073CC8B37DDDE106952DA5C52CFBBA4F599445B4D`.

## Preserved boundary and limitations

This replacement changes no Unreal asset, map, route, collision, gameplay coordinate, threshold, runtime, save, authority, session, economy, brain, wager, settlement, inventory, network, catalog, housing, Stadium, or avatar behavior.

The board is not evidence of owner-approved final placement, production geometry, collision, detailed architecture, enterable towers, interiors, facade design, production materials/textures, lighting, player capacity, accessibility, subjective usability, minimum-PC performance, or beta readiness. Solid colors are review aids only. The six background towers are not playable locations.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

The owner reviews the replacement top-down and three district/skyline views and chooses one truthful outcome: accept the composition for one smallest production asset-family review, request a bounded district/mass/tower revision, or reject it. No Phase 2 modeling begins until that decision and a new Scope Director gate.
