"""Build and validate the Phase 1L.5bq deterministic in-place landing candidate."""

import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "JumpActionCandidate"
SOURCE_BLEND = SOURCE_DIR / "JumpActionCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "jump_action_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_jump_action_candidate.py"
OUTPUT_BLEND = ROOT / "LandingActionCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "landing_action_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_FILES = {
    "build_jump_action_candidate.py": "75DEABE42D0581700C0436315159EC5703F5E10509A017D8C1016544704E5256",
    "PROVENANCE.md": "ED26256F3A753E50E39278ECA04D7E1D0A057F72FC579B0852C6B29995139A2A",
    "renders/Review_SignalJacketJump_Airborne.png": "D91FCF84708EC4FBCF4F6ED9ADA7DFCF8DA6CCCA6D48890557C623F77550E466",
    "renders/Review_SignalJacketJump_Takeoff.png": "59D208BF6FEA5BB177378793282B70688C5BE33823C1D4536B0EB78C7F7C3A78",
    "renders/Review_StarterJump_Airborne.png": "925F1526AF4FDDC8AC0896BA7D8437C4D891B5BA54B0B692A4795EBE5F708806",
    "renders/Review_StarterJump_Takeoff.png": "51D3C07E79A8E2D2AD4B24F859A62CD51116DBF0E66FD9D84017493CB5869579",
    "jump_action_custody.json": "CD30E679450CF548EF39480342F06BA767C76BC42529078BFCED106E669936AC",
    "JumpActionCharacterCandidate.blend": "BABA8F5E655EB2629E5736F4D2DF8DD206BFA09EC55A2E3708A35CFD6DB52848",
}
SOURCE_SEMANTIC_SHA256 = "D582C924E160C4086BCFAEF4781D3902B47254E55410C4089797D1BD178C4BA8"
WALK_ACTION_NAME = "walk_candidate_v1"
RUN_ACTION_NAME = "run_candidate_v1"
JUMP_ACTION_NAME = "jump_candidate_v1"
ACTION_NAME = "land_candidate_v1"
FPS = 30
FRAME_START = 1
FRAME_END = 11
SAMPLE_FRAMES = [1, 6, 11]
POSE_LABELS = {1: "airborne", 6: "contact", 11: "neutral_recovery"}
RENDER_SIZE = (720, 900)


def load_source_module():
    spec = importlib.util.spec_from_file_location("phase1l5bp_jump", SOURCE_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


JUMP = load_source_module()
RUN = JUMP.RUN
WALK = JUMP.WALK
JACKET = JUMP.JACKET
OUTFIT = JUMP.OUTFIT
SKIN = JUMP.SKIN


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def rounded(values):
    return [round(float(value), 6) for value in values]


def source_json():
    return json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))


def source_custody():
    records = []
    for relative, expected in sorted(SOURCE_FILES.items()):
        path = SOURCE_DIR / relative
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"accepted Phase 1L.5bp byte custody differs: {relative} {actual}")
        records.append({"file": f"../JumpActionCandidate/{relative}", "bytes": path.stat().st_size, "sha256": actual})
    semantic = source_json()["semantic"]["identity_sha256"]
    if semantic != SOURCE_SEMANTIC_SHA256:
        raise RuntimeError("accepted Phase 1L.5bp semantic custody differs")
    return {"files": records, "semantic_sha256": semantic}


def find_objects():
    return JUMP.find_objects()


def retained_scene_records(mannequin, armature, top, bottom, jacket):
    source = source_json()["semantic"]
    base = JACKET.retained_source_semantic(mannequin, armature, top, bottom)
    jacket_weights = OUTFIT.object_weight_custody(jacket, armature, {"spine"}, JACKET.component_records(jacket))
    records = {
        "body_geometry_sha256": base["body_geometry_sha256"],
        "armature": base["armature"],
        "starter_top": base[OUTFIT.TOP_ITEM],
        "starter_bottom": base[OUTFIT.BOTTOM_ITEM],
        "signal_jacket": jacket_weights,
        "mesh_geometry_sha256": {
            "mannequin": SKIN.mesh_signature(mannequin),
            OUTFIT.TOP_ITEM: OUTFIT.mesh_signature(top),
            OUTFIT.BOTTOM_ITEM: OUTFIT.mesh_signature(bottom),
            JACKET.JACKET_ITEM: OUTFIT.mesh_signature(jacket),
        },
    }
    if jacket_weights != source["preserved_scene"]["signal_jacket"]:
        raise RuntimeError("retained Signal Jacket geometry/binding differs")
    if records["mesh_geometry_sha256"][JACKET.JACKET_ITEM] != source["preserved_scene"]["signal_jacket"]["geometry_sha256"]:
        raise RuntimeError("retained Signal Jacket mesh identity differs")
    return records


def pose_values(frame):
    return {
        1: {"spine": 4.0, "upper_arm.L": 30.0, "upper_arm.R": 30.0, "forearm.L": 18.0, "forearm.R": 18.0,
            "thigh.L": 22.0, "thigh.R": 22.0, "shin.L": -28.0, "shin.R": -28.0},
        6: {"spine": -8.0, "upper_arm.L": -12.0, "upper_arm.R": -12.0, "forearm.L": 10.0, "forearm.R": 10.0,
            "thigh.L": -22.0, "thigh.R": -22.0, "shin.L": 30.0, "shin.R": 30.0},
        11: {"spine": 0.0, "upper_arm.L": 0.0, "upper_arm.R": 0.0, "forearm.L": 0.0, "forearm.R": 0.0,
             "thigh.L": 0.0, "thigh.R": 0.0, "shin.L": 0.0, "shin.R": 0.0},
    }[frame]


def build_action(armature):
    walk_action = bpy.data.actions.get(WALK_ACTION_NAME)
    run_action = bpy.data.actions.get(RUN_ACTION_NAME)
    jump_action = bpy.data.actions.get(JUMP_ACTION_NAME)
    if len(bpy.data.actions) != 3 or any(item is None for item in (walk_action, run_action, jump_action)) or not armature.animation_data or armature.animation_data.action != jump_action:
        raise RuntimeError("accepted source must retain walk/run and assigned jump_candidate_v1 only")
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    SKIN.clear_pose(armature)
    action = bpy.data.actions.new(ACTION_NAME)
    action["asset_role"] = "IN_PLACE_LANDING_POSE_CANDIDATE"
    action["basis_source"] = "DEC-034 bounded landing proof on Phase 1L.5bg ACharacter trajectory authority"
    action["pose_sequence"] = "airborne_to_contact_to_neutral_recovery"
    action["root_motion"] = False
    walk_action.use_fake_user = True
    run_action.use_fake_user = True
    jump_action.use_fake_user = True
    armature.animation_data_create()
    armature.animation_data.action = action

    for frame in SAMPLE_FRAMES:
        for bone_name, degrees in pose_values(frame).items():
            bone = armature.pose.bones[bone_name]
            bone.rotation_mode = "XYZ"
            bone.rotation_euler[1] = math.radians(degrees)
            bone.keyframe_insert(data_path="rotation_euler", index=1, frame=frame, group=bone_name)
        root = armature.pose.bones["root"]
        for axis in range(3):
            root.location[axis] = 0.0
            root.keyframe_insert(data_path="location", index=axis, frame=frame, group="root")
    for curve in action.fcurves:
        for keyframe in curve.keyframe_points:
            keyframe.interpolation = "LINEAR"
    scene.frame_set(FRAME_START)
    return action


def curve_bone_name(data_path):
    match = re.fullmatch(r'pose\.bones\["([^"]+)"\]\.(rotation_euler|location)', data_path)
    if not match:
        raise RuntimeError(f"unexpected Action path: {data_path}")
    return match.group(1), match.group(2)


def action_semantic(action):
    if len(bpy.data.actions) != 4 or action.name != ACTION_NAME:
        raise RuntimeError("exactly retained walk/run/jump and new named landing Actions are required")
    curves = []
    for curve in sorted(action.fcurves, key=lambda item: (item.data_path, item.array_index)):
        bone_name, channel = curve_bone_name(curve.data_path)
        keys = []
        for keyframe in curve.keyframe_points:
            keys.append({
                "frame": round(float(keyframe.co[0]), 6),
                "value": round(float(keyframe.co[1]), 9),
                "interpolation": keyframe.interpolation,
            })
        if [entry["frame"] for entry in keys] != [float(frame) for frame in SAMPLE_FRAMES]:
            raise RuntimeError("Action sample frames differ")
        if any(entry["interpolation"] != "LINEAR" for entry in keys):
            raise RuntimeError("landing keys must remain deterministic linear interpolation")
        curves.append({"bone": bone_name, "channel": channel, "axis": curve.array_index, "keys": keys})
    expected = {
        ("root", "location", 0), ("root", "location", 1), ("root", "location", 2),
        ("spine", "rotation_euler", 1),
        ("upper_arm.L", "rotation_euler", 1), ("upper_arm.R", "rotation_euler", 1),
        ("forearm.L", "rotation_euler", 1), ("forearm.R", "rotation_euler", 1),
        ("thigh.L", "rotation_euler", 1), ("thigh.R", "rotation_euler", 1),
        ("shin.L", "rotation_euler", 1), ("shin.R", "rotation_euler", 1),
    }
    actual = {(curve["bone"], curve["channel"], curve["axis"]) for curve in curves}
    if actual != expected or len(curves) != 12:
        raise RuntimeError("landing Action must contain exact nine pose and three zero-root curves")
    for curve in curves:
        values = [key["value"] for key in curve["keys"]]
        maximum = max(abs(value) for value in values)
        if curve["channel"] == "location" and maximum != 0.0:
            raise RuntimeError("root translation must remain exact zero")
        if curve["channel"] == "rotation_euler" and maximum > math.radians(30.0) + 0.0000001:
            raise RuntimeError("landing pose exceeds the bounded 30-degree pitch envelope")
        if curve["channel"] == "rotation_euler":
            expected_values = [math.radians(pose_values(frame)[curve["bone"]]) for frame in SAMPLE_FRAMES]
            if any(abs(actual - expected) > 0.0000001 for actual, expected in zip(values, expected_values)):
                raise RuntimeError(f"landing pose values differ: {curve['bone']}")
    semantic = {
        "name": ACTION_NAME,
        "action_count": 4,
        "fps": FPS,
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "sample_frames": SAMPLE_FRAMES,
        "duration_seconds": round((FRAME_END - FRAME_START) / FPS, 9),
        "pose_labels": [POSE_LABELS[frame] for frame in SAMPLE_FRAMES],
        "pose_degrees": {str(frame): pose_values(frame) for frame in SAMPLE_FRAMES},
        "root_translation_m": [0.0, 0.0, 0.0],
        "trajectory_authority": "ACharacter_only_not_authored_here",
        "curves": curves,
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def retained_source_action(action, expected):
    if action is None or action.name != expected["name"]:
        raise RuntimeError(f"retained {expected['name']} is missing")
    curves = []
    for curve in sorted(action.fcurves, key=lambda item: (item.data_path, item.array_index)):
        bone_name, channel = curve_bone_name(curve.data_path)
        curves.append({
            "bone": bone_name,
            "channel": channel,
            "axis": curve.array_index,
            "keys": [{
                "frame": round(float(key.co[0]), 6),
                "value": round(float(key.co[1]), 9),
                "interpolation": key.interpolation,
            } for key in curve.keyframe_points],
        })
    if curves != expected["curves"]:
        raise RuntimeError(f"retained {action.name} curves differ")
    property_keys = ("cycles_per_second", "cycle_duration_seconds", "limb_pitch_degrees", "spine_sway_degrees")
    if all(key in expected for key in property_keys):
        properties = {key: action[key] for key in property_keys}
        if any(abs(float(value) - float(expected[key])) > 0.000000001 for key, value in properties.items()):
            raise RuntimeError(f"retained {action.name} properties differ")
    return expected


def evaluated_coordinates(obj):
    return OUTFIT.evaluated_coordinates(obj)


def displacement_record(deltas):
    moved = [delta for delta in deltas if delta.length > 0.000001]
    if any(not all(math.isfinite(value) for value in delta) for delta in deltas):
        raise RuntimeError("non-finite deformation sample")
    return {
        "moved_vertex_count": len(moved),
        "max_displacement_m": round(max((delta.length for delta in moved), default=0.0), 6),
        "delta_identity_sha256": canonical_sha256([rounded(delta) for delta in deltas]),
    }


def time_sampled_deformation(mannequin, armature, top, bottom, jacket):
    scene = bpy.context.scene
    objects = (mannequin, top, bottom, jacket)
    scene.frame_set(FRAME_END)
    baseline = {obj.name: evaluated_coordinates(obj) for obj in objects}
    samples = []
    combined = []
    per_object = {obj.name: {"vertex_count": len(obj.data.vertices), "max_moved_vertex_count": 0, "max_displacement_m": 0.0} for obj in objects}
    for frame in SAMPLE_FRAMES:
        scene.frame_set(frame)
        frame_record = {"frame": frame, "pose": POSE_LABELS[frame], "time_seconds": round((frame - FRAME_START) / FPS, 9), "objects": {}}
        root = armature.pose.bones["root"]
        if any(abs(value) > 0.000000001 for value in root.location):
            raise RuntimeError("sampled root translation differs from zero")
        for obj in objects:
            current = evaluated_coordinates(obj)
            deltas = [current[index] - baseline[obj.name][index] for index in range(len(current))]
            record = displacement_record(deltas)
            frame_record["objects"][obj.name] = record
            combined.extend(rounded(delta) for delta in deltas)
            summary = per_object[obj.name]
            summary["max_moved_vertex_count"] = max(summary["max_moved_vertex_count"], record["moved_vertex_count"])
            summary["max_displacement_m"] = max(summary["max_displacement_m"], record["max_displacement_m"])
        samples.append(frame_record)
    if per_object[mannequin.name]["max_moved_vertex_count"] == 0:
        raise RuntimeError("mannequin landing deformation was not demonstrated")
    if any(per_object[name]["max_moved_vertex_count"] == 0 for name in (top.name, bottom.name, jacket.name)):
        raise RuntimeError("both authorized clothing presentations must deform under the landing Action")
    if any(not (0.0 < record["max_displacement_m"] < 0.5) for record in per_object.values()):
        raise RuntimeError("landing deformation must remain finite and bounded")
    scene.frame_set(FRAME_END)
    if not SKIN.pose_is_clear(armature):
        raise RuntimeError("saved neutral-recovery pose must remain clear rest")
    result = {
        "sample_frames": SAMPLE_FRAMES,
        "pose_labels": [POSE_LABELS[frame] for frame in SAMPLE_FRAMES],
        "samples": samples,
        "objects": per_object,
        "presentations": {
            "starter": {"visible_items": [OUTFIT.TOP_ITEM, OUTFIT.BOTTOM_ITEM], "deforming_items": [OUTFIT.TOP_ITEM, OUTFIT.BOTTOM_ITEM]},
            "signal_jacket": {"visible_items": [JACKET.JACKET_ITEM, OUTFIT.BOTTOM_ITEM], "deforming_items": [JACKET.JACKET_ITEM, OUTFIT.BOTTOM_ITEM]},
        },
        "root_translation_zero_all_samples": True,
        "combined_delta_identity_sha256": canonical_sha256(combined),
    }
    return result


def render_reviews(top, bottom, jacket, armature):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100
    camera = scene.camera
    for presentation, show_top in (("Starter", True), ("SignalJacket", False)):
        top.hide_render = not show_top
        jacket.hide_render = show_top
        bottom.hide_render = False
        for frame, x in ((6, 4.25), (11, -4.25)):
            scene.frame_set(frame)
            camera.location = (x, -4.25, 0.95)
            SKIN.point_at(camera, (0.0, 0.0, 0.9))
            path = RENDER_DIR / f"Review_{presentation}Landing_{POSE_LABELS[frame].title().replace('_', '')}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            SKIN.canonicalize_png(path)
    top.hide_render = True
    jacket.hide_render = False
    bottom.hide_render = False
    scene.frame_set(FRAME_END)


def validate_boundaries(mannequin, armature, top, bottom, jacket, action):
    errors = []
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if len(meshes) != 4 or len(bpy.data.objects) != 6:
        errors.append("retained exact four meshes/six objects are required")
    if len(bpy.data.actions) != 4 or {item.name for item in bpy.data.actions} != {WALK_ACTION_NAME, RUN_ACTION_NAME, JUMP_ACTION_NAME, ACTION_NAME}:
        errors.append("exactly retained walk/run/jump and new land_candidate_v1 Actions are required")
    if not armature.animation_data or armature.animation_data.action != action or armature.animation_data.nla_tracks:
        errors.append("Action assignment differs or NLA exists")
    if any(obj.animation_data for obj in (mannequin, top, bottom, jacket)):
        errors.append("only the retained armature may own animation data")
    if any(obj.parent or obj.data.shape_keys for obj in (top, bottom, jacket)):
        errors.append("clothing parenting and shape keys are forbidden")
    if any(modifier.type != "ARMATURE" for obj in (top, bottom, jacket) for modifier in obj.modifiers):
        errors.append("cloth, collision, and non-armature modifiers are forbidden")
    if any(pose_bone.constraints for pose_bone in armature.pose.bones):
        errors.append("control rig, IK, and constraints are forbidden")
    if not top.hide_render or jacket.hide_render or bottom.hide_render:
        errors.append("saved review visibility must retain the accepted Signal Jacket presentation")
    if bpy.context.scene.frame_current != FRAME_END or not SKIN.pose_is_clear(armature):
        errors.append("saved source must remain at the clear neutral-recovery pose")
    if errors:
        raise RuntimeError("\n".join(errors))


def scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, run_record, jump_record, action_record, deformation):
    source = source_json()["semantic"]
    semantic = {
        "source_semantic_sha256": SOURCE_SEMANTIC_SHA256,
        "preserved_scene": retained,
        "preserved_presets": source["preserved_presets"],
        "preserved_materials": source["preserved_materials"],
        "preserved_midpoints_m": source["preserved_midpoints_m"],
        "preserved_starter_items": source["preserved_starter_items"],
        "preserved_signal_jacket_item": source["preserved_signal_jacket_item"],
        "preserved_walk_action": walk_record,
        "preserved_run_action": run_record,
        "preserved_jump_action": jump_record,
        "landing_action": action_record,
        "time_sampled_deformation": deformation,
        "saved_frame": FRAME_END,
        "saved_pose_clear": SKIN.pose_is_clear(armature),
        "saved_review_visibility": {OUTFIT.TOP_ITEM: "hidden", OUTFIT.BOTTOM_ITEM: "visible", JACKET.JACKET_ITEM: "visible"},
        "object_counts": {
            "total": len(bpy.data.objects),
            "mesh": len([obj for obj in bpy.data.objects if obj.type == "MESH"]),
            "armature": len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]),
            "camera": len([obj for obj in bpy.data.objects if obj.type == "CAMERA"]),
            "light": len([obj for obj in bpy.data.objects if obj.type == "LIGHT"]),
            "action": len(bpy.data.actions),
        },
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def write_manifest(semantic, custody):
    renders = []
    for presentation in ("Starter", "SignalJacket"):
        for frame in (6, 11):
            filename = f"Review_{presentation}Landing_{POSE_LABELS[frame].title().replace('_', '')}.png"
            path = RENDER_DIR / filename
            width, height = SKIN.png_dimensions(path)
            renders.append({"file": f"renders/{filename}", "presentation": presentation, "frame": frame, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bq deterministic in-place landing Action and clothed contact/recovery deformation proof",
        "status": "retained_walk_run_jump_plus_in_place_landing_pose_action_source_only_not_runtime_or_final_animation",
        "blender_version": bpy.app.version_string,
        "source_custody": custody,
        "semantic": semantic,
        "renders": renders,
        "files": {
            "blend": {"file": OUTPUT_BLEND.name, "identity": "semantic_only"},
            "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "boundaries": {
            "actions": 4,
            "walk_actions": 1,
            "run_actions": 1,
            "jump_actions": 1,
            "land_actions": 1,
            "extra_animations": 0,
            "nla_tracks": 0,
            "root_motion": 0,
            "ik": 0,
            "control_rigs": 0,
            "constraints": 0,
            "drivers": 0,
            "exports": 0,
            "fbx": 0,
            "unreal_imports": 0,
            "unreal_integration": 0,
            "runtime_changes": 0,
            "client_changes": 0,
            "package_input_changes": 0,
            "gameplay_authority_changes": 0,
            "brain_or_simulator_changes": 0,
            "final_art_claim": False,
            "beta_readiness_claim": False,
            "version_1_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_outputs():
    custody = source_custody()
    mannequin, armature, top, bottom, jacket = find_objects()
    action = bpy.data.actions.get(ACTION_NAME)
    if action is None:
        raise RuntimeError("landing Action is missing")
    source = source_json()["semantic"]
    walk_record = retained_source_action(bpy.data.actions.get(WALK_ACTION_NAME), source["preserved_walk_action"])
    run_record = retained_source_action(bpy.data.actions.get(RUN_ACTION_NAME), source["preserved_run_action"])
    jump_record = retained_source_action(bpy.data.actions.get(JUMP_ACTION_NAME), source["jump_action"])
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, run_record, jump_record, action_record, deformation)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required landing outputs are missing or a blend backup exists")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody or manifest.get("semantic") != semantic:
        raise RuntimeError("retained source or landing semantic custody differs")
    if manifest.get("blender_version") != bpy.app.version_string or len(manifest.get("renders", [])) != 4:
        raise RuntimeError("Blender or render custody differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if SKIN.png_dimensions(path) != RENDER_SIZE or path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
            raise RuntimeError(f"render identity differs: {path.name}")
    for key, path in (("builder", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"{key} identity differs")
    print(
        "ODDSWELL_LANDING_ACTION_VALIDATION|result=PASS|actions=4|walk=1|run=1|jump=1|land=1|"
        f"curves={len(action_record['curves'])}|samples=3|renders=4|root_translation=0|poses=airborne,contact,neutral_recovery|"
        f"body_moved={deformation['objects'][mannequin.name]['max_moved_vertex_count']}|"
        f"starter_top_moved={deformation['objects'][top.name]['max_moved_vertex_count']}|"
        f"starter_bottom_moved={deformation['objects'][bottom.name]['max_moved_vertex_count']}|"
        f"jacket_moved={deformation['objects'][jacket.name]['max_moved_vertex_count']}|"
        "nla=0|root_motion=0|ik=0|control_rig=0|exports=0|imports=0|runtime=0|client=0"
    )
    return semantic


def build():
    custody = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    JUMP.validate_outputs()
    mannequin, armature, top, bottom, jacket = find_objects()
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    source = source_json()["semantic"]
    walk_record = retained_source_action(bpy.data.actions.get(WALK_ACTION_NAME), source["preserved_walk_action"])
    run_record = retained_source_action(bpy.data.actions.get(RUN_ACTION_NAME), source["preserved_run_action"])
    jump_record = retained_source_action(bpy.data.actions.get(JUMP_ACTION_NAME), source["jump_action"])
    action = build_action(armature)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    render_reviews(top, bottom, jacket, armature)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    if retained != retained_scene_records(mannequin, armature, top, bottom, jacket):
        raise RuntimeError("retained predecessor scene semantics changed during additive build")
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, run_record, jump_record, action_record, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    source_custody()
    print(
        "ODDSWELL_LANDING_ACTION_BUILD|result=PASS|artifacts=8|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_LANDING_ACTION_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=4")
        return
    build()


if __name__ == "__main__":
    main()
