# Corrected limb pitch handoff

This derivative preserves the original twelve-bone rig, four meshes, four Actions, key times, and angle values. Rotation curves move from local Y (longitudinal twist, zero knee travel) to local X (the intended limb pitch). The builder measures before/after knee travel, retains original sources, and compares two scene-reopen FBX exports. Mesh FBXs are byte-identical copies of the prior accepted mesh handoff.

Run `build_motion_axes.py` with the installed Blender 4.5.5 LTS background interpreter and `PYTHONHASHSEED=0`. `motion_axis_custody.json` records exact FBX hashes, rates, frame counts, and measured joint travel. `MotionAxisCharacterCandidate.blend` is a separate editable derivative; its file bytes are not claimed to be deterministic across Blender saves.

Unreal animation import uses uniform scale 100, with mesh scale 1, to preserve the original meter-to-centimeter skeletal bind scale. `../UnrealImport/import_character.py` verifies fresh imports; `correct_animation_import.py` is a hash-bound migration for the specific earlier assets. Native `OddsWell.Character.SkeletalVisualBridge` checks evaluated head height and knee travel. These remain primitive production candidates, not final art.
