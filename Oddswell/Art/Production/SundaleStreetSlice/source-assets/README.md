# Anatomical source

`makehuman-base.obj` is the hm08 core base mesh from the MakeHuman Community repository, downloaded for this scene from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj

The source header explicitly releases this asset under CC0. The retained `MAKEHUMAN-LICENSE.ASSETS.md` is from:

https://raw.githubusercontent.com/makehumancommunity/makehuman/master/LICENSE.ASSETS.md

The scene builder reads only the body group and joint reference points, normalizes its height to 1.8 m, and retains the head/neck, lower legs and hands for the clothed static study. No helper surfaces, game skeleton, or new gameplay preset are introduced. The original source file is preserved intact. Exact hashes are recorded in the scene delivery manifest.

The continuing character pass narrows the source hand spread, relaxes the fingers and preserves calf volume while correcting the base stance. The leg surface extends beneath the shorts to prevent gaps at the posed hems. At the owner's September 21 request for a more human character, the source skull, face and ears replaced the earlier authored faceless head. The lower neck is cropped, fitted and extended beneath the jacket collar. Locally authored eyes use the source eye-joint positions; iris/pupil patches, brow strands and face tint are additional native detail. The original anatomy remains unchanged on disk.

The subsequent body pass retains the source UVs while scaling/curling the hands and refining the calf/ankle width. The hand-region crop follows the wrist/knuckle direction and includes the complete thumb, fixing an exposed boundary from the earlier X-coordinate cutoff. These are derived static shapes; the original OBJ remains unchanged.

## Skin source

The retained diffuse map and original `.mhmat` come from the official [MakeHuman system assets](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) CC0 pack. The material explicitly records its September 2020 CC0 release and Data Collection AB, Joel Palmius and Jonas Hauquier as copyright holders at release. `skin-source.json` records archive/member hashes, URLs, and the original material-name versus directory/tag discrepancy. `../fetch_skin.py` validates those bytes before extraction.

The original body UVs are preserved on the exposed head, hands and legs; the fitted neck skirt interpolates them beneath the collar. The shader adjusts saturation/value and roughness while the original image remains unchanged. This is a static derivative anatomy/material study, with no claim of a scan, final character identity or production rig.

## Fabric surface sources

`fabric-sources.json` retains the URLs, original MD5/SHA-256 identities, authors and physical dimensions of [Terlenka](https://polyhaven.com/a/terlenka) and [Denim Fabric 04](https://polyhaven.com/a/denim_fabric_04). Both are distributed under [Poly Haven CC0](https://polyhaven.com/license), photographed by colormass and processed by Rico Cilliers. Six original 2K diffuse, displacement and roughness maps are retained unchanged. `../fetch_fabrics.py` restores them and checks upstream identities. The native shader uses grayscale diffuse variation with the OddsWell garment colors, physical-scale box projection and fine bump.

## Mature tree source

`jacaranda_tree_4k.blend` is the original CC0 [Jacaranda Tree](https://polyhaven.com/a/jacaranda_tree), authored by Rico Cilliers with guidance from Rob Tuytel. `jacaranda-source.json` records its exact URL/hash and the ten retained 2K surface maps. `../mature_trees.py` adapts native leaf seeds, growth density, foliage appearance and planting proportions into three shared variants. Secondary variants receive upright or spreading proportions and a gentle upper-branch lean. The source file is preserved intact; the derivatives and maps are packed into the main street-scene Blender file.

## Broad-leaf source

`island_tree_01_2k.blend` is the original CC0 [Island Tree 01](https://polyhaven.com/a/island_tree_01), processed by Rico Cilliers and scanned/processed by Rob Tuytel. `broadleaf-source.json` retains official API MD5 verification, local SHA-256 hashes, URLs and seven leaf/twig maps. The source trunk and its texture channels are not used. `../broadleaf_canopy.py` adapts LOD1 clusters, preserving UVs while simplifying geometry and adjusting scale and shading. These clusters grow on the raised Jacaranda branching and are instanced around locally authored shrub stems. Both original Blender sources remain unchanged on disk.

The realism pass corrects the handedness of the source Y/Z coordinate conversion: derived face order and matching UV corners are reversed together. This makes exposed skin normals outward without altering the original OBJ or its UV values, and permits meaningful cloth contact against the legs.

## Pinned facial targets

`facial-targets.json` records six original hm08 CC0 targets from official MakeHuman commit `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`, including pinned URLs, upstream Git blob SHA-1 identities, SHA-256 values and byte counts. `../fetch_face_targets.py` validates the source identities and CC0/hm08 headers. The source files remain byte-for-byte intact. The native builder applies `head-age-incr.target` at 0.55 and each paired `eye-height2-decr.target` at 0.45 before coordinate conversion, only in memory. These restrained artistic changes do not imply a scanned person or a measured age. Locally authored iris vertex colors, brow curves and eyelash curves require no extra texture maps.

The added sources are `caucasian-male-young.target`, `head-rectangular.target` and `head-fat-decr.target`, retained at the same official commit and byte-verified against its Git blob identities. `../refine_face_character.py` applies these as local head shape keys at 0.65, 0.30 and 0.22, subtracting the source head-joint translation and blending into the fitted neck. The source filenames describe the upstream morph controls; this is an authored fictional character, not a scan or likeness of a particular person.
