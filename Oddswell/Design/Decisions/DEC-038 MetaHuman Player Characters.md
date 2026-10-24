---
tags:
  - decision
  - character
  - launch
status: owner-decision
date: 2026-10-24
---

# DEC-038 MetaHuman Player Characters

## Context and authority

The [[Development/Epic Store Launch Plan]] item D5 asked how the eight required player presets get real characters. The Bible requires masculine and feminine presentations across four skin tones. The licensed Renderpeople scan (Eric) is one man and cannot cover them. On 2026-10-24 the owner chose the recommended option, MetaHuman.

## Decision

The eight player presets will be built as **MetaHumans**, using Epic's MetaHuman Creator, which ships with the installed Unreal Engine 5.8.

- The accepted scanned human sets the quality bar and look reference: realistic faces and bodies, and casual OddsWell clothing.
- The off-white starter outfit and the Signal Jacket are rebuilt as MetaHuman-compatible wardrobe items. The DEC-036 long-garment rule still applies.
- Gameplay stays identical across presets. Preset IDs, skin tones, movement, capsule, camera and saves keep their existing contracts.
- MetaHuman's cloud step (face auto-rigging and high-resolution texture download) needs the owner's Epic account signed in to the Unreal editor. Character creation and assembly are otherwise scripted.

## Boundaries

- No real person's likeness: faces are original MetaHuman presets or edits.
- Performance is measured on the minimum-spec target in M5. Characters use the Optimized pipeline at medium quality unless measurement says otherwise.
- The Renderpeople scan stays a local reference asset under its licence. It does not ship unless separately decided.
