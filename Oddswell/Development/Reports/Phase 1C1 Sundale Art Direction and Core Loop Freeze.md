# Phase 1C.1 — Sundale Art Direction and Core Loop Freeze

Date: 2026-07-20

## Outcome

Phase 1C.1 converts the owner-selected Concept B direction into one buildable planning contract: [[Design/Sundale Art Direction and Core Loop]]. The contract freezes the minimal visual language, graybox ceiling, location order, segment distances, wayfinding hierarchy, and next-phase acceptance evidence for the beta first city.

The working name remains Sundale. No Unreal graybox or final asset was created in this phase.

## Bible and roadmap coverage

- Advances `Enter the first city`, `Required beta locations`, `World rules`, and `Art, music, and storytelling`.
- Preserves all seven required beta location types on one continuous compact loop.
- Uses the approved Concept B theme, commons-ring geography, palette, lighting, materials, and social atmosphere from [[Design/Decisions/DEC-008 Beta First City Direction]].
- Defines Phase 1C.2 acceptance evidence without implementing later apartment, store, multiplayer, Odds Bucks, wager, or final-art systems.

## Frozen planning values

| Evidence | Frozen value |
| --- | --- |
| Playable graybox ceiling | `340 m × 280 m` / `34,000 × 28,000 cm` |
| Central commons | `140 m × 90 m` / `14,000 × 9,000 cm` |
| Canonical route centerline | `800 m` / `80,000 cm` |
| Required entrances | Studio, job, clothing, arena, sportsbook, furniture |
| Required activity landmark | Public basketball court |
| Walk projection at `260 cm/s` | `307.7 s` / approximately `5:08` |
| Run projection at `520 cm/s` | `153.8 s` / approximately `2:34` |

Traversal values are arithmetic projections, not packaged runtime results.

## Delivered artifacts

- [[Design/Sundale Art Direction and Core Loop]]
- [[Visual Maps/Sundale Core Loop]]
- Updated [[Design/Beta Game Bible]] implementation boundary and decision queue.
- Updated [[Development/Beta Delivery Roadmap]], [[Development/Current Plan]], [[Visual Maps/Beta Delivery Roadmap]], [[Visual Maps/Beta Game Scope]], [[Visual Maps/First City Concepts]], and [[Visual Maps/Project Tool Map]].

## Validation

- Every required beta location appears exactly once in the canonical loop specification.
- Segment distances sum to exactly `800 m`.
- Projected traversal arithmetic matches the approved Phase 1B.3 walk/run values.
- Obsidian wiki links and Canvas file references resolve.
- Modified Canvas files parse as JSON, retain unique node IDs, and use separated readable groups.
- Documentation diff and repository hygiene checks pass.

No Unreal build, package, runtime, Map Check, simulation regression, or Brain Admin run is claimed because Phase 1C.1 changes documentation and visual planning only.

## Boundaries and cost

- No final art, production asset, asset license, paid API, external service, large download, installation, Unreal source/map/config change, multiplayer, apartment implementation, economy, wagering, deployment, model, training, or retraining work was added.
- Project spend initiated by this phase: `$0.00`.

## Next gate

Phase 1C.2 is the smallest truthful next phase: build the primitive Sundale graybox in a separate Unreal map, add separately named placeholder thresholds and collision-safe streets, package it, then measure the complete route against the Phase 1C.1 projections.
