# Phase 1E.1 — Private Empty Studio Enter and Exit

Date: 2026-07-20
Status: Complete on `agent/phase-0d`
Cost: `$0.00`

## Outcome

One packaged placeholder avatar entered a private, completely empty Studio from Sundale, walked `200.0 cm` inside it, exited, and returned to Sundale. The accepted Studio reported exactly six structural surfaces, zero furniture, zero decorations, and zero active furniture snap points.

## Smallest implementation

An explicit Studio game-mode URL reuses the already-existing empty Bootstrap map as a private interior container. At runtime it creates only a floor, ceiling, four walls, and one necessary point light from Unreal built-ins. The room adds no binary map, apartment framework, furniture actor, decoration, inventory, ownership claim, ledger, store, or service.

At the Sundale Studio threshold, a standalone player receives a `Press E` prompt. `E` enters the private Studio; after key release, `E` returns to Sundale. The key-release arm prevents one held press from immediately bouncing between maps.

The opt-in acceptance path uses the same level transitions. It passes only after the Studio structure count is six, furniture count is zero, the avatar walks at least `200 cm` on the interior floor, and the process returns to Sundale.

## Evidence

- Editor acceptance: entered, reported the exact empty contents, walked `200.1 cm`, exited, returned, and passed.
- Windows package acceptance: entered, reported the exact empty contents, walked `200.0 cm`, exited, returned, and passed in `5.50s` with exit code `0`.
- The package log contains zero fatal, ensure, Studio-fail, or Studio-ready-fail markers.
- No OddsWell process remained after the run.

## Validation

- UE `5.8` editor and game targets compiled successfully after replacing one rejected point-light convenience accessor with the actual UE 5.8 component property.
- Native `OddsWell.Character` automation passed `5/5`.
- Windows BuildCookRun for Sundale and Bootstrap succeeded in `64.89s`; the archive contains `52` files totaling `1,041,934,259` bytes.
- The complete frozen simulation regression suite passed `65/65` in `133.495s`.
- OddsWell Admin Console self-check and Python compilation passed.

## Boundary and next gate

This is a standalone local private-interior proof. It does not yet persist Studio ownership or a return location, preserve a multiplayer session during travel, create larger apartment interiors, activate snap points, add furniture, grant inventory, buy an item, use Odds Bucks, allow visits, or prove external hosting. Those claims remain inactive.

The next roadmap step is **Phase 1E.2 — Studio ownership and return persistence**.
