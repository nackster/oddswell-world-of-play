# Sundale character and landscape study

The owner’s first OddsWell concept picture remains the visual target. [DevelopmentGoal.md](DevelopmentGoal.md) records the active goal and acceptance criteria. The scene is being developed through actual modeling and Blender Cycles renders; the reference is not projected onto geometry or used as a scene background.

September 21 continuation: after the modest fold checkpoint `8c868ec`, the shorts were rebuilt as a continuous tailored surface through the hips and inseam, the sleeve caps and shoulder join were softened, and civic limestone gained restrained sediment variation. All six native views were rebuilt. The visual goal remains active; see [VisualReview.md](VisualReview.md) for the remaining gaps.

The owner's next direction was to make the character more human. From checkpoint `c255dd5`, the featureless oval head was replaced with the retained anatomical skull, jaw, nose, lips and ears. Fitted eyes, fine brow strands and localized skin tint complete this first human-face study. A cropped source-shoulder defect was caught in close-up and removed; the neck now extends inside the collar. The review set includes eight native views, adding front and profile portraits.

![Native gameplay view](StreetSlice_Gameplay.png)

This pass develops a tailored slate jacket with a sewn teal yoke, shaped sleeves, fine seams and localized folds; continuous cotton shorts; relaxed hands, fuller calves and a grounded walking stance; closed canvas shoes with heel details. The promenade has mature tree canopies, grasses, flowering stems, groundcover, fallen leaves, planted seats, deeper illuminated retail windows and a landscaped arena approach. Restrained teal connects clothing, stone furniture, lights and the arena.

![Character inspection](StreetSlice_Character_Detail.png)

![Landscape inspection](StreetSlice_Landscape_Detail.png)

## Native source and rendering

Open `OddsWell_Sundale_StreetSlice.blend` in Blender 4.5 or later. It is compressed and contains packed surface maps and the sky environment. Named collections separate the character, planting, architecture, civic details, court, arena and lights. Thirteen mature trees share three evaluated growth variants; their original growth-node source and deterministic adaptations are retained.

- `build_scene.py` rebuilds the scene. It executes `develop_character_landscape.py` for garment construction and landscape detail, and `mature_trees.py` for the adapted tree family.
- `broadleaf_canopy.py` adapts retained leaf clusters to the tree branching and foreground shrubs. The woody structure is raised before leaf emission so leaf proportions remain intact.
- `refine_minerals.py` layers fine pores and mineral grain into the native stone and brick materials, and directs oak fibers along the seats and shelves.
- `refine_character_head.py` fits the source-derived neck beneath the collar, constructs eyes at the retained anatomical joints, fits brow strands to the head, and adds restrained skin variation.
- `render_views.py` reopens the saved scene and renders the 1920x1080 gameplay view at 160 samples plus seven inspection views at 96 samples. `inspect_details.py` provides faster 48-sample close-ups during modeling; `-- --head-only --gpu` renders the face front and profile.
- `verify_scene.py` checks the cold-open artifact, packed resources, eight cameras, flat court paint, a closed anatomical head and paired eyes, the neck crop, stance-foot contact, connected jacket/shorts surfaces, three closed boundary loops at the shorts waist/hems, and the three shared tree variants. Use `-- --draft` before final cameras exist.
- `fetch_stone_material.py`, `fetch_sky.py`, `fetch_tree.py` and `fetch_broadleaf.py` restore the retained public source maps if needed. The finished Blender file packs 24 maps, including seven leaf/twig maps added in the broad-leaf pass.

Run Blender with `--background --factory-startup --disable-autoexec --python-exit-code 1 --python build_scene.py`. Add `-- --preview` for a 1100x619 draft. Python exceptions must cause a nonzero exit. The preview is a working file; delivery renders and their hashes are recorded in `delivery.json` after verification.

The build and render scripts accept `--gpu` after the `--` separator to use an available NVIDIA OptiX device; omit it for CPU rendering. This changes the render device, not the requested resolution or samples. The retained refinement render set records its device in `scene-evidence.json`.

## Sources and adaptations

Architecture, paving, court, arena, civic furniture, garments, grasses, flowering stems, groundcover, smaller leaf geometry and scene composition were authored for this study.

The exposed anatomical surfaces derive from the [MakeHuman hm08 CC0 base mesh](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md). The original OBJ, asset license and transformations remain under `source-assets`. This is a static clothing/anatomy study, not a new approved gameplay rig.

The mature trees adapt the branching and growth masks of [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree), by Rico Cilliers with guidance from Rob Tuytel, under CC0. The woody structure is raised before growing leaves. One emission pass combines the original branch masks; secondary variants add upright or spreading proportions and a gentle upper-branch lean. The original source Blender file is unchanged. `source-assets/jacaranda-source.json` records the exact source and ten retained 2K map hashes.

Broad leaf clusters and their twig materials come from [Island Tree 01](https://polyhaven.com/a/island_tree_01), by Rico Cilliers and Rob Tuytel, also CC0. The original native file and seven 2K maps are retained in `source-assets/broadleaf-source.json`. The derivative simplifies the source LOD1 clusters while retaining UVs, adjusts their scale and light transmission, and uses the same leaf family in stemmed foreground shrubs with a darker understory material. This is an authored fictional planting family, not a botanical claim that the two source trees are the same species.

Surface maps are [Sandstone Blocks 08](https://polyhaven.com/a/sandstone_blocks_08) and [Bark Brown 01](https://polyhaven.com/a/bark_brown_01), by Rob Tuytel. The photographed environment is [Kloppenheim 06 (Pure Sky)](https://polyhaven.com/a/kloppenheim_06_puresky), by Greg Zaal and Jarod Guest. These are distributed under [Poly Haven’s CC0 license](https://polyhaven.com/license), with URLs and hashes retained in `textures`. No paid marketplace asset or paid image generation was used in this modeling pass.

## Current limits

The goal remains active. The reference still has more resolved garment behavior, architectural variety, planting composition and photographic surface detail. These native renders demonstrate progress and expose remaining defects; they do not claim an exact match or final art approval.

The tested Unreal character and map remain separate. This scene has not established animation compatibility, production LODs, collision, baked game materials or a frame-rate budget. Offline render quality does not grant runtime integration or beta-exit credit.
