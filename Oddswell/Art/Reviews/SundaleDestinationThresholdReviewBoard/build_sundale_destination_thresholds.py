"""Build and validate the noncanonical Phase 1L.3f destination-threshold board."""

import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleDestinationThresholdReviewBoard.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

SAMPLE_IDS = (
    "ThresholdStudioApartment",
    "ThresholdJob",
    "ThresholdClothingStore",
    "ThresholdFurnitureStore",
    "ThresholdArena",
    "ThresholdTicketBooth",
)
CELL_CENTERS = {
    sample_id: ((index % 3 - 1) * 12.0, (0.5 - index // 3) * 12.0)
    for index, sample_id in enumerate(SAMPLE_IDS)
}
TRIANGLE_CEILING = 2500
BOARD_BOUNDS_M = {"x": (-19.01, 19.01), "y": (-13.01, 13.01), "z": (-0.51, 9.01)}

# Frozen read-only references extracted from PlaceholderLocomotion.cpp at HEAD 6df1351.
# Bounds are exact axis-aligned unions of the listed 100 cm native-cube part specs.
PRODUCTION_REFS = {
    "ThresholdStudioApartment": {
        "anchor_cm": [0.0, 0.0, 220.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [-1100.0, 1100.0], "y": [1.0, 450.0], "z": [325.0, 975.0]},
        "frontage_part_ids": ["StudioFacade", "StudioAwning", "StudioIdentityLeft", "StudioIdentityRight"],
        "source_lines": [79, 95, 1082, 1088, 1120, 1121],
        "scope_note": "shared Studio/owned One-bedroom exterior entrance; Apartment Management kiosk excluded",
    },
    "ThresholdJob": {
        "anchor_cm": [9500.0, 0.0, 0.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [8875.0, 10125.0], "y": [-20.0, 342.5], "z": [0.0, 940.0]},
        "frontage_part_ids": ["JobFrontagePierLeft", "JobFrontagePierRight", "JobFrontageHeader", "JobFrontageLanding", "JobFrontageApproach"],
        "source_lines": [88, 118, 1143, 1144, 1145, 1146, 1147],
        "scope_note": "exterior-only Job frontage",
    },
    "ThresholdClothingStore": {
        "anchor_cm": [12500.0, 9000.0, 0.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [11275.0, 12147.5], "y": [8472.5, 9527.5], "z": [0.0, 840.0]},
        "frontage_part_ids": ["ClothingStoreFrontagePostLeft", "ClothingStoreFrontagePostRight", "ClothingStoreFrontageHeader", "ClothingStoreFrontageDisplay", "ClothingStoreFrontageApproach"],
        "source_lines": [92, 119, 1191, 1192, 1193, 1194, 1195],
        "scope_note": "exterior-only Clothing Store frontage",
    },
    "ThresholdFurnitureStore": {
        "anchor_cm": [-9500.0, 5000.0, 0.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [-10147.5, -9275.0], "y": [4472.5, 5527.5], "z": [0.0, 840.0]},
        "frontage_part_ids": ["FurnitureStoreFrontagePostLeft", "FurnitureStoreFrontagePostRight", "FurnitureStoreFrontageHeader", "FurnitureStoreFrontageDisplay", "FurnitureStoreFrontageApproach"],
        "source_lines": [93, 120, 1203, 1204, 1205, 1206, 1207],
        "scope_note": "exterior-only Furniture Store frontage",
    },
    "ThresholdArena": {
        "anchor_cm": [7000.0, 18000.0, 0.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [6572.5, 7427.5], "y": [16610.0, 17645.0], "z": [0.0, 822.5]},
        "frontage_part_ids": ["ArenaEntrancePierLeft", "ArenaEntrancePierRight", "ArenaEntrancePortalCap", "ArenaEntranceThresholdInset", "ArenaEntranceApproachBand"],
        "source_lines": [103, 126, 1167, 1168, 1169, 1170, 1171],
        "scope_note": "Arena entry portal only",
    },
    "ThresholdTicketBooth": {
        "anchor_cm": [1000.0, 18000.0, 0.0],
        "interaction_radius_cm": 350.0,
        "frontage_bounds_cm": {"x": [710.0, 1290.0], "y": [16775.0, 17645.0], "z": [0.0, 630.0]},
        "frontage_part_ids": ["TicketBoothFrontagePostLeft", "TicketBoothFrontagePostRight", "TicketBoothFrontageHeader", "TicketBoothFrontageCounter", "TicketBoothFrontageApproach"],
        "source_lines": [104, 127, 1179, 1180, 1181, 1182, 1183],
        "scope_note": "exterior-only Ticket Booth frontage",
    },
}
PRODUCTION_CLEARANCE_REFS = {
    "Arena_to_TicketBooth": {
        "anchor_distance_cm": 6000.0,
        "summed_interaction_radii_cm": 700.0,
        "edge_clearance_cm": 5300.0,
        "source_lines": [14951, 15005],
    }
}

PALETTE = {
    "warm_limestone": ("#D8C8A9", (0.847059, 0.784314, 0.662745, 1.0)),
    "muted_terracotta": ("#A65F47", (0.650980, 0.372549, 0.278431, 1.0)),
    "sand_concrete": ("#B9A783", (0.725490, 0.654902, 0.513725, 1.0)),
    "sage_green": ("#6D7F62", (0.427451, 0.498039, 0.384314, 1.0)),
    "restrained_cobalt": ("#315F79", (0.192157, 0.372549, 0.474510, 1.0)),
    "burnt_orange": ("#C46D3B", (0.768627, 0.427451, 0.231373, 1.0)),
    "charcoal_gray": ("#4D5051", (0.301961, 0.313725, 0.317647, 1.0)),
}
VIEWS = (
    ("Unified_SundaleDestinationThresholds.png", "UNIFIED_BOARD", None, (0.0, -45.0, 34.0), (0.0, 0.0, 3.1), 48.0, (1920, 1080)),
    *tuple(
        (
            f"Closeup_{sample_id}.png",
            "THRESHOLD_CLOSEUP",
            sample_id,
            (CELL_CENTERS[sample_id][0], CELL_CENTERS[sample_id][1] - 18.0, 4.5),
            (CELL_CENTERS[sample_id][0], CELL_CENTERS[sample_id][1], 2.6),
            32.0,
            (1280, 720),
        )
        for sample_id in SAMPLE_IDS
    ),
)

MATERIALS = {}
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


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.84
    material["accepted_palette_hex"] = PALETTE[name][0]
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, sample_id, role):
    obj["sample_id"] = sample_id
    obj["asset_role"] = role
    obj["noncanonical"] = True
    obj["open_passage_proxy"] = role == "OPEN_PASSAGE_PROXY"
    obj["collision_claim"] = False
    for field in ("external_reference", "texture", "interior", "text_sign", "brand", "gameplay", "prompt_change"):
        obj[field] = False
    return obj


def add_root(sample_id):
    root = bpy.data.objects.new(f"THRESHOLD_ROOT__{sample_id}", None)
    tag(root, sample_id, "NONCANONICAL_THRESHOLD_REVIEW")
    root["open_passage_proxy"] = True
    GEOMETRY.objects.link(root)
    return root


def add_cube(name, location, dimensions, material_name, parent, role):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, parent.get("sample_id", ""), role)
    obj.parent = parent
    move_to_collection(obj, GEOMETRY)
    return obj


def add_passage_proxy(parent, center, width, height, depth=1.0):
    proxy = bpy.data.objects.new(f"OPEN_PASSAGE_PROXY__{parent['sample_id']}", None)
    tag(proxy, parent["sample_id"], "OPEN_PASSAGE_PROXY")
    proxy.location = (center[0], center[1], height / 2.0)
    proxy.empty_display_type = "CUBE"
    proxy.empty_display_size = 0.5
    proxy["review_width_m"] = width
    proxy["review_height_m"] = height
    proxy["review_depth_m"] = depth
    proxy.parent = parent
    GEOMETRY.objects.link(proxy)


def add_apron(root, cx, cy, accent, width=3.2, depth=3.2):
    add_cube(f"{root.name}__APRON", (cx, cy - depth / 2.0 - 1.0, 0.08), (width, depth, 0.16), accent, root, "THRESHOLD_APRON")


def build_studio():
    sample_id = "ThresholdStudioApartment"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    for side in (-1, 1):
        add_cube(f"{root.name}__WING_{side:+d}", (cx + side * 2.0, cy, 2.5), (2.0, 2.2, 5.0), "warm_limestone", root, "RESIDENTIAL_FRAME")
    add_cube(f"{root.name}__LINTEL", (cx, cy, 4.4), (2.0, 2.2, 1.2), "muted_terracotta", root, "SHARED_ENTRY_LINTEL")
    add_cube(f"{root.name}__AWNING", (cx, cy - 1.45, 3.45), (3.6, 1.0, 0.25), "burnt_orange", root, "RETURN_LANDMARK_AWNING")
    add_cube(f"{root.name}__BALCONY_BAND", (cx, cy - 1.2, 4.6), (5.6, 0.35, 0.25), "muted_terracotta", root, "RESIDENTIAL_BALCONY_CUE")
    add_apron(root, cx, cy, "sand_concrete", 3.0, 3.0)
    add_passage_proxy(root, (cx, cy - 0.9), 2.0, 3.8)


def build_job():
    sample_id = "ThresholdJob"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    for side in (-1, 1):
        add_cube(f"{root.name}__PIER_{side:+d}", (cx + side * 2.2, cy, 2.35), (0.75, 2.1, 4.7), "charcoal_gray", root, "PRACTICAL_CANOPY_PIER")
    add_cube(f"{root.name}__HEADER", (cx, cy, 4.75), (5.2, 2.1, 0.45), "burnt_orange", root, "CANOPY_HEADER")
    for offset in (-1.5, 0.0, 1.5):
        add_cube(f"{root.name}__SLAT_{offset:+.1f}", (cx + offset, cy - 1.55, 4.55), (0.3, 1.2, 0.3), "sand_concrete", root, "STRUCTURAL_CANOPY_RHYTHM")
    add_apron(root, cx, cy, "restrained_cobalt", 2.7, 3.4)
    add_passage_proxy(root, (cx, cy - 0.9), 3.0, 4.2)


def build_clothing():
    sample_id = "ThresholdClothingStore"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    add_cube(f"{root.name}__TALL_FIN", (cx - 2.25, cy, 2.7), (0.65, 2.0, 5.4), "restrained_cobalt", root, "ASYMMETRIC_RETAIL_FIN")
    add_cube(f"{root.name}__SHORT_FIN", (cx + 2.15, cy, 2.05), (0.95, 2.0, 4.1), "burnt_orange", root, "ASYMMETRIC_RETAIL_FIN")
    add_cube(f"{root.name}__HEADER", (cx, cy, 4.45), (4.8, 2.0, 0.5), "warm_limestone", root, "RETAIL_HEADER")
    for side in (-1, 1):
        add_cube(f"{root.name}__DISPLAY_FRAME_{side:+d}", (cx + side * 1.75, cy - 1.12, 1.45), (1.2, 0.24, 2.5), "charcoal_gray", root, "DISPLAY_BAY_CUE")
    add_apron(root, cx, cy, "restrained_cobalt", 2.4, 3.8)
    add_passage_proxy(root, (cx, cy - 0.9), 2.2, 3.7)


def build_furniture():
    sample_id = "ThresholdFurnitureStore"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    for side in (-1, 1):
        add_cube(f"{root.name}__SHOWROOM_POST_{side:+d}", (cx + side * 2.25, cy, 2.4), (0.8, 2.4, 4.8), "sage_green", root, "SHOWROOM_POST")
    add_cube(f"{root.name}__SHOWROOM_HEADER", (cx, cy, 4.6), (5.3, 2.4, 0.5), "sage_green", root, "SHOWROOM_HEADER")
    add_cube(f"{root.name}__DEEP_CANOPY", (cx, cy - 1.7, 3.65), (4.8, 1.7, 0.28), "warm_limestone", root, "DEEP_SHOWROOM_CANOPY")
    add_cube(f"{root.name}__PLINTH_LEFT", (cx - 1.8, cy - 1.25, 0.55), (1.2, 0.5, 1.1), "sand_concrete", root, "SHOWROOM_PLINTH")
    add_apron(root, cx, cy, "burnt_orange", 3.0, 3.6)
    add_passage_proxy(root, (cx, cy - 1.0), 2.8, 4.0)


def build_arena():
    sample_id = "ThresholdArena"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    for offset in (-3.0, -1.0, 1.0, 3.0):
        add_cube(f"{root.name}__PORTAL_PIER_{offset:+.1f}", (cx + offset, cy, 2.7), (0.55, 2.5, 5.4), "charcoal_gray", root, "ARENA_PORTAL_PIER")
    add_cube(f"{root.name}__PORTAL_CAP", (cx, cy, 5.45), (7.3, 2.5, 0.55), "burnt_orange", root, "ARENA_PORTAL_CAP")
    add_cube(f"{root.name}__BROAD_CANOPY", (cx, cy - 1.8, 4.55), (7.6, 1.6, 0.3), "restrained_cobalt", root, "ARENA_CANOPY")
    add_apron(root, cx, cy, "sand_concrete", 5.8, 4.0)
    add_passage_proxy(root, (cx, cy - 1.0), 1.45, 4.8)


def build_ticket():
    sample_id = "ThresholdTicketBooth"
    cx, cy = CELL_CENTERS[sample_id]
    root = add_root(sample_id)
    for side in (-1, 1):
        add_cube(f"{root.name}__POST_{side:+d}", (cx + side * 2.0, cy, 2.1), (0.55, 2.0, 4.2), "charcoal_gray", root, "COMPACT_BOOTH_POST")
    add_cube(f"{root.name}__HEADER", (cx, cy, 4.2), (4.7, 2.0, 0.45), "burnt_orange", root, "COMPACT_BOOTH_HEADER")
    for side in (-1, 1):
        add_cube(f"{root.name}__COUNTER_{side:+d}", (cx + side * 1.45, cy - 1.1, 1.05), (1.3, 0.65, 2.1), "sand_concrete", root, "SPLIT_COUNTER_CUE")
    add_cube(f"{root.name}__OFFSET_BAR", (cx + 1.55, cy - 1.45, 2.65), (1.45, 0.45, 0.35), "restrained_cobalt", root, "ASYMMETRIC_BOOTH_CUE")
    add_apron(root, cx, cy, "restrained_cobalt", 2.2, 3.2)
    add_passage_proxy(root, (cx, cy - 1.0), 1.6, 3.8)


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
    GEOMETRY = bpy.data.collections.new("THRESHOLD_REVIEW_GEOMETRY")
    bpy.context.scene.collection.children.link(GEOMETRY)

    MATERIALS.clear()
    for name, (_hex, color) in PALETTE.items():
        MATERIALS[name] = make_material(name, color)

    board_root = bpy.data.objects.new("BOARD_ROOT", None)
    tag(board_root, "", "BOARD_ROOT")
    GEOMETRY.objects.link(board_root)
    add_cube("REVIEW_BOARD", (0.0, 0.0, -0.25), (38.0, 26.0, 0.5), "sand_concrete", board_root, "REVIEW_BOARD")
    for x in (-6.0, 6.0):
        add_cube(f"BOARD_DIVIDER_X_{x:+.0f}", (x, 0.0, 0.03), (0.08, 25.0, 0.06), "charcoal_gray", board_root, "BOARD_DIVIDER")
    add_cube("BOARD_DIVIDER_Y", (0.0, 0.0, 0.03), (37.0, 0.08, 0.06), "charcoal_gray", board_root, "BOARD_DIVIDER")

    build_studio()
    build_job()
    build_clothing()
    build_furniture()
    build_arena()
    build_ticket()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = PALETTE["sand_concrete"][1][:3]
    scene["phase"] = "Phase 1L.3f"
    scene["status"] = "NONCANONICAL_DESTINATION_THRESHOLD_REVIEW"
    for field in ("external_refs_count", "textures_count", "interiors_count", "text_signs_count", "brands_count", "gameplay_changes_count", "prompt_changes_count"):
        scene[field] = 0
    for field in ("production_map_changed", "production_route_changed", "production_collision_changed", "production_navigation_changed", "package_changed"):
        scene[field] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, -5.0, 23.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 1900.0
    key.data.shape = "DISK"
    key.data.size = 18.0
    point_camera(key, key.location, (0.0, 0.0, 0.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 20.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.55, -0.35, -0.45)
    sun.data.energy = 2.0

    for filename, view_role, sample_id, location, target, lens, _resolution in VIEWS:
        camera_data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", camera_data)
        default.objects.link(camera)
        point_camera(camera, location, target)
        camera.data.lens = lens
        camera["view_role"] = view_role
        camera["sample_id"] = sample_id or ""
        camera["render_file"] = filename


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def sample_triangle_counts():
    counts = defaultdict(int)
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.get("sample_id") in SAMPLE_IDS:
            counts[obj["sample_id"]] += mesh_triangles(obj)
    return dict(counts)


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = {obj.get("sample_id"): obj for obj in objects if obj.type == "EMPTY" and obj.name.startswith("THRESHOLD_ROOT__")}
    if set(roots) != set(SAMPLE_IDS) or len(roots) != 6:
        errors.append("exactly six deterministic threshold roots are required")
    proxies = [obj for obj in objects if obj.get("asset_role") == "OPEN_PASSAGE_PROXY"]
    if Counter(obj.get("sample_id") for obj in proxies) != Counter({sample_id: 1 for sample_id in SAMPLE_IDS}):
        errors.append("each threshold requires exactly one open-passage proxy")
    if any(obj.get("open_passage_proxy") is not True or obj.get("collision_claim") is not False for obj in proxies):
        errors.append("open-passage proxies must retain collision_claim=false")
    sample_meshes = [obj for obj in objects if obj.type == "MESH" and obj.get("sample_id") in SAMPLE_IDS]
    if {obj.get("sample_id") for obj in sample_meshes} != set(SAMPLE_IDS):
        errors.append("each exact threshold ID must own native mesh geometry")
    forbidden_fields = ("external_reference", "texture", "interior", "text_sign", "brand", "gameplay", "prompt_change")
    if any(obj.get("collision_claim") is not False or any(obj.get(field) is not False for field in forbidden_fields) for obj in sample_meshes):
        errors.append("sample boundaries must remain false")

    triangles = sample_triangle_counts()
    for sample_id in SAMPLE_IDS:
        if not 0 < triangles.get(sample_id, 0) <= TRIANGLE_CEILING:
            errors.append(f"{sample_id} triangle count is outside 1..{TRIANGLE_CEILING}")

    for obj in [obj for obj in objects if obj.type == "MESH"]:
        for material in obj.data.materials:
            if material.name not in PALETTE or material.get("accepted_palette_hex") != PALETTE[material.name][0]:
                errors.append(f"{obj.name} uses a nonaccepted material")
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not (BOARD_BOUNDS_M["x"][0] <= world.x <= BOARD_BOUNDS_M["x"][1] and BOARD_BOUNDS_M["y"][0] <= world.y <= BOARD_BOUNDS_M["y"][1] and BOARD_BOUNDS_M["z"][0] <= world.z <= BOARD_BOUNDS_M["z"][1]):
                errors.append(f"{obj.name} exceeds review-board bounds")
                break

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    expected_names = {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}
    if {camera.name for camera in cameras} != expected_names:
        errors.append("camera IDs differ from the unified plus six-closeup contract")
    if Counter(camera.get("view_role") for camera in cameras) != Counter({"UNIFIED_BOARD": 1, "THRESHOLD_CLOSEUP": 6}):
        errors.append("camera roles must be one unified board plus six closeups")
    if {camera.get("sample_id") for camera in cameras if camera.get("view_role") == "THRESHOLD_CLOSEUP"} != set(SAMPLE_IDS):
        errors.append("each threshold must have one closeup camera")
    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if not bpy.data.materials or any(material.name not in PALETTE for material in bpy.data.materials):
        errors.append("materials must be a nonempty accepted-palette subset")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, textures, and images are forbidden")
    if any(scene.get(field) != 0 for field in ("external_refs_count", "textures_count", "interiors_count", "text_signs_count", "brands_count", "gameplay_changes_count", "prompt_changes_count")):
        errors.append("all zero-count boundaries must remain zero")
    if any(scene.get(field) is not False for field in ("production_map_changed", "production_route_changed", "production_collision_changed", "production_navigation_changed", "package_changed")):
        errors.append("production and package boundaries must remain false")
    if any(obj.type in {"ARMATURE", "VOLUME", "META", "FONT"} for obj in objects):
        errors.append("characters, volumes, metaballs, and text signs are forbidden")

    if require_outputs:
        files = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if files != sorted(view[0] for view in VIEWS):
            errors.append(f"expected exactly seven review PNGs, found {files}")
        for filename, _role, _sample_id, _location, _target, _lens, resolution in VIEWS:
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
        "ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_VALIDATION|result=PASS|samples=6|"
        "open_passage_proxies=6|collision_claim=false|views=1_unified+6_closeup|engine=eevee|"
        f"triangle_ceiling={TRIANGLE_CEILING}|palette=accepted_subset|external_refs=0|textures=0|"
        "interiors=0|text_signs=0|brands=0|gameplay=0|prompt_changes=0|production_map_changed=false|"
        "production_route_changed=false|production_collision_changed=false|production_navigation_changed=false|package_changed=false"
    )
    return triangles


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    sample_objects = [obj for obj in bpy.data.objects if obj.get("sample_id") in SAMPLE_IDS]
    for filename, _role, sample_id, _location, _target, _lens, (width, height) in VIEWS:
        for obj in sample_objects:
            obj.hide_render = bool(sample_id and obj.get("sample_id") != sample_id)
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)
    for obj in sample_objects:
        obj.hide_render = False
    scene.camera = bpy.data.objects["CAMERA__Unified_SundaleDestinationThresholds"]


def write_manifest(triangles):
    renders = []
    for filename, role, sample_id, location, target, lens, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}", "role": role, "sample_id": sample_id,
            "camera_location_m": location, "camera_target_m": target, "lens_mm": lens,
            "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3f Sundale destination entrance/threshold treatments",
        "status": "noncanonical_owner_review_board",
        "engine": "BLENDER_EEVEE_NEXT",
        "deterministic_builder": Path(__file__).name,
        "sample_contract": {
            "sample_ids": list(SAMPLE_IDS), "sample_count": 6, "instance_counts": {sample_id: 1 for sample_id in SAMPLE_IDS},
            "triangle_counts": triangles, "triangle_ceiling_per_sample": TRIANGLE_CEILING,
            "bounds_m": BOARD_BOUNDS_M, "native_geometry_only": True,
            "open_passage_proxy": True, "collision_claim": False,
        },
        "production_references": PRODUCTION_REFS,
        "production_clearance_references": PRODUCTION_CLEARANCE_REFS,
        "palette": {name: value[0] for name, value in PALETTE.items()},
        "renders": renders,
        "boundaries": {
            "external_references": 0, "textures": 0, "interiors": 0, "text_signs": 0, "brands": 0,
            "gameplay_changes": 0, "prompt_changes": 0, "collision_claim": False,
            "production_map_changed": False, "production_route_changed": False,
            "production_collision_changed": False, "production_navigation_changed": False,
            "package_changed": False,
        },
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "limitations": [
            "review-only entrance silhouettes; not production geometry, collision, navigation, placement, or accessibility proof",
            "open passage is a geometric review proxy and makes no production-clearance claim",
            "promotion, production clearance, and placement remain owner-gated",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(triangles):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    contract = manifest.get("sample_contract", {})
    if contract.get("sample_ids") != list(SAMPLE_IDS) or contract.get("instance_counts") != {sample_id: 1 for sample_id in SAMPLE_IDS}:
        raise RuntimeError("manifest sample identities/counts differ")
    if contract.get("triangle_counts") != triangles or contract.get("open_passage_proxy") is not True or contract.get("collision_claim") is not False:
        raise RuntimeError("manifest geometry/passsage contract differs")
    refs = manifest.get("production_references", {})
    if set(refs) != set(SAMPLE_IDS) or any(refs[sample_id].get("anchor_cm") != PRODUCTION_REFS[sample_id]["anchor_cm"] or refs[sample_id].get("interaction_radius_cm") != 350.0 or refs[sample_id].get("frontage_bounds_cm") != PRODUCTION_REFS[sample_id]["frontage_bounds_cm"] for sample_id in SAMPLE_IDS):
        raise RuntimeError("manifest production references differ from frozen extraction")
    if manifest.get("production_clearance_references") != PRODUCTION_CLEARANCE_REFS:
        raise RuntimeError("manifest production clearance reference differs")
    boundaries = manifest.get("boundaries", {})
    if any(boundaries.get(field) != 0 for field in ("external_references", "textures", "interiors", "text_signs", "brands", "gameplay_changes", "prompt_changes")) or boundaries.get("collision_claim") is not False:
        raise RuntimeError("manifest zero boundaries differ")
    for render in manifest.get("renders", []):
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
        print(f"ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_{marker}|result=PASS|manifest=true|render_hashes=7|manual_input=false")
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
    print("ODDSWELL_SUNDALE_DESTINATION_THRESHOLDS_BUILD|result=PASS|artifacts=10|manual_input=false")


if __name__ == "__main__":
    main()
