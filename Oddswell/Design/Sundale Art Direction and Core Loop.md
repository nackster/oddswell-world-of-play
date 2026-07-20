# Sundale Art Direction and Core Loop

Status: **PHASE 1C.1 CANONICAL PLANNING FREEZE**

This is the smallest buildable art and layout contract for the beta first city selected in [[Design/Decisions/DEC-008 Beta First City Direction]]. It guides the next Unreal graybox without pretending that concept art, final assets, interiors, multiplayer, economy, or wagering systems already exist.

**Working-name rule:** Sundale remains the working city name. Renaming it does not reopen the approved city direction or loop.

See [[Visual Maps/Sundale Core Loop|the clean visual loop map]] and [[Development/Reports/Phase 1C1 Sundale Art Direction and Core Loop Freeze|the Phase 1C.1 evidence report]].

## Identity sentence

**Sundale is a warm modern civic neighborhood where a shaded public commons connects modest housing, daily work, street basketball, practical shopping, and the arena that represents the player's ambition.**

## Minimal art-direction freeze

### Architecture and massing

- Human-scale perimeter buildings use three to six stories; graybox variation should avoid one flat roofline.
- The arena is the single dominant landmark, with a low contemporary bowl and canopy rather than a monumental tower.
- The starter residential edge is visibly modest but maintained, never depicted as a slum.
- The job frontage is practical and readable without choosing the job fantasy or mechanic.
- Clothing and furniture storefronts share a covered promenade but remain separate entrances.
- The sportsbook uses a distinct public entrance on the arena frontage. This freezes location only, not wager UI, rules, odds, payouts, or operations.
- Repeated deep awnings, mature trees, worn brick paving, and a distinctive court edge keep the district from feeling like a generic new development.

### Palette

| Role | Planning color | Reference value | Use |
| --- | --- | --- | --- |
| Primary wall | Warm limestone | `#D8C8A9` | Pale stucco and textured concrete masses |
| Secondary wall | Muted terracotta | `#A65F47` | Selected facades and court-side accents |
| Ground | Sand concrete | `#B9A783` | Promenades, curbs, and commons paving |
| Landscape | Sage green | `#6D7F62` | Tree and planter identity |
| Wayfinding | Restrained cobalt | `#315F79` | Repeated geometric route marks and court bands |
| Social accent | Burnt orange | `#C46D3B` | Awnings, court details, and warm focal accents |
| Neutral road | Charcoal gray | `#4D5051` | Streets and service surfaces |

These values are planning references, not calibrated final materials. Navigation must remain understandable without color alone.

### Materials

- Textured concrete and stucco.
- Brick pavers with restrained wear and repair variation.
- Painted metal awnings and railings.
- Clear or lightly tinted storefront glass.
- Asphalt and concrete street surfaces.
- Tree canopy, low planters, and limited climbing greenery.

No final texture, mesh, foliage pack, generated image, marketplace item, or external license is approved by this sheet.

### Light and atmosphere

- Default target: dry late-afternoon daylight with long, readable patterned shade.
- Warm window and awning light supports the transition toward evening without turning the city into a nightlife district.
- The commons remains bright enough to read players and clothing from across the space.
- Background music direction remains warm rhythmic movement, light percussion, and social outdoor energy for the owner's later music work.

### Wayfinding hierarchy

1. Arena roof and canopy: city-scale north landmark.
2. Commons tree canopy and paving: central orientation anchor.
3. Cobalt route marks plus repeated awning geometry: local loop guidance.
4. Public court colors and fence silhouette: east-side activity landmark.
5. Distinct door canopies: location entrances without relying on readable commercial branding.

### Explicit visual exclusions

- No futuristic technology, fantasy skyline, giant monument, canal network, water-city features, Tartaria-inspired monumentality, mansion district, luxury resort language, or vehicle system.
- No real brands, teams, advertisements, or copied city landmarks.
- No giant empty plazas, decorative districts outside the first-hour loop, or generalized multi-city infrastructure.
- No claim of final character proportions, final team identity, or production-ready art.

## Frozen graybox footprint

| Item | Planning value | Unreal value |
| --- | ---: | ---: |
| Bounded playable footprint | `340 m × 280 m` | `34,000 × 28,000 cm` |
| Central commons | `140 m × 90 m` | `14,000 × 9,000 cm` |
| Primary route centerline | `800 m` | `80,000 cm` total |
| Normal pedestrian clear width | `4 m` minimum | `400 cm` minimum |
| Allowed short pinch point | `3 m` minimum | `300 cm` minimum |
| Arena graybox height | `24 m` target | `2,400 cm` target |
| Perimeter building height | `3–6 stories` | varied placeholder masses |

The footprint is a graybox ceiling for Phase 1C, not a production-world size commitment. The route is continuous, step-free, and requires no elevator, loading screen, vehicle, jump, parkour move, or interior traversal.

## Canonical clockwise core loop

| Order | Location or segment | Segment distance | Cumulative distance | Required beta coverage |
| ---: | --- | ---: | ---: | --- |
| 1 | Starter Studio entrance | — | `0 m` | Apartment access point and player spawn anchor |
| 2 | Job frontage | `95 m` | `95 m` | Visible physical job location; mechanic remains open |
| 3 | Clothing store entrance | `120 m` | `215 m` | Separate basic clothing storefront |
| 4 | Arena main entrance | `145 m` | `360 m` | Simplified basketball arena |
| 5 | Sportsbook public entrance | `60 m` | `420 m` | Physical wagering location on the arena frontage |
| 6 | Public basketball court | `125 m` | `545 m` | Commons activity and east-side landmark |
| 7 | Furniture store entrance | `110 m` | `655 m` | Separate basic furniture storefront |
| 8 | Return to Starter Studio | `145 m` | `800 m` | Completes the connected street loop |

### Projected traversal only

Using the approved placeholder movement values from Phase 1B.3:

- Walk at `260 cm/s`: `80,000 ÷ 260 = 307.7 seconds`, approximately **5 minutes 8 seconds** without stops.
- Run at `520 cm/s`: `80,000 ÷ 520 = 153.8 seconds`, approximately **2 minutes 34 seconds** without stops.

These are arithmetic planning projections, not measured Unreal evidence. Phase 1C.2 must build the graybox, then record actual packaged traversal time, collision, route continuity, visibility, and performance.

## Central commons shortcuts

Two broad cross-paths may shorten ordinary errands, but they do not replace the canonical acceptance loop:

- West-to-east commons crossing between the job side and court side.
- South-to-north commons crossing between the Studio side and arena axis.

Both shortcuts must preserve the commons as a social space and keep the arena visible. Their exact lengths remain graybox measurements rather than frozen guesses.

## Graybox acceptance contract for Phase 1C.2

The next phase is complete only when one fresh packaged run proves:

1. One avatar spawns at the Starter Studio entrance and can follow the full clockwise route back to the same point.
2. Every required entrance is represented by a separately named, collision-safe placeholder threshold.
3. The route is continuous and step-free, with no dead end, stuck point, unintended fall, required jump, or blocked doorway.
4. The arena is visible as the north landmark from at least the central commons and one arrival segment.
5. The court and commons are visually distinct without final assets.
6. Actual walk and run times are recorded and compared with the `5:08` and `2:34` projections.
7. Map Check, packaged launch, locomotion, frozen regressions, Brain Admin self-check, documentation, Canvas, hashes, and repository hygiene pass.

## Boundary

Phase 1C.1 changes planning authority only. It adds no Unreal level, map geometry, collision, navigation, source, config, material, mesh, final art, interior, multiplayer, account, store system, inventory, Odds Bucks, wagering logic, deployment, model, training, or retraining behavior.
