# Phase 1H.26AR.1 - Development-Only Held-Input Receipt Lifecycle Driver

**Date:** 2026-07-31
**Status:** COMPLETE FOR THE DEVELOPMENT-ONLY DRIVER
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

One explicit Windows Development-build command now proves the fixed H26AQ receipt through the existing player paths:

1. hold native `W` / `A` / `D` input to walk from the Sundale spawn to the physical ticket booth;
2. press and release native `E` to open the exact receipt;
3. release and press `E` again to close it;
4. hold `A` until outside the existing booth radius;
5. hold `W` / `A` / `D` to return; and
6. press and release `E` to reopen the same receipt before a clean exit.

The accepted packaged run started `17,986 cm` from the booth, reached `342 cm` inside its existing `350 cm` interaction radius, left to `652 cm`, returned, and exited with the receipt reopened. Final displacement from the original spawn was `17,645 cm`.

This is H26AR.1 driver evidence only. It does not claim the broader H26AR normal-player or cold-restart lifecycle.

## Minimal implementation

Ponytail full mode added one state machine in the existing placeholder character. It is compiled only under `UE_BUILD_DEVELOPMENT` and starts only for the exact explicit flag:

`-CanonicalAutomaticReceiptHeldInputDriver`

The driver injects `IE_Pressed`, held `IE_Repeat`, and `IE_Released` events through Unreal's native `APlayerController::InputKey(FInputKeyEventArgs::CreateSimulated(...))` path. Existing `IsInputKeyDown`, `PollKeyboardMovement`, `AddMovementInput`, proximity calculation, interaction arming, and `PollSportsbookInteraction` behavior do the work.

The state machine can output only `W`, `A`, `D`, and `E`. Booth direction and distance select the held movement keys. It cannot output a transform, teleport, receipt action, wager action, settlement action, or authoritative write.

## Start and failure gates

Before injecting any input, the driver requires all of the following:

- Windows Development code is present;
- the exact command-line flag is present;
- local standalone play;
- `SundaleGraybox`;
- the non-QA saved-profile lane;
- the existing H26AQ loader has returned the exact Mesa-win receipt; and
- the saved source contains the fixed H26AN automatic decision identity linked to the H26AJ finalization.

Wrong map, nonlocal or non-standalone play, missing or invalid receipt, QA-slot flags, changed runtime boundaries, a `110`-second total timeout, a `3`-second movement stall, an unsupported direction, or an unexpected menu state fails closed. Every completion, failure, and `EndPlay` path releases all injected keys. Test and Shipping builds omit the flag parse, state, methods, input-event include, and runtime call through the `UE_BUILD_DEVELOPMENT` compile gate.

A full Win64 Shipping build passed, and a binary-string audit found zero instances of the flag or H26AR.1 runtime marker. The installed UE 5.8 distribution refuses every `Test` target before project compilation (`Targets cannot be built in the Test configuration with this engine distribution`), so no Test-build pass is claimed. The same `UE_BUILD_DEVELOPMENT` gate excludes the driver when `UE_BUILD_TEST` is active.

## Forbidden-path audit

The driver block contains none of the following:

- `SetActorLocation`;
- `TeleportTo` or any direct transform/position write;
- `ToggleSportsbookOfferPreview` or `CloseTicketBoothMenu`;
- wager, settlement, payout, refund, or server RPC calls;
- `SaveGameToSlot` or another persistence writer;
- level travel; or
- direct `AddMovementInput`.

The state machine reaches the already-existing movement and booth methods only through native key state.

## Packaged proof

The final explicit `Bootstrap+SundaleGraybox` Windows Development package contains `50` files totaling `1,048,675,951` bytes and zero Python files.

The accepted runtime marker is:

`ODDSWELL_H26AR1_HELD_INPUT_DRIVER|result=PASS|reason=completed|build=Development|map=SundaleGraybox|standalone=true|local=true|receipt=H26AQ|input=PlayerController.InputKey|movement=PollKeyboardMovement_AddMovementInput|interaction=PollSportsbookInteraction|keys=W_A_D_E|start_distance_cm=17986|nearest_distance_cm=342|leave_distance_cm=652|travel_cm=17645|menu_open=true|source_write=false|transform_write=false|direct_receipt_action=false|full_H26AR_lifecycle=false`

The game-native `1280x800` reopened-receipt capture is readable and unclipped. It shows Mesa selected and winner, stake `40`, final Harbor `79-113` Mesa, returned `94`, net `+54`, balance `154`, and one close instruction. The PNG is `647,484` bytes with SHA-256 `5bd67947d8472cdc9ae2576c8ad988310a280d41f13a67a97936c3658453c1aa`.

The authoritative saved profile remained exactly:

- length: `10,658` bytes;
- SHA-256: `78c3e43ddc4c0e63e671187dc2b81a35e633ef6de2bddd5a6bf25871bbbfdc29`; and
- UTC mtime: `2026-07-31T04:21:47.1328700Z`.

## Corrective evidence

The first packaged attempt correctly stopped after its stall gate measured only `50 cm` of travel. One simulated digital press did not preserve raw held input across later PlayerInput ticks. The narrow correction added native `IE_Repeat` events for already-held keys while retaining one press edge, one release edge, and universal cleanup. No direct movement or fallback was added. The failed attempt is preliminary evidence and is not counted as acceptance.

One verbose Python full-suite attempt was also rejected after an output-pipe timeout at `300` seconds; no test failure was reported. The unchanged quiet rerun below is the accepted full-suite result.

## Verification

- Focused H26AR.1 native automation: PASS `1/1`.
- Final full native automation: PASS `43/43`.
- Canonical Python `3.12.13` timing guard at verified High priority: PASS `1/1` in `53.986s`.
- Canonical Python `3.12.13` full regression at verified High priority: PASS `105/105` in `130.214s`.
- Brain Admin `--check`: PASS.
- Python compilation: PASS.
- Final editor build: PASS.
- Final game compile inside BuildCookRun: PASS.
- Win64 Shipping build and zero-driver-string binary audit: PASS.
- Win64 Test build: unavailable in the installed UE distribution; rejected before project compilation, with exclusion covered by the Development-only compile gate.
- Fresh Windows Development BuildCookRun: PASS in `43.83s`.
- Package boundary, zero-Python, direct-action source audit, screenshot inspection, SaveGame byte/hash/mtime invariance, whitespace, and process cleanup: PASS.

## Scope boundary and next gate

H26AR.1 adds no player-visible production feature and no generalized navigation framework. It adds no new receipt authority, UI, persistence, schema, dependency, economy command, payout, correction, later market, online authority, backend, deployment, retraining, simulator behavior, or brain behavior.

Stop for Scope Director review. A separate H26AR proof gate may reuse this committed Development-only driver to collect broader normal-player and cold-restart lifecycle evidence. That proof must not be inferred from H26AR.1.
