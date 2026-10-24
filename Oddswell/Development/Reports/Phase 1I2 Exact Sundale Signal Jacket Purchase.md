# Phase 1I.2 - Exact Sundale Signal Jacket Purchase

**Date:** 2026-07-31
**Status:** COMPLETE FOR THE LOCAL AUTHORITATIVE PROFILE
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The owner-approved `sundale_signal_jacket` can now be purchased at the physical Sundale clothing-store waypoint for exactly `60` Odds Bucks. The player presses E once to review the fixed offer and E again to confirm it.

The server revalidates the Sundale map and `350 cm` store radius. It accepts no client item ID, price, balance, or ledger command. One immutable ledger entry records command `store:sundale:signal_jacket:purchase:v1`, delta `-60`, reason `clothing_purchase`, and the resulting balance. That same command is the smallest durable local ownership proof, so no second inventory schema was added.

## Safety and boundaries

- The candidate ledger is persisted before the in-memory authority changes.
- An underfunded player receives no item and no debit.
- Exact retry and cold restart return already-owned without another entry or debit.
- Leaving the store cancels the confirmation state.
- Purchase does not auto-equip or grant a free demonstration item.
- No generalized inventory/catalog service, chair purchase, furniture placement, refund, selling, storage, rotation, marketplace, trading, real-money path, design brain, athlete brain, odds brain, or simulator behavior was added.
- The explicit purchase QA driver is compiled only in Development. It teleports only to the already-tested clothing waypoint as setup, then sends normal simulated E press/release input through `PlayerController.InputKey`; production proximity, confirmation, RPC, validation, save, and feedback paths remain unchanged.

## Verification

| Gate | Result |
| --- | --- |
| Unreal editor build | PASS |
| Focused purchase/idempotency/cold-load automation | PASS `1/1` |
| Final native OddsWell automation | PASS `44/44` |
| Frozen Python brain/simulator/execution suite | PASS `105/105` in `137.246s` |
| Brain Admin self-check | PASS |
| Self-operated fresh editor-game process | PASS: E/E purchase, entries `2`, balance `40`, owned `true` |
| Self-operated cold editor-game process | PASS: E/E already-owned, entries `2`, balance `40`, no second debit, cleanup `true` |
| Development staging boundary | PASS: fresh production implementation staged with zero Python; package containers mounted and Sundale initialized |

The fresh package was staged before the Development-only QA driver was added, so the two-process interaction proof is accurately labeled editor-game evidence rather than packaged-driver evidence. The production purchase implementation exercised by the driver is the same code staged in the package.

## Next gate

Phase 1I.3 may let the owner explicitly equip the already-owned Signal Jacket in the single `outfit` slot and prove its appearance to one other local city client. It must not purchase again, auto-equip, add another garment, or begin the Modular Chair path.
