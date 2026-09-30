# Continuous neck and fitted collar

This native Blender candidate continues [RaglanPatternCandidate](../RaglanPatternCandidate/README.md), source SHA-256 `D646E3AAF1C312AF61EA03D9C2AD4A28C6074BA6B84245B6D1E31DDA9134E587`. It retains the adult torso/hip counter-rotation, sewn six-panel jacket, four-panel shorts and slate/teal OddsWell identity. No new external assets are adopted; the 31 packed licensed maps and retained CC0 anatomy remain in the editable scene.

The collar stand drops from a mean 53.471 mm to 31.013 mm. Its 384-column strip follows the actual neck section through a smooth continuous loft while every bottom attachment stays fixed. The lower anatomical neck extends smoothly by up to 25 mm inside the garment; upper face controls above world height 1.499 m remain exactly unchanged. This addresses the original head's rounded closing cap, which became exposed by the shorter stand. Zipper tape, teeth, slider and pull follow the new neckline. The retained woven and knit shaders use broader diffuse response, lower specular response and finer knit bump.

The [saved scene](NeckCollar.blend) has two new editable keys: `Continuous lower neck` at one gives the fitted neck and zero restores its original controls; `Original tall collar` at one restores the original collar controls. Both restorations are exact in the cold audit. The separate hash-pinned source retains the original scene, material response and shell method. The original 244-part `Body flow | stance blend` still drives the earlier/new stance; the head's new neck key is separate. This is an authored static pose, not an eight-preset fitting or animation guarantee.

## Native review

- [Full front](NeckCollar_Front.png)
- [Full rear](NeckCollar_Rear.png)
- [Side profile](NeckCollar_Profile.png)
- [Torso close-up](NeckCollar_TorsoFront.png)
- [Neck close-up](NeckCollar_NeckClose.png)
- [Gameplay scene](NeckCollar_Gameplay.png)

These are native Cycles renders from the delivered saved scene, at 12 samples for figure studies and 24 for gameplay. Technical checks do not constitute visual acceptance. The neckline is cleaner, but shoulder peaks, lower-neck texture stretching, smooth chest/fabric response and generic facial presentation still prevent the very-real human goal from being complete.

## Reproduction and checks

[build.py](build.py) opens the hash-pinned source and imports the existing body-warp/point-update functions from [BodyFlowCandidate/build.py](../BodyFlowCandidate/build.py) and [RaglanPatternCandidate/build.py](../RaglanPatternCandidate/build.py). Run it with Blender 4.5.5 LTS in background mode using `--python-exit-code 1 --python`. Run each audit in a fresh process afterward. [Delivery-manifest.json](Delivery-manifest.json) binds the saved scene, scripts, reports and renders to their SHA-256 hashes.

[audit.py](audit.py) requires zero nonadjacent BVH overlap flags on both the complete collar midsurface and inner fabric shell at render subdivision, a closed positive-volume shell, skin clearance, unchanged bottom attachments, exact original control restoration, unchanged upper face controls and a continuous neck without detected crossing. It additionally checks the jacket shell against the extended neck. [NeckCollar-audit.json](NeckCollar-audit.json) records the measurements. [audit_jacket.py](audit_jacket.py) independently checks the retained jacket, attachment and stance contracts; [Jacket-audit.json](Jacket-audit.json) holds its result. [cold-check.json](cold-check.json) records the shared scene check. The shared verifier now distinguishes the bounded vertical neck extension from facial morphs, whose fixed-neck rule remains enforced.

Early nearest-surface collar fitting incorrectly followed the artificial closing cap and produced overlaps. Those drafts were rejected. The retained continuous neck and strip loft pass the complete static checks; local surface checks and control-only measurements were insufficient for the rejected drafts. An open collar midsurface has no physical fabric-volume claim; only the closed thick shell's volume is reported.

## Next roadmap work

Continue shoulder/chest cloth shape, lower-neck texture mapping and facial individuality, then review the whole figure against the first OddsWell reference. Retain the softer hip/chest stance and the narrow teal signature. The scene milestone follows with architectural/retail variety, selective layered planting and warm lighting. Later engine handoff requires baked material/hair detail, a compatible rigged derivative, measured LOD/collision budgets and controlled Unreal validation. Existing starter-outfit walk review and stopped export/import preparation remain authoritative. This offline checkpoint grants no runtime, physical first-hour, Phase 1L exit, beta-exit or final-art approval.
