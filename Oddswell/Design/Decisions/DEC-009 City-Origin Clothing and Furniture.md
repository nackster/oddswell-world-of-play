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

## Approved beta starter catalog

The owner approved the smallest Phase 1I catalog on July 31, 2026:

| Item ID | Player-facing name | Type | Price | Beta behavior |
| --- | --- | --- | ---: | --- |
| `sundale_signal_jacket` | Sundale Signal Jacket | Clothing | `60` Odds Bucks | One modern slate-and-teal Sundale outfit upgrade using the single `outfit` slot. |
| `sundale_modular_chair` | Sundale Modular Chair | Furniture | `100` Odds Bucks | One modern gray-and-teal chair using the single predefined `studio_primary` snap point. |

The shared worn off-white starter outfit remains onboarding equipment and is not a store item. The Studio still starts completely empty. Beta provides no refunds, selling, storage, rotation, free placement, gifting, marketplace, or trading.

## Beta boundary

- Beta needs only these two Sundale-origin catalog records.
- Do not build a generalized multi-city catalog service, travel system, cross-city store, marketplace, item transfer, gifting, auction, or trading system for this rule.
- Phase 1I.2 implements the exact Signal Jacket purchase. Its immutable `store:sundale:signal_jacket:purchase:v1` ledger command encodes the Sundale item identity and is the local durable ownership record.
- Phase 1I.3 adds one explicit owned-item equip at the physical clothing store and replicates the slate-and-teal graybox outfit to another local Sundale client. Equip adds no debit, does not auto-equip on purchase or restart, and does not grant the chair or activate furniture placement.
- City origin never changes athlete decisions, game outcomes, Odds Bucks settlement, or player ability.

## Future clothing-design brain

A future clothing-design brain may propose new visual concepts after the first item is proven. It is not implemented, trained, or authorized to publish merchandise, set prices, modify catalogs, grant inventory, or change player state. Every proposed item still requires owner art approval and a separately versioned catalog decision before implementation.

## Future boundary

When additional cities are separately approved after beta, each receives its own clothing and furniture catalog. Player-to-player exchange remains outside beta and is not authorized by this decision.
