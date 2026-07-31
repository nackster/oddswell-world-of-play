# Phase 1I.3 - Owned Signal Jacket Equip and Shared City Visibility

**Date:** 2026-07-31
**Status:** COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE AND ONE OTHER LOCAL SUNDALE CLIENT
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The local owner can explicitly equip the already-owned `sundale_signal_jacket` at the physical Sundale clothing-store waypoint. Inside the existing `350 cm` interaction radius, one E press replaces the starter top with a slate-and-teal graybox jacket in the single `outfit` slot. Another local Sundale client receives the replicated equip state and renders that appearance on the other player.

The existing immutable `store:sundale:signal_jacket:purchase:v1` debit remains the ownership proof. Equip creates no ledger entry, costs `0` Odds Bucks, and never happens automatically after purchase or restart.

## Authority and boundaries

- The server revalidates Sundale, store proximity, the local authoritative profile, and exact ownership.
- The client supplies no item ID, price, ledger command, balance, material, color, or arbitrary appearance payload.
- The graybox adds only one slate top material and one visible teal band. The starter bottom remains unchanged.
- The one local authoritative profile can equip; the second client is a replicated observer because production accounts and online inventory authority do not exist yet.
- Equip is session state for this local slice. A cold owner explicitly equips again; no false cold-equip persistence is claimed.
- No new garment, chair, furniture placement, catalog service, refund, selling, storage, rotation, trading, marketplace, real-money path, brain behavior, simulator behavior, or deployment was added.

## Verification

| Gate | Result |
| --- | --- |
| Unreal editor/game build | PASS |
| Focused owned-equip authority/economy automation | PASS `1/1` |
| Full native OddsWell automation | PASS `45/45` |
| Frozen Python brain/simulator/execution suite | PASS `105/105` in `166.268s` |
| Brain Admin self-check | PASS |
| Fresh Windows Development BuildCookRun | PASS in `56.03s`; `50` files / `1,048,832,447` bytes / zero Python files |
| Packaged owner process | PASS: normal E path, physical store, explicit equip, ledger `2`, balance `40`, additional debit `false`, auto-equip `false` |
| Packaged observer process | PASS: second player visible, replicated equip received, slate-and-teal graybox rendered |
| Process and QA cleanup | PASS: both processes exited `0`; isolated QA slot absent |

The packaged `1280x720` screenshot was visually inspected. It shows the observer in off-white starter clothing and the other local player beside them wearing the distinct slate jacket and teal band.

## Next gate

Phase 1I.4 may implement only the approved `100`-Odds-Bucks `sundale_modular_chair`, an idempotent purchase at the physical furniture store, and its visible result at the single predefined `studio_primary` Studio snap point. It must not add free placement, rotation, storage, selling, refunds, another item, apartment upgrades, trading, or real-money behavior.
