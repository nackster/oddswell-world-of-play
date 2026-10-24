# Torso and posed cotton development

Editable offline OddsWell human study derived from `UpperHipHandCandidate/UpperDrape.blend` (SHA-256 `90af187cf9cfa558f4d06a4b7398d02a8097991309e06789dbf61b0ebc36afeb`).

The new Basis-relative `Natural ribcage to waist transition` keys taper the retained body support and jacket gradually through the waist. They affect 3,760 body and 1,391 jacket controls, with maximum offsets of 10 and 12 mm. Body/contact and jacket/sewing-cage copies continue sharing their respective meshes. Original controls, previous keys, UVs, skinning and walking curves remain.

The original shorts and midsurface retain their full pose, clearance, compression and fold construction. A new Geometry Nodes stage before subdivision fits front cotton toward the actual posed leg and registered pelvic surfaces, using a nominal 12 mm allowance divided by the local hit-normal Y component. It caps inward depth at 40 mm, gates front-facing hits and fades across 1,710 weighted controls. This is authored geometric fitting, not physical cloth simulation or a measured clearance guarantee. Six local smoothing passes round its transition. Geodesic fades protect open waist and hem boundaries.

Lateral ray projection and a subsequent constant lateral taper were rejected: the former introduced clothing self-intersections, the latter exposed the legs. Neither is retained in this model. The torso's existing male anatomy target is preserved rather than applied again.

Run the recipes with Blender 4.5.5 LTS: `build.py`, `audit.py`, `probe.py -- --all`, `followers.py`, `render.py -- --focus --skip-gameplay --isolated --cpu`, `render-walk.py -- --preview`, and `render-game.py`. Recipes locate the repository from their location and require the retained source and existing licensed packed maps. CPU rendering avoids the GPU failure encountered in earlier work.

Read the JSON reports and `WholeFigureReview.md` for the exact validation scope. This is an intermediate human development checkpoint. Visual acceptance remains open. The model is not an imported runtime asset, complete body-contact certification, photographic human, or finished Sundale scene.
