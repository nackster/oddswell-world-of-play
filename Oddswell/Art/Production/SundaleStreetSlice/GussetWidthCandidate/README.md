# Existing gusset width and leg-transition study

`GussetWidth.blend` follows `../PanelBalanceCandidate/PanelBalance.blend` (SHA-256 `A4790ADF03B98752780F2002B4033BFDF09282849C8D5D0ADD4E2D4BAF458EB2`). The saved editable study has SHA-256 `C9420581B4DFDF22E4E2D398F38A6A9C186AFF92D02D71BF31352E2B70B77554`.

The retained shorts **already had** a connected, 39-station paired gusset. A corrected mesh audit measures its actual maximum span at 21.5 mm in the predecessor scene, although an older scene property records a nominal 44 mm design width. This study adds up to 15 mm on each side of that strip and blends the change through the upper leg controls; the saved maximum span is 47.3 mm. The waist ring, first leg rings, back-pocket panels and jacket are unchanged.

Native front, rear, profile, full-rear and gameplay renders are retained. The saddle looks broader and less pinched in the close front/rear views without a new visible hole; the improvement at full-body and gameplay scale is small. `verify_gusset.py` confirms the width change, unchanged waist/leg-opening controls, one manifold surface with the same three openings, and unchanged vertex/face counts. Cold `verify_scene.py --draft` passes.

This is **not** a new gusset or completed front/back shorts pattern. The upper shorts remain a broad annular shell, and the seat/crotch folds still look synthetic beside the original reference. The active human-realism goal also requires more convincing face/skin, jacket folds and footwear before scene realism can be accepted. This remains offline Blender art, not a runtime-ready character.
