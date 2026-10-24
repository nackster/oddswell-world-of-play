# Scanned human character direction

At the user's request, character development switches to an imported scanned human instead of further small edits to the earlier body. The selected asset is Renderpeople **Eric Rigged 001**, downloaded from the publisher's [free rigged pack](https://renderpeople.com/free-3d-people/).

The model contains 10,353 vertices, 10,558 polygons, original UVs and skinning, and an 88-bone skeleton. Three original texture files are packed in the editable character. The imported mesh, topology, UVs, weights and bind matrices pass exact comparisons against the original import. Texture bytes match the downloaded diffuse, normal and gloss files.

`Full.png`, `Face.png` and `Gameplay.png` render the actual imported geometry in the retained Sundale setting. Full/face images use 40 CPU samples. `Walking.mp4` contains 24 native frames at 640 x 704, 12 fps, lasting two seconds. The original native walk is mapped to 20 vendor bones over 49 authored keys. This is an offline movement study with lowest-vertex grounding, not a finished gait, foot-lock/contact proof or engine integration.

The compact editable file is kept at `downloads/licensed-characters/RenderpeopleEric/OddsWellHuman.blend`. Its geometry, rig, motion study and three packed maps are self-contained. The full street-scene study also remains locally at `client/OddsWell/Saved/NextTen20260912/ScannedHumanStudy/ScannedHumanWalk.blend`.

The publisher's [license](https://renderpeople.com/general-terms-and-conditions/) permits game and rendered-image use but restricts model-file redistribution. Vendor sources and derived Blender files stay in ignored local storage. This repository retains recipes, checks and permitted rendered previews rather than redistributing those model files.

To rebuild, run `fetch.py` with Python, then use Blender 4.5.5 LTS for `inspect.py`, `build.py`, `retarget.py`, `audit.py`, `render.py -- --walk --preview` and `export.py`, in that order. Repository recipe copies write to the local licensed-asset folder. Download and scene-source hashes are pinned in the reports.

The source business clothing is temporary for the realism study. Next adapt the character's styling to OddsWell, refine the walk and facial performance, and validate the compatible game derivative before engine import. The full human/landscape goal remains active; existing starter-outfit and runtime gates retain their status.
