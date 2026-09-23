# Shorts pattern review — September 23, 2026

The [front](Shorts_Close_Front.png) and [rear](Shorts_Close_Rear.png) are native 48-sample Cycles renders from posed candidate SHA-256 `001FB31C1C206A4C72245873E44850718CCC5F70CB2D699888FB0E28F727DBEA`. `render_shorts_close.py` reproduces the cameras without changing the Blend. The source visual candidate and the original street-slice scene remain unchanged.

The upper front is a broad, nearly cylindrical panel between the jacket hem and crotch. At the rear, the seat volume transitions abruptly into the leg and the pockets are only curve outlines. The left rear inseam gathers into a broad cluster; the hems show uneven compression. These shapes are visible even though the existing technical check reports a connected garment, three openings, and positive sampled thigh clearance.

The control mesh uses 17 eighty-point hip rings, 36 eighty-point rings for each leg, and a shared saddle. In `develop_character_landscape.py`, the leg-to-hip join uses `blend=t**4`; most of that transition is concentrated near the top. This geometry, followed by cloth settling and smoothing, is the likely source of the flat upper panel and concentrated lower folds. That causal diagnosis needs confirmation with a rebuilt pattern render.

Three isolated studies were rejected. A 14 mm upper-hip taper exposed the jacket waistband and buried pocket seams. Projected cloth pocket panels improved the outline but pinched over the right seat fold; the last sampled surface still dipped about 0.045 mm into the shorts at one face center. A front fly facing and diagonal pocket openings read as rigid applied strips. None changed the retained Blender candidate.

The next modeling pass should revise the hip-to-leg and saddle transition in the actual garment control mesh, rerun the native cloth study, and compare front/rear close-ups before rebuilding pocket and fly construction. Passing geometry checks alone will not close the human-realism goal.

Follow-up: a simple `t**2` transition increased the central rear peak and was rejected. A separate 44 mm tapered gusset connected the two leg panels across a real cloth strip instead of one center line. The resulting native [candidate](../ShortsGussetCandidate/README.md) passed a fresh static geometry check and gives a somewhat rounder rear, but still leaves a broad upper front and concentrated left inseam fold. It is retained as a topology study, not a replacement for the verified source or a human-realism acceptance.
