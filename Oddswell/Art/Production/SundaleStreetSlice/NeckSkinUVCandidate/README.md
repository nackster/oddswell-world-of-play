# Continuous neck skin mapping

This native Blender candidate continues [ShoulderEaseCandidate](../ShoulderEaseCandidate/README.md), source SHA-256 `9A6BB3CA8D257CD7E130D0CDDC460264D7B645D4669E4D68416F7CA35E80730F`. It corrects the extruded lower-neck skin map while retaining the torso/hip stance, rounder shoulders, fitted clothing and slate/teal OddsWell identity. No external assets or replacement textures are introduced.

The retained neck has 50 long skirt faces, each with identical top and bottom UV coordinates despite about 60 mm of geometric height. Their zero texture area stretches one row of the packed skin photograph vertically. The new `Continuous neck skin UV` layer estimates a local angular/height gradient from valid upper-neck mapping, then extends that gradient down the skirt. The hidden closing-cap rim follows the new bottom coordinates. The original `MakeHuman source UV` layer remains byte-exact; all upper-neck and face control UVs stay exact. An explicit UV Map node routes only the head's existing CC0 skin photograph through the derived layer. Pore relief and other skin shader paths remain intact.

The [saved scene](NeckSkinUV.blend) retains the separate original UV layer and source scene. To compare the old mapping, route the skin image Vector input to `MakeHuman source UV` through an explicit UV Map node. Merely changing the active layer does not override the delivered explicit node. This is a local gradient extension, not a newly painted atlas or a full-body UV rebuild.

## Native review

- [Neck front close-up](NeckSkinUV_NeckFront.png)
- [Neck rear close-up](NeckSkinUV_NeckRear.png)
- [Full front](NeckSkinUV_Front.png)
- [Gameplay scene](NeckSkinUV_Gameplay.png)

The native Cycles views use 12 samples for figure/neck studies and 24 for gameplay. Front and rear close-ups show reduced vertical stretching and more natural skin variation, with no detected break at shared bottom UV edges. Remaining chest/underarm cloth, collar-to-jacket ledge, skin/form refinement and facial individuality keep the very-real human goal open.

## Reproduction and evidence

[build.py](build.py) opens the hash-pinned source and uses Blender's bundled NumPy for the local least-squares UV gradients. Run with Blender 4.5.5 LTS using `--python-exit-code 1 --python`. [uv-slope.json](uv-slope.json) records each bottom UV and its fitted derivative. No dependency installation is needed.

[audit.py](audit.py) opens both source and delivered scenes in a fresh process. It requires exact coordinates, topology, object transforms and shape-key values/coordinates for all 4,720 mesh/curve objects; exact packed bytes for all 31 source maps; and preservation of all 893 original UV layers. It also requires nonzero area and no folded UV triangles on the repaired skirt, matching shared bottom UVs, unchanged upper-neck/face UV controls, and the explicit head-only shader route. [NeckSkinUV-audit.json](NeckSkinUV-audit.json) records those checks. [cold-check.json](cold-check.json) records the independent shared scene check. [Delivery-manifest.json](Delivery-manifest.json) binds the actual saved source, scripts, reports and review renders to SHA-256 hashes.

Geometry is exact to the previously checked shoulder candidate, so this mapping pass does not claim a new cloth simulation or animation/rig proof. Continue chest/underarm drape and collar attachment, facial/form refinement and whole-reference review; then architectural/retail variety, selective layered planting and warm street lighting. Material/hair baking, a compatible rigged derivative, LOD/collision budgets and controlled engine validation remain later requirements. Existing starter-outfit walk acceptance and stopped export/import preparation remain authoritative. No runtime, final-art, physical first-hour, Phase 1L exit or beta-exit credit follows; the goal remains active.
