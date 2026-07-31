# Phase 1I.1 - Exact Sundale Starter Catalog Freeze

**Date:** 2026-07-31
**Status:** COMPLETE AS OWNER-APPROVED DESIGN AUTHORITY ONLY
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The owner approved the smallest possible Phase 1I beta catalog:

| Item ID | Name | Price | Rule |
| --- | --- | ---: | --- |
| `sundale_signal_jacket` | Sundale Signal Jacket | `60` Odds Bucks | Modern slate-and-teal clothing upgrade in the single `outfit` slot. |
| `sundale_modular_chair` | Sundale Modular Chair | `100` Odds Bucks | Modern gray-and-teal furniture at the single `studio_primary` snap point. |

The prices preserve a visible first-loop choice: the accepted `100`-Odds-Bucks job shift can fund either item before wagering; the fixed `40` wager leaves `60` after a loss and `154` after the proven Mesa win.

## Boundaries

- The worn off-white starter outfit remains onboarding equipment, not merchandise.
- The starting Studio remains completely empty.
- No item record, purchase, debit, ownership, inventory, equip, replication, furniture placement, refund, selling, storage, rotation, marketplace, trading, or real-money path was implemented.
- A future clothing-design brain may propose concepts only. It is not implemented or trained and cannot publish merchandise, set prices, modify catalogs, grant inventory, or change player state. Every future item remains owner-approved.

## Verification

- DEC-009, Beta Game Bible, Beta Delivery Roadmap, Current Plan, this report, and the two affected clean canvases agree on item identity, price, origin, slot/snap point, absent features, and the future brain's proposal-only boundary.
- Markdown links resolve.
- Both canvas JSON files parse; IDs, edge endpoints, and file references remain valid; edited cards remain contained and non-overlapping.
- Whitespace and repository hygiene pass.
- Playable/manual verification is not applicable because this phase changes design authority only and adds no executable behavior. Codex will perform the playable purchase verification when Phase 1I.2 implements it.

## Next gate

Phase 1I.2 may add one idempotent server-authoritative Odds Bucks purchase command for `sundale_signal_jacket` at exactly `60`. It must not auto-equip the jacket, grant free inventory, or begin the chair purchase/placement path.
