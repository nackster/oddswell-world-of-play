# Anatomical source

`makehuman-base.obj` is the hm08 core base mesh from the MakeHuman Community repository, downloaded for this scene from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj

The source header explicitly releases this asset under CC0. The retained `MAKEHUMAN-LICENSE.ASSETS.md` is from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/LICENSE.ASSETS.md

The scene builder reads only the body group and joint reference points, normalizes its height to 1.8 m, and retains the lower legs and hands for the clothed static study. The head is an authored faceless surface. No helper surfaces, game skeleton, or new gameplay preset are introduced. The original source file is preserved intact. Exact hashes are recorded in the scene delivery manifest.

The continuing character pass narrows the source hand spread, relaxes the fingers and preserves calf volume while correcting the base stance. The leg surface extends beneath the shorts to prevent gaps at the posed hems. A new authored faceless skull/jaw/neck replaces the source head. The original anatomy remains unchanged on disk.

## Mature tree source

`jacaranda_tree_4k.blend` is the original CC0 [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree), authored by Rico Cilliers with guidance from Rob Tuytel. `jacaranda-source.json` records its exact URL/hash and the ten retained 2K surface maps. `../mature_trees.py` adapts native leaf seeds, growth density, foliage appearance and planting proportions into three shared variants. Secondary variants receive upright or spreading proportions and a gentle upper-branch lean. The source file is preserved intact; the derivatives and maps are packed into the main street-scene Blender file.

## Broad-leaf source

`island_tree_01_2k.blend` is the original CC0 [Island Tree 01](https://polyhaven.com/a/island_tree_01), processed by Rico Cilliers and scanned/processed by Rob Tuytel. `broadleaf-source.json` retains official API MD5 verification, local SHA-256 hashes, URLs and seven leaf/twig maps. The source trunk and its texture channels are not used. `../broadleaf_canopy.py` adapts LOD1 clusters, preserving UVs while simplifying geometry and adjusting scale and shading. These clusters grow on the raised Jacaranda branching and are instanced around locally authored shrub stems. Both original Blender sources remain unchanged on disk.
