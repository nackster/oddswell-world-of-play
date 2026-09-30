# Rounded shoulder ease over the adult torso

This native Blender candidate continues [NeckCollarCandidate](../NeckCollarCandidate/README.md), source SHA-256 `1808A6254A566651C0731EE23C5E74FB7A126572863584D7366511D5336260C7`. It retains the defined torso/hip stance, six sewn jacket panels, fitted four-panel shorts, continuous lower neck and narrow teal OddsWell signature. No additional external assets are adopted; the 31 packed licensed maps and retained CC0 anatomy remain available.

The source shoulder peaks had about 27-34 mm signed clearance from the actual anatomical support. Two local ease fields bring that surplus closer, then 32 rounds of graded control relaxation round the ridge. Render-resolution fitting maintains the free-cloth body margin between controls. Fully held collar, waist and cuff attachments stay fixed. Raglan stitch paths are regenerated from the actual sewn UV edges; yoke, zipper and welt detail follow the new surface. The original native 60-frame cotton settle remains the starting shape; this is an authored fitting pass after that settle, not a new simulation or walking-cycle proof.

The [saved scene](ShoulderEase.blend) retains original controls in `Before rounded shoulder ease` and restores them through the `Original raised shoulders` key at one. Its default is zero. The separate hash-pinned source remains unchanged. The 244-part native stance control and separate neck/collar restoration controls remain editable.

## Native review views

- [Full front](ShoulderEase_Front.png)
- [Full rear](ShoulderEase_Rear.png)
- [Side profile](ShoulderEase_Profile.png)
- [Torso close-up](ShoulderEase_TorsoFront.png)
- [Neck close-up](ShoulderEase_NeckClose.png)
- [Gameplay scene](ShoulderEase_Gameplay.png)

The native Cycles views use 12 samples for figure studies and 24 for gameplay. The shoulders read rounder and less raised in the close front view. Smooth chest/fabric response, the collar-to-jacket ledge, lower-neck texture stretching and generic facial presentation still require development. This is visual progress toward the owner's very-real human goal, not final art acceptance.

## Reproduction and verification

[build.py](build.py) opens the hash-pinned source, reuses the body-warp and point-update functions, and reuses the retained raglan builder's sewn-edge tracing and fitted trim. Run with Blender 4.5.5 LTS using `--python-exit-code 1 --python`. [Delivery-manifest.json](Delivery-manifest.json) records the saved scene, scripts, native views, reports and source dependency hashes.

[audit.py](audit.py) cold-opens the delivered scene and checks the whole jacket midsurface and inner fabric shell at render subdivision, positive closed fabric volume, four openings, fixed attachments, body clearance and both endpoints of the 244-part stance control. It also checks the original shoulder key restores exactly and records the two measured ridge controls: reductions are 6.016 mm and 15.864 mm. The regression guard requires both to exceed 5 mm and one to exceed 15 mm; these bounded checks do not establish the full realism goal. [ShoulderEase-audit.json](ShoulderEase-audit.json) records the actual movements and clearances. [audit_collar.py](audit_collar.py) repeats the neck/collar restoration, overlap and skin-clearance checks on the updated jacket; [Collar-audit.json](Collar-audit.json) records them. [cold-check.json](cold-check.json) records the independent shared saved-scene check. All are static checks at this authored pose.

## Roadmap continuation

Continue coherent chest/underarm cloth and collar-to-jacket attachment, lower-neck texture mapping and facial individuality. Review the whole figure against the first OddsWell concept before advancing architectural/retail variety, selective layered planting and warm scene lighting. Later engine handoff requires baked materials and hair detail, a compatible rigged derivative, measured LOD/collision budgets and controlled Unreal validation. The existing starter-outfit walk acceptance gate and stopped export/import preparation remain authoritative. No runtime, physical first-hour, Phase 1L exit, beta-exit or final-art credit follows from this offline checkpoint. The human-realism goal remains active.
