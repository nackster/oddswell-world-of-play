# Raglan jacket over the torso and hip stance

This native Blender candidate continues [FourPanelCottonCandidate](../FourPanelCottonCandidate/README.md), source SHA-256 `39078A975AB485FDBB543A57C06C32F127A5C7BC6EDE2C3E9880A2CF0A854B20`. Four new torso quarters and two sleeve panels replace the previous joined-volume jacket. The original adult anatomy, fitted four-panel shorts, hip/chest counter-rotation, skin and cloth maps, teal identity band and Sundale setting remain the starting design. No additional external assets are adopted.

The sleeves follow depth-weighted cross sections of the actual posed arm support through the elbow bends. A higher underarm join and broad chest shaping replace the old rigid junction. The 6,274 controls and 6,144 quad faces form one sewn sheet with four openings and six cloth UV islands. A native 60-frame cotton settle preserves drafted, fitted and raw gravity coordinates as separate point attributes. Local underarm relaxation and fold fillets round narrow creases; final fit checks the evaluated curved surface between controls, including the transition beside held hems. Fully held neck, hem and cuff controls stay fixed. The constrained inner fabric shell remains 1.2 mm thick. Teal panels, stitches, pocket welts, zipper tape and teeth follow the resulting surface.

Review views are native Cycles renders: 12 samples for the four figure studies, 24 for gameplay.

- [Full front](RaglanPattern_Front.png)
- [Full rear](RaglanPattern_Rear.png)
- [Side profile](RaglanPattern_Profile.png)
- [Torso close-up](RaglanPattern_TorsoFront.png)
- [Gameplay scene](RaglanPattern_Gameplay.png)

The [saved scene](RaglanPattern.blend) retains the 244-part `Body flow | stance blend` control. Zero restores the inverse-warped previous stance of this **new jacket pattern**, not the superseded jacket mesh. The source scene remains separately available. The final candidate keeps 31 packed licensed maps and the retained CC0 anatomical support. [audit.py](audit.py) cold-opens the candidate and checks at the greater of viewport and render subdivision for both cloth and anatomical support. It requires zero nonadjacent overlap flags on the whole cloth midsurface and thick shell, positive closed fabric volume, four garment openings, fixed attachments and at least 3.5 mm evaluated free-cloth clearance. These are static checks at the retained pose, not a walking-cycle or production-rig guarantee. [RaglanPattern-audit.json](RaglanPattern-audit.json), [cold-check.json](cold-check.json) and [Delivery-manifest.json](Delivery-manifest.json) hold the results and hashes.

[build.py](build.py) opens the hash-pinned source, drafts and settles the new panels, and runs [finish.py](finish.py) to produce the final candidate. Run it with Blender 4.5.5 LTS in background mode using `--python-exit-code 1 --python`. Intermediate draft and bake cache files go to `client/OddsWell/Saved/NextTen20260912/RaglanPatternBuild`, outside this delivery. [body-sections.json](body-sections.json) retains the arm guides; [measure_sections.py](measure_sections.py) regenerates them from the source anatomy. Reopen audits run in a separate Blender process.

## Visual findings and next roadmap work

Front and rear review show a clearer chest-to-waist shape and continuous sleeves following the bent arms. The hips and shorts retain the earlier stance and panel construction. The broad slate jacket and restrained teal band remain recognizable in the street view. The close-up still shows artificial fabric response, a high collar, an overly smooth chest and generic facial presentation. This candidate advances construction; it does not complete the owner's very-real human goal or grant final art approval.

The first finished draft passed viewport checks but failed the finer render-resolution test: seven inner-shell overlap pairs and a small free-cloth/body penetration remained. Another local rear-shoulder fillet and render-resolution fitting corrected that draft. The fitting search uses movable controls so held collar/hem controls cannot starve the correction beside attachments. Both the final audit and retained review renders use the corrected candidate.

The corrected audit checks 96,716 evaluated free-cloth points with minimum clearance 3.679 mm. The visible character has 3,348,452 evaluated viewport triangles; the new jacket contributes 99,360 versus the source's 208,288. Scalp fibers still contribute 1,728,000 triangles. These are offline planning measurements for later baking, rig and LOD work, not a runtime performance result.

Continue collar/shoulder presentation, cloth finish and facial individuality, then review the whole figure against the original OddsWell concept. After human visual acceptance, the existing roadmap proceeds to architectural and retail variety, selective layered planting and warm scene lighting. Engine handoff then requires baked materials and hair detail, a compatible rigged derivative, measured LOD/collision budgets, and controlled Unreal validation. Export/import preparation remains stopped pending existing acceptance gates. Offline renders provide no runtime, physical first-hour, Phase 1L exit, beta-exit or release credit.
