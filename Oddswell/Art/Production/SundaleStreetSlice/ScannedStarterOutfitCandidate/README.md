# Off-white starter outfit on the accepted scanned human

This advances milestone 1 of [[Development/Project Completion Roadmap]]. It dresses the accepted Eric scan in the beta starter outfit: an off-white ribbed mock-neck long-sleeve top, off-white cuffed joggers, and slate canvas sneakers with off-white soles, flat laces and a teal heel tab. Long garments follow the owner's 2026-10-20 choice in [[Design/Decisions/DEC-036 Scanned Human Starter Outfit Long Garments|DEC-036]]; shorts wait for an approved body source.

## What was built

Each garment is a separate skinned shell on the scan's own 88-bone rig, so nothing is a recolour of the suit.

- **Top:** fitted from 2,061 clothed scan faces. A constrained relaxation smooths away the vest's V-edge, collar and pocket steps without letting the fabric sink back toward the scan. It is finished with ribbed mock-neck, cuff and hem bands. The mock neck rises just above the scanned shirt collar, so the formal collar never shows.
- **Joggers:** fitted from 2,223 faces with a little extra inner-thigh clearance and gathered rib ankle cuffs. The scan's own normal map, reached through copied UVs, gives them real fold detail.
- **Sneakers:** fitted from 603 shoe faces with a 22 mm off-white sole band.

The rib bands are fitted to each garment's smoothed surface and carry a knit-rib shading pattern. Skin weights come from the nearest clothed scan surface, normalized per vertex. The lower top blends toward the hip bone so the hem does not follow the thighs.

Off-white uses the established palette value `[0.92, 0.90, 0.82]` as a display colour, shaded through its linear equivalent. The raw value rendered as paper white. Slate `[0.12, 0.18, 0.22]` and teal `[0.08, 0.72, 0.68]` match the Signal Jacket.

## Evidence

| File | Shows |
|---|---|
| `Full.png`, `Front.png`, `Side.png`, `Back.png` | Whole figure; walking, rest and side poses |
| `Close.png`, `Neck.png`, `NeckBack.png`, `Feet.png` | Neck, rib, cuff and sneaker detail |
| `Jacket.png` | Signal Jacket replacing the starter top, as the runtime does, over the joggers and sneakers |
| `Gameplay.png` | Retained Sundale street scene from its gameplay camera (offline Blender, **not Unreal**) |
| `Walking.mp4` | Two-second native walk preview, 24 frames at 12 fps |
| `Coverage.png`, `coverage-report.json` | Show-through masks: original suit fabric visible past the new garments is red |

**Checks:**

- The original mesh, UVs, weights, bind matrices and packed maps match the retained identity hash after a cold reopen.
- Every garment and trim evaluates to finite geometry at all 49 walk keys.
- Visible show-through was measured with flat masks from five cameras at 13 frames. The mean is 0.28% of the figure's clothing pixels, and the worst sample is 1.16% (right-side view, frame 9).

## Honest limits

- **Remaining show-through:** a small patch of the original trousers on the forward-swinging upper thigh in side views, and a thin wrist sliver of the white shirt cuff at some frames. Hidden interpenetration is not measured.
- **Silhouette:** the top keeps some of the vest's bulk across the back, and the joggers keep a pressed centre crease from the trouser scan. The mock neck flares slightly at its front base.
- **Sneakers:** they keep the dress shoe's last and read as mid-height.
- **Motion:** this is skinned shells, not cloth simulation. Feet are not locked, and hands and planted-foot timing are unchanged from the motion study.
- **Not runtime proof:** this does not reconcile the eight preset IDs or four tones, a production export contract, Unreal import or performance. The earlier rejected Phase 1L.5ct starter review keeps its status.

## Custody and rebuild

The editable model stays in ignored local storage at `downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy/OddsWellStarterOutfit.blend`. Vendor geometry, textures and derived Blender files are not redistributed here. `manifest.json` pins the candidate and evidence hashes.

Rebuild with Blender 4.5.5 LTS in background mode using `--factory-startup --disable-autoexec --python-exit-code 1`. Run the steps in this order:

1. `inspect.py` (Blender)
2. `select.py` (Python with Pillow)
3. `build.py -- --preview` (Blender)
4. `coverage.py` (Blender)
5. `street.py` (Blender)
6. Encode `Frames/%04d.png` at 12 fps with ffmpeg.
7. `retain.py` (Python)

**Next:** whole-character review against the street concept, then the production rig/preset/export contract. The body-source question for shorts and preset variety belongs to that contract.
