# Cotton tension over the anatomical stance

This native Blender continuation of [AnatomicalNecklineCandidate](../AnatomicalNecklineCandidate/README.md) develops actual sewn-cloth tension over the retained torso/hip stance. An 80-frame cotton study transfers the authored neck and shoulder fit into the original six-panel rest pattern, then settles against the anatomical support with the current neckline, waist and cuffs held. The fitted result moves controls by up to 20.341 mm. The slate/teal OddsWell identity, head, hands, hips, shorts, legs, footwear and street geometry remain unchanged.

The raw solver result moved controls by up to 20.870 mm. Its midsurface had no detected self-intersections, but the 1.2 mm fabric shell initially crossed at tight underarm creases. Five bounded, measured crease regions receive local rounding, followed by render-resolution body fitting. The accepted sheet and shell have zero detected nonadjacent intersection pairs, with 96,716 checked free-cloth points clearing the body by at least 3.670 mm. Raglan stitches, yoke, welts, zipper tape/teeth and the collar facing follow the changed surface. This is an authored finish after a native settle, not an untouched simulation output.

## Source and review

[CottonTension.blend](CottonTension.blend) retains separate before, transferred sewn-rest and raw gravity attributes. `Original pre-settle jacket` and `Original pre-settle collar facing` restore the immediate source controls exactly when activated alone. `Raw post-neckline cotton settle` exposes the solver output separately. Earlier source restoration keys remain. All four original simulation/attachment attributes remain byte-exact; the older 60-frame drape record is preserved separately from this new 80-frame study. The 244-part torso/hip stance control remains editable.

- [Torso front](CottonTension_TorsoFront.png)
- [Full front](CottonTension_Front.png)
- [Full rear](CottonTension_Rear.png)
- [Profile](CottonTension_Profile.png)
- [Neck front](CottonTension_NeckFront.png)
- [Neck rear](CottonTension_NeckRear.png)
- [Gameplay scene](CottonTension_Gameplay.png)

The native Cycles views use 12 samples for figure/close views and 24 for gameplay. They show a modest improvement in shoulder/sleeve tension and diagonal folds while preserving the waist/hip silhouette and collar attachment. Broad cloth finish, generic facial presentation and hand/whole-body gesture remain below the requested very-real target. [WholeFigureReview.md](WholeFigureReview.md) directs the next larger body work toward coordinated walking development, followed by whole-reference review and the street roadmap. These renders do not establish a walking animation or final human acceptance.

## Reproduction and evidence

[build.py](build.py) opens source SHA-256 `C72E84C4033D6A8F86C89BECD7A1BB2736460728A32132ADEEE57C1F17932CA3`. It reuses the existing body-flow inverse, evaluated cloth fitter, sewn-edge tracing and facing construction. The native cotton settings are quality 10, mass 0.24 kg, tension/compression/shear stiffness 32/16/12, bending 0.4, 1 mm body margin, 2 mm cloth margin and 3 mm self-collision margin. The original body collision margin is restored after simulation. [drape-bake.json](drape-bake.json) retains the source/rest/settings-bound 80-frame raw coordinates; matching inputs reuse this bake, while changed inputs trigger a fresh native solve. [render.py](render.py) produces the seven review views. Run with Blender 4.5.5 LTS and `--python-exit-code 1 --python`; no new dependency is installed.

[audit.py](audit.py) compares the saved candidate with its immediate source. Only the jacket, facing and fitted trim may change. It verifies all 894 original UV layers and all 31 packed licensed maps exactly, source geometry preservation elsewhere, original simulation/attachment attributes, exact immediate-source restoration, current facing boundary/contact fit and all 244 stance drivers. [CottonTension-audit.json](CottonTension-audit.json) records those results. [audit_jacket.py](audit_jacket.py) screens the complete sheet and thick shell at render subdivision and verifies topology, four openings, fixed attachments, anatomical fit and positive closed fabric volume; [Jacket-audit.json](Jacket-audit.json) records the results. [cold-check.json](cold-check.json) is the independent shared scene check. The delivered native scene is byte-identical to the checked and rendered study. [Delivery-manifest.json](Delivery-manifest.json) binds the actual delivered scene, scripts, cache, reports, renders and source dependencies to hashes. No assets or textures are replaced.

The foot review is corrected: the immediate source already has a flat planted right sole and a left heel raised 71.511 mm relative to its toe. This pass preserves that geometry. The former profile impression of two flat feet was too weak to support that diagnosis. Whole-body stiffness remains visible and needs a coordinated native walking study rather than another isolated heel lift.

The full human/landscape goal remains active. Continue pelvis/knee/arm/hand walking gesture and garment response together, then facial/material refinement and whole-reference review. Architectural/retail variety, layered planting and warm street composition remain subsequent scene work. Baking, a compatible rigged derivative, LODs and controlled engine validation follow the established gates. Existing starter-outfit walk acceptance and stopped export/import preparation remain authoritative; this offline study grants no runtime, final-art, physical first-hour, Phase 1L exit or beta-exit credit.
