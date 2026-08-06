---
tags:
  - development
  - beta
  - unreal-engine
  - character
  - exit-review
status: complete
date: 2026-07-20
---

# Phase 1B Exit Review: Character Onboarding Evidence Closure

## Decision

**PHASE 1B COMPLETE.** The committed Phase 1B.1–1B.5 evidence proves the roadmap exit path: a fresh player can choose one of eight gameplay-identical placeholder presets, enter the packaged placeholder world, move with the approved third-person controls, close the process, reopen it, and recover the exact same appearance. No demographic field changes gameplay.

## Exit-clause evidence

| Exit clause | Committed evidence | Result |
| --- | --- | --- |
| Eight gameplay-identical presets | Commit `8fe374e` and [[Development/Reports/Phase 1B1 Character Preset Catalog]] lock eight unique IDs, two cosmetic presentations, the same four skin tones for each presentation, identical starter equipment, and no gameplay modifiers. | PASS |
| Fast selection with a safe default | Commit `c2cc693` and [[Development/Reports/Phase 1B2 Fast Local Character Selection Screen]] prove all eight catalog entries, deterministic default `masculine_tone_1`, bounded keyboard/controller navigation, and one confirmation. | PASS |
| Cosmetic identity only | The Phase 1B.1 catalog contains only ID, presentation, skin tone, and equipment IDs. [[Design/Decisions/DEC-007 Phase 1B Character Defaults]] prohibits demographic effects on ability, wealth, intelligence, behavior, or athlete outcomes. | PASS |
| Direct handoff into the game | Commit `bada971` and [[Development/Reports/Phase 1B5 Local Character Appearance Persistence and First-Playable Handoff]] save a valid complete appearance before confirmation and enter the existing BlockCourtBenchmark locomotion mode. | PASS |
| Approved third-person movement | Commit `39cb8cb` and [[Development/Reports/Phase 1B3 Controllable Placeholder Avatar and Approved Locomotion]] prove native walk, held run, look, jump, landing, camera collision, and keyboard/mouse/controller routes. | PASS |
| Separate replaceable starter clothing | Commit `43bc592` and [[Development/Reports/Phase 1B4 Replaceable Starter Outfit]] prove distinct top and bottom slots and components, independent removal/restoration, the exact off-white starter IDs, and unchanged locomotion. | PASS |
| Minimal versioned local record | Commit `bada971` stores only schema version `1`, preset ID, top ID, and bottom ID in one native `USaveGame` record. | PASS |
| All-or-nothing validation and fallback | Phase 1B.5 native automation covers missing/unreadable data, wrong object, unsupported version, unknown preset/item, swapped slots, duplicate items, and incomplete outfits. Every rejected record falls back to the first validated complete preset without deletion or rewrite. | PASS |
| Exact non-default cold recovery | Phase 1B.5 Process A saved `feminine_tone_2`, skin `D2A078FF`, `starter_offwhite_top`, and `starter_offwhite_bottom`; Process B performed no selection or save write and loaded those exact values with `source=loaded`. | PASS |
| No demographic gameplay effect | The saved schema has no attribute or modifier fields; presentation remains cosmetic, skin changes only the separate body/head material, every preset uses the same outfit, and the recovered non-default appearance retained the same movement proof. | PASS |

## Final integrated acceptance evidence

- Corrected UE 5.8 editor and game builds passed after the first handoff run exposed and rejected an invalid W/A/S/D axis binding. Keyboard movement now uses native key polling, the remaining axis keys are verified `Axis1D`, and the accepted evidence contains zero ensure matches.
- Native `OddsWell.Character` automation passed **5/5**: appearance persistence, locomotion defaults, preset catalog, selection state, and starter outfit.
- The corrected clean Windows Development package passed in `109.45s`; its 58 files total `1,042,154,326` bytes and its pak is newer than the final source.
- The accepted two-process packaged proof used a non-default preset, passed outfit and locomotion QA in both processes, produced no second selection or save write, cleaned the QA slot, and exited without failure, error, fatal, assert, unhandled, or ensure matches.
- Frozen Python regressions passed **65/65** in `132.457s`. Brain Admin self-check and Python compilation passed.
- Documentation links, Canvas JSON, Git/LFS and ignored-output hygiene, frozen map/replay hashes, scoped whitespace, and diff checks passed. Cost was **$0.00**.

The exit review does not rerun Unreal, packaging, or the frozen suite because it changes documentation only and the accepted Phase 1B.5 source state was committed as `bada971` immediately before this review.

## Current read-only audit

- The Phase 1B commit chain is contiguous and clean: `8fe374e` → `c2cc693` → `39cb8cb` → `43bc592` → `bada971`.
- The review began from a clean worktree. Baseline diff check, Obsidian links, and the existing Beta Delivery Roadmap Canvas JSON passed.
- `Bootstrap.umap` remains SHA-256 `44fc5e531591672e10e3740a780eafb34326c2eadc7d85a37cfa352541932c16`.
- `BlockCourtBenchmark.umap` remains SHA-256 `f970a2f4609f2d6ec24475ae48c98e12db53bde2cd95a238f2015c3ff0840018`.
- The tracked replay fixture remains SHA-256 `35d03b7b472901ab3f498c8cd389cea4b9cd1ed9309bafe85cbbd3af1160719f`.
- The dedicated appearance QA save is absent and no related OddsWell, Unreal, shader-worker, or Uba process remains.

## Boundary and mandatory next gate

This review changes documentation only. It adds no runtime, source, map, configuration, save, gameplay, art, preset, clothing, city, backend, network, multiplayer, economy, credits, purchase, wagering, monetization, paid service, deployment, model, training, retraining, Phase 0, or replay behavior.

**Phase 1C is an OWNER GATE.** Before any city implementation, the owner must explicitly approve the world/city name, theme, geography and core walking-loop direction, visual language, and a minimal art-direction sheet. No city identity is canonized by this review.
