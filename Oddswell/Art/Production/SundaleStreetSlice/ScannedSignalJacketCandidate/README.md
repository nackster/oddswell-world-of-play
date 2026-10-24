# Signal Jacket on the accepted scanned human

This advances the wardrobe task in [[Development/Project Completion Roadmap]]. It adds a separate long-sleeve Signal Jacket shell to the accepted Eric character, with modeled zip tape and individual teeth, angled pocket welts, a tapered rib collar and a restrained chest tab. The slate `[0.12, 0.18, 0.22, 1]` and teal `[0.08, 0.72, 0.68, 1]` match the existing Signal Jacket palette.

The shell derives its fit from 1,816 selected clothed upper-body faces of the licensed scan, with 1,826 vertices and the original normalized skin weights. It is offset 8 mm, rounded and given garment thickness. A rest-space height attribute gives the shoulder band a continuous boundary through deformation. Trim pieces receive normalized source-surface skinning and share the same 88-bone rig. This is geometry and native shading, rather than a recolored vest image.

The original human's geometry, UVs, vertex groups/weights, bind matrices and three packed map bytes remain exact after cold reopen. Every jacket/trim mesh is evaluated at all 49 authored walk keys and checked for finite geometry. `jacket-report.json` retains the measurements and source/candidate identity. These checks do not prove collision-free cloth, planted feet, or game compatibility.

`Full.png` shows the whole figure. `Front.png`, `Close.png` and `Back.png` focus on the garment; `Walking.mp4` is a two-second native preview. `Gameplay.png` places the new character and jacket in the retained Sundale street scene using its gameplay camera. That scene is an offline Blender composition, not an Unreal screenshot.

The first trial had a jagged shoulder-color boundary and a pointed collar derived too closely from the business shirt. The retained candidate replaces those with a continuous rest-space color boundary and a smooth tapered collar. The closed zip silhouette reads as casual outerwear. Source white cuffs and a small shirt-neck edge remain visible; formal trousers, belt and shoes are temporary. Hands and planted-foot timing remain unfinished. This is a reviewable jacket checkpoint, not complete starter-outfit or final visual acceptance.

The editable source stays in ignored local storage at `downloads/licensed-characters/RenderpeopleEric/SignalJacketStudy/OddsWellSignalJacket.blend`, alongside the unchanged source scan. Vendor geometry, textures and derived Blender assets are not redistributed in this repository. Recipes, scalar selection indices, checks and permitted renders are retained here under the existing local licensed-asset workflow.

Rebuild locally: run `inspect.py` in Blender, `select.py` with Python/Pillow, and `build.py -- --preview` in Blender 4.5.5 LTS. Run `street.py` for the retained street-camera view. Encode the 24 odd native frames at 12 fps with ffmpeg. Use background mode, `--factory-startup`, `--disable-autoexec` and `--python-exit-code 1`.

Next establish a compatible underlying body/leg mesh and off-white casual starter garments, then footwear and relaxed hands. Review the complete character before freezing the production rig/preset/export contract and testing it in Unreal. The previous rejected starter-outfit review and all first-hour/runtime/beta gates keep their existing status.
