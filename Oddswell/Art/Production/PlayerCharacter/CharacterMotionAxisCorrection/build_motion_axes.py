"""Preserve the four motion curves while correcting local limb pitch from Y to X."""
import importlib.util
import json
import math
import shutil
import struct
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent
TIMED = ROOT.parent / "CharacterFBXTimingCorrection"
spec = importlib.util.spec_from_file_location("timed_export", TIMED / "build_timed_exports.py")
timed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timed)
original = timed.original


def knee_motion(armature, action):
    for bone in armature.pose.bones:
        bone.rotation_euler = (0, 0, 0)
    armature.animation_data.action = action
    positions = []
    for frame in range(int(action.frame_range[0]), int(action.frame_range[1]) + 1):
        bpy.context.scene.frame_set(frame)
        positions.append(armature.pose.bones["shin.L"].head.copy())
    return max((p - positions[0]).length for p in positions)


old_manifest = json.loads((TIMED / "timed_export_custody.json").read_text())
source, contract = original.source_custody()
hashes = []
records = []
motions = []
for attempt in range(2):
    bpy.ops.wm.open_mainfile(filepath=str(original.SOURCE_BLEND))
    original.LAND.validate_outputs()
    armature = bpy.data.objects[contract["shared_skeleton"]["source_object"]]
    for action in bpy.data.actions:
        before = knee_motion(armature, action)
        curves = [c for c in action.fcurves if c.data_path.endswith("rotation_euler")]
        assert curves and all(c.array_index == 1 for c in curves)
        keys_before = [[tuple(k.co) for k in c.keyframe_points] for c in curves]
        for curve in curves:
            curve.array_index = 0
        action.update_tag()
        after = knee_motion(armature, action)
        assert keys_before == [[tuple(k.co) for k in c.keyframe_points] for c in curves]
        assert before < 0.00001 and after > 0.05, (action.name, before, after)
        if attempt == 1:
            motions.append({"action": action.name, "original_knee_travel_m": before,
                            "corrected_knee_travel_m": after, "curve_values_and_times_unchanged": True})
    armature.name = "Armature"
    current = {}
    for row in old_manifest["exports"]:
        target = ROOT / row["file"]
        if row["file"].startswith("SK_"):
            assert original.sha256(TIMED / row["file"]) == row["sha256"]
            shutil.copyfile(TIMED / row["file"], target)
        else:
            action = bpy.data.actions[row["contents"][1]]
            for bone in armature.pose.bones:
                bone.rotation_euler = (0, 0, 0)
            armature.animation_data.action = action
            scene = bpy.context.scene
            scene.frame_start, scene.frame_end = map(int, action.frame_range)
            scene.render.fps = row["timing"]["fps"]
            scene.render.fps_base = 1.0
            scene.frame_set(scene.frame_start)
            seconds = row["timing"]["authored_seconds"]
            bits = struct.unpack("<I", struct.pack("<f", seconds))[0]
            rounded = struct.unpack("<f", struct.pack("<I", bits))[0]
            if rounded < seconds:
                rounded = struct.unpack("<f", struct.pack("<I", bits + 1))[0]
            timed.export_duration_ticks = math.ceil(rounded * timed.TICKS_PER_SECOND)
            original.select_only([armature])
            original.common_export(target, {"ARMATURE"}, True)
            assert abs(timed.duration(target) - row["timing"]["seconds"]) < 1e-9
        current[row["file"]] = original.sha256(target)
        if attempt == 1:
            (ROOT / row["sha256_record"]).write_text(f"{current[row['file']]}  {row['file']}\n", encoding="ascii", newline="\n")
            records.append({**row, "sha256": current[row["file"]], "bytes": target.stat().st_size})
    hashes.append(current)
assert hashes[0] == hashes[1]
for bone in armature.pose.bones:
    bone.rotation_euler = (0, 0, 0)
armature.animation_data.action = bpy.data.actions["walk_candidate_v1"]
bpy.context.scene.render.fps = 28
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 21
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "MotionAxisCharacterCandidate.blend"))
manifest = {"source_blend_sha256": original.sha256(original.SOURCE_BLEND),
            "source_contract_sha256": original.sha256(original.CONTRACT_PATH),
            "historical_exports_preserved": True, "repeat_hashes_equal": True,
            "correction": "rotation_euler local Y twist to local X pitch; original curve values/times preserved",
            "joint_motion": motions, "exports": records}
(ROOT / "motion_axis_custody.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
print("ODDSWELL_MOTION_AXIS_EXPORT_PASS " + json.dumps(motions))
