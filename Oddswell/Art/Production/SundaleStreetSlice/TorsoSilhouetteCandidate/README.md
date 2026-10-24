# Adult arm contour and sleeve study

`TorsoSilhouette.blend` continues the editable `CottonEaseCandidate` scene. One new anatomical-support key adds a graded arm taper around the existing centerlines; one shared jacket/cage key reduces excessive sleeve ease. A graded posed-surface fit follows the actual arm and three shallow outward elbow gathers add cloth definition. Original source controls, old keys/UVs/fields/weights, bones, walking animation, licensed packed maps, shaders and scene remain preserved.

Use Blender 4.5.5 to run `build.py`, `audit.py` and `render.py` from this repository. `render.py --body` produces matched temporary clay views of the internal support; it changes no saved native material or visibility. `render-walk.py --preview` produces the native odd-frame images used for the two-second 12 fps walking preview.

See [WholeFigureReview.md](WholeFigureReview.md), [cold-audit.json](cold-audit.json), [build-report.json](build-report.json) and [Delivery-manifest.json](Delivery-manifest.json). This offline art checkpoint keeps the full human/landscape goal active and does not advance the separate starter-outfit or stopped engine handoff gates.
