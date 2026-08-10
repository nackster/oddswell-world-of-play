# Sundale Production Asset Scope

Status: **OWNER-ACCEPTED CURRENT PLANNING BASELINE - PRODUCTION PROMOTION STILL REQUIRES A SEPARATE GATE**

This document turns the approved Sundale concept direction into a complete, reviewable beta art-production boundary. The owner superseded the earlier small-city, metropolitan, and radial boards with a larger noncanonical business-clustered mega-city review. That preview does not mutate the proven production graybox, claim that the listed production assets exist, or promote the Phase 1L.2 Job-canopy pilot to canonical final art.

See [[Design/Sundale Art Direction and Core Loop]], [[Design/Decisions/DEC-008 Beta First City Direction]], [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]], and [[Development/Reports/Phase 1L2 Sundale Job Canopy Blender to Unreal Pilot]].

## What exists today

- One approved Sundale concept image and frozen warm civic-commons direction.
- One measured `340 m x 280 m` graybox, a `140 m x 90 m` central commons, and an `800 m` route.
- Exactly `45` authored graybox actors: ground, commons, four route segments, two shortcuts, seven destination/building masses including the Arena canopy, six thresholds, one court with two primitive hoops, four primitive trees, and four environment/light actors.
- Native-primitive presentation layers for the required destinations, Studio/One-bedroom interior, Stadium public viewing, prompts, and feedback.
- One noncanonical Blender pipeline pilot containing two simple one-meter Job-canopy meshes, `88` triangles total, used for three frontage parts.
- One owner-accepted current noncanonical business-clustered planning baseline at commit `b77e0e1`: `2400x1800 m`, six districts around one `600x420 m` Commons/Park, `144` street-level masses, thirty-six playable-core towers, and twenty-four background skyline towers. The owner accepted it at the 2026-08-09/10 conversation boundary and allowed future bounded revision. It remains review art, not production geometry.
- One bounded noncanonical architectural-language review board with exactly six low-poly facade samples and six low-poly tower silhouettes, one pair per accepted district. Owner acceptance and production promotion remain pending separate gates.

The current Blender pilot is not a person, complete building, apartment, landscape, or finished city. It proves authoring, validation, FBX export, Unreal import, Git LFS, cook, package, and runtime loading.

## Production goal

Evaluate one contemporary, walkable `2400x1800 m` business-clustered mega-city planning/play envelope with Financial/Downtown, Arena/Entertainment, Shopping/Retail, Dining/Nightlife, Home Design/Furniture, and Residential/Neighborhood Services districts branching from one central Commons/Park while preserving the validated production route and gameplay anchors until a later production-layout approval. Production art should replace proven placeholders in controlled families rather than rebuild the whole map at once.

The visual target remains warm limestone and terracotta street-level buildings around a shaded civic commons, with brick paving, mature trees, covered storefronts, a public court, and a contemporary arena anchoring its district. Thirty-six towers are proposed as playable-core skyline masses with an exact district split; twenty-four additional towers remain background skyline beyond the play boundary, four per district sector.

## Master scene boundary

| Scene element | Production target | Current authority |
| --- | --- | --- |
| Playable preview | One proposed `2400 m x 1800 m` business-clustered mega-city planning/play envelope | Owner-accepted current planning baseline; not production map authority |
| Districts | Financial/Downtown, Arena/Entertainment, Shopping/Retail, Dining/Nightlife, Home Design/Furniture, Residential/Neighborhood Services | Exactly six in replacement preview |
| Central commons | One proposed `600 m x 420 m` Commons/Park | Preview hub; production graybox remains `140x90 m` |
| Production route | Existing measured route remains exactly `800 m` | Frozen production authority; not redrawn or replaced by preview |
| Preview circulation | Twelve radial spokes, three ring roads, and forty-eight local streets | Proposed only; no route-distance, travel-time, capacity, collision, or production claim |
| Gameplay landmarks | Studio/apartment, attached management kiosk, Job, Clothing, Furniture, Arena, Ticket Booth, Public Court, Commons/Park | Required and labeled in preview |
| Street-level masses | Exactly `144`, split `24` per district | Noncanonical composition ceiling |
| Skyscrapers | Exactly `60`: thirty-six playable-core towers plus twenty-four background skyline towers | Core split `12/6/5/5/4/4`; background split `4` per district sector beyond the boundary |
| Ground-floor scope | Gameplay-relevant ground floors only initially | No generic interiors or enterable skyline towers |
| Time and weather | Dry late-afternoon daylight with patterned shade | Approved direction, not final lighting |
| Vehicles | None for beta | Explicitly excluded |

## Every gameplay-critical exterior

These are the only unique beta destination exteriors. Store and Job gameplay remains at the exterior interaction point unless a later owner decision explicitly adds interiors.

| ID | Asset or set | Required pieces | Interior for beta | Status |
| --- | --- | --- | --- | --- |
| `BLD-STUDIO-EXT` | Starter apartment/residential exterior | `3-5` story shell, Studio doorway, modest residential windows/balconies, awning, return landmark | Private Studio only | Production model not started |
| `BLD-JOB-EXT` | Job building and frontage | Practical shell, two canopy piers, canopy header, landing, approach cue | No | Two-piece canopy pipeline pilot only; final Job fiction remains open |
| `BLD-CLOTHING-EXT` | Clothing store exterior | Covered-promenade shell, two posts, header, display bay, entrance cue | No | Production model not started |
| `BLD-FURNITURE-EXT` | Furniture store exterior | Covered-promenade shell, two posts, header, display bay, entrance cue | No | Production model not started |
| `BLD-ARENA-EXT` | Arena exterior | Low bowl, roof/canopy, portal piers/cap, threshold, approach band | Public-viewing graybox only | Production model not started |
| `BLD-TICKET-BOOTH` | Physical wagering/ticket booth | Arena-frontage booth, two posts, header, counter, approach cue | No separate interior | Production model not started |
| `PROP-APT-KIOSK` | Apartment-management kiosk | Two posts, header, threshold, approach cue | No | Production model not started |

The Ticket Booth is the current physical wagering location. A second standalone sportsbook building is not added unless the owner later changes that direction.

## Business-clustered mega-city massing and skyline

The earlier small-city, metropolitan, and `1400x1000 m` radial proposals are superseded as active review directions. The business-clustered replacement uses exactly `144` street-level building masses, divided `24` per district, plus exactly sixty skyscrapers.

- Thirty-six skyscrapers are proposed playable-core landmarks and each sits on one counted street-level mass. The exact Financial/Arena/Shopping/Dining/Home/Residential split is `12/6/5/5/4/4`.
- Twenty-four skyscrapers are background skyline only, four per district sector, and sit wholly beyond the proposed play boundary.
- Twelve radial spokes branch from the Commons/Park, joined by three concentric rings and forty-eight local streets (`8` per district). All are composition guides without route-distance, travel-time, capacity, collision, or production claims.
- Required first-hour landmarks stay on or near the inner ring so the larger optional review city does not imply a longer mandatory first-hour route.
- Scenic land-use shell labels are bounded to exactly twenty-four Restaurants (`4` per district), eight Nightlife/Bar shells in Dining/Nightlife, three Shopping Centers in Shopping/Retail, eight Furniture/Showrooms in Home Design/Furniture, and twelve Financial/Offices in Financial/Downtown.
- Those labels describe architectural clustering only. They add no restaurant, bar or alcohol service, store, purchase, catalog, economy, age-rating, or gameplay behavior.
- Only gameplay-relevant ground floors are considered initially. Generic street masses and skyline towers receive no interiors.
- Reusable limestone, terracotta, and charcoal/neutral families remain the preferred production approach; the preview does not freeze final facade counts, rooflines, or tower architecture.
- The preview adds no location, mechanic, traffic system, capacity promise, or production-route change.

The current planning composition is owner-accepted. A future bounded revision remains allowed, and a separate Scope Director gate is still required before any production mesh family expands.

## Architectural-language review samples

Phase 1L.3b narrows the next art decision to one exterior facade/tower pair for each accepted district ID. The board uses only Blender-native opaque low-poly geometry and the frozen seven-color planning palette. Facades remain below `240` triangles each and tower silhouettes below `96` triangles each; the unified board and six closeups are review evidence, not a production kit.

The samples add no texture, external reference, interior, brand, catalog, framework, placement, collision, service, or gameplay behavior. They do not alter the accepted `2400x1800 m`, six-district, `144`-mass, sixty-tower planning baseline or the production `800 m` route. Owner acceptance is required before any sample is promoted, iterated into a reusable production family, or used to justify expansion.

## Central commons and landscape

Sundale has one central commons/park, not several separate parks. The production set is:

- One brick-paved commons surface with restrained wear and repair variation.
- Two broad step-free cross paths.
- Three mature shade-tree mesh variants with an initial ceiling of `12` instances; the four validated graybox tree anchors are replaced first.
- One low-planter module, with an initial ceiling of `10` instances.
- One bench family, with an initial ceiling of `8` instances.
- One pedestrian-lamp family, with an initial ceiling of `12` instances.
- One litter-bin family, with an initial ceiling of `6` instances.
- One short railing/bollard family for edge definition where required.

The counts above are performance and repetition ceilings for the first citywide review, not permission to clutter the route. Final placement follows a top-down and eye-level owner review.

## Public basketball court

One outdoor public court remains the east-side activity landmark:

- One court surface and painted line set.
- Four edge/boundary modules and one center treatment.
- Two hoop assemblies, each with pole, backboard, and rim/net treatment.
- One modular fence/edge-silhouette set where it does not obstruct the route.
- Two small bench/player-rest clusters drawn from the commons prop kit.

This is environmental art only. It does not add a second playable basketball mode.

## Streets, paving, and wayfinding

- One street/asphalt material family.
- One curb and sidewalk modular kit.
- One brick-paver family for the commons and covered promenade.
- Six production doorway/threshold treatments matching the existing collision-safe thresholds.
- One cobalt route-mark family that remains understandable without color alone.
- One storefront-glass material family.
- One painted-metal awning/railing material family.
- No moving or drivable vehicles, traffic simulation, transit, or generalized road system.

Phase 1L.3e narrows this section to one noncanonical 64x64 m four-arm review vignette with exactly nine review identities covering asphalt, straight/corner curbs, straight/corner sidewalks, one paver transition reference, and three shape-coded cobalt route marks. Straight, turn, and destination use a bar/double-chevron, right-angle arrow, and ring/target silhouette respectively, so the proposal is not color-only. The board is not the canonical 800 m route, records exact_distance_m=null and canonical=false, and adds no traffic, vehicles, collision, navigation, production catalog, or gameplay. Owner acceptance and a separate promotion gate remain required.

## Required interiors

| ID | Interior | Production scope | Explicit exclusions |
| --- | --- | --- | --- |
| `INT-STUDIO` | Private Starter Studio | Preserve the existing approximately `8 m x 6 m x 2.9 m` shell, entry/exit, lighting, empty default, trim, and one furniture snap point | No free placement, decoration controls, roommate/visitor support, or extra rooms |
| `INT-ONEBED` | Owned One-bedroom state | Reuse the Studio footprint with the approved partition/open doorway and retained chair | No separate larger level or later apartment tier |
| `INT-STADIUM` | Public viewing | Preserve eight blocking surfaces, five zones, court perimeter, viewing treatment, replay placement, and exit | No locker rooms, concourses beyond proven zones, crowd system, suites, or full arena simulation |

Job, Clothing, Furniture, Ticket Booth, and scenic buildings have no beta interiors.

## Furniture and clothing art

- One production Sundale Modular Chair replacing the current three-part placeholder.
- One production worn off-white starter outfit set.
- One production Sundale Signal Jacket compatible with the approved avatar base.
- No additional beta clothing or furniture catalog is authorized by this scope.

## Player-character art is a separate approval track

No production person is being modeled yet. The current player is a primitive placeholder, and the final body proportions, faces, hair, and broader options remain open.

Before character production, approve one lightweight character sheet covering:

- Two gameplay-identical base presentations: masculine and feminine.
- The same four approved skin tones across both presentations.
- One shared skeletal and locomotion compatibility target.
- The worn off-white starter outfit and Signal Jacket fit.
- Neutral proportions that do not imply ability, wealth, intelligence, or behavior.

After that approval, the minimum beta character-art set is two body meshes or one compatible shared body system, four skin-tone materials, one starter outfit, one Signal Jacket, one skeletal rig, and the existing idle/walk/run/jump locomotion set. Faces, hair catalog, names, pronouns, a deep creator, and additional outfits remain outside this first production set.

## Material families

The first production city kit is limited to these shared families:

1. Warm limestone stucco.
2. Muted terracotta stucco.
3. Textured concrete.
4. Sand concrete.
5. Brick pavers.
6. Charcoal asphalt/service surface.
7. Painted metal.
8. Storefront glass.
9. Court surface/lines.
10. Foliage/trunk.

Use tiling materials, trim sheets, and instances before unique textures. No real brands, teams, advertisements, copied landmarks, or unlicensed assets.

## Lightweight review sequence

No long, high-quality render is required to approve form and layout. Every asset family should pass this sequence:

1. **Citywide massing board:** one high-resolution top-down and six district eye-level Blender Eevee views showing the `2400x1800 m` envelope, six districts, all required landmarks, `144` street masses, sixty towers, Commons/Park, court, business-cluster labels, and proposed radial circulation. No production textures; simple review colors only.
2. **Architectural-language board:** one native low-poly facade and tower-silhouette pair for each of the six accepted districts, presented together and in six district closeups; promotion remains owner-gated.
3. **Asset contact sheet:** front, rear, left, right, top, and perspective views with dimensions, triangle count, material slots, UV count, and status.
4. **Unreal in-place proof:** one packaged fixed view before/after, asset-load marker, collision/route check, and short warmed resource sample.
5. **Owner decision:** approve, request one bounded revision, or reject before the asset family expands.

Use Blender Workbench or Eevee for review images. Do not use slow Cycles renders for blockout approval.

## Recommended production order

1. Use the owner-accepted business-clustered planning baseline to scope one smallest next Phase 1L art dependency; preserve separate asset-family review gates and allow a future bounded citywide revision.
2. Build the shared facade, street, paving, and prop kits.
3. Complete the central commons and public court.
4. Replace the six gameplay-building exteriors, Arena canopy, Ticket Booth, and apartment kiosk in route order.
5. Complete the Studio/One-bedroom and Stadium public-viewing interiors.
6. Replace the Modular Chair and approved clothing placeholders.
7. Freeze the separate character sheet, then build and rig the minimum player set.
8. Run final LOD/collision/material/package/performance and accessibility reviews.
9. Return to the deferred Phase 1K hands-on first-hour playtest before beta exit.

## Production guardrails

- Preserve the validated route, gameplay anchors, thresholds, authority, ledger, saves, inventory, wagering, settlement, brains, and private-apartment boundary.
- Keep prototypes noncanonical until the owner approves their review sheet.
- Every production asset needs original/licensed provenance, stable source files, deterministic export settings, Git LFS coverage, dimensions, triangle/UV/material evidence, collision policy, LOD evidence, and a packaged Unreal proof.
- Prototype targets favor low polygon counts, one material slot where practical, no textures unless a style decision requires them, and fast Workbench reviews.
- Do not call a blockout, concept image, generated image, or pipeline pilot final art.
- Do not expand beyond the `2400x1800 m`, six-district, `144`-mass, sixty-tower preview ceiling, or expand services, catalogs, apartment tiers, interiors, or characters, merely because the pipeline works.

## Owner-review decisions

The approved Sundale concept, production `800 m` route, required destinations, palette, materials, atmosphere, and current business-clustered planning baseline remain authoritative at their stated levels. The earlier small-city, metropolitan, and radial boards are superseded only as review directions; the current production map remains unchanged. Acceptance of the planning baseline does not approve production modeling. The remaining proposed details need an explicit owner review before catalog-scale modeling:

1. Landscape instance ceilings and the final commons composition.
2. The character silhouette/proportion sheet.
3. Promotion of any pilot asset from noncanonical to production art.
