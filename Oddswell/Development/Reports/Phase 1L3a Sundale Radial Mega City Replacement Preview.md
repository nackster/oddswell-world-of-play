# Phase 1L.3a Sundale Radial Mega-City Replacement Preview

Date: 2026-08-09
Branch: `agent/phase-0d`
Status: OWNER-REQUESTED RADIAL REPLACEMENT PREVIEW COMPLETE; COMPOSITION DECISION OPEN
Cost: `$0.00`

## Outcome first

OddsWell now has one larger noncanonical Sundale review preview matching the owner's radial mega-city direction: an exact `1400x1000 m` playable boundary, one central `320x240 m` Commons/Park, four surrounding districts, `72` street-level masses, and `24` proposed skyscrapers. Eight radial spokes, two rings, and sixteen local cross-streets communicate a park-centered street structure without changing the production Unreal map, collision, proven `800 m` route, runtime, or gameplay.

This remains new-art-batch Phase `1/6`. It replaces the prior Phase 1L.3a review artifact; it is not Phase 2 and not production approval.

## Owner decision and supersession

The owner said the previous metropolitan direction was right but requested a bigger city with more buildings, skyscrapers, streets, and a middle park from which everything branches. The `800x600 m`, three-district, `36`-mass, ten-tower review remains in [[Development/Reports/Phase 1L3a Sundale Metropolitan Replacement Preview]] and Git history, but it is superseded as the active review direction.

[[Design/Sundale Production Asset Scope]] now records the radial review ceiling while preserving the smaller production graybox and measured route as current runtime authority.

## Exact radial-preview contract

| Element | Exact review value |
| --- | ---: |
| Proposed playable boundary | `1400x1000 m` |
| Central Commons/Park | `320x240 m` |
| Districts | `4` |
| Street-level masses | `72` (`18` per district) |
| Skyscrapers | `24` |
| Playable-core towers | `12` (`3` per district), each on a counted base |
| Background skyline towers | `12` (`3` per side), wholly outside the proposed boundary |
| Required landmark labels | `9` |
| Radial spoke boulevards | `8` |
| Ring roads | `2` |
| Local cross-streets | `16` (`4` per district) |
| Canonical preview-route distance | none |
| Top-down labels / plates | `39 / 39` |
| Vehicles / modeled interiors | `0 / 0` |

The districts are:

1. South Residential/Retail;
2. West Residential/Services;
3. East Commerce/Work;
4. North Arena/Entertainment.

The required landmarks are the Studio/apartment frontage, attached Apartment Management kiosk, Job, Clothing, Furniture, Arena, Ticket Booth, Public Court, and central Commons/Park. All first-hour landmarks remain on or near the proposed inner ring. The Studio and management kiosk retain their attached review relationship.

Only gameplay-relevant ground floors are contemplated initially. Generic street masses and all skyline towers remain exterior blockouts with no interior promise.

## Circulation and park boundary

Exactly eight radial spoke boulevards branch from the park. One inner destination ring and one outer distributor ring join the spokes, while sixteen local cross-streets are split four per district. They are composition guides only:

- the manifest records `exact_distance_m: null` and `canonical: false`;
- it also records no travel-time, capacity, collision, or production-road claim;
- no production route object exists in the Blend;
- the production `800 m` route is referenced only as unchanged authority.

The park is only ten native low-poly review placeholders: four lawn quadrants, two promenades, and four tree-grove blocks. This preview does not create final landscape assets, traffic, vehicles, transit, World Partition, navigation, or a production road system.

## Focused Blender validation

Blender `4.5.5 LTS` headless build and saved-Blend reopen both pass:

```text
ODDSWELL_SUNDALE_RADIAL_VALIDATION|result=PASS|playable=1400x1000m|commons=320x240m|districts=4|street_masses=72|street_per_district=18|towers=24|core_towers=12|background_towers=12|required_landmarks=9|spokes=8|rings=2|local_streets=16|canonical_route_distance=false|labels=39|plates=39|views=1_top+4_eye|eye_height_m=1.7|camera_clearance_m=20|engine=eevee|cycles=false|external_refs=0|vehicles=0|interiors=0
ODDSWELL_SUNDALE_RADIAL_FOCUSED|result=PASS|manifest=true|render_hashes=5|districts=4|street_masses=72|towers=24|core=12|background=12|landmarks=9|spokes=8|rings=2|locals=16|labels=39|plates=39|camera_clearance_m=20|canonical_route_distance=false|manual_input=false
```

The focused validator locks the exact boundary, park, district identities/counts, street-mass totals, tower split, counted core bases, wholly outside background towers, attached kiosk, landmark presence and inner-ring proximity, street topology/no-distance rule, primitive park roles, no vehicles/interiors, label bodies/roles/contrast/plates, camera count/height/resolution/targets, minimum `20 m` horizontal camera clearance from every mass/tower/court/park AABB, Eevee/no Cycles, five render names/hashes, and zero external references.

| Focused artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleCitywideMassing.blend` | 2,133,428 | `B6B5616E77D1C60D19D15D7BABBB3ED9C8DB4E42CAEB42ADB4E6211737640E73` |
| `build_sundale_massing_board.py` | 46,110 | `20EED00158FEE7A2E538FEF90BABB32BC994A7672AC2D3421BBCD9235EFF4396` |
| `manifest.json` | 8,743 | `6FD35F7C0EE564D88848C46C1940598EBAC41B0F5B00B4F4D0611E4A45F39503` |
| `PROVENANCE.md` | 2,435 | `146DF5C36A5699E1EC3ECE2DABA5422D1662ADFFB4AB086A49DEA8D3264ECFC2` |
| headless build log | 2,932 | `517BEB298C0F304AFE8597BA9611BB650726CDB61BF7BE63C6374460D5313349` |
| saved-Blend reopen/focused log | 882 | `722E00FFE021524741624643B0A68CB07A54449470E245E5CBE3C9F5939FB61D` |

Both Blender stderr files are zero bytes. The Blend retains the existing Git LFS rule; its prospective pointer is OID `b6b5616e77d1c60d19d15d7babbb3ed9c8db4e42caeb42adb4e6211737640e73`, size `2,133,428`. No `.blend1` backup exists.

## Render evidence

| Review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `TopDown_RadialMegaCityPreview.png` | `2560x1800` | 3,327,374 | `094CEC0B23E8EFFC7BECD06BDB57918F33135579E663FF24828D66017A34AC77` |
| `EyeLevel_SouthResidentialRetailParkSkyline.png` | `1280x720` | 655,631 | `13B75CA75145EB23EB4AAB3629776A6161B9A13C4C661252469E655F3791AD09` |
| `EyeLevel_WestResidentialServicesParkSkyline.png` | `1280x720` | 676,186 | `775A3DFFC4C3A61657A59ED085AE4569CCF8F5CDB9EDB0BA52B4C7025CAFBB93` |
| `EyeLevel_EastCommerceWorkParkSkyline.png` | `1280x720` | 678,776 | `2279CD550BB3A6AC292160203D293308561415611D8E287A9264FED412233CF6` |
| `EyeLevel_NorthArenaEntertainmentParkSkyline.png` | `1280x720` | 656,249 | `BFDA7B6DEB10EDD82EE8F2651E643FD1B68F8D7D6719618A15359692674C05E7` |

All five accepted images were inspected at original resolution. The top-down board visibly includes the complete boundary, central park, four district labels, nine required landmarks, twelve core-tower labels, twelve background-tower labels, title, and proposed/no-distance legend without observed label-to-label overlap or frame clipping. The four eye views are intentionally distinct:

- South: park lawn and promenade foreground, proposed radial/ring guide, residential/retail skyline;
- West: park opening and circulation foreground, residential/services skyline;
- East: park opening and circulation foreground, commerce/work skyline;
- North: park foreground, proposed circulation, Arena/entertainment skyline.

Every accepted eye camera is at `1.7 m` and at least `20 m` horizontally clear of every modeled mass, tower, court, and park AABB. Early West/East near-wall drafts and earlier thick-road diagnostics were rejected, overwritten, and are not accepted evidence.

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

The board is not evidence of owner-approved final placement, production geometry, collision, road capacity, travel time, detailed architecture, enterable towers, interiors, facade design, production materials/textures, final landscape, lighting, accessibility, subjective usability, minimum-PC performance, or beta readiness. Solid colors and park blocks are review aids only. The twelve background towers are not playable locations.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

The owner reviews the radial top-down and four district/park/skyline views and chooses one truthful outcome: accept the composition for one smallest production asset-family review, request a bounded park/district/street/mass/tower revision, or reject it. No Phase 2 modeling begins until that decision and a new Scope Director gate.
