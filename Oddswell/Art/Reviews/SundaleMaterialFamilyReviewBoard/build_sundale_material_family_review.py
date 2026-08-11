"""Build and validate the noncanonical Phase 1L.3h material-family review board."""

import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleMaterialFamilyReviewBoard.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

PALETTE = {
    "#D8C8A9": (0.847059, 0.784314, 0.662745, 1.0),
    "#A65F47": (0.650980, 0.372549, 0.278431, 1.0),
    "#B9A783": (0.725490, 0.654902, 0.513725, 1.0),
    "#6D7F62": (0.427451, 0.498039, 0.384314, 1.0),
    "#315F79": (0.192157, 0.372549, 0.474510, 1.0),
    "#C46D3B": (0.768627, 0.427451, 0.231373, 1.0),
    "#4D5051": (0.301961, 0.313725, 0.317647, 1.0),
}

# Exact accepted family order. The optional accent is also an accepted palette anchor.
FAMILIES = (
    ("MATERIAL_FAMILY__WARM_LIMESTONE_STUCCO", "warm limestone stucco", "#D8C8A9", "NOISE", None),
    ("MATERIAL_FAMILY__MUTED_TERRACOTTA_STUCCO", "muted terracotta stucco", "#A65F47", "NOISE", None),
    ("MATERIAL_FAMILY__TEXTURED_CONCRETE", "textured concrete", "#D8C8A9", "NOISE", "#4D5051"),
    ("MATERIAL_FAMILY__SAND_CONCRETE", "sand concrete", "#B9A783", "NOISE", None),
    ("MATERIAL_FAMILY__BRICK_PAVERS", "brick pavers", "#A65F47", "BRICK", "#C46D3B"),
    ("MATERIAL_FAMILY__CHARCOAL_ASPHALT_SERVICE_SURFACE", "charcoal asphalt/service surface", "#4D5051", "NOISE", None),
    ("MATERIAL_FAMILY__PAINTED_METAL", "painted metal", "#C46D3B", "WAVE", None),
    ("MATERIAL_FAMILY__STOREFRONT_GLASS", "storefront glass", "#315F79", "NOISE", None),
    ("MATERIAL_FAMILY__COURT_SURFACE_LINES", "court surface/lines", "#315F79", "WAVE", "#D8C8A9"),
    ("MATERIAL_FAMILY__FOLIAGE_TRUNK", "foliage/trunk", "#6D7F62", "NOISE", "#B9A783"),
)
FAMILY_IDS = tuple(item[0] for item in FAMILIES)
FAMILY_BY_ID = {item[0]: item for item in FAMILIES}
PAIR_CONTRACT = (
    ("PAIR_01_STUCCO", FAMILY_IDS[0:2], "Pair_01_Stucco.png"),
    ("PAIR_02_CONCRETE", FAMILY_IDS[2:4], "Pair_02_Concrete.png"),
    ("PAIR_03_GROUND", FAMILY_IDS[4:6], "Pair_03_Ground.png"),
    ("PAIR_04_FACADE", FAMILY_IDS[6:8], "Pair_04_Facade.png"),
    ("PAIR_05_COURT_LANDSCAPE", FAMILY_IDS[8:10], "Pair_05_CourtLandscape.png"),
)
SHORT_LABELS = {
    FAMILY_IDS[0]: "LIMESTONE\nSTUCCO",
    FAMILY_IDS[1]: "TERRACOTTA\nSTUCCO",
    FAMILY_IDS[2]: "TEXTURED\nCONCRETE",
    FAMILY_IDS[3]: "SAND\nCONCRETE",
    FAMILY_IDS[4]: "BRICK\nPAVERS",
    FAMILY_IDS[5]: "ASPHALT /\nSERVICE",
    FAMILY_IDS[6]: "PAINTED\nMETAL",
    FAMILY_IDS[7]: "STOREFRONT\nGLASS",
    FAMILY_IDS[8]: "COURT SURFACE /\nLINES",
    FAMILY_IDS[9]: "FOLIAGE /\nTRUNK",
}
COLUMN_X = (-8.6, -4.3, 0.0, 4.3, 8.6)
SWATCH_POSITIONS = {
    family_id: (COLUMN_X[index // 2], (2.2 if index % 2 == 0 else -1.3), 0.1)
    for index, family_id in enumerate(FAMILY_IDS)
}
VIEWS = (
    ("Unified_MaterialFamilyBoard.png", "UNIFIED_BOARD", None, FAMILY_IDS, (0.0, 0.05, 22.0), (0.0, 0.05, 0.0), 24.8, (1920, 1080)),
    *tuple(
        (
            filename,
            "PAIRED_CLOSEUP",
            pair_id,
            family_ids,
            (0.0, 0.05, 12.0),
            (0.0, 0.05, 0.0),
            9.0,
            (1280, 720),
        )
        for index, (pair_id, family_ids, filename) in enumerate(PAIR_CONTRACT)
    ),
)

SWATCH_ENVELOPE_M = (2.0, 2.0, 0.2)
TRIANGLE_CEILING = 256
BOARD_BOUNDS_M = {"x": (-11.41, 11.41), "y": (-3.81, 3.81), "z": (-0.21, 0.31)}
NODE_ALLOWLIST = {
    "ShaderNodeOutputMaterial",
    "ShaderNodeBsdfPrincipled",
    "ShaderNodeTexNoise",
    "ShaderNodeTexBrick",
    "ShaderNodeTexWave",
    "ShaderNodeBump",
    "ShaderNodeValToRGB",
}
PATTERN_NODE = {
    "NOISE": "ShaderNodeTexNoise",
    "BRICK": "ShaderNodeTexBrick",
    "WAVE": "ShaderNodeTexWave",
}

FAMILY_MATERIALS = {}
SWATCHES = {}
LABEL_OBJECTS = {}
LABEL_PLATES = {}
GEOMETRY = None


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


def simple_material(name, anchor_hex, roughness=0.82):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = PALETTE[anchor_hex]
    shader.inputs["Roughness"].default_value = roughness
    material["accepted_palette_anchor"] = anchor_hex
    material["support_material"] = True
    return material


def family_material(family_id, anchor_hex, pattern, accent_hex):
    material = bpy.data.materials.new(f"MAT__{family_id}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = PALETTE[anchor_hex]
    shader.inputs["Roughness"].default_value = 0.86
    texture = nodes.new(PATTERN_NODE[pattern])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.08

    if pattern == "NOISE":
        texture.inputs["Scale"].default_value = 5.0 if "STUCCO" in family_id else 13.0
        texture.inputs["Detail"].default_value = 3.0
        texture.inputs["Roughness"].default_value = 0.62
        height_output = texture.outputs["Fac"]
    elif pattern == "BRICK":
        texture.inputs["Color1"].default_value = PALETTE[anchor_hex]
        texture.inputs["Color2"].default_value = PALETTE[accent_hex]
        texture.inputs["Mortar"].default_value = PALETTE["#D8C8A9"]
        texture.inputs["Scale"].default_value = 7.0
        texture.inputs["Mortar Size"].default_value = 0.045
        height_output = texture.outputs["Fac"]
        material.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    else:
        texture.wave_type = "BANDS"
        texture.bands_direction = "X"
        texture.inputs["Scale"].default_value = 8.0 if accent_hex else 24.0
        texture.inputs["Distortion"].default_value = 0.5
        height_output = texture.outputs["Fac"]

    if accent_hex and pattern != "BRICK":
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = PALETTE[anchor_hex]
        ramp.color_ramp.elements[1].color = PALETTE[accent_hex]
        if family_id == "MATERIAL_FAMILY__COURT_SURFACE_LINES":
            ramp.color_ramp.interpolation = "CONSTANT"
            ramp.color_ramp.elements[0].position = 0.47
            ramp.color_ramp.elements[1].position = 0.53
        material.node_tree.links.new(texture.outputs["Fac"], ramp.inputs["Fac"])
        material.node_tree.links.new(ramp.outputs["Color"], shader.inputs["Base Color"])

    if family_id == "MATERIAL_FAMILY__PAINTED_METAL":
        shader.inputs["Metallic"].default_value = 0.68
        shader.inputs["Roughness"].default_value = 0.34
    elif family_id == "MATERIAL_FAMILY__STOREFRONT_GLASS":
        shader.inputs["Metallic"].default_value = 0.08
        shader.inputs["Roughness"].default_value = 0.12
        shader.inputs["Transmission Weight"].default_value = 0.28
        bump.inputs["Strength"].default_value = 0.04
    elif family_id == "MATERIAL_FAMILY__CHARCOAL_ASPHALT_SERVICE_SURFACE":
        bump.inputs["Strength"].default_value = 0.38

    material.node_tree.links.new(height_output, bump.inputs["Height"])
    material.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    material["family_id"] = family_id
    material["accepted_palette_anchor"] = anchor_hex
    material["accepted_palette_accent"] = accent_hex or ""
    material["procedural_pattern"] = pattern
    material["native_nodes_only"] = True
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def add_cube(name, location, dimensions, material, family_id="", role="BOARD_SUPPORT"):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj["family_id"] = family_id
    obj["asset_role"] = role
    obj["external_reference"] = False
    obj["image_texture"] = False
    obj["interior"] = False
    obj["gameplay"] = False
    move_to_collection(obj, GEOMETRY)
    return obj


def add_label(family_id, location, plate_material, text_material):
    plate = add_cube(
        f"LABEL_PLATE__{family_id}",
        (location[0], location[1], 0.225),
        (3.6, 0.7, 0.05),
        plate_material,
        family_id,
        "FAMILY_LABEL_PLATE",
    )
    curve = bpy.data.curves.new(f"LABEL_DATA__{family_id}", "FONT")
    curve.body = SHORT_LABELS[family_id]
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.23
    curve.space_line = 0.82
    curve.extrude = 0.008
    curve.materials.append(text_material)
    label = bpy.data.objects.new(f"LABEL_TEXT__{family_id}", curve)
    label.location = (location[0], location[1], 0.255)
    label["family_id"] = family_id
    label["asset_role"] = "FAMILY_LABEL_TEXT"
    label["label_body"] = SHORT_LABELS[family_id]
    label["built_in_font_only"] = True
    label["external_reference"] = False
    GEOMETRY.objects.link(label)
    LABEL_PLATES[family_id] = plate
    LABEL_OBJECTS[family_id] = label
    return label


def canonical_label_position(family_id):
    swatch = SWATCH_POSITIONS[family_id]
    return swatch[0], (0.75 if swatch[1] > 0.0 else -2.75)


def apply_pair_presentation(family_ids):
    for index, family_id in enumerate(family_ids):
        x = -2.0 if index == 0 else 2.0
        swatch = SWATCHES.get(family_id) or bpy.data.objects[f"SWATCH__{family_id}"]
        plate = LABEL_PLATES.get(family_id) or bpy.data.objects[f"LABEL_PLATE__{family_id}"]
        label = LABEL_OBJECTS.get(family_id) or bpy.data.objects[f"LABEL_TEXT__{family_id}"]
        swatch.location = (x, 0.5, 0.1)
        plate.location = (x, -1.05, 0.225)
        label.location = (x, -1.05, 0.255)
    bpy.context.view_layer.update()


def restore_unified_layout(family_ids=FAMILY_IDS):
    for family_id in family_ids:
        swatch = SWATCHES.get(family_id) or bpy.data.objects[f"SWATCH__{family_id}"]
        plate = LABEL_PLATES.get(family_id) or bpy.data.objects[f"LABEL_PLATE__{family_id}"]
        label = LABEL_OBJECTS.get(family_id) or bpy.data.objects[f"LABEL_TEXT__{family_id}"]
        swatch.location = SWATCH_POSITIONS[family_id]
        x, y = canonical_label_position(family_id)
        plate.location = (x, y, 0.225)
        label.location = (x, y, 0.255)
    bpy.context.view_layer.update()


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
    default = bpy.data.collections.get("Collection")
    default.name = "BOARD_LIGHTS_CAMERAS"
    GEOMETRY = bpy.data.collections.new("MATERIAL_FAMILY_REVIEW_GEOMETRY")
    bpy.context.scene.collection.children.link(GEOMETRY)

    board_material = simple_material("MAT__BOARD_SUPPORT", "#B9A783")
    divider_material = simple_material("MAT__BOARD_DIVIDER", "#4D5051")
    label_plate_material = simple_material("MAT__LABEL_PLATE", "#4D5051", 0.7)
    label_text_material = simple_material("MAT__LABEL_TEXT", "#D8C8A9", 0.65)
    FAMILY_MATERIALS.clear()
    SWATCHES.clear()
    LABEL_OBJECTS.clear()
    LABEL_PLATES.clear()
    for family_id, _label, anchor_hex, pattern, accent_hex in FAMILIES:
        FAMILY_MATERIALS[family_id] = family_material(family_id, anchor_hex, pattern, accent_hex)

    add_cube("REVIEW_BOARD", (0.0, 0.0, -0.1), (22.8, 7.6, 0.2), board_material)
    for index, x in enumerate((-6.45, -2.15, 2.15, 6.45), 1):
        add_cube(f"BOARD_DIVIDER_COLUMN_{index}", (x, 0.0, 0.015), (0.05, 7.2, 0.03), divider_material)
    add_cube("BOARD_DIVIDER_ROW", (0.0, 0.05, 0.015), (22.4, 0.05, 0.03), divider_material)

    for family_id in FAMILY_IDS:
        root = bpy.data.objects.new(f"SWATCH_ROOT__{family_id}", None)
        root["family_id"] = family_id
        root["asset_role"] = "MATERIAL_FAMILY_ROOT"
        root["noncanonical"] = True
        GEOMETRY.objects.link(root)
        swatch = add_cube(
            f"SWATCH__{family_id}",
            SWATCH_POSITIONS[family_id],
            SWATCH_ENVELOPE_M,
            FAMILY_MATERIALS[family_id],
            family_id,
            "STANDARDIZED_MATERIAL_SWATCH",
        )
        swatch.parent = root
        swatch["standard_envelope_m"] = SWATCH_ENVELOPE_M
        SWATCHES[family_id] = swatch
        add_label(family_id, canonical_label_position(family_id), label_plate_material, label_text_material)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_depth = "8"
    scene.world.color = PALETTE["#4D5051"][:3]
    scene["phase"] = "Phase 1L.3h"
    scene["status"] = "NONCANONICAL_MATERIAL_FAMILY_REVIEW"
    scene["family_count"] = 10
    scene["swatch_count"] = 10
    for field in ("external_refs_count", "image_textures_count", "brands_count", "catalogs_count", "interiors_count", "gameplay_changes_count"):
        scene[field] = 0
    for field in ("production_client_changed", "production_map_changed", "production_runtime_changed", "production_config_changed", "production_tests_changed", "package_changed"):
        scene[field] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.0, 14.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 1750.0
    key.data.shape = "DISK"
    key.data.size = 10.0
    point_camera(key, key.location, (0.0, 0.0, 0.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 10.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.35, -0.28, -0.45)
    sun.data.energy = 1.4

    for filename, role, pair_id, family_ids, location, target, ortho_scale, _resolution in VIEWS:
        camera_data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = ortho_scale
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", camera_data)
        default.objects.link(camera)
        point_camera(camera, location, target)
        camera["view_role"] = role
        camera["pair_id"] = pair_id or ""
        camera["family_ids"] = "|".join(family_ids)
        camera["render_file"] = filename
    bpy.context.view_layer.update()


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def family_triangle_counts():
    counts = defaultdict(int)
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.get("asset_role") == "STANDARDIZED_MATERIAL_SWATCH":
            counts[obj["family_id"]] += mesh_triangles(obj)
    return dict(counts)


def projected_bbox(obj, scene, camera):
    points = [world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
    return min(point.x for point in points), min(point.y for point in points), max(point.x for point in points), max(point.y for point in points)


def boxes_overlap(first, second, gap=0.004):
    return not (first[2] + gap <= second[0] or second[2] + gap <= first[0] or first[3] + gap <= second[1] or second[3] + gap <= first[1])


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = [obj for obj in objects if obj.type == "EMPTY" and obj.get("asset_role") == "MATERIAL_FAMILY_ROOT"]
    swatches = [obj for obj in objects if obj.type == "MESH" and obj.get("asset_role") == "STANDARDIZED_MATERIAL_SWATCH"]
    label_plates = [obj for obj in objects if obj.type == "MESH" and obj.get("asset_role") == "FAMILY_LABEL_PLATE"]
    label_texts = [obj for obj in objects if obj.type == "FONT" and obj.get("asset_role") == "FAMILY_LABEL_TEXT"]
    if len(roots) != 10 or {obj.get("family_id") for obj in roots} != set(FAMILY_IDS):
        errors.append("exactly ten deterministic material-family roots are required")
    if len(swatches) != 10 or {obj.get("family_id") for obj in swatches} != set(FAMILY_IDS):
        errors.append("exactly one standardized swatch per accepted family is required")
    if len(label_plates) != 10 or {obj.get("family_id") for obj in label_plates} != set(FAMILY_IDS):
        errors.append("exactly one high-contrast label plate per family is required")
    if len(label_texts) != 10 or {obj.get("family_id") for obj in label_texts} != set(FAMILY_IDS):
        errors.append("exactly one built-in-text label per family is required")
    if {obj.get("family_id"): obj.get("label_body") for obj in label_texts} != SHORT_LABELS:
        errors.append("family short-label mapping differs")
    if any(obj.get("built_in_font_only") is not True or (obj.data.font.filepath and not obj.data.font.filepath.startswith("<")) for obj in label_texts):
        errors.append("family labels must use only Blender's built-in font")
    for swatch in swatches:
        if tuple(round(value, 6) for value in swatch.dimensions) != SWATCH_ENVELOPE_M:
            errors.append(f"{swatch.name} differs from the 2x2x0.2 m envelope")
        if len(swatch.data.materials) != 1 or swatch.data.materials[0].get("family_id") != swatch.get("family_id"):
            errors.append(f"{swatch.name} material-family identity differs")
        if any(swatch.get(field) is not False for field in ("external_reference", "image_texture", "interior", "gameplay")):
            errors.append(f"{swatch.name} violates a zero boundary")

    triangles = family_triangle_counts()
    if set(triangles) != set(FAMILY_IDS) or any(not 0 < count <= TRIANGLE_CEILING for count in triangles.values()):
        errors.append(f"every family must own 1..{TRIANGLE_CEILING} triangles")

    family_materials = [material for material in bpy.data.materials if material.get("family_id")]
    if len(family_materials) != 10 or {material.get("family_id") for material in family_materials} != set(FAMILY_IDS):
        errors.append("exactly ten family materials are required")
    for material in family_materials:
        family_id = material["family_id"]
        _fid, _label, anchor_hex, pattern, accent_hex = FAMILY_BY_ID[family_id]
        node_types = {node.bl_idname for node in material.node_tree.nodes}
        if not node_types <= NODE_ALLOWLIST or PATTERN_NODE[pattern] not in node_types:
            errors.append(f"{family_id} uses a forbidden or missing procedural node")
        if material.get("accepted_palette_anchor") != anchor_hex or material.get("accepted_palette_accent") != (accent_hex or ""):
            errors.append(f"{family_id} palette anchors differ")
        if anchor_hex not in PALETTE or (accent_hex and accent_hex not in PALETTE) or material.get("native_nodes_only") is not True:
            errors.append(f"{family_id} must remain accepted-palette and native-node only")
    for material in bpy.data.materials:
        if not {node.bl_idname for node in material.node_tree.nodes} <= NODE_ALLOWLIST:
            errors.append(f"{material.name} contains a node outside the allowlist")

    for obj in [obj for obj in objects if obj.type in {"MESH", "FONT"}]:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not all(BOARD_BOUNDS_M[axis][0] <= world[index] <= BOARD_BOUNDS_M[axis][1] for index, axis in enumerate(("x", "y", "z"))):
                errors.append(f"{obj.name} exceeds review-board bounds")
                break

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    if len(cameras) != 6 or {camera.name for camera in cameras} != {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}:
        errors.append("camera identities must be one unified plus five paired closeups")
    if Counter(camera.get("view_role") for camera in cameras) != Counter({"UNIFIED_BOARD": 1, "PAIRED_CLOSEUP": 5}):
        errors.append("camera roles must be one unified plus five paired closeups")
    if {camera.get("pair_id") for camera in cameras if camera.get("view_role") == "PAIRED_CLOSEUP"} != {pair[0] for pair in PAIR_CONTRACT}:
        errors.append("paired-closeup identities differ")
    scene = bpy.context.scene
    for filename, role, _pair_id, family_ids, _location, _target, _scale, _resolution in VIEWS:
        camera = bpy.data.objects.get(f"CAMERA__{Path(filename).stem}")
        if camera:
            if role == "PAIRED_CLOSEUP":
                apply_pair_presentation(family_ids)
            swatch_boxes = []
            plate_boxes = []
            label_boxes = []
            for family_id in family_ids:
                swatch_box = projected_bbox(next(obj for obj in swatches if obj.get("family_id") == family_id), scene, camera)
                plate_box = projected_bbox(next(obj for obj in label_plates if obj.get("family_id") == family_id), scene, camera)
                label_box = projected_bbox(next(obj for obj in label_texts if obj.get("family_id") == family_id), scene, camera)
                swatch_boxes.append((family_id, swatch_box))
                plate_boxes.append((family_id, plate_box))
                label_boxes.append((family_id, label_box))
                for element_role, box in (("swatch", swatch_box), ("plate", plate_box), ("label", label_box)):
                    if box[0] < 0.03 or box[1] < 0.03 or box[2] > 0.97 or box[3] > 0.97:
                        errors.append(f"{filename} clips {family_id} {element_role}: {box}")
                if not (plate_box[0] <= label_box[0] and plate_box[1] <= label_box[1] and plate_box[2] >= label_box[2] and plate_box[3] >= label_box[3]):
                    errors.append(f"{filename} label escapes its plate: {family_id}")
            plate_overlaps = [
                f"{first_id}/{second_id}"
                for index, (first_id, first_box) in enumerate(plate_boxes)
                for second_id, second_box in plate_boxes[index + 1:]
                if boxes_overlap(first_box, second_box)
            ]
            if plate_overlaps:
                errors.append(f"{filename} overlaps family label plates: {plate_overlaps}")
            if any(boxes_overlap(plate_box, swatch_box) for _plate_id, plate_box in plate_boxes for _swatch_id, swatch_box in swatch_boxes):
                errors.append(f"{filename} overlaps a label plate and swatch")
            if role == "PAIRED_CLOSEUP":
                content_boxes = [box for _family_id, box in swatch_boxes + plate_boxes]
                combined = (
                    min(box[0] for box in content_boxes),
                    min(box[1] for box in content_boxes),
                    max(box[2] for box in content_boxes),
                    max(box[3] for box in content_boxes),
                )
                occupancy = (combined[2] - combined[0], combined[3] - combined[1])
                centers = [((box[0] + box[2]) / 2.0) for _family_id, box in swatch_boxes]
                if occupancy[0] < 0.75 or occupancy[1] < 0.5 or abs((combined[0] + combined[2]) / 2.0 - 0.5) > 0.03:
                    errors.append(f"{filename} lacks meaningful centered pair occupancy: {combined}")
                if not centers[0] < 0.45 < 0.55 < centers[1] or abs(centers[0] + centers[1] - 1.0) > 0.03:
                    errors.append(f"{filename} pair is not balanced side-by-side: {centers}")
                restore_unified_layout(family_ids)

    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, image textures, and source images are forbidden")
    if any(font.filepath and not font.filepath.startswith("<") for font in bpy.data.fonts):
        errors.append("only Blender's built-in font may identify families")
    zero_fields = ("external_refs_count", "image_textures_count", "brands_count", "catalogs_count", "interiors_count", "gameplay_changes_count")
    if any(scene.get(field) != 0 for field in zero_fields):
        errors.append("external refs, image textures, brands, catalogs, interiors, and gameplay must remain zero")
    false_fields = ("production_client_changed", "production_map_changed", "production_runtime_changed", "production_config_changed", "production_tests_changed", "package_changed")
    if any(scene.get(field) is not False for field in false_fields):
        errors.append("production client/map/runtime/config/test/package boundaries must remain false")
    if any(obj.type in {"ARMATURE", "VOLUME", "META"} for obj in objects):
        errors.append("unsupported geometry is forbidden")

    if require_outputs:
        render_files = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if render_files != sorted(view[0] for view in VIEWS):
            errors.append(f"expected exactly six review PNGs, found {render_files}")
        for filename, _role, _pair_id, _family_ids, _location, _target, _scale, resolution in VIEWS:
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
        "ODDSWELL_SUNDALE_MATERIAL_FAMILY_VALIDATION|result=PASS|families=10|swatches=10|"
        "envelope_m=2x2x0.2|tri_ceiling=256|views=1_unified+5_paired|full_framing=true|"
        "palette=accepted_anchors|nodes=blender_native_allowlist|external_refs=0|image_textures=0|"
        "brands=0|catalogs=0|interiors=0|gameplay=0|production_changed=false|engine=eevee"
    )
    return triangles


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    family_renderables = [obj for obj in bpy.data.objects if obj.get("family_id") in FAMILY_IDS and obj.type in {"MESH", "FONT"}]
    for filename, role, _pair_id, family_ids, _location, _target, _scale, (width, height) in VIEWS:
        visible = set(family_ids)
        if role == "PAIRED_CLOSEUP":
            apply_pair_presentation(family_ids)
        for obj in family_renderables:
            obj.hide_render = obj.get("family_id") not in visible
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)
        if role == "PAIRED_CLOSEUP":
            restore_unified_layout(family_ids)
    for obj in family_renderables:
        obj.hide_render = False


def write_provenance():
    PROVENANCE_PATH.write_text(
        "# Sundale Shared Material-Family Review Board Provenance\n\n"
        "- Phase: `Phase 1L.3h`\n"
        "- Status: noncanonical owner review only\n"
        "- Builder: `build_sundale_material_family_review.py`\n"
        "- Geometry: exactly ten standardized Blender-native `2x2x0.2 m` cube swatches\n"
        "- Materials: Blender-native procedural nodes from the validated allowlist; no image textures\n"
        "- Labels: deterministic high-contrast plates with Blender built-in text only\n"
        "- Palette: accepted Sundale planning anchors only\n"
        "- Renderer: Blender Eevee\n"
        "- External references, images, textures, brands, catalogs, interiors, and gameplay: none\n"
        "- Client, map, runtime, config, tests, package, prior review artifacts, and Phase 1K: unchanged\n\n"
        "The ten families are review evidence only, not final art or production authority. Owner acceptance and a separate production-promotion/expansion gate remain required.\n",
        encoding="utf-8",
    )


def write_manifest(triangles):
    renders = []
    for filename, role, pair_id, family_ids, location, target, ortho_scale, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}",
            "role": role,
            "pair_id": pair_id,
            "family_ids": list(family_ids),
            "camera_location_m": list(location),
            "camera_target_m": list(target),
            "orthographic_scale": ortho_scale,
            "full_framing_validated": True,
            "pair_presentation_positions_m": (
                [
                    {"family_id": family_ids[0], "swatch_center": [-2.0, 0.5, 0.1], "label_center": [-2.0, -1.05, 0.255]},
                    {"family_id": family_ids[1], "swatch_center": [2.0, 0.5, 0.1], "label_center": [2.0, -1.05, 0.255]},
                ]
                if role == "PAIRED_CLOSEUP" else []
            ),
            "meaningful_pair_occupancy_validated": role == "PAIRED_CLOSEUP",
            "balanced_side_by_side_validated": role == "PAIRED_CLOSEUP",
            "horizontal_unified_layout": "5_columns_x_2_rows",
            "short_label_mapping": SHORT_LABELS,
            "built_in_family_label_count": 10,
            "label_plate_count": 10,
            "label_label_overlap_count": 0,
            "label_swatch_overlap_count": 0,
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3h Sundale shared material-family review board",
        "status": "noncanonical_owner_review_board",
        "engine": "BLENDER_EEVEE_NEXT",
        "deterministic_builder": Path(__file__).name,
        "review_contract": {
            "family_ids": list(FAMILY_IDS),
            "family_names": [item[1] for item in FAMILIES],
            "family_count": 10,
            "swatch_count": 10,
            "one_swatch_per_family": True,
            "swatch_envelope_m": list(SWATCH_ENVELOPE_M),
            "triangle_counts": triangles,
            "triangle_ceiling_per_sample": TRIANGLE_CEILING,
            "bounds_m": BOARD_BOUNDS_M,
            "pair_contract": [{"pair_id": pair_id, "family_ids": list(family_ids)} for pair_id, family_ids, _filename in PAIR_CONTRACT],
            "node_allowlist": sorted(NODE_ALLOWLIST),
            "native_geometry_only": True,
            "blender_native_procedural_nodes_only": True,
            "image_textures": 0,
            "full_framing_validated": True,
            "horizontal_unified_layout": "5_columns_x_2_rows",
            "short_label_mapping": SHORT_LABELS,
            "built_in_family_label_count": 10,
            "label_plate_count": 10,
            "label_label_overlap_count": 0,
            "label_swatch_overlap_count": 0,
        },
        "families": [
            {"family_id": family_id, "name": label, "palette_anchor": anchor_hex, "palette_accent": accent_hex, "procedural_pattern": pattern}
            for family_id, label, anchor_hex, pattern, accent_hex in FAMILIES
        ],
        "accepted_palette": sorted(PALETTE),
        "renders": renders,
        "external_references": [],
        "image_textures": [],
        "brands": [],
        "catalogs": [],
        "interiors": [],
        "gameplay_changes": [],
        "production_authority_preserved": {
            "client_changed": False,
            "map_changed": False,
            "runtime_changed": False,
            "config_changed": False,
            "tests_changed": False,
            "package_changed": False,
            "prior_review_artifacts_changed": False,
            "phase_1k_waived": False,
        },
        "lfs": {"blend_required": True, "pattern": "*.blend filter=lfs"},
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "limitations": [
            "review-only material-family swatches, not production or final art",
            "no placement, performance, accessibility, collision, interaction, service, catalog, brand, interior, or gameplay claim",
            "owner acceptance and a separate production promotion/expansion gate remain required",
            "no roadmap Phase 2 or beta-readiness authority",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(triangles):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    contract = manifest.get("review_contract", {})
    if contract.get("family_ids") != list(FAMILY_IDS) or contract.get("family_names") != [item[1] for item in FAMILIES]:
        raise RuntimeError("manifest family identities differ")
    if contract.get("family_count") != 10 or contract.get("swatch_count") != 10 or contract.get("one_swatch_per_family") is not True:
        raise RuntimeError("manifest exact family/swatch counts differ")
    if contract.get("swatch_envelope_m") != list(SWATCH_ENVELOPE_M) or contract.get("triangle_counts") != triangles or contract.get("triangle_ceiling_per_sample") != TRIANGLE_CEILING:
        raise RuntimeError("manifest envelope/triangle contract differs")
    if contract.get("node_allowlist") != sorted(NODE_ALLOWLIST) or contract.get("blender_native_procedural_nodes_only") is not True or contract.get("image_textures") != 0 or contract.get("full_framing_validated") is not True:
        raise RuntimeError("manifest node/image/framing contract differs")
    if contract.get("horizontal_unified_layout") != "5_columns_x_2_rows" or contract.get("short_label_mapping") != SHORT_LABELS or contract.get("built_in_family_label_count") != 10 or contract.get("label_plate_count") != 10:
        raise RuntimeError("manifest label/layout contract differs")
    if contract.get("label_label_overlap_count") != 0 or contract.get("label_swatch_overlap_count") != 0:
        raise RuntimeError("manifest label-overlap contract differs")
    if [entry.get("family_id") for entry in manifest.get("families", [])] != list(FAMILY_IDS):
        raise RuntimeError("manifest family order differs")
    if any(manifest.get(field) for field in ("external_references", "image_textures", "brands", "catalogs", "interiors", "gameplay_changes")):
        raise RuntimeError("manifest zero boundaries differ")
    authority = manifest.get("production_authority_preserved", {})
    if any(authority.get(field) is not False for field in ("client_changed", "map_changed", "runtime_changed", "config_changed", "tests_changed", "package_changed", "prior_review_artifacts_changed", "phase_1k_waived")):
        raise RuntimeError("manifest production authority differs")
    if len(manifest.get("renders", [])) != 6 or Counter(render.get("role") for render in manifest["renders"]) != Counter({"UNIFIED_BOARD": 1, "PAIRED_CLOSEUP": 5}):
        raise RuntimeError("manifest view contract differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"] or render.get("full_framing_validated") is not True:
            raise RuntimeError(f"render identity differs: {path.name}")
        if render.get("role") == "PAIRED_CLOSEUP":
            positions = render.get("pair_presentation_positions_m", [])
            if [entry.get("family_id") for entry in positions] != render.get("family_ids") or render.get("meaningful_pair_occupancy_validated") is not True or render.get("balanced_side_by_side_validated") is not True:
                raise RuntimeError(f"paired presentation contract differs: {path.name}")
    for key, path in (("blend", BLEND_PATH), ("script", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"artifact identity differs: {path.name}")


def main():
    validate_only = "--validate-only" in sys.argv
    focused = "--focused-validate" in sys.argv
    if validate_only or focused:
        triangles = validate_scene(require_outputs=True)
        validate_manifest(triangles)
        marker = "FOCUSED" if focused else "REOPEN"
        print(f"ODDSWELL_SUNDALE_MATERIAL_FAMILY_{marker}|result=PASS|manifest=true|render_hashes=6|full_framing=true|manual_input=false")
        return
    build_scene()
    validate_scene(require_outputs=False)
    render_all()
    write_provenance()
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    triangles = validate_scene(require_outputs=False)
    write_manifest(triangles)
    validate_scene(require_outputs=True)
    validate_manifest(triangles)
    print("ODDSWELL_SUNDALE_MATERIAL_FAMILY_BUILD|result=PASS|artifacts=10|manual_input=false")


if __name__ == "__main__":
    main()
