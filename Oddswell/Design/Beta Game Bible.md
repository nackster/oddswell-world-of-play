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
- **RESOLVED FOR THE CURRENT WAGERING PLACEHOLDER:** the existing sportsbook route point is presented as the stadium ticket booth. When the player walks into its interaction radius, the normal-play prompt is exactly `Press E to open betting odds`; `E` opens the graphical read-only basketball market browser. Match Winner is active, while Margin, Overtime, Points, Rebounds, and Personal Fouls are visibly locked without invented odds. Final booth architecture, art, signage, wager submission treatment, and whether a separate sportsbook remains in the final city are open.

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
4. Player-points threshold, such as a fictional athlete reaching 30 points.
5. Player-rebounds threshold.
6. Player-fouls threshold after fouls become an authoritative recorded statistic.

Each market must be introduced separately behind exact probability, locking, settlement, replay, and audit evidence. Match Winner remains first. Points, rebounds, and fouls are separate player-prop gates; a listed beta target does not authorize simultaneous implementation of every market.

**CURRENT INTERFACE DIRECTION:** [[Design/Basketball Betting Interface Research]] establishes a short market-tab row, consistent selection cards, persistent slip, explicit pre-commit disclosures, keyboard/controller/mouse access, and text labels in addition to color. Phase 1H.24 implements that direction as a native read-only Unreal HUD. Only validated Match Winner odds are published; every later category remains locked until its separate evidence chain passes.

### Approved basketball, odds, and wager separation

Under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]], the **Basketball Brain** chooses legal sport intentions, the **Basketball Rules and Outcome Engine** produces the authoritative sealed result, the **Basketball Odds Brain** produces a versioned offer from one equal public pregame snapshot, and the deterministic **Wager and Settlement Engine** locks and settles Odds Bucks against that result. Admin reconciliation observes the linked evidence without controlling it.

The data flow is one way. Wagers, stakes, Odds Bucks balances, purchases, and displayed odds never feed back into athlete decisions or game resolution. This architecture is approved; each market still requires separately approved and proven operating rules.

**RESOLVED FOR MATCH WINNER V1:** [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]] freezes the public model, fair whole-Odds-Bucks payout formula, `10`–`100` stake range in increments of `10`, game-start lock, void/refund behavior, separate correction entries, and equal-public-information boundary. Player-prop formulas and thresholds remain separate later gates.

### Wager integrity

- **GUARDRAIL:** the server owns balances, lock times, outcomes, and settlement.
- **GUARDRAIL:** every player receives the same competitively relevant information.
- **GUARDRAIL:** the client renders authoritative results and never resimulates basketball.
- **GUARDRAIL:** purchases, appearance, apartment level, and job history never influence athlete decisions or game outcomes.
- **GUARDRAIL:** probabilities, payouts, and displayed odds must be versioned, explainable, and auditable before a new market becomes active.
- **GUARDRAIL:** the Basketball Odds Brain receives only the same frozen public pregame snapshot shown to players; it receives no future result, hidden RNG state, or private advantage.
- **GUARDRAIL:** the Wager and Settlement Engine may consume a sealed authoritative result but has no control path back into basketball simulation.
- **GUARDRAIL:** private Athlete Life Brain choices never enter an odds offer. Only explicitly published consequences shared equally with every player may affect a later probability.

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
- **CURRENT LOCAL EVIDENCE:** the validated machine-local Odds Bucks ledger, balance, and next-job eligibility are visible as an output-only read-only projection under [[Development/Reports/Phase 1G5 Read Only Odds Bucks Admin Reconciliation]]. The exact retained canonical loss chain is also visible through the independently validated output-only H26O Operations history card; broader player-visible history and generalized settlement remain unproved.
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
| Wagers | Winner, margin, overtime, then points/rebounds/fouls player props, introduced one at a time | BETA TARGET / MATCH WINNER RULES PROVEN |
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
8. **PARTIALLY RESOLVED:** the system boundary is isolated under [[Design/Decisions/DEC-016 Basketball Odds and Wager Isolation]], and Match Winner v1 rules are approved under [[Design/Decisions/DEC-017 Match Winner Odds and Stake Defaults]]. Margin, overtime, points, rebounds, and fouls need separate rules and evidence; external-beta legal/platform/age/region gates remain open.
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
- Phase 1H.1 freezes the first Match Winner rules, Phase 1H.2 implements the offer contract, Phase 1H.3 persists one machine-local accepted request plus stake debit, Phase 1H.4 persists one separate idempotent game-start lock decision, Phase 1H.5 links that chain to the exact sealed Season 1, Game 1 result, Phase 1H.6 derives the Harbor-selected/Mesa-winner decision as `lost`, `GrossReturnDue = 0`, status `decided_pending_apply`, Phase 1H.7 creates one separate immutable `settled_lost` finalization with gross return applied `0`, Phase 1H.8 exposes that loss through one independently validated read-only Operations reconciliation/history card, Phase 1H.9 proves one isolated Mesa-selected exact-win decision with probability `40000000`, the approved integer formula, `GrossReturnDue = 100`, and `decided_pending_apply`, Phase 1H.10 atomically applies that exact return once with one `+100` `match_winner_payout` entry plus one separate immutable `settled_won` finalization, Phase 1H.11 reuses the existing v1 read-only reconciliation/card for exact win evidence, Phase 1H.12 persists one separate immutable canceled-game disposition for an explicitly noncanonical QA chain, Phase 1H.13 derives one separate immutable `voided` decision with refund due `40` and status `decided_void_pending_refund`, Phase 1H.14 atomically applies the exact refund with one sequence-`3` `+40` `match_winner_refund` entry plus one separate immutable `settled_void` finalization, Phase 1H.15 reuses the existing reconciliation-v1 path and single independently validated Operations card for the exact canceled-wager history, Phase 1H.16 exposes the exact canonical Season 1, Game 1 offer through a strict read-only preview at the separate Sundale Sportsbook frontage, and Phase 1H.17 adds one explicitly noncanonical machine-local upcoming QA request at that frontage; see [[Development/Reports/Phase 1H17 Player Facing Upcoming QA Match Winner Request]]. In H17 QA mode the player can choose either offered team, choose `10`–`100` Odds Bucks in increments of `10`, review the exact gross return, and explicitly confirm. Server authority atomically persists one pending request and one linked stake debit; exact retry is duplicate-safe and invalid, late, conflicting, completed-H16, or underfunded attempts mutate nothing. The normal H16 canonical preview remains read-only. Canonical Season 1, Game 1 results, old exact loss `2/60`, old exact win `3/160`, and exact void `3/100` remain unchanged. No canonical player wager route/history, generalized refund service, correction, prop market, account, trusted clock, backend, deployment, real-money connection, or brain change is implemented.
- Phase 1H.18 adds one cold-restored, read-only receipt for the exact pending H17 QA request; see [[Development/Reports/Phase 1H18 Cold Restored Pending Match Winner Receipt]]. At the existing Sportsbook frontage, `E` shows only the independently validated request, offer/version, selection, stake, accepted/lock times, `accepted_pending_lock`, linked `2/-40` stake entry, and balance `60`, then closes on leave. Missing, stale, mismatched, duplicate, migrated, locked, resulted, or otherwise invented evidence exposes no partial values. The receipt process performs no request, debit, lock, result, migration, reconciliation write, or persisted mutation. Canonical submission, game-start and settlement integration, correction, and broader player history remain unproved.
- Phase 1H.19 adds one server-owned lock at exact authoritative QA game start `2100086400` for the exact noncanonical H17 request; see [[Development/Reports/Phase 1H19 Exact Upcoming QA Game Start Lock]]. The transition owns its fixed command, request, Season `100`, Game `1`, and time; no player command or timestamp enters it. It appends one immutable `locked` record while preserving the H17 request, offer, Sparks selection, stake `40`, accepted time, linked `2/-40` debit, balance `60`, and job cooldown. Cold exact retry is duplicate-safe and wrong, early, late, conflicting, second, invented, completed-H16, or malformed evidence mutates nothing. No canonical schedule, result, replay, simulation, settlement, correction, backend, deployment, real-money connection, UI, or brain change is proven.
- Phase 1H.20 adds one server-owned canceled-game disposition at exact post-lock QA time `2100086700` for the H17/H19 chain; see [[Development/Reports/Phase 1H20 Immutable Authoritative Upcoming QA Cancellation Evidence]]. The transition owns its fixed command/evidence pair, links, Season `100`, Game `1`, neutral `game_canceled` reason, and `closed_canceled` status. It preserves the exact request/debit, lock, ledger `2`, balance `60`, and cooldown, and creates no normal result, settlement, refund decision, credit, or finalization. Cold exact retry is duplicate-safe; wrong, conflicting, second, malformed, fabricated-result, or completed-H16 evidence mutates nothing. Canonical games, prior exact histories, simulator, brains, UI, backend, deployment, and real-money boundaries remain unchanged.
- Phase 1H.21 adds one server-owned void/refund-due decision for the exact H17/H19/H20 chain; see [[Development/Reports/Phase 1H21 Immutable Exact Upcoming QA Void Refund Due Decision]]. The fixed parameterless transition derives Sparks, stake `40`, `game_canceled`, `voided`, refund due `40`, and `decided_void_pending_refund` from the immutable request, lock, and cancellation evidence. Ledger count remains `2`, balance remains `60`, cooldown remains exact, and no refund is applied or finalized. Cold exact retry is duplicate-safe; wrong links/evidence, conflict, second, malformed, normal-result overlap, or persisted cancellation/decision tamper mutates nothing. Canonical games, prior exact histories, simulator, brains, UI, backend, deployment, and real-money boundaries remain unchanged.
- Phase 1H.22 atomically applies the exact H21 refund and records one separate immutable `settled_void` finalization for the H17/H19/H20/H21 chain; see [[Development/Reports/Phase 1H22 Idempotent Exact Upcoming QA Refund Application and Finalization]]. The fixed parameterless server transition appends ledger sequence `3`, `+40`, `match_winner_refund`, balance `100`, then binds refund due/applied `40`, count `3`, balance `100`, and every exact upstream link. H21 remains `decided_void_pending_refund`. Cold exact retry is duplicate-safe; wrong links, conflict, second finalization, tamper, malformed identity, normal-result overlap, or unexpected ledger evidence mutates nothing. No new history/UI, correction, canonical integration, simulator, brain, backend, deployment, or real-money path is proven.
- Phase 1H.23 cleans the current normal player-facing route without changing wager authority; see [[Development/Reports/Phase 1H23 Player Facing Ticket Booth Odds Presentation Cleanup]]. The existing sportsbook route point is labeled as the stadium ticket booth, proximity shows exactly `Press E to open betting odds`, and `E` shows only the matchup, decimal odds, approved stake range, lock rule, and one close instruction. Offer identity, commitments, Unix time, QA wording, return tables, and the persistent league shortcut hint remain off the normal player screen. The native text panel and physical booth are still placeholders; no production menu, final art, request/debit, settlement, new market, simulator, or brain behavior was added.
- Phase 1H.24 replaces that temporary text panel with an original native Unreal graphical browser; see [[Design/Basketball Betting Interface Research]] and [[Development/Reports/Phase 1H24 Graphical Ticket Booth Basketball Market Browser]]. Four concise market tabs, Match Winner selection cards, a persistent read-only slip, explicit active/locked wording, modal controls, mouse tabs, and keyboard/controller navigation are rendered in normal play. Margin, Overtime, Points, Rebounds, and Personal Fouls are visible but publish no odds. No canonical request/debit, new market contract, settlement, simulator, or brain behavior was added.
- Phase 1H.25 reuses the existing reconciliation-v1 writer, live API, independent validator, and single read-only Operations card for the exact noncanonical H17-to-H22 Season `100`, Game `1` cancellation/refund history; see [[Development/Reports/Phase 1H25 Read Only Exact Upcoming QA Wager Reconciliation History]]. It shows Sparks, stake/refund `40`, the exact request-to-finalization command chain, ledger `2/-40/60` then `3/+40/100`, `settled_void`, balance `100`, and net `0` only after the whole fixed chain validates. Missing, stale, partial, mixed, or tampered evidence shows no partial values. The card has no controls, and canonical submission, correction, broader history, later markets, simulator behavior, and brain behavior remain unproved.
- Phase 1H.26A through 1H.26P establish one active canonical local-beta opener from immutable schedule through one private canonical game result, immutable Match Winner request/lock/result link, deterministic loss decision, immutable loss finalization, output-only Admin history, and one exact player-visible settled-loss receipt; see [[Development/Reports/Phase 1H26K Immutable Private Canonical Game Result Record]], [[Development/Reports/Phase 1H26N Server Owned Exact Canonical Match Winner Loss Finalization]], [[Development/Reports/Phase 1H26O Read Only Exact Canonical Match Winner Loss Reconciliation History]], and [[Development/Reports/Phase 1H26P Read Only Player Facing Exact Canonical Settled Loss Receipt]]. H26H freezes every current `simulate_scheduled_game` input/version from immutable pre-wager evidence. H26I records one external digest-only execution receipt, H26J independently recomputes and seals that exact digest, and H26K records the exact private score/winner. H26L links the result, H26M derives Harbor-selected/Mesa-winner `lost` with return due `0`, H26N records `settled_lost` without a ledger entry, H26O reuses the existing reconciliation writer/API/card to show odds `1.7365`, potential `69`, final `97–101`, return `0`, net `-40`, count `2`, and balance `60` only after the complete retained chain validates, and H26P renders the exact Harbor-selected `97–101` loss, returned `0`, net `-40`, and balance `60` at the physical ticket booth from that same authoritative chain without writing. The older archived `101`–`104` result remains separate. Generalized player history, win/void/correction receipts, correction, broader history, new markets, payout/refund paths, simulator/brain change, backend, and deployment remain unproved.
- Phase 1H.26Q through 1H.26U connect one deliberately narrow normal player route to that retained canonical chain: interactive review, exact Harbor/`40` two-confirm placement, one automatic exact-tipoff H26G lock, one automatic H26H commitment after durable lock reload, and one automatic fixed-path private H26I handoff after durable H26H reload. H26H alone owns the private seed and frozen execution input derived from pre-wager H26A/H26B evidence; neither appears at the locked ticket booth. The execution consumer, H26I digest receipt, and H26J-H26P remain manual, so this does not claim automatic simulation, result publication, settlement, or history. See [[Development/Reports/Phase 1H26Q Interactive Canonical Match Winner Selection and Pre Commit Bet Slip Review]], [[Development/Reports/Phase 1H26R Exact Harbor 40 Canonical Wager Placement]], [[Development/Reports/Phase 1H26S Automatic Exact Canonical Tipoff Lock]], [[Development/Reports/Phase 1H26T Automatic Canonical Active Game Execution Commitment]], and [[Development/Reports/Phase 1H26U Automatic Private Canonical Game Execution Handoff]].
- Phase 1H.26AH.1 adds one bounded wayfinding correction for the exact validated settled-loss receipt; see [[Development/Reports/Phase 1H26AH1 Settled Receipt Ticket Booth Direction Cue]]. In Sundale city play only, outside the fixed ticket-booth radius and with its screen closed, one top-center cue reports the booth relative to the player's facing as ahead, left, right, or behind plus current meters. The cue yields to the existing proximity prompt and is absent without a valid receipt, on other maps, in Studio/stadium, or while the booth screen is open. This is not a navigation system, minimap, quest tracker, saved objective, generalized receipt history, or change to wagering, simulation, or any brain.
- Phase 1H.26AH closes the normal-player proof for that same exact settled-loss receipt and committed package; see [[Development/Reports/Phase 1H26AH Normal Player Settled Loss Receipt Lifecycle Proof]]. A player can follow the city cue, open the exact Harbor-selected `79-113` loss receipt, close it, leave, return, reopen it, cold restart, and reopen the identical receipt again. The H26P interaction reads the validated SaveGame directly and performs no H26O write; the authoritative save remains exact and rejected evidence exposes no partial receipt. This is proof-only, uses no QA receipt or teleport flags, and adds no production behavior, generalized history, wager path, simulation, or brain change.
- Phase 1H.26AI extends only the server-owned decision boundary to the exact current canonical Mesa-selected `40` win; see [[Development/Reports/Phase 1H26AI Exact Current Offer Mesa 40 Win Decision Compatibility and Isolated Proof]]. The fixed current offer probability `42413307` and approved integer formula derive gross return due `94`; the immutable decision is `won` and `decided_pending_apply`. The ledger remains `2/-40/60`, the retained Harbor-loss route remains exact, invalid evidence fails closed, and no payout, finalization, reconciliation, receipt, normal-player Mesa wager path, simulator change, or brain change is implemented.
- Phase 1H.26AJ applies that exact current return once; see [[Development/Reports/Phase 1H26AJ Exact Current Mesa 94 Return Application and Win Finalization]]. The server-owned atomic finalizer appends sequence `3`, `+94`, `match_winner_payout`, reaches balance `154`, and records one immutable `settled_won` finalization while the H26AI decision remains unchanged. Exact retry is duplicate-safe and altered/conflicting evidence mutates nothing. The existing load contract regenerates its current-value read-only projection, but independent Admin validation and any player-facing win receipt remain unproved.
- Phase 1H.26AK independently validates and displays that exact current win through the existing read-only Brain Admin Operations card; see [[Development/Reports/Phase 1H26AK Read Only Exact Current Win Reconciliation History]]. The fixed H26AJ projection shows Mesa selected and won, probability `42413307`, score `79-113`, return `94`, net `+54`, three ledger entries, balance `154`, `settled_won`, replay seal, and exact command/ledger linkage only after the whole allowlisted chain validates. Altered, mixed, or partial evidence exposes no partial values. No endpoint, card, schema, dependency, Admin mutation control, or player receipt was added.
- Phase 1H.26AL reuses the same physical ticket-booth receipt for that exact current win; see [[Development/Reports/Phase 1H26AL Read Only Player Facing Exact Current Win Receipt]]. After the complete H26AJ chain validates, the player-facing surface shows `WIN`, Mesa selected, final `79-113`, returned `94`, net `+54`, balance `154`, and one close instruction. The read is byte-stable and performs no write. Pending, partial, mixed, or altered evidence exposes no receipt, and both approved loss variants remain exact. This does not create a normal-player Mesa wager path, generalized history, another settlement action, or any brain/simulator change.
- Phase 1H.26V freezes the design-only consumer authority boundary in [[Design/Decisions/DEC-019 Private Local Execution Supervisor Boundary]]: local-beta engineering may later prove one separate, explicit, one-shot trusted development supervisor with fixed private directories, an absolute allowlisted interpreter, existing `phase1h.execution`, one atomic commitment-keyed attempt, a `120`-second timeout, bounded private logs, and fail-closed no-repair behavior. Bundled or client-spawned Python is rejected; a trusted backend worker is deferred. No supervisor, process, receipt, service, backend, runtime behavior, or H26J-H26P automation is implemented. See [[Development/Reports/Phase 1H26V Private Execution Consumer Authority Review]].
