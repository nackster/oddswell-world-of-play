# Phase 1L.3a Sundale Business-Clustered Mega-City Replacement Preview

Date: 2026-08-09
Branch: `agent/phase-0d`
Status: OWNER-REQUESTED BUSINESS-CLUSTERED REPLACEMENT PREVIEW COMPLETE; COMPOSITION DECISION OPEN
Cost: `$0.00`

## Outcome first

OddsWell now has one larger noncanonical Sundale review preview matching the owner's business-clustering direction: an exact `2400x1800 m` planning/play envelope, one central `600x420 m` Commons/Park, six radial districts, `144` street-level masses, and `60` proposed skyscrapers. Exact scenic architectural tags group restaurants throughout the city while concentrating Nightlife/Bar, Shopping Center, Furniture/Showroom, and Financial/Office shells in their logical districts. This is review massing only; it adds no business service, alcohol, purchase, catalog, economy, age-rating, or gameplay behavior.

This remains new-art-batch Phase `1/6`. It supersedes the prior radial Phase 1L.3a review artifact; it is not Phase 2 and not production approval.

## Owner direction and supersession

The owner requested a still larger city with logical same-business clustering: a Financial district, restaurants throughout, a bar-scene area, shopping centers, and furniture stores. The prior `1400x1000 m`, four-district, `72`-mass, twenty-four-tower radial board remains in [[Development/Reports/Phase 1L3a Sundale Radial Mega City Replacement Preview]] and Git history, but it is superseded as the active review direction.

[[Design/Sundale Production Asset Scope]] now records the business-clustered review ceiling while preserving the smaller production graybox and measured `800 m` route as current runtime authority.

## Exact preview contract

| Element | Exact review value |
| --- | ---: |
| Proposed planning/play envelope | `2400x1800 m` |
| Central Commons/Park | `600x420 m` |
| Districts | `6` |
| Street-level masses | `144` (`24` per district) |
| Skyscrapers | `60` |
| Playable-core towers | `36`, each on a counted base |
| Core tower district split | Financial/Arena/Shopping/Dining/Home/Residential = `12/6/5/5/4/4` |
| Background skyline towers | `24` (`4` per district sector), outside the play boundary |
| Required landmark labels | `9` = seven functional identities + kiosk + park |
| Radial spoke boulevards | `12` |
| Ring roads | `3` |
| Local district streets | `48` (`8` per district) |
| Canonical preview-route distance | none |
| Top-down labels / plates | `24 / 24` |
| Vehicles / modeled interiors / gameplay additions | `0 / 0 / 0` |

The six districts are:

1. Financial + Downtown;
2. Arena + Entertainment;
3. Shopping + Retail;
4. Dining + Nightlife;
5. Home Design + Furniture;
6. Residential + Neighborhood Services.

The nine required landmark identities are Studio/apartment frontage, attached Apartment Management kiosk, Job, Clothing, Furniture, Arena, Ticket Booth, Public Court, and central Commons/Park. The exact structure is seven functional building/location identities, one attached kiosk point, and one park area. All remain on or near the proposed inner ring; the Studio and kiosk retain their attached review relationship.

## Business-cluster shell boundary

The `144` street masses carry exact deterministic scenic land-use tags:

| Scenic architectural tag | Exact distribution |
| --- | ---: |
| Restaurant | `24`, exactly `4` per district |
| Nightlife/Bar | `8`, all in Dining/Nightlife |
| Shopping Center | `3`, all in Shopping/Retail |
| Furniture/Showroom | `8`, all in Home Design/Furniture |
| Financial/Office | `12`, all in Financial/Downtown |

Remaining shells use bounded mixed, residential, service, and entertainment review tags. The top board shows a high-contrast color legend and one short business-summary plate per district; the focused validator, not a fabricated storefront claim, locks every per-shell distribution.

These tags describe scenic architectural and land-use massing only. The preview creates no restaurant operation, bar or alcohol service, functional business, new Clothing/Furniture store, purchase, catalog, economy, inventory, age-rating, or gameplay behavior.

## Circulation, park, and skyline boundary

Exactly twelve radial spoke boulevards branch from the park. Three concentric rings join the spokes, while forty-eight local streets are split eight per district. They are composition guides only:

- the manifest records `exact_distance_m: null` and `canonical: false`;
- it records no travel-time, capacity, collision, or production-road claim;
- no production route object exists in the Blend;
- the production `800 m` route is referenced only as unchanged authority.

The park remains ten native low-poly review placeholders: four lawn quadrants, two promenades, and four tree-grove blocks. Thirty-six core towers sit on counted street bases; twenty-four background towers are exterior skyline only and remain outside the proposed play boundary. No tower or generic street mass promises an interior.

## Focused Blender validation

Blender `4.5.5 LTS` headless build and saved-Blend reopen both pass:

```text
ODDSWELL_SUNDALE_BUSINESS_VALIDATION|result=PASS|playable=2400x1800m|commons=600x420m|districts=6|street_masses=144|street_per_district=24|towers=60|core_towers=36|background_towers=24|required_landmarks=9|functional_locations=7|attached_kiosk=1|park=1|restaurants=24|nightlife_bar_shells=8|shopping_centers=3|furniture_showrooms=8|financial_offices=12|spokes=12|rings=3|local_streets=48|canonical_route_distance=false|labels=24|plates=24|views=1_top+6_eye|eye_height_m=1.7|camera_clearance_m=20|engine=eevee|cycles=false|external_refs=0|vehicles=0|interiors=0|gameplay_added=false
ODDSWELL_SUNDALE_BUSINESS_FOCUSED|result=PASS|manifest=true|render_hashes=7|districts=6|street_masses=144|towers=60|core=36|background=24|landmarks=9|restaurants=24|nightlife_bar_shells=8|shopping_centers=3|furniture_showrooms=8|financial_offices=12|spokes=12|rings=3|locals=48|labels=24|plates=24|camera_clearance_m=20|canonical_route_distance=false|gameplay_added=false|manual_input=false
```

The focused validator locks the exact envelope, park, six identities/counts, mass totals, tower split and counted core bases, background sector placement outside the envelope, exact land-use counts and distributions, exact seven-plus-one-plus-one landmark structure, attached kiosk, landmark presence and inner-ring proximity, street topology/no-distance rule, primitive park roles, no services/commerce/gameplay addition, no vehicles/interiors, label bodies/roles/contrast/plates, camera count/height/resolution/targets, minimum `20 m` horizontal camera clearance from every mass/tower/court/park AABB, Eevee/no Cycles, seven render names/hashes, and zero external references.

| Focused artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `SundaleCitywideMassing.blend` | 3,185,582 | `8531EEB17E86C0F61EBA8F411E97C1D4DB4A021889F33138649C42307DE23456` |
| `build_sundale_massing_board.py` | 52,921 | `B25353151EAC21CDE317CBCE1C3C9590116FD055A54C179278FC37F971B6D72E` |
| `manifest.json` | 10,844 | `9DE95B4F6BDC72A8130BDAD3989CBFB4FD0E05046998A66A49E8212590B06B2E` |
| `PROVENANCE.md` | 3,831 | `B5058C92D1642E21BA097FCF6034907772D17F8C0F6243D118121C3BBB08DE12` |
| headless build log | 8,232 | `8B2C4E63DA2C33162474DB0F6C9C3E535A128A5BA945D5EA23E0C879C02553CA` |
| saved-Blend reopen/focused log | 2,368 | `6965E805432E495E5FD77BA725BFFA80A63D218C99234CC0C5137FD652AAF9B2` |

Both Blender stderr files are zero bytes. The Blend retains the existing Git LFS rule; its prospective pointer is OID `8531eeb17e86c0f61eba8f411e97c1d4db4a021889f33138649c42307de23456`, size `3,185,582`. No `.blend1` backup exists.

## Render evidence

| Review view | Dimensions | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `TopDown_BusinessClusteredMegaCityPreview.png` | `3200x2400` | 6,874,084 | `7FA4CDFB6F9D18CCCD6F5C71AB54CE60906FF53303B9CECEF7F227582D1A57F3` |
| `EyeLevel_FinancialDowntownParkSkyline.png` | `1280x720` | 651,716 | `A35DD1723D381FB8F0C699D6D514D3FE48D86F7C6143DF4207F94933D62ED456` |
| `EyeLevel_ArenaEntertainmentParkSkyline.png` | `1280x720` | 657,774 | `6678F3011396C91F183D469BCDE43FECAFB7268AB55CDE1C0A60DB62AF805154` |
| `EyeLevel_ShoppingRetailParkSkyline.png` | `1280x720` | 640,231 | `2F12F28415BA3323063BBB33F93057DCC5F0F87279BFE8B34986FF3099AC15F7` |
| `EyeLevel_DiningNightlifeParkSkyline.png` | `1280x720` | 622,611 | `165629BAD52CF3E5385296016AEBDADB368F7C7F1555E23D57657F3106BBE5D9` |
| `EyeLevel_HomeDesignFurnitureParkSkyline.png` | `1280x720` | 645,820 | `E007694F8177A580E2556302740B4B3EC8ECDF98A1BC27D98653759C92767F07` |
| `EyeLevel_ResidentialNeighborhoodServicesParkSkyline.png` | `1280x720` | 649,523 | `F63488D09DE300A727CA5EBFEF31F67D524507D9E301539CB8AB4D54B678B02B` |

All seven accepted images were inspected at original resolution. The top board visibly includes the complete envelope and park, six district plates, nine required landmark plates, six business-summary plates, title, business-color legend, and exact proposed/no-distance/no-capacity scope legend without observed label-to-label overlap or frame clipping. The first top render with information plates too far toward the frame edge was rejected, overwritten, and is not accepted evidence.

The six eye views are intentionally distinct:

- Financial/Downtown: park foreground and a dense gold core skyline;
- Arena/Entertainment: centered promenade/spoke and blue Arena skyline;
- Shopping/Retail: park/grove foreground and blue retail skyline;
- Dining/Nightlife: centered promenade/spoke and purple district skyline;
- Home Design/Furniture: park/grove foreground and teal district skyline;
- Residential/Neighborhood Services: park/grove foreground and light neighborhood skyline.

Every accepted eye camera is at `1.7 m`, at least `20 m` horizontally clear of every modeled mass, tower, court, and park AABB, and deterministically targets its district across the park. The views prove bounded composition reviewability only, not storefront readability, business functionality, every street angle, final architecture, or subjective usability.

## Production and package invariance

| Gate | Result |
| --- | --- |
| Production client diff from canonical parent | PASS `0` paths |
| `SundaleGraybox.umap` SHA-256 | PASS `180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015` |
| Full native Unreal automation | REUSED PASS `72/72`; production source/tests unchanged; frozen log SHA-256 `94A4E884C84A9614CE76983C3F202A653F54DF7E58594C15A8085BAA0E615AC4` |
| Repository-pinned Python `3.12.13` | REUSED PASS `105/105` (`9+2+8+46+40`); production source/tests unchanged |
| Brain Admin `--check` | REUSED PASS; frozen log SHA-256 `D0EC87F0C4586A63F332837562B25BD44C57F02FB788B6FDE599102AE2C3BA44` |
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

The board is not evidence of owner-approved final placement, production geometry, collision, street capacity, travel time, detailed architecture, real or functional businesses, alcohol service, purchases, catalogs, enterable towers, interiors, facade design, production materials/textures, final landscape, lighting, age rating, accessibility, subjective usability, minimum-PC performance, or beta readiness. Solid colors and low-poly park blocks are review aids only. The twenty-four background towers are not playable locations.

Phase 1K hands-on held-control and route-usability evidence remains incomplete and deferred to the MVP playtest, not waived.

## Next gate

The owner reviews the top-down business-cluster plan and six district/park/skyline views and chooses one truthful outcome: accept the composition for one smallest production asset-family review, request one bounded district/business/street/mass/tower revision, or reject it. No Phase 2 modeling begins until that decision and a new Scope Director gate.
