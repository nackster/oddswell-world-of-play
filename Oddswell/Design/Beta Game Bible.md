---
tags:
  - design
  - beta
  - scope
  - canonical
status: canonical-beta-draft
date: 2026-07-18
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
- **BETA TARGET:** selection should be fast and should send the chosen preset directly into the game.
- **OPEN:** exact preset count, body options, faces, hair, names, pronouns, accessibility options, and later editing.

The presets must not attach ability, wealth, intelligence, behavior, or athlete outcomes to gender presentation, skin tone, or any demographic feature.

### 2. Enter the first city

- **LOCKED:** the player enters one original 3D city and can walk around it.
- **LOCKED:** the first city needs an original name, theme, skyline, architecture, atmosphere, and visual identity.
- **OPEN:** city name, world name, biome, culture, layout, weather, and art direction.
- **GUARDRAIL:** no agent may invent and canonize the city identity without owner approval.

### 3. Discover the starter home

- **LOCKED:** every player starts with a modest studio apartment.
- **BETA TARGET:** the first hour makes the apartment easy to find and establishes it as the player's home and progression anchor.
- **OPEN:** arrival sequence, apartment access, loading/instancing, ownership UI, and decorating controls.

### 4. Find work and the sports location

- **LOCKED:** the city contains a visible place where the player earns Odds Bucks through a job.
- **LOCKED:** the city contains a basketball stadium and a physical location where the player can wager.
- **BETA TARGET:** the player can discover both places by exploring the city.
- **OPEN:** job type, job interaction, tutorial guidance, map markers, allowance timing, and whether wagering occurs in the stadium, an attached sportsbook, or both.

### 5. Place and watch the first wager

- **LOCKED:** basketball is the first sport.
- **LOCKED:** the player can wager Odds Bucks and see the result through a visual game presentation.
- **BETA TARGET:** a complete game presentation should initially aim for roughly two to five minutes.
- **OPEN:** exact duration, broadcast style, ability to skip or accelerate, and whether important games receive a longer presentation.

### 6. Experience the consequence

- **LOCKED:** a winning wager adds Odds Bucks and a losing wager removes them.
- **LOCKED:** Odds Bucks can be saved or spent on apartment upgrades, furniture, and clothing.
- **BETA TARGET:** a player who runs out waits for or completes the next job/allowance opportunity instead of being permanently locked out.
- **OPEN:** daily grant amount, job payout, cadence, minimum balance, prices, wager limits, and anti-inflation rules.

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
- **BETA TARGET:** compact, dense, memorable, and understandable on foot.
- **BETA TARGET:** the player should be able to enjoy moving through the city outside game time.
- **LATER:** additional cities, intercity travel, houses, mansions, vehicles, large social districts, and other sports venues.
- **GUARDRAIL:** do not build a generalized multi-city system before the first city proves what needs reuse.

## Avatar and clothing

- **LOCKED:** player avatar selected from defaults during onboarding.
- **LOCKED:** minimal worn off-white starter clothing.
- **LOCKED:** a basic clothing store lets the player buy improvements with Odds Bucks.
- **BETA TARGET:** purchased clothing visibly changes the avatar.
- **OPEN:** character proportions, camera view, animation set, exact clothing count, sizing/body compatibility, changing-room flow, and whether individual garments or complete outfits are sold.
- **LATER:** a deep character creator, large cosmetic catalog, premium cosmetics, player marketplace, and user-generated items.

## Housing and furniture

### Apartment progression

- **LOCKED:** studio apartment is the starting home.
- **LOCKED:** the beta needs a visible ladder of larger apartments purchased with substantial amounts of Odds Bucks.
- **BETA TARGET:** one-bedroom, two-bedroom, three-bedroom, and four-bedroom apartments are named upgrade levels.
- **OPEN:** the owner's speech also named a "pet house," likely meaning "penthouse," while describing five apartment levels. Confirm the intended word and whether the studio is included in the count.
- **LATER:** detached houses and mansions.

### Furniture

- **LOCKED:** a very basic furniture store sells items for Odds Bucks.
- **LOCKED:** furniture is associated with the player's apartment progression.
- **BETA TARGET:** the player can acquire and see at least a small approved set of furniture in the owned apartment.
- **OPEN:** exact catalog, placement controls, rotation, storage, collision rules, room restrictions, refunds, and whether apartment layouts are separate interiors or upgrades of one interior.

## Basketball and wagering

### League

- **LOCKED:** basketball is the only beta sport.
- **LOCKED:** begin with two fictional teams in one shared authoritative league.
- **LOCKED:** athletes, results, statistics, injuries, and history persist.
- **OPEN:** the owner referenced a regular-basketball-like season length, but the exact number was unclear in the speech. The Scope Director must not infer it.
- **LATER:** additional basketball teams, playoffs, full drafts, trades, free agency, detailed contracts, and complete 10-20-year career simulation unless separately promoted into beta.
- **LATER:** combat sports/fights are the next sport direction after basketball proves the full loop.

### Beta wager markets

The beta target includes:

1. Match winner.
2. Winning margin or spread-style outcome.
3. Whether the game reaches overtime.
4. Player scoring threshold, such as a fictional athlete reaching 30 points.

Each market must be introduced separately behind exact locking, settlement, replay, and audit evidence. Match winner remains the first and simplest market. A listed beta target does not authorize simultaneous implementation of every market.

### Wager integrity

- **GUARDRAIL:** the server owns balances, lock times, outcomes, and settlement.
- **GUARDRAIL:** every player receives the same competitively relevant information.
- **GUARDRAIL:** the client renders authoritative results and never resimulates basketball.
- **GUARDRAIL:** purchases, appearance, apartment level, and job history never influence athlete decisions or game outcomes.
- **GUARDRAIL:** payouts and displayed odds must be versioned, explainable, and auditable before a new market becomes active.

## Odds Bucks economy

- **LOCKED:** **Odds Bucks** is the only game currency.
- **LOCKED:** no second lifestyle or betting currency.
- **LOCKED:** Odds Bucks may be earned through work and won or lost through wagering.
- **LOCKED:** Odds Bucks may be saved or spent on permitted clothing, furniture, and apartment upgrades.
- **LOCKED FOR BETA:** real-money Odds Bucks purchases are not part of the beta.
- **LATER:** real-money purchases may be considered only after legal, platform, payment, age-rating, regional, economy, fraud, and audit gates are satisfied.
- **OPEN:** starting balance, daily allowance, job income, prices, wager sizes, payout limits, recovery rules, sinks, and inflation targets.

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
- **OPEN:** 2D, 2.5D, or full 3D match fidelity; camera language; commentary; replay cuts; crowd size; skipping; condensed mode; and final duration.
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
- Odds Bucks ledger and wager settlement only after those systems are authorized.
- Audit history for consequential changes.

Admin features do not become beta player features. The server remains authoritative, and financial or live operations require authentication, least privilege, confirmations, and audit records.

## Beta feature matrix

| Area | Beta commitment | Status |
| --- | --- | --- |
| Character | Fast preset selection, varied appearances, minimal worn starter outfit | LOCKED / details OPEN |
| World | One walkable original 3D city | LOCKED / identity OPEN |
| Home | Starter studio and purchasable larger-apartment ladder | LOCKED / exact tiers OPEN |
| Work | One physical job location and repeatable Odds Bucks recovery | LOCKED / mechanic OPEN |
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
| Multiplayer city presence | Not yet decided | OPEN |
| City theme and names | Must be owner-approved | OPEN |

## Explicitly outside beta unless the owner changes scope

- Real-money Odds Bucks purchases.
- A second currency.
- Cash-out, player-to-player currency transfer, or player marketplace.
- Houses, mansions, multiple cities, intercity travel, or vehicles.
- Combat sports or any sport besides basketball.
- Full 10-20-year career ecosystem.
- Large clothing or furniture catalogs.
- Open voice/text chat and large social systems.
- Final live-service scale, deployment, or monetization claims.
- Silent self-training, uncontrolled model updates, or invented neural-network claims.

## Unresolved owner decisions

The Scope Director must stop and ask when a phase depends on one of these:

1. First world and city name, theme, geography, culture, and visual identity.
2. Exact player camera and movement style.
3. Exact character preset range and post-start customization.
4. Whether "pet house" meant "penthouse," and whether beta has five or six total apartment tiers.
5. Apartment upgrade layouts and decorating interaction.
6. Exact job, payout, allowance, and recovery cadence.
7. Exact basketball season length; the spoken number was unclear.
8. Final game-presentation duration and fidelity.
9. Order, rules, limits, and payout formulas for the four beta wager markets.
10. Initial clothing and furniture catalog sizes.
11. Whether beta players see one another in the city or only share the league and results.
12. Engine and exact version, followed by explicit download, license, disk, and project-creation approval.
13. Minimum PC specification, release model, age target, and regions.

## Scope Director rules

Before proposing a phase, the Scope Director must:

1. Read this entire document, [[Development/Current Plan|Current Plan]], the latest phase report, and relevant accepted decisions.
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
- Phase 1A.0 verified the local workstation and replay interface.
- The next implementation gate is owner-approved installation of one named 3D engine/version and an empty packaged-build benchmark.
- No engine installation, city, avatar, apartment, Odds Bucks ledger, wager settlement, clothing store, or furniture store is complete merely because it appears in this beta plan.

