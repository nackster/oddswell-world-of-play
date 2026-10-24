# Scanned human movement checkpoint

This advances step 1 of [[Development/Project Completion Roadmap]] using the accepted Renderpeople Eric base. It shortens the exaggerated walking motion and relaxes the upper arms further toward the sides. The original source business clothing and open hands remain temporary.

`Full.png`, `Front.png`, `Side.png` and `Walking.mp4` are native Blender renders of the actual rigged mesh. A real studio ground plane and shadow make shoe height easier to inspect. The wider review camera retains the whole figure. This is a development study, not final gait acceptance.

`refine.py` loads the pinned compact source, damps existing quaternion motion around each bone's sampled center, adds 0.18 radians of upper-arm relaxation, reduces root motion, and regrounds the mesh at all 49 authored keys. The original action is copied before editing. The original file is retained unchanged.

The candidate is cold-opened and checked for identical source geometry, topology, UVs, vertex groups/weights, bind matrices and packed-map bytes. All 49 authored keys pass the ground check; 97 integer/half-frame samples are recorded in `motion-report.json`. Interpolation has a worst sampled ground penetration of 1.55 mm, so this is not final foot-contact acceptance. Whole-mesh grounding is not planted-foot locking or a sliding/contact proof. The source and candidate maximum foot-bone separation are measured in that report; the new maximum is approximately 17% smaller.

The editable candidate is stored locally at `downloads/licensed-characters/RenderpeopleEric/MotionRefinement/OddsWellHumanMotion.blend`. Vendor-derived models and textures remain in ignored storage under the existing publisher license. This folder retains the recipe, permitted rendered previews and reports only. Rebuild using Blender 4.5.5 LTS: `--background --factory-startup --disable-autoexec --python-exit-code 1 --python refine.py -- --preview`; then encode the 24 native frames at 12 fps using ffmpeg.

Next: suitable OddsWell casual wardrobe and relaxed hand poses, whole-character visual review, then an explicit production rig/preset/export contract and engine verification. This checkpoint does not change Unreal, the approved economy, first-hour proof or beta readiness.
