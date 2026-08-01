# Phase 1I.5 - Exact One-Bedroom Upgrade Purchase and In-Place Interior

**Date:** 2026-08-01
**Status:** COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND OWNED STUDIO
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The local player can buy the owner-approved One-bedroom tier only at the physical apartment-management kiosk beside the Sundale apartment entrance. Inside the existing `350 cm` interaction radius, one E press reviews the exact `500`-Odds-Bucks price and a second E press confirms it. The server revalidates the map, distance, local profile, Studio prerequisite, fixed tier, price, and immutable command.

The saved `housing:sundale:one_bedroom:upgrade:v1` `-500` ledger entry is durable ownership evidence. On entry, the existing Studio gains a three-surface partition with an open doorway, creating separate graybox living and bedroom areas without a second interior or save schema. An already-owned Sundale Modular Chair remains at `studio_primary` on the living-room side after purchase and cold restart.

## Authority and boundaries

- Underfunded, missing-Studio, outside-kiosk, non-authoritative, failed-save, conflicting, and exact-retry paths do not create a second debit or tier.
- The candidate ledger is saved before the in-memory balance changes.
- Ownership derives from the exact immutable ledger record rather than a client-supplied tier or price.
- Ponytail reused the existing Odds Bucks ledger, Studio ownership, two-step physical-store interaction, Studio transition, fixed chair snap, and local SaveGame. No generalized housing service, inventory database, new schema, or dependency was added.
- The partition and kiosk are graybox proof. Final modern apartment art remains later content work.
- Later apartment tiers, additional snap points, refunds, resale, rent, mortgage, storage, trading, marketplace, real money, online authority, simulator behavior, and brain behavior remain absent.

## Self-operated verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused One-bedroom authority/interior automation | PASS `1/1` |
| Focused One-bedroom ledger automation | PASS `1/1` |
| Full native OddsWell automation | PASS `49/49` |
| Frozen Python brain/simulator/execution suite | PASS `105/105` (`84` + `21`) |
| Brain Admin self-check | PASS |
| Fresh Windows Development BuildCookRun | PASS in `70.83s` |
| Final package audit | PASS: `50` files / `1,049,119,983` bytes / zero Python files |
| Packaged fresh process | PASS: physical kiosk, two E presses, Studio prerequisite, chair `-100`, One-bedroom `-500`, balance `0`, three partition surfaces, open doorway, chair preserved |
| Packaged cold process | PASS: exact ownership, balance, partition, doorway, and chair restored; isolated QA saves cleaned |
| Screenshot inspection | PASS: fresh and cold `1280x720` captures visibly show the partition, doorway, living area, and retained chair |
| Process cleanup | PASS: no OddsWell, Unreal, AutomationTool, or RunUAT process remained |

## Next gate

Phase 1I's smallest approved local lifestyle loop is complete: buy/equip/show one clothing item, buy/display one furniture item, and buy/restore one apartment upgrade. The earliest incomplete roadmap dependency is Phase 1J.1: present existing authoritative athlete talent, specialty, form, fatigue, injury, availability, and bounded Life Brain evidence without changing the frozen brains or exposing hidden resolver state.
