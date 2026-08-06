# Phase 1I.4 - Exact Sundale Modular Chair Purchase and Studio Display

**Date:** 2026-08-01
**Status:** COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND OWNED STUDIO
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The local player can buy the approved `sundale_modular_chair` only at the physical Sundale furniture-store waypoint. Inside the existing `350 cm` interaction radius, one E press reviews the exact `100`-Odds-Bucks price and a second E press confirms it. The server owns the item ID, price, immutable command, reason, and final validation.

The immutable `store:sundale:modular_chair:purchase:v1` `-100` ledger entry is the durable ownership record. An owned Studio derives one three-part gray-and-teal placeholder from that record and displays it at the single `studio_primary` snap point after normal entry and after a cold process restart.

## Authority and boundaries

- Underfunded, outside-store, non-authoritative, failed-save, conflicting, and exact-retry paths do not create a second debit or item.
- The candidate ledger is saved before the in-memory balance changes.
- The Studio shows no chair without both Studio ownership and the exact chair purchase record.
- Ponytail reused the existing job funding, Odds Bucks ledger, two-step store interaction, Studio transition, and Studio ownership paths. No inventory database, generalized catalog service, placement editor, or new dependency was added.
- The chair is one temporary three-cube graybox item at one fixed point. There is no free placement, rotation, storage, selling, refund, second furniture item, apartment upgrade, trading, real-money path, simulator change, or brain change.

## Self-operated verification

| Gate | Result |
| --- | --- |
| Unreal editor/game build | PASS |
| Focused exact purchase/economy automation | PASS `1/1` |
| Focused furniture authority/display automation | PASS `1/1` |
| Full native OddsWell automation | PASS `47/47` |
| Frozen Python brain/simulator/execution suite | PASS `105/105` in `137.361s` |
| Brain Admin self-check | PASS |
| Editor fresh process | PASS: normal E review/confirm, physical store, ledger `2`, balance `0`, ownership true, normal Studio entry, one item / three parts |
| Editor cold process | PASS: ownership and `studio_primary` display restored; exact QA saves cleaned |
| Final Windows Development BuildCookRun | PASS in `45.47s`; `50` files / `1,048,965,711` bytes / zero Python files |
| Packaged fresh process | PASS: exact purchase and Studio display through the same interaction path |
| Packaged cold process | PASS: cold restore, one item / three parts, cleanup true |
| Process cleanup | PASS: no OddsWell, Unreal, or test process remained |

The editor and final packaged `1280x720` fresh/cold screenshots were visually inspected. They clearly show a recognizable gray pedestal chair with a teal back inside the Studio; the fresh screen also reports the exact purchase and `0`-Odds-Bucks balance, and the final cold screen truthfully says `Press E to leave your Studio` rather than calling the furnished room empty.

## Next gate

Phase 1I.5 is an owner gate. Before any apartment-upgrade purchase path, the owner must approve the exact first purchasable tier, its Odds Bucks price and prerequisites, and whether it uses a separate interior or an upgrade of the Studio. Those values and layouts must not be invented.
