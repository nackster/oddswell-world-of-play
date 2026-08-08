# Sundale Production Asset Scope

Status: **PROPOSED PRODUCTION SCOPE - OWNER REVIEW REQUIRED BEFORE CATALOG-SCALE MODELING**

This document turns the approved Sundale concept direction into a complete, reviewable beta art-production boundary. It does not claim that the listed production assets already exist, and it does not promote the Phase 1L.2 Job-canopy pilot to canonical final art.

See [[Design/Sundale Art Direction and Core Loop]], [[Design/Decisions/DEC-008 Beta First City Direction]], [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]], and [[Development/Reports/Phase 1L2 Sundale Job Canopy Blender to Unreal Pilot]].

## What exists today

- One approved Sundale concept image and frozen warm civic-commons direction.
- One measured `340 m x 280 m` graybox, a `140 m x 90 m` central commons, and an `800 m` route.
- Exactly `45` authored graybox actors: ground, commons, four route segments, two shortcuts, seven destination/building masses including the Arena canopy, six thresholds, one court with two primitive hoops, four primitive trees, and four environment/light actors.
- Native-primitive presentation layers for the required destinations, Studio/One-bedroom interior, Stadium public viewing, prompts, and feedback.
- One noncanonical Blender pipeline pilot containing two simple one-meter Job-canopy meshes, `88` triangles total, used for three frontage parts.

The current Blender pilot is not a person, complete building, apartment, landscape, or finished city. It proves authoring, validation, FBX export, Unreal import, Git LFS, cook, package, and runtime loading.

## Production goal

Build one compact, contemporary, walkable beta district that matches the approved Sundale image and preserves the validated route and gameplay anchors. Production art should replace proven placeholders in controlled families rather than rebuild the whole map at once.

The visual target remains warm limestone and terracotta mid-rise buildings around a shaded civic commons, with brick paving, mature trees, covered storefronts, a public court, and a low contemporary arena closing the north view.

## Master scene boundary

| Scene element | Production target | Current authority |
| --- | --- | --- |
| Playable district | One `340 m x 280 m` Sundale district | Frozen graybox ceiling |
| Central commons | One `140 m x 90 m` plaza/park | Frozen orientation anchor |
| Main route | Four outer segments totaling `800 m` | Frozen and measured |
| Commons shortcuts | Two broad step-free crossings | Frozen |
| Gameplay destinations | Studio, Job, Clothing, Arena, Ticket Booth, Public Court, Furniture | Frozen |
| Building height | Human-scale `3-6` stories | Frozen direction |
| Arena height | Approximately `24 m`; dominant north landmark | Frozen direction |
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

## Scenic perimeter buildings

The approved concept needs a believable neighborhood around the gameplay destinations, but the beta does not need every background facade to be a unique mesh or an enterable building.

Recommended owner-review ceiling: **ten nonenterable scenic shells**, assembled from three reusable modular families:

| Family | Proposed shell count | Visual role |
| --- | ---: | --- |
| Warm limestone residential/mixed-use | `4` | Main neutral neighborhood fabric |
| Muted terracotta residential/mixed-use | `3` | Warm rhythm and skyline variation |
| Charcoal/neutral service and corner buildings | `3` | Ground the side streets and prevent resort-like uniformity |

All ten remain `3-6` stories, use repeated windows/doors/balconies/parapets, contain no playable interiors, add no locations or mechanics, and must not narrow the validated route. Exact footprints and rooflines require approval on the citywide blockout before production modeling.

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

1. **Citywide massing board:** top-down and three eye-level Blender Workbench views showing all gameplay buildings, the ten proposed scenic shells, commons, court, arena axis, and route. No textures; simple approved palette only.
2. **Style sample board:** one limestone facade bay, one terracotta facade bay, one storefront/awning bay, one tree/planter grouping, and the Arena/Ticket Booth silhouette.
3. **Asset contact sheet:** front, rear, left, right, top, and perspective views with dimensions, triangle count, material slots, UV count, and status.
4. **Unreal in-place proof:** one packaged fixed view before/after, asset-load marker, collision/route check, and short warmed resource sample.
5. **Owner decision:** approve, request one bounded revision, or reject before the asset family expands.

Use Blender Workbench or Eevee for review images. Do not use slow Cycles renders for blockout approval.

## Recommended production order

1. Freeze this scope and approve the citywide massing board.
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
- Do not expand the city, catalogs, apartment tiers, interiors, characters, or districts merely because the pipeline works.

## Owner-review decisions

The approved Sundale concept, compact route, required destinations, palette, materials, and atmosphere remain authoritative. The following proposed production details need an explicit owner review before catalog-scale modeling:

1. Ten scenic perimeter shells and their exact placement/roofline mix.
2. Landscape instance ceilings and the final commons composition.
3. The first citywide massing board.
4. The character silhouette/proportion sheet.
5. Promotion of any pilot asset from noncanonical to production art.
