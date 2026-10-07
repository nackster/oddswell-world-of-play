# Anatomical shoulder fit and moving cloth finish

`ShoulderChest.blend` continues `TorsoFlowCandidate/TorsoFlow.blend`, SHA-256 `3d4b732f51a6d2b79a0ed18a9b4f94b67c843cefd1b14a968bc62bf4591f4dc3`.

One shared editable shoulder key reduces excess ease over the actual rest anatomy. It changes 196 jacket controls by at most 27.406 mm while retaining the original collar boundary and all older keys. The visible jacket and refined sewing cage share a derived mesh; historical cages and source control data remain intact. The earlier underarm weighting and thickness clamp remain in use.

Lowering the shoulders exposed neckline contacts introduced by subdivision between the fixed collar edge and lower neighboring controls. A local outside-skin constraint after subdivision corrects that transition before the fabric shell. This preserves the boundary controls rather than raising the shoulder peaks again. The nominal shell remains 1.2 mm.

Derived UVs for the six sewn panels use area-weighted rest derivatives to scale the existing licensed 266 mm terlenka maps. The original UV atlas, image bytes and shaders remain intact. A jacket-only shader copy gives a modestly lighter slate dye and matte fiber response. Two restrained front-quarter tension ridges and short zipper/waist gathers add outward native relief after anatomical clearance and before subdivision; garment and detail cage share the same field. These are authored tailoring, not a physical cloth simulation.

Rebuild with Blender 4.5.5 LTS: run `build.py`, `cloth_folds.py`, `neck_clearance.py`, then `audit.py` and `render.py`, using `--python-exit-code 1 --python`. `render.py -- --preview` produces 24 native frames for a two-second 12 fps preview. Existing custody/render helpers remain in `HipSeatMotionCandidate` and `HandArticulationCandidate`.

The cold audit preserves original controls/edges/old UVs/old keys, licensed packed maps and rig rest/six poses. It compares unedited support, shorts, legs and footwear geometry in six poses, checks the added UVs, and records complete jacket shell/self and jacket/body-support intersections across all 49 authored integer frames. The two visible front welt details have sampled contact and edge bounds compared with six source poses. Hidden historical stitches are not counted as a visible-seam pass. Remaining body contacts are reported explicitly. Read `WholeFigureReview.md` with the full-body, close and gameplay images; this remains an offline development checkpoint without runtime or beta credit.
