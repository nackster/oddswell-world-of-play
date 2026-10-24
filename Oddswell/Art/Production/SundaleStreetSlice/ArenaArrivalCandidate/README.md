# Sundale arena arrival

`ArenaArrival.blend` continues the reviewed `LayeredPlantingCandidate/LayeredPlanting.blend`, SHA-256 `e2559843759bcf76db05c0e97caf790e1f012d5ccfe9cb01db2f5344811a8f94`.

The front half of the arena now has 48 physical, six-millimeter glazed bays and three native concourse levels with slabs, rails, a curved inner wall and interior lighting. Eight central bays begin above a signed stone canopy; six inset door leaves face an actual central passage. The crossing ground-level bands are opened, and the center upper support lands on the canopy. Sixty replaced original arena objects remain editable and hidden. The roof, approach, original scene objects/materials, human, walk, retail, court and planting remain preserved.

The first trial was too bright and had a blank wall behind the doors. The retained revision reduces concourse lighting, provides visible small LED fixtures and opens the central corridor. The area emitters are hidden from direct camera/glossy/transmission rays; their modeled fixture surfaces remain visible. New glass is a copy of the arena material, while original materials are unchanged. Gray plaster and LED materials are authored native shaders. No bitmap is added; all 31 licensed packed maps remain preserved.

Run `build.py`, `audit.py` and `render.py` with Blender 4.5.5 LTS and `--python-exit-code 1 --python`. Mesh/box/tube/branch helpers are reused from `../build_scene.py`; custody helpers come from `../HipSeatMotionCandidate/audit.py`. Six source/candidate views match the arena, entrance and original gameplay camera at walk frame 7. `WholeSceneReview.md` records the remaining composition and realism work.

The independent cold audit preserves original controls/edges/old UVs/keys, packed maps, shaders, rest/six poses, full walk keyframes, original object transforms and visible human geometry in six poses. It checks actual bay thickness/count, central cut height, door vertical bounds and one ray through the central back-wall opening to the passage end. This is an offline architectural art study, not acceptance of a walkable or runtime arena.
