"""Build and validate the noncanonical Sundale metropolitan review preview."""

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleCitywideMassing.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
TOP_RENDER_SIZE = (2560, 1800)
EYE_RENDER_SIZE = (1280, 720)
PLAYABLE_SIZE_M = (1400.0, 1000.0)
COMMONS_SIZE_M = (320.0, 240.0)
LABEL_TEXT_Z_M = 500.0
LABEL_PLATE_Z_M = 499.7
LABEL_PLATE_DEPTH_M = 0.2
LABEL_CONTRAST_MIN = 5.0
EYE_CAMERA_CLEARANCE_M = 20.0

COLORS = {
    "ground": (0.12, 0.14, 0.15, 1.0),
    "south": (0.30, 0.27, 0.23, 1.0),
    "west": (0.24, 0.30, 0.27, 1.0),
    "east": (0.29, 0.27, 0.23, 1.0),
    "north": (0.25, 0.27, 0.31, 1.0),
    "ring": (0.12, 0.46, 0.63, 1.0),
    "spoke": (0.67, 0.49, 0.28, 1.0),
    "local": (0.32, 0.36, 0.38, 1.0),
    "commons": (0.35, 0.48, 0.34, 1.0),
    "promenade": (0.72, 0.64, 0.50, 1.0),
    "grove": (0.20, 0.38, 0.24, 1.0),
    "limestone": (0.85, 0.78, 0.66, 1.0),
    "terracotta": (0.65, 0.37, 0.28, 1.0),
    "charcoal": (0.25, 0.27, 0.28, 1.0),
    "orange": (0.77, 0.43, 0.23, 1.0),
    "cobalt": (0.12, 0.46, 0.63, 1.0),
    "teal": (0.08, 0.60, 0.56, 1.0),
    "court": (0.28, 0.45, 0.39, 1.0),
    "label": (0.03, 0.04, 0.05, 1.0),
}

DISTRICTS = {
    "SOUTH_RESIDENTIAL_RETAIL": ((0.0, -360.0), (1400.0, 280.0), "south"),
    "WEST_RESIDENTIAL_SERVICES": ((-530.0, 0.0), (340.0, 440.0), "west"),
    "EAST_COMMERCE_WORK": ((530.0, 0.0), (340.0, 440.0), "east"),
    "NORTH_ARENA_ENTERTAINMENT": ((0.0, 360.0), (1400.0, 280.0), "north"),
}

DISTRICT_SLOTS = {
    "SOUTH_RESIDENTIAL_RETAIL": [
        *[(x, -410.0) for x in (-560.0, -420.0, -280.0, -140.0, 0.0, 140.0, 280.0, 420.0, 560.0)],
        (-540.0, -250.0), (-400.0, -250.0), (-338.0, -250.0), (-240.0, -250.0), (-130.0, -250.0),
        (10.0, -250.0), (170.0, -250.0), (330.0, -250.0), (530.0, -250.0),
    ],
    "WEST_RESIDENTIAL_SERVICES": [(x, y) for x in (-600.0, -480.0, -360.0) for y in (-180.0, -108.0, -36.0, 36.0, 108.0, 180.0)],
    "EAST_COMMERCE_WORK": [(x, y) for x in (360.0, 480.0, 600.0) for y in (-180.0, -108.0, -36.0, 36.0, 108.0, 180.0)],
    "NORTH_ARENA_ENTERTAINMENT": [
        *[(x, 410.0) for x in (-560.0, -420.0, -280.0, -140.0, 0.0, 140.0, 280.0, 420.0, 560.0)],
        (-560.0, 250.0), (-400.0, 250.0), (-240.0, 250.0), (-90.0, 250.0), (150.0, 250.0),
        (253.0, 250.0), (360.0, 250.0), (480.0, 250.0), (600.0, 250.0),
    ],
}

CORE_TOWER_SLOTS = {
    "SOUTH_RESIDENTIAL_RETAIL": {14: "CORE_TOWER__SOUTH_01", 15: "CORE_TOWER__SOUTH_02", 16: "CORE_TOWER__SOUTH_03"},
    "WEST_RESIDENTIAL_SERVICES": {1: "CORE_TOWER__WEST_01", 9: "CORE_TOWER__WEST_02", 17: "CORE_TOWER__WEST_03"},
    "EAST_COMMERCE_WORK": {5: "CORE_TOWER__EAST_01", 9: "CORE_TOWER__EAST_02", 13: "CORE_TOWER__EAST_03"},
    "NORTH_ARENA_ENTERTAINMENT": {9: "CORE_TOWER__NORTH_01", 10: "CORE_TOWER__NORTH_02", 11: "CORE_TOWER__NORTH_03"},
}

MASS_OVERRIDES = {
    ("SOUTH_RESIDENTIAL_RETAIL", 10): ("LANDMARK__STUDIO_APARTMENT", (100.0, 70.0, 22.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("SOUTH_RESIDENTIAL_RETAIL", 11): ("LANDMARK__APARTMENT_MANAGEMENT", (24.0, 24.0, 8.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
    ("SOUTH_RESIDENTIAL_RETAIL", 12): ("LANDMARK__CLOTHING", (80.0, 60.0, 20.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("SOUTH_RESIDENTIAL_RETAIL", 13): ("LANDMARK__FURNITURE", (80.0, 60.0, 20.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("EAST_COMMERCE_WORK", 2): ("LANDMARK__JOB", (80.0, 52.0, 20.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
    ("NORTH_ARENA_ENTERTAINMENT", 13): ("LANDMARK__ARENA", (180.0, 90.0, 30.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("NORTH_ARENA_ENTERTAINMENT", 14): ("LANDMARK__TICKET_BOOTH", (26.0, 26.0, 10.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
}


def street_mass_specs():
    specs = []
    colors = ("limestone", "terracotta", "charcoal")
    prefixes = {name: name.split("_")[0] for name in DISTRICTS}
    for district_index, (district, slots) in enumerate(DISTRICT_SLOTS.items()):
        for index, location in enumerate(slots):
            tower_id = CORE_TOWER_SLOTS[district].get(index)
            if (district, index) in MASS_OVERRIDES:
                name, dimensions, color, role = MASS_OVERRIDES[(district, index)]
            elif tower_id:
                suffix = tower_id.rsplit("_", 1)[-1]
                name = f"CORE_BASE__{prefixes[district]}_{suffix}"
                dimensions, color, role = (78.0, 58.0, 26.0), "charcoal", "PROPOSED_CORE_TOWER_BASE"
            else:
                name = f"STREET__{prefixes[district]}_{index + 1:02d}"
                dimensions = ((88.0, 68.0, 16.0 + 4.0 * (index % 3)) if district in {"SOUTH_RESIDENTIAL_RETAIL", "NORTH_ARENA_ENTERTAINMENT"} else (76.0, 48.0, 16.0 + 3.0 * (index % 3)))
                color, role = colors[(index + district_index) % len(colors)], "PROPOSED_STREET_MASS"
            specs.append((name, district, location, dimensions, color, role, tower_id))
    return specs


STREET_MASSES = street_mass_specs()

TOWERS = [
    ("CORE_TOWER__SOUTH_01", "PLAYABLE_CORE", "SOUTH_RESIDENTIAL_RETAIL", "CORE_BASE__SOUTH_01", (10.0, -250.0), (42.0, 42.0), 185.0, "cobalt"),
    ("CORE_TOWER__SOUTH_02", "PLAYABLE_CORE", "SOUTH_RESIDENTIAL_RETAIL", "CORE_BASE__SOUTH_02", (170.0, -250.0), (44.0, 44.0), 220.0, "terracotta"),
    ("CORE_TOWER__SOUTH_03", "PLAYABLE_CORE", "SOUTH_RESIDENTIAL_RETAIL", "CORE_BASE__SOUTH_03", (330.0, -250.0), (40.0, 40.0), 195.0, "limestone"),
    ("CORE_TOWER__WEST_01", "PLAYABLE_CORE", "WEST_RESIDENTIAL_SERVICES", "CORE_BASE__WEST_01", (-600.0, -108.0), (42.0, 42.0), 210.0, "terracotta"),
    ("CORE_TOWER__WEST_02", "PLAYABLE_CORE", "WEST_RESIDENTIAL_SERVICES", "CORE_BASE__WEST_02", (-480.0, 36.0), (40.0, 40.0), 175.0, "cobalt"),
    ("CORE_TOWER__WEST_03", "PLAYABLE_CORE", "WEST_RESIDENTIAL_SERVICES", "CORE_BASE__WEST_03", (-360.0, 180.0), (44.0, 44.0), 230.0, "limestone"),
    ("CORE_TOWER__EAST_01", "PLAYABLE_CORE", "EAST_COMMERCE_WORK", "CORE_BASE__EAST_01", (360.0, 180.0), (42.0, 42.0), 225.0, "cobalt"),
    ("CORE_TOWER__EAST_02", "PLAYABLE_CORE", "EAST_COMMERCE_WORK", "CORE_BASE__EAST_02", (480.0, 36.0), (44.0, 44.0), 190.0, "terracotta"),
    ("CORE_TOWER__EAST_03", "PLAYABLE_CORE", "EAST_COMMERCE_WORK", "CORE_BASE__EAST_03", (600.0, -108.0), (40.0, 40.0), 215.0, "limestone"),
    ("CORE_TOWER__NORTH_01", "PLAYABLE_CORE", "NORTH_ARENA_ENTERTAINMENT", "CORE_BASE__NORTH_01", (-560.0, 250.0), (44.0, 44.0), 235.0, "terracotta"),
    ("CORE_TOWER__NORTH_02", "PLAYABLE_CORE", "NORTH_ARENA_ENTERTAINMENT", "CORE_BASE__NORTH_02", (-400.0, 250.0), (42.0, 42.0), 200.0, "cobalt"),
    ("CORE_TOWER__NORTH_03", "PLAYABLE_CORE", "NORTH_ARENA_ENTERTAINMENT", "CORE_BASE__NORTH_03", (-240.0, 250.0), (40.0, 40.0), 245.0, "limestone"),
    ("SKYLINE_TOWER__WEST_01", "BACKGROUND_SKYLINE", "WEST", None, (-790.0, -300.0), (60.0, 60.0), 230.0, "charcoal"),
    ("SKYLINE_TOWER__WEST_02", "BACKGROUND_SKYLINE", "WEST", None, (-800.0, 0.0), (64.0, 64.0), 275.0, "limestone"),
    ("SKYLINE_TOWER__WEST_03", "BACKGROUND_SKYLINE", "WEST", None, (-790.0, 300.0), (58.0, 58.0), 245.0, "terracotta"),
    ("SKYLINE_TOWER__EAST_01", "BACKGROUND_SKYLINE", "EAST", None, (790.0, -300.0), (60.0, 60.0), 255.0, "limestone"),
    ("SKYLINE_TOWER__EAST_02", "BACKGROUND_SKYLINE", "EAST", None, (800.0, 0.0), (64.0, 64.0), 290.0, "charcoal"),
    ("SKYLINE_TOWER__EAST_03", "BACKGROUND_SKYLINE", "EAST", None, (790.0, 300.0), (58.0, 58.0), 235.0, "terracotta"),
    ("SKYLINE_TOWER__NORTH_01", "BACKGROUND_SKYLINE", "NORTH", None, (-420.0, 590.0), (60.0, 60.0), 260.0, "charcoal"),
    ("SKYLINE_TOWER__NORTH_02", "BACKGROUND_SKYLINE", "NORTH", None, (0.0, 600.0), (64.0, 64.0), 305.0, "terracotta"),
    ("SKYLINE_TOWER__NORTH_03", "BACKGROUND_SKYLINE", "NORTH", None, (420.0, 590.0), (60.0, 60.0), 280.0, "limestone"),
    ("SKYLINE_TOWER__SOUTH_01", "BACKGROUND_SKYLINE", "SOUTH", None, (-420.0, -590.0), (60.0, 60.0), 240.0, "terracotta"),
    ("SKYLINE_TOWER__SOUTH_02", "BACKGROUND_SKYLINE", "SOUTH", None, (0.0, -600.0), (64.0, 64.0), 285.0, "charcoal"),
    ("SKYLINE_TOWER__SOUTH_03", "BACKGROUND_SKYLINE", "SOUTH", None, (420.0, -590.0), (60.0, 60.0), 265.0, "limestone"),
]

RADIAL_SPOKES = {
    "PREVIEW__SPOKE_N": [(0.0, 120.0), (0.0, 500.0)],
    "PREVIEW__SPOKE_NE": [(160.0, 120.0), (700.0, 500.0)],
    "PREVIEW__SPOKE_E": [(160.0, 0.0), (700.0, 0.0)],
    "PREVIEW__SPOKE_SE": [(160.0, -120.0), (700.0, -500.0)],
    "PREVIEW__SPOKE_S": [(0.0, -120.0), (0.0, -500.0)],
    "PREVIEW__SPOKE_SW": [(-160.0, -120.0), (-700.0, -500.0)],
    "PREVIEW__SPOKE_W": [(-160.0, 0.0), (-700.0, 0.0)],
    "PREVIEW__SPOKE_NW": [(-160.0, 120.0), (-700.0, 500.0)],
}

RING_ROADS = {
    "PREVIEW__RING_INNER": [(-240.0, -170.0), (0.0, -190.0), (240.0, -170.0), (300.0, 0.0), (240.0, 170.0), (0.0, 190.0), (-240.0, 170.0), (-300.0, 0.0)],
    "PREVIEW__RING_OUTER": [(-520.0, -360.0), (0.0, -410.0), (520.0, -360.0), (610.0, 0.0), (520.0, 360.0), (0.0, 410.0), (-520.0, 360.0), (-610.0, 0.0)],
}

LOCAL_CROSS_STREETS = {
    **{f"PREVIEW__LOCAL_SOUTH_{index}": ("SOUTH_RESIDENTIAL_RETAIL", [(x, -490.0), (x, -220.0)]) for index, x in enumerate((-420.0, -140.0, 140.0, 420.0), 1)},
    **{f"PREVIEW__LOCAL_WEST_{index}": ("WEST_RESIDENTIAL_SERVICES", [(-690.0, y), (-300.0, y)]) for index, y in enumerate((-160.0, -55.0, 55.0, 160.0), 1)},
    **{f"PREVIEW__LOCAL_EAST_{index}": ("EAST_COMMERCE_WORK", [(300.0, y), (690.0, y)]) for index, y in enumerate((-160.0, -55.0, 55.0, 160.0), 1)},
    **{f"PREVIEW__LOCAL_NORTH_{index}": ("NORTH_ARENA_ENTERTAINMENT", [(x, 220.0), (x, 490.0)]) for index, x in enumerate((-420.0, -140.0, 140.0, 420.0), 1)},
}

PARK_FEATURES = [
    ("PARK__LAWN_SW", "LAWN_QUADRANT", (-82.0, -62.0), (146.0, 106.0, 0.12), "commons"),
    ("PARK__LAWN_SE", "LAWN_QUADRANT", (82.0, -62.0), (146.0, 106.0, 0.12), "commons"),
    ("PARK__LAWN_NW", "LAWN_QUADRANT", (-82.0, 62.0), (146.0, 106.0, 0.12), "commons"),
    ("PARK__LAWN_NE", "LAWN_QUADRANT", (82.0, 62.0), (146.0, 106.0, 0.12), "commons"),
    ("PARK__PROMENADE_EW", "PROMENADE", (0.0, 0.0), (320.0, 10.0, 0.18), "promenade"),
    ("PARK__PROMENADE_NS", "PROMENADE", (0.0, 0.0), (10.0, 240.0, 0.20), "promenade"),
    ("PARK__GROVE_SW", "TREE_GROVE_PLACEHOLDER", (-126.0, -90.0), (24.0, 24.0, 7.0), "grove"),
    ("PARK__GROVE_SE", "TREE_GROVE_PLACEHOLDER", (126.0, -90.0), (24.0, 24.0, 7.0), "grove"),
    ("PARK__GROVE_NW", "TREE_GROVE_PLACEHOLDER", (-126.0, 90.0), (24.0, 24.0, 7.0), "grove"),
    ("PARK__GROVE_NE", "TREE_GROVE_PLACEHOLDER", (126.0, 90.0), (24.0, 24.0, 7.0), "grove"),
]

LANDMARK_LABELS = {
    "STUDIO_APARTMENT": ("STUDIO / APT", (-400.0, -220.0)),
    "APARTMENT_MANAGEMENT": ("APT MGMT", (-330.0, -285.0)),
    "JOB": ("JOB", (360.0, -65.0)),
    "CLOTHING": ("CLOTHING", (-240.0, -220.0)),
    "FURNITURE": ("FURNITURE", (-130.0, -285.0)),
    "ARENA": ("ARENA", (150.0, 225.0)),
    "TICKET_BOOTH": ("TICKET", (270.0, 285.0)),
    "PUBLIC_COURT": ("PUBLIC COURT", (-230.0, 205.0)),
    "COMMONS_PARK": ("COMMONS / PARK", (0.0, 0.0)),
}

TOWER_LABELS = {}
for name, placement, district_or_side, _base, (x, y), _footprint, _height, _color in TOWERS:
    body = name.replace("CORE_TOWER__", "CORE ").replace("SKYLINE_TOWER__", "SKY ").replace("_", " ")
    if placement == "BACKGROUND_SKYLINE":
        x = -710.0 if district_or_side == "WEST" else 710.0 if district_or_side == "EAST" else x
        y = 535.0 if district_or_side == "NORTH" else -535.0 if district_or_side == "SOUTH" else y
    TOWER_LABELS[name] = (body, (x, y))

DISTRICT_LABELS = {
    "SOUTH_RESIDENTIAL_RETAIL": ("SOUTH | RESIDENTIAL + RETAIL", (0.0, -475.0)),
    "WEST_RESIDENTIAL_SERVICES": ("WEST | RESIDENTIAL + SERVICES", (-600.0, 205.0)),
    "EAST_COMMERCE_WORK": ("EAST | COMMERCE + WORK", (600.0, 205.0)),
    "NORTH_ARENA_ENTERTAINMENT": ("NORTH | ARENA + ENTERTAINMENT", (0.0, 475.0)),
}

VIEWS = [
    ("TopDown_RadialMegaCityPreview.png", "top_down", (0.0, 0.0, 1500.0), (0.0, 0.0, 0.0), 2000.0, TOP_RENDER_SIZE),
    ("EyeLevel_SouthResidentialRetailParkSkyline.png", "eye_level", (0.0, -145.0, 1.7), (0.0, 20.0, 12.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_WestResidentialServicesParkSkyline.png", "eye_level", (-185.0, 0.0, 1.7), (20.0, 0.0, 12.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_EastCommerceWorkParkSkyline.png", "eye_level", (185.0, 0.0, 1.7), (-20.0, 0.0, 12.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_NorthArenaEntertainmentParkSkyline.png", "eye_level", (0.0, 145.0, 1.7), (0.0, -20.0, 12.0), None, EYE_RENDER_SIZE),
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def material(name, color, roughness=0.82):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    node = result.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = color
    node.inputs["Roughness"].default_value = roughness
    return result


def add_cube(name, location, dimensions, color, collection, kind, **properties):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[color])
    obj["asset_kind"] = kind
    for key, value in properties.items():
        obj[key] = value
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_polyline(name, points, collection, kind, color, width, cyclic=False, **properties):
    data = bpy.data.curves.new(f"{name}_DATA", "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = width
    data.bevel_resolution = 0
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, (x, y) in zip(spline.points, points):
        point.co = (x, y, 0.12, 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    data.materials.append(MATERIALS[color])
    obj["asset_kind"] = kind
    obj["status"] = "PROPOSED_CIRCULATION"
    obj["distance_canonical"] = False
    obj["cyclic"] = cyclic
    for key, value in properties.items():
        obj[key] = value
    collection.objects.link(obj)
    return obj


def add_text(name, body, location, size, collection, color):
    data = bpy.data.curves.new(f"{name}_DATA", "FONT")
    data.body = body
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = size
    data.extrude = 0.025
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    data.materials.append(MATERIALS[color])
    collection.objects.link(obj)
    return obj


def contrast_ratio(foreground, background):
    def luminance(color):
        channels = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in color[:3]]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def add_review_label(label_id, body, location, size, color, category, collection):
    plate_height = 18.0 if size >= 10.0 else 14.0 if size >= 8.0 else 12.0
    width = max(34.0, len(body) * (5.0 if size >= 8.0 else 4.2))
    x, y = location
    plate = add_cube(
        f"PLATE__{label_id}",
        (x, y, LABEL_PLATE_Z_M),
        (width, plate_height, LABEL_PLATE_DEPTH_M),
        "label",
        collection,
        "review_label_plate",
        label_id=label_id,
        label_category=category,
        top_down_only=True,
        plate_width_m=width,
        plate_height_m=plate_height,
        plate_color="label",
    )
    plate.visible_shadow = False
    text = add_text(f"LABEL__{label_id}", body, (x, y, LABEL_TEXT_Z_M), size, collection, color)
    text.visible_shadow = False
    text["asset_kind"] = "metropolitan_review_label"
    text["label_id"] = label_id
    text["label_category"] = category
    text["top_down_only"] = True
    text["font_size_m"] = size
    text["text_color"] = color
    text["plate_color"] = "label"
    text["contrast_ratio"] = contrast_ratio(COLORS[color], COLORS["label"])
    return text, plate


def point_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.collections):
        if block.name != "Collection":
            bpy.data.collections.remove(block)
    root = bpy.context.scene.collection
    default = bpy.data.collections.get("Collection")
    core = bpy.data.collections.new("PLAYABLE_CORE_PREVIEW")
    skyline = bpy.data.collections.new("BACKGROUND_SKYLINE_PREVIEW")
    guides = bpy.data.collections.new("REVIEW_GUIDES")
    root.children.link(core)
    root.children.link(skyline)
    root.children.link(guides)
    if default:
        root.children.unlink(default)
        bpy.data.collections.remove(default)

    global MATERIALS
    MATERIALS = {name: material(f"MAT__{name.upper()}", color) for name, color in COLORS.items()}

    add_cube("PREVIEW__PLAYABLE_BOUNDARY_1400X1000M", (0.0, 0.0, -0.25), (*PLAYABLE_SIZE_M, 0.5), "ground", core, "playable_boundary", status="NONCANONICAL_PREVIEW", collision_boundary=False)
    for district_id, ((x, y), (width, depth), color) in DISTRICTS.items():
        add_cube(f"DISTRICT__{district_id}", (x, y, 0.04), (width, depth, 0.08), color, core, "district", district_id=district_id, status="PROPOSED_DISTRICT")
    add_cube("LANDMARK__COMMONS_PARK", (0.0, 0.0, 0.18), (*COMMONS_SIZE_M, 0.18), "commons", core, "commons_park", landmark_id="COMMONS_PARK", status="REQUIRED_BETA_LANDMARK")
    for name, role, (x, y), (width, depth, height), color in PARK_FEATURES:
        add_cube(name, (x, y, 0.2 + height / 2.0), (width, depth, height), color, core, "park_placeholder", role=role, status="NONCANONICAL_REVIEW_PLACEHOLDER", final_landscape=False)
    add_cube("LANDMARK__PUBLIC_COURT", (-230.0, 170.0, 0.28), (80.0, 46.0, 0.2), "court", core, "public_court", landmark_id="PUBLIC_COURT", status="REQUIRED_BETA_LANDMARK", inner_ring_access=True)

    base_heights = {}
    for name, district, (x, y), (width, depth, height), color, role, tower_id in STREET_MASSES:
        obj = add_cube(name, (x, y, height / 2.0 + 0.35), (width, depth, height), color, core, "street_mass", district_id=district, role=role, status="NONCANONICAL_PREVIEW", ground_floor_scope="GAMEPLAY_RELEVANT_ONLY", interiors=False, inner_ring_access=role == "REQUIRED_BETA_LANDMARK")
        if tower_id:
            obj["tower_id"] = tower_id
            base_heights[name] = height

    street_guides = []
    for name, points in RADIAL_SPOKES.items():
        street_guides.append(add_polyline(name, points, core, "radial_spoke", "spoke", 1.0, branches_from_park=True))
    for name, points in RING_ROADS.items():
        street_guides.append(add_polyline(name, points, core, "ring_road", "ring", 1.0, cyclic=True))
    for name, (district, points) in LOCAL_CROSS_STREETS.items():
        street_guides.append(add_polyline(name, points, core, "local_cross_street", "local", 0.65, district_id=district))

    for name, placement, district_or_side, base_id, (x, y), (width, depth), height, color in TOWERS:
        bottom = base_heights[base_id] + 0.35 if base_id else 0.35
        target_collection = core if placement == "PLAYABLE_CORE" else skyline
        add_cube(name, (x, y, bottom + height / 2.0), (width, depth, height), color, target_collection, "skyscraper", placement=placement, district_id=district_or_side if placement == "PLAYABLE_CORE" else "", skyline_side=district_or_side if placement == "BACKGROUND_SKYLINE" else "", base_id=base_id or "", status="PROPOSED_SKYSCRAPER", interiors=False)

    top_guides = []
    label_specs = []
    label_specs.extend((f"LANDMARK_{key}", body, location, 11.0, "teal", "REQUIRED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items())
    label_specs.extend((f"TOWER_{key}", body, location, 8.0, "orange", "PLAYABLE_CORE_TOWER" if key.startswith("CORE_") else "BACKGROUND_TOWER") for key, (body, location) in TOWER_LABELS.items())
    label_specs.extend((f"DISTRICT_{key}", body, location, 13.0, "teal", "DISTRICT") for key, (body, location) in DISTRICT_LABELS.items())
    label_specs.extend([
        ("INFO_TITLE", "SUNDALE RADIAL MEGA-CITY PREVIEW | NONCANONICAL", (0.0, 650.0), 13.0, "teal", "INFO"),
        ("INFO_LEGEND", "8 SPOKES + 2 RINGS + 16 LOCAL STREETS | ALL PROPOSED | NO DISTANCE / CAPACITY CLAIM", (0.0, -650.0), 9.0, "orange", "INFO"),
    ])
    for spec in label_specs:
        text, plate = add_review_label(*spec, guides)
        top_guides.extend((text, plate))

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "REVIEW_CAMERA"
    camera.data.lens = 28.0
    camera.data.clip_end = 3000.0
    camera["asset_kind"] = "review_camera"
    for owner in list(camera.users_collection):
        owner.objects.unlink(camera)
    guides.objects.link(camera)
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 500.0))
    sun = bpy.context.object
    sun.name = "REVIEW_SUN"
    sun.rotation_euler = (math.radians(30.0), math.radians(-20.0), math.radians(125.0))
    sun.data.energy = 4.5
    for owner in list(sun.users_collection):
        owner.objects.unlink(sun)
    guides.objects.link(sun)

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 500.0))
    fill = bpy.context.object
    fill.name = "REVIEW_FILL"
    fill.rotation_euler = (math.radians(45.0), math.radians(10.0), math.radians(-45.0))
    fill.data.energy = 1.8
    fill.data.use_shadow = False
    for owner in list(fill.users_collection):
        owner.objects.unlink(fill)
    guides.objects.link(fill)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.world.color = (0.25, 0.28, 0.33)
    scene.view_settings.exposure = 0.8
    scene["phase"] = "Phase 1L.3a radial mega-city replacement preview"
    scene["status"] = "NONCANONICAL_OWNER_PREVIEW"
    scene["production_route_m"] = 800.0
    scene["preview_route_distance_canonical"] = False
    scene["preview_capacity_claim"] = False
    scene["cycles_forbidden"] = True

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for stale in RENDER_DIR.glob("*.png"):
        stale.unlink()
    for filename, view_type, location, target, ortho_scale, (width, height) in VIEWS:
        for guide in top_guides:
            guide.hide_render = view_type != "top_down"
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        camera.data.type = "ORTHO" if view_type == "top_down" else "PERSP"
        camera.data.lens = 28.0
        if ortho_scale:
            camera.data.ortho_scale = ortho_scale
        point_camera(camera, location, target)
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)

    for guide in top_guides:
        guide.hide_render = False
    top_view = VIEWS[0]
    scene.render.resolution_x, scene.render.resolution_y = top_view[5]
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = top_view[4]
    point_camera(camera, top_view[2], top_view[3])
    scene.render.filepath = str(RENDER_DIR / top_view[0])
    bpy.context.preferences.filepaths.save_version = 0
    BLEND_PATH.with_suffix(".blend1").unlink(missing_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)


def expected_label_specs():
    specs = {}
    specs.update({f"LANDMARK_{key}": (body, location, 11.0, "teal", "REQUIRED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items()})
    specs.update({f"TOWER_{key}": (body, location, 8.0, "orange", "PLAYABLE_CORE_TOWER" if key.startswith("CORE_") else "BACKGROUND_TOWER") for key, (body, location) in TOWER_LABELS.items()})
    specs.update({f"DISTRICT_{key}": (body, location, 13.0, "teal", "DISTRICT") for key, (body, location) in DISTRICT_LABELS.items()})
    specs["INFO_TITLE"] = ("SUNDALE RADIAL MEGA-CITY PREVIEW | NONCANONICAL", (0.0, 650.0), 13.0, "teal", "INFO")
    specs["INFO_LEGEND"] = ("8 SPOKES + 2 RINGS + 16 LOCAL STREETS | ALL PROPOSED | NO DISTANCE / CAPACITY CLAIM", (0.0, -650.0), 9.0, "orange", "INFO")
    return specs


def curve_points(obj):
    return [(round(point.co.x, 3), round(point.co.y, 3)) for point in obj.data.splines[0].points]


def validate_scene(require_manifest):
    errors = []
    objects = bpy.data.objects
    boundary = objects.get("PREVIEW__PLAYABLE_BOUNDARY_1400X1000M")
    if not boundary or any(abs(a - b) > 0.001 for a, b in zip(boundary.dimensions[:2], PLAYABLE_SIZE_M)):
        errors.append("playable preview boundary must be exactly 1400x1000m")

    districts = [obj for obj in objects if obj.get("asset_kind") == "district"]
    if {obj.get("district_id") for obj in districts} != set(DISTRICTS) or len(districts) != 4:
        errors.append("exactly four named preview districts are required")
    for district_id, ((x, y), (width, depth), _color) in DISTRICTS.items():
        obj = objects.get(f"DISTRICT__{district_id}")
        if not obj or any(abs(a - b) > 0.001 for a, b in zip(obj.location[:2], (x, y))) or any(abs(a - b) > 0.001 for a, b in zip(obj.dimensions[:2], (width, depth))):
            errors.append(f"{district_id} dimensions/location differ")

    park = objects.get("LANDMARK__COMMONS_PARK")
    if not park or any(abs(a - b) > 0.001 for a, b in zip(park.dimensions[:2], COMMONS_SIZE_M)) or any(abs(value) > 0.001 for value in park.location[:2]):
        errors.append("central Commons/Park must be exactly 320x240m at the city hub")
    park_parts = {obj.name: obj for obj in objects if obj.get("asset_kind") == "park_placeholder"}
    if set(park_parts) != {spec[0] for spec in PARK_FEATURES}:
        errors.append(f"park placeholders must match the exact native low-poly set: {len(park_parts)}")
    for name, role, (x, y), (width, depth, height), _color in PARK_FEATURES:
        obj = park_parts.get(name)
        if not obj or obj.type != "MESH" or obj.get("role") != role or obj.get("final_landscape") is not False:
            errors.append(f"{name} park role/native/finality contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(obj.location, (x, y, 0.2 + height / 2.0))) or any(abs(a - b) > 0.001 for a, b in zip(obj.dimensions, (width, depth, height))):
            errors.append(f"{name} park dimensions/location differ")

    masses = [obj for obj in objects if obj.get("asset_kind") == "street_mass"]
    district_counts = Counter(obj.get("district_id") for obj in masses)
    if len(masses) != 72 or district_counts != Counter({name: 18 for name in DISTRICTS}):
        errors.append(f"street masses must total 72 and 18 per district: {len(masses)}, {district_counts}")
    if any(obj.get("ground_floor_scope") != "GAMEPLAY_RELEVANT_ONLY" or obj.get("interiors") is not False for obj in masses):
        errors.append("street masses must remain exterior blockouts with gameplay-relevant ground floors only")
    expected_masses = {spec[0]: spec for spec in STREET_MASSES}
    if {obj.name for obj in masses} != set(expected_masses):
        errors.append("street mass identities differ from the deterministic contract")
    for name, district, (x, y), (width, depth, height), _color, role, tower_id in STREET_MASSES:
        obj = objects.get(name)
        if not obj or obj.get("district_id") != district or obj.get("role") != role or obj.get("tower_id", "") != (tower_id or ""):
            errors.append(f"{name} district/role/tower contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(obj.location, (x, y, height / 2.0 + 0.35))) or any(abs(a - b) > 0.001 for a, b in zip(obj.dimensions, (width, depth, height))):
            errors.append(f"{name} dimensions/location differ")
    bases = {obj.name: obj for obj in masses if obj.get("role") == "PROPOSED_CORE_TOWER_BASE"}
    base_district_counts = Counter(obj.get("district_id") for obj in bases.values())
    if len(bases) != 12 or base_district_counts != Counter({name: 3 for name in DISTRICTS}):
        errors.append(f"exactly twelve playable-core bases, three per district, are required: {len(bases)}, {base_district_counts}")

    towers = [obj for obj in objects if obj.get("asset_kind") == "skyscraper"]
    placement_counts = Counter(obj.get("placement") for obj in towers)
    core_district_counts = Counter(obj.get("district_id") for obj in towers if obj.get("placement") == "PLAYABLE_CORE")
    background_side_counts = Counter(obj.get("skyline_side") for obj in towers if obj.get("placement") == "BACKGROUND_SKYLINE")
    if len(towers) != 24 or placement_counts != Counter({"PLAYABLE_CORE": 12, "BACKGROUND_SKYLINE": 12}):
        errors.append(f"tower split must be 12 playable/12 background: {len(towers)}, {placement_counts}")
    if core_district_counts != Counter({name: 3 for name in DISTRICTS}) or background_side_counts != Counter({side: 3 for side in ("NORTH", "SOUTH", "EAST", "WEST")}):
        errors.append(f"tower district/side split must remain three each: {core_district_counts}, {background_side_counts}")
    if {obj.name for obj in towers} != {spec[0] for spec in TOWERS}:
        errors.append("tower identities differ from the deterministic contract")
    for tower in towers:
        x, y = tower.location.x, tower.location.y
        half_x, half_y = tower.dimensions.x / 2.0, tower.dimensions.y / 2.0
        wholly_inside = abs(x) + half_x <= PLAYABLE_SIZE_M[0] / 2.0 and abs(y) + half_y <= PLAYABLE_SIZE_M[1] / 2.0
        wholly_outside = x + half_x < -PLAYABLE_SIZE_M[0] / 2.0 or x - half_x > PLAYABLE_SIZE_M[0] / 2.0 or y + half_y < -PLAYABLE_SIZE_M[1] / 2.0 or y - half_y > PLAYABLE_SIZE_M[1] / 2.0
        if tower.get("placement") == "PLAYABLE_CORE" and (not wholly_inside or tower.get("base_id") not in bases):
            errors.append(f"{tower.name} must be inside the boundary on a counted street-level base")
        if tower.get("placement") == "BACKGROUND_SKYLINE" and (not wholly_outside or tower.get("base_id")):
            errors.append(f"{tower.name} must be wholly outside the playable boundary without a core base")
    for name, placement, district_or_side, base_id, (x, y), (width, depth), height, _color in TOWERS:
        tower = objects.get(name)
        bottom = bases[base_id].dimensions.z + 0.35 if base_id else 0.35
        if not tower or tower.get("placement") != placement or tower.get("base_id") != (base_id or ""):
            errors.append(f"{name} placement/base contract differs")
        elif tower.get("district_id") != (district_or_side if placement == "PLAYABLE_CORE" else "") or tower.get("skyline_side") != (district_or_side if placement == "BACKGROUND_SKYLINE" else ""):
            errors.append(f"{name} district/skyline-side contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(tower.location, (x, y, bottom + height / 2.0))) or any(abs(a - b) > 0.001 for a, b in zip(tower.dimensions, (width, depth, height))):
            errors.append(f"{name} dimensions/location differ")

    required_mass_names = {
        "LANDMARK__STUDIO_APARTMENT", "LANDMARK__APARTMENT_MANAGEMENT", "LANDMARK__JOB",
        "LANDMARK__CLOTHING", "LANDMARK__FURNITURE", "LANDMARK__ARENA", "LANDMARK__TICKET_BOOTH",
    }
    if not required_mass_names.issubset({obj.name for obj in masses}) or not objects.get("LANDMARK__PUBLIC_COURT") or not objects.get("LANDMARK__COMMONS_PARK"):
        errors.append("all nine required beta landmarks must be present")
    studio = objects.get("LANDMARK__STUDIO_APARTMENT")
    kiosk = objects.get("LANDMARK__APARTMENT_MANAGEMENT")
    if not studio or not kiosk or abs((studio.location.x + studio.dimensions.x / 2.0) - (kiosk.location.x - kiosk.dimensions.x / 2.0)) > 0.001:
        errors.append("Apartment Management kiosk must stay attached to the Studio/apartment frontage")
    inner_ring_landmarks = [objects.get(name) for name in required_mass_names] + [objects.get("LANDMARK__PUBLIC_COURT")]
    for landmark in inner_ring_landmarks:
        if not landmark:
            continue
        x, y = abs(landmark.location.x), abs(landmark.location.y)
        near_ring = (abs(y - 190.0) <= 90.0 and x <= 430.0) or (abs(x - 300.0) <= 100.0 and y <= 280.0)
        if not near_ring or landmark.get("inner_ring_access") is not True:
            errors.append(f"{landmark.name} must remain on/near the inner destination ring")

    spokes = {obj.name: obj for obj in objects if obj.get("asset_kind") == "radial_spoke"}
    rings = {obj.name: obj for obj in objects if obj.get("asset_kind") == "ring_road"}
    local_streets = {obj.name: obj for obj in objects if obj.get("asset_kind") == "local_cross_street"}
    circulation = list(spokes.values()) + list(rings.values()) + list(local_streets.values())
    if set(spokes) != set(RADIAL_SPOKES) or set(rings) != set(RING_ROADS) or set(local_streets) != set(LOCAL_CROSS_STREETS):
        errors.append(f"street topology must be exact 8 spokes/2 rings/16 locals: {len(spokes)}/{len(rings)}/{len(local_streets)}")
    if any(obj.get("distance_canonical") is not False or "distance_m" in obj for obj in circulation):
        errors.append("all preview streets must remain proposed guides with no canonical distance")
    for name, points in RADIAL_SPOKES.items():
        if name in spokes and (curve_points(spokes[name]) != points or spokes[name].get("branches_from_park") is not True or spokes[name].get("cyclic") is not False):
            errors.append(f"{name} radial topology differs")
    for name, points in RING_ROADS.items():
        if name in rings and (curve_points(rings[name]) != points or rings[name].get("cyclic") is not True):
            errors.append(f"{name} ring topology differs")
    local_district_counts = Counter(obj.get("district_id") for obj in local_streets.values())
    if local_district_counts != Counter({name: 4 for name in DISTRICTS}):
        errors.append(f"local cross streets must remain four per district: {local_district_counts}")
    for name, (district, points) in LOCAL_CROSS_STREETS.items():
        if name in local_streets and (curve_points(local_streets[name]) != points or local_streets[name].get("district_id") != district or local_streets[name].get("cyclic") is not False):
            errors.append(f"{name} local topology differs")
    if [obj for obj in objects if obj.get("asset_kind") == "canonical_route"]:
        errors.append("the radial preview must not recanonize or replace the production route")

    specs = expected_label_specs()
    labels = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "metropolitan_review_label"}
    plates = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "review_label_plate"}
    if set(labels) != set(specs) or set(plates) != set(specs):
        errors.append(f"review labels/plates must cover exactly 9 landmarks + 24 towers + 4 districts + 2 info: labels={len(labels)}, plates={len(plates)}")
    for label_id, (body, (x, y), size, color, category) in specs.items():
        label, plate = labels.get(label_id), plates.get(label_id)
        plate_height = 18.0 if size >= 10.0 else 14.0 if size >= 8.0 else 12.0
        width = max(34.0, len(body) * (5.0 if size >= 8.0 else 4.2))
        if not label or label.data.body != body or label.get("label_category") != category or not label.get("top_down_only"):
            errors.append(f"{label_id} text/category/top-down contract differs")
        elif abs(label.data.size - size) > 0.001 or any(abs(a - b) > 0.001 for a, b in zip(label.location, (x, y, LABEL_TEXT_Z_M))):
            errors.append(f"{label_id} font size/location differs")
        elif label.get("text_color") != color or label.get("contrast_ratio", 0.0) < LABEL_CONTRAST_MIN:
            errors.append(f"{label_id} contrast contract differs")
        if not plate or plate.get("label_category") != category or not plate.get("top_down_only"):
            errors.append(f"{label_id} plate category/top-down contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(plate.dimensions, (width, plate_height, LABEL_PLATE_DEPTH_M))):
            errors.append(f"{label_id} plate dimensions differ")

    render_files = sorted(RENDER_DIR.glob("*.png"))
    if [path.name for path in render_files] != sorted(view[0] for view in VIEWS):
        errors.append(f"expected exactly five named review renders, found {[path.name for path in render_files]}")
    if BLEND_PATH.with_suffix(".blend1").exists():
        errors.append("Blender backup output is forbidden")
    if sum(view[1] == "top_down" for view in VIEWS) != 1 or sum(view[1] == "eye_level" for view in VIEWS) != 4:
        errors.append("review requires exactly one top-down and four eye-level views")
    if any(abs(view[2][2] - 1.7) > 0.001 for view in VIEWS if view[1] == "eye_level"):
        errors.append("all district cameras must remain at 1.7m")
    if VIEWS[0][5] != TOP_RENDER_SIZE or any(view[5] != EYE_RENDER_SIZE for view in VIEWS[1:]):
        errors.append("review resolutions differ from the approved high-resolution top/eye contract")
    camera_obstacles = masses + towers + [obj for obj in (park, objects.get("LANDMARK__PUBLIC_COURT")) if obj]
    for filename, view_type, location, target, _ortho, _resolution in VIEWS:
        if view_type != "eye_level":
            continue
        if abs(target[0]) > COMMONS_SIZE_M[0] / 2.0 or abs(target[1]) > COMMONS_SIZE_M[1] / 2.0:
            errors.append(f"{filename} must frame the central park opening")
        for obstacle in camera_obstacles:
            dx = max(abs(location[0] - obstacle.location.x) - obstacle.dimensions.x / 2.0, 0.0)
            dy = max(abs(location[1] - obstacle.location.y) - obstacle.dimensions.y / 2.0, 0.0)
            if math.hypot(dx, dy) < EYE_CAMERA_CLEARANCE_M:
                errors.append(f"{filename} camera is within {EYE_CAMERA_CLEARANCE_M:.0f}m of {obstacle.name}")
    if bpy.context.scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review engine must be Eevee")
    if bpy.data.libraries or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external Blender libraries/images are forbidden")
    if [obj for obj in objects if obj.get("asset_kind") == "character"]:
        errors.append("production character geometry is forbidden")
    if [obj for obj in objects if obj.get("asset_kind") == "vehicle"]:
        errors.append("vehicles are forbidden in the radial mega-city preview")
    if require_manifest and not MANIFEST_PATH.exists():
        errors.append("manifest.json is missing")
    if errors:
        raise RuntimeError("\n".join(errors))
    print("ODDSWELL_SUNDALE_RADIAL_VALIDATION|result=PASS|playable=1400x1000m|commons=320x240m|districts=4|street_masses=72|street_per_district=18|towers=24|core_towers=12|background_towers=12|required_landmarks=9|spokes=8|rings=2|local_streets=16|canonical_route_distance=false|labels=39|plates=39|views=1_top+4_eye|eye_height_m=1.7|camera_clearance_m=20|engine=eevee|cycles=false|external_refs=0|vehicles=0|interiors=0")
    return district_counts, placement_counts, core_district_counts, background_side_counts


def write_manifest(district_counts, placement_counts, core_district_counts, background_side_counts):
    renders = []
    for filename, view_type, location, target, _ortho, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}", "view_type": view_type, "camera_location_m": location,
            "target_m": target, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3a radial mega-city replacement preview",
        "status": "noncanonical_owner_radial_mega_city_preview",
        "supersedes": "Phase 1L.3a 800x600m/36-mass/10-tower metropolitan preview",
        "engine": "BLENDER_EEVEE_NEXT",
        "cycles": False,
        "production_authority_preserved": {
            "unreal_map": "/Game/Maps/SundaleGraybox",
            "unreal_map_sha256": "180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015",
            "production_route_m": 800.0,
            "production_route_changed": False,
        },
        "preview_contract": {
            "playable_boundary_m": PLAYABLE_SIZE_M,
            "districts": {key: {"center_m": value[0], "size_m": value[1]} for key, value in DISTRICTS.items()},
            "district_count": len(DISTRICTS),
            "street_mass_count": len(STREET_MASSES),
            "street_masses_per_district": dict(district_counts),
            "core_tower_base_count": 12,
            "skyscraper_count": len(TOWERS),
            "tower_placement_counts": dict(placement_counts),
            "core_towers_per_district": dict(core_district_counts),
            "background_towers_per_side": dict(background_side_counts),
            "required_landmarks": list(LANDMARK_LABELS),
            "commons_park_m": COMMONS_SIZE_M,
            "park_placeholder_roles": dict(Counter(spec[1] for spec in PARK_FEATURES)),
            "preview_circulation": {
                "radial_spokes": len(RADIAL_SPOKES),
                "ring_roads": len(RING_ROADS),
                "local_cross_streets": len(LOCAL_CROSS_STREETS),
                "local_cross_streets_per_district": dict(Counter(spec[0] for spec in LOCAL_CROSS_STREETS.values())),
                "canonical": False,
                "exact_distance_m": None,
                "capacity_claim": False,
                "travel_time_claim": False,
                "collision_claim": False,
            },
            "first_hour_landmarks_near_inner_ring": True,
            "eye_camera_clearance_m": EYE_CAMERA_CLEARANCE_M,
            "eye_view_targets_commons_park": True,
            "street_guides_visible_in_eye_views": True,
            "street_level_only_initially": True,
            "vehicles": False,
            "interiors": False,
        },
        "label_contract": {
            "top_down_only": True,
            "required_landmark_count": len(LANDMARK_LABELS),
            "tower_count": len(TOWER_LABELS),
            "district_count": len(DISTRICT_LABELS),
            "info_count": 2,
            "total": len(expected_label_specs()),
            "plate_count": len(expected_label_specs()),
            "minimum_contrast_ratio": LABEL_CONTRAST_MIN,
            "labels": {key: spec[0] for key, spec in expected_label_specs().items()},
        },
        "renders": renders,
        "external_references": [],
        "limitations": [
            "not production Unreal geometry or a production-route replacement",
            "not approved final placement, capacity, travel time, interiors, facades, collision, materials, lighting, accessibility, usability, performance, or readiness",
            "background skyline towers are outside the proposed playable/collision boundary",
            "park lawns, promenades, and tree groves are native low-poly review placeholders, not final landscape assets",
        ],
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    validate_only = "--validate-only" in sys.argv
    if not validate_only:
        build_scene()
        district_counts, placement_counts, core_district_counts, background_side_counts = validate_scene(require_manifest=False)
        write_manifest(district_counts, placement_counts, core_district_counts, background_side_counts)
    else:
        district_counts, placement_counts, core_district_counts, background_side_counts = validate_scene(require_manifest=True)
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        contract = manifest.get("preview_contract", {})
        if any((
            contract.get("street_masses_per_district") != dict(district_counts),
            contract.get("tower_placement_counts") != dict(placement_counts),
            contract.get("core_towers_per_district") != dict(core_district_counts),
            contract.get("background_towers_per_side") != dict(background_side_counts),
        )):
            raise RuntimeError("manifest preview counts differ from the Blend")
        if manifest.get("label_contract", {}).get("labels") != {key: spec[0] for key, spec in expected_label_specs().items()}:
            raise RuntimeError("manifest label contract differs from the Blend")
        for render in manifest["renders"]:
            path = ROOT / render["file"]
            if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
                raise RuntimeError(f"render hash differs: {path.name}")
        print("ODDSWELL_SUNDALE_RADIAL_FOCUSED|result=PASS|manifest=true|render_hashes=5|districts=4|street_masses=72|towers=24|core=12|background=12|landmarks=9|spokes=8|rings=2|locals=16|labels=39|plates=39|camera_clearance_m=20|canonical_route_distance=false|manual_input=false")


if __name__ == "__main__":
    main()
