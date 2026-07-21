---
tags:
  - development
  - beta
  - roadmap
  - scope
status: active
date: 2026-07-19
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
- Phase 1A.1a Unreal Engine 5.8 installation and first-editor-launch verification: **COMPLETE**; see [[Development/Reports/Phase 1A1a Unreal Engine Installation and Editor Launch Verification]].
- Phase 1A.1b official Microsoft Visual C++ x64 runtime alignment and post-reboot Unreal recheck: **COMPLETE**; see [[Development/Reports/Phase 1A1b Visual Cpp Runtime Prerequisite Alignment and Unreal Recheck]].
- Phase 1A.1c smallest empty local Windows project creation and reopen: **COMPLETE**; see [[Development/Reports/Phase 1A1c Minimal Blank OddsWell Project Bootstrap and Reopen]].
- Phase 1A.1d empty Windows package, launch, and baseline measurement: **COMPLETE**; see [[Development/Reports/Phase 1A1d Empty Windows Package Launch and Baseline Measurement]].
- Phase 1A.2a noncanonical primitive street block, basketball court, and representative asset iteration: **COMPLETE**; see [[Development/Reports/Phase 1A2a Noncanonical Street Block and Basketball Court Graybox]].
- Phase 1A.2b direct rendering of the existing verified 421-frame replay: **COMPLETE**; see [[Development/Reports/Phase 1A2b Authoritative 421-Frame Replay Renderer]].
- Phase 1A.3 Unreal Engine 5.8 beta adoption: **COMPLETE** by owner decision on July 19, 2026; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].
- Phase 1B camera/movement and minimum placeholder preset direction: **APPROVED**; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]].
- Phase 1B.1 validated character preset and starter-outfit catalog: **COMPLETE**; see [[Development/Reports/Phase 1B1 Character Preset Catalog]].
- Phase 1B.2 fast local character-selection screen with a safe default: **COMPLETE**; see [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]].
- Phase 1B.3 controllable primitive placeholder and approved locomotion: **COMPLETE**; see [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]].
- Phase 1B.4 separate replaceable starter outfit: **COMPLETE**; see [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]].
- Phase 1B.5 local appearance persistence and first-playable handoff: **COMPLETE**; see [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]].
- Phase 1B character onboarding exit review: **COMPLETE**; see [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].
- Phase 1C.0 noncanonical first-city concept packages: **COMPLETE**; see [[Development/Reports/Phase 1C0 Noncanonical First City Concept Packages]].
- Phase 1C owner selection: **COMPLETE**. The owner selected Concept B — Daymark / Sundale on July 20, 2026; see [[Design/Decisions/DEC-008 Beta First City Direction]].
- Phase 1C.1 minimal art-direction and loop freeze: **COMPLETE**; see [[Development/Reports/Phase 1C1 Sundale Art Direction and Core Loop Freeze]].
- Phase 1C.2 primitive Sundale graybox and packaged route measurement: **COMPLETE**; see [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].
- Phase 1C exit: **PASSED**. The primitive city route is measurable and traversable; final city art remains unbuilt.
- Phase 1D owner defaults: **RESOLVED**; see [[Design/Decisions/DEC-010 Phase 1D Shared City Defaults]].
- Phase 1D.1 local two-client shared-city presence: **COMPLETE**; see [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]].
- Phase 1D.2 replicated appearance and starter clothing: **COMPLETE**; see [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]].
- Phase 1D.3 cold reconnect and visible-state restore: **COMPLETE**; see [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]].
- Phase 1D.4 local concurrency ladder: **COMPLETE**; see [[Development/Reports/Phase 1D4 Local Concurrency Ladder]].
- Phase 1D exit: **PASSED FOR THE LOCAL PROTOTYPE**. No beta instance ceiling or external-host readiness is claimed.
- Phase 1E owner defaults: **RESOLVED FOR THE FIRST STUDIO**; see [[Design/Decisions/DEC-011 Empty Starter Studio]] and [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- Phase 1E.1 private empty Studio enter/exit: **COMPLETE**; see [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]].
- Phase 1E.1a continuous mouse camera orbit correction: **COMPLETE**; see [[Development/Reports/Phase 1E1a Continuous Mouse Camera Orbit Correction]].
- Phase 1E.2 Studio ownership and return persistence: **COMPLETE**; see [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]].
- Phase 1E.3 six-tier housing progression catalog: **COMPLETE**; see [[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]].
- Phase 1E.4 player-visible locked housing goals: **COMPLETE**; see [[Development/Reports/Phase 1E4 Player-Visible Locked Housing Goals]].
- Phase 1E standalone foundation: **COMPLETE THROUGH CURRENT DEPENDENCIES**. Furniture activation remains blocked until Phase 1I supplies a legitimate purchase and ownership record.
- Phase 1F.1 player league view: **COMPLETE**; see [[Development/Reports/Phase 1F1 Player League View]].
- Phase 1F.2 stadium and public viewing-location graybox: **COMPLETE**; see [[Development/Reports/Phase 1F2 Stadium and Public Viewing Graybox]].
- Phase 1F.3 direct archived replay consumption in the stadium: **COMPLETE**; see [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]].
- Phase 1F.4 readable three-minute fixed-camera presentation: **COMPLETE**; see [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]] and [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]].
- Phase 1F.5 replay-view result invariance: **COMPLETE**; see [[Development/Reports/Phase 1F5 Replay View Result Invariance]].
- Phase 1F exit: **PASSED FOR THE CURRENT ARCHIVED-GAME SLICE**. The 82-game/two-team variety decision remains open and no backend reconnect is claimed.
- Next gate: **PHASE 1G.1 EMPTY ODDS BUCKS LEDGER**. Add only append-only, idempotent virtual-currency authority; do not invent starting balance, payout, cadence, price, or limit amounts. Sundale remains a working name.
- Current prerequisite note: UE 5.8, the aligned x64 runtime and .NET Framework 4.8 SDK, portable project, reproducible local Windows package, empty-map launch, LFS, generated-file ignores, primitive block/court iteration, collision, cold-process reopen, direct recorded-replay rendering, deterministic packaged traces, and local resource sampling are verified. UE 5.8 is now the approved beta client engine.

No later roadmap phase is authorized merely because it appears below.

## Critical path

| Order | Phase | Player-facing outcome | Status |
| --- | --- | --- | --- |
| 1 | 1A — Engine and packaged-build proof | A real 3D client can build and run | COMPLETE |
| 2 | 1B — Character selection and movement | Choose a default avatar and enter the world | COMPLETE |
| 3 | 1C — First-city identity and graybox | Walk between every required beta location | COMPLETE |
| 4 | 1D — Shared-city presence | Players see one another and equipped clothing | COMPLETE |
| 5 | 1E — Studio and apartment progression | Enter a persistent home and see the six-tier goal | FOUNDATION COMPLETE / FURNITURE IN 1I |
| 6 | 1F — League, stadium, and match viewing | Research and watch authoritative basketball | COMPLETE FOR CURRENT ARCHIVED GAME |
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
2. **1A.1a COMPLETE:** install the owner-approved free engine candidate and verify one no-project editor launch and normal exit.
3. **1A.1b COMPLETE:** align the official Microsoft x64 runtime, reboot manually, and verify the no-project editor without the earlier prerequisite warning.
4. **1A.1c COMPLETE:** create and reopen the smallest empty local Windows project with one empty default map.
5. **1A.1d COMPLETE:** package and run that unchanged empty Windows project; record disk, build time, launch time, frame time, memory, and explained runtime networking.
6. **1A.2a COMPLETE:** add one noncanonical primitive street block and basketball court to a separate benchmark map; record one representative asset iteration and preserve the empty-package baseline.
7. **1A.2b COMPLETE:** directly render the existing verified 421-frame replay without resimulating basketball.
8. **1A.3 COMPLETE:** owner accepted the benchmark evidence and approved Unreal Engine 5.8 for beta client development on July 19, 2026; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].

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

1. **1B.1 COMPLETE:** placeholder preset data for varied masculine/feminine presentations and skin tones; see [[Development/Reports/Phase 1B1 Character Preset Catalog]].
2. **1B.2 COMPLETE:** fast local selection screen with a safe default; see [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]].
3. **1B.3 COMPLETE:** one controllable primitive placeholder with the approved camera and input direction; see [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]].
4. **1B.4 COMPLETE:** worn off-white starter top and bottom are separate replaceable primitive equipment; see [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]].
5. **1B.5 COMPLETE:** the selected preset and equipped starter outfit save locally, enter the packaged placeholder world, and recover exactly after a cold process restart; see [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]].

### Owner gates

- **RESOLVED:** third-person camera and beta movement direction; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]].
- **RESOLVED FOR PLACEHOLDERS:** eight-preset minimum and neutral placeholder direction; final character art remains deferred to the later art-direction gate.

### Exit evidence

A fresh player can choose a preset, enter a packaged placeholder world, move, close, reopen, and recover the same appearance without demographic attributes affecting gameplay.

**PASSED:** the committed Phase 1B.1–1B.5 evidence satisfies every clause; see [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].

## Phase 1C — First-city identity and graybox

### Bible sections advanced

- Enter the first city.
- Required beta locations.
- Art, music, and storytelling.

### Owner gate — complete

The owner selected Concept B — Daymark / Sundale on July 20, 2026. The theme, mostly flat commons-ring geography, visual language, and atmosphere are approved under [[Design/Decisions/DEC-008 Beta First City Direction]]. Sundale remains a working name.

**Phase 1C.0 planning evidence:** three grounded modern-day alternatives are complete in [[Design/First City Concept Packages]] and [[Visual Maps/First City Concepts]]. Concept B is selected. Phase 1C.1 subsequently froze the minimal Sundale art-direction sheet and measurable compact walking loop in [[Design/Sundale Art Direction and Core Loop]].

### Smallest delivery path

1. **1C.1 COMPLETE:** freeze the minimal Sundale art-direction sheet and `800 m` projected compact walking loop; see [[Design/Sundale Art Direction and Core Loop]].
2. **1C.2 COMPLETE:** graybox the apartment entrance, one job, stadium/sportsbook, clothing store, furniture store, public court, commons, and connecting streets in a separate map.
3. **COMPLETE IN 1C.2:** add blocking-floor collision, map-owned spawn/game mode, primitive landmarks, named thresholds, and simple route wayfinding. This does not claim NPC navigation or final assets.
4. **COMPLETE IN 1C.2:** benchmark the full required route in a packaged build before final city art.

### Exit evidence

**PASSED:** one packaged placeholder avatar walked and ran the entire `800 m` core loop, visited all eleven checkpoints, returned home, and retained blocking-floor collision without final assets. See [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].

## Phase 1D — Shared-city presence

### Bible sections advanced

- Shared player presence.
- Avatar and clothing visibility.

### Smallest delivery path

1. **1D.1 COMPLETE:** two local playable clients join the packaged Sundale instance, receive replicated temporary identities, pass through one another, and produce server-observed movement evidence; see [[Development/Reports/Phase 1D1 Local Two-Client Shared City Presence]].
2. **1D.2 COMPLETE:** the server validates and replicates each selected preset plus equipped starter top/bottom; both packaged clients agree on both distinct players' visible state; see [[Development/Reports/Phase 1D2 Replicated Appearance and Starter Clothing]].
3. **1D.3 COMPLETE:** a cold local client process rejoins the same server from the existing validated appearance SaveGame and restores the exact server-visible preset/top/bottom tuple; see [[Development/Reports/Phase 1D3 Cold Reconnect Visible State Restore]].
4. **1D.4 COMPLETE:** one packaged build passed local `2`, `3`, and `4` total-client rungs; every process saw all submitted visible states and the server measured every remote mover; see [[Development/Reports/Phase 1D4 Local Concurrency Ladder]].

### Owner gates

- **RESOLVED FOR LOCAL PROOF:** two clients first, `$0.00`, and no region/hosting choice before evidence.
- **RESOLVED:** players pass through one another and use temporary visible `Player 1` / `Player 2` proof labels.
- **STILL OPEN:** reconnect and local ladder evidence now exist, but they do not justify inventing a beta instance ceiling.
- **REQUIRED BEFORE EXTERNAL BETA:** minimum blocking/reporting surface and explicit external hosting/service approval.

### Exit evidence

**PASSED FOR THE LOCAL PROTOTYPE:** the packaged ladder measured `2`, `3`, and `4` total clients. Every client saw all approved owner-submitted appearances and the server measured every remote client moving at least `300 cm`. This does not prove an external beta capacity ceiling.

## Phase 1E — Studio and apartment progression

### Bible sections advanced

- Discover the starter home.
- Housing and furniture.

### Smallest delivery path

1. **1E.1 COMPLETE:** enter, walk and orbit the camera inside, then leave one private, completely empty placeholder Studio; see [[Development/Reports/Phase 1E1 Private Empty Studio Enter and Exit]] and [[Development/Reports/Phase 1E1a Continuous Mouse Camera Orbit Correction]].
2. **1E.2 COMPLETE:** persist Studio ownership and the player's exact Sundale return location across a cold process restart; see [[Development/Reports/Phase 1E2 Studio Ownership and Return Persistence]].
3. **1E.3 COMPLETE:** represent the six locked tiers in validated data—Studio, 1BR, 2BR, 3BR, 4BR, and Penthouse—while only Studio is available; see [[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]].
4. **1E.4 COMPLETE:** show one player-visible text status for all six tiers without building five unavailable interiors or inventing prices; see [[Development/Reports/Phase 1E4 Player-Visible Locked Housing Goals]].
5. Activate predefined furniture snap points only after Phase 1I supplies a legitimate purchase and ownership record; never grant free demonstration furniture.

### Owner gates

- **RESOLVED:** the starting Studio contains no free furniture or decoration; see [[Design/Decisions/DEC-011 Empty Starter Studio]].
- **RESOLVED FOR BETA:** interiors are private and other-player apartment visits are excluded; see [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- **RESOLVED FOR FIRST PLACEMENT:** use predefined snap points after purchase; their exact count and locations remain later content work.
- **OPEN BEFORE BUILDING LARGER INTERIORS:** whether tiers use separate interiors or upgrades of one interior.

### Exit evidence

The player can return to the same owned, empty Studio; all six tiers exist as truthful progression data while unbuilt interiors are clearly unavailable. The first furniture appears only after a legitimate Phase 1I purchase, never as a free Phase 1E prop.

**FOUNDATION PASSED THROUGH CURRENT DEPENDENCIES:** ownership, return persistence, the empty Studio, all six tier records, and visible locked/unbuilt statuses are proven. Step 5 remains deliberately blocked until Phase 1I creates a legitimate purchase and item-ownership path, so Phase 1F may proceed without fabricating furniture.

## Phase 1F — League, stadium, and match viewing

### Bible sections advanced

- Basketball and wagering: league.
- Match presentation.
- Find the sports location.

### Smallest delivery path

1. **COMPLETE:** show the existing public teams, athletes, schedule, standings, availability, and history in the player client. See [[Development/Reports/Phase 1F1 Player League View]].
2. **COMPLETE:** graybox the stadium and public viewing location, with the future presentation area reserved and wagering kept inactive. See [[Development/Reports/Phase 1F2 Stadium and Public Viewing Graybox]].
3. **COMPLETE:** consume one verified archived replay directly inside the stadium without resimulation. See [[Development/Reports/Phase 1F3 Direct Archived Replay Consumption in Stadium]].
4. **COMPLETE:** owner-approved symbolic 3D placeholders, one fixed broadcast camera, text callouts without voice commentary, and a rendered three-minute presentation show score, clock, actors, key events, regulation/overtime status, and final seal. See [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F4 Readable Three Minute Stadium Presentation]].
5. **COMPLETE:** full watch, direct skip, mid-watch player skip, late arrival, and seal-validated cold reconnect all terminate at the identical frame `421`, score `101-104`, and authoritative seal without resimulation. Forged reconnect evidence renders zero frames. See [[Development/Reports/Phase 1F5 Replay View Result Invariance]].

### Owner gates

- **RESOLVED THROUGH PHASE 1F.5:** placeholder fidelity, one fixed camera, text-only callouts, three-minute full-watch duration, and result-invariant `S` skip; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]. Final art, crowd, replay cuts, condensed mode, and special-game duration remain later decisions.
- How an 82-game season remains varied with the initial two-team scope.

### Exit evidence

The player can research a scheduled game, go to the venue, watch or skip the same authoritative result, and inspect the immutable history. The client never resimulates basketball.

**EXIT PASSED FOR THE CURRENT ARCHIVED-GAME SLICE:** the packaged player path can watch or press `S` to skip to the same sealed result; QA evidence proves late-arrival and seal-validated cold-reconnect reconstruction. Production backend/session reconnect and 82-game variety remain unbuilt or open.

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

1. Freeze one tiny approved clothing set and one tiny furniture set. Both sets are Sundale-origin catalogs under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]]; later cities receive separate catalogs rather than sharing one universal store inventory.
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

1. **RESOLVED:** Unreal Engine 5.8 beta adoption; see [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption]].
2. **RESOLVED FOR PHASE 1B:** camera, movement, and minimum placeholder presets; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults]]. Final art remains later.
3. **RESOLVED FOR PHASE 1C:** Daymark / Sundale supplies the approved modern civic-commons direction; the primitive packaged `800 m` route passed Phase 1C exit. Sundale remains a working name and final art remains open; see [[Design/Decisions/DEC-008 Beta First City Direction]], [[Design/Sundale Art Direction and Core Loop]], and [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]].
4. **CURRENT OWNER GATE:** shared-city instance capacity, regions, collision, names, and minimal safety surface.
5. Apartment instancing, layouts, visits, and decorating controls.
6. 82-game schedule variety, team count, calendar, and presentation cadence.
7. **PARTIALLY RESOLVED:** current placeholder fidelity, fixed camera, text-only callouts, three-minute full-watch duration, and result-invariant player skip; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]. Final content treatment remains later.
8. Job, starting Odds Bucks, income, allowance, recovery, prices, and limits.
9. Wager markets, odds, payouts, lock, limits, correction, and cancellation.
10. Clothing/furniture catalog, pricing, equipment, placement, and refunds. City-origin identity is resolved under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].
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
