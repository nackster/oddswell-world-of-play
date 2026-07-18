---
tags:
  - development
  - beta
  - roadmap
  - scope
status: active
date: 2026-07-18
---

# OddsWell Beta Delivery Roadmap

## Purpose

This roadmap converts [[Design/Beta Game Bible|OddsWell Beta Game Bible]] into a dependency-ordered delivery path. The Bible defines **what** the beta is. This roadmap defines the current expected **order**. [[Development/Current Plan|Current Plan]] and phase reports prove **what is actually complete**.

The roadmap is intentionally made of measurable product gates, not hundreds of speculative tasks. The Scope Director may split a phase into the smallest truthful subphase, but it may not skip dependencies, invent an OPEN decision, or begin Version 1 early.

## Status labels

- **COMPLETE:** committed and validated evidence exists.
- **ACTIVE:** current delivery area.
- **OWNER GATE:** progress requires an explicit owner decision or approval.
- **PENDING:** dependency is not complete.
- **BETA EXIT:** release-wide evidence and owner acceptance are required.

## Current checkpoint

- Phase 0 simulation foundation: **COMPLETE and frozen** except for demonstrated defects or a measured beta requirement.
- Phase 1A.0 local 3D readiness audit: **COMPLETE** at commit `2634541`.
- Next smallest gate: **Phase 1A.1 owner-approved pilot engine installation and empty packaged-build bootstrap**.
- Current blocker: the owner must approve the engine, exact installer version, large download/disk installation, current license terms, and one minimal local project.

No later roadmap phase is authorized merely because it appears below.

## Critical path

| Order | Phase | Player-facing outcome | Status |
| --- | --- | --- | --- |
| 1 | 1A — Engine and packaged-build proof | A real 3D client can build and run | ACTIVE / OWNER GATE |
| 2 | 1B — Character selection and movement | Choose a default avatar and enter the world | PENDING |
| 3 | 1C — First-city identity and graybox | Walk between every required beta location | PENDING / OWNER GATE |
| 4 | 1D — Shared-city presence | Players see one another and equipped clothing | PENDING |
| 5 | 1E — Studio and apartment progression | Enter a persistent home and see the six-tier goal | PENDING |
| 6 | 1F — League, stadium, and match viewing | Research and watch authoritative basketball | PENDING |
| 7 | 1G — Odds Bucks and work recovery | Earn, persist, audit, and recover virtual currency | PENDING |
| 8 | 1H — Wager locking and settlement | Place approved wagers and receive exact outcomes | PENDING |
| 9 | 1I — Stores and lifestyle upgrades | Buy, equip, display, and place basic items | PENDING |
| 10 | 1J — Athlete life and league storytelling | Understand athletes, availability, and consequences | PENDING |
| 11 | 1K — First-hour integration | Complete the entire beta promise in one session | PENDING |
| 12 | 1L — Content, presentation, and accessibility | The slice feels coherent and readable | PENDING |
| 13 | 1M — Reliability, compliance, and beta exit | The owner can truthfully approve beta release | BETA EXIT |

## Phase 1A — Engine and packaged-build proof

### Bible sections advanced

- Current implementation boundary.
- World and city scope.
- Match presentation authority boundary.

### Ordered gates

1. **1A.0 COMPLETE:** local hardware, compiler, Git/LFS, and replay-interface readiness audit.
2. **1A.1 OWNER GATE:** install one approved free engine/version; create, reopen, package, and run the smallest empty Windows project; record disk, build time, launch time, frame time, and memory.
3. **1A.2:** build one placeholder block and court; directly render the existing verified 421-frame replay without resimulating basketball.
4. **1A.3:** owner reviews benchmark evidence and accepts, rejects, or requests one measured comparison. No permanent engine choice is inferred from an empty project.

### Exit evidence

- Reproducible local packaged build.
- Measured representative performance and asset iteration.
- Generated/cache directories remain untracked.
- Frozen 65-test simulation and Admin checks remain green.
- Owner records the engine decision.

## Phase 1B — Character selection and movement

### Bible sections advanced

- First-hour player journey: choose a default character.
- Avatar and clothing.

### Smallest delivery path

1. Placeholder preset data for varied masculine/feminine presentations and skin tones.
2. Fast selection screen with a safe default.
3. One controllable placeholder avatar with the approved camera and input direction.
4. Worn off-white starter outfit represented as replaceable equipment, not permanent character geometry.
5. Save/reload the selected preset and equipped starter outfit locally before multiplayer persistence.

### Owner gates

- Camera and movement style.
- Minimum preset range and character-art direction.

### Exit evidence

A fresh player can choose a preset, enter a packaged placeholder world, move, close, reopen, and recover the same appearance without demographic attributes affecting gameplay.

## Phase 1C — First-city identity and graybox

### Bible sections advanced

- Enter the first city.
- Required beta locations.
- Art, music, and storytelling.

### Owner gate

Approve the world/city name, theme, geography, visual language, and a minimal art-direction sheet. Agents may research or present options, but may not canonize one.

### Smallest delivery path

1. Freeze a compact walking-loop layout.
2. Graybox the apartment entrance, one job, stadium/sportsbook, clothing store, furniture store, and connecting streets.
3. Add collision, navigation, spawn, landmarks, and simple wayfinding.
4. Benchmark the full required route in a packaged build before final city art.

### Exit evidence

One avatar can walk the entire core loop without dead ends, broken collision, excessive empty travel, or final assets.

## Phase 1D — Shared-city presence

### Bible sections advanced

- Shared player presence.
- Avatar and clothing visibility.

### Smallest delivery path

1. Two local clients join one bounded city instance.
2. Replicate identity, position, rotation, movement state, and equipped starter clothing.
3. Leave, reconnect, and restore the same visible state.
4. Measure a small concurrency ladder before choosing a beta instance ceiling.

### Owner gates

- Initial instance capacity and region direction.
- Player collision, visible names, and minimum blocking/reporting surface.
- External hosting or service approval; the first proof remains local when possible.

### Exit evidence

At least two measured clients can walk together and see the same approved clothing state without item ownership transfer, chat, or invented social systems.

## Phase 1E — Studio and apartment progression

### Bible sections advanced

- Discover the starter home.
- Housing and furniture.

### Smallest delivery path

1. Enter and leave one placeholder Studio interior.
2. Persist Studio ownership and player return location.
3. Represent the six locked tiers in data: Studio, 1BR, 2BR, 3BR, 4BR, Penthouse.
4. Prove one visible furniture ownership/placement path in the Studio.
5. Show locked upgrade goals without building six final interiors at once.

### Owner gates

- Apartment instancing and visit rules.
- Layout strategy, decorating controls, and whether tiers use separate interiors.

### Exit evidence

The player can return to the same Studio and see one persisted item; all six tiers exist as truthful progression data, while unbuilt interiors are clearly unavailable.

## Phase 1F — League, stadium, and match viewing

### Bible sections advanced

- Basketball and wagering: league.
- Match presentation.
- Find the sports location.

### Smallest delivery path

1. Show the existing public teams, athletes, schedule, standings, availability, and history in the player client.
2. Graybox the stadium and physical wagering/viewing location.
3. Consume one verified archived replay directly.
4. Produce a readable two-to-five-minute presentation with score, clock, actors, key events, overtime, and final seal.
5. Prove that watch, skip, late arrival, and reconnect never change the recorded result.

### Owner gates

- Match fidelity, cameras, commentary, skip/condensed rules, and duration.
- How an 82-game season remains varied with the initial two-team scope.

### Exit evidence

The player can research a scheduled game, go to the venue, watch or skip the same authoritative result, and inspect the immutable history. The client never resimulates basketball.

## Phase 1G — Odds Bucks and work recovery

### Bible sections advanced

- Odds Bucks economy.
- Find work.
- Experience the consequence.

### Smallest delivery path

1. Add the server-authoritative virtual Odds Bucks ledger with append-only entries and idempotent commands.
2. Create one placeholder job/recovery action.
3. Credit one verified job payout and restore it across restart/reconnect.
4. Add starting balance and zero-balance recovery only after owner amounts are frozen.
5. Expose truthful reconciliation in Admin.

### Owner gates

- Job fantasy and interaction.
- Starting balance, income, allowance cadence, recovery floor, prices, and limits.

### Exit evidence

The player can earn, retain, and audit virtual Odds Bucks through one non-paid path. No wager, real-money purchase, trade, or second currency is added in this phase.

## Phase 1H — Wager locking and settlement

### Bible sections advanced

- Place and watch the first wager.
- Beta wager markets.
- Wager integrity.

### Market order

1. Match winner.
2. Winning margin or spread-style outcome.
3. Overtime occurrence.
4. Player-points threshold.

Each market is its own evidence gate. A later market does not begin until the previous active market proves exact lock, settlement, rollback, replay/history linkage, and Admin reconciliation.

### Owner gates

- Market rules and order confirmation.
- Odds and payout formula, limits, lock time, correction/cancellation policy, and equal public information.
- Legal, platform, age-rating, and regional review before any external beta involving wagering mechanics.

### Exit evidence

Every accepted wager has one immutable request, balance entry, lock decision, authoritative result, settlement, and history record. No payment or real-money Odds Bucks path exists.

## Phase 1I — Stores and lifestyle upgrades

### Bible sections advanced

- Avatar and clothing.
- Furniture.
- Odds Bucks spending.

### Smallest delivery path

1. Freeze one tiny approved clothing set and one tiny furniture set.
2. Buy one clothing item with an idempotent Odds Bucks command.
3. Equip it and show it to another city client.
4. Buy one furniture item and show it in the Studio.
5. Prove one apartment-upgrade purchase path only after pricing and layout availability are truthful.

### Owner gates

- Initial catalog counts, prices, art approvals, equipment slots, placement rules, and refund policy.

### Exit evidence

Ownership, balance, appearance, and apartment state reconcile across reconnect and rollback. Trading, gifting, marketplace, and real-money purchasing remain absent.

## Phase 1J — Athlete life and league storytelling

### Bible sections advanced

- Athletes and brains.
- Environmental and emergent storytelling.

### Smallest delivery path

1. Present durable talent differences, specialties, form, fatigue, injuries, availability, and current Life Brain choices using existing authoritative evidence.
2. Show a visible causal explanation without exposing hidden RNG or private resolver state.
3. Test whether players can understand why a fictional athlete may perform differently.
4. Reopen frozen brain scope only if first-playable testing identifies a named missing experience that existing fields cannot represent.

### Owner gates

- Any new nightlife, club, doubt, morale, relationship, legal-event, or permanent career behavior beyond the frozen implementation.

### Exit evidence

Players can distinguish generational stars, specialists, average players, weaker players, health, and bounded life consequences without a false realism, learning, or neural-network claim.

## Phase 1K — First-hour integration

### Bible sections advanced

- Entire first-hour player journey.
- Beta win condition.

### End-to-end path

1. Choose character.
2. Enter the shared city and see other equipped avatars.
3. Find the Studio, job, stadium/sportsbook, and stores.
4. Earn Odds Bucks.
5. Research and place the first approved wager.
6. Watch or skip the authoritative game.
7. Receive exact settlement.
8. Save or buy one visible clothing, furniture, or apartment progression upgrade.

### Exit evidence

Observed first-time players complete the loop without developer intervention. Confusion and failure points become measured follow-up phases, not speculative systems.

## Phase 1L — Content, presentation, and accessibility

### Bible sections advanced

- Art, music, and storytelling.
- World, avatar, housing, match, and store presentation.

### Delivery path

1. Replace only the placeholders visible in the proven first-hour path.
2. Apply the approved city, character, team, clothing, furniture, UI, lighting, atmosphere, and audio rules.
3. Add owner-provided or properly licensed music through the approved asset pipeline.
4. Add scalable graphics, readable UI, input remapping, subtitles/captions where needed, contrast, and motion options.
5. Benchmark packaged performance after every representative asset family.

### Exit evidence

The complete loop is visually coherent, readable, accessible at the approved baseline, and within measured PC performance targets. Large catalogs and unseen districts remain out of scope.

## Phase 1M — Reliability, compliance, and beta exit

### Release-wide gates

1. Persistence, migration, backup, restore, rollback, and reconnect.
2. Shared-city capacity, latency, disconnect, and recovery.
3. Odds Bucks, wager, inventory, and apartment reconciliation.
4. Replay and settlement immutability.
5. Authentication, authorization, secrets, audit, privacy, blocking, reporting, and moderation for the approved surface.
6. Accessibility and minimum-PC performance.
7. Legal, platform, age-rating, regional, and wagering-mechanic review for the intended beta audience.
8. Observed first-hour usability and retention evidence.
9. Admin operational checks and incident recovery.
10. Owner review of every OPEN decision still affecting release.

### Exit evidence

A Beta Exit Report states **READY**, **BLOCKED WITH MEASURED CAUSE**, or **NOT READY**. Only the owner can approve beta release and later authorize a Version 1 scope freeze under [[Design/Version 1 Game Bible|Version 1 Game Bible]].

## Owner-decision queue in dependency order

1. Engine, exact version, installation, license, and minimal project.
2. Camera, movement, minimum character presets, and character-art direction.
3. World/city name, theme, geography, visual language, and core layout.
4. Shared-city instance capacity, regions, collision, names, and minimal safety surface.
5. Apartment instancing, layouts, visits, and decorating controls.
6. 82-game schedule variety, team count, calendar, and presentation cadence.
7. Match presentation fidelity, duration, skipping, and commentary.
8. Job, starting Odds Bucks, income, allowance, recovery, prices, and limits.
9. Wager markets, odds, payouts, lock, limits, correction, and cancellation.
10. Clothing/furniture catalog, pricing, equipment, placement, and refunds.
11. Minimum PC, accessibility, beta audience, regions, and release channel.

## Scope Director operating rules

1. Read the entire Beta Game Bible, then this roadmap, Current Plan, latest report, and relevant decisions.
2. Follow the earliest incomplete dependency unless a measured defect requires a corrective gate.
3. Cite the roadmap phase and exact Bible section advanced.
4. Choose one smallest phase or subphase with explicit acceptance evidence.
5. Stop and ask the owner when the next dependency is an OWNER GATE or OPEN decision.
6. Never mark a roadmap phase complete from documentation alone when its outcome requires running software.
7. Update the roadmap status only after the Coordinator verifies a scoped commit and evidence.
8. Keep Version 1 and POST-V1 work inactive until owner-approved beta exit.
9. Preserve the frozen Phase 0 brains, authoritative event log, equal-information boundary, server-owned Odds Bucks/settlement, and immutable history.
10. Prefer one playable vertical path over generalized frameworks, large asset catalogs, or invisible infrastructure.

## Explicitly parked outside this roadmap

- Real-money Odds Bucks purchases.
- Player item trading, gifting, marketplace, or transfer.
- Other sports, including fights.
- Additional cities, travel, vehicles, houses, and mansions.
- Full 10-20-year career ecosystem.
- Open chat/voice or large social systems unless separately approved for beta safety needs.
- Version 1 implementation before beta exit approval.

