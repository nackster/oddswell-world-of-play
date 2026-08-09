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
TOP_RENDER_SIZE = (1920, 1440)
EYE_RENDER_SIZE = (1280, 720)
PLAYABLE_SIZE_M = (800.0, 600.0)
COMMONS_SIZE_M = (280.0, 140.0)
LABEL_TEXT_Z_M = 300.0
LABEL_PLATE_Z_M = 299.7
LABEL_PLATE_DEPTH_M = 0.2
LABEL_CONTRAST_MIN = 5.0

COLORS = {
    "ground": (0.12, 0.14, 0.15, 1.0),
    "south": (0.30, 0.27, 0.23, 1.0),
    "central": (0.24, 0.31, 0.28, 1.0),
    "north": (0.25, 0.27, 0.31, 1.0),
    "road": (0.20, 0.23, 0.25, 1.0),
    "shortcut": (0.43, 0.50, 0.38, 1.0),
    "commons": (0.35, 0.48, 0.34, 1.0),
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
    "SOUTH_RESIDENTIAL_RETAIL": ((0.0, -190.0), (800.0, 220.0), "south"),
    "CENTRAL_CIVIC_COMMONS": ((0.0, 20.0), (800.0, 200.0), "central"),
    "NORTH_ARENA_ENTERTAINMENT": ((0.0, 210.0), (800.0, 180.0), "north"),
}

# Exactly 12 masses per district. Four PROPOSED_CORE_TOWER_BASE entries support the four playable-core towers.
STREET_MASSES = [
    ("LANDMARK__STUDIO_APARTMENT", "SOUTH_RESIDENTIAL_RETAIL", (-310.0, -235.0), (100.0, 70.0, 22.0), "limestone", "REQUIRED_BETA_LANDMARK", None),
    ("LANDMARK__APARTMENT_MANAGEMENT", "SOUTH_RESIDENTIAL_RETAIL", (-248.0, -235.0), (24.0, 24.0, 8.0), "terracotta", "REQUIRED_BETA_LANDMARK", None),
    ("LANDMARK__JOB", "SOUTH_RESIDENTIAL_RETAIL", (-140.0, -235.0), (80.0, 60.0, 20.0), "terracotta", "REQUIRED_BETA_LANDMARK", None),
    ("LANDMARK__CLOTHING", "SOUTH_RESIDENTIAL_RETAIL", (-30.0, -235.0), (80.0, 60.0, 22.0), "limestone", "REQUIRED_BETA_LANDMARK", None),
    ("LANDMARK__FURNITURE", "SOUTH_RESIDENTIAL_RETAIL", (80.0, -235.0), (80.0, 60.0, 22.0), "limestone", "REQUIRED_BETA_LANDMARK", None),
    ("CORE_BASE__SOUTH_01", "SOUTH_RESIDENTIAL_RETAIL", (-60.0, -125.0), (80.0, 55.0, 24.0), "charcoal", "PROPOSED_CORE_TOWER_BASE", "CORE_TOWER__SOUTH_01"),
    ("STREET__SOUTH_01", "SOUTH_RESIDENTIAL_RETAIL", (210.0, -235.0), (90.0, 60.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__SOUTH_02", "SOUTH_RESIDENTIAL_RETAIL", (330.0, -235.0), (70.0, 60.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__SOUTH_03", "SOUTH_RESIDENTIAL_RETAIL", (-320.0, -125.0), (90.0, 50.0, 18.0), "charcoal", "PROPOSED_STREET_MASS", None),
    ("STREET__SOUTH_04", "SOUTH_RESIDENTIAL_RETAIL", (-205.0, -125.0), (80.0, 50.0, 20.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__SOUTH_05", "SOUTH_RESIDENTIAL_RETAIL", (175.0, -125.0), (90.0, 50.0, 24.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__SOUTH_06", "SOUTH_RESIDENTIAL_RETAIL", (305.0, -125.0), (90.0, 50.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("CORE_BASE__CENTRAL_01", "CENTRAL_CIVIC_COMMONS", (-340.0, 45.0), (70.0, 70.0, 26.0), "charcoal", "PROPOSED_CORE_TOWER_BASE", "CORE_TOWER__CENTRAL_01"),
    ("CORE_BASE__CENTRAL_02", "CENTRAL_CIVIC_COMMONS", (340.0, 45.0), (70.0, 70.0, 26.0), "charcoal", "PROPOSED_CORE_TOWER_BASE", "CORE_TOWER__CENTRAL_02"),
    ("STREET__CENTRAL_01", "CENTRAL_CIVIC_COMMONS", (-340.0, -50.0), (70.0, 50.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_02", "CENTRAL_CIVIC_COMMONS", (-250.0, -55.0), (70.0, 40.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_03", "CENTRAL_CIVIC_COMMONS", (-235.0, 60.0), (80.0, 50.0, 22.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_04", "CENTRAL_CIVIC_COMMONS", (-340.0, 105.0), (70.0, 40.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_05", "CENTRAL_CIVIC_COMMONS", (-180.0, -65.0), (60.0, 30.0, 16.0), "charcoal", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_06", "CENTRAL_CIVIC_COMMONS", (340.0, -50.0), (70.0, 50.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_07", "CENTRAL_CIVIC_COMMONS", (250.0, -55.0), (70.0, 40.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_08", "CENTRAL_CIVIC_COMMONS", (235.0, 60.0), (80.0, 50.0, 22.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_09", "CENTRAL_CIVIC_COMMONS", (340.0, 105.0), (70.0, 40.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__CENTRAL_10", "CENTRAL_CIVIC_COMMONS", (180.0, -65.0), (60.0, 30.0, 16.0), "charcoal", "PROPOSED_STREET_MASS", None),
    ("LANDMARK__ARENA", "NORTH_ARENA_ENTERTAINMENT", (160.0, 230.0), (220.0, 100.0, 30.0), "limestone", "REQUIRED_BETA_LANDMARK", None),
    ("LANDMARK__TICKET_BOOTH", "NORTH_ARENA_ENTERTAINMENT", (285.0, 230.0), (30.0, 30.0, 10.0), "terracotta", "REQUIRED_BETA_LANDMARK", None),
    ("CORE_BASE__NORTH_01", "NORTH_ARENA_ENTERTAINMENT", (-340.0, 245.0), (70.0, 70.0, 28.0), "charcoal", "PROPOSED_CORE_TOWER_BASE", "CORE_TOWER__NORTH_01"),
    ("STREET__NORTH_01", "NORTH_ARENA_ENTERTAINMENT", (-340.0, 150.0), (70.0, 50.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_02", "NORTH_ARENA_ENTERTAINMENT", (-250.0, 135.0), (80.0, 40.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_03", "NORTH_ARENA_ENTERTAINMENT", (-150.0, 135.0), (80.0, 40.0, 22.0), "charcoal", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_04", "NORTH_ARENA_ENTERTAINMENT", (-50.0, 135.0), (80.0, 40.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_05", "NORTH_ARENA_ENTERTAINMENT", (50.0, 135.0), (80.0, 40.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_06", "NORTH_ARENA_ENTERTAINMENT", (150.0, 135.0), (80.0, 40.0, 22.0), "charcoal", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_07", "NORTH_ARENA_ENTERTAINMENT", (250.0, 135.0), (80.0, 40.0, 18.0), "limestone", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_08", "NORTH_ARENA_ENTERTAINMENT", (350.0, 145.0), (60.0, 50.0, 20.0), "terracotta", "PROPOSED_STREET_MASS", None),
    ("STREET__NORTH_09", "NORTH_ARENA_ENTERTAINMENT", (-120.0, 235.0), (80.0, 60.0, 24.0), "limestone", "PROPOSED_STREET_MASS", None),
]

TOWERS = [
    ("CORE_TOWER__SOUTH_01", "PLAYABLE_CORE", "CORE_BASE__SOUTH_01", (-60.0, -125.0), (36.0, 36.0), 150.0, "cobalt"),
    ("CORE_TOWER__CENTRAL_01", "PLAYABLE_CORE", "CORE_BASE__CENTRAL_01", (-340.0, 45.0), (40.0, 40.0), 180.0, "terracotta"),
    ("CORE_TOWER__CENTRAL_02", "PLAYABLE_CORE", "CORE_BASE__CENTRAL_02", (340.0, 45.0), (40.0, 40.0), 165.0, "cobalt"),
    ("CORE_TOWER__NORTH_01", "PLAYABLE_CORE", "CORE_BASE__NORTH_01", (-340.0, 245.0), (40.0, 40.0), 200.0, "terracotta"),
    ("SKYLINE_TOWER__WEST_SOUTH", "BACKGROUND_SKYLINE", None, (-500.0, -170.0), (50.0, 50.0), 170.0, "charcoal"),
    ("SKYLINE_TOWER__WEST_NORTH", "BACKGROUND_SKYLINE", None, (-500.0, 170.0), (55.0, 55.0), 220.0, "limestone"),
    ("SKYLINE_TOWER__NORTH_01", "BACKGROUND_SKYLINE", None, (-260.0, 390.0), (60.0, 60.0), 240.0, "charcoal"),
    ("SKYLINE_TOWER__NORTH_02", "BACKGROUND_SKYLINE", None, (0.0, 410.0), (55.0, 55.0), 210.0, "terracotta"),
    ("SKYLINE_TOWER__NORTH_03", "BACKGROUND_SKYLINE", None, (280.0, 390.0), (60.0, 60.0), 250.0, "limestone"),
    ("SKYLINE_TOWER__EAST", "BACKGROUND_SKYLINE", None, (500.0, 100.0), (50.0, 50.0), 190.0, "charcoal"),
]

BOULEVARDS = {
    "PREVIEW__BOULEVARD_SOUTH": ((0.0, -185.0, 0.31), (770.0, 18.0, 0.12)),
    "PREVIEW__BOULEVARD_CENTRAL_WEST": ((-270.0, 0.0, 0.31), (230.0, 14.0, 0.12)),
    "PREVIEW__BOULEVARD_CENTRAL_EAST": ((270.0, 0.0, 0.31), (230.0, 14.0, 0.12)),
    "PREVIEW__BOULEVARD_NORTH": ((0.0, 165.0, 0.31), (770.0, 14.0, 0.12)),
    "PREVIEW__BOULEVARD_WEST_SPINE": ((-385.0, -10.0, 0.31), (14.0, 560.0, 0.12)),
    "PREVIEW__BOULEVARD_EAST_SPINE": ((385.0, -10.0, 0.31), (14.0, 560.0, 0.12)),
}

SHORTCUTS = {
    "PREVIEW__SHORTCUT_STUDIO_COMMONS": [(-310.0, -190.0), (-230.0, -120.0), (-150.0, -45.0)],
    "PREVIEW__SHORTCUT_COMMONS_ARENA": [(140.0, 80.0), (170.0, 130.0), (205.0, 175.0)],
}

LANDMARK_LABELS = {
    "STUDIO_APARTMENT": ("STUDIO / APT", (-310.0, -235.0)),
    "APARTMENT_MANAGEMENT": ("APT MGMT", (-248.0, -235.0)),
    "JOB": ("JOB", (-140.0, -235.0)),
    "CLOTHING": ("CLOTHING", (-30.0, -235.0)),
    "FURNITURE": ("FURNITURE", (80.0, -235.0)),
    "ARENA": ("ARENA", (160.0, 230.0)),
    "TICKET_BOOTH": ("TICKET", (285.0, 230.0)),
    "PUBLIC_COURT": ("PUBLIC COURT", (-235.0, 220.0)),
    "COMMONS_PARK": ("COMMONS / PARK", (0.0, 25.0)),
}

TOWER_LABELS = {
    "CORE_TOWER__SOUTH_01": ("CORE TOWER S1", (-60.0, -125.0)),
    "CORE_TOWER__CENTRAL_01": ("CORE TOWER C1", (-340.0, 45.0)),
    "CORE_TOWER__CENTRAL_02": ("CORE TOWER C2", (340.0, 45.0)),
    "CORE_TOWER__NORTH_01": ("CORE TOWER N1", (-340.0, 245.0)),
    "SKYLINE_TOWER__WEST_SOUTH": ("SKY W1", (-500.0, -170.0)),
    "SKYLINE_TOWER__WEST_NORTH": ("SKY W2", (-500.0, 170.0)),
    "SKYLINE_TOWER__NORTH_01": ("SKY N1", (-260.0, 390.0)),
    "SKYLINE_TOWER__NORTH_02": ("SKY N2", (0.0, 410.0)),
    "SKYLINE_TOWER__NORTH_03": ("SKY N3", (280.0, 390.0)),
    "SKYLINE_TOWER__EAST": ("SKY E1", (500.0, 100.0)),
}

DISTRICT_LABELS = {
    "SOUTH_RESIDENTIAL_RETAIL": ("SOUTH | RESIDENTIAL + RETAIL", (0.0, -290.0)),
    "CENTRAL_CIVIC_COMMONS": ("CENTRAL | CIVIC COMMONS", (0.0, 105.0)),
    "NORTH_ARENA_ENTERTAINMENT": ("NORTH | ARENA + ENTERTAINMENT", (0.0, 290.0)),
}

VIEWS = [
    ("TopDown_MetropolitanPreview.png", "top_down", (0.0, 30.0, 950.0), (0.0, 30.0, 0.0), 1100.0, TOP_RENDER_SIZE),
    ("EyeLevel_SouthResidentialRetail.png", "eye_level", (-340.0, -185.0, 1.7), (320.0, -180.0, 35.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_CentralCommonsCivicSkyline.png", "eye_level", (-80.0, 20.0, 1.7), (260.0, 60.0, 55.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_NorthArenaEntertainment.png", "eye_level", (-260.0, 200.0, 1.7), (200.0, 235.0, 50.0), None, EYE_RENDER_SIZE),
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


def add_polyline(name, points, collection):
    data = bpy.data.curves.new(f"{name}_DATA", "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = 1.5
    data.bevel_resolution = 0
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, (x, y) in zip(spline.points, points):
        point.co = (x, y, 0.6, 1.0)
    obj = bpy.data.objects.new(name, data)
    data.materials.append(MATERIALS["shortcut"])
    obj["asset_kind"] = "proposed_shortcut"
    obj["status"] = "PROPOSED_CIRCULATION"
    obj["distance_canonical"] = False
    obj["top_down_only"] = True
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

    add_cube("PREVIEW__PLAYABLE_BOUNDARY_800X600M", (0.0, 0.0, -0.25), (800.0, 600.0, 0.5), "ground", core, "playable_boundary", status="NONCANONICAL_PREVIEW", collision_boundary=False)
    for district_id, ((x, y), (width, depth), color) in DISTRICTS.items():
        add_cube(f"DISTRICT__{district_id}", (x, y, 0.04), (width, depth, 0.08), color, core, "district", district_id=district_id, status="PROPOSED_DISTRICT")
    add_cube("LANDMARK__COMMONS_PARK", (0.0, 25.0, 0.18), (*COMMONS_SIZE_M, 0.18), "commons", core, "commons_park", landmark_id="COMMONS_PARK", status="REQUIRED_BETA_LANDMARK")
    add_cube("LANDMARK__PUBLIC_COURT", (-235.0, 220.0, 0.28), (90.0, 50.0, 0.2), "court", core, "public_court", landmark_id="PUBLIC_COURT", status="REQUIRED_BETA_LANDMARK")

    base_heights = {}
    for name, district, (x, y), (width, depth, height), color, role, tower_id in STREET_MASSES:
        obj = add_cube(name, (x, y, height / 2.0 + 0.35), (width, depth, height), color, core, "street_mass", district_id=district, role=role, status="NONCANONICAL_PREVIEW", ground_floor_scope="GAMEPLAY_RELEVANT_ONLY", interiors=False)
        if tower_id:
            obj["tower_id"] = tower_id
            base_heights[name] = height

    for name, location, dimensions in [(name, location, dimensions) for name, (location, dimensions) in BOULEVARDS.items()]:
        add_cube(name, location, dimensions, "road", core, "proposed_boulevard", status="PROPOSED_CIRCULATION", distance_canonical=False)
    shortcut_guides = [add_polyline(name, points, core) for name, points in SHORTCUTS.items()]

    for name, placement, base_id, (x, y), (width, depth), height, color in TOWERS:
        bottom = base_heights[base_id] + 0.35 if base_id else 0.35
        target_collection = core if placement == "PLAYABLE_CORE" else skyline
        add_cube(name, (x, y, bottom + height / 2.0), (width, depth, height), color, target_collection, "skyscraper", placement=placement, base_id=base_id or "", status="PROPOSED_SKYSCRAPER", interiors=False)

    top_guides = []
    label_specs = []
    label_specs.extend((f"LANDMARK_{key}", body, location, 8.0, "teal", "REQUIRED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items())
    label_specs.extend((f"TOWER_{key}", body, location, 6.5, "orange", "PLAYABLE_CORE_TOWER" if key.startswith("CORE_") else "BACKGROUND_TOWER") for key, (body, location) in TOWER_LABELS.items())
    label_specs.extend((f"DISTRICT_{key}", body, location, 10.0, "teal", "DISTRICT") for key, (body, location) in DISTRICT_LABELS.items())
    label_specs.extend([
        ("INFO_TITLE", "SUNDALE METROPOLITAN PREVIEW | NONCANONICAL", (0.0, 350.0), 10.0, "teal", "INFO"),
        ("INFO_LEGEND", "TEAL = REQUIRED / DISTRICT | ORANGE = PROPOSED TOWER | ROADS = PROPOSED, NO DISTANCE CLAIM", (0.0, -350.0), 7.0, "orange", "INFO"),
    ])
    for spec in label_specs:
        text, plate = add_review_label(*spec, guides)
        top_guides.extend((text, plate))

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "REVIEW_CAMERA"
    camera.data.lens = 28.0
    camera.data.clip_end = 2000.0
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
    scene["phase"] = "Phase 1L.3a metropolitan replacement preview"
    scene["status"] = "NONCANONICAL_OWNER_PREVIEW"
    scene["production_route_m"] = 800.0
    scene["preview_route_distance_canonical"] = False
    scene["cycles_forbidden"] = True

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for stale in RENDER_DIR.glob("*.png"):
        stale.unlink()
    for filename, view_type, location, target, ortho_scale, (width, height) in VIEWS:
        for guide in top_guides + shortcut_guides:
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

    for guide in top_guides + shortcut_guides:
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
    specs.update({f"LANDMARK_{key}": (body, location, 8.0, "teal", "REQUIRED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items()})
    specs.update({f"TOWER_{key}": (body, location, 6.5, "orange", "PLAYABLE_CORE_TOWER" if key.startswith("CORE_") else "BACKGROUND_TOWER") for key, (body, location) in TOWER_LABELS.items()})
    specs.update({f"DISTRICT_{key}": (body, location, 10.0, "teal", "DISTRICT") for key, (body, location) in DISTRICT_LABELS.items()})
    specs["INFO_TITLE"] = ("SUNDALE METROPOLITAN PREVIEW | NONCANONICAL", (0.0, 350.0), 10.0, "teal", "INFO")
    specs["INFO_LEGEND"] = ("TEAL = REQUIRED / DISTRICT | ORANGE = PROPOSED TOWER | ROADS = PROPOSED, NO DISTANCE CLAIM", (0.0, -350.0), 7.0, "orange", "INFO")
    return specs


def validate_scene(require_manifest):
    errors = []
    objects = bpy.data.objects
    boundary = objects.get("PREVIEW__PLAYABLE_BOUNDARY_800X600M")
    if not boundary or any(abs(a - b) > 0.001 for a, b in zip(boundary.dimensions[:2], PLAYABLE_SIZE_M)):
        errors.append("playable preview boundary must be exactly 800x600m")

    districts = [obj for obj in objects if obj.get("asset_kind") == "district"]
    if {obj.get("district_id") for obj in districts} != set(DISTRICTS) or len(districts) != 3:
        errors.append("exactly three named preview districts are required")

    masses = [obj for obj in objects if obj.get("asset_kind") == "street_mass"]
    district_counts = Counter(obj.get("district_id") for obj in masses)
    if len(masses) != 36 or district_counts != Counter({name: 12 for name in DISTRICTS}):
        errors.append(f"street masses must total 36 and 12 per district: {len(masses)}, {district_counts}")
    if any(obj.get("ground_floor_scope") != "GAMEPLAY_RELEVANT_ONLY" or obj.get("interiors") is not False for obj in masses):
        errors.append("street masses must remain exterior blockouts with gameplay-relevant ground floors only")
    bases = {obj.name: obj for obj in masses if obj.get("role") == "PROPOSED_CORE_TOWER_BASE"}
    if len(bases) != 4:
        errors.append(f"exactly four playable-core tower bases are required, found {len(bases)}")

    towers = [obj for obj in objects if obj.get("asset_kind") == "skyscraper"]
    placement_counts = Counter(obj.get("placement") for obj in towers)
    if len(towers) != 10 or placement_counts != Counter({"PLAYABLE_CORE": 4, "BACKGROUND_SKYLINE": 6}):
        errors.append(f"tower split must be 4 playable/6 background: {len(towers)}, {placement_counts}")
    for tower in towers:
        x, y = tower.location.x, tower.location.y
        half_x, half_y = tower.dimensions.x / 2.0, tower.dimensions.y / 2.0
        wholly_inside = abs(x) + half_x <= PLAYABLE_SIZE_M[0] / 2.0 and abs(y) + half_y <= PLAYABLE_SIZE_M[1] / 2.0
        wholly_outside = x + half_x < -PLAYABLE_SIZE_M[0] / 2.0 or x - half_x > PLAYABLE_SIZE_M[0] / 2.0 or y + half_y < -PLAYABLE_SIZE_M[1] / 2.0 or y - half_y > PLAYABLE_SIZE_M[1] / 2.0
        if tower.get("placement") == "PLAYABLE_CORE" and (not wholly_inside or tower.get("base_id") not in bases):
            errors.append(f"{tower.name} must be inside the boundary on a counted street-level base")
        if tower.get("placement") == "BACKGROUND_SKYLINE" and (not wholly_outside or tower.get("base_id")):
            errors.append(f"{tower.name} must be wholly outside the playable boundary without a core base")

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

    boulevards = [obj for obj in objects if obj.get("asset_kind") == "proposed_boulevard"]
    shortcuts = [obj for obj in objects if obj.get("asset_kind") == "proposed_shortcut"]
    circulation = boulevards + shortcuts
    if len(boulevards) != 6 or len(shortcuts) != 2 or any(obj.get("distance_canonical") is not False or "distance_m" in obj for obj in circulation):
        errors.append("preview circulation must remain six boulevards plus two shortcuts with no canonical distance")
    if any(obj.get("top_down_only") is not True for obj in shortcuts):
        errors.append("review shortcut guides must remain top-down-only rather than eye-level barriers")
    if [obj for obj in objects if obj.get("asset_kind") == "canonical_route"]:
        errors.append("the metropolitan preview must not recanonize or replace the production route")

    specs = expected_label_specs()
    labels = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "metropolitan_review_label"}
    plates = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "review_label_plate"}
    if set(labels) != set(specs) or set(plates) != set(specs):
        errors.append(f"review labels/plates must cover exactly 9 landmarks + 10 towers + 3 districts + 2 info: labels={len(labels)}, plates={len(plates)}")
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
        errors.append(f"expected exactly four named review renders, found {[path.name for path in render_files]}")
    if BLEND_PATH.with_suffix(".blend1").exists():
        errors.append("Blender backup output is forbidden")
    if sum(view[1] == "top_down" for view in VIEWS) != 1 or sum(view[1] == "eye_level" for view in VIEWS) != 3:
        errors.append("review requires exactly one top-down and three eye-level views")
    if any(abs(view[2][2] - 1.7) > 0.001 for view in VIEWS if view[1] == "eye_level"):
        errors.append("all district cameras must remain at 1.7m")
    if VIEWS[0][5] != TOP_RENDER_SIZE or any(view[5] != EYE_RENDER_SIZE for view in VIEWS[1:]):
        errors.append("review resolutions differ from the approved high-resolution top/eye contract")
    if bpy.context.scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review engine must be Eevee")
    if bpy.data.libraries or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external Blender libraries/images are forbidden")
    if [obj for obj in objects if obj.get("asset_kind") == "character"]:
        errors.append("production character geometry is forbidden")
    if [obj for obj in objects if obj.get("asset_kind") == "vehicle"]:
        errors.append("vehicles are forbidden in the metropolitan preview")
    if require_manifest and not MANIFEST_PATH.exists():
        errors.append("manifest.json is missing")
    if errors:
        raise RuntimeError("\n".join(errors))
    print("ODDSWELL_SUNDALE_METRO_VALIDATION|result=PASS|playable=800x600m|districts=3|street_masses=36|street_per_district=12|towers=10|core_towers=4|background_towers=6|required_landmarks=9|boulevards=6|shortcuts=2|canonical_route_distance=false|labels=24|plates=24|views=1_top+3_eye|eye_height_m=1.7|engine=eevee|cycles=false|external_refs=0")
    return district_counts, placement_counts


def write_manifest(district_counts, placement_counts):
    renders = []
    for filename, view_type, location, target, _ortho, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}", "view_type": view_type, "camera_location_m": location,
            "target_m": target, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3a metropolitan replacement preview",
        "status": "noncanonical_owner_metropolitan_preview",
        "supersedes": "Phase 1L.3a 340x280m small-city massing proposal",
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
            "core_tower_base_count": 4,
            "skyscraper_count": len(TOWERS),
            "tower_placement_counts": dict(placement_counts),
            "required_landmarks": list(LANDMARK_LABELS),
            "commons_park_m": COMMONS_SIZE_M,
            "preview_circulation": {"boulevards": len(BOULEVARDS), "shortcuts": len(SHORTCUTS), "canonical": False, "exact_distance_m": None},
            "street_level_only_initially": True,
            "vehicles": False,
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
            "not approved final placement, capacity, interiors, facades, collision, materials, lighting, accessibility, usability, performance, or readiness",
            "background skyline towers are outside the proposed playable/collision boundary",
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
        district_counts, placement_counts = validate_scene(require_manifest=False)
        write_manifest(district_counts, placement_counts)
    else:
        district_counts, placement_counts = validate_scene(require_manifest=True)
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        contract = manifest.get("preview_contract", {})
        if contract.get("street_masses_per_district") != dict(district_counts) or contract.get("tower_placement_counts") != dict(placement_counts):
            raise RuntimeError("manifest preview counts differ from the Blend")
        if manifest.get("label_contract", {}).get("labels") != {key: spec[0] for key, spec in expected_label_specs().items()}:
            raise RuntimeError("manifest label contract differs from the Blend")
        for render in manifest["renders"]:
            path = ROOT / render["file"]
            if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
                raise RuntimeError(f"render hash differs: {path.name}")
        print("ODDSWELL_SUNDALE_METRO_FOCUSED|result=PASS|manifest=true|render_hashes=4|districts=3|street_masses=36|towers=10|core=4|background=6|landmarks=9|labels=24|plates=24|canonical_route_distance=false|manual_input=false")


if __name__ == "__main__":
    main()
