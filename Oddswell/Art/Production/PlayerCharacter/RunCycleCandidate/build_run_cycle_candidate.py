"""Build and validate the Phase 1L.5bo deterministic in-place run candidate."""

import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "WalkCycleCandidate"
SOURCE_BLEND = SOURCE_DIR / "WalkCycleCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "walk_cycle_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_walk_cycle_candidate.py"
OUTPUT_BLEND = ROOT / "RunCycleCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "run_cycle_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_FILES = {
    "build_walk_cycle_candidate.py": "9F8D53CC316D1B5C211132C50907C6C965F37952AC91620896F1A543E76A107E",
    "PROVENANCE.md": "46042F992B14BA33632A16E152EEEEF9F9F004FFFE4E60CF8B8C753EEF92AE45",
    "renders/Review_SignalJacketWalk_Frame06.png": "B2CA11E3648BF3A55770FFE34AD59BA90886FF27E92C8C6EDD87197FF60FD406",
    "renders/Review_SignalJacketWalk_Frame16.png": "DEB37B226E937EA8A078D59D70C8108CE3C77B79EB2E43D65AE24A6A44285715",
    "renders/Review_StarterWalk_Frame06.png": "F0BAA8230A89C79E844A8B061101F3C05F23886D4A4129BE6CEAC1439861B860",
    "renders/Review_StarterWalk_Frame16.png": "7C2681951E61CC6968160D3835B8F76596D832102A304CFD4D5595689383BA2D",
    "walk_cycle_custody.json": "F5677DA0726B9FD050C206A984174F91CE933AC537A7E2383A98B1A786DFF575",
    "WalkCycleCharacterCandidate.blend": "FCADE6F5004730F1A5307F75BEB75D54ADA33F7ECD285B52F44F6165B2B07F9C",
}
SOURCE_SEMANTIC_SHA256 = "01EE564AD289A5768863E7818F8D08C0F592FD9C8C497F239B80EDF05E7EF6E2"
WALK_ACTION_NAME = "walk_candidate_v1"
ACTION_NAME = "run_candidate_v1"
FPS = 44
FRAME_START = 1
FRAME_END = 21
SAMPLE_FRAMES = [1, 6, 11, 16, 21]
RUN_RATE_HZ = 2.2
LIMB_PITCH_DEGREES = 30.0
SPINE_SWAY_DEGREES = 5.0
RENDER_SIZE = (720, 900)


def load_source_module():
    spec = importlib.util.spec_from_file_location("phase1l5bn_walk", SOURCE_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WALK = load_source_module()
JACKET = WALK.JACKET
OUTFIT = WALK.OUTFIT
SKIN = WALK.SKIN


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
            raise RuntimeError(f"accepted Phase 1L.5bn byte custody differs: {relative} {actual}")
        records.append({"file": f"../WalkCycleCandidate/{relative}", "bytes": path.stat().st_size, "sha256": actual})
    semantic = source_json()["semantic"]["identity_sha256"]
    if semantic != SOURCE_SEMANTIC_SHA256:
        raise RuntimeError("accepted Phase 1L.5bn semantic custody differs")
    return {"files": records, "semantic_sha256": semantic}


def find_objects():
    return WALK.find_objects()


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
    phase = {1: 0.0, 6: 1.0, 11: 0.0, 16: -1.0, 21: 0.0}[frame]
    return {
        "upper_arm.L": phase * LIMB_PITCH_DEGREES,
        "upper_arm.R": -phase * LIMB_PITCH_DEGREES,
        "thigh.L": -phase * LIMB_PITCH_DEGREES,
        "thigh.R": phase * LIMB_PITCH_DEGREES,
        "spine": phase * SPINE_SWAY_DEGREES,
    }


def build_action(armature):
    walk_action = bpy.data.actions.get(WALK_ACTION_NAME)
    if len(bpy.data.actions) != 1 or walk_action is None or not armature.animation_data or armature.animation_data.action != walk_action:
        raise RuntimeError("accepted source must retain only the assigned walk_candidate_v1 Action")
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    SKIN.clear_pose(armature)
    action = bpy.data.actions.new(ACTION_NAME)
    action["asset_role"] = "IN_PLACE_RUN_CANDIDATE"
    action["basis_source"] = "Phase 1L.5bg primitive run"
    action["cycles_per_second"] = RUN_RATE_HZ
    action["cycle_duration_seconds"] = (FRAME_END - FRAME_START) / FPS
    action["limb_pitch_degrees"] = LIMB_PITCH_DEGREES
    action["spine_sway_degrees"] = SPINE_SWAY_DEGREES
    action["root_motion"] = False
    walk_action.use_fake_user = True
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
    if len(bpy.data.actions) != 2 or action.name != ACTION_NAME:
        raise RuntimeError("exactly the retained walk and new named run Actions are required")
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
            raise RuntimeError("run keys must remain deterministic linear interpolation")
        if abs(keys[0]["value"] - keys[-1]["value"]) > 0.000000001:
            raise RuntimeError("run loop endpoints differ")
        curves.append({"bone": bone_name, "channel": channel, "axis": curve.array_index, "keys": keys})
    expected = {
        ("root", "location", 0), ("root", "location", 1), ("root", "location", 2),
        ("spine", "rotation_euler", 1),
        ("upper_arm.L", "rotation_euler", 1), ("upper_arm.R", "rotation_euler", 1),
        ("thigh.L", "rotation_euler", 1), ("thigh.R", "rotation_euler", 1),
    }
    actual = {(curve["bone"], curve["channel"], curve["axis"]) for curve in curves}
    if actual != expected or len(curves) != 8:
        raise RuntimeError("run Action must contain exact five pitch and three zero-root curves")
    for curve in curves:
        values = [key["value"] for key in curve["keys"]]
        maximum = max(abs(value) for value in values)
        if curve["channel"] == "location" and maximum != 0.0:
            raise RuntimeError("root translation must remain exact zero")
        if curve["bone"] in {"upper_arm.L", "upper_arm.R", "thigh.L", "thigh.R"} and abs(maximum - math.radians(LIMB_PITCH_DEGREES)) > 0.0000001:
            raise RuntimeError("run limb pitch differs from exact 30-degree basis")
        if curve["bone"] == "spine" and abs(maximum - math.radians(SPINE_SWAY_DEGREES)) > 0.0000001:
            raise RuntimeError("bounded torso sway differs")
    duration = (FRAME_END - FRAME_START) / FPS
    if abs((1.0 / duration) - RUN_RATE_HZ) > 0.000000001:
        raise RuntimeError("run cycle rate differs from exact 2.2 Hz basis")
    semantic = {
        "name": ACTION_NAME,
        "action_count": 2,
        "fps": FPS,
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "sample_frames": SAMPLE_FRAMES,
        "cycle_duration_seconds": round(duration, 9),
        "cycles_per_second": RUN_RATE_HZ,
        "limb_pitch_degrees": LIMB_PITCH_DEGREES,
        "spine_sway_degrees": SPINE_SWAY_DEGREES,
        "root_translation_m": [0.0, 0.0, 0.0],
        "loop_end_equality": True,
        "curves": curves,
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def retained_walk_action(action):
    expected = source_json()["semantic"]["action"]
    if action is None or action.name != WALK_ACTION_NAME:
        raise RuntimeError("retained walk_candidate_v1 is missing")
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
        raise RuntimeError("retained walk Action curves differ")
    properties = {
        "cycles_per_second": action["cycles_per_second"],
        "cycle_duration_seconds": action["cycle_duration_seconds"],
        "limb_pitch_degrees": action["limb_pitch_degrees"],
        "spine_sway_degrees": action["spine_sway_degrees"],
    }
    if any(abs(float(value) - float(expected[key])) > 0.000000001 for key, value in properties.items()):
        raise RuntimeError("retained walk Action properties differ")
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
    scene.frame_set(FRAME_START)
    baseline = {obj.name: evaluated_coordinates(obj) for obj in objects}
    samples = []
    combined = []
    per_object = {obj.name: {"vertex_count": len(obj.data.vertices), "max_moved_vertex_count": 0, "max_displacement_m": 0.0} for obj in objects}
    for frame in SAMPLE_FRAMES:
        scene.frame_set(frame)
        frame_record = {"frame": frame, "time_seconds": round((frame - FRAME_START) / FPS, 9), "objects": {}}
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
    end = {obj.name: evaluated_coordinates(obj) for obj in objects}
    if any((baseline[name][index] - end[name][index]).length > 0.000001 for name in baseline for index in range(len(baseline[name]))):
        raise RuntimeError("time-sampled mesh loop endpoints differ")
    if per_object[mannequin.name]["max_moved_vertex_count"] == 0:
        raise RuntimeError("mannequin walk deformation was not demonstrated")
    if any(per_object[name]["max_moved_vertex_count"] == 0 for name in (top.name, bottom.name, jacket.name)):
        raise RuntimeError("both authorized clothing presentations must deform under the walk Action")
    if any(not (0.0 < record["max_displacement_m"] < 0.5) for record in per_object.values()):
        raise RuntimeError("run deformation must remain finite and bounded")
    scene.frame_set(FRAME_START)
    if not SKIN.pose_is_clear(armature):
        raise RuntimeError("saved loop-start pose must remain clear rest")
    result = {
        "sample_frames": SAMPLE_FRAMES,
        "samples": samples,
        "objects": per_object,
        "presentations": {
            "starter": {"visible_items": [OUTFIT.TOP_ITEM, OUTFIT.BOTTOM_ITEM], "deforming_items": [OUTFIT.TOP_ITEM, OUTFIT.BOTTOM_ITEM]},
            "signal_jacket": {"visible_items": [JACKET.JACKET_ITEM, OUTFIT.BOTTOM_ITEM], "deforming_items": [JACKET.JACKET_ITEM, OUTFIT.BOTTOM_ITEM]},
        },
        "root_translation_zero_all_samples": True,
        "mesh_loop_end_equality": True,
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
        for frame, x in ((6, 4.25), (16, -4.25)):
            scene.frame_set(frame)
            camera.location = (x, -4.25, 0.95)
            SKIN.point_at(camera, (0.0, 0.0, 0.9))
            path = RENDER_DIR / f"Review_{presentation}Run_Frame{frame:02d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            SKIN.canonicalize_png(path)
    top.hide_render = True
    jacket.hide_render = False
    bottom.hide_render = False
    scene.frame_set(FRAME_START)


def validate_boundaries(mannequin, armature, top, bottom, jacket, action):
    errors = []
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if len(meshes) != 4 or len(bpy.data.objects) != 6:
        errors.append("retained exact four meshes/six objects are required")
    if len(bpy.data.actions) != 2 or {item.name for item in bpy.data.actions} != {WALK_ACTION_NAME, ACTION_NAME}:
        errors.append("exactly retained walk_candidate_v1 and new run_candidate_v1 Actions are required")
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
    if bpy.context.scene.frame_current != FRAME_START or not SKIN.pose_is_clear(armature):
        errors.append("saved source must remain at the clear loop-start pose")
    if errors:
        raise RuntimeError("\n".join(errors))


def scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, action_record, deformation):
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
        "run_action": action_record,
        "time_sampled_deformation": deformation,
        "saved_frame": FRAME_START,
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
        for frame in (6, 16):
            filename = f"Review_{presentation}Run_Frame{frame:02d}.png"
            path = RENDER_DIR / filename
            width, height = SKIN.png_dimensions(path)
            renders.append({"file": f"renders/{filename}", "presentation": presentation, "frame": frame, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bo deterministic in-place run-cycle Action and clothed time-sampled deformation proof",
        "status": "retained_walk_plus_in_place_run_action_time_sampled_source_only_not_runtime_or_final_animation",
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
            "actions": 2,
            "walk_actions": 1,
            "run_actions": 1,
            "jump_actions": 0,
            "land_actions": 0,
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
        raise RuntimeError("run Action is missing")
    walk_record = retained_walk_action(bpy.data.actions.get(WALK_ACTION_NAME))
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, action_record, deformation)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required run outputs are missing or a blend backup exists")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody or manifest.get("semantic") != semantic:
        raise RuntimeError("retained source or run semantic custody differs")
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
        "ODDSWELL_RUN_CYCLE_VALIDATION|result=PASS|actions=2|walk=1|run=1|rate_hz=2.2|limb_pitch_deg=30|"
        f"curves={len(action_record['curves'])}|samples=5|renders=4|root_translation=0|loop_equal=true|"
        f"body_moved={deformation['objects'][mannequin.name]['max_moved_vertex_count']}|"
        f"starter_top_moved={deformation['objects'][top.name]['max_moved_vertex_count']}|"
        f"starter_bottom_moved={deformation['objects'][bottom.name]['max_moved_vertex_count']}|"
        f"jacket_moved={deformation['objects'][jacket.name]['max_moved_vertex_count']}|"
        "jump=0|land=0|nla=0|root_motion=0|ik=0|control_rig=0|exports=0|imports=0|runtime=0|client=0"
    )
    return semantic


def build():
    custody = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    WALK.validate_outputs()
    mannequin, armature, top, bottom, jacket = find_objects()
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    walk_record = retained_walk_action(bpy.data.actions.get(WALK_ACTION_NAME))
    action = build_action(armature)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    render_reviews(top, bottom, jacket, armature)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    if retained != retained_scene_records(mannequin, armature, top, bottom, jacket):
        raise RuntimeError("retained predecessor scene semantics changed during additive build")
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, walk_record, action_record, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    source_custody()
    print(
        "ODDSWELL_RUN_CYCLE_BUILD|result=PASS|artifacts=8|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_RUN_CYCLE_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=4")
        return
    build()


if __name__ == "__main__":
    main()
