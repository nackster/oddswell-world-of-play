# Front/rear shorts panel balance

`PanelBalance.blend` follows `../CrewCutCandidate/CrewCut.blend` (SHA-256 `974ADD328315034C3DD09C6C4393B825E47FFC994315366552446A313AE89EE5`). The saved editable candidate has SHA-256 `A4790ADF03B98752780F2002B4033BFDF09282849C8D5D0ADD4E2D4BAF458EB2`.

`../CrewCutCandidate/PatternLayout.json` maps the retained 17 upper 80-point rings to front and rear control paths, side boundaries, and 39 paired gusset stations. At the lower upper-shorts ring the previous front/rear arc lengths were 0.5499/0.5163 m. This candidate moves at most 13.3 mm of existing cloth depth from front toward back through the lower hip, yielding 0.5340/0.5284 m. The 0.9103 m upper waist ring, jacket band, and leg hems retain their fit. Both sewn back pockets and stitches were refitted to the changed surface.

Native front, rear, profile, and full-rear renders were reviewed. An initial upper transition exposed dark triangles beneath the jacket; the retained version brings that transition to zero before the waistband and removes the gaps. The visible gain is modest, especially at full-body scale. `verify_panel_balance.py` passes the saved arc, waist, and pocket-clearance checks; cold `verify_scene.py --draft` also passes.

This is a redistribution of the existing connected garment, **not** the sewn front/back panel and saddle rebuild. The central crotch folds and seat drape still read synthetic. The face/skin, jacket tailoring, shoe/ankle detail, and whole-reference acceptance remain open. Offline Blender art does not establish runtime character readiness.
