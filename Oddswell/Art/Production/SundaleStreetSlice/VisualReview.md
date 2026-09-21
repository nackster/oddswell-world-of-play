# Character and landscape development review

The first OddsWell picture remains the target, and the visual-quality goal remains **active**. The original starting point is `76ccb76`; preceding character/landscape checkpoints are `ae5144c` and `ab7ec49`.

Reference picture:

![Accepted first reference](../../Reviews/OddsWellStreetIdentityCandidate/OddsWell_Visual_Direction_Concept.png)

Current native gameplay render:

![Native scene comparison](StreetSlice_Gameplay.png)

## Refinement after the first character checkpoint

On September 21, the owner resumed the saved broadleaf checkpoint. A first hip-fold preview produced narrow, stripe-like marks and was rejected. The retained pass uses broader, lower-amplitude shorts folds and a slightly stronger jacket-body fold. Gameplay plus five inspection views were rebuilt from the same editable scene. In the close-ups the result is a modest improvement, not a resolved cloth simulation: the shorts still have a stiff hip/crotch shape and the jacket shoulder-to-sleeve transition still needs art direction.

The latest landscape pass replaces the fine compound foliage with adapted broad-leaf geometry and raises the woody branching before leaf emission. A single distribution pass over the combined branch masks reduces hanging, crowded patches. The court view reveals the far basket and more of the arena. Foreground shrubs now have woody stems and overlapping clusters from the same leaf family, with darker understory material settings. The retained Island Tree 01 source and seven leaf/twig maps are documented alongside the original Jacaranda source.

The jacket torso and posed sleeves now form one continuous surface. Smoothly interpolated tailoring profiles reduce angular shoulder and hip bands; the teal panels and seams are fitted to that surface. Hidden inner-sleeve panel vertices are removed before fitting so they cannot appear as teal slivers on the front shoulder. The cuff profile follows the sleeve, and compression folds fade into the knit bands.

The shorts have open, thickened hems after their volume union. Native close-ups also exposed insufficient thigh coverage inside the hem; the retained anatomical surface now extends farther under the shorts and fits within their opening. The exposed calves retain their volume. These changes address gaps and intersections, not only shading.

Thirteen mature trees use three shared growth variants with different leaf seeds, densities and crown proportions. The foreground hero stays fixed for composition; upright and spreading forms vary the street and forecourt. Stone and fired paving gain sparse pores and fine mineral relief, while oak fibers follow the seat slats and shelves. At gameplay distance these material changes are subtle; they do not replace the reference's richer wear and photographic detail.

## Changes visible in the native scene

- **Character:** clothing surfaces now include localized folds, matching seams, cuffs, a continuous pair of shorts, front zipper/welt pockets, heel details and a teal yoke extending onto the sleeves. Calves retain their volume, hands have a more relaxed shape, and the stance foot touches the promenade. A continuous faceless head surface avoids the anatomical source’s eye and mouth openings.
- **Landscape:** shared mature tree geometry has more detailed branching and textured foliage, with adjusted growth density, proportions and color. The foreground tree moves behind the character; lower planting combines shrubs, grasses, flowers, groundcover, soil and fallen leaves. Planted stone seats and forecourt gardens connect the court to the arena.
- **Light and depth:** the arena moves farther back, shops have deeper lit interiors, and a photographed sky plus warm sunlight and reflected light replace the plain sky and flatter illumination. Tree shadows break up the promenade. Court paint remains flat against the play surface.

## Defects caught during review

Native previews and close-ups exposed sparse foliage, overly regular cloth folds, thin calves, floating feet, open shoe heels, a collar gap, separate shorts sections, floating roof planting, shoulder openings and distorted facial smoothing. These were corrected in the editable source and re-rendered. Raw modeling and render logs remain under the project’s ignored `client/OddsWell/Saved/NextTen20260912` work folder; the delivery manifest identifies the retained outputs. Working preview images are overwritten as the scene develops.

The tree comparison led to adapting CC0 native branching and leaf geometry instead of retaining the original radial-branch approximation. Source authorship is recorded in the README and retained manifests. Shrub stems and placement, grasses, garments, architecture and scene composition remain locally authored; shrub leaf geometry now shares the retained broad-leaf source.

## What remains below the reference

The reference has more natural garment drape, richer architectural variation and shop contents, subtler weathering, a more composed mixture of plants, and a more photographic finish. The current character is a static model and the scene is deliberately an offline art study. A successful render and geometric checks do not close those visual gaps.

The next visible priorities are natural cloth drape around the hips and shoulder seam, varied facade/window arrangements, more convincing retail contents, and less uniformly clean foreground surfaces. Paving scale is established, but wear and small color changes still need refinement. Broad-leaf geometry is now present; crown composition, color balance and selective pruning still need art direction against the reference.

The higher trunks materially open the court view, but some low edge branches remain. Selective court-facing pruning and measured physical clearances are still required before treating this as production planting.

Next iterations should focus on those remaining visible differences before spending effort on engine import. LODs, collision, baked game materials, rigging and performance remain separate requirements. No runtime code, production map or tested package was changed by this art pass.
