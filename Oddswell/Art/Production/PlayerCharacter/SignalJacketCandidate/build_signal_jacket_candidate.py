"""Build and validate the Phase 1L.5bm deterministic Signal Jacket candidate."""

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "WornStarterOutfitCandidate"
SOURCE_BLEND = SOURCE_DIR / "WornStarterOutfitCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "outfit_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_worn_starter_outfit_candidate.py"
REVIEW_MANIFEST = ROOT.parents[2] / "Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json"
OUTPUT_BLEND = ROOT / "SignalJacketCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "signal_jacket_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_FILES = {
    "build_worn_starter_outfit_candidate.py": "2F6C89F04DAF1F906CB1094961BBC7B436A9FF6DC2CC5627BC9CF7E85F585296",
    "outfit_custody.json": "CEA9E5C49AEB93587BCD88535271B6AC807BDC5D2995F1321BE97CA31C617DDF",
    "PROVENANCE.md": "DC590745C2DAA82CF92E6466583016B377FB2EF8D72BB0915691A3C04586AB0B",
    "renders/Review_RestWornOutfit.png": "01E120CF309E031C8297351746C1B175EFEA093D2CFF8DE4BA478B26E598C02A",
    "renders/Review_StaticDeformationWornOutfit.png": "19D77BE007D613B9B5CF6FE68BA466BF285CEE9629393A6C2C9A44DAA4640CDD",
    "WornStarterOutfitCharacterCandidate.blend": "8638D6EEA3D8414EFFA4D2F8F656E1F761AB176C3D47F1DB11CE016159675D90",
}
SOURCE_SEMANTIC_SHA256 = "244E7CCCC5AECA4B118AD74CBC959B97AEBEBB2D2B5139E98F243155361345A2"
REVIEW_MANIFEST_SHA256 = "CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A"
JACKET_ITEM = "sundale_signal_jacket"
JACKET_OBJECT = "CLOTHING__sundale_signal_jacket"
SLATE_MATERIAL = "CLOTHING__signal_jacket_slate"
TEAL_MATERIAL = "CLOTHING__signal_jacket_teal"
SLATE_RGBA = [0.12, 0.18, 0.22, 1.0]
TEAL_RGBA = [0.08, 0.72, 0.68, 1.0]
SHELL_FIT = {"location": (0.0, -0.012, 1.235), "dimensions": (0.58, 0.315, 0.50)}
ACCENT_FIT = {"location": (0.0, -0.171, 1.29), "dimensions": (0.59, 0.018, 0.075)}
RENDER_SIZE = (720, 900)


def load_source_module():
    spec = importlib.util.spec_from_file_location("phase1l5bl_outfit", SOURCE_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OUTFIT = load_source_module()
SKIN = OUTFIT.SKIN


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
            raise RuntimeError(f"accepted Phase 1L.5bl byte custody differs: {relative} {actual}")
        records.append({"file": f"../WornStarterOutfitCandidate/{relative}", "bytes": path.stat().st_size, "sha256": actual})
    semantic = source_json()["semantic"]["identity_sha256"]
    if semantic != SOURCE_SEMANTIC_SHA256 or sha256(REVIEW_MANIFEST) != REVIEW_MANIFEST_SHA256:
        raise RuntimeError("accepted source semantic or Phase 1L.3g review custody differs")
    return {
        "files": records,
        "semantic_sha256": semantic,
        "review_manifest": {
            "file": "../../../Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json",
            "sha256": REVIEW_MANIFEST_SHA256,
        },
    }


def expected_fit_signature():
    return [
        {"role": "SIGNAL_JACKET_ACCENT_PROXY", "location_m": list(ACCENT_FIT["location"]), "rotation_rad": [0.0, 0.0, 0.0], "dimensions_m": list(ACCENT_FIT["dimensions"])},
        {"role": "SIGNAL_JACKET_PROXY", "location_m": list(SHELL_FIT["location"]), "rotation_rad": [0.0, 0.0, 0.0], "dimensions_m": list(SHELL_FIT["dimensions"])},
    ]


def validate_fit_contract():
    outfit = json.loads(REVIEW_MANIFEST.read_text(encoding="utf-8"))["outfit_fit"]
    if outfit["signal_jacket_item_id"] != JACKET_ITEM or outfit["signal_jacket_proxy_design_count"] != 1:
        raise RuntimeError("Signal Jacket item/design contract differs")
    if outfit["signal_jacket_slate_rgba"] != SLATE_RGBA or outfit["signal_jacket_teal_rgba"] != TEAL_RGBA:
        raise RuntimeError("Signal Jacket color contract differs")
    if outfit["signal_jacket_transform_signature"] != expected_fit_signature():
        raise RuntimeError("Signal Jacket Phase 1L.3g transform signature differs")
    return outfit["signal_jacket_transform_signature"]


def make_material(name, color_id, rgba):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = rgba
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.86
    material["item_color_id"] = color_id
    material["exact_rgba_json"] = json.dumps(rgba, separators=(",", ":"))
    return material


def add_component(name, fit, material, collection):
    obj = OUTFIT.add_cube(name, fit["location"], fit["dimensions"], collection)
    obj.data.materials.append(material)
    return obj


def build_jacket(mannequin):
    if bpy.data.objects.get(JACKET_OBJECT) or bpy.data.materials.get(SLATE_MATERIAL) or bpy.data.materials.get(TEAL_MATERIAL):
        raise RuntimeError("accepted source already contains Signal Jacket candidate data")
    collection = mannequin.users_collection[0]
    slate = make_material(SLATE_MATERIAL, "signal_jacket_slate", SLATE_RGBA)
    teal = make_material(TEAL_MATERIAL, "signal_jacket_teal", TEAL_RGBA)
    shell = add_component("JACKET__shell", SHELL_FIT, slate, collection)
    accent = add_component("JACKET__accent", ACCENT_FIT, teal, collection)
    bpy.ops.object.select_all(action="DESELECT")
    shell.select_set(True)
    accent.select_set(True)
    bpy.context.view_layer.objects.active = shell
    bpy.ops.object.join()
    jacket = bpy.context.object
    jacket.name = JACKET_OBJECT
    jacket["asset_role"] = "ALTERNATIVE_SIGNAL_JACKET"
    jacket["item_id"] = JACKET_ITEM
    jacket["fit_source"] = "Phase 1L.3g Signal Jacket proxy"
    jacket["fit_roles_json"] = json.dumps(["SIGNAL_JACKET_PROXY", "SIGNAL_JACKET_ACCENT_PROXY"], separators=(",", ":"))
    jacket["review_worn_with"] = OUTFIT.BOTTOM_ITEM
    jacket["alternative_to"] = OUTFIT.TOP_ITEM
    return jacket


def component_records(jacket):
    records = []
    for indices in SKIN.connected_components(jacket.data):
        record = OUTFIT.component_record(jacket, indices)
        record["owner"] = "spine"
        records.append(record)
    if len(records) != 2:
        raise RuntimeError("Signal Jacket must remain one mesh with exact shell and accent components")
    return sorted(records, key=lambda record: record["center_m"][1])


def bind_jacket(jacket, armature):
    group = jacket.vertex_groups.new(name="spine")
    group.add([vertex.index for vertex in jacket.data.vertices], 1.0, "REPLACE")
    modifier = jacket.modifiers.new("ARMATURE__sundale_signal_jacket", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    modifier.use_deform_preserve_volume = False
    return OUTFIT.object_weight_custody(jacket, armature, {"spine"}, component_records(jacket))


def apply_torso_diagnostic(armature):
    SKIN.apply_diagnostic_pose(armature)
    spine = armature.pose.bones["spine"]
    spine.rotation_mode = "XYZ"
    spine.rotation_euler[1] = math.radians(8.0)
    bpy.context.view_layer.update()


def evaluated_coordinates(obj):
    return OUTFIT.evaluated_coordinates(obj)


def static_deformation(jacket, top, bottom, armature):
    objects = (jacket, top, bottom)
    SKIN.clear_pose(armature)
    rest = {obj.name: evaluated_coordinates(obj) for obj in objects}
    apply_torso_diagnostic(armature)
    posed = {obj.name: evaluated_coordinates(obj) for obj in objects}
    result = {}
    combined = []
    for obj in objects:
        deltas = [posed[obj.name][index] - rest[obj.name][index] for index in range(len(rest[obj.name]))]
        moved = [delta for delta in deltas if delta.length > 0.000001]
        combined.extend(rounded(delta) for delta in deltas)
        result[obj["item_id"]] = {
            "vertex_count": len(deltas),
            "moved_vertex_count": len(moved),
            "moved_coverage": round(len(moved) / len(deltas), 6),
            "max_displacement_m": round(max((delta.length for delta in moved), default=0.0), 6),
            "delta_identity_sha256": canonical_sha256([rounded(delta) for delta in deltas]),
        }
    if result[JACKET_ITEM]["moved_vertex_count"] != len(jacket.data.vertices) or result[OUTFIT.TOP_ITEM]["moved_vertex_count"] != len(top.data.vertices):
        raise RuntimeError("bounded spine diagnostic must move every jacket and retained starter-top vertex")
    if not all(math.isfinite(value) and 0.0 < value < 0.5 for value in (result[JACKET_ITEM]["max_displacement_m"], result[OUTFIT.TOP_ITEM]["max_displacement_m"])):
        raise RuntimeError("bounded torso displacement is not finite or proportionate")
    SKIN.clear_pose(armature)
    restored = {obj.name: evaluated_coordinates(obj) for obj in objects}
    if any((rest[name][index] - restored[name][index]).length > 0.000001 for name in rest for index in range(len(rest[name]))):
        raise RuntimeError("Signal Jacket diagnostic did not restore deterministic rest")
    result["combined_delta_identity_sha256"] = canonical_sha256(combined)
    result["diagnostic_only"] = True
    result["spine_rotation_degrees"] = [0.0, 8.0, 0.0]
    result["joints_exercised"] = ["spine", "shoulders", "elbows", "hips", "knees"]
    return result


def render_reviews(jacket, top, bottom, armature):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100
    camera = scene.camera
    top.hide_render = True
    jacket.hide_render = False
    bottom.hide_render = False

    SKIN.clear_pose(armature)
    camera.location = (0.0, -6.0, 0.95)
    SKIN.point_at(camera, (0.0, 0.0, 0.9))
    rest_path = RENDER_DIR / "Review_RestSignalJacketAlternative.png"
    scene.render.filepath = str(rest_path)
    bpy.ops.render.render(write_still=True)
    SKIN.canonicalize_png(rest_path)

    apply_torso_diagnostic(armature)
    camera.location = (4.25, -4.25, 0.95)
    SKIN.point_at(camera, (0.0, 0.0, 0.9))
    static_path = RENDER_DIR / "Review_StaticTorsoDeformationSignalJacketAlternative.png"
    scene.render.filepath = str(static_path)
    bpy.ops.render.render(write_still=True)
    SKIN.canonicalize_png(static_path)
    SKIN.clear_pose(armature)


def validate_boundaries(mannequin, armature, top, bottom, jacket):
    errors = []
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if len(meshes) != 4 or {obj.name for obj in meshes} != {mannequin.name, top.name, bottom.name, jacket.name}:
        errors.append("exact retained mannequin, starter top/bottom, and one Signal Jacket mesh are required")
    if len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]) != 1 or armature.name != SKIN.ARMATURE_NAME:
        errors.append("exact retained shared armature is required")
    if len(bpy.data.materials) != 7 or [slot.material.name for slot in jacket.material_slots] != [SLATE_MATERIAL, TEAL_MATERIAL]:
        errors.append("exact slate/teal two-slot Signal Jacket material contract is required")
    if jacket.get("item_id") != JACKET_ITEM or jacket.get("alternative_to") != OUTFIT.TOP_ITEM or jacket.get("review_worn_with") != OUTFIT.BOTTOM_ITEM:
        errors.append("Signal Jacket alternative review identity differs")
    if not top.hide_render or jacket.hide_render or bottom.hide_render:
        errors.append("review must show Signal Jacket as alternative top with starter bottom")
    if any(obj.parent or obj.data.shape_keys for obj in (top, bottom, jacket)):
        errors.append("clothing parenting and shape keys are forbidden")
    if any(modifier.type != "ARMATURE" for obj in (top, bottom, jacket) for modifier in obj.modifiers):
        errors.append("cloth, collision, and non-armature modifiers are forbidden")
    if bpy.data.actions or any(obj.animation_data for obj in (mannequin, armature, top, bottom, jacket)):
        errors.append("Actions, NLA, motion, and drivers are forbidden")
    if any(pose_bone.constraints for pose_bone in armature.pose.bones) or not SKIN.pose_is_clear(armature):
        errors.append("control rig, IK, constraints, or saved pose are forbidden")
    if errors:
        raise RuntimeError("\n".join(errors))


def retained_source_semantic(mannequin, armature, top, bottom):
    source = source_json()["semantic"]
    top_components = [OUTFIT.component_record(top, indices) for indices in SKIN.connected_components(top.data)]
    for record in top_components:
        record["owner"] = "spine"
    bottom_components = [OUTFIT.component_record(bottom, indices) for indices in SKIN.connected_components(bottom.data)]
    for record, owner in zip(bottom_components, OUTFIT.bottom_assignments(bottom_components)):
        record["owner"] = owner
    records = {
        "body_geometry_sha256": SKIN.mesh_signature(mannequin),
        "armature": {"name": armature.name, "bones": SKIN.armature_semantic(armature)},
        OUTFIT.TOP_ITEM: OUTFIT.object_weight_custody(top, armature, {"spine"}, top_components),
        OUTFIT.BOTTOM_ITEM: OUTFIT.object_weight_custody(bottom, armature, {"root", "thigh.L", "thigh.R"}, bottom_components),
    }
    if records["body_geometry_sha256"] != source["body_geometry_sha256"] or records["armature"] != source["armature"]:
        raise RuntimeError("retained mannequin geometry or shared armature differs")
    if records[OUTFIT.TOP_ITEM] != source["outfit"][OUTFIT.TOP_ITEM]["weights"] or records[OUTFIT.BOTTOM_ITEM] != source["outfit"][OUTFIT.BOTTOM_ITEM]["weights"]:
        raise RuntimeError("retained starter outfit geometry/binding differs")
    return records


def scene_semantic(mannequin, armature, top, bottom, jacket, fit_signature, jacket_weights, deformation):
    source = source_json()["semantic"]
    retained = retained_source_semantic(mannequin, armature, top, bottom)
    semantic = {
        "source_semantic_sha256": SOURCE_SEMANTIC_SHA256,
        "body_geometry_sha256": retained["body_geometry_sha256"],
        "armature": retained["armature"],
        "preserved_presets": source["preserved_presets"],
        "preserved_materials": source["preserved_materials"],
        "preserved_midpoints_m": source["preserved_midpoints_m"],
        "preserved_starter_outfit": {
            "item_ids": [OUTFIT.TOP_ITEM, OUTFIT.BOTTOM_ITEM],
            OUTFIT.TOP_ITEM: retained[OUTFIT.TOP_ITEM],
            OUTFIT.BOTTOM_ITEM: retained[OUTFIT.BOTTOM_ITEM],
        },
        "signal_jacket": {
            "item_id": JACKET_ITEM,
            "object": jacket.name,
            "alternative_to": OUTFIT.TOP_ITEM,
            "worn_with": OUTFIT.BOTTOM_ITEM,
            "mesh_count": 1,
            "component_count": 2,
            "phase1l3g_transform_signature": fit_signature,
            "materials": [
                {"slot": 0, "name": SLATE_MATERIAL, "rgba": SLATE_RGBA, "textures": 0},
                {"slot": 1, "name": TEAL_MATERIAL, "rgba": TEAL_RGBA, "textures": 0},
            ],
            "weights": jacket_weights,
        },
        "static_deformation": deformation,
        "review_visibility": {OUTFIT.TOP_ITEM: "hidden_as_alternative", OUTFIT.BOTTOM_ITEM: "visible", JACKET_ITEM: "visible"},
        "rest_pose_saved": SKIN.pose_is_clear(armature),
        "object_counts": {
            "total": len(bpy.data.objects),
            "mesh": len([obj for obj in bpy.data.objects if obj.type == "MESH"]),
            "armature": len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]),
            "camera": len([obj for obj in bpy.data.objects if obj.type == "CAMERA"]),
            "light": len([obj for obj in bpy.data.objects if obj.type == "LIGHT"]),
        },
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def write_manifest(semantic, custody):
    renders = []
    for filename, role in (
        ("Review_RestSignalJacketAlternative.png", "REST_SIGNAL_JACKET_ALTERNATIVE"),
        ("Review_StaticTorsoDeformationSignalJacketAlternative.png", "STATIC_TORSO_SIGNAL_JACKET_ALTERNATIVE"),
    ):
        path = RENDER_DIR / filename
        width, height = SKIN.png_dimensions(path)
        renders.append({"file": f"renders/{filename}", "role": role, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bm deterministic Sundale Signal Jacket refit and shared-armature deformation proof",
        "status": "signal_jacket_alternative_static_diagnostic_only_not_runtime_or_final_art",
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
            "signal_jacket_meshes": 1,
            "signal_jacket_materials": 2,
            "sleeves_or_invented_design": 0,
            "other_clothing": 0,
            "inventory_changes": 0,
            "price_changes": 0,
            "catalog_changes": 0,
            "equip_changes": 0,
            "economy_changes": 0,
            "cloth_physics": 0,
            "collision_modifiers": 0,
            "textures": 0,
            "shape_keys": 0,
            "control_rigs": 0,
            "ik": 0,
            "constraints": 0,
            "drivers": 0,
            "actions": 0,
            "nla_tracks": 0,
            "motion_clips": 0,
            "exports": 0,
            "unreal_imports": 0,
            "runtime_changes": 0,
            "client_changes": 0,
            "map_config_package_input_changes": 0,
            "faces_hair_second_silhouette": 0,
            "final_readiness_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def current_records(mannequin, armature, top, bottom, jacket):
    jacket_weights = OUTFIT.object_weight_custody(jacket, armature, {"spine"}, component_records(jacket))
    deformation = static_deformation(jacket, top, bottom, armature)
    return jacket_weights, deformation


def find_objects():
    mannequin, armature = SKIN.find_objects()
    top = bpy.data.objects.get(OUTFIT.TOP_OBJECT)
    bottom = bpy.data.objects.get(OUTFIT.BOTTOM_OBJECT)
    jacket = bpy.data.objects.get(JACKET_OBJECT)
    if top is None or bottom is None or jacket is None:
        raise RuntimeError("retained starter outfit or Signal Jacket object is missing")
    return mannequin, armature, top, bottom, jacket


def validate_outputs():
    custody = source_custody()
    fit_signature = validate_fit_contract()
    mannequin, armature, top, bottom, jacket = find_objects()
    validate_boundaries(mannequin, armature, top, bottom, jacket)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required additive Signal Jacket outputs are missing or a blend backup exists")
    jacket_weights, deformation = current_records(mannequin, armature, top, bottom, jacket)
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, fit_signature, jacket_weights, deformation)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody or manifest.get("semantic") != semantic:
        raise RuntimeError("retained source or Signal Jacket semantic custody differs")
    if manifest.get("blender_version") != bpy.app.version_string or len(manifest.get("renders", [])) != 2:
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
        "ODDSWELL_SIGNAL_JACKET_VALIDATION|result=PASS|jacket_meshes=1|components=2|materials=2|"
        f"vertices={len(jacket.data.vertices)}|groups=1|modifiers=1|unweighted=0|non_normalized=0|max_influences=1|"
        f"jacket_moved={deformation[JACKET_ITEM]['moved_vertex_count']}|starter_top_moved={deformation[OUTFIT.TOP_ITEM]['moved_vertex_count']}|"
        "rest_pose_saved=true|inventory=0|catalog=0|economy=0|physics=0|collision=0|textures=0|shape_keys=0|"
        "control_rig=0|ik=0|constraints=0|drivers=0|actions=0|nla=0|clips=0|exports=0|imports=0|runtime=0|client=0"
    )
    return semantic


def build():
    custody = source_custody()
    fit_signature = validate_fit_contract()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    OUTFIT.validate_outputs()
    mannequin, armature = SKIN.find_objects()
    top = bpy.data.objects[OUTFIT.TOP_OBJECT]
    bottom = bpy.data.objects[OUTFIT.BOTTOM_OBJECT]
    retained = retained_source_semantic(mannequin, armature, top, bottom)
    jacket = build_jacket(mannequin)
    jacket_weights = bind_jacket(jacket, armature)
    deformation = static_deformation(jacket, top, bottom, armature)
    render_reviews(jacket, top, bottom, armature)
    validate_boundaries(mannequin, armature, top, bottom, jacket)
    if retained != retained_source_semantic(mannequin, armature, top, bottom):
        raise RuntimeError("retained predecessor scene semantics changed during additive build")
    semantic = scene_semantic(mannequin, armature, top, bottom, jacket, fit_signature, jacket_weights, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    source_custody()
    print(
        "ODDSWELL_SIGNAL_JACKET_BUILD|result=PASS|artifacts=5|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_SIGNAL_JACKET_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=2")
        return
    build()


if __name__ == "__main__":
    main()
