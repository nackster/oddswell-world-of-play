# Phase 1H.26AH.1 — Settled-Receipt Ticket-Booth Direction Cue

## Outcome

The exact validated H26P settled-loss receipt now gives the player one small wayfinding cue in Sundale city play:

`SETTLED BET READY — TICKET BOOTH: AHEAD / LEFT / RIGHT / BEHIND — ### m`

The packaged `1280x720` proof from the exact H26AG save showed `RIGHT — 180 m` in a top-center navy panel with a gold rule. The cue is readable without covering the character or central street view.

## Small implementation

One pure helper reuses the fixed `SportsbookInteractionLocation`, the existing `SportsbookInteractionRadius`, the player's current 2D position, and control-facing yaw. It chooses the dominant forward/right axis, rounds the current 2D distance from centimeters to meters, and returns one display string. The existing `AOddsWellSportsbookHUD::DrawHUD` path draws it only when neither the ticket-booth menu nor the existing proximity prompt is active.

No new service, component, actor, saved field, timer, objective, navigation graph, minimap, dependency, or generalized direction framework was added.

## Authority and visibility gates

The existing H26P loader remains the sole receipt authority. The HUD only receives a non-null settled-loss receipt after that loader validates the complete authoritative chain, so missing, partial, mixed, or tampered evidence cannot produce the cue.

The helper independently requires all of the following:

- map name contains `SundaleGraybox`;
- a valid H26P receipt is present;
- player is outside the fixed `350 cm` booth interaction radius;
- ticket-booth menu/receipt is closed; and
- player is not in the Studio or stadium.

At the booth radius, the existing `Press E to open betting odds` prompt takes over. The cue never writes a receipt, ledger, reconciliation, SaveGame, or simulation value.

## Verification

- Unreal Engine 5.8 editor build: PASS in `16.16s`.
- Unreal Engine 5.8 game build: PASS in `22.71s`.
- Focused H26AH.1 native automation: `1/1` PASS, covering exact spawn text, all four relative directions, meter distance, invalid receipt, wrong map, menu-open, Studio, stadium, and booth-radius handoff.
- Retained H26P native automation: `1/1` PASS.
- Full native OddsWell automation: `38/38` PASS.
- Canonical Python 3.12 regression: `105/105` PASS in `134.024s`.
- Separate supervisor regression: `28/28` PASS in `2.513s`.
- Brain Admin supported `--check`: PASS.
- Python compilation: PASS.
- Deterministic public league export: `30,288` bytes, SHA-256 `e08e4d44ef99c45689621351e1c983240ab476039ed17bba8c1ecec0f22923ff`.
- Deterministic archived replay export: `421` frames, `256,442` bytes, SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- Explicit `Bootstrap+SundaleGraybox` Windows BuildCookRun: PASS in `53.76s`.
- Final package: `50` files, `1,048,234,622` bytes, zero Python.
- Packaged direct-Sundale startup: exact H26AG `Duplicate`, existing H26P receipt `READY`, final score `79-113`, ledger `2`, balance `60`.
- Packaged offscreen visual proof: `1280x720`, exact `RIGHT — 180 m` cue visible and unclipped.
- Cost: `$0.00`.

The first Windows capture attempt was rejected because active owner input caused the capture helper to return another window. It is not accepted evidence. Unreal's own packaged offscreen `HighResShot` produced the accepted game-only visual without taking control of the owner's active application.

## Scope boundary

H26AH.1 is a corrective local wayfinding cue for one already valid settled-loss receipt. It adds no general navigation, minimap, quest tracking, marker persistence, QA teleport, receipt history, new wager, correction, later market, online authority, backend, deployment, simulation change, or brain change. The next implementation requires a fresh Scope Director decision.
