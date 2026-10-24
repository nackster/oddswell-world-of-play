---
tags:
  - development
  - beta
  - unreal-engine
  - character
status: complete
date: 2026-07-19
---

# Phase 1B.1: Character Preset Catalog

## Outcome

OddsWell now has the first executable Phase 1B data slice: eight gameplay-identical placeholder character presets covering the approved masculine and feminine presentations across the same four skin tones.

Every preset starts with `starter_offwhite_top` and `starter_offwhite_bottom` item IDs. The starter clothing is therefore replaceable equipment data, not permanent character geometry.

## Scope advanced

- Beta Game Bible: **First-hour player journey — Choose a default character**.
- Beta Game Bible: **Avatar and clothing**.
- Player-facing risk reduced: the selection screen can consume one validated catalog instead of embedding inconsistent demographic or outfit behavior in UI code.

## Implementation

- `CharacterPresetCatalog.h/.cpp` defines the minimal native UE 5.8 catalog and validator.
- The catalog contains cosmetic identity, presentation, skin tone, and equipped item IDs only. It contains no gameplay attributes or modifiers.
- One native automation test locks the eight unique IDs, four-per-presentation split, same four skin tones, and identical two-piece starter equipment.
- [[Design/Decisions/DEC-007 Phase 1B Character Defaults]] records the owner's camera, movement, preset, and starter-outfit decisions.

## Validation

- UE 5.8 `OddsWellEditor` Development build: **passed**.
- `OddsWell.Character.PresetCatalog` native automation test: **1/1 passed**.
- Frozen Python regression suite: **65/65 passed** in `132.517s`.
- Brain Admin self-check: **passed**.
- Python compilation: **passed**.
- Cost: **$0.00**.

## Boundary and next gate

This phase adds no selection screen, mesh, animation, controllable pawn, save file, multiplayer state, final character art, city identity, economy, wagering, service, or deployment.

The next smallest gate is **Phase 1B.2: a fast local character-selection screen with a safe default**, consuming this catalog without adding final art.
