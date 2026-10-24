# Sundale promenade sightline and reflected light

`PromenadeLight.blend` continues `ArenaArrivalCandidate/ArenaArrival.blend`, SHA-256 `4be22d54515ef82276331c3286147e5f77dad9ddc2491d4e29d39eaf720cd524`.

One arrival-axis tree moves from (2, 40) to (−4.9, 42) with its stone surround, soil, original understory and current groundcover/grass/litter. Three complete civic lamps shift 0.5 m toward the court edge, retaining a gap to the blue surface. Thirty-five original objects receive recorded translations. Original control geometry, licensed maps and materials remain editable and unchanged. The original gameplay camera remains fixed.

Two copies of the retained bounce lights provide a modest increase in shade illumination: broad bounce 250→300 and courtyard reflection 700→950. Original light data remains intact, with the original two emitters hidden and the copies visible. Sun, world, native lettering, character, animation, other architecture and court geometry remain preserved. No new bitmap assets are added.

Eight matched native renders review the source/candidate torso, hips, complete side figure and gameplay composition. The full-body review camera was widened after catching a cropped sole. Run `build.py`, `audit.py` and `render.py` in Blender 4.5.5 LTS with `--python-exit-code 1 --python`. The cold audit reuses custody helpers from `../HipSeatMotionCandidate/audit.py` and checks all original controls/maps/shaders/world/light data/lettering, full walk keys, rig rest/six poses and six-pose visible human geometry. Declared moves, lamp bounds relative to the blue court and tree/soil alignment are checked.

Thirty camera-to-arrival geometric rays compare the source and candidate. They ignore foliage alpha transparency, so the paired gameplay render is the visual evidence; ray counts alone do not establish complete optical visibility. See `WholeSceneReview.md` for remaining human, shop, planting and lighting work. The full goal remains active; this is offline scene development.
