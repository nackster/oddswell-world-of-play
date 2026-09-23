# Human body pose candidate

This is an editable visual candidate built from the retained Sundale street-slice scene, not a replacement for its neutral-bind or walk evidence. The source Blend remains SHA-256 `0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127`.

Run `build_pose_candidate.py` with Blender 4.5.5 in the parent scene. It moves 238 upper-body character objects together, including head shape keys, eyes, hair, jacket fit/drape layers, trim, cuffs, hands and nails. The pose uses a 50 mm forward lean, 25 mm shift toward the planted stance, 3.5° shoulder yaw, 75 mm opposing arm swing, 28 mm shoulder taper and 18 mm outer-shoulder drop. Legs, shorts, calf hair and footwear retain their source coordinates and foot contact. The resulting native `OddsWell_Human_Body_Pose_Candidate.blend` includes the original packed maps and ten cameras.

The rear and front PNGs are direct 64-sample Cycles renders of that candidate. The rear shows a narrower shoulder line and some torso weight over the planted foot. The front still shows an overly smooth jacket and broad, flat shorts around the seat and crotch. The face and hands need more natural variation. This candidate is a checkpoint for visual review, not final human realism or an animated/runtime asset.

The parent `verify_scene.py` accepts the pose-aware head center and rotated eye ray while retaining the original scene checks. A fresh cold reopen of this candidate passed with ten cameras, 31 packed maps, 3.5 mm minimum shorts-to-thigh clearance, 4.5 mm minimum free-jacket-to-support clearance, and the planted right sole at 51 mm. These tests establish geometry continuity, not visual acceptance. The next visible pass should reshape the shorts seat/crotch and jacket shoulder/sleeve folds, then review front, rear and gameplay scale against the first reference.

`PatternReview/ShortsPatternReview.md` retains close front/rear native views and the rejected hip, pocket and fly studies. It identifies the shared hip-to-leg saddle as the next garment mesh to rebuild; the posed Blend is unchanged.

`ShortsGussetCandidate/` now retains a separate 44 mm saddle-gusset topology study with close and full-body renders. It keeps this pose scene's face, hands, jacket and footwear intact. The gusset candidate has less thigh clearance and still falls short of the visual goal, so this parent remains the unchanged verified pose reference.

`ShortsSculptCandidate/` continues from that gusset by softening the concentrated left inseam fold and subtly shaping the front thigh. Its close and whole-figure renders still show an overly simple upper shorts panel. The separate candidate passes static checks with 2.48 mm sampled thigh clearance; it is not final human art.
