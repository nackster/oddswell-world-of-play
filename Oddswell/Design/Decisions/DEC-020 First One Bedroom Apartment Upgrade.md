---
tags:
  - decision
  - beta
  - housing
  - economy
  - sundale
status: accepted
date: 2026-08-01
---

# DEC-020 First One-Bedroom Apartment Upgrade

## Decision

The first purchasable housing tier is the **One-bedroom** apartment. It costs exactly `500` Odds Bucks, requires the player to own the starting Studio, and upgrades that Studio interior in place.

The purchase is available only at the apartment-management kiosk beside the Sundale apartment entrance. One E press reviews the offer and a second E press confirms it. The server owns the tier ID, price, prerequisite check, immutable ledger command, and final distance/map validation.

The existing `studio_primary` living-room snap point remains valid after the upgrade. If the player already owns the Sundale Modular Chair, it remains visible there. The One-bedroom adds only a graybox partition and open doorway for the beta proof; it is not final apartment art.

## Frozen values

| Field | Approved value |
| --- | --- |
| Tier ID | `one_bedroom` |
| Display name | One-bedroom |
| Price | `500` Odds Bucks |
| Prerequisite | Own Studio |
| Purchase location | Apartment-management kiosk beside the Sundale apartment entrance |
| Confirmation | Two E presses: review, then confirm |
| Interior model | Upgrade the existing Studio in place |
| Existing chair | Preserve at `studio_primary` in the living area |
| Immutable command | `housing:sundale:one_bedroom:upgrade:v1` |

## Boundaries

- Two-bedroom, Three-bedroom, Four-bedroom, and Penthouse prices, requirements, layouts, and purchase paths remain unapproved and unavailable.
- The graybox partition is implementation evidence, not final modern apartment design.
- No generalized property service, mortgage, rent, refund, resale, storage, trading, marketplace, real-money path, online account authority, simulator change, or brain change is authorized by this decision.

## Evidence

The implemented local-beta path is recorded in [[Development/Reports/Phase 1I5 Exact One Bedroom Upgrade Purchase and In Place Interior]].
