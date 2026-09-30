# Anatomical neckline and chest connection

This native Blender continuation of [NeckSkinUVCandidate](../NeckSkinUVCandidate/README.md) replaces the floating collar-to-jacket ledge with a coordinated neckline, knit stand, facing and fastening fitted to the retained anatomy. It preserves the existing waist definition, pelvis/chest counter-rotation, shorts and slate/teal OddsWell identity. This checkpoint changes the upper garment; it does not add a walking animation or a new hip deformation.

The original flat facing was detached from the rebuilt jacket. A facing-only refit looked cleaner but entered the internal anatomical torso support by 23 mm, so it was rejected. Raising individual collar points to that support produced an uneven stand and was also rejected. The retained version uses a level neckline above the actual support, fitted radially to the visible neck. Every row of the 31.013 mm stand follows the skin section at its own height, rather than spanning a straight line between its ends. The neckline height is 1.478451 m in scene space. Original neck attachments intentionally move: maximum jacket anchor motion 65.587 mm and collar bottom motion 61.851 mm. The waist and cuff attachments remain fixed.

The shoulder/chest transition receives a graded displacement and evaluated-surface anatomical fit. Sewn raglan edges, yoke, welts and fastening follow the changed garment. The zipper tape, teeth, slider and pull extend through the new stand. The three-ring facing follows the actual render-resolution garment boundaries with less than 0.361 mm rim error, replacing the exposed ledge.

## Editable source and native review

[AnatomicalNeckline.blend](AnatomicalNeckline.blend) retains `Original low jacket neckline`, `Original low collar attachment` and `Original floating collar facing` keys plus their before-coordinate attributes. Each key restores its original source controls exactly when activated alone with the other restore keys at zero. Earlier neck, tall-collar and shoulder restoration controls remain. The 244-part `Body flow | stance blend` still drives the previous torso/hip stance. The original six-panel jacket draft/fit/gravity coordinates and 60-frame settle are retained; the new neckline is an authored fit after that settle, not a fresh simulation.

- [Full rear](AnatomicalNeckline_Rear.png)
- [Full front](AnatomicalNeckline_Front.png)
- [Profile](AnatomicalNeckline_Profile.png)
- [Torso front](AnatomicalNeckline_TorsoFront.png)
- [Neck front](AnatomicalNeckline_NeckFront.png)
- [Neck rear](AnatomicalNeckline_NeckRear.png)
- [Gameplay scene](AnatomicalNeckline_Gameplay.png)

These native Cycles renders use 12 samples for figure/close views and 24 for gameplay. Front and rear show a continuous attachment and a cleaner collar-to-chest transition. Full-figure review still finds broad synthetic chest/underarm folds, a restrained but stiff walking gesture, generic facial presentation and smooth clothing/footwear. [WholeFigureReview.md](WholeFigureReview.md) records the next visible work against the original concept. These are review images, not photographic-realism acceptance.

## Checks and reproduction

[build.py](build.py) opens the hash-pinned source and executes [fit_neckline.py](fit_neckline.py); [render.py](render.py) produces all seven views. Run with Blender 4.5.5 LTS and `--python-exit-code 1 --python`. The source SHA-256 is `D8F4CA3DCAEFE622247EB24191ACFAE68F9F3E5EAC1642EE5404D51ECBE6000B`. The delivered scene preserves the reviewed native study with a nonvisual history repair: original `Collision fit` simulation coordinates remain intact, while `Anatomical attachment targets` stores the authored neckline. [Fit-history-audit.json](Fit-history-audit.json) proves exact geometry, transforms, shape keys, UVs and packed maps before/after that separation. Builder output paths adapt to this folder and retain both records directly. No new assets, textures or dependencies are installed.

[audit.py](audit.py) compares the delivered scene to that source, allowing only the coupled upper-garment/trim changes. It verifies exact preservation of 894 source UV layers and all 31 packed licensed maps, unchanged remaining geometry, positive facing support clearance, zero nonadjacent facing intersections, exact original-attachment restoration and all 244 stance drivers. [AnatomicalNeckline-audit.json](AnatomicalNeckline-audit.json) records the results. [audit_collar.py](audit_collar.py) checks the whole stand at render subdivision; [Collar-audit.json](Collar-audit.json) reports zero midsurface/shell intersections, positive closed fabric volume and minimum inner-shell skin clearance 3.486 mm. The previous fixed-bottom invariant is replaced by measured authored movement and exact restoration because this pass deliberately relocates the neckline.

[audit_jacket.py](audit_jacket.py) checks the entire jacket sheet and thick shell; [Jacket-audit.json](Jacket-audit.json) reports zero nonadjacent intersections, positive closed shell volume, fixed current attachment targets and 96,716 checked free-cloth points with minimum body clearance 3.648 mm. These are static checks of the saved pose. [cold-check.json](cold-check.json) records the independent shared scene check, including retained garment detail. [Delivery-manifest.json](Delivery-manifest.json) binds the delivered source, scripts, reports, renders and source dependencies to SHA-256 hashes.

The full human-realism goal remains active. Continue broad garment/pose refinement and whole-reference review, then architecture/retail variety, selective layered planting and warm scene lighting. Baking, a compatible rigged derivative, LODs and controlled engine validation follow the existing acceptance gates. The separate starter-outfit walk review and stopped export/import preparation remain authoritative. This offline checkpoint grants no runtime, final-art, physical first-hour, Phase 1L exit or beta-exit credit.
