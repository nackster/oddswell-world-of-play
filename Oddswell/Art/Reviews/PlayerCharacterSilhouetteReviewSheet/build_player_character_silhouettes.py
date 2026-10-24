"""Build and validate the noncanonical Phase 1L.3g character review sheet."""

import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[3]
BLEND_PATH = ROOT / "PlayerCharacterSilhouetteReviewSheet.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
PRESET_SOURCE = REPO_ROOT / "client/OddsWell/Source/OddsWell/CharacterPresetCatalog.cpp"
APPEARANCE_SOURCE = REPO_ROOT / "client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp"
PRESET_SOURCE_SHA256 = "C78132F21C303838BA7F0C0ED75E5A8B81260747F688760DF7E0A7C1E281AB1F"
APPEARANCE_SOURCE_SHA256 = "22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298"

BASE_IDS = ("CharacterPresentationMasculine", "CharacterPresentationFeminine")
TONE_RGBA8 = {
    "tone_1": [246, 218, 194, 255],
    "tone_2": [210, 160, 120, 255],
    "tone_3": [145, 96, 68, 255],
    "tone_4": [82, 52, 38, 255],
}
PRESET_IDS = tuple(
    f"{presentation}_tone_{tone}"
    for presentation in ("masculine", "feminine")
    for tone in range(1, 5)
)
STARTER_IDS = ("starter_offwhite_top", "starter_offwhite_bottom")
SIGNAL_JACKET_ID = "sundale_signal_jacket"
STARTER_RGBA = (0.92, 0.90, 0.82, 1.0)
JACKET_SLATE_RGBA = (0.12, 0.18, 0.22, 1.0)
JACKET_TEAL_RGBA = (0.08, 0.72, 0.68, 1.0)
STARTER_TOP_FIT = {"location": (0.0, 0.0, 1.22), "dimensions": (0.54, 0.285, 0.48)}
STARTER_BOTTOM_FIT = {"location": (0.0, 0.0, 0.87), "dimensions": (0.405, 0.275, 0.22)}
STARTER_LEG_FIT = {"hip_x": 0.155, "knee_x": 0.13, "top_z": 0.87, "bottom_z": 0.57, "radius": 0.096}
JACKET_FIT = {"location": (0.0, -0.012, 1.235), "dimensions": (0.58, 0.315, 0.50)}
JACKET_ACCENT_FIT = {"location": (0.0, -0.171, 1.29), "dimensions": (0.59, 0.018, 0.075)}
SHARED_STATURE_M = 1.80
JOINT_LANDMARKS_M = {
    "ankle": 0.10,
    "knee": 0.53,
    "hip": 0.94,
    "wrist": 0.78,
    "elbow": 1.12,
    "shoulder": 1.45,
    "head_center": 1.66,
    "crown": SHARED_STATURE_M,
}
INSTANCE_X = (-5.4, -1.8, 1.8, 5.4)
INSTANCE_Y = {BASE_IDS[0]: 2.70, BASE_IDS[1]: -2.70}
BOARD_BOUNDS_M = {"x": [-7.45, 7.45], "y": [-3.05, 3.05], "z": [-0.16, 4.32]}
TRIANGLE_CEILING_PER_INSTANCE = 1500
VIEW_ANGLES_DEG = {
    "Unified_EightPresetLineup.png": 18.0,
    "Review_Front.png": 0.0,
    "Review_Side.png": 90.0,
    "Review_Back.png": 180.0,
    "Review_ThreeQuarter.png": -45.0,
}
VIEW_RESOLUTIONS = {
    "Unified_EightPresetLineup.png": (1920, 1080),
    "Review_Front.png": (1600, 900),
    "Review_Side.png": (1600, 900),
    "Review_Back.png": (1600, 900),
    "Review_ThreeQuarter.png": (1600, 900),
}

MATERIALS = {}
GEOMETRY = None
DISPLAY_ROOTS = []


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def png_dimensions(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def rgba8_normalized(rgba8):
    return [round(channel / 255.0, 9) for channel in rgba8]


def make_material(name, rgba):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.86
    material["exact_rgba"] = list(rgba)
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, preset_id, role):
    obj["preset_id"] = preset_id
    obj["asset_role"] = role
    obj["noncanonical"] = True
    obj["gameplay_identical"] = True
    obj["shared_skeleton_target"] = True
    for field in (
        "external_reference",
        "texture",
        "armature",
        "rig",
        "animation",
        "face",
        "hair",
        "person_name",
        "pronoun",
        "deep_creator",
        "extra_outfit",
        "gameplay",
        "ability_inference",
        "wealth_inference",
        "intelligence_inference",
        "behavior_inference",
        "age_inference",
        "ethnicity_inference",
        "athlete_outcome_inference",
    ):
        obj[field] = False
    return obj


def add_root(preset_id, base_id, tone_id, location, outfit_state):
    root = bpy.data.objects.new(f"DISPLAY_ROOT__{preset_id}", None)
    tag(root, preset_id, "DISPLAY_INSTANCE_ROOT")
    root.location = location
    root["base_id"] = base_id
    root["tone_id"] = tone_id
    root["skin_rgba8"] = TONE_RGBA8[tone_id]
    root["outfit_state"] = outfit_state
    root["shared_stature_m"] = SHARED_STATURE_M
    root["shared_joint_landmarks_json"] = json.dumps(JOINT_LANDMARKS_M, sort_keys=True)
    GEOMETRY.objects.link(root)
    DISPLAY_ROOTS.append(root)
    return root


def add_cube(name, location, dimensions, material_name, parent, role):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, parent["preset_id"], role)
    obj.parent = parent
    move_to_collection(obj, GEOMETRY)
    return obj


def add_sphere(name, location, radius, material_name, parent, role):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, parent["preset_id"], role)
    obj.parent = parent
    move_to_collection(obj, GEOMETRY)
    return obj


def add_limb(name, start, end, radius, material_name, parent, role):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    midpoint = (start + end) / 2.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=direction.length, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, parent["preset_id"], role)
    obj.parent = parent
    move_to_collection(obj, GEOMETRY)
    return obj


def add_landmark(parent, name, x, y, z):
    marker = bpy.data.objects.new(f"LANDMARK__{parent['preset_id']}__{name}", None)
    tag(marker, parent["preset_id"], "SHARED_JOINT_LANDMARK")
    marker.location = (x, y, z)
    marker.empty_display_type = "PLAIN_AXES"
    marker.empty_display_size = 0.025
    marker["landmark_name"] = name
    marker["landmark_height_m"] = z
    marker.parent = parent
    GEOMETRY.objects.link(marker)


def add_mannequin(root):
    base_id = root["base_id"]
    preset_id = root["preset_id"]
    skin = f"skin_{root['tone_id']}"
    masculine = base_id == BASE_IDS[0]
    shoulder_x = 0.255 if masculine else 0.235
    hip_x = 0.145 if masculine else 0.165
    torso_width = 0.48 if masculine else 0.43
    hip_width = 0.33 if masculine else 0.37

    add_sphere(f"{preset_id}__HEAD", (0.0, 0.0, JOINT_LANDMARKS_M["head_center"]), 0.14, skin, root, "FACELESS_HEAD")
    add_limb(f"{preset_id}__NECK", (0.0, 0.0, 1.47), (0.0, 0.0, 1.55), 0.075, skin, root, "NECK")
    add_cube(f"{preset_id}__TORSO", (0.0, 0.0, 1.215), (torso_width, 0.25, 0.49), skin, root, "NEUTRAL_BODY_BASE")
    add_cube(f"{preset_id}__PELVIS", (0.0, 0.0, 0.91), (hip_width, 0.24, 0.18), skin, root, "NEUTRAL_BODY_BASE")

    for side in (-1.0, 1.0):
        shoulder = (side * shoulder_x, 0.0, JOINT_LANDMARKS_M["shoulder"])
        elbow = (side * (shoulder_x + 0.035), 0.0, JOINT_LANDMARKS_M["elbow"])
        wrist = (side * (shoulder_x + 0.020), 0.0, JOINT_LANDMARKS_M["wrist"])
        add_limb(f"{preset_id}__UPPER_ARM_{side:+.0f}", shoulder, elbow, 0.064, skin, root, "NEUTRAL_ARM")
        add_limb(f"{preset_id}__FOREARM_{side:+.0f}", elbow, wrist, 0.055, skin, root, "NEUTRAL_ARM")
        add_sphere(f"{preset_id}__HAND_{side:+.0f}", (wrist[0], 0.0, wrist[2] - 0.055), 0.06, skin, root, "NEUTRAL_HAND")

        hip = (side * hip_x, 0.0, JOINT_LANDMARKS_M["hip"])
        knee = (side * 0.13, 0.0, JOINT_LANDMARKS_M["knee"])
        ankle = (side * 0.13, 0.0, JOINT_LANDMARKS_M["ankle"])
        add_limb(f"{preset_id}__THIGH_{side:+.0f}", hip, knee, 0.085, skin, root, "NEUTRAL_LEG")
        add_limb(f"{preset_id}__SHIN_{side:+.0f}", knee, ankle, 0.07, skin, root, "NEUTRAL_LEG")
        add_cube(f"{preset_id}__SHOE_{side:+.0f}", (side * 0.13, -0.055, 0.055), (0.16, 0.28, 0.11), "shoe_charcoal", root, "NEUTRAL_SHOE")

    for name, height in JOINT_LANDMARKS_M.items():
        add_landmark(root, name, 0.0, 0.0, height)

    # One approved starter proxy design is reused across both bases and all tones.
    add_cube(f"{preset_id}__STARTER_TOP", STARTER_TOP_FIT["location"], STARTER_TOP_FIT["dimensions"], "starter_offwhite", root, "STARTER_OFFWHITE_TOP_PROXY")
    add_cube(f"{preset_id}__STARTER_BOTTOM", STARTER_BOTTOM_FIT["location"], STARTER_BOTTOM_FIT["dimensions"], "starter_offwhite", root, "STARTER_OFFWHITE_BOTTOM_PROXY")
    for side in (-1.0, 1.0):
        add_limb(
            f"{preset_id}__STARTER_LEG_{side:+.0f}",
            (side * STARTER_LEG_FIT["hip_x"], 0.0, STARTER_LEG_FIT["top_z"]),
            (side * STARTER_LEG_FIT["knee_x"], 0.0, STARTER_LEG_FIT["bottom_z"]),
            STARTER_LEG_FIT["radius"],
            "starter_offwhite",
            root,
            "STARTER_OFFWHITE_BOTTOM_PROXY",
        )

    if root["outfit_state"] == "signal_jacket":
        add_cube(f"{preset_id}__SIGNAL_JACKET", JACKET_FIT["location"], JACKET_FIT["dimensions"], "jacket_slate", root, "SIGNAL_JACKET_PROXY")
        add_cube(f"{preset_id}__SIGNAL_JACKET_ACCENT", JACKET_ACCENT_FIT["location"], JACKET_ACCENT_FIT["dimensions"], "jacket_teal", root, "SIGNAL_JACKET_ACCENT_PROXY")


def add_review_label(text, location, size, material_name, role):
    curve = bpy.data.curves.new(f"LABEL_DATA__{text}", "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.004
    obj = bpy.data.objects.new(f"LABEL__{text}", curve)
    tag(obj, "", role)
    obj.location = location
    obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    obj.data.materials.append(MATERIALS[material_name])
    obj["label_body"] = text
    GEOMETRY.objects.link(obj)
    return obj


def add_label_plate(label_id, text, location, dimensions, size, parent, plate_role, text_role, accent_material):
    plate = add_cube(f"LABEL_PLATE__{label_id}", location, dimensions, "board_dark", parent, plate_role)
    plate["label_id"] = label_id
    add_cube(
        f"LABEL_ACCENT__{label_id}",
        (location[0], location[1] - dimensions[1] / 2.0 - 0.008, location[2] - dimensions[2] / 2.0 + 0.025),
        (dimensions[0] - 0.08, 0.012, 0.035),
        accent_material,
        parent,
        "LABEL_PLATE_ACCENT",
    )["label_id"] = label_id
    label = add_review_label(
        text,
        (location[0], location[1] - dimensions[1] / 2.0 - 0.016, location[2]),
        size,
        "starter_offwhite",
        text_role,
    )
    label["label_id"] = label_id


def point_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_scene():
    global GEOMETRY
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)
    for curve in list(bpy.data.curves):
        bpy.data.curves.remove(curve)
    default = bpy.data.collections.get("Collection")
    default.name = "BOARD_LIGHTS_CAMERAS"
    GEOMETRY = bpy.data.collections.new("CHARACTER_REVIEW_GEOMETRY")
    bpy.context.scene.collection.children.link(GEOMETRY)
    DISPLAY_ROOTS.clear()

    MATERIALS.clear()
    MATERIALS.update({
        "skin_tone_1": make_material("skin_tone_1", rgba8_normalized(TONE_RGBA8["tone_1"])),
        "skin_tone_2": make_material("skin_tone_2", rgba8_normalized(TONE_RGBA8["tone_2"])),
        "skin_tone_3": make_material("skin_tone_3", rgba8_normalized(TONE_RGBA8["tone_3"])),
        "skin_tone_4": make_material("skin_tone_4", rgba8_normalized(TONE_RGBA8["tone_4"])),
        "starter_offwhite": make_material("starter_offwhite", STARTER_RGBA),
        "jacket_slate": make_material("jacket_slate", JACKET_SLATE_RGBA),
        "jacket_teal": make_material("jacket_teal", JACKET_TEAL_RGBA),
        "board_warm": make_material("board_warm", (0.58, 0.52, 0.43, 1.0)),
        "board_dark": make_material("board_dark", (0.10, 0.12, 0.13, 1.0)),
        "row_cobalt": make_material("row_cobalt", (0.19, 0.37, 0.47, 1.0)),
        "row_terracotta": make_material("row_terracotta", (0.65, 0.37, 0.28, 1.0)),
        "shoe_charcoal": make_material("shoe_charcoal", (0.12, 0.13, 0.14, 1.0)),
    })

    board_root = bpy.data.objects.new("BOARD_ROOT", None)
    tag(board_root, "", "BOARD_ROOT")
    GEOMETRY.objects.link(board_root)
    add_cube("REVIEW_BOARD", (0.0, 0.0, -0.10), (14.8, 6.0, 0.20), "board_warm", board_root, "REVIEW_BOARD")
    add_cube("ROW_BAND_MASCULINE", (0.0, 2.55, 0.025), (14.5, 0.26, 0.05), "row_cobalt", board_root, "PRESENTATION_ROW_CUE")
    add_cube("ROW_BAND_FEMININE", (0.0, -2.55, 0.025), (14.5, 0.26, 0.05), "row_terracotta", board_root, "PRESENTATION_ROW_CUE")

    for presentation_index, base_id in enumerate(BASE_IDS):
        prefix = "masculine" if presentation_index == 0 else "feminine"
        for tone_index, tone_id in enumerate(TONE_RGBA8, start=1):
            preset_id = f"{prefix}_tone_{tone_index}"
            outfit_state = "signal_jacket" if tone_index == 4 else "starter_offwhite"
            root = add_root(preset_id, base_id, tone_id, (INSTANCE_X[tone_index - 1], INSTANCE_Y[base_id], 0.0), outfit_state)
            add_mannequin(root)

    for base_index, (base_id, accent) in enumerate(((BASE_IDS[0], "row_cobalt"), (BASE_IDS[1], "row_terracotta"))):
        add_label_plate(
            base_id,
            base_id,
            (0.0, 2.86, 4.15 - base_index),
            (5.8, 0.08, 0.30),
            0.16,
            board_root,
            "APPROVED_PRESENTATION_LABEL_PLATE",
            "APPROVED_PRESENTATION_LABEL",
            accent,
        )
    for presentation_index, base_id in enumerate(BASE_IDS):
        prefix = "masculine" if presentation_index == 0 else "feminine"
        accent = "row_cobalt" if presentation_index == 0 else "row_terracotta"
        for tone_index, tone_id in enumerate(TONE_RGBA8, start=1):
            preset_id = f"{prefix}_tone_{tone_index}"
            add_label_plate(
                preset_id,
                f"{preset_id} | {tone_id}",
                (INSTANCE_X[tone_index - 1], 2.86, 3.72 - presentation_index),
                (3.18, 0.08, 0.30),
                0.125,
                board_root,
                "PRESET_TONE_LABEL_PLATE",
                "PRESET_TONE_ID_LABEL",
                accent,
            )

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.065, 0.070)
    scene["phase"] = "Phase 1L.3g"
    scene["status"] = "NONCANONICAL_CHARACTER_SILHOUETTE_REVIEW"
    scene["display_count"] = 8
    scene["shared_stature_m"] = SHARED_STATURE_M
    scene["joint_landmarks_json"] = json.dumps(JOINT_LANDMARKS_M, sort_keys=True)
    scene["gameplay_identical"] = True
    scene["shared_skeleton_target"] = True
    for field in ("armatures_count", "rigs_count", "animations_count", "faces_count", "hair_count", "names_count", "pronouns_count", "deep_creator_count", "extra_outfits_count", "external_refs_count", "textures_count", "gameplay_changes_count", "ability_inferences_count", "wealth_inferences_count", "intelligence_inferences_count", "behavior_inferences_count", "age_inferences_count", "ethnicity_inferences_count", "athlete_outcome_inferences_count"):
        scene[field] = 0
    for field in ("production_character_created", "production_map_changed", "production_client_changed", "package_changed"):
        scene[field] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, -6.0, 10.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 1350.0
    key.data.shape = "RECTANGLE"
    key.data.size = 9.0
    key.data.size_y = 6.0
    point_camera(key, key.location, (0.0, 0.0, 0.9))
    bpy.ops.object.light_add(type="AREA", location=(0.0, 6.0, 6.0))
    fill = bpy.context.object
    fill.name = "LIGHT_FILL"
    fill.data.energy = 750.0
    fill.data.size = 8.0
    point_camera(fill, fill.location, (0.0, 0.0, 1.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 8.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.45, -0.30, -0.55)
    sun.data.energy = 1.8

    camera_data = bpy.data.cameras.new("CAMERA_DATA__CHARACTER_SHEET")
    camera = bpy.data.objects.new("CAMERA__CHARACTER_SHEET", camera_data)
    default.objects.link(camera)
    point_camera(camera, (0.0, -22.0, 10.5), (0.0, 0.0, 1.65))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 16.2
    scene.camera = camera


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def instance_triangle_counts():
    counts = defaultdict(int)
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.get("preset_id") in PRESET_IDS:
            counts[obj["preset_id"]] += mesh_triangles(obj)
    return dict(counts)


def clothing_transform_signature(preset_id, roles):
    signature = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.get("preset_id") != preset_id or obj.get("asset_role") not in roles:
            continue
        signature.append({
            "role": obj["asset_role"],
            "location_m": [round(value, 6) for value in obj.location],
            "rotation_rad": [round(value, 6) for value in obj.rotation_euler],
            "dimensions_m": [round(value, 6) for value in obj.dimensions],
        })
    return sorted(signature, key=lambda item: (item["role"], item["location_m"], item["dimensions_m"]))


def projected_bbox(obj, scene, camera):
    points = [world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
    return (min(point.x for point in points), min(point.y for point in points), max(point.x for point in points), max(point.y for point in points))


def merged_projected_bbox(objects, scene, camera):
    boxes = [projected_bbox(obj, scene, camera) for obj in objects]
    return (min(box[0] for box in boxes), min(box[1] for box in boxes), max(box[2] for box in boxes), max(box[3] for box in boxes))


def boxes_overlap(first, second, gap=0.002):
    return not (first[2] + gap <= second[0] or second[2] + gap <= first[0] or first[3] + gap <= second[1] or second[3] + gap <= first[1])


def validate_scene(require_outputs):
    errors = []
    if not PRESET_SOURCE.exists() or sha256(PRESET_SOURCE) != PRESET_SOURCE_SHA256:
        errors.append("production preset source hash differs from the extracted contract")
    if not APPEARANCE_SOURCE.exists() or sha256(APPEARANCE_SOURCE) != APPEARANCE_SOURCE_SHA256:
        errors.append("production appearance-color source hash differs from the extracted contract")
    objects = list(bpy.data.objects)
    roots = [obj for obj in objects if obj.type == "EMPTY" and obj.get("asset_role") == "DISPLAY_INSTANCE_ROOT"]
    if len(roots) != 8 or {obj.get("preset_id") for obj in roots} != set(PRESET_IDS):
        errors.append("exactly eight current preset display roots are required")
    if Counter(obj.get("base_id") for obj in roots) != Counter({BASE_IDS[0]: 4, BASE_IDS[1]: 4}):
        errors.append("exactly four instances per approved presentation base are required")
    if Counter(obj.get("tone_id") for obj in roots) != Counter({tone_id: 2 for tone_id in TONE_RGBA8}):
        errors.append("each exact tone identity must appear once per base")
    if any(list(obj.get("skin_rgba8")) != TONE_RGBA8[obj.get("tone_id")] for obj in roots):
        errors.append("display root tone RGBA differs from the production catalog")
    if any(obj.get("shared_stature_m") != SHARED_STATURE_M or json.loads(obj.get("shared_joint_landmarks_json", "{}")) != JOINT_LANDMARKS_M for obj in roots):
        errors.append("shared stature or joint landmarks differ")
    if Counter(obj.get("outfit_state") for obj in roots) != Counter({"starter_offwhite": 6, "signal_jacket": 2}):
        errors.append("outfit review must be six starter plus one jacket fit per base")

    meshes = [obj for obj in objects if obj.type == "MESH" and obj.get("preset_id") in PRESET_IDS]
    if {obj.get("preset_id") for obj in meshes} != set(PRESET_IDS):
        errors.append("each display root requires primitive mesh geometry")
    forbidden = ("external_reference", "texture", "armature", "rig", "animation", "face", "hair", "person_name", "pronoun", "deep_creator", "extra_outfit", "gameplay", "ability_inference", "wealth_inference", "intelligence_inference", "behavior_inference", "age_inference", "ethnicity_inference", "athlete_outcome_inference")
    if any(obj.get("gameplay_identical") is not True or obj.get("shared_skeleton_target") is not True or any(obj.get(field) is not False for field in forbidden) for obj in meshes):
        errors.append("mesh review boundaries differ")
    if any(obj.type in {"ARMATURE", "VOLUME", "META"} for obj in objects):
        errors.append("armatures, volumes, and metaballs are forbidden")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, textures, and source images are forbidden")

    triangles = instance_triangle_counts()
    if set(triangles) != set(PRESET_IDS) or any(not 0 < count <= TRIANGLE_CEILING_PER_INSTANCE for count in triangles.values()):
        errors.append("per-instance triangle counts exceed the review ceiling")
    starter_roles = Counter(obj.get("asset_role") for obj in meshes)
    if starter_roles["STARTER_OFFWHITE_TOP_PROXY"] != 8 or starter_roles["STARTER_OFFWHITE_BOTTOM_PROXY"] != 24:
        errors.append("starter proxy fit must be present on all eight displays")
    if starter_roles["SIGNAL_JACKET_PROXY"] != 2 or starter_roles["SIGNAL_JACKET_ACCENT_PROXY"] != 2:
        errors.append("Signal Jacket proxy must be fitted once per base")
    starter_signatures = [
        clothing_transform_signature(preset_id, {"STARTER_OFFWHITE_TOP_PROXY", "STARTER_OFFWHITE_BOTTOM_PROXY"})
        for preset_id in PRESET_IDS
    ]
    if not starter_signatures[0] or any(signature != starter_signatures[0] for signature in starter_signatures[1:]):
        errors.append("starter top/bottom dimensions and transforms must match across all bases and tones")
    jacket_signatures = [
        clothing_transform_signature(preset_id, {"SIGNAL_JACKET_PROXY", "SIGNAL_JACKET_ACCENT_PROXY"})
        for preset_id in ("masculine_tone_4", "feminine_tone_4")
    ]
    if not jacket_signatures[0] or jacket_signatures[0] != jacket_signatures[1]:
        errors.append("Signal Jacket dimensions and transforms must match across both bases")
    landmarks = [obj for obj in objects if obj.get("asset_role") == "SHARED_JOINT_LANDMARK"]
    if len(landmarks) != 8 * len(JOINT_LANDMARKS_M) or Counter(obj.get("landmark_name") for obj in landmarks) != Counter({name: 8 for name in JOINT_LANDMARKS_M}):
        errors.append("shared landmark identities/counts differ")

    expected_label_bodies = {BASE_IDS[0], BASE_IDS[1]} | {
        f"{preset_id} | tone_{1 + index % 4}" for index, preset_id in enumerate(PRESET_IDS)
    }
    label_objects = [obj for obj in objects if obj.type == "FONT"]
    label_plates = [obj for obj in objects if obj.type == "MESH" and obj.get("asset_role") in {"APPROVED_PRESENTATION_LABEL_PLATE", "PRESET_TONE_LABEL_PLATE"}]
    if len(label_objects) != 10 or {obj.get("label_body") for obj in label_objects} != expected_label_bodies:
        errors.append("exactly two base labels and eight exact preset/tone labels are required")
    if len(label_plates) != 10 or {obj.get("label_id") for obj in label_plates} != set(BASE_IDS) | set(PRESET_IDS):
        errors.append("each exact base or preset/tone label requires one dedicated plate")
    if Counter(obj.get("asset_role") for obj in label_plates) != Counter({"APPROVED_PRESENTATION_LABEL_PLATE": 2, "PRESET_TONE_LABEL_PLATE": 8}):
        errors.append("label plate roles/counts differ")
    if len([obj for obj in objects if obj.get("asset_role") == "LABEL_PLATE_ACCENT"]) != 10:
        errors.append("each label plate requires one high-contrast row accent")

    camera = next((obj for obj in objects if obj.type == "CAMERA" and obj.name == "CAMERA__CHARACTER_SHEET"), None)
    if camera and len(label_plates) == 10:
        silhouette_by_preset = {
            preset_id: [obj for obj in meshes if obj.get("preset_id") == preset_id]
            for preset_id in PRESET_IDS
        }
        for view_name, angle in VIEW_ANGLES_DEG.items():
            for root in roots:
                root.rotation_euler[2] = math.radians(angle)
            bpy.context.view_layer.update()
            plate_boxes = {plate.name: projected_bbox(plate, bpy.context.scene, camera) for plate in label_plates}
            silhouette_boxes = {
                preset_id: merged_projected_bbox(preset_meshes, bpy.context.scene, camera)
                for preset_id, preset_meshes in silhouette_by_preset.items()
            }
            if any(box[0] < 0.015 or box[1] < 0.015 or box[2] > 0.985 or box[3] > 0.985 for box in plate_boxes.values()):
                errors.append(f"{view_name} clips a dedicated label plate")
            plate_items = list(plate_boxes.items())
            if any(boxes_overlap(first_box, second_box) for index, (_first_name, first_box) in enumerate(plate_items) for _second_name, second_box in plate_items[index + 1:]):
                errors.append(f"{view_name} overlaps dedicated label plates")
            label_silhouette_overlaps = [
                f"{plate_name}/{preset_id}"
                for plate_name, plate_box in plate_boxes.items()
                for preset_id, silhouette_box in silhouette_boxes.items()
                if boxes_overlap(plate_box, silhouette_box)
            ]
            if label_silhouette_overlaps:
                errors.append(f"{view_name} overlaps label/silhouette pairs: {label_silhouette_overlaps}")
            silhouette_items = list(silhouette_boxes.items())
            silhouette_overlaps = [
                f"{first_id}/{second_id}"
                for index, (first_id, first_box) in enumerate(silhouette_items)
                for second_id, second_box in silhouette_items[index + 1:]
                if boxes_overlap(first_box, second_box)
            ]
            if silhouette_overlaps:
                errors.append(f"{view_name} overlaps complete display silhouettes: {silhouette_overlaps}")
        for root in roots:
            root.rotation_euler[2] = 0.0
        bpy.context.view_layer.update()
    elif camera is None:
        errors.append("character-sheet camera is missing")

    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if scene.get("display_count") != 8 or scene.get("shared_stature_m") != SHARED_STATURE_M or scene.get("gameplay_identical") is not True or scene.get("shared_skeleton_target") is not True:
        errors.append("scene fairness contract differs")
    zero_fields = ("armatures_count", "rigs_count", "animations_count", "faces_count", "hair_count", "names_count", "pronouns_count", "deep_creator_count", "extra_outfits_count", "external_refs_count", "textures_count", "gameplay_changes_count", "ability_inferences_count", "wealth_inferences_count", "intelligence_inferences_count", "behavior_inferences_count", "age_inferences_count", "ethnicity_inferences_count", "athlete_outcome_inferences_count")
    if any(scene.get(field) != 0 for field in zero_fields):
        errors.append("all zero-count boundaries must remain zero")
    if any(scene.get(field) is not False for field in ("production_character_created", "production_map_changed", "production_client_changed", "package_changed")):
        errors.append("production boundaries must remain false")

    if require_outputs:
        files = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if files != sorted(VIEW_ANGLES_DEG):
            errors.append(f"expected exactly five review PNGs, found {files}")
        for filename, resolution in VIEW_RESOLUTIONS.items():
            path = RENDER_DIR / filename
            if path.exists() and png_dimensions(path) != resolution:
                errors.append(f"{filename} dimensions differ")
        if not BLEND_PATH.exists() or not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("Blend, manifest, and provenance are required")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("Blender backup output is forbidden")
    if errors:
        raise RuntimeError("\n".join(errors))
    print(
        "ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_VALIDATION|result=PASS|bases=2|tones=4|displays=8|"
        "views=1_unified+4_review|stature_m=1.8|joint_landmarks=shared|gameplay_identical=true|"
        "shared_skeleton_target=true|armatures=0|rigs=0|animations=0|faces=0|hair=0|names=0|"
        "pronouns=0|deep_creator=0|extra_outfits=0|external_refs=0|textures=0|gameplay=0|"
        "label_plates=10|label_overlaps=0|silhouette_overlaps=0|demographic_inferences=0|engine=eevee"
    )
    return triangles


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    for filename, angle in VIEW_ANGLES_DEG.items():
        for root in DISPLAY_ROOTS:
            root.rotation_euler[2] = math.radians(angle)
        width, height = VIEW_RESOLUTIONS[filename]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)
    for root in DISPLAY_ROOTS:
        root.rotation_euler[2] = 0.0


def write_manifest(triangles):
    roots = sorted(
        (obj for obj in bpy.data.objects if obj.get("asset_role") == "DISPLAY_INSTANCE_ROOT"),
        key=lambda obj: PRESET_IDS.index(obj["preset_id"]),
    )
    renders = []
    for filename, angle in VIEW_ANGLES_DEG.items():
        path = RENDER_DIR / filename
        width, height = VIEW_RESOLUTIONS[filename]
        renders.append({
            "file": f"renders/{filename}",
            "role": "UNIFIED_EIGHT_PRESET_LINEUP" if filename.startswith("Unified") else filename.removeprefix("Review_").removesuffix(".png").upper(),
            "display_rotation_deg": angle,
            "complete_display_count": 8,
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3g Player-character silhouette, proportion, and outfit-fit review sheet",
        "status": "noncanonical_owner_review_sheet",
        "engine": "BLENDER_EEVEE_NEXT",
        "deterministic_builder": Path(__file__).name,
        "source_contract": {
            "pre_phase_head": "bf8ccbbf0a185aa61f73a806fb672953f56f2991",
            "preset_source": "client/OddsWell/Source/OddsWell/CharacterPresetCatalog.cpp",
            "preset_source_lines": [9, 10, 16, 17, 18, 19, 20, 21, 22, 23],
            "preset_source_sha256": PRESET_SOURCE_SHA256,
            "appearance_color_source": "client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp",
            "appearance_color_source_lines": [80, 81, 82],
            "appearance_color_source_sha256": APPEARANCE_SOURCE_SHA256,
        },
        "review_contract": {
            "base_ids": list(BASE_IDS),
            "base_count": 2,
            "tone_rgba8": TONE_RGBA8,
            "tone_rgba_normalized": {tone: rgba8_normalized(rgba) for tone, rgba in TONE_RGBA8.items()},
            "preset_ids": list(PRESET_IDS),
            "display_count": 8,
            "shared_stature_m": SHARED_STATURE_M,
            "shared_joint_landmarks_m": JOINT_LANDMARKS_M,
            "gameplay_identical": True,
            "shared_skeleton_target": True,
            "triangle_counts": triangles,
            "triangle_ceiling_per_display": TRIANGLE_CEILING_PER_INSTANCE,
            "bounds_m": BOARD_BOUNDS_M,
            "primitive_mannequin_geometry_only": True,
        },
        "display_instances": [
            {
                "preset_id": root["preset_id"],
                "base_id": root["base_id"],
                "tone_id": root["tone_id"],
                "skin_rgba8": list(root["skin_rgba8"]),
                "outfit_state": root["outfit_state"],
            }
            for root in roots
        ],
        "outfit_fit": {
            "starter_proxy_design_count": 1,
            "starter_item_ids": list(STARTER_IDS),
            "starter_rgba": list(STARTER_RGBA),
            "starter_fit_display_count": 8,
            "signal_jacket_proxy_design_count": 1,
            "signal_jacket_item_id": SIGNAL_JACKET_ID,
            "signal_jacket_slate_rgba": list(JACKET_SLATE_RGBA),
            "signal_jacket_teal_rgba": list(JACKET_TEAL_RGBA),
            "signal_jacket_fit_display_count": 2,
            "signal_jacket_fit_base_ids": list(BASE_IDS),
            "starter_transform_signature": clothing_transform_signature(PRESET_IDS[0], {"STARTER_OFFWHITE_TOP_PROXY", "STARTER_OFFWHITE_BOTTOM_PROXY"}),
            "signal_jacket_transform_signature": clothing_transform_signature("masculine_tone_4", {"SIGNAL_JACKET_PROXY", "SIGNAL_JACKET_ACCENT_PROXY"}),
            "fit_offsets_shared_between_bases": True,
        },
        "label_contract": {
            "base_label_bodies": list(BASE_IDS),
            "preset_tone_label_bodies": [f"{preset_id} | tone_{1 + index % 4}" for index, preset_id in enumerate(PRESET_IDS)],
            "dedicated_plate_count": 10,
            "high_contrast": True,
            "projected_frame_safe_all_views": True,
            "projected_plate_overlap_count_all_views": 0,
            "projected_plate_silhouette_overlap_count_all_views": 0,
            "projected_silhouette_overlap_count_all_views": 0,
        },
        "renders": renders,
        "boundaries": {
            "armatures": 0, "rigs": 0, "animations": 0, "faces": 0, "hair": 0,
            "person_names": 0, "pronouns": 0, "deep_creator": 0, "extra_outfits": 0,
            "external_references": 0, "textures": 0, "gameplay_changes": 0,
            "ability_inferences": 0, "wealth_inferences": 0, "intelligence_inferences": 0,
            "behavior_inferences": 0, "age_inferences": 0, "ethnicity_inferences": 0,
            "athlete_outcome_inferences": 0,
            "production_character_created": False, "production_map_changed": False,
            "production_client_changed": False, "package_changed": False,
        },
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "limitations": [
            "review-only faceless primitive mannequins; not production people, skeletal meshes, rigging, animation, or final character art",
            "shared landmarks are a visual compatibility target, not a completed skeleton or deformation proof",
            "owner approval and a separate production-promotion gate are required before character modeling or rigging",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(triangles):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    source = manifest.get("source_contract", {})
    if source.get("preset_source_sha256") != PRESET_SOURCE_SHA256 or source.get("appearance_color_source_sha256") != APPEARANCE_SOURCE_SHA256:
        raise RuntimeError("manifest production source hashes differ")
    contract = manifest.get("review_contract", {})
    if contract.get("base_ids") != list(BASE_IDS) or contract.get("preset_ids") != list(PRESET_IDS) or contract.get("display_count") != 8:
        raise RuntimeError("manifest identity/count contract differs")
    if contract.get("tone_rgba8") != TONE_RGBA8 or contract.get("shared_stature_m") != SHARED_STATURE_M or contract.get("shared_joint_landmarks_m") != JOINT_LANDMARKS_M:
        raise RuntimeError("manifest tone/stature/landmark contract differs")
    if contract.get("triangle_counts") != triangles or contract.get("gameplay_identical") is not True or contract.get("shared_skeleton_target") is not True:
        raise RuntimeError("manifest fairness/geometry contract differs")
    outfit = manifest.get("outfit_fit", {})
    if outfit.get("starter_proxy_design_count") != 1 or outfit.get("starter_item_ids") != list(STARTER_IDS) or outfit.get("signal_jacket_proxy_design_count") != 1 or outfit.get("signal_jacket_item_id") != SIGNAL_JACKET_ID or outfit.get("signal_jacket_fit_base_ids") != list(BASE_IDS):
        raise RuntimeError("manifest outfit-fit contract differs")
    if outfit.get("starter_transform_signature") != clothing_transform_signature(PRESET_IDS[0], {"STARTER_OFFWHITE_TOP_PROXY", "STARTER_OFFWHITE_BOTTOM_PROXY"}) or outfit.get("signal_jacket_transform_signature") != clothing_transform_signature("masculine_tone_4", {"SIGNAL_JACKET_PROXY", "SIGNAL_JACKET_ACCENT_PROXY"}):
        raise RuntimeError("manifest outfit dimensions/transforms differ")
    labels = manifest.get("label_contract", {})
    if labels.get("base_label_bodies") != list(BASE_IDS) or labels.get("preset_tone_label_bodies") != [f"{preset_id} | tone_{1 + index % 4}" for index, preset_id in enumerate(PRESET_IDS)] or labels.get("dedicated_plate_count") != 10:
        raise RuntimeError("manifest label identity/count contract differs")
    if labels.get("high_contrast") is not True or labels.get("projected_frame_safe_all_views") is not True or any(labels.get(field) != 0 for field in ("projected_plate_overlap_count_all_views", "projected_plate_silhouette_overlap_count_all_views", "projected_silhouette_overlap_count_all_views")):
        raise RuntimeError("manifest label visibility contract differs")
    boundaries = manifest.get("boundaries", {})
    if any(boundaries.get(field) != 0 for field in ("armatures", "rigs", "animations", "faces", "hair", "person_names", "pronouns", "deep_creator", "extra_outfits", "external_references", "textures", "gameplay_changes", "ability_inferences", "wealth_inferences", "intelligence_inferences", "behavior_inferences", "age_inferences", "ethnicity_inferences", "athlete_outcome_inferences")):
        raise RuntimeError("manifest zero boundaries differ")
    if any(boundaries.get(field) is not False for field in ("production_character_created", "production_map_changed", "production_client_changed", "package_changed")):
        raise RuntimeError("manifest production boundaries differ")
    if len(manifest.get("renders", [])) != 5 or any(render.get("complete_display_count") != 8 for render in manifest["renders"]):
        raise RuntimeError("manifest view contract differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
            raise RuntimeError(f"render hash differs: {path.name}")
    for key, path in (("blend", BLEND_PATH), ("script", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"artifact hash differs: {path.name}")


def main():
    validate_only = "--validate-only" in sys.argv
    focused = "--focused-validate" in sys.argv
    if validate_only or focused:
        triangles = validate_scene(require_outputs=True)
        validate_manifest(triangles)
        marker = "FOCUSED" if focused else "REOPEN"
        print(f"ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_{marker}|result=PASS|manifest=true|render_hashes=5|manual_input=false")
        return
    build_scene()
    validate_scene(require_outputs=False)
    render_all()
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    triangles = validate_scene(require_outputs=False)
    write_manifest(triangles)
    validate_scene(require_outputs=True)
    validate_manifest(triangles)
    print("ODDSWELL_PLAYER_CHARACTER_SILHOUETTES_BUILD|result=PASS|artifacts=8|manual_input=false")


if __name__ == "__main__":
    main()
