# Sundale foreground apparel shop

`RetailDepth.blend` continues the reviewed `ShoulderChestCandidate/ShoulderChest.blend`, SHA-256 `8b2f0e5634f1198bbdbb5054c961668cb86825764ada8d24355296cbc290de7a`.

The first apparel shop visible along the gameplay approach, facade at X −7.2 m / Y 7 m, now has a native room extending 3.65 m behind the facade reference plane. The original 1.48 m backing and solid rear volume are retained but hidden, along with this shop's generic goods, flat shirts and old hangers. Explicit visibility changes are recorded in `build-report.json`; original geometry remains editable.

New oak/plaster floor, ceiling and wall returns define the deeper space. An oak island, folded cotton apparel, supported clothing rails and two static displays of the reviewed modeled jacket replace the generic display blocks. The two jackets share a baked garment mesh; the player and its rig remain unchanged. A physical OddsWell plaque continues the slate, restrained teal and warm mineral identity. Warm area lights reveal the interior. Existing licensed fabric/maps and native built-in lettering are reused; no bitmap assets are added.

Run `build.py`, `audit.py` and `render.py` with Blender 4.5.5 LTS and `--python-exit-code 1 --python`. The original native geometry helpers remain in `build_scene.py`; cold custody helpers remain in `HipSeatMotionCandidate/audit.py`. Before/after inspection cameras are matched, and the original gameplay camera is retained. `render.py` recreates both source comparison images, both retained views and the 1920×1080 gameplay view.

The cold audit preserves all original mesh/curve controls, edges, UVs, keys, packed maps, shaders, rig rest/six poses and full native walk keyframe data. All visible main-character geometry is compared in six poses. Existing 49-frame human checks remain the immediate source's scoped proof, not a new or broader runtime claim. See `WholeSceneReview.md` for remaining human, neighborhood and lighting work. This room study does not establish walkable entry, shop collision/LOD/performance or beta readiness.
