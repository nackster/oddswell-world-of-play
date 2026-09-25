# Upper shorts and jacket-waist rebuild

The previous editable art source is `PocketPanelCandidate/PocketPanel.blend` (SHA-256 `F4C098DFC315FF9AF49AC3F8ABE15E60D32AF28A062F7E01F5714A24B11A9052`). Its rear pockets and hems are worth retaining, but the upper shorts remain a smooth annular hip shell joined to two leg tubes through a narrow saddle. The source construction is visible in `develop_character_landscape.py`: 17 eighty-point hip rings, two eighty-point leg rings, and a 44 mm tapered gusset. The source-derived pelvic collision trial does not fit this posed shell closely enough to serve as a new cloth target without alignment work.

The next retained checkpoint is `WaistPatternCandidate/WaistPattern.blend`: a coupled waist/rib/jacket contour that reduces the upper shorts circumference to 0.910 m without changing the lower hip substantially. It improves the adult waist-to-hip silhouette but does not replace the annular upper shell or saddle. Use this newer scene as the source for the remaining pattern reconstruction.

The later `PanelBalanceCandidate/PanelBalance.blend` is the current fit source. Its measured panel-path audit (`CrewCutCandidate/PatternLayout.json`) found 0.5499 m front arc and 0.5163 m rear arc on the lower upper-shorts ring. A bounded front-to-rear cloth-depth redistribution brings those paths to 0.5340/0.5284 m without opening the waist or moving the leg hems. Native review shows a modest silhouette gain; the 17-ring annular topology and 39-point saddle bridge still require replacement as a coupled pattern. The first transition trial opened dark triangles beneath the jacket band and was rejected; the retained transition ends before that band.

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

The next modeling pass should replace the annular upper front/back shell and its saddle junction with pattern-controlled panels shaped around a *fitted* walking pelvis and thigh support. Retain the two leg openings, current hems and pockets; fit their cloth panels and stitches to the new surface. Build front/rear panels, side and center construction, and the saddle as one continuous cloth pattern before adding decorative seams. Fit the ribbed band and jacket hem to the resulting waist in the same pass. Then review close front, rear, three-quarter and profile renders alongside the gameplay camera. Reject self-crossing crotch folds, exposed dark gaps, detached pockets/seams, thigh intersections, and a hem that rides up. Keep the human-realism goal active until the full figure matches the original reference visually; technical checks alone cannot accept it.
