# Character and landscape development review

The first OddsWell picture remains the target, and the visual-quality goal remains **active**. The original starting point is `76ccb76`; preceding character/landscape checkpoints are `ae5144c` and `ab7ec49`.

Reference picture:

![Accepted first reference](../../Reviews/OddsWellStreetIdentityCandidate/OddsWell_Visual_Direction_Concept.png)

Current native gameplay render:

![Native scene comparison](StreetSlice_Gameplay.png)

## Current reference refinement

Continuing from human-face checkpoint `f46ac3b`, the upper jacket and arms are slimmer together, bringing the silhouette closer to the original reference. The slate fabric has less broad sheen, the jaw is subtly wider, and the shorts have localized diagonal gathers with a shallower rear-seat crease. Original anatomical UVs now carry a retained CC0 MakeHuman skin map across the head, hands and legs. Native close-ups show lip, cheek, ear and scalp variation; eye surface relief was reduced and reflections refined. The scene packs 25 maps and retains eight native review views.

The original procedural tint was still too uniform in the portraits. The source UV map adds surface variation without changing the original texture bytes. Full-figure and portrait review checked facial registration, neck/collar fit, cuffs and exposed limbs. Early jacket sheen was too broad and was reduced before delivery. These are static modeled creases and shaded skin; facial expression, eyelid refinement, individual identity and natural cloth drape remain open.

## Refinement after the first character checkpoint

The preceding owner request specifically asked for a more human character. From `c255dd5`, the authored oval head was replaced with the retained MakeHuman skull, face, ears and neck. Paired fitted eyes have separate curved irises and pupils; finer brow strands follow the evaluated face, with restrained cheek/lip tint and skin shading. The first native portraits exposed source shoulder fragments protruding through the collar. A planar neck crop and fitted skirt beneath the collar removed those fragments. A second brow draft was too coarse and high, so its strands were made finer and repositioned. Front and profile portraits are now part of the eight-view review set.

The result reads as human anatomy rather than a featureless mannequin, but remains a neutral static face study. Skin variation, the eyes, expression and individual character identity still need refinement before final approval. The front/profile images are native scene renders with the same outdoor lighting, not generated portraits.

![Human face study](StreetSlice_Head_Front.png)

![Profile and collar fit](StreetSlice_Head_Profile.png)

On September 21, the owner resumed the saved broadleaf checkpoint. A first hip-fold preview produced narrow, stripe-like marks and was rejected. Checkpoint `8c868ec` retained broader, lower-amplitude shorts folds and a slightly stronger jacket-body fold.

The next pass replaces overlapping, voxel-unioned shorts volumes with a single surface sharing the hip circumference and curved inseam. The first transition produced a pronounced rear shelf; close-up review led to a gradual blend over the full leg height and reduced pre-pose offsets. Pocket seams were fitted to the evaluated cloth. The retained rear and three-quarter views show a smoother hip-to-leg transition and less bulky crotch. Sleeve caps are narrower and the upper shoulder join is locally relaxed. These are visible modeling improvements, but the cloth still reads as a static sculpt and the rear inseam needs further art direction.

Civic limestone now combines lower-contrast grain with broken horizontal sediment variation over its existing pores. The change is deliberately subtle. It is not a substitute for object-specific wear, edge treatment or more varied architecture.

The latest landscape pass replaces the fine compound foliage with adapted broad-leaf geometry and raises the woody branching before leaf emission. A single distribution pass over the combined branch masks reduces hanging, crowded patches. The court view reveals the far basket and more of the arena. Foreground shrubs now have woody stems and overlapping clusters from the same leaf family, with darker understory material settings. The retained Island Tree 01 source and seven leaf/twig maps are documented alongside the original Jacaranda source.

The jacket torso and posed sleeves now form one continuous surface. Smoothly interpolated tailoring profiles reduce angular shoulder and hip bands; the teal panels and seams are fitted to that surface. Hidden inner-sleeve panel vertices are removed before fitting so they cannot appear as teal slivers on the front shoulder. The cuff profile follows the sleeve, and compression folds fade into the knit bands.

The shorts have open, thickened hems and an open waist, with subdivision over the continuous tailored surface. The cold-open check counts the three boundary loops and rejects non-manifold edges. Earlier native close-ups exposed insufficient thigh coverage inside the hem; the retained anatomical surface extends farther under the shorts and fits within their opening. The exposed calves retain their volume. These changes address gaps and intersections, not only shading.

Thirteen mature trees use three shared growth variants with different leaf seeds, densities and crown proportions. The foreground hero stays fixed for composition; upright and spreading forms vary the street and forecourt. Stone and fired paving gain sparse pores and fine mineral relief, while oak fibers follow the seat slats and shelves. At gameplay distance these material changes are subtle; they do not replace the reference's richer wear and photographic detail.

## Changes visible in the native scene

- **Character:** clothing surfaces now include localized folds, matching seams, cuffs, a continuous pair of shorts, front zipper/welt pockets, heel details and a teal yoke extending onto the sleeves. Calves retain their volume, hands have a more relaxed shape, and the stance foot touches the promenade. The source-derived human head has a closed fitted neck, facial anatomy, paired eyes and fine brows.
- **Landscape:** shared mature tree geometry has more detailed branching and textured foliage, with adjusted growth density, proportions and color. The foreground tree moves behind the character; lower planting combines shrubs, grasses, flowers, groundcover, soil and fallen leaves. Planted stone seats and forecourt gardens connect the court to the arena.
- **Light and depth:** the arena moves farther back, shops have deeper lit interiors, and a photographed sky plus warm sunlight and reflected light replace the plain sky and flatter illumination. Tree shadows break up the promenade. Court paint remains flat against the play surface.

## Defects caught during review

Native previews and close-ups exposed sparse foliage, overly regular cloth folds, thin calves, floating feet, open shoe heels, a collar gap, separate shorts sections, floating roof planting, shoulder openings and distorted facial smoothing. These were corrected in the editable source and re-rendered. Raw modeling and render logs remain under the project’s ignored `client/OddsWell/Saved/NextTen20260912` work folder; the delivery manifest identifies the retained outputs. Working preview images are overwritten as the scene develops.

The tree comparison led to adapting CC0 native branching and leaf geometry instead of retaining the original radial-branch approximation. Source authorship is recorded in the README and retained manifests. Shrub stems and placement, grasses, garments, architecture and scene composition remain locally authored; shrub leaf geometry now shares the retained broad-leaf source.

## What remains below the reference

The reference has more natural garment drape, richer architectural variation and shop contents, subtler weathering, a more composed mixture of plants, and a more photographic finish. The current character is a static model and the scene is deliberately an offline art study. A successful render and geometric checks do not close those visual gaps.

The next visible priorities are eyelid and eye detail, expression, a more relaxed hand pose, cloth behavior at the rear inseam and shoulder seam, varied facade/window arrangements, more convincing retail contents, and less uniformly clean foreground surfaces. Paving scale is established, but wear and small color changes still need refinement. Broad-leaf geometry is now present; crown composition, color balance and selective pruning still need art direction against the reference.

The higher trunks materially open the court view, but some low edge branches remain. Selective court-facing pruning and measured physical clearances are still required before treating this as production planting.

Next iterations should focus on those remaining visible differences before spending effort on engine import. LODs, collision, baked game materials, rigging and performance remain separate requirements. No runtime code, production map or tested package was changed by this art pass.
