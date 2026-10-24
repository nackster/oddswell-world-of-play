---
tags:
  - development
  - beta
  - unreal-engine
  - character
status: complete
date: 2026-07-19
---

# Phase 1B.2: Fast Local Character Selection Screen

## Outcome

OddsWell now packages and visibly runs a local character-selection screen for all eight approved placeholder presets. It starts on a valid deterministic default and records exactly one confirmation for the current session.

## Implementation

- `FOddsWellCharacterSelectionState` validates [[Development/Reports/Phase 1B1 Character Preset Catalog|the Phase 1B.1 catalog]] before exposing a selection, wraps navigation within its eight entries, and rejects a second confirmation.
- `AOddsWellCharacterSelectionHUD` draws a compact four-by-two native screen directly from that catalog. Every card uses the same neutral block silhouette, the catalog skin tone, and visible replaceable off-white top and bottom.
- Arrow keys and WASD navigate; Enter and Space confirm. Controller D-pad and bottom face button routes use the same selection state.
- `AOddsWellCharacterSelectionGameMode` is activated only by an explicit map URL for this proof. The empty Bootstrap default, the block/court benchmark, and recorded-replay mode remain unchanged.
- No UI framework, content asset, external service, paid dependency, account, backend, or persistence layer was added.

## Validation

- UE 5.8 `OddsWellEditor` Development build: **passed**, 4/4 actions in `5.13s`.
- UE 5.8 `OddsWell` Development game build: **passed**, 7/7 actions in `15.77s`.
- Native `OddsWell.Character` automation: **2/2 passed**, covering the catalog and selection state, including safe default, bounds, one-confirmation behavior, and controller-key routes.
- Windows BuildCookRun: **passed** with exit code `0` in `49.32s`; archive contains 55 files totaling `1,040,712,435` bytes.
- Packaged visual QA: all eight cards, selection highlight, shared placeholder layout, and replaceable off-white clothing labels were visible. The default confirmed `masculine_tone_1`; a second run navigated five steps and confirmed `feminine_tone_2`.
- Each proof log contains exactly one expected session-local confirmation, zero fatal/assert/unhandled matches, and a clean exit.
- Frozen Python regression suite: **65/65 passed** in `149.527s`.
- Brain Admin self-check and Python compilation: **passed**.
- Obsidian links, Beta Delivery Roadmap canvas JSON, frozen map/replay hashes, Git LFS and ignored-output rules, Android network/token boundary, whitespace, and scoped-diff checks: **passed**.
- Controller behavior is covered by native automation; no physical controller hardware was tested.
- Cost: **$0.00**.

The first packaged launch surfaced a Windows Firewall permission dialog. Automation did not interact with it or change security/network settings. The owner manually chose **Cancel**; a fresh bounded safe-default rerun then showed the full screen without any Firewall/security prompt or other modal, confirmed `masculine_tone_1` exactly once, exited cleanly, and left no OddsWell, Unreal Editor, Trace, or shader-worker process.

## Truth boundary

This phase does not create a controllable pawn, third-person camera, movement, mesh, skeletal rig, animation, final character art, character name, personality, gameplay attribute, save file, world transition, account, backend, multiplayer state, economy, wagering, deployment, model job, or retraining claim.

The next smallest gate is **Phase 1B.3: one controllable placeholder avatar with the approved third-person camera and keyboard/mouse/controller walk, run, and jump direction**.
