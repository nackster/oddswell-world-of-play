---
tags:
  - design
  - version-1
  - scope
  - canonical
status: canonical-v1-draft
date: 2026-07-18
---

# OddsWell Version 1 Game Bible

## Purpose

This document defines the first OddsWell version that may follow the beta. It protects the post-beta direction without allowing agents to skip beta, invent Version 1 features, or mistake a future idea for an approved release commitment.

Version 1 does not begin automatically. The owner must first approve a formal beta exit and a Version 1 scope freeze.

## Release order

1. **Beta:** prove the complete player loop defined in [[Design/Beta Game Bible|Beta Game Bible]].
2. **Version 1:** harden the proven beta into a stable first post-beta release.
3. **Later expansion:** consider new sports, cities, houses, trading, real-money purchases, and deeper social systems only through separate owner decisions.

No Version 1 phase may displace an unfinished beta requirement.

## Truth labels

- **INHERITED:** locked by the Beta Game Bible and retained in Version 1.
- **V1 REQUIRED:** necessary for a truthful, stable post-beta release of an inherited feature.
- **OPEN:** requires owner approval before implementation.
- **POST-V1 CANDIDATE:** remembered future direction, not Version 1 scope.
- **GUARDRAIL:** authority, safety, evidence, legal, platform, security, or operational boundary.

## Version 1 promise

Version 1 delivers a stable shared 3D OddsWell city where players can:

- Enter with a persistent avatar.
- Walk around together and visibly show earned clothing.
- Live in and upgrade an apartment.
- Work for Odds Bucks.
- Follow a persistent fictional basketball league.
- Place approved Odds Bucks wagers.
- Watch short authoritative games.
- Keep their balance, clothing, furniture, apartment, wager history, and league history across sessions.

Version 1 is the beta fantasy made dependable and coherent. It is not automatically a larger world.

## Version 1 player loop

`sign in -> enter shared city -> check home and appearance -> work or review league -> wager Odds Bucks -> watch or return for result -> settle -> buy/save/equip/decorate -> continue through the 82-game season`

The loop must remain understandable to a new player and durable for a returning player.

## Inherited world scope

- **INHERITED:** one original compact 3D city.
- **INHERITED:** players can see one another walking in the city.
- **INHERITED:** equipped clothing is visible to nearby players.
- **INHERITED:** apartment building, job, basketball stadium/wagering location, clothing store, furniture store, and connecting streets.
- **V1 REQUIRED:** stable city-session joining, leaving, reconnecting, and avatar replication.
- **V1 REQUIRED:** bounded instancing or capacity rules that keep movement and appearance reliable on supported hardware.
- **OPEN:** maximum players per city instance, server region strategy, reconnect behavior, player collision, emotes, names above avatars, friends, parties, and apartment visits.
- **OPEN:** text chat, voice chat, direct messaging, and public groups. None may ship without moderation, privacy, blocking, reporting, and age-safety decisions.
- **POST-V1 CANDIDATE:** more cities, travel, vehicles, and large social districts.

## Avatar and clothing

- **INHERITED:** fast default-character choice with varied masculine/feminine presentations, skin tones, and appearances.
- **INHERITED:** worn off-white starter clothing.
- **INHERITED:** basic clothing store using Odds Bucks.
- **INHERITED:** purchased clothing retains its origin city; the beta catalog is Sundale-specific, and any separately approved future city receives its own catalog under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].
- **INHERITED:** owned clothing can be equipped and shown to other players.
- **V1 REQUIRED:** avatar appearance and equipped clothing persist accurately across sessions and city instances.
- **V1 REQUIRED:** missing or invalid cosmetic data falls back safely without deleting ownership.
- **OPEN:** final preset count, body system, hair, faces, accessories, outfit slots, catalog size, rarity, seasonal collections, and changing-room flow.
- **POST-V1 CANDIDATE:** player-created clothing and large cosmetic catalogs.

## Apartments and furniture

### Inherited apartment ladder

1. Studio — starting apartment.
2. One-bedroom.
3. Two-bedroom.
4. Three-bedroom.
5. Four-bedroom.
6. Penthouse.

- **INHERITED:** larger apartments are purchased with substantial Odds Bucks.
- **INHERITED:** a basic furniture store supplies visible apartment items.
- **INHERITED:** purchased furniture retains its origin city; the beta catalog is Sundale-specific, and any separately approved future city receives its own catalog under [[Design/Decisions/DEC-009 City-Origin Clothing and Furniture]].
- **V1 REQUIRED:** apartment ownership, equipped/placed furniture, and upgrades persist without duplication or loss.
- **OPEN:** layouts, prices, storage, placement rules, rotation, collision, capacity, refunds, apartment visits, and whether each tier is a separate interior.
- **POST-V1 CANDIDATE:** houses and mansions.

## Shared basketball league

- **INHERITED:** basketball remains the first and only committed sport.
- **INHERITED:** fictional teams and athletes share one authoritative schedule, results, statistics, injuries, and history.
- **INHERITED:** the regular-season target is **82 games per team**, matching the current NBA regular-season count as a scale reference.
- **GUARDRAIL:** OddsWell remains a fictional league and does not copy NBA teams, athletes, branding, schedules, or intellectual property.
- **OPEN:** Version 1 team count. Two beta teams playing 82 games only against one another may be too repetitive; agents may not invent expansion teams to solve that product decision.
- **OPEN:** calendar duration, games per real day, time zones, playoffs, tie-breakers, off-season timing, and whether all 82 games are individually presented or some are summarized.
- **POST-V1 CANDIDATE:** combat sports/fights after basketball proves the complete release loop.

Official scale reference: [NBA 2025-26 regular-season schedule](https://www.nba.com/news/2025-26-nba-regular-season-schedule), which states that each team plays 82 regular-season games.

## Athletes and brains

- **INHERITED:** rare generational-superstar archetypes, other stars, specialists, average athletes, and below-average athletes.
- **INHERITED:** durable ability, role/opportunity, consistency, fatigue, health, life consequences, decisions, and bounded randomness remain separate layers.
- **INHERITED:** simple train, rest, recover, socialize/nightlife, injury, and temporary-form consequences use visible fictional causal chains.
- **INHERITED:** sport brains choose legal intent; rules engines resolve; event logs record; clients render.
- **V1 REQUIRED:** every active brain/policy version is named, auditable, replay-safe, and truthfully represented in Admin.
- **V1 REQUIRED:** stored games and completed history remain immutable across brain updates.
- **OPEN:** any deeper personality, relationship, mental-state, story, discipline, legal-event, or long-term career feature not already proven in beta.
- **POST-V1 CANDIDATE:** complete 10-20-year career ecosystems, contracts, retirement, Hall of Fame, and post-career roles.

No Version 1 claim may describe fictional deterministic behavior as real-world realism, consciousness, neural activity, autonomous learning, or silent self-improvement.

## Match presentation

- **INHERITED:** watchable representation of the authoritative event log.
- **INHERITED:** initial target of roughly two to five minutes.
- **INHERITED:** score, clock, teams, athletes, key actions, overtime, and wager-relevant events.
- **V1 REQUIRED:** reconnecting or skipping presentation never changes the result or settlement.
- **V1 REQUIRED:** players who watch, skip, arrive late, or remain offline receive the same final authoritative outcome.
- **OPEN:** final 2D/2.5D/3D fidelity, broadcast cameras, commentary, crowd, replay cuts, highlights, condensed mode, accessibility, and performance tiers.

## Wagers and Odds Bucks

- **INHERITED:** Odds Bucks is the only currency.
- **INHERITED:** earn through work; win or lose through wagers; save; spend on approved clothing, furniture, and apartments.
- **INHERITED:** beta market targets are match winner, winning margin, overtime, and player-points thresholds, activated one at a time only after evidence.
- **V1 REQUIRED:** server-authoritative append-only balance ledger, idempotent settlement, exact lock times, versioned odds/payouts, reconciliation, recovery, and Admin audit.
- **V1 REQUIRED:** equal competitively relevant information and no paid, cosmetic, social, or housing advantage in game outcomes.
- **V1 REQUIRED:** zero-balance players retain a non-paid work/allowance recovery route.
- **OPEN:** starting balance, job income, allowance cadence, wager limits, market limits, payout formulas, economy sinks, inflation targets, and correction/cancellation policy.
- **OPEN:** real-money Odds Bucks purchases. They do not become Version 1 scope merely because Version 1 follows beta.
- **GUARDRAIL:** real-money purchases require separate owner approval plus current legal, platform, payment, regional, age-rating, fraud, security, economy, and audit review.

## Work and lifestyle progression

- **INHERITED:** at least one visible city job or recovery activity.
- **INHERITED:** work supplies Odds Bucks and prevents permanent lockout after losses.
- **V1 REQUIRED:** job completion and payouts are server-authoritative, rate-limited, auditable, and resilient to disconnects or duplicate submissions.
- **OPEN:** job fantasy, interaction, difficulty, duration, daily limits, failure state, repeatability, and whether allowance and work are separate systems.

## Item ownership and future trading

- **INHERITED:** players own clothing and furniture and can display them in the approved ways.
- **V1 REQUIRED:** ownership records are server-authoritative and protected from duplication, accidental deletion, rollback, and double spending.
- **POST-V1 CANDIDATE:** players may eventually exchange or trade clothing and furniture.

Trading is intentionally not a Version 1 commitment. Before it can enter a selection phase, the owner must approve its exact form and the project must address inventory authority, duplication, fraud, account theft, coercion/scams, moderation, support, market manipulation, rollback, taxes/legal exposure where applicable, platform rules, and the interaction with any real-money Odds Bucks purchase.

No agent may create a marketplace, transfer endpoint, trade UI, item valuation, auction house, or player-to-player ownership transfer from this future note alone.

## Art, audio, and world identity

- **INHERITED:** one distinctive original city and coherent character/item/world art direction.
- **INHERITED:** environmental and emergent storytelling through exploration, athletes, games, wins, losses, and progression.
- **INHERITED:** the owner expects to contribute background music.
- **V1 REQUIRED:** approved source, license, version, and production status for every shipped asset.
- **V1 REQUIRED:** consistent character, clothing, furniture, city, team, UI, lighting, and audio language.
- **OPEN:** city/world name, theme, architecture, palette, weather, music direction, team identities, final character style, and final asset-production ownership.
- **POST-BETA DIRECTION:** later cities may explore substantially more elaborate identities, including a water-focused city and a Tartaria-inspired monumental city. These are future concept directions only; they do not authorize beta scope, a multi-city system, production assets, or historical claims.

## Persistence, multiplayer, and operations

Version 1 cannot truthfully release the shared-city loop without:

- Persistent player account and avatar identity.
- Server-authoritative Odds Bucks, inventory, apartment ownership, wagers, and settlement.
- Shared league state and immutable match history.
- Secure authentication and session handling.
- Save, backup, restore, migration, and rollback evidence.
- Capacity, latency, disconnect, and reconnect tests.
- Player blocking/reporting and moderation appropriate to the approved social surface.
- Audit logs for consequential Admin actions.
- Monitoring and recovery procedures for the systems actually released.

These are release requirements, not permission to choose vendors, deploy publicly, collect personal data, or buy services without owner approval.

## Version 1 Admin Console

The Admin Console should expose only real, authorized systems:

- Game and brain versions, evaluation status, and evidence.
- Teams, athletes, 82-game schedule, league history, and replay verification.
- City-session health and player-presence status without exposing private information.
- Clothing, furniture, and apartment content availability.
- Odds Bucks ledger reconciliation and wager settlement after those systems exist.
- Audit history, confirmations, roles, and permissions for consequential changes.

The Admin Console never edits authoritative production data directly without validated commands, access controls, and audit evidence.

## Beta-to-Version-1 promotion gates

Version 1 work may begin only after the owner accepts a beta exit report covering:

1. The complete first-hour loop works end to end.
2. Shared-city movement and equipped clothing are stable at a measured player count.
3. The authoritative basketball, wager, and settlement path passes replay and ledger reconciliation.
4. Zero-balance recovery works without real-money payment.
5. Apartment, clothing, furniture, and Odds Bucks persist through reconnect, migration, and rollback tests.
6. Players understand the fictional league, wagers, outcomes, and upgrade loop in observed beta testing.
7. Performance meets an owner-approved PC target.
8. Security, privacy, moderation, accessibility, platform, age-rating, and regional gates for the approved beta surface are reviewed.
9. Critical defects have measured owners and resolution status.
10. The owner approves the exact Version 1 feature freeze.

## Version 1 feature matrix

| Area | Version 1 direction | Status |
| --- | --- | --- |
| Core loop | Stable inherited city/work/wager/watch/upgrade loop | INHERITED / V1 REQUIRED |
| Shared city | Players walk together and show equipped clothing | INHERITED |
| Apartments | Studio through Penthouse | INHERITED |
| Basketball | Fictional authoritative league; 82 games per team | INHERITED |
| Team count | More than the two-team beta | OPEN |
| Wager markets | Only beta-proven markets | INHERITED / evidence-gated |
| Odds Bucks | One currency; no automatic real-money purchase | INHERITED / real money OPEN |
| Clothing/furniture ownership | Persistent and visible | INHERITED / V1 REQUIRED |
| Player item trading | Remembered but not scheduled | POST-V1 CANDIDATE |
| Other sports/fights | Not automatically Version 1 | POST-V1 CANDIDATE |
| Additional cities/houses | Not automatically Version 1 | POST-V1 CANDIDATE |
| Social communication | Requires owner and safety scope | OPEN |
| Public deployment | Requires separate approval and release gates | OPEN |

## Explicitly not authorized by this Version 1 draft

- Starting Version 1 before beta exit approval.
- Player-to-player item trading or marketplace.
- Real-money Odds Bucks purchases.
- Cash-out or conversion to real-world value.
- Additional sports, cities, houses, mansions, or vehicles.
- Open chat, voice, direct messages, or user-generated content.
- Silent model retraining or unreviewed brain promotion.
- Public deployment, paid infrastructure, paid assets, or third-party services.

## Unresolved owner decisions for Version 1

1. Version 1 release purpose: closed post-beta test, early access, or public commercial release.
2. City/world identity and final art direction.
3. Engine and exact version.
4. Team count needed to make an 82-game season varied and believable.
5. Real-time season calendar and playoff structure.
6. Shared-city instance capacity and region strategy.
7. Social features and moderation surface.
8. Apartment visit rules and furniture interaction depth.
9. Clothing and furniture catalog targets.
10. Job and allowance design.
11. Wager-market order, odds, payout, limit, and correction rules.
12. Minimum PC specification and performance targets.
13. Whether real-money Odds Bucks are considered for Version 1 or explicitly deferred again.
14. Whether player item trading belongs after Version 1 or in a later Version 1 update.

## Scope Director rules

Until the owner approves beta exit, the Scope Director must use [[Design/Beta Game Bible|Beta Game Bible]] for implementation planning and treat this Version 1 document only as a future boundary.

After beta exit approval, it must:

1. Read this entire document and the accepted Version 1 scope-freeze decision.
2. Preserve every inherited beta authority and evidence boundary.
3. Cite the exact Version 1 section advanced by a proposed phase.
4. Explain which release risk is reduced.
5. Ask the owner rather than implement an **OPEN** item.
6. Never schedule a **POST-V1 CANDIDATE** without a new owner decision.
7. Prefer hardening one proven path over adding breadth.
8. Never claim release readiness without measured multiplayer, persistence, security, economy, replay, and operational evidence.

## Current boundary

- Beta development remains active.
- Version 1 has not begun.
- This document records inheritance, release-quality requirements, open decisions, and future exclusions.
- Player item trading is remembered but not authorized.
