"""Build and validate the Phase 1L.5bn deterministic in-place walk candidate."""

import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "SignalJacketCandidate"
SOURCE_BLEND = SOURCE_DIR / "SignalJacketCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "signal_jacket_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_signal_jacket_candidate.py"
OUTPUT_BLEND = ROOT / "WalkCycleCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "walk_cycle_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_FILES = {
    "build_signal_jacket_candidate.py": "AEF602088661869625461D29C818B433D4EB86D88BAD19099CC6B52ADA4582DE",
    "PROVENANCE.md": "FF3EB12355DAC84A08A00FE6B58883F64D69547DD4125027CAADF9D9FD3D515E",
    "renders/Review_RestSignalJacketAlternative.png": "E90EFB2DBCFCBC35D20D58BE682529C3A6E836F29B11EDB39A0E426308CC4B0E",
    "renders/Review_StaticTorsoDeformationSignalJacketAlternative.png": "5425F6C898A458DFFDFB2FEDB778EC95ED44DD61910AF84F9E391880F445220E",
    "signal_jacket_custody.json": "F8AD6E6671876D65E3A846B0E2AF69848CAD29C0321D036FAE25AA068826F15B",
    "SignalJacketCharacterCandidate.blend": "6BA252C2B7E51360582673EBEA408B6E036708122834C3BEC01E6812A883FBBB",
}
SOURCE_SEMANTIC_SHA256 = "DBE2724EFA94F7969C80BEF6D6B885D2E568475BC00BA8D0270ADDF15CFB807D"
ACTION_NAME = "walk_candidate_v1"
FPS = 28
FRAME_START = 1
FRAME_END = 21
SAMPLE_FRAMES = [1, 6, 11, 16, 21]
WALK_RATE_HZ = 1.4
LIMB_PITCH_DEGREES = 18.0
SPINE_SWAY_DEGREES = 3.0
RENDER_SIZE = (720, 900)


def load_source_module():
    spec = importlib.util.spec_from_file_location("phase1l5bm_jacket", SOURCE_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


JACKET = load_source_module()
OUTFIT = JACKET.OUTFIT
SKIN = JACKET.SKIN


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
            raise RuntimeError(f"accepted Phase 1L.5bm byte custody differs: {relative} {actual}")
        records.append({"file": f"../SignalJacketCandidate/{relative}", "bytes": path.stat().st_size, "sha256": actual})
    semantic = source_json()["semantic"]["identity_sha256"]
    if semantic != SOURCE_SEMANTIC_SHA256:
        raise RuntimeError("accepted Phase 1L.5bm semantic custody differs")
    return {"files": records, "semantic_sha256": semantic}


def find_objects():
    return JACKET.find_objects()


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
    if jacket_weights != source["signal_jacket"]["weights"]:
        raise RuntimeError("retained Signal Jacket geometry/binding differs")
    if records["mesh_geometry_sha256"][JACKET.JACKET_ITEM] != source["signal_jacket"]["weights"]["geometry_sha256"]:
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
    if bpy.data.actions or armature.animation_data:
        raise RuntimeError("accepted source must contain no Action or animation data")
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    SKIN.clear_pose(armature)
    action = bpy.data.actions.new(ACTION_NAME)
    action["asset_role"] = "IN_PLACE_WALK_CANDIDATE"
    action["basis_source"] = "Phase 1L.5bg primitive walk"
    action["cycles_per_second"] = WALK_RATE_HZ
    action["cycle_duration_seconds"] = (FRAME_END - FRAME_START) / FPS
    action["limb_pitch_degrees"] = LIMB_PITCH_DEGREES
    action["spine_sway_degrees"] = SPINE_SWAY_DEGREES
    action["root_motion"] = False
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
    if len(bpy.data.actions) != 1 or action.name != ACTION_NAME:
        raise RuntimeError("exactly one named walk Action is required")
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
            raise RuntimeError("walk keys must remain deterministic linear interpolation")
        if abs(keys[0]["value"] - keys[-1]["value"]) > 0.000000001:
            raise RuntimeError("walk loop endpoints differ")
        curves.append({"bone": bone_name, "channel": channel, "axis": curve.array_index, "keys": keys})
    expected = {
        ("root", "location", 0), ("root", "location", 1), ("root", "location", 2),
        ("spine", "rotation_euler", 1),
        ("upper_arm.L", "rotation_euler", 1), ("upper_arm.R", "rotation_euler", 1),
        ("thigh.L", "rotation_euler", 1), ("thigh.R", "rotation_euler", 1),
    }
    actual = {(curve["bone"], curve["channel"], curve["axis"]) for curve in curves}
    if actual != expected or len(curves) != 8:
        raise RuntimeError("walk Action must contain exact five pitch and three zero-root curves")
    for curve in curves:
        values = [key["value"] for key in curve["keys"]]
        maximum = max(abs(value) for value in values)
        if curve["channel"] == "location" and maximum != 0.0:
            raise RuntimeError("root translation must remain exact zero")
        if curve["bone"] in {"upper_arm.L", "upper_arm.R", "thigh.L", "thigh.R"} and abs(maximum - math.radians(LIMB_PITCH_DEGREES)) > 0.00000001:
            raise RuntimeError("walk limb pitch differs from exact 18-degree basis")
        if curve["bone"] == "spine" and abs(maximum - math.radians(SPINE_SWAY_DEGREES)) > 0.00000001:
            raise RuntimeError("bounded torso sway differs")
    duration = (FRAME_END - FRAME_START) / FPS
    if abs((1.0 / duration) - WALK_RATE_HZ) > 0.000000001:
        raise RuntimeError("walk cycle rate differs from exact 1.4 Hz basis")
    semantic = {
        "name": ACTION_NAME,
        "action_count": 1,
        "fps": FPS,
        "frame_start": FRAME_START,
        "frame_end": FRAME_END,
        "sample_frames": SAMPLE_FRAMES,
        "cycle_duration_seconds": round(duration, 9),
        "cycles_per_second": WALK_RATE_HZ,
        "limb_pitch_degrees": LIMB_PITCH_DEGREES,
        "spine_sway_degrees": SPINE_SWAY_DEGREES,
        "root_translation_m": [0.0, 0.0, 0.0],
        "loop_end_equality": True,
        "curves": curves,
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


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
        raise RuntimeError("walk deformation must remain finite and bounded")
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
            path = RENDER_DIR / f"Review_{presentation}Walk_Frame{frame:02d}.png"
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
    if len(bpy.data.actions) != 1 or bpy.data.actions[0] != action or action.name != ACTION_NAME:
        errors.append("exactly one walk Action is required")
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


def scene_semantic(mannequin, armature, top, bottom, jacket, retained, action_record, deformation):
    source = source_json()["semantic"]
    semantic = {
        "source_semantic_sha256": SOURCE_SEMANTIC_SHA256,
        "preserved_scene": retained,
        "preserved_presets": source["preserved_presets"],
        "preserved_materials": source["preserved_materials"],
        "preserved_midpoints_m": source["preserved_midpoints_m"],
        "preserved_starter_items": source["preserved_starter_outfit"]["item_ids"],
        "preserved_signal_jacket_item": source["signal_jacket"]["item_id"],
        "action": action_record,
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
            filename = f"Review_{presentation}Walk_Frame{frame:02d}.png"
            path = RENDER_DIR / filename
            width, height = SKIN.png_dimensions(path)
            renders.append({"file": f"renders/{filename}", "presentation": presentation, "frame": frame, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bn deterministic in-place walk-cycle Action and clothed time-sampled deformation proof",
        "status": "single_in_place_walk_action_time_sampled_source_only_not_runtime_or_final_animation",
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
            "actions": 1,
            "walk_actions": 1,
            "run_actions": 0,
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
        raise RuntimeError("walk Action is missing")
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, action_record, deformation)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required walk outputs are missing or a blend backup exists")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody or manifest.get("semantic") != semantic:
        raise RuntimeError("retained source or walk semantic custody differs")
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
        "ODDSWELL_WALK_CYCLE_VALIDATION|result=PASS|actions=1|walk=1|rate_hz=1.4|limb_pitch_deg=18|"
        f"curves={len(action_record['curves'])}|samples=5|renders=4|root_translation=0|loop_equal=true|"
        f"body_moved={deformation['objects'][mannequin.name]['max_moved_vertex_count']}|"
        f"starter_top_moved={deformation['objects'][top.name]['max_moved_vertex_count']}|"
        f"starter_bottom_moved={deformation['objects'][bottom.name]['max_moved_vertex_count']}|"
        f"jacket_moved={deformation['objects'][jacket.name]['max_moved_vertex_count']}|"
        "run=0|jump=0|land=0|nla=0|root_motion=0|ik=0|control_rig=0|exports=0|imports=0|runtime=0|client=0"
    )
    return semantic


def build():
    custody = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    JACKET.validate_outputs()
    mannequin, armature, top, bottom, jacket = find_objects()
    retained = retained_scene_records(mannequin, armature, top, bottom, jacket)
    action = build_action(armature)
    action_record = action_semantic(action)
    deformation = time_sampled_deformation(mannequin, armature, top, bottom, jacket)
    render_reviews(top, bottom, jacket, armature)
    validate_boundaries(mannequin, armature, top, bottom, jacket, action)
    if retained != retained_scene_records(mannequin, armature, top, bottom, jacket):
        raise RuntimeError("retained predecessor scene semantics changed during additive build")
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, retained, action_record, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    source_custody()
    print(
        "ODDSWELL_WALK_CYCLE_BUILD|result=PASS|artifacts=7|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_WALK_CYCLE_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=4")
        return
    build()


if __name__ == "__main__":
    main()
