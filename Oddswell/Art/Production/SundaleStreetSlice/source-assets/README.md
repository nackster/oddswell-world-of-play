# Anatomical source

`makehuman-base.obj` is the hm08 core base mesh from the MakeHuman Community repository, downloaded for this scene from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj

The source header explicitly releases this asset under CC0. The retained `MAKEHUMAN-LICENSE.ASSETS.md` is from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/LICENSE.ASSETS.md

The scene builder reads only the body group and joint reference points, normalizes its height to 1.8 m, and retains the head/neck, lower legs and hands for the clothed static study. No helper surfaces, game skeleton, or new gameplay preset are introduced. The original source file is preserved intact. Exact hashes are recorded in the scene delivery manifest.

The continuing character pass narrows the source hand spread, relaxes the fingers and preserves calf volume while correcting the base stance. The leg surface extends beneath the shorts to prevent gaps at the posed hems. At the owner's September 21 request for a more human character, the source skull, face and ears replaced the earlier authored faceless head. The lower neck is cropped, fitted and extended beneath the jacket collar. Locally authored eyes use the source eye-joint positions; iris/pupil patches, brow strands and face tint are additional native detail. The original anatomy remains unchanged on disk.

## Skin source

The retained diffuse map and original `.mhmat` come from the official [MakeHuman system assets](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) CC0 pack. The material explicitly records its September 2020 CC0 release and Data Collection AB, Joel Palmius and Jonas Hauquier as copyright holders at release. `skin-source.json` records archive/member hashes, URLs, and the original material-name versus directory/tag discrepancy. `../fetch_skin.py` validates those bytes before extraction.

The original body UVs are preserved on the exposed head, hands and legs; the fitted neck skirt interpolates them beneath the collar. The shader adjusts saturation/value and roughness while the original image remains unchanged. This is a static derivative anatomy/material study, with no claim of a scan, final character identity or production rig.

## Mature tree source

`jacaranda_tree_4k.blend` is the original CC0 [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree), authored by Rico Cilliers with guidance from Rob Tuytel. `jacaranda-source.json` records its exact URL/hash and the ten retained 2K surface maps. `../mature_trees.py` adapts native leaf seeds, growth density, foliage appearance and planting proportions into three shared variants. Secondary variants receive upright or spreading proportions and a gentle upper-branch lean. The source file is preserved intact; the derivatives and maps are packed into the main street-scene Blender file.

## Broad-leaf source

`island_tree_01_2k.blend` is the original CC0 [Island Tree 01](https://polyhaven.com/a/island_tree_01), processed by Rico Cilliers and scanned/processed by Rob Tuytel. `broadleaf-source.json` retains official API MD5 verification, local SHA-256 hashes, URLs and seven leaf/twig maps. The source trunk and its texture channels are not used. `../broadleaf_canopy.py` adapts LOD1 clusters, preserving UVs while simplifying geometry and adjusting scale and shading. These clusters grow on the raised Jacaranda branching and are instanced around locally authored shrub stems. Both original Blender sources remain unchanged on disk.
