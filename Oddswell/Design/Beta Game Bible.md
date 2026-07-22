---
tags:
  - design
  - beta
  - scope
  - canonical
status: canonical-beta-draft
date: 2026-07-19
---

# OddsWell Beta Game Bible

## Purpose

This is the canonical product outline for the OddsWell beta. It tells the Scope Director what game we are building, what belongs in beta, what belongs later, and what still requires an owner decision.

The Scope Director must read this document before selecting a phase. It may not convert an unresolved idea into an approved feature, invent lore, choose a city or engine, or claim that an unimplemented system already exists.

## Truth labels

- **LOCKED:** explicit owner direction for the beta.
- **BETA TARGET:** intended beta behavior; details may still require testing or a smaller implementation decision.
- **OPEN:** the owner must decide before work that depends on it begins.
- **LATER:** part of the long-term vision, not beta scope.
- **GUARDRAIL:** a safety, authority, evidence, legal, platform, or production boundary.

## Authority order

1. The owner's newest explicit decision and accepted decision records.
2. This Beta Game Bible.
3. [[Design/Decisions/DEC-002 First Playable Scope|First Playable Scope]].
4. [[Design/Game Vision|Game Vision]].
5. The original long-form concept.

[[Development/Current Plan|Current Plan]] and phase reports prove what is actually built. They do not turn an idea into a product decision.

[[Development/Beta Delivery Roadmap|Beta Delivery Roadmap]] defines the dependency order used to turn this Bible into achievable phases. The Bible remains product authority when the roadmap is updated.

## Beta promise

**LOCKED:** OddsWell is a walkable 3D fantasy city centered on a persistent fictional basketball league and one unified virtual currency called **Odds Bucks**.

The beta fantasy is:

> Choose a simple character, arrive with almost nothing, explore a distinctive city, earn Odds Bucks through a job, visit the basketball stadium or sportsbook, wager on short watchable games, live with wins and losses, and improve your clothing and apartment over time.

The world should feel explorable and reactive rather than like a collection of menus. The inspiration is the freedom and everyday interaction of persistent world games, not copying their worlds, characters, missions, or visual identity.

## Beta win condition

The beta succeeds when a new player can complete one understandable loop:

`choose character -> enter city -> see studio -> find job -> earn Odds Bucks -> inspect basketball game -> place wager -> watch result -> settle wager -> buy or save toward a visible upgrade`

Every required beta feature must support this loop, the credibility of the fictional athletes, or safe operation of the loop.

## First-hour player journey

### 1. Choose a default character

- **LOCKED:** choose from a small set of default masculine and feminine character presentations with varied skin tones and appearances.
- **LOCKED:** the starting outfit is extremely simple, worn, nearly white clothing described by the owner as almost like rags.
- **LOCKED:** the minimum beta range is eight gameplay-identical placeholders: masculine and feminine presentations across the same four skin tones; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]].
- **BETA TARGET:** selection should be fast and should send the chosen preset directly into the game.
- **OPEN:** final body options, faces, hair, names, pronouns, accessibility options, and later editing.

The presets must not attach ability, wealth, intelligence, behavior, or athlete outcomes to gender presentation, skin tone, or any demographic feature.

### 2. Enter the first city

- **LOCKED:** the player enters one original 3D city and can walk around it.
- **LOCKED:** the first city needs an original name, theme, skyline, architecture, atmosphere, and visual identity.
- **PARTIALLY RESOLVED:** the owner selected the Sundale modern civic-commons direction under [[Design/Decisions/DEC-008 Beta First City Direction]]. Phase 1C then froze its compact route and proved the primitive packaged `800 m` graybox traversal in [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]]. The final city name, world name, culture details, and production art remain open.
- **GUARDRAIL:** no agent may invent and canonize the city identity without owner approval.

### 3. Discover the starter home

- **LOCKED:** every player starts with a modest studio apartment.
- **BETA TARGET:** the first hour makes the apartment easy to find and establishes it as the player's home and progression anchor.
- **OPEN:** arrival sequence, apartment access, loading/instancing, ownership UI, and decorating controls.

### 4. Find work and the sports location

- **LOCKED:** the city contains a visible place where the player earns Odds Bucks through a job.
- **LOCKED:** the city contains a basketball stadium and a physical location where the player can wager.
- **BETA TARGET:** the player can discover both places by exploring the city.
- **RESOLVED FOR THE CURRENT PLACEHOLDER:** Sundale's existing `Job` marker uses a server-validated `E` interaction. A local saved profile starts at `0` Odds Bucks, earns `100` on its first successful shift, and can earn another `100` after each rolling `24`-hour cooldown under [[Design/Decisions/DEC-015 Phase 1G4 Rolling Job Recovery Defaults]]. The first shift counts as period one, unused Odds Bucks accumulate, and there is no separate allowance. Final job fiction, tutorial guidance, map markers, prices, and whether wagering occurs in the stadium, an attached sportsbook, or both remain open.

### 5. Place and watch the first wager

- **LOCKED:** basketball is the first sport.
- **LOCKED:** the player can wager Odds Bucks and see the result through a visual game presentation.
- **BETA TARGET:** a complete game presentation should initially aim for roughly two to five minutes.
- **RESOLVED FOR THE CURRENT BETA PLACEHOLDER:** symbolic 3D athletes, one fixed broadcast camera, text callouts without voice commentary, an approximately three-minute full watch, and `S` to skip to the same sealed final result. Phase 1F.5 also proves late-arrival and seal-validated cold-reconnect reconstruction; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]. Whether important games later receive a longer presentation remains open.

### 6. Experience the consequence

- **LOCKED:** a winning wager adds Odds Bucks and a losing wager removes them.
- **LOCKED:** Odds Bucks can be saved or spent on apartment upgrades, furniture, and clothing.
- **BETA TARGET:** a player who runs out waits for or completes the next job/allowance opportunity instead of being permanently locked out.
- **RESOLVED FOR LOCAL BETA RECOVERY:** the player starts at `0`, earns `100` per successful placeholder shift, and becomes eligible again on a rolling `24`-hour cooldown. The first payout counts as the first period, balances accumulate, and no separate allowance or catch-up payout exists. Prices, wager limits, production account authority, clock integrity, and anti-inflation rules remain open.

## World and city scope

### Required beta locations

1. Starter apartment and apartment access point.
2. One job location.
3. Basketball stadium or simplified arena.
4. Physical wagering location associated with basketball.
5. Basic clothing store.
6. Basic furniture store.
7. Walkable streets connecting the core loop.

### World rules

- **LOCKED:** one city only for beta.
- **LOCKED:** players can walk around the city together and see one another's equipped clothing.
- **BETA TARGET:** compact, dense, memorable, and understandable on foot.
- **BETA TARGET:** the player should be able to enjoy moving through the city outside game time.
- **LATER:** additional cities, intercity travel, houses, mansions, vehicles, large social districts, and other sports venues.
- **GUARDRAIL:** do not build a generalized multi-city system before the first city proves what needs reuse.

### Shared player presence

- **LOCKED:** the beta city is multiplayer rather than a private city with only shared league results.
- **LOCKED:** clothing is a visible form of earned status and self-expression around other players.
- **LOCKED FOR BETA:** apartment interiors are private to their owning player and other-player apartment visits are not part of the beta. See [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- **BETA TARGET:** player movement, appearance, and equipped clothing replicate reliably within a bounded city instance.
- **OPEN:** instance capacity, regions, player collision, names, emotes, friends, parties, text chat, voice chat, blocking, reporting, and moderation.
- **LATER:** player-to-player exchange or trading of clothing and furniture. The future direction is preserved in [[Design/Version 1 Game Bible|Version 1 Game Bible]], but it is not beta authorization.

## Avatar and clothing

- **LOCKED:** player avatar selected from defaults during onboarding.
- **LOCKED:** minimal worn off-white starter clothing.
- **LOCKED:** third-person trailing camera; keyboard/mouse and controller walk, run, and jump; no beta combat, crouching, parkour, or vehicles. The beta starter top and bottom are replaceable equipment; see [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]].
- **LOCKED:** a basic clothing store lets the player buy improvements with Odds Bucks.
- **LOCKED:** purchasable clothing has durable city origin and is sold through its origin city's catalog; beta clothing merchandise is Sundale-specific under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]]. The shared worn starter outfit is an onboarding exception.
- **BETA TARGET:** purchased clothing visibly changes the avatar.
- **OPEN:** final character proportions, animation set, exact store clothing count, sizing/body compatibility, changing-room flow, and whether later store items are individual garments or complete outfits.
- **LATER:** a deep character creator, large cosmetic catalog, premium cosmetics, player marketplace, and user-generated items.

## Housing and furniture

### Apartment progression

- **LOCKED:** studio apartment is the starting home.
- **LOCKED:** the beta needs a visible ladder of larger apartments purchased with substantial amounts of Odds Bucks.
- **LOCKED:** there are six named tiers: Studio, One-bedroom, Two-bedroom, Three-bedroom, Four-bedroom, and Penthouse.
- **LATER:** detached houses and mansions.

### Furniture

- **LOCKED:** the starting Studio is completely empty of furniture and decoration; every placeable furnishing must be purchased later. Structural surfaces, the entry/exit, necessary lighting, and collision are not furniture. See [[Design/Decisions/DEC-011 Empty Starter Studio]].
- **LOCKED FOR BETA:** the first furniture-placement interaction uses predefined snap points after a valid purchase and ownership record exists. See [[Design/Decisions/DEC-012 Phase 1E Apartment Defaults]].
- **LOCKED:** a very basic furniture store sells items for Odds Bucks.
- **LOCKED:** purchasable furniture has durable city origin and is sold through its origin city's catalog; beta furniture merchandise is Sundale-specific under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].
- **LOCKED:** furniture is associated with the player's apartment progression.
- **BETA TARGET:** the player can acquire and see at least a small approved set of furniture in the owned apartment.
- **OPEN:** exact catalog, snap-point count and locations, rotation, storage, collision rules, room restrictions, refunds, and whether apartment layouts are separate interiors or upgrades of one interior.

## Basketball and wagering

### League

- **LOCKED:** basketball is the only beta sport.
- **LOCKED:** begin with two fictional teams in one shared authoritative league.
- **LOCKED:** athletes, results, statistics, injuries, and history persist.
- **LOCKED:** the regular-season target is 82 games per team, matching the current NBA regular-season count as a scale reference.
- **OPEN:** an 82-game season with only two beta teams may become repetitive; the owner must approve any team-count or schedule-format change rather than having an agent invent one.
- **LATER:** additional basketball teams, playoffs, full drafts, trades, free agency, detailed contracts, and complete 10-20-year career simulation unless separately promoted into beta.
- **LATER:** combat sports/fights are the next sport direction after basketball proves the full loop.

Official scale reference: [NBA 2025-26 regular-season schedule](https://www.nba.com/news/2025-26-nba-regular-season-schedule), which states that each team plays 82 regular-season games.

### Beta wager markets

The beta target includes:

1. Match winner.
2. Winning margin or spread-style outcome.
3. Whether the game reaches overtime.
4. Player scoring threshold, such as a fictional athlete reaching 30 points.

Each market must be introduced separately behind exact locking, settlement, replay, and audit evidence. Match winner remains the first and simplest market. A listed beta target does not authorize simultaneous implementation of every market.

### Approved basketball, odds, and wager separation

Under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]], the **Basketball Brain** chooses legal sport intentions, the **Basketball Rules and Outcome Engine** produces the authoritative sealed result, the **Basketball Odds Brain** produces a versioned offer from one equal public pregame snapshot, and the deterministic **Wager and Settlement Engine** locks and settles Odds Bucks against that result. Admin reconciliation observes the linked evidence without controlling it.

The data flow is one way. Wagers, stakes, Odds Bucks balances, purchases, and displayed odds never feed back into athlete decisions or game resolution. This architecture is approved; wager formulas and operating rules remain open.

### Wager integrity

- **GUARDRAIL:** the server owns balances, lock times, outcomes, and settlement.
- **GUARDRAIL:** every player receives the same competitively relevant information.
- **GUARDRAIL:** the client renders authoritative results and never resimulates basketball.
- **GUARDRAIL:** purchases, appearance, apartment level, and job history never influence athlete decisions or game outcomes.
- **GUARDRAIL:** probabilities, payouts, and displayed odds must be versioned, explainable, and auditable before a new market becomes active.
- **GUARDRAIL:** the Basketball Odds Brain receives only the same frozen public pregame snapshot shown to players; it receives no future result, hidden RNG state, or private advantage.
- **GUARDRAIL:** the Wager and Settlement Engine may consume a sealed authoritative result but has no control path back into basketball simulation.

## Odds Bucks economy

- **LOCKED:** **Odds Bucks** is the only game currency.
- **LOCKED:** no second lifestyle or betting currency.
- **LOCKED:** Odds Bucks may be earned through work and won or lost through wagering.
- **LOCKED:** Odds Bucks may be saved or spent on permitted clothing, furniture, and apartment upgrades.
- **LOCKED FOR BETA:** real-money Odds Bucks purchases are not part of the beta.
- **LATER:** real-money purchases may be considered only after legal, platform, payment, age-rating, regional, economy, fraud, and audit gates are satisfied.
- **RESOLVED FOR THE LOCAL BETA PLACEHOLDER:** starting balance is `0`; a successful placeholder shift pays `100`; the next shift becomes eligible after a rolling `24` hours; the first payout counts as period one; balances accumulate; and there is no separate allowance or missed-period catch-up under [[Design/Decisions/DEC-015 Phase 1G4 Rolling Job Recovery Defaults]]. Prices, wager sizes, broader payout limits, production account and time authority, sinks, and inflation targets remain open.

## Athletes and brains

### Athlete identity

- **LOCKED:** athletes are persistent fictional people, not interchangeable ratings.
- **LOCKED:** rare generational-superstar archetypes can perform at an elite level most nights across long careers.
- **LOCKED:** the league also contains stars, specialists, average athletes, and below-average athletes.
- **LOCKED:** a great shooter can remain a weak defender, and an elite defender may contribute little scoring.
- **GUARDRAIL:** real athletes may be used only as private design analogies; beta characters, identities, statistics, and stories remain fictional.

### Performance layers

`durable ability + age/development + role/opportunity + consistency + fatigue/health + life consequences + decisions + bounded randomness`

The Basketball Brain chooses legal intents. The authoritative rules engine resolves outcomes. The Athlete Life Brain controls bounded off-court choices and consequences. Neither brain silently rewrites match history.

### Beta life behavior target

- Training, rest, recovery, and social choices.
- Simple nightlife or club behavior that can reduce practice or recovery when chosen repeatedly.
- Injuries and availability.
- Temporary doubt, morale, or form only if represented with neutral fictional rules and visible causal evidence.
- Understandable consequence chains, for example:

`late night -> reduced recovery -> weaker practice/readiness -> possible performance or availability effect`

- **GUARDRAIL:** no demographic stereotypes, real-person allegations, medical diagnosis claims, or unexplained punishment.
- **GUARDRAIL:** the current frozen Phase 0 stack is the implementation truth. New beta behavior requires a separately measured phase; this document does not claim it already exists.

### Career boundary

- **BETA TARGET:** persistent athlete identity, current ratings, season statistics, availability, simple life choices, and visible history.
- **LATER:** complete 10-20-year career simulation, deep relationships, contracts, full transaction systems, retirement ecosystem, Hall of Fame, and retired-athlete careers.

## Match presentation

- **LOCKED:** the player sees what is happening rather than receiving only a final number.
- **BETA TARGET:** a readable, dramatic two-to-five-minute presentation using the authoritative event log.
- **BETA TARGET:** recognizable teams and athletes, score, game clock, key actions, overtime, and wager-relevant events.
- **RESOLVED FOR THE CURRENT BETA PLACEHOLDER:** symbolic 3D placeholders, one fixed broadcast camera, text callouts without voice commentary, approximately three minutes for a full watch, and `S` to skip to the same sealed final result. Late arrival and seal-validated cold reconnect resume only from the immutable archive; see [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]].
- **OPEN AFTER PHASE 1F.4:** final athlete and team art, crowd size, replay cuts, condensed mode, and whether important games receive longer presentations.
- **GUARDRAIL:** visual animation may interpolate movement but may not change the recorded score, clock, actors, events, or settlement.

## Art, music, and storytelling

- **BETA TARGET:** a distinctive original visual identity rather than a generic modern city.
- **BETA TARGET:** stylized production remains the current recommendation until the owner approves a final art bible.
- **OPEN:** city theme, visual style, character proportions, materials, palette, lighting, architecture, and team identities.
- **BETA TARGET:** background music supports exploration and sports atmosphere; the owner expects to work on music.
- **LOCKED:** storytelling is primarily environmental and emergent through exploration, athlete behavior, games, wins, losses, and progression rather than a required linear campaign.
- **GUARDRAIL:** another AI or artist may later own 3D design. The project brain must distinguish approved assets from concepts and must not treat generated images as production-ready models.

## Admin and operations

The local Brain Observatory grows into the game Admin Console only as real systems exist. Beta operations eventually need truthful controls or views for:

- Brain versions and evaluation evidence.
- Teams, athletes, schedule, games, replay, and league state.
- Clothing, furniture, and apartment-content availability.
- **CURRENT LOCAL EVIDENCE:** the validated machine-local Odds Bucks ledger, balance, and next-job eligibility are visible as an output-only read-only projection under [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]]. Wager settlement remains unavailable until separately authorized and proven.
- Audit history for consequential changes.

Admin features do not become beta player features. The server remains authoritative, and financial or live operations require authentication, least privilege, confirmations, and audit records.

## Beta feature matrix

| Area | Beta commitment | Status |
| --- | --- | --- |
| Character | Fast preset selection, varied appearances, minimal worn starter outfit | LOCKED / details OPEN |
| World | One walkable original 3D city | LOCKED / SUNDALE DIRECTION APPROVED / NAME OPEN |
| Home | Studio, 1BR, 2BR, 3BR, 4BR, and Penthouse progression | LOCKED / layouts OPEN |
| Work | One physical job location and repeatable Odds Bucks recovery | LOCKED / LOCAL RECOVERY PROVEN |
| Basketball | Two fictional teams, persistent league, watchable authoritative games | LOCKED |
| Wagers | Winner, margin, overtime, and player-points targets, introduced one at a time | BETA TARGET |
| Currency | Odds Bucks only; earn, wager, save, and spend | LOCKED |
| Real-money credits | Not in beta | LATER / gated |
| Clothing | Basic store and visible purchased upgrades | LOCKED / catalog OPEN |
| Furniture | Basic store and apartment-visible purchases | LOCKED / interaction OPEN |
| Athlete brains | Distinct talent, decisions, health, simple life behavior, visible consequences | LOCKED / some behavior not yet built |
| Careers | Persistent current identities and history | BETA TARGET |
| Full career ecosystem | 10-20 years, deep contracts, retirement, post-career roles | LATER |
| Other sports | Combat sports/fights after basketball | LATER |
| Houses and mansions | Beyond apartment progression | LATER |
| Multiplayer city presence | Players walk together and show equipped clothing | LOCKED / capacity OPEN |
| City theme and names | Sundale civic-commons direction; working name | DIRECTION APPROVED / NAME OPEN |

## Explicitly outside beta unless the owner changes scope

- Real-money Odds Bucks purchases.
- A second currency.
- Cash-out, player-to-player currency transfer, or player marketplace.
- Houses, mansions, multiple cities, intercity travel, or vehicles.
- Combat sports or any sport besides basketball.
- Full 10-20-year career ecosystem.
- Large clothing or furniture catalogs.
- Player-to-player exchange, trading, marketplace, or gifting of clothing and furniture.
- Open voice/text chat and large social systems.
- Final live-service scale, deployment, or monetization claims.
- Silent self-training, uncontrolled model updates, or invented neural-network claims.

## Unresolved owner decisions

The Scope Director must stop and ask when a phase depends on one of these:

1. **PARTIALLY RESOLVED:** Sundale's theme, commons-ring geography, atmosphere, palette, material family, wayfinding, and minimal loop are approved under [[Design/Decisions/DEC-008 Beta First City Direction]] and [[Design/Sundale Art Direction and Core Loop]]. Final city/world names, culture details, and production art remain open.
2. **RESOLVED:** beta camera and movement style under [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]].
3. **PARTIALLY RESOLVED:** eight-placeholder minimum range under [[Design/Decisions/DEC-007 Phase 1B Character Defaults|DEC-007]]; final character art and post-start customization remain open.
4. Apartment upgrade layouts and decorating interaction.
5. **RESOLVED FOR LOCAL BETA RECOVERY:** start at `0`, earn `100` per successful placeholder shift on a rolling `24`-hour cooldown, accumulate the balance, and provide no separate allowance or catch-up payout. Final job fiction and production account/time authority remain open.
6. How an 82-game season stays varied with the initial two-team scope.
7. **PARTIALLY RESOLVED:** current beta placeholder fidelity, camera, commentary, duration, and result-invariant player skip under [[Design/Decisions/DEC-013 Phase 1F4 Presentation Defaults]] and [[Development/Reports/Phase 1F5 Replay View Result Invariance]]; final art, crowd, replay cuts, condensed mode, and special-game duration remain open.
8. **PARTIALLY RESOLVED:** the Basketball Brain, Basketball Odds Brain, Rules and Outcome Engine, and Wager and Settlement Engine are isolated under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]]. Market order confirmation, rules, limits, payout formulas, lock time, correction/cancellation policy, and equal public information remain open.
9. Initial clothing and furniture catalog sizes.
10. Shared-city capacity, instancing, regions, communication, blocking, reporting, and moderation.
11. **RESOLVED:** Unreal Engine 5.8 is approved for beta client development under [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption|DEC-006]].
12. Minimum PC specification, release model, age target, and regions.

## Scope Director rules

Before proposing a phase, the Scope Director must:

1. Read this entire document, [[Development/Beta Delivery Roadmap|Beta Delivery Roadmap]], [[Development/Current Plan|Current Plan]], the latest phase report, and relevant accepted decisions.
2. Name the Beta Game Bible section advanced by the phase.
3. Explain the player-facing beta risk reduced by the phase.
4. Select the smallest phase that produces evidence or a usable piece of the core loop.
5. Keep **OPEN** items unresolved and ask the owner when they block progress.
6. Never schedule **LATER** work merely because it is described in the long-term concept.
7. Never claim a **LOCKED** or **BETA TARGET** feature is implemented without code, tests, and a phase report proving it.
8. Preserve the authoritative event-log boundary, server-owned settlement, equal-information rule, and frozen Phase 0 history.
9. Prefer placeholders and one real vertical path over generalized frameworks or large content production.
10. End every phase with the next smallest gate and any owner decision required before it.

## Current implementation boundary

- Phase 0 basketball simulation is frozen at its validated baseline except for demonstrated defects or a measured beta requirement.
- Phase 1A is complete. The owner accepted the measured UE 5.8 packaged-build, graybox, and authoritative replay-rendering evidence in [[Design/Decisions/DEC-006 Unreal Engine 5.8 Beta Adoption|DEC-006]].
- Phase 1B is complete. The committed catalog, safe-default selection, third-person movement, replaceable starter outfit, and exact local cold-process appearance recovery satisfy the character-onboarding exit evidence in [[Development/Reports/Phase 1B Exit Review Character Onboarding Evidence Closure]].
- Phase 1C is complete at the primitive-graybox boundary. The owner selected **Concept B — Daymark / Sundale**, Phase 1C.1 froze the `340 m × 280 m` footprint and `800 m` route, and Phase 1C.2 proved packaged walk/run traversal in [[Development/Reports/Phase 1C2 Primitive Sundale Graybox and Packaged Route Measurement]]. Sundale remains the working name; final city art is not proven.
- Phase 1D passed for the local shared-city prototype. External hosting and a beta capacity ceiling are not proven.
- Phase 1E's standalone Studio foundation is complete through ownership, cold return, and six visible housing tiers. Furniture activation remains dependent on a legitimate Phase 1I purchase and ownership path.
- Phase 1F passed for the current archived-game slice: watch, player skip, late arrival, and seal-validated cold reconstruction converge on the same result without client resimulation. Backend reconnect and full-season presentation variety are not proven.
- Phase 1G.1 provides the server-authoritative append-only Odds Bucks ledger, Phase 1G.2 adds the server-validated `Job` interaction, Phase 1G.3 proves the first persistent `100`-Odds-Bucks credit, Phase 1G.4 proves rolling `24`-hour repeat recovery across a cold packaged-process restart, and Phase 1G.5 exposes a validated output-only projection in Brain Admin; see [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]]. The local profile starts at `0`, balances accumulate, and there is no allowance or catch-up payout. No online account identity, trusted backend clock, backend reconnect, multi-device recovery, Admin mutation authority, price, purchase, wager, settlement, real-money path, or second currency is proven.
- Phase 1H.0 approves the isolated Basketball Odds Brain and Wager and Settlement Engine architecture in [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]]. This is design evidence only; no odds offer, wager request, stake debit, lock, settlement, or wager Admin view is implemented.
