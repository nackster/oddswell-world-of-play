# Phase 1E.2 — Studio Ownership and Return Persistence

Date: 2026-07-20
Status: Complete on `agent/phase-0d`
Cost: `$0.00`

## Outcome

The starter Studio now has one durable local ownership record. The first valid entry grants that default Studio and saves the avatar's exact Sundale doorway position. Leaving the Studio and reopening the game restore that saved position while the private interior remains completely empty.

## Smallest implementation

One native Unreal `SaveGame` object stores schema version `1`, the owned-Studio flag, and one Sundale return vector. It uses a separate production slot and isolated QA slot. Records with the wrong type, unsupported schema, missing ownership, or a non-finite/out-of-range return coordinate are rejected as a whole.

The existing `E` interaction writes the record before entering. Entry stops if the record cannot be saved. Exit stops if valid ownership cannot be loaded. In standalone Sundale, the existing game mode uses the validated vector as the avatar spawn point. No database, account system, service, entitlement framework, furniture, inventory, catalog, economy, or new interior was added.

## Direct evidence

- Editor write/return run: ownership saved, Studio structure `6`, furniture `0`, decorations `0`, snap points `0`, exit restored with `0.0 cm` horizontal error.
- Separate cold editor process: ownership loaded, the same return point restored with `0.0 cm` error, and the isolated QA save was deleted.
- Packaged write/return run: ownership saved, the empty Studio entered and exited, and the exact return point restored with `0.0 cm` error.
- Separate cold packaged process: ownership and the same return point survived restart with `0.0 cm` error; QA cleanup was verified.
- The clean two-map Windows BuildCookRun completed in `111.07s`. The archive contains `57` files totaling `1,042,131,802` bytes.

## Validation

- Unreal editor and game targets compiled with UE `5.8`.
- Native `OddsWell.Character` automation passed `6/6`, including memory, disk, invalid-record, and cleanup checks for Studio persistence.
- The complete frozen simulation regression suite passed `65/65` in `132.3s`.
- Brain Admin self-check and Python compilation passed.
- Accepted logs contain zero fatal, ensure, or Studio-persistence failure markers.
- No OddsWell or Unreal process remained. Repository diff hygiene passed.

## Boundary and next gate

This is local standalone persistence. It does not add accounts, external hosting, multiplayer interior handoff, visits, larger interiors, furniture, decoration, snap points, inventory, a catalog, Odds Bucks, purchases, trading, final art, or deployment.

The next roadmap step is **Phase 1E.3 — represent Studio, 1BR, 2BR, 3BR, 4BR, and Penthouse as truthful progression data while only the Studio is available**.

## Phase 1E.3 follow-up

[[Development/Reports/Phase 1E3 Six-Tier Housing Progression Catalog]] now defines those six ordered tiers and keeps every larger interior explicitly locked and unbuilt. The Phase 1E.2 ownership and return evidence remains unchanged.
