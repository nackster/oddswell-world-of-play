# Upper shorts and jacket-waist rebuild

The previous editable art source is `PocketPanelCandidate/PocketPanel.blend` (SHA-256 `F4C098DFC315FF9AF49AC3F8ABE15E60D32AF28A062F7E01F5714A24B11A9052`). Its rear pockets and hems are worth retaining, but the upper shorts remain a smooth annular hip shell joined to two leg tubes. The original `develop_character_landscape.py` used a shared saddle centerline; `HumanBodyPoseCandidate/ShortsGussetCandidate/` later replaced it with a connected 39-station paired gusset. The historical 44 mm design label is not its current evaluated width: a corrected audit measures a 21.5 mm maximum span in the later `PanelBalance` source. The source-derived pelvic collision trial does not fit this posed shell closely enough to serve as a new cloth target without alignment work.

The next retained checkpoint is `WaistPatternCandidate/WaistPattern.blend`: a coupled waist/rib/jacket contour that reduces the upper shorts circumference to 0.910 m without changing the lower hip substantially. It improves the adult waist-to-hip silhouette but does not replace the annular upper shell or saddle. Use this newer scene as the source for the remaining pattern reconstruction.

The later `PanelBalanceCandidate/PanelBalance.blend` corrected front/rear depth: its measured panel-path audit (`CrewCutCandidate/PatternLayout.json`) found 0.5499 m front arc and 0.5163 m rear arc on the lower upper-shorts ring, then brought those paths to 0.5340/0.5284 m without opening the waist or moving the leg hems. The first transition trial opened dark triangles beneath the jacket band and was rejected; the retained transition ends before that band.

`GussetWidthCandidate/GussetWidth.blend` is now the current fit source. It widens the **existing** paired gusset to a measured 47.3 mm maximum and blends the adjustment through the upper legs. Front/rear close views show a broader saddle without a new hole, but the change is minor in full-body and gameplay views. The 17-ring upper shell and cloth drape still need a true front/back panel rebuild joined to the fitted pelvis and thigh support.

September 24 evidence from native Cycles studies, retained in ignored `client/OddsWell/Saved/NextTen20260912/`:

| Study | Maximum change | Visual decision |
| --- | ---: | --- |
| Coordinated waist/hem counter-tilt | 6.0 mm | Too subtle to improve the broad seat; leave unpromoted. |
| Broad upper cotton ease | 4.8 mm | Imperceptible in matched rear/front close views. |
| Strong upper cotton ease | 14.3 mm | Reads as an applied diagonal ridge above the pocket. |
| Narrow saddle recess | 16.0 mm | Pinches the connected saddle into exposed protruding folds; reject. |
| Broad rear seat fit | 11.8 mm | Slightly smooths the arch but preserves the flat, blocky upper silhouette. |
| Paired rear-seat contour | 21.0 mm | Adds a padded profile without correcting the annular shell or saddle; reject. |

A source-derived pelvis raycast audit also found widely varying sampled rear offsets (about 2–115 mm across the upper rings) and negative front offsets down to about -43 mm. Those values depend on an incomplete posed proxy and are **not** continuous collision-clearance proof. They are enough to rule out blindly reusing that proxy for another cotton settle.

The next modeling pass should replace the annular upper front/back shell with pattern-controlled panels shaped around a *fitted* walking pelvis and thigh support, integrating the existing gusset with those panels. Retain the two leg openings, current hems and pockets; fit their cloth panels and stitches to the new surface. Build front/rear panels, side and center construction, and the saddle as one continuous cloth pattern before adding decorative seams. Fit the ribbed band and jacket hem to the resulting waist in the same pass. Then review close front, rear, three-quarter and profile renders alongside the gameplay camera. Reject self-crossing crotch folds, exposed dark gaps, detached pockets/seams, thigh intersections, and a hem that rides up. Keep the human-realism goal active until the full figure matches the original reference visually; technical checks alone cannot accept it.
