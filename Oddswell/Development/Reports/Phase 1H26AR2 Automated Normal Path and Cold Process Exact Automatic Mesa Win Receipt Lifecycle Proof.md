# Phase 1H.26AR.2 - Automated Normal-Path and Cold-Process Exact Automatic Mesa Win Receipt Lifecycle Proof

**Date:** 2026-07-31
**Status:** COMPLETE FOR THE FIXED H26AQ AUTOMATED DEVELOPMENT PROOF
**Branch:** `agent/phase-0d`
**Cost:** `$0.00`

## Outcome

The committed H26AR.1 Development-only held-input driver completed the exact H26AQ receipt lifecycle in two entirely separate packaged Development processes:

1. Process A loaded the authoritative automatic Mesa-win profile, used native `W` / `A` / `D` movement and `E` interaction, opened the receipt, closed it, left the booth radius, returned, reopened the receipt, captured it, and exited cleanly.
2. Only after Process A had fully terminated, Process B cold-launched against the same unchanged user directory and repeated the same native-input lifecycle, captured the identical receipt values, and exited cleanly.

This is automated normal-path proof. It is not manual-player or usability proof.

## Exact player evidence

Both game-native `1280x800` captures are readable and unclipped. Each shows exactly:

- `BET SETTLED — WIN`;
- Mesa Vista Sol selected and winner;
- stake `40` Odds Bucks;
- final Harbor `79-113` Mesa;
- returned `94`;
- net `+54`;
- balance `154`; and
- one `E or ESC: CLOSE` instruction.

Process A produced one driver `PASS`, started `17,986 cm` from the booth, reached `342 cm` inside the `350 cm` radius, left to `651 cm`, and finished `17,644 cm` from its starting point. Process B independently produced one driver `PASS`, started `17,986 cm` away, reached `340 cm`, left to `651 cm`, and finished `17,644 cm` from its starting point. Each process emitted the exact H26AQ receipt marker at load, first open, and reopen.

The retained captures are:

- `Runtime/Captures/ProcessA-NormalPath-Receipt.png`: `649,356` bytes, SHA-256 `8fac16f1ee9612276c62ce04ee561f283b1e45cf0cf1b2147bc16258ce550699`;
- `Runtime/Captures/ProcessB-ColdProcess-Receipt.png`: `647,964` bytes, SHA-256 `2a5156c5a542cff45eda58bf32858a7d44881b19fdcf6d715a2f273f6f1f21ea`.

The pixels can differ because each process rendered a separate live frame; the authoritative receipt values and single close instruction are identical.

## Authority and input boundary

Both commands use only `SundaleGraybox`, `-CanonicalAutomaticReceiptHeldInputDriver`, window/render options, an isolated `-userdir`, and an absolute log. They include no QA receipt, QA slot, teleport, transform, or direct-action flag.

The accepted marker proves the existing path:

`PlayerController.InputKey` -> `PollKeyboardMovement` / `AddMovementInput` -> booth proximity -> `PollSportsbookInteraction`.

The driver outputs only `W`, `A`, `D`, and `E`. Its source block contains no direct transform, teleport, receipt open/close method, wager, settlement, payout, refund, RPC, persistence write, or direct `AddMovementInput` call. No production source changed in this phase.

## Exact persistence invariance

Before Process A, between Process A and Process B, and after Process B, the same authoritative file remained exactly:

- length: `10,658` bytes;
- SHA-256: `78c3e43ddc4c0e63e671187dc2b81a35e633ef6de2bddd5a6bf25871bbbfdc29`; and
- UTC mtime: `2026-07-31T04:21:47.1328700Z`.

Process A exited `0` in `78.064s`; Process B exited `0` in `77.882s`. Zero OddsWell or Unreal process remained after either boundary.

## Verification

- Focused H26AR.1 native automation: PASS `1/1` in `15.111s`.
- Full frozen native automation: PASS `43/43` in `18.232s`.
- Canonical Python `3.12.13` timing guard: PASS `1/1` in `17.929s`, PID `44932`, verified High priority.
- Full frozen Python regression: PASS `105/105` in `138.442s`, timing module first, PID `20184`, verified High priority.
- Brain Admin `--check`: PASS.
- Python compilation: PASS for `45` files.
- Package boundary: unchanged accepted H26AR.1 Development package, `50` files, `1,048,675,951` bytes, zero Python files.
- Source/direct-action audit, command audit, SaveGame invariance, two screenshot inspections, whitespace, and final process cleanup: PASS.

Two preliminary timing-controller invocations produced `1/1 OK` but did not expose an exit code to their PowerShell caller; they are not accepted evidence. One preliminary root discovery command ran zero tests and was also rejected. The accepted runs above used an explicit process runner and the complete ordered frozen module list; no test or threshold changed.

## Evidence

Local ignored evidence root:

`client/OddsWell/Saved/Evidence/Phase1H26AR2-20260731/Proof-20260731-084538`

- `Runtime/Logs/ProcessA-NormalPath.log`
- `Runtime/Logs/ProcessB-ColdProcess.log`
- `Runtime/Captures/ProcessA-NormalPath-Receipt.png`
- `Runtime/Captures/ProcessB-ColdProcess-Receipt.png`
- `Verification/H26AR2-FocusedNative.log`
- `Verification/H26AR2-FullNative.log`
- `Verification/Python-TimingGuard-Accepted.err.log`
- `Verification/Python-Full-Accepted.err.log`
- `Verification/BrainAdmin-Check.log`

## Scope boundary and next gate

H26AR.2 adds no player-visible feature, production behavior, persistence field, schema, dependency, authority, wager, payout, correction, generalized receipt history, online service, backend, deployment, retraining, simulator change, or brain change. It proves only the fixed automatic H26AQ receipt through the committed Development-only native-input driver across a normal packaged process and one later cold packaged process.

Stop for fresh Scope Director review. Manual-player usability, other receipts, variable stakes, multiple wagers, correction, later markets, and online authority remain separate and unproved.
