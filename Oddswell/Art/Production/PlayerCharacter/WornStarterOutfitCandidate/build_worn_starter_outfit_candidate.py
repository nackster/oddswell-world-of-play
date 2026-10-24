"""Build and validate the Phase 1L.5bl deterministic worn starter outfit."""

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "SkinnedSharedSkeletonCandidate"
SOURCE_BLEND = SOURCE_DIR / "SkinnedSharedSkeletonCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "skinning_custody.json"
SOURCE_BUILDER = SOURCE_DIR / "build_skinned_shared_skeleton_candidate.py"
REVIEW_MANIFEST = ROOT.parents[2] / "Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json"
OUTPUT_BLEND = ROOT / "WornStarterOutfitCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "outfit_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_BLEND_SHA256 = "9CBD196FDB42FA76788673467D16954733796AE6820073075005444B0942A443"
SOURCE_MANIFEST_SHA256 = "09BCC9BFDA60E1F7FE6F0288D52AA8C4FA22671653C2A190D96A682802CF9751"
SOURCE_BUILDER_SHA256 = "985FE86049B28108E0A56573CA4328755062644EB4AAA4EB5C518D3BF5248FFD"
SOURCE_SEMANTIC_SHA256 = "8F86A1FE89E9975C75B31D6700FA3FD64A98F87139C2C7DF0B721197ED25F146"
REVIEW_MANIFEST_SHA256 = "CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A"
TOP_ITEM = "starter_offwhite_top"
BOTTOM_ITEM = "starter_offwhite_bottom"
TOP_OBJECT = "CLOTHING__starter_offwhite_top"
BOTTOM_OBJECT = "CLOTHING__starter_offwhite_bottom"
MATERIAL_NAME = "CLOTHING__starter_offwhite"
STARTER_RGBA = [0.92, 0.9, 0.82, 1.0]
TOP_FIT = {"location": (0.0, 0.0, 1.22), "dimensions": (0.54, 0.285, 0.48)}
BOTTOM_FIT = {"location": (0.0, 0.0, 0.87), "dimensions": (0.405, 0.275, 0.22)}
LEG_FIT = {"hip_x": 0.155, "knee_x": 0.13, "top_z": 0.87, "bottom_z": 0.57, "radius": 0.096}
RENDER_SIZE = (720, 900)


def load_skin_module():
    spec = importlib.util.spec_from_file_location("phase1l5bk_skin", SOURCE_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SKIN = load_skin_module()


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


def review_json():
    return json.loads(REVIEW_MANIFEST.read_text(encoding="utf-8"))


def source_custody():
    custody = {
        "blend": {"file": "../SkinnedSharedSkeletonCandidate/SkinnedSharedSkeletonCharacterCandidate.blend", "sha256": sha256(SOURCE_BLEND)},
        "manifest": {"file": "../SkinnedSharedSkeletonCandidate/skinning_custody.json", "sha256": sha256(SOURCE_MANIFEST)},
        "builder": {"file": "../SkinnedSharedSkeletonCandidate/build_skinned_shared_skeleton_candidate.py", "sha256": sha256(SOURCE_BUILDER)},
        "semantic_sha256": source_json()["semantic"]["identity_sha256"],
        "review_manifest": {"file": "../../../Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json", "sha256": sha256(REVIEW_MANIFEST)},
    }
    actual = {
        "blend": custody["blend"]["sha256"],
        "manifest": custody["manifest"]["sha256"],
        "builder": custody["builder"]["sha256"],
        "semantic": custody["semantic_sha256"],
        "review": custody["review_manifest"]["sha256"],
    }
    expected = {
        "blend": SOURCE_BLEND_SHA256,
        "manifest": SOURCE_MANIFEST_SHA256,
        "builder": SOURCE_BUILDER_SHA256,
        "semantic": SOURCE_SEMANTIC_SHA256,
        "review": REVIEW_MANIFEST_SHA256,
    }
    if actual != expected:
        raise RuntimeError(f"accepted source or fit custody differs: {actual}")
    return custody


def expected_proxy_signature():
    signature = [
        {"role": "STARTER_OFFWHITE_TOP_PROXY", "location_m": list(TOP_FIT["location"]), "rotation_rad": [0.0, 0.0, 0.0], "dimensions_m": list(TOP_FIT["dimensions"])},
        {"role": "STARTER_OFFWHITE_BOTTOM_PROXY", "location_m": list(BOTTOM_FIT["location"]), "rotation_rad": [0.0, 0.0, 0.0], "dimensions_m": list(BOTTOM_FIT["dimensions"])},
    ]
    for side in (-1.0, 1.0):
        start = Vector((side * LEG_FIT["hip_x"], 0.0, LEG_FIT["top_z"]))
        end = Vector((side * LEG_FIT["knee_x"], 0.0, LEG_FIT["bottom_z"]))
        direction = end - start
        signature.append({
            "role": "STARTER_OFFWHITE_BOTTOM_PROXY",
            "location_m": rounded((start + end) / 2.0),
            "rotation_rad": rounded(direction.to_track_quat("Z", "Y").to_euler()),
            "dimensions_m": [round(LEG_FIT["radius"] * 2.0, 6), round(LEG_FIT["radius"] * 2.0, 6), round(direction.length, 6)],
        })
    return sorted(signature, key=lambda item: (item["role"], item["location_m"], item["dimensions_m"]))


def validate_fit_contract():
    outfit = review_json()["outfit_fit"]
    if outfit["starter_item_ids"] != [TOP_ITEM, BOTTOM_ITEM] or outfit["starter_rgba"] != STARTER_RGBA:
        raise RuntimeError("starter item/color contract differs")
    if outfit["starter_proxy_design_count"] != 1 or outfit["starter_transform_signature"] != expected_proxy_signature():
        raise RuntimeError("starter proxy dimensions or fit signature differ")
    return outfit["starter_transform_signature"]


def apply_transform(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)
    return obj


def move_to_collection(obj, collection):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def add_cube(name, location, dimensions, collection):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transform(obj)
    move_to_collection(obj, collection)
    return obj


def add_limb(name, start, end, collection):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=LEG_FIT["radius"], depth=direction.length, location=(start + end) / 2.0)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    apply_transform(obj)
    move_to_collection(obj, collection)
    return obj


def make_material():
    material = bpy.data.materials.new(MATERIAL_NAME)
    material.use_nodes = True
    material.diffuse_color = STARTER_RGBA
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = STARTER_RGBA
    shader.inputs["Roughness"].default_value = 0.86
    material["item_color_id"] = "starter_offwhite"
    material["exact_rgba_json"] = json.dumps(STARTER_RGBA, separators=(",", ":"))
    return material


def tag_clothing(obj, item_id, material, fit_roles):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
    obj["asset_role"] = "WORN_STARTER_OUTFIT"
    obj["item_id"] = item_id
    obj["color_id"] = "starter_offwhite"
    obj["exact_rgba_json"] = json.dumps(STARTER_RGBA, separators=(",", ":"))
    obj["fit_source"] = "Phase 1L.3g starter proxy"
    obj["fit_roles_json"] = json.dumps(fit_roles, separators=(",", ":"))


def build_clothing(mannequin):
    if bpy.data.objects.get(TOP_OBJECT) or bpy.data.objects.get(BOTTOM_OBJECT) or bpy.data.materials.get(MATERIAL_NAME):
        raise RuntimeError("accepted source already contains starter outfit production meshes")
    collection = mannequin.users_collection[0]
    material = make_material()
    top = add_cube(TOP_OBJECT, TOP_FIT["location"], TOP_FIT["dimensions"], collection)
    tag_clothing(top, TOP_ITEM, material, ["STARTER_OFFWHITE_TOP_PROXY"])

    bottom_parts = [add_cube("BOTTOM__pelvis", BOTTOM_FIT["location"], BOTTOM_FIT["dimensions"], collection)]
    for side in (-1.0, 1.0):
        bottom_parts.append(add_limb(
            f"BOTTOM__upper_leg_{'L' if side > 0.0 else 'R'}",
            (side * LEG_FIT["hip_x"], 0.0, LEG_FIT["top_z"]),
            (side * LEG_FIT["knee_x"], 0.0, LEG_FIT["bottom_z"]),
            collection,
        ))
    bpy.ops.object.select_all(action="DESELECT")
    for part in bottom_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = bottom_parts[0]
    bpy.ops.object.join()
    bottom = bpy.context.object
    bottom.name = BOTTOM_OBJECT
    tag_clothing(bottom, BOTTOM_ITEM, material, ["STARTER_OFFWHITE_BOTTOM_PROXY"])
    return top, bottom


def component_record(obj, indices):
    summary = SKIN.component_summary(obj.data, indices)
    summary["object"] = obj.name
    return summary


def bind_clothing(obj, armature, assignments):
    components = SKIN.connected_components(obj.data)
    records = [component_record(obj, indices) for indices in components]
    owners = assignments(records)
    if len(owners) != len(records):
        raise RuntimeError("clothing component assignment differs")
    groups = {name: obj.vertex_groups.new(name=name) for name in sorted(set(owners))}
    for indices, record, owner in zip(components, records, owners):
        groups[owner].add(indices, 1.0, "REPLACE")
        record["owner"] = owner
    modifier = obj.modifiers.new(f"ARMATURE__{obj['item_id']}", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    modifier.use_deform_preserve_volume = False
    return records


def top_assignments(records):
    if len(records) != 1:
        raise RuntimeError("starter top must remain one proxy component")
    return ["spine"]


def bottom_assignments(records):
    if len(records) != 3:
        raise RuntimeError("starter bottom must retain pelvis and two upper-leg components")
    owners = []
    for record in records:
        x = record["center_m"][0]
        owners.append("root" if abs(x) < 0.1 else ("thigh.L" if x > 0.0 else "thigh.R"))
    return owners


def mesh_signature(obj):
    payload = {
        "vertices": [rounded(vertex.co) for vertex in obj.data.vertices],
        "edges": [list(edge.vertices) for edge in obj.data.edges],
        "polygons": [list(polygon.vertices) for polygon in obj.data.polygons],
        "materials": [slot.material.name for slot in obj.material_slots],
    }
    return canonical_sha256(payload)


def object_weight_custody(obj, armature, allowed_groups, components):
    names_by_index = {group.index: group.name for group in obj.vertex_groups}
    if set(names_by_index.values()) != set(allowed_groups):
        raise RuntimeError(f"{obj.name} bone groups differ")
    counts = {name: 0 for name in allowed_groups}
    unweighted = 0
    non_normalized = 0
    influence_histogram = {}
    for vertex in obj.data.vertices:
        influences = [(names_by_index[entry.group], entry.weight) for entry in vertex.groups]
        influence_histogram[str(len(influences))] = influence_histogram.get(str(len(influences)), 0) + 1
        if not influences:
            unweighted += 1
            continue
        if abs(sum(weight for _name, weight in influences) - 1.0) > 0.000001:
            non_normalized += 1
        for name, _weight in influences:
            counts[name] += 1
    modifiers = list(obj.modifiers)
    if unweighted or non_normalized or influence_histogram != {"1": len(obj.data.vertices)}:
        raise RuntimeError(f"{obj.name} weights must be full, normalized, and single-influence")
    if len(modifiers) != 1 or modifiers[0].type != "ARMATURE" or modifiers[0].object != armature:
        raise RuntimeError(f"{obj.name} must have exactly one shared-armature modifier")
    if any(count == 0 for count in counts.values()):
        raise RuntimeError(f"{obj.name} has an unused allowed bone group")
    return {
        "vertex_count": len(obj.data.vertices),
        "polygon_count": len(obj.data.polygons),
        "geometry_sha256": mesh_signature(obj),
        "allowed_groups": sorted(allowed_groups),
        "group_vertex_counts": counts,
        "influence_histogram": influence_histogram,
        "max_influences_per_vertex": 1,
        "unweighted_vertices": 0,
        "non_normalized_vertices": 0,
        "modifier": {"name": modifiers[0].name, "armature": modifiers[0].object.name, "type": modifiers[0].type},
        "components": components,
    }


def evaluated_coordinates(obj):
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def outfit_deformation(top, bottom, armature):
    SKIN.clear_pose(armature)
    rest = {obj.name: evaluated_coordinates(obj) for obj in (top, bottom)}
    SKIN.apply_diagnostic_pose(armature)
    posed = {obj.name: evaluated_coordinates(obj) for obj in (top, bottom)}
    records = {}
    combined = []
    for obj in (top, bottom):
        deltas = [posed[obj.name][index] - rest[obj.name][index] for index in range(len(rest[obj.name]))]
        moved = [delta for delta in deltas if delta.length > 0.000001]
        combined.extend(rounded(delta) for delta in deltas)
        records[obj["item_id"]] = {
            "moved_vertex_count": len(moved),
            "max_displacement_m": round(max((delta.length for delta in moved), default=0.0), 6),
            "delta_identity_sha256": canonical_sha256([rounded(delta) for delta in deltas]),
        }
    SKIN.clear_pose(armature)
    restored = {obj.name: evaluated_coordinates(obj) for obj in (top, bottom)}
    if any((rest[name][index] - restored[name][index]).length > 0.000001 for name in rest for index in range(len(rest[name]))):
        raise RuntimeError("starter outfit did not restore to deterministic rest")
    records["combined_delta_identity_sha256"] = canonical_sha256(combined)
    records["diagnostic_only"] = True
    records["joints_exercised"] = ["shoulders", "elbows", "hips", "knees"]
    return records


def render_reviews(armature):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    camera = scene.camera
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100

    SKIN.clear_pose(armature)
    camera.location = (0.0, -6.0, 0.95)
    SKIN.point_at(camera, (0.0, 0.0, 0.9))
    rest_path = RENDER_DIR / "Review_RestWornOutfit.png"
    scene.render.filepath = str(rest_path)
    bpy.ops.render.render(write_still=True)
    SKIN.canonicalize_png(rest_path)

    SKIN.apply_diagnostic_pose(armature)
    camera.location = (4.25, -4.25, 0.95)
    SKIN.point_at(camera, (0.0, 0.0, 0.9))
    diagnostic_path = RENDER_DIR / "Review_StaticDeformationWornOutfit.png"
    scene.render.filepath = str(diagnostic_path)
    bpy.ops.render.render(write_still=True)
    SKIN.canonicalize_png(diagnostic_path)
    SKIN.clear_pose(armature)


def validate_boundaries(mannequin, armature, top, bottom):
    errors = []
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    clothing = [obj for obj in meshes if obj.get("asset_role") == "WORN_STARTER_OUTFIT"]
    if len(meshes) != 3 or {obj.get("item_id") for obj in clothing} != {TOP_ITEM, BOTTOM_ITEM} or len(clothing) != 2:
        errors.append("exact mannequin plus two starter clothing mesh identities are required")
    if len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]) != 1 or armature.name != SKIN.ARMATURE_NAME:
        errors.append("exact retained shared armature is required")
    if len(bpy.data.materials) != 5 or bpy.data.materials.get(MATERIAL_NAME) is None:
        errors.append("exact one additional off-white clothing material is required")
    if any(obj.parent or obj.data.shape_keys for obj in (top, bottom)):
        errors.append("clothing parenting and shape keys are forbidden")
    if any(modifier.type != "ARMATURE" for obj in (top, bottom) for modifier in obj.modifiers):
        errors.append("cloth physics, collision, and non-armature modifiers are forbidden")
    if bpy.data.actions or armature.animation_data or mannequin.animation_data or top.animation_data or bottom.animation_data:
        errors.append("Actions, NLA, motion, and drivers are forbidden")
    if any(pose_bone.constraints for pose_bone in armature.pose.bones):
        errors.append("control rig, IK, and constraints are forbidden")
    if not SKIN.pose_is_clear(armature):
        errors.append("saved source must retain clear rest pose")
    if errors:
        raise RuntimeError("\n".join(errors))


def scene_semantic(mannequin, armature, top, bottom, fit_signature, top_weights, bottom_weights, deformation):
    source = source_json()["semantic"]
    semantic = {
        "source_semantic_sha256": SOURCE_SEMANTIC_SHA256,
        "body_geometry_sha256": SKIN.mesh_signature(mannequin),
        "armature": {"name": armature.name, "bones": SKIN.armature_semantic(armature)},
        "preserved_presets": source["preset_ids"],
        "preserved_materials": source["materials"],
        "preserved_midpoints_m": source["neutral_horizontal_midpoints_m"],
        "outfit": {
            "object_count": 2,
            "item_ids": [TOP_ITEM, BOTTOM_ITEM],
            "material": {"name": MATERIAL_NAME, "rgba": STARTER_RGBA, "textures": 0},
            "phase1l3g_transform_signature": fit_signature,
            TOP_ITEM: {"object": top.name, "weights": top_weights},
            BOTTOM_ITEM: {"object": bottom.name, "weights": bottom_weights},
        },
        "static_deformation": deformation,
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
    for filename, role in (("Review_RestWornOutfit.png", "REST_WORN_OUTFIT"), ("Review_StaticDeformationWornOutfit.png", "STATIC_DIAGNOSTIC_WORN_OUTFIT")):
        path = RENDER_DIR / filename
        width, height = SKIN.png_dimensions(path)
        renders.append({"file": f"renders/{filename}", "role": role, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bl deterministic worn starter-outfit refit and shared-armature deformation proof",
        "status": "worn_starter_outfit_static_diagnostic_only_not_runtime_or_final_art",
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
            "clothing_meshes": 2,
            "signal_jackets": 0,
            "other_clothing": 0,
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
            "economy_changes": 0,
            "catalog_changes": 0,
            "final_art_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def current_records(mannequin, armature, top, bottom):
    top_components = [component_record(top, indices) for indices in SKIN.connected_components(top.data)]
    for record, owner in zip(top_components, top_assignments(top_components)):
        record["owner"] = owner
    bottom_components = [component_record(bottom, indices) for indices in SKIN.connected_components(bottom.data)]
    for record, owner in zip(bottom_components, bottom_assignments(bottom_components)):
        record["owner"] = owner
    top_weights = object_weight_custody(top, armature, {"spine"}, top_components)
    bottom_weights = object_weight_custody(bottom, armature, {"root", "thigh.L", "thigh.R"}, bottom_components)
    deformation = outfit_deformation(top, bottom, armature)
    return top_weights, bottom_weights, deformation


def validate_outputs():
    custody = source_custody()
    fit_signature = validate_fit_contract()
    mannequin, armature = SKIN.find_objects()
    top = bpy.data.objects.get(TOP_OBJECT)
    bottom = bpy.data.objects.get(BOTTOM_OBJECT)
    if top is None or bottom is None:
        raise RuntimeError("starter outfit objects are missing")
    validate_boundaries(mannequin, armature, top, bottom)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required additive outfit outputs are missing or a blend backup exists")
    top_weights, bottom_weights, deformation = current_records(mannequin, armature, top, bottom)
    semantic = scene_semantic(mannequin, armature, top, bottom, fit_signature, top_weights, bottom_weights, deformation)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody or manifest.get("semantic") != semantic:
        raise RuntimeError("retained outfit source/semantic custody differs")
    if manifest.get("blender_version") != bpy.app.version_string or len(manifest.get("renders", [])) != 2:
        raise RuntimeError("Blender/render custody differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if SKIN.png_dimensions(path) != RENDER_SIZE or path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
            raise RuntimeError(f"render identity differs: {path.name}")
    for key, path in (("builder", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"{key} identity differs")
    print(
        "ODDSWELL_WORN_STARTER_OUTFIT_VALIDATION|result=PASS|clothing_meshes=2|items=2|materials=1|"
        f"top_vertices={len(top.data.vertices)}|bottom_vertices={len(bottom.data.vertices)}|top_groups=1|bottom_groups=3|"
        "modifiers=2|unweighted=0|non_normalized=0|max_influences=1|rest_pose_saved=true|"
        "signal_jacket=0|other_clothes=0|physics=0|collision=0|textures=0|shape_keys=0|"
        "control_rig=0|ik=0|constraints=0|drivers=0|actions=0|nla=0|clips=0|exports=0|imports=0|runtime=0"
    )
    return semantic


def build():
    custody = source_custody()
    fit_signature = validate_fit_contract()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    SKIN.validate_outputs()
    mannequin, armature = SKIN.find_objects()
    accepted_body_geometry = SKIN.mesh_signature(mannequin)
    accepted_armature = SKIN.armature_semantic(armature)
    top, bottom = build_clothing(mannequin)
    top_components = bind_clothing(top, armature, top_assignments)
    bottom_components = bind_clothing(bottom, armature, bottom_assignments)
    top_weights = object_weight_custody(top, armature, {"spine"}, top_components)
    bottom_weights = object_weight_custody(bottom, armature, {"root", "thigh.L", "thigh.R"}, bottom_components)
    deformation = outfit_deformation(top, bottom, armature)
    render_reviews(armature)
    validate_boundaries(mannequin, armature, top, bottom)
    if SKIN.mesh_signature(mannequin) != accepted_body_geometry or SKIN.armature_semantic(armature) != accepted_armature:
        raise RuntimeError("retained body geometry or shared armature changed")
    semantic = scene_semantic(mannequin, armature, top, bottom, fit_signature, top_weights, bottom_weights, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    if sha256(SOURCE_BLEND) != SOURCE_BLEND_SHA256 or sha256(SOURCE_MANIFEST) != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("accepted Phase 1L.5bk source changed during additive build")
    print(
        "ODDSWELL_WORN_STARTER_OUTFIT_BUILD|result=PASS|artifacts=5|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_WORN_STARTER_OUTFIT_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=2")
        return
    build()


if __name__ == "__main__":
    main()
