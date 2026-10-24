---
tags: [development, milestone, launch]
status: milestone-2-delivered-with-known-gap
date: 2026-10-24
---

# Milestone 2: Complete loop with real characters

This delivers M2 of [[Development/Epic Store Launch Plan]] under [[Design/Decisions/DEC-038 MetaHuman Player Characters|DEC-038]].

## What's new in the build

1. **Title screen:** Continue (when a career exists), New career (asks before replacing a save), Settings and Quit.
2. **Character chooser:** the eight presets are now real MetaHumans: Kelvin, Lorenzo, Trey, Isaiah, Jelena, Grace, Sunita and Zuri. Each stands on a turning stand with studio lighting and a backdrop.
3. **In the world:** the chosen MetaHuman walks, runs and jumps through Epic's standard locomotion animation, in Sundale, the arena and your home. Movement, camera, capsule and saves are unchanged.
   - The Signal Jacket (and, since M3, any bought clothing) recolours the garment's shirt.
4. **Pause menu (Esc or Start):** Resume, Settings, Quit to title, Quit game. The game and any replay freeze while it is open.
5. **Settings:** display mode, resolution, graphics quality, VSync, frame limit, mouse sensitivity, invert Y and control hints. They're saved with Unreal's standard user settings.
6. **First-day guide:** a checklist (shift, bet, watch, sleep) with an on-screen marker toward the next place.

## How it was built

- **MetaHuman builds:** `client/tools/metahuman/` builds each MetaHuman from Epic's presets through the MetaHuman Creator Python API, retrying the flaky cloud step. `setup_runtime.py` links the MetaHuman skeleton to the mannequin animation skeleton.
  - The generated MetaHumans are about 450 MB each and are not in Git. Rebuild them with `build_set.py`.
- **Assembly:** `Career/OddsWellMetaHumanAppearance.cpp` assembles a MetaHuman on the existing character:
  - The body runs locomotion and the outfit follows the body.
  - The face runs Epic's `ABP_Face`.
  - Hair, brows and beard bind to the face.

## Evidence

| Check | Result |
|---|---|
| Editor automation | 77/77 pass. The character test now checks the MetaHuman path: body visible and animated, face animated on the body, outfit following, placeholder hidden, and the jacket shown |
| Packaged front end (`-FrontEndShots`) | Title, Kelvin, Zuri and Settings captured |
| Packaged play-through (`-CareerSmoke`) | PASS. The MetaHuman is ready in all three levels: Sundale, arena and home |

Screenshots: `FrontEnd_1_Title`, `FrontEnd_2_ChooserKelvin`, `FrontEnd_3_ChooserZuri`, `FrontEnd_4_Settings`, `CareerSmoke_01_Welcome`, `CareerSmoke_07_Studio`.

## Known gap: MetaHuman hair does not render

The hair, brow and beard grooms attach without errors: visible, registered, sane bounds, and no warnings in the cook or the game. They still don't draw in the packaged build. Kelvin's curly fade, goatee and mustache are missing, so he looks bald. Some presets (Zuri) are bald by design.

Already ruled out:
- Leader-pose face: the face now runs `ABP_Face`, as in Epic's blueprint.
- GPU skin cache: it is enabled on the face and body.
- Engine warnings during registration: the hair now warms its graphics pipeline cache before it registers, which removed the one engine warning.

Still to check, as the first task of M4 (presentation):
1. Epic's LOD sync and MetaHuman components, which drive groom LOD in the generated blueprint.
2. Substrate with the hair-card materials.
3. Whether a face-on comparison with Epic's blueprint renders hair in this build.

`ODDSWELL_METAHUMAN_GROOM` log lines record each groom's state when the chooser shows a preset.

## Still to do from M2

- **First-hour test:** "someone who has never seen the game finishes the first hour without help" needs a real player.
