---
tags:
  - development
  - beta
  - unreal-engine
  - character
  - persistence
status: complete
date: 2026-07-20
---

# Phase 1B.5: Local Character Appearance Persistence and First-Playable Handoff

## Outcome

A chosen placeholder now saves locally, enters the existing packaged BlockCourtBenchmark, and recovers the same catalog appearance after a real process close and cold restart. The recovered appearance includes the preset's catalog skin tone plus the exact replaceable off-white starter top and bottom. Phase 1B's choose, enter, move, close, and recover path is now executable without a backend.

## Minimal native implementation

- One native Unreal `USaveGame` class stores only schema version `1`, `preset_id`, `top_item_id`, and `bottom_item_id`. It uses one fixed production-local slot and one separate bounded QA slot at user index `0`.
- The Phase 1B.1 catalog remains the authority for preset identity, skin tone, and the exact starter equipment IDs. The equipment resolver is shared by saving, loading, and the existing replaceable-outfit state; no catalog was duplicated.
- A valid Phase 1B.2 confirmation validates the complete appearance, checks `SaveGameToSlot`, marks the selection confirmed only after the save succeeds, and travels directly into the existing BlockCourtBenchmark locomotion game mode. A failed save remains visibly and locally unconfirmed for handoff.
- Loading is all-or-nothing. Missing, unreadable, wrong-object, unsupported-version, unknown-preset, unknown-item, wrong-slot, duplicate, or incomplete data selects the first validated catalog preset and its complete outfit without deleting or rewriting the rejected record.
- The Phase 1B.3/1B.4 pawn applies the loaded catalog skin tone to the separate neutral body and head, then equips the stored exact top and bottom. Presentation remains stored cosmetic identity only; it changes no placeholder geometry or gameplay value.
- QA uses the dedicated local slot, verifies its deletion, and leaves no QA save behind. There is no persistence framework, repository abstraction, JSON, database, registry, cloud, account, backend, network, multiplayer, profile UI, migration machinery, cryptography, compression, or new dependency.

## Corrected UE 5.8 input defect

The first packaged handoff exposed a handled UE 5.8 ensure because the Phase 1B.3 pawn had bound digital W/A/S/D keys through `BindAxisKey`, which requires one-dimensional axis keys. That run was rejected as evidence.

The root cause was fixed once in the shared locomotion input setup: digital keyboard movement is polled through native `IsInputKeyDown`, while only MouseX/MouseY and controller stick axes remain on `BindAxisKey`. Native automation now asserts that every remaining axis binding is `Axis1D` and that W/A/S/D are not. Corrected editor, test, game, package, and runtime evidence were rebuilt afterward.

## Build and automated validation

- Corrected UE 5.8 `OddsWellEditor` Development build: **passed**, 5 actions; UnrealBuildTool completed in `8.43s`.
- Native `OddsWell.Character` automation: **5/5 passed** for appearance persistence, locomotion defaults, preset catalog, selection state, and starter outfit. There were zero failure, error, fatal, assert, unhandled, or ensure matches, and the QA save was absent afterward.
- Corrected UE 5.8 `OddsWell` Development game build: **passed**, 4 actions; UnrealBuildTool completed in `13.44s`.
- Corrected clean Windows Development BuildCookRun: **passed** in `109.45s`; the archive contains 58 files totaling `1,042,154,326` bytes, and its pak timestamp is later than the final source timestamp.
- Frozen Python regressions: **65/65 passed** in `132.457s`. Brain Admin self-check and Python compilation: **passed**.

## Packaged two-process proof

Before the accepted sequence, the corrected build loaded the QA record left by the rejected ensure run, deleted it through the native QA cleanup path, verified absence, and produced zero ensure or error matches.

### Process A: choose, save, and enter

- Began with no QA save.
- Wrote exactly one PASS record with `schema=1`, preset `feminine_tone_2`, top `starter_offwhite_top`, bottom `starter_offwhite_bottom`, and `confirmed_once=true`.
- Entered the existing BlockCourtBenchmark and loaded the same record with `source=loaded`, skin `D2A078FF`, feminine cosmetic presentation, and the exact two starter IDs.
- Computer Use showed one noncanonical avatar with the selected medium/dark catalog skin on its separate body/head plus distinct off-white upper and lower primitive equipment. No security overlay was present.
- Outfit and locomotion QA passed; the process exited cleanly with no ensure, error, assert, fatal, or unhandled match. The QA save remained for the cold-process proof.

### Process B: cold load and cleanup

- Started only after Process A fully closed. It produced zero selection-confirmation and zero save-write records.
- Loaded the exact same preset, skin, top, and bottom with `source=loaded`.
- Outfit and locomotion QA passed. Native cleanup logged PASS with `exists=false`, and the process exited cleanly with no ensure, error, assert, fatal, or unhandled match.
- The dedicated QA save was absent afterward. No related process remained.
- Bounded network samples returned no TCP or UDP endpoint rows.

The fresh executable initially displayed Windows Firewall. Automation did not interact or change a security setting; the owner clicked **Cancel** before the accepted corrected sequence continued.

## Preserved evidence and boundary

- `Bootstrap.umap` remains SHA-256 `44fc5e531591672e10e3740a780eafb34326c2eadc7d85a37cfa352541932c16`.
- `BlockCourtBenchmark.umap` remains SHA-256 `f970a2f4609f2d6ec24475ae48c98e12db53bde2cd95a238f2015c3ff0840018`.
- The tracked replay fixture remains SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`; its authoritative seal, 421 frames, and no-resimulation path remain unchanged.
- No position, world, camera, movement calibration, economy, currency, inventory ownership, pricing, store, wager, account, backend, multiplayer, replication, new clothing, final art, skeletal mesh, rig, animation, city canon, Phase 0, replay, model, training, retraining, paid service, or deployment behavior was added.
- Cost: **$0.00**.

The next gate is a **Phase 1B exit review** against the roadmap's complete choose → enter → move → close/reopen → recover evidence. Phase 1C implementation must then stop for owner approval of the first-city name, theme, geography, visual language, and minimal art-direction sheet.
