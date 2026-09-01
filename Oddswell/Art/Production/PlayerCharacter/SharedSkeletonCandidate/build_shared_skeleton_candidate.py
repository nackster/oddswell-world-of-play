"""Build and validate the Phase 1L.5bj neutral shared-skeleton candidate."""

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[4]
CONTRACT_PATH = ROOT.parent / "production_candidate_contract.json"
REVIEW_MANIFEST_PATH = REPO_ROOT / "Oddswell/Art/Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json"
BLEND_PATH = ROOT / "SharedSkeletonCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"
RENDER_ENGINE = "BLENDER_WORKBENCH"

CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
PRESET_IDS = tuple(CONTRACT["appearance"]["preset_ids"])
TONE_RGBA8 = CONTRACT["appearance"]["tone_rgba8"]
LANDMARKS = CONTRACT["shared_landmarks_m"]
STATURE_M = CONTRACT["body"]["stature_m"]

# Arithmetic midpoints of the two Phase 1L.3g review silhouettes.
MIDPOINTS = {
    "shoulder_half_width_m": (0.255 + 0.235) / 2.0,
    "elbow_half_width_m": (0.290 + 0.270) / 2.0,
    "wrist_half_width_m": (0.275 + 0.255) / 2.0,
    "hip_half_width_m": (0.145 + 0.165) / 2.0,
    "knee_half_width_m": (0.130 + 0.130) / 2.0,
    "ankle_half_width_m": (0.130 + 0.130) / 2.0,
    "torso_width_m": round((0.480 + 0.430) / 2.0, 3),
    "torso_depth_m": (0.250 + 0.250) / 2.0,
    "pelvis_width_m": (0.330 + 0.370) / 2.0,
    "pelvis_depth_m": (0.240 + 0.240) / 2.0,
}

MATERIAL_NAMES = tuple(f"SKIN__{tone_id}" for tone_id in TONE_RGBA8)
VIEW_SPECS = {
    "Review_Front.png": {"role": "FRONT", "camera": (0.0, -6.0, 0.95)},
    "Review_Side.png": {"role": "SIDE", "camera": (6.0, 0.0, 0.95)},
    "Review_ThreeQuarter.png": {"role": "THREE_QUARTER", "camera": (4.25, -4.25, 0.95)},
}
RENDER_SIZE = (720, 900)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def png_dimensions(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def canonicalize_png(path):
    """Strip Blender's volatile PNG text metadata while preserving pixels."""
    data = path.read_bytes()
    output = bytearray(data[:8])
    cursor = 8
    while cursor < len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        end = cursor + length + 12
        chunk_type = data[cursor + 4 : cursor + 8]
        if chunk_type in {b"IHDR", b"IDAT", b"IEND"}:
            output.extend(data[cursor:end])
        cursor = end
        if chunk_type == b"IEND":
            break
    path.write_bytes(output)


def rounded(values):
    return [round(value, 6) for value in values]


def rgba_normalized(rgba8):
    return [round(channel / 255.0, 9) for channel in rgba8]


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for data_group in (
        bpy.data.meshes,
        bpy.data.armatures,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.actions,
    ):
        for item in list(data_group):
            data_group.remove(item)
    collection = bpy.data.collections.new("SHARED_SKELETON_CANDIDATE")
    bpy.context.scene.collection.children.link(collection)
    return collection


def make_material(tone_id, rgba8):
    material = bpy.data.materials.new(f"SKIN__{tone_id}")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    rgba = rgba_normalized(rgba8)
    material.diffuse_color = rgba
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.88
    material["tone_id"] = tone_id
    material["rgba8_json"] = json.dumps(rgba8, separators=(",", ":"))
    return material


def apply_transform(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)
    return obj


def add_cube(name, location, dimensions):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return apply_transform(obj)


def add_sphere(name, location, radius):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    return apply_transform(obj)


def add_limb(name, start, end, radius):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=radius,
        depth=direction.length,
        location=(start + end) / 2.0,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return apply_transform(obj)


def build_mannequin(collection, materials):
    pieces = [
        add_sphere("HEAD", (0.0, 0.0, LANDMARKS["head_center"]), 0.14),
        add_limb("NECK", (0.0, 0.0, 1.47), (0.0, 0.0, 1.55), 0.075),
        add_cube("TORSO", (0.0, 0.0, 1.215), (MIDPOINTS["torso_width_m"], MIDPOINTS["torso_depth_m"], 0.49)),
        add_cube("PELVIS", (0.0, 0.0, 0.91), (MIDPOINTS["pelvis_width_m"], MIDPOINTS["pelvis_depth_m"], 0.18)),
    ]
    for side, suffix in ((1.0, "L"), (-1.0, "R")):
        shoulder = (side * MIDPOINTS["shoulder_half_width_m"], 0.0, LANDMARKS["shoulder"])
        elbow = (side * MIDPOINTS["elbow_half_width_m"], 0.0, LANDMARKS["elbow"])
        wrist = (side * MIDPOINTS["wrist_half_width_m"], 0.0, LANDMARKS["wrist"])
        hip = (side * MIDPOINTS["hip_half_width_m"], 0.0, LANDMARKS["hip"])
        knee = (side * MIDPOINTS["knee_half_width_m"], 0.0, LANDMARKS["knee"])
        ankle = (side * MIDPOINTS["ankle_half_width_m"], 0.0, LANDMARKS["ankle"])
        pieces.extend((
            add_limb(f"UPPER_ARM.{suffix}", shoulder, elbow, 0.064),
            add_limb(f"FOREARM.{suffix}", elbow, wrist, 0.055),
            add_sphere(f"HAND.{suffix}", (wrist[0], 0.0, wrist[2] - 0.055), 0.06),
            add_limb(f"THIGH.{suffix}", hip, knee, 0.085),
            add_limb(f"SHIN.{suffix}", knee, ankle, 0.070),
            add_cube(f"FOOT.{suffix}", (ankle[0], -0.055, 0.055), (0.16, 0.28, 0.11)),
        ))

    for obj in pieces:
        for owner in list(obj.users_collection):
            owner.objects.unlink(obj)
        collection.objects.link(obj)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    mannequin = bpy.context.object
    mannequin.name = "MANNEQUIN__neutral_beta"
    for material in materials:
        mannequin.data.materials.append(material)
    for polygon in mannequin.data.polygons:
        polygon.material_index = 1
    mannequin["asset_role"] = "FACELESS_NON_ANATOMICAL_NEUTRAL_MANNEQUIN"
    mannequin["faceless"] = True
    mannequin["non_anatomical"] = True
    mannequin["stature_m"] = STATURE_M
    mannequin["silhouette_id"] = CONTRACT["body"]["silhouette_id"]
    mannequin["preset_ids_json"] = json.dumps(PRESET_IDS, separators=(",", ":"))
    mannequin["tone_rgba8_json"] = json.dumps(TONE_RGBA8, sort_keys=True, separators=(",", ":"))
    mannequin["neutral_midpoints_json"] = json.dumps(MIDPOINTS, sort_keys=True, separators=(",", ":"))
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    return mannequin


def bone_specs():
    specs = {
        "root": ((0.0, 0.0, 0.0), (0.0, 0.0, LANDMARKS["ankle"]), None, False),
        "spine": ((0.0, 0.0, LANDMARKS["hip"]), (0.0, 0.0, LANDMARKS["shoulder"]), "root", False),
        "neck": ((0.0, 0.0, LANDMARKS["shoulder"]), (0.0, 0.0, LANDMARKS["head_center"]), "spine", True),
        "head": ((0.0, 0.0, LANDMARKS["head_center"]), (0.0, 0.0, LANDMARKS["crown"]), "neck", True),
    }
    for side, suffix in ((1.0, "L"), (-1.0, "R")):
        shoulder = (side * MIDPOINTS["shoulder_half_width_m"], 0.0, LANDMARKS["shoulder"])
        elbow = (side * MIDPOINTS["elbow_half_width_m"], 0.0, LANDMARKS["elbow"])
        wrist = (side * MIDPOINTS["wrist_half_width_m"], 0.0, LANDMARKS["wrist"])
        hip = (side * MIDPOINTS["hip_half_width_m"], 0.0, LANDMARKS["hip"])
        knee = (side * MIDPOINTS["knee_half_width_m"], 0.0, LANDMARKS["knee"])
        ankle = (side * MIDPOINTS["ankle_half_width_m"], 0.0, LANDMARKS["ankle"])
        specs.update({
            f"upper_arm.{suffix}": (shoulder, elbow, "spine", False),
            f"forearm.{suffix}": (elbow, wrist, f"upper_arm.{suffix}", True),
            f"thigh.{suffix}": (hip, knee, "root", False),
            f"shin.{suffix}": (knee, ankle, f"thigh.{suffix}", True),
        })
    return specs


def build_armature(collection):
    data = bpy.data.armatures.new("ARMATURE_DATA__shared_bilateral_v1")
    armature = bpy.data.objects.new("ARMATURE__shared_bilateral_v1", data)
    collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for name, (head, tail, _parent, _connected) in bone_specs().items():
        bone = data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        created[name] = bone
    for name, (_head, _tail, parent, connected) in bone_specs().items():
        if parent:
            created[name].parent = created[parent]
            created[name].use_connect = connected
    bpy.ops.object.mode_set(mode="OBJECT")
    armature.select_set(False)
    armature.show_in_front = True
    armature.data.display_type = "OCTAHEDRAL"
    armature["asset_role"] = "SHARED_BILATERAL_ARMATURE"
    armature["landmarks_json"] = json.dumps(LANDMARKS, sort_keys=True, separators=(",", ":"))
    armature["deformation_ready"] = False
    armature["control_rig"] = False
    armature["ik"] = False
    return armature


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def build_review_scene(collection):
    scene = bpy.context.scene
    scene.render.engine = RENDER_ENGINE
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.world.color = (0.025, 0.032, 0.038)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_specular_highlight = False

    camera_data = bpy.data.cameras.new("CAMERA_DATA__candidate_review")
    camera = bpy.data.objects.new("CAMERA__candidate_review", camera_data)
    collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.08
    scene.camera = camera
    return camera


def scene_semantics():
    mannequin = next(obj for obj in bpy.data.objects if obj.get("asset_role") == "FACELESS_NON_ANATOMICAL_NEUTRAL_MANNEQUIN")
    armature = next(obj for obj in bpy.data.objects if obj.type == "ARMATURE")
    mannequin.data.calc_loop_triangles()
    bones = {}
    for bone in sorted(armature.data.bones, key=lambda item: item.name):
        bones[bone.name] = {
            "head_m": rounded(bone.head_local),
            "tail_m": rounded(bone.tail_local),
            "parent": bone.parent.name if bone.parent else None,
            "connected": bone.use_connect,
        }
    materials = {
        material["tone_id"]: json.loads(material["rgba8_json"])
        for material in sorted(bpy.data.materials, key=lambda item: item.name)
    }
    bounds = [mannequin.matrix_world @ Vector(corner) for corner in mannequin.bound_box]
    semantic = {
        "contract_id": CONTRACT["contract_id"],
        "object_counts": {
            "total": len(bpy.data.objects),
            "mesh": len([obj for obj in bpy.data.objects if obj.type == "MESH"]),
            "armature": len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]),
            "camera": len([obj for obj in bpy.data.objects if obj.type == "CAMERA"]),
            "light": len([obj for obj in bpy.data.objects if obj.type == "LIGHT"]),
        },
        "mannequin": {
            "name": mannequin.name,
            "vertices": len(mannequin.data.vertices),
            "polygons": len(mannequin.data.polygons),
            "triangles": len(mannequin.data.loop_triangles),
            "bounds_min_m": rounded((min(point.x for point in bounds), min(point.y for point in bounds), min(point.z for point in bounds))),
            "bounds_max_m": rounded((max(point.x for point in bounds), max(point.y for point in bounds), max(point.z for point in bounds))),
            "material_slots": [slot.material.name for slot in mannequin.material_slots],
            "active_tone": "tone_2",
        },
        "armature": {"name": armature.name, "bone_count": len(bones), "bones": bones},
        "materials": materials,
        "neutral_horizontal_midpoints_m": MIDPOINTS,
        "preset_ids": list(PRESET_IDS),
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def validate_contract():
    review = json.loads(REVIEW_MANIFEST_PATH.read_text(encoding="utf-8"))
    errors = []
    if CONTRACT.get("contract_id") != "player_character_shared_skeleton_candidate_v1":
        errors.append("contract identity differs")
    if CONTRACT.get("status") != "owner_approved_contract_only" or CONTRACT.get("cost_usd") != 0:
        errors.append("contract approval/cost differs")
    if CONTRACT.get("body") != {"faceless": True, "silhouette_count": 1, "silhouette_id": "neutral_beta", "stature_m": 1.8}:
        errors.append("body contract differs")
    if tuple(CONTRACT.get("appearance", {}).get("preset_ids", [])) != PRESET_IDS or len(set(PRESET_IDS)) != 8:
        errors.append("exact eight preset identities differ")
    if TONE_RGBA8 != review["review_contract"]["tone_rgba8"] or len(TONE_RGBA8) != 4:
        errors.append("exact four-tone palette differs")
    if LANDMARKS != review["review_contract"]["shared_joint_landmarks_m"] or len(LANDMARKS) != 8:
        errors.append("exact shared landmarks differ")
    if CONTRACT.get("next_gate") != "deterministic_blender_mannequin_and_shared_armature":
        errors.append("next gate differs")
    if errors:
        raise RuntimeError("\n".join(errors))


def validate_scene(require_outputs):
    validate_contract()
    errors = []
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    if len(meshes) != 1 or meshes[0].get("asset_role") != "FACELESS_NON_ANATOMICAL_NEUTRAL_MANNEQUIN":
        errors.append("exactly one neutral mannequin mesh is required")
    if len(armatures) != 1 or armatures[0].get("asset_role") != "SHARED_BILATERAL_ARMATURE":
        errors.append("exactly one shared bilateral armature is required")
    if len(bpy.data.materials) != 4 or tuple(sorted(material.name for material in bpy.data.materials)) != tuple(sorted(MATERIAL_NAMES)):
        errors.append("exactly four tone materials are required")
    if len(bpy.data.actions) != 0:
        errors.append("actions/animations are forbidden")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries/textures/images are forbidden")
    if meshes:
        mannequin = meshes[0]
        if mannequin.parent or mannequin.modifiers or mannequin.vertex_groups or mannequin.data.shape_keys:
            errors.append("parenting, modifiers, weights, vertex groups, and shape keys are forbidden")
        if len(mannequin.material_slots) != 4 or json.loads(mannequin["preset_ids_json"]) != list(PRESET_IDS):
            errors.append("mannequin appearance metadata differs")
        bounds = [mannequin.matrix_world @ Vector(corner) for corner in mannequin.bound_box]
        if abs(min(point.z for point in bounds)) > 0.000001 or abs(max(point.z for point in bounds) - STATURE_M) > 0.000001:
            errors.append("mannequin floor/crown bounds must be exact 0/1.80 m")
    if armatures:
        armature = armatures[0]
        expected = bone_specs()
        if {bone.name for bone in armature.data.bones} != set(expected) or len(armature.data.bones) != 12:
            errors.append("shared armature bone identities/count differ")
        else:
            for name, (head, tail, parent, connected) in expected.items():
                bone = armature.data.bones[name]
                if any(abs(actual - wanted) > 0.000001 for actual, wanted in zip(bone.head_local, head)):
                    errors.append(f"{name} head differs")
                if any(abs(actual - wanted) > 0.000001 for actual, wanted in zip(bone.tail_local, tail)):
                    errors.append(f"{name} tail differs")
                if (bone.parent.name if bone.parent else None) != parent or bone.use_connect != connected:
                    errors.append(f"{name} hierarchy differs")
        if any(pose_bone.constraints for pose_bone in armature.pose.bones) or armature.animation_data:
            errors.append("constraints, IK, drivers, and animation data are forbidden")
    if require_outputs:
        render_names = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if render_names != sorted(VIEW_SPECS):
            errors.append(f"exact three review renders required, found {render_names}")
        for filename in VIEW_SPECS:
            path = RENDER_DIR / filename
            if path.exists() and png_dimensions(path) != RENDER_SIZE:
                errors.append(f"{filename} dimensions differ")
        if not BLEND_PATH.exists() or not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("blend, manifest, and provenance are required")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("blend backup is forbidden")
    if errors:
        raise RuntimeError("\n".join(errors))
    semantic = scene_semantics()
    print(
        "ODDSWELL_SHARED_SKELETON_CANDIDATE_VALIDATION|result=PASS|"
        f"objects={semantic['object_counts']['total']}|mannequins=1|armatures=1|bones=12|materials=4|"
        "presets=8|tones=4|stature_m=1.8|silhouettes=1|weights=0|deformation=0|"
        "control_rig=0|ik=0|actions=0|clothing=0|exports=0|imports=0"
    )
    return semantic


def render_all(camera):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    for filename, spec in VIEW_SPECS.items():
        camera.location = spec["camera"]
        point_at(camera, (0.0, 0.0, 0.9))
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)
        canonicalize_png(RENDER_DIR / filename)


def write_manifest(semantic):
    renders = []
    for filename, spec in VIEW_SPECS.items():
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}",
            "role": spec["role"],
            "width": RENDER_SIZE[0],
            "height": RENDER_SIZE[1],
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.5bj deterministic neutral mannequin and shared-armature Blender source",
        "status": "production_candidate_source_not_runtime",
        "engine": RENDER_ENGINE,
        "blender_version": bpy.app.version_string,
        "deterministic_builder": Path(__file__).name,
        "contract_source": {
            "file": "../production_candidate_contract.json",
            "sha256": sha256(CONTRACT_PATH),
            "decision": CONTRACT["decision"],
        },
        "review_source": {
            "file": "../../../Reviews/PlayerCharacterSilhouetteReviewSheet/manifest.json",
            "sha256": sha256(REVIEW_MANIFEST_PATH),
        },
        "semantic": semantic,
        "renders": renders,
        "files": {
            "blend": {"file": BLEND_PATH.name, "identity": "semantic_only"},
            "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "boundaries": {
            "mannequins": 1,
            "armatures": 1,
            "skin_weights": 0,
            "deformation": 0,
            "control_rigs": 0,
            "ik": 0,
            "clothing_refits": 0,
            "animations": 0,
            "actions": 0,
            "fbx_exports": 0,
            "unreal_imports": 0,
            "runtime_changes": 0,
            "external_assets": 0,
            "paid_inputs": 0,
            "final_art_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(semantic):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("semantic") != semantic:
        raise RuntimeError("manifest semantic identity differs")
    if manifest.get("contract_source", {}).get("sha256") != sha256(CONTRACT_PATH):
        raise RuntimeError("manifest contract hash differs")
    if manifest.get("review_source", {}).get("sha256") != sha256(REVIEW_MANIFEST_PATH):
        raise RuntimeError("manifest review-source hash differs")
    if manifest.get("blender_version") != bpy.app.version_string or manifest.get("engine") != RENDER_ENGINE:
        raise RuntimeError("manifest Blender identity differs")
    if len(manifest.get("renders", [])) != 3:
        raise RuntimeError("manifest render count differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
            raise RuntimeError(f"render identity differs: {path.name}")
    for key, path in (("builder", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"{key} identity differs")
    zero_fields = (
        "skin_weights", "deformation", "control_rigs", "ik", "clothing_refits", "animations",
        "actions", "fbx_exports", "unreal_imports", "runtime_changes", "external_assets", "paid_inputs",
    )
    if any(manifest["boundaries"].get(field) != 0 for field in zero_fields) or manifest["boundaries"].get("final_art_claim") is not False:
        raise RuntimeError("manifest zero boundary differs")


def main():
    validate_only = "--validate-only" in sys.argv
    focused = "--focused-validate" in sys.argv
    if validate_only or focused:
        semantic = validate_scene(require_outputs=True)
        validate_manifest(semantic)
        marker = "FOCUSED" if focused else "REOPEN"
        print(
            f"ODDSWELL_SHARED_SKELETON_CANDIDATE_{marker}|result=PASS|"
            f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=3"
        )
        return

    collection = reset_scene()
    materials = [make_material(tone_id, rgba8) for tone_id, rgba8 in TONE_RGBA8.items()]
    build_mannequin(collection, materials)
    build_armature(collection)
    camera = build_review_scene(collection)
    scene = bpy.context.scene
    scene["phase"] = "Phase 1L.5bj"
    scene["contract_id"] = CONTRACT["contract_id"]
    scene["status"] = "PRODUCTION_CANDIDATE_SOURCE_NOT_RUNTIME"
    scene["stature_m"] = STATURE_M
    scene["silhouette_count"] = 1
    scene["preset_count"] = 8
    scene["tone_count"] = 4
    scene["skin_weights"] = 0
    scene["deformation"] = 0
    scene["animations"] = 0
    scene["runtime_changes"] = 0
    validate_scene(require_outputs=False)
    render_all(camera)
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    semantic = validate_scene(require_outputs=False)
    write_manifest(semantic)
    validate_scene(require_outputs=True)
    validate_manifest(semantic)
    print(
        "ODDSWELL_SHARED_SKELETON_CANDIDATE_BUILD|result=PASS|artifacts=6|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


if __name__ == "__main__":
    main()
