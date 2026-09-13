# Sundale character and landscape study

The owner’s first OddsWell concept picture remains the visual target. [DevelopmentGoal.md](DevelopmentGoal.md) records the active goal and acceptance criteria. The scene is being developed through actual modeling and Blender Cycles renders; the reference is not projected onto geometry or used as a scene background.

![Native gameplay view](StreetSlice_Gameplay.png)

This pass develops a tailored slate jacket with a sewn teal yoke, shaped sleeves, fine seams and localized folds; continuous cotton shorts; relaxed hands, fuller calves and a grounded walking stance; closed canvas shoes with heel details. The promenade has mature tree canopies, grasses, flowering stems, groundcover, fallen leaves, planted seats, deeper illuminated retail windows and a landscaped arena approach. Restrained teal connects clothing, stone furniture, lights and the arena.

![Character inspection](StreetSlice_Character_Detail.png)

![Landscape inspection](StreetSlice_Landscape_Detail.png)

## Native source and rendering

Open `OddsWell_Sundale_StreetSlice.blend` in Blender 4.5 or later. It is compressed and contains packed surface maps and the sky environment. Named collections separate the character, planting, architecture, civic details, court, arena and lights. Mature trees share one evaluated mesh; their original growth-node source and deterministic adaptations are retained.

- `build_scene.py` rebuilds the scene. It executes `develop_character_landscape.py` for garment construction and landscape detail, and `mature_trees.py` for the adapted tree family.
- `render_views.py` reopens the saved scene and renders the 1920x1080 gameplay view at 160 samples plus inspection views at 96 samples. `inspect_details.py` provides faster 48-sample close-ups during modeling.
- `verify_scene.py` checks the cold-open artifact, packed resources, cameras, flat court paint, collar boundaries, stance-foot contact and the connected shorts surface. Use `-- --draft` before final cameras exist.
- `fetch_stone_material.py`, `fetch_sky.py` and `fetch_tree.py` restore the retained public source maps if needed. The finished Blender file already packs the required maps.

Run Blender with `--background --factory-startup --disable-autoexec --python-exit-code 1 --python build_scene.py`. Add `-- --preview` for a 1100x619 draft. Python exceptions must cause a nonzero exit. The preview is a working file; delivery renders and their hashes are recorded in `delivery.json` after verification.

## Sources and adaptations

Architecture, paving, court, arena, civic furniture, garments, grasses, flowering stems, groundcover, smaller leaf geometry and scene composition were authored for this study.

The exposed anatomical surfaces derive from the [MakeHuman hm08 CC0 base mesh](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md). The original OBJ, asset license and transformations remain under `source-assets`. This is a static clothing/anatomy study, not a new approved gameplay rig.

The mature trees adapt [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree), by Rico Cilliers with guidance from Rob Tuytel, under CC0. Native growth-node density and leaf size, shader settings, placement, proportions and rotation are adjusted in `mature_trees.py`. The original source Blender file is unchanged. `source-assets/jacaranda-source.json` records the exact source and ten 2K map hashes. Opening the original source alone may request its original 4K paths; the builder explicitly substitutes and packs the retained 2K maps.

Surface maps are [Sandstone Blocks 08](https://polyhaven.com/a/sandstone_blocks_08) and [Bark Brown 01](https://polyhaven.com/a/bark_brown_01), by Rob Tuytel. The photographed environment is [Kloppenheim 06 (Pure Sky)](https://polyhaven.com/a/kloppenheim_06_puresky), by Greg Zaal and Jarod Guest. These are distributed under [Poly Haven’s CC0 license](https://polyhaven.com/license), with URLs and hashes retained in `textures`. No paid marketplace asset or paid image generation was used in this modeling pass.

## Current limits

The goal remains active. The reference still has more resolved garment behavior, architectural variety, planting composition and photographic surface detail. These native renders demonstrate progress and expose remaining defects; they do not claim an exact match or final art approval.

The tested Unreal character and map remain separate. This scene has not established animation compatibility, production LODs, collision, baked game materials or a frame-rate budget. Offline render quality does not grant runtime integration or beta-exit credit.
