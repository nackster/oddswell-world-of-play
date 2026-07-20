---
tags:
  - decision
  - beta
  - clothing
  - furniture
  - city
status: approved
date: 2026-07-20
---

# DEC-009: City-Origin Clothing and Furniture

## Decision

Every purchasable clothing and furniture item belongs to the city where it is originally sold. A city's stores offer their own city-specific catalog rather than a universal catalog shared by every city.

For beta, Sundale is the only city, so every beta store item is Sundale-origin merchandise. The worn off-white starter outfit is onboarding equipment rather than purchased city merchandise and may remain a shared starter exception.

## Ownership rule

- `origin_city_id` is durable item identity and must survive persistence, reconciliation, and any later migration.
- A city-origin item is sold through its origin city's approved store catalog by default.
- Once legitimately owned, an item remains owned. City origin describes where it is sold, not a rule that destroys, disables, or unequips it outside that city.
- Future players should be able to show clothing or furniture obtained in another city, making city origin visible progression and identity.

## Beta boundary

- Beta needs only the Sundale origin value and tiny approved Sundale clothing/furniture catalogs.
- Do not build a generalized multi-city catalog service, travel system, cross-city store, marketplace, item transfer, gifting, auction, or trading system for this rule.
- Exact item counts, designs, prices, rarity, equipment slots, placement rules, refunds, and catalog implementation remain later owner gates.
- City origin never changes athlete decisions, game outcomes, Odds Bucks settlement, or player ability.

## Future boundary

When additional cities are separately approved after beta, each receives its own clothing and furniture catalog. Player-to-player exchange remains outside beta and is not authorized by this decision.
