"""Build and validate the noncanonical Sundale business-cluster review preview."""

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
TOP_RENDER_SIZE = (3200, 2400)
EYE_RENDER_SIZE = (1280, 720)
PLAYABLE_SIZE_M = (2400.0, 1800.0)
COMMONS_SIZE_M = (600.0, 420.0)
LABEL_TEXT_Z_M = 500.0
LABEL_PLATE_Z_M = 499.7
LABEL_PLATE_DEPTH_M = 0.2
LABEL_CONTRAST_MIN = 5.0
EYE_CAMERA_CLEARANCE_M = 20.0

COLORS = {
    "ground": (0.12, 0.14, 0.15, 1.0),
    "financial_district": (0.34, 0.31, 0.23, 1.0),
    "arena_district": (0.25, 0.27, 0.31, 1.0),
    "shopping_district": (0.28, 0.30, 0.36, 1.0),
    "dining_district": (0.31, 0.24, 0.28, 1.0),
    "home_district": (0.24, 0.31, 0.29, 1.0),
    "residential_district": (0.30, 0.27, 0.23, 1.0),
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
    "restaurant": (0.82, 0.39, 0.16, 1.0),
    "nightlife": (0.58, 0.24, 0.68, 1.0),
    "shopping": (0.15, 0.43, 0.72, 1.0),
    "furniture": (0.10, 0.55, 0.47, 1.0),
    "financial": (0.82, 0.66, 0.20, 1.0),
    "court": (0.28, 0.45, 0.39, 1.0),
    "label": (0.03, 0.04, 0.05, 1.0),
}

DISTRICTS = {
    "FINANCIAL_DOWNTOWN": ((800.0, 370.0), (550.0, 440.0), "financial_district"),
    "ARENA_ENTERTAINMENT": ((0.0, 650.0), (1000.0, 400.0), "arena_district"),
    "SHOPPING_RETAIL": ((800.0, -370.0), (550.0, 440.0), "shopping_district"),
    "DINING_NIGHTLIFE": ((0.0, -650.0), (1000.0, 400.0), "dining_district"),
    "HOME_DESIGN_FURNITURE": ((-800.0, -370.0), (550.0, 440.0), "home_district"),
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": ((-800.0, 370.0), (550.0, 440.0), "residential_district"),
}

DISTRICT_SLOTS = {
    "FINANCIAL_DOWNTOWN": [(x, y) for y in (190.0, 265.0, 340.0, 415.0, 490.0, 565.0) for x in (590.0, 740.0, 890.0, 1040.0)],
    "ARENA_ENTERTAINMENT": [(x, y) for y in (500.0, 600.0, 700.0, 800.0) for x in (-420.0, -252.0, -84.0, 84.0, 252.0, 420.0)],
    "SHOPPING_RETAIL": [(x, y) for y in (-190.0, -265.0, -340.0, -415.0, -490.0, -565.0) for x in (590.0, 740.0, 890.0, 1040.0)],
    "DINING_NIGHTLIFE": [(x, y) for y in (-500.0, -600.0, -700.0, -800.0) for x in (-420.0, -252.0, -84.0, 84.0, 252.0, 420.0)],
    "HOME_DESIGN_FURNITURE": [(x, y) for y in (-190.0, -265.0, -340.0, -415.0, -490.0, -565.0) for x in (-590.0, -740.0, -890.0, -1040.0)],
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": [(x, y) for y in (190.0, 265.0, 340.0, 415.0, 490.0, 565.0) for x in (-590.0, -740.0, -890.0, -1040.0)],
}

CORE_TOWER_INDICES = {
    "FINANCIAL_DOWNTOWN": tuple(range(4, 16)),
    "ARENA_ENTERTAINMENT": (6, 7, 10, 11, 14, 15),
    "SHOPPING_RETAIL": (6, 9, 12, 15, 19),
    "DINING_NIGHTLIFE": (6, 9, 12, 15, 18),
    "HOME_DESIGN_FURNITURE": (6, 9, 14, 17),
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": (6, 9, 14, 17),
}

DISTRICT_SHORT = {
    "FINANCIAL_DOWNTOWN": "FINANCIAL",
    "ARENA_ENTERTAINMENT": "ARENA",
    "SHOPPING_RETAIL": "SHOPPING",
    "DINING_NIGHTLIFE": "DINING",
    "HOME_DESIGN_FURNITURE": "HOME",
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": "RESIDENTIAL",
}

CORE_TOWER_SLOTS = {
    district: {index: f"CORE_TOWER__{DISTRICT_SHORT[district]}_{sequence:02d}" for sequence, index in enumerate(indices, 1)}
    for district, indices in CORE_TOWER_INDICES.items()
}

MASS_OVERRIDES = {
    ("RESIDENTIAL_NEIGHBORHOOD_SERVICES", 0): ("LANDMARK__STUDIO_APARTMENT", (110.0, 70.0, 22.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("RESIDENTIAL_NEIGHBORHOOD_SERVICES", 1): ("LANDMARK__APARTMENT_MANAGEMENT", (20.0, 24.0, 8.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
    ("FINANCIAL_DOWNTOWN", 0): ("LANDMARK__JOB", (86.0, 58.0, 20.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
    ("SHOPPING_RETAIL", 0): ("LANDMARK__CLOTHING", (86.0, 58.0, 20.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("HOME_DESIGN_FURNITURE", 0): ("LANDMARK__FURNITURE", (86.0, 58.0, 20.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("ARENA_ENTERTAINMENT", 2): ("LANDMARK__ARENA", (180.0, 90.0, 30.0), "limestone", "REQUIRED_BETA_LANDMARK"),
    ("ARENA_ENTERTAINMENT", 3): ("LANDMARK__TICKET_BOOTH", (26.0, 26.0, 10.0), "terracotta", "REQUIRED_BETA_LANDMARK"),
}

MASS_LOCATION_OVERRIDES = {
    ("RESIDENTIAL_NEIGHBORHOOD_SERVICES", 0): (-590.0, 190.0),
    ("RESIDENTIAL_NEIGHBORHOOD_SERVICES", 1): (-525.0, 190.0),
    ("ARENA_ENTERTAINMENT", 2): (0.0, 500.0),
    ("ARENA_ENTERTAINMENT", 3): (110.0, 500.0),
}

RESTAURANT_SLOTS = {district: {20, 21, 22, 23} for district in DISTRICTS}
NIGHTLIFE_SLOTS = {"DINING_NIGHTLIFE": set(range(8))}
SHOPPING_CENTER_SLOTS = {"SHOPPING_RETAIL": {4, 5, 7}}
FURNITURE_SHOWROOM_SLOTS = {"HOME_DESIGN_FURNITURE": {1, 2, 3, 4, 5, 7, 8, 10}}
FINANCIAL_OFFICE_SLOTS = {"FINANCIAL_DOWNTOWN": set(range(4, 16))}
EXACT_SCENIC_LAND_USE_COUNTS = {
    "RESTAURANT_SCENIC": 24,
    "NIGHTLIFE_BAR_SCENIC": 8,
    "SHOPPING_CENTER_SCENIC": 3,
    "FURNITURE_SHOWROOM_SCENIC": 8,
    "FINANCIAL_OFFICE_SCENIC": 12,
}

DEFAULT_LAND_USE = {
    "FINANCIAL_DOWNTOWN": "MIXED_DOWNTOWN_SCENIC",
    "ARENA_ENTERTAINMENT": "ENTERTAINMENT_SCENIC",
    "SHOPPING_RETAIL": "RETAIL_SERVICE_SCENIC",
    "DINING_NIGHTLIFE": "DINING_SERVICE_SCENIC",
    "HOME_DESIGN_FURNITURE": "HOME_SERVICE_SCENIC",
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": "RESIDENTIAL_SERVICE_SCENIC",
}

LAND_USE_COLORS = {
    "RESTAURANT_SCENIC": "restaurant",
    "NIGHTLIFE_BAR_SCENIC": "nightlife",
    "SHOPPING_CENTER_SCENIC": "shopping",
    "FURNITURE_SHOWROOM_SCENIC": "furniture",
    "FINANCIAL_OFFICE_SCENIC": "financial",
}


def land_use_for(district, index, is_landmark):
    if is_landmark:
        return "EXISTING_FUNCTIONAL_LANDMARK"
    if index in RESTAURANT_SLOTS[district]:
        return "RESTAURANT_SCENIC"
    if index in NIGHTLIFE_SLOTS.get(district, set()):
        return "NIGHTLIFE_BAR_SCENIC"
    if index in SHOPPING_CENTER_SLOTS.get(district, set()):
        return "SHOPPING_CENTER_SCENIC"
    if index in FURNITURE_SHOWROOM_SLOTS.get(district, set()):
        return "FURNITURE_SHOWROOM_SCENIC"
    if index in FINANCIAL_OFFICE_SLOTS.get(district, set()):
        return "FINANCIAL_OFFICE_SCENIC"
    return DEFAULT_LAND_USE[district]


def street_mass_specs():
    specs = []
    colors = ("limestone", "terracotta", "charcoal")
    for district_index, (district, slots) in enumerate(DISTRICT_SLOTS.items()):
        for index, location in enumerate(slots):
            location = MASS_LOCATION_OVERRIDES.get((district, index), location)
            tower_id = CORE_TOWER_SLOTS[district].get(index)
            if (district, index) in MASS_OVERRIDES:
                name, dimensions, color, role = MASS_OVERRIDES[(district, index)]
            elif tower_id:
                suffix = tower_id.rsplit("_", 1)[-1]
                name = f"CORE_BASE__{DISTRICT_SHORT[district]}_{suffix}"
                dimensions, color, role = (78.0, 58.0, 26.0), "charcoal", "PROPOSED_CORE_TOWER_BASE"
            else:
                name = f"STREET__{DISTRICT_SHORT[district]}_{index + 1:02d}"
                dimensions = ((120.0, 68.0, 16.0 + 4.0 * (index % 3)) if district in {"ARENA_ENTERTAINMENT", "DINING_NIGHTLIFE"} else (104.0, 54.0, 16.0 + 3.0 * (index % 3)))
                color, role = colors[(index + district_index) % len(colors)], "PROPOSED_STREET_MASS"
            land_use = land_use_for(district, index, role == "REQUIRED_BETA_LANDMARK")
            color = LAND_USE_COLORS.get(land_use, color)
            specs.append((name, district, location, dimensions, color, role, tower_id, land_use))
    return specs


STREET_MASSES = street_mass_specs()

BACKGROUND_TOWER_SLOTS = {
    "FINANCIAL_DOWNTOWN": [(1300.0, 230.0), (1320.0, 360.0), (1340.0, 490.0), (1360.0, 620.0)],
    "ARENA_ENTERTAINMENT": [(-480.0, 1010.0), (-160.0, 1030.0), (160.0, 1030.0), (480.0, 1010.0)],
    "SHOPPING_RETAIL": [(1300.0, -230.0), (1320.0, -360.0), (1340.0, -490.0), (1360.0, -620.0)],
    "DINING_NIGHTLIFE": [(-480.0, -1010.0), (-160.0, -1030.0), (160.0, -1030.0), (480.0, -1010.0)],
    "HOME_DESIGN_FURNITURE": [(-1300.0, -230.0), (-1320.0, -360.0), (-1340.0, -490.0), (-1360.0, -620.0)],
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": [(-1300.0, 230.0), (-1320.0, 360.0), (-1340.0, 490.0), (-1360.0, 620.0)],
}

DISTRICT_TOWER_COLORS = {
    "FINANCIAL_DOWNTOWN": "financial",
    "ARENA_ENTERTAINMENT": "cobalt",
    "SHOPPING_RETAIL": "shopping",
    "DINING_NIGHTLIFE": "nightlife",
    "HOME_DESIGN_FURNITURE": "furniture",
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": "limestone",
}


def tower_specs():
    specs = []
    district_order = list(DISTRICTS)
    for name, district, location, _dimensions, _color, _role, tower_id, _land_use in STREET_MASSES:
        if not tower_id:
            continue
        sequence = int(tower_id.rsplit("_", 1)[-1])
        footprint = 40.0 + 2.0 * (sequence % 3)
        height = 165.0 + 15.0 * ((sequence + district_order.index(district)) % 7)
        specs.append((tower_id, "PLAYABLE_CORE", district, name, location, (footprint, footprint), height, DISTRICT_TOWER_COLORS[district]))
    for district, locations in BACKGROUND_TOWER_SLOTS.items():
        for sequence, location in enumerate(locations, 1):
            footprint = 58.0 + 2.0 * (sequence % 3)
            height = 230.0 + 20.0 * ((sequence + district_order.index(district)) % 5)
            specs.append((f"SKYLINE_TOWER__{DISTRICT_SHORT[district]}_{sequence:02d}", "BACKGROUND_SKYLINE", district, None, location, (footprint, footprint), height, DISTRICT_TOWER_COLORS[district]))
    return specs


TOWERS = tower_specs()

def ellipse_points(radius_x, radius_y):
    return [(round(math.cos(math.radians(angle)) * radius_x, 3), round(math.sin(math.radians(angle)) * radius_y, 3)) for angle in range(0, 360, 30)]


RADIAL_SPOKES = {
    f"PREVIEW__SPOKE_{index:02d}": [
        (round(math.cos(math.radians(angle)) * 325.0, 3), round(math.sin(math.radians(angle)) * 235.0, 3)),
        (round(math.cos(math.radians(angle)) * 1150.0, 3), round(math.sin(math.radians(angle)) * 850.0, 3)),
    ]
    for index, angle in enumerate(range(0, 360, 30), 1)
}

RING_ROADS = {
    "PREVIEW__RING_INNER": ellipse_points(400.0, 300.0),
    "PREVIEW__RING_MIDDLE": ellipse_points(700.0, 520.0),
    "PREVIEW__RING_OUTER": ellipse_points(1040.0, 760.0),
}

LOCAL_CROSS_STREETS = {
    **{f"PREVIEW__LOCAL_FINANCIAL_{index}": ("FINANCIAL_DOWNTOWN", [(550.0, y), (1100.0, y)]) for index, y in enumerate((190.0, 245.0, 300.0, 355.0, 410.0, 465.0, 520.0, 575.0), 1)},
    **{f"PREVIEW__LOCAL_ARENA_{index}": ("ARENA_ENTERTAINMENT", [(x, 450.0), (x, 850.0)]) for index, x in enumerate((-420.0, -300.0, -180.0, -60.0, 60.0, 180.0, 300.0, 420.0), 1)},
    **{f"PREVIEW__LOCAL_SHOPPING_{index}": ("SHOPPING_RETAIL", [(550.0, y), (1100.0, y)]) for index, y in enumerate((-575.0, -520.0, -465.0, -410.0, -355.0, -300.0, -245.0, -190.0), 1)},
    **{f"PREVIEW__LOCAL_DINING_{index}": ("DINING_NIGHTLIFE", [(x, -850.0), (x, -450.0)]) for index, x in enumerate((-420.0, -300.0, -180.0, -60.0, 60.0, 180.0, 300.0, 420.0), 1)},
    **{f"PREVIEW__LOCAL_HOME_{index}": ("HOME_DESIGN_FURNITURE", [(-1100.0, y), (-550.0, y)]) for index, y in enumerate((-575.0, -520.0, -465.0, -410.0, -355.0, -300.0, -245.0, -190.0), 1)},
    **{f"PREVIEW__LOCAL_RESIDENTIAL_{index}": ("RESIDENTIAL_NEIGHBORHOOD_SERVICES", [(-1100.0, y), (-550.0, y)]) for index, y in enumerate((190.0, 245.0, 300.0, 355.0, 410.0, 465.0, 520.0, 575.0), 1)},
}

PARK_FEATURES = [
    ("PARK__LAWN_SW", "LAWN_QUADRANT", (-155.0, -110.0), (280.0, 190.0, 0.12), "commons"),
    ("PARK__LAWN_SE", "LAWN_QUADRANT", (155.0, -110.0), (280.0, 190.0, 0.12), "commons"),
    ("PARK__LAWN_NW", "LAWN_QUADRANT", (-155.0, 110.0), (280.0, 190.0, 0.12), "commons"),
    ("PARK__LAWN_NE", "LAWN_QUADRANT", (155.0, 110.0), (280.0, 190.0, 0.12), "commons"),
    ("PARK__PROMENADE_EW", "PROMENADE", (0.0, 0.0), (600.0, 14.0, 0.18), "promenade"),
    ("PARK__PROMENADE_NS", "PROMENADE", (0.0, 0.0), (14.0, 420.0, 0.20), "promenade"),
    ("PARK__GROVE_SW", "TREE_GROVE_PLACEHOLDER", (-240.0, -165.0), (30.0, 30.0, 8.0), "grove"),
    ("PARK__GROVE_SE", "TREE_GROVE_PLACEHOLDER", (240.0, -165.0), (30.0, 30.0, 8.0), "grove"),
    ("PARK__GROVE_NW", "TREE_GROVE_PLACEHOLDER", (-240.0, 165.0), (30.0, 30.0, 8.0), "grove"),
    ("PARK__GROVE_NE", "TREE_GROVE_PLACEHOLDER", (240.0, 165.0), (30.0, 30.0, 8.0), "grove"),
]

LANDMARK_LABELS = {
    "STUDIO_APARTMENT": ("A | STUDIO / APT", (-590.0, 145.0)),
    "APARTMENT_MANAGEMENT": ("A | APT MGMT", (-525.0, 235.0)),
    "JOB": ("A | JOB", (590.0, 145.0)),
    "CLOTHING": ("A | CLOTHING", (590.0, -145.0)),
    "FURNITURE": ("A | FURNITURE", (-590.0, -145.0)),
    "ARENA": ("A | ARENA", (0.0, 500.0)),
    "TICKET_BOOTH": ("A | TICKET", (115.0, 445.0)),
    "PUBLIC_COURT": ("A | PUBLIC COURT", (0.0, -300.0)),
    "COMMONS_PARK": ("A | COMMONS / PARK", (0.0, 0.0)),
}

DISTRICT_LABELS = {
    "FINANCIAL_DOWNTOWN": ("FINANCIAL + DOWNTOWN", (900.0, 790.0)),
    "ARENA_ENTERTAINMENT": ("ARENA + ENTERTAINMENT", (0.0, 870.0)),
    "SHOPPING_RETAIL": ("SHOPPING + RETAIL", (900.0, -790.0)),
    "DINING_NIGHTLIFE": ("DINING + NIGHTLIFE", (0.0, -870.0)),
    "HOME_DESIGN_FURNITURE": ("HOME DESIGN + FURNITURE", (-900.0, -790.0)),
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": ("RESIDENTIAL + NEIGHBORHOOD SERVICES", (-900.0, 790.0)),
}

BUSINESS_CLUSTER_LABELS = {
    "FINANCIAL_DOWNTOWN": ("P | 12 OFFICE + 4 RESTAURANT", (900.0, 720.0)),
    "ARENA_ENTERTAINMENT": ("P | ENTERTAINMENT + 4 RESTAURANT", (0.0, 810.0)),
    "SHOPPING_RETAIL": ("P | 3 SHOPPING CENTERS + 4 RESTAURANT", (900.0, -720.0)),
    "DINING_NIGHTLIFE": ("P | 8 BAR SHELLS + 4 RESTAURANT", (0.0, -810.0)),
    "HOME_DESIGN_FURNITURE": ("P | 8 SHOWROOMS + 4 RESTAURANT", (-900.0, -720.0)),
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": ("P | NEIGHBORHOOD SERVICES + 4 RESTAURANT", (-900.0, 720.0)),
}

VIEWS = [
    ("TopDown_BusinessClusteredMegaCityPreview.png", "top_down", (0.0, 0.0, 2200.0), (0.0, 0.0, 0.0), 2400.0, TOP_RENDER_SIZE),
    ("EyeLevel_FinancialDowntownParkSkyline.png", "eye_level", (-325.0, -235.0, 1.7), (800.0, 370.0, 30.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_ArenaEntertainmentParkSkyline.png", "eye_level", (0.0, -235.0, 1.7), (0.0, 650.0, 30.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_ShoppingRetailParkSkyline.png", "eye_level", (-325.0, 235.0, 1.7), (800.0, -370.0, 30.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_DiningNightlifeParkSkyline.png", "eye_level", (0.0, 235.0, 1.7), (0.0, -650.0, 30.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_HomeDesignFurnitureParkSkyline.png", "eye_level", (325.0, 235.0, 1.7), (-800.0, -370.0, 30.0), None, EYE_RENDER_SIZE),
    ("EyeLevel_ResidentialNeighborhoodServicesParkSkyline.png", "eye_level", (325.0, -235.0, 1.7), (-800.0, 370.0, 30.0), None, EYE_RENDER_SIZE),
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
    obj["capacity_claim"] = False
    obj["travel_time_claim"] = False
    obj["collision_claim"] = False
    obj["production_road"] = False
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
    text["asset_kind"] = "business_cluster_review_label"
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

    add_cube("PREVIEW__PLAYABLE_BOUNDARY_2400X1800M", (0.0, 0.0, -0.25), (*PLAYABLE_SIZE_M, 0.5), "ground", core, "playable_boundary", status="NONCANONICAL_PREVIEW", collision_boundary=False)
    for district_id, ((x, y), (width, depth), color) in DISTRICTS.items():
        add_cube(f"DISTRICT__{district_id}", (x, y, 0.04), (width, depth, 0.08), color, core, "district", district_id=district_id, status="PROPOSED_DISTRICT")
    add_cube("LANDMARK__COMMONS_PARK", (0.0, 0.0, 0.18), (*COMMONS_SIZE_M, 0.18), "commons", core, "commons_park", landmark_id="COMMONS_PARK", status="REQUIRED_BETA_LANDMARK")
    for name, role, (x, y), (width, depth, height), color in PARK_FEATURES:
        add_cube(name, (x, y, 0.2 + height / 2.0), (width, depth, height), color, core, "park_placeholder", role=role, status="NONCANONICAL_REVIEW_PLACEHOLDER", final_landscape=False)
    add_cube("LANDMARK__PUBLIC_COURT", (0.0, -300.0, 0.28), (80.0, 46.0, 0.2), "court", core, "public_court", landmark_id="PUBLIC_COURT", status="REQUIRED_BETA_LANDMARK", inner_ring_access=True)

    base_heights = {}
    for name, district, (x, y), (width, depth, height), color, role, tower_id, land_use in STREET_MASSES:
        obj = add_cube(name, (x, y, height / 2.0 + 0.35), (width, depth, height), color, core, "street_mass", district_id=district, role=role, land_use_tag=land_use, status="NONCANONICAL_PREVIEW", review_scope="SCENIC_ARCHITECTURAL_LAND_USE_SHELL_ONLY", interiors=False, business_service=False, catalog_added=False, gameplay_added=False, alcohol_service=False, inner_ring_access=role == "REQUIRED_BETA_LANDMARK")
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

    for name, placement, district_or_sector, base_id, (x, y), (width, depth), height, color in TOWERS:
        bottom = base_heights[base_id] + 0.35 if base_id else 0.35
        target_collection = core if placement == "PLAYABLE_CORE" else skyline
        add_cube(name, (x, y, bottom + height / 2.0), (width, depth, height), color, target_collection, "skyscraper", placement=placement, district_id=district_or_sector if placement == "PLAYABLE_CORE" else "", skyline_sector=district_or_sector if placement == "BACKGROUND_SKYLINE" else "", base_id=base_id or "", status="PROPOSED_SKYSCRAPER", interiors=False, gameplay_added=False)

    top_guides = []
    label_specs = []
    label_specs.extend((f"LANDMARK_{key}", body, location, 10.0, "teal", "EXISTING_AUTHORIZED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items())
    label_specs.extend((f"DISTRICT_{key}", body, location, 12.0, "teal", "PROPOSED_DISTRICT") for key, (body, location) in DISTRICT_LABELS.items())
    label_specs.extend((f"BUSINESS_{key}", body, location, 8.0, "orange", "PROPOSED_BUSINESS_CLUSTER") for key, (body, location) in BUSINESS_CLUSTER_LABELS.items())
    label_specs.extend([
        ("INFO_TITLE", "SUNDALE BUSINESS-CLUSTERED MEGA-CITY | NONCANONICAL", (0.0, 390.0), 14.0, "teal", "INFO"),
        ("INFO_BUSINESS_LEGEND", "ORANGE RESTAURANT | PURPLE BAR SHELL | BLUE SHOPPING | TEAL SHOWROOM | GOLD OFFICE", (0.0, 340.0), 8.0, "orange", "INFO"),
        ("INFO_SCOPE_LEGEND", "A = EXISTING FUNCTIONAL | P = SCENIC SHELLS | 12 SPOKES + 3 RINGS + 48 LOCAL | NO DISTANCE / CAPACITY", (0.0, -400.0), 8.0, "orange", "INFO"),
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
    scene["phase"] = "Phase 1L.3a business-clustered mega-city replacement preview"
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
    specs.update({f"LANDMARK_{key}": (body, location, 10.0, "teal", "EXISTING_AUTHORIZED_LANDMARK") for key, (body, location) in LANDMARK_LABELS.items()})
    specs.update({f"DISTRICT_{key}": (body, location, 12.0, "teal", "PROPOSED_DISTRICT") for key, (body, location) in DISTRICT_LABELS.items()})
    specs.update({f"BUSINESS_{key}": (body, location, 8.0, "orange", "PROPOSED_BUSINESS_CLUSTER") for key, (body, location) in BUSINESS_CLUSTER_LABELS.items()})
    specs["INFO_TITLE"] = ("SUNDALE BUSINESS-CLUSTERED MEGA-CITY | NONCANONICAL", (0.0, 390.0), 14.0, "teal", "INFO")
    specs["INFO_BUSINESS_LEGEND"] = ("ORANGE RESTAURANT | PURPLE BAR SHELL | BLUE SHOPPING | TEAL SHOWROOM | GOLD OFFICE", (0.0, 340.0), 8.0, "orange", "INFO")
    specs["INFO_SCOPE_LEGEND"] = ("A = EXISTING FUNCTIONAL | P = SCENIC SHELLS | 12 SPOKES + 3 RINGS + 48 LOCAL | NO DISTANCE / CAPACITY", (0.0, -400.0), 8.0, "orange", "INFO")
    return specs


def curve_points(obj):
    return [(round(point.co.x, 3), round(point.co.y, 3)) for point in obj.data.splines[0].points]


def validate_scene(require_manifest):
    errors = []
    objects = bpy.data.objects
    boundary = objects.get("PREVIEW__PLAYABLE_BOUNDARY_2400X1800M")
    if not boundary or any(abs(a - b) > 0.001 for a, b in zip(boundary.dimensions[:2], PLAYABLE_SIZE_M)):
        errors.append("playable preview boundary must be exactly 2400x1800m")

    districts = [obj for obj in objects if obj.get("asset_kind") == "district"]
    if {obj.get("district_id") for obj in districts} != set(DISTRICTS) or len(districts) != 6:
        errors.append("exactly six named preview districts are required")
    for district_id, ((x, y), (width, depth), _color) in DISTRICTS.items():
        obj = objects.get(f"DISTRICT__{district_id}")
        if not obj or any(abs(a - b) > 0.001 for a, b in zip(obj.location[:2], (x, y))) or any(abs(a - b) > 0.001 for a, b in zip(obj.dimensions[:2], (width, depth))):
            errors.append(f"{district_id} dimensions/location differ")

    park = objects.get("LANDMARK__COMMONS_PARK")
    if not park or any(abs(a - b) > 0.001 for a, b in zip(park.dimensions[:2], COMMONS_SIZE_M)) or any(abs(value) > 0.001 for value in park.location[:2]):
        errors.append("central Commons/Park must be exactly 600x420m at the city hub")
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
    if len(masses) != 144 or district_counts != Counter({name: 24 for name in DISTRICTS}):
        errors.append(f"street masses must total 144 and 24 per district: {len(masses)}, {district_counts}")
    if any(obj.get("review_scope") != "SCENIC_ARCHITECTURAL_LAND_USE_SHELL_ONLY" or obj.get("interiors") is not False for obj in masses):
        errors.append("street masses must remain exterior scenic architectural/land-use shells only")
    if any(obj.get("business_service") is not False or obj.get("catalog_added") is not False or obj.get("gameplay_added") is not False or obj.get("alcohol_service") is not False for obj in masses):
        errors.append("street masses must add no business service, catalog, gameplay, or alcohol behavior")
    expected_masses = {spec[0]: spec for spec in STREET_MASSES}
    if {obj.name for obj in masses} != set(expected_masses):
        errors.append("street mass identities differ from the deterministic contract")
    for name, district, (x, y), (width, depth, height), _color, role, tower_id, land_use in STREET_MASSES:
        obj = objects.get(name)
        if not obj or obj.get("district_id") != district or obj.get("role") != role or obj.get("tower_id", "") != (tower_id or "") or obj.get("land_use_tag") != land_use:
            errors.append(f"{name} district/role/tower/land-use contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(obj.location, (x, y, height / 2.0 + 0.35))) or any(abs(a - b) > 0.001 for a, b in zip(obj.dimensions, (width, depth, height))):
            errors.append(f"{name} dimensions/location differ")
    land_use_counts = Counter(obj.get("land_use_tag") for obj in masses)
    for land_use, expected in EXACT_SCENIC_LAND_USE_COUNTS.items():
        if land_use_counts[land_use] != expected:
            errors.append(f"{land_use} must count exactly {expected}, found {land_use_counts[land_use]}")
    restaurant_district_counts = Counter(obj.get("district_id") for obj in masses if obj.get("land_use_tag") == "RESTAURANT_SCENIC")
    if restaurant_district_counts != Counter({name: 4 for name in DISTRICTS}):
        errors.append(f"restaurant scenic shells must count four per district: {restaurant_district_counts}")
    concentrated_land_uses = {
        "NIGHTLIFE_BAR_SCENIC": "DINING_NIGHTLIFE",
        "SHOPPING_CENTER_SCENIC": "SHOPPING_RETAIL",
        "FURNITURE_SHOWROOM_SCENIC": "HOME_DESIGN_FURNITURE",
        "FINANCIAL_OFFICE_SCENIC": "FINANCIAL_DOWNTOWN",
    }
    for land_use, district in concentrated_land_uses.items():
        if {obj.get("district_id") for obj in masses if obj.get("land_use_tag") == land_use} != {district}:
            errors.append(f"{land_use} must remain concentrated in {district}")
    bases = {obj.name: obj for obj in masses if obj.get("role") == "PROPOSED_CORE_TOWER_BASE"}
    base_district_counts = Counter(obj.get("district_id") for obj in bases.values())
    expected_core_counts = Counter({district: len(indices) for district, indices in CORE_TOWER_INDICES.items()})
    if len(bases) != 36 or base_district_counts != expected_core_counts:
        errors.append(f"exactly 36 playable-core bases with the approved district split are required: {len(bases)}, {base_district_counts}")

    towers = [obj for obj in objects if obj.get("asset_kind") == "skyscraper"]
    placement_counts = Counter(obj.get("placement") for obj in towers)
    core_district_counts = Counter(obj.get("district_id") for obj in towers if obj.get("placement") == "PLAYABLE_CORE")
    background_sector_counts = Counter(obj.get("skyline_sector") for obj in towers if obj.get("placement") == "BACKGROUND_SKYLINE")
    if len(towers) != 60 or placement_counts != Counter({"PLAYABLE_CORE": 36, "BACKGROUND_SKYLINE": 24}):
        errors.append(f"tower split must be 36 playable/24 background: {len(towers)}, {placement_counts}")
    if core_district_counts != expected_core_counts or background_sector_counts != Counter({district: 4 for district in DISTRICTS}):
        errors.append(f"tower district/sector split differs: {core_district_counts}, {background_sector_counts}")
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
    for name, placement, district_or_sector, base_id, (x, y), (width, depth), height, _color in TOWERS:
        tower = objects.get(name)
        bottom = bases[base_id].dimensions.z + 0.35 if base_id else 0.35
        if not tower or tower.get("placement") != placement or tower.get("base_id") != (base_id or ""):
            errors.append(f"{name} placement/base contract differs")
        elif tower.get("district_id") != (district_or_sector if placement == "PLAYABLE_CORE" else "") or tower.get("skyline_sector") != (district_or_sector if placement == "BACKGROUND_SKYLINE" else ""):
            errors.append(f"{name} district/skyline-sector contract differs")
        elif any(abs(a - b) > 0.001 for a, b in zip(tower.location, (x, y, bottom + height / 2.0))) or any(abs(a - b) > 0.001 for a, b in zip(tower.dimensions, (width, depth, height))):
            errors.append(f"{name} dimensions/location differ")

    required_mass_names = {
        "LANDMARK__STUDIO_APARTMENT", "LANDMARK__APARTMENT_MANAGEMENT", "LANDMARK__JOB",
        "LANDMARK__CLOTHING", "LANDMARK__FURNITURE", "LANDMARK__ARENA", "LANDMARK__TICKET_BOOTH",
    }
    if not required_mass_names.issubset({obj.name for obj in masses}) or not objects.get("LANDMARK__PUBLIC_COURT") or not objects.get("LANDMARK__COMMONS_PARK"):
        errors.append("all nine required beta landmarks must be present")
    functional_location_names = (required_mass_names - {"LANDMARK__APARTMENT_MANAGEMENT"}) | {"LANDMARK__PUBLIC_COURT"}
    if len(functional_location_names) != 7 or len(required_mass_names) != 7 or len(LANDMARK_LABELS) != 9:
        errors.append("required landmarks must remain seven functional building/location identities plus attached kiosk plus Commons/Park")
    studio = objects.get("LANDMARK__STUDIO_APARTMENT")
    kiosk = objects.get("LANDMARK__APARTMENT_MANAGEMENT")
    if not studio or not kiosk or abs((studio.location.x + studio.dimensions.x / 2.0) - (kiosk.location.x - kiosk.dimensions.x / 2.0)) > 0.001:
        errors.append("Apartment Management kiosk must stay attached to the Studio/apartment frontage")
    inner_ring_landmarks = [objects.get(name) for name in required_mass_names] + [objects.get("LANDMARK__PUBLIC_COURT")]
    for landmark in inner_ring_landmarks:
        if not landmark:
            continue
        radius = math.hypot(landmark.location.x, landmark.location.y)
        near_ring = 280.0 <= radius <= 700.0
        if not near_ring or landmark.get("inner_ring_access") is not True:
            errors.append(f"{landmark.name} must remain on/near the inner destination ring")

    spokes = {obj.name: obj for obj in objects if obj.get("asset_kind") == "radial_spoke"}
    rings = {obj.name: obj for obj in objects if obj.get("asset_kind") == "ring_road"}
    local_streets = {obj.name: obj for obj in objects if obj.get("asset_kind") == "local_cross_street"}
    circulation = list(spokes.values()) + list(rings.values()) + list(local_streets.values())
    if set(spokes) != set(RADIAL_SPOKES) or set(rings) != set(RING_ROADS) or set(local_streets) != set(LOCAL_CROSS_STREETS):
        errors.append(f"street topology must be exact 12 spokes/3 rings/48 locals: {len(spokes)}/{len(rings)}/{len(local_streets)}")
    if any(obj.get("distance_canonical") is not False or "distance_m" in obj or obj.get("capacity_claim") is not False or obj.get("travel_time_claim") is not False or obj.get("collision_claim") is not False or obj.get("production_road") is not False for obj in circulation):
        errors.append("all preview streets must remain proposed guides with no distance/capacity/travel/collision/production claim")
    for name, points in RADIAL_SPOKES.items():
        if name in spokes and (curve_points(spokes[name]) != points or spokes[name].get("branches_from_park") is not True or spokes[name].get("cyclic") is not False):
            errors.append(f"{name} radial topology differs")
    for name, points in RING_ROADS.items():
        if name in rings and (curve_points(rings[name]) != points or rings[name].get("cyclic") is not True):
            errors.append(f"{name} ring topology differs")
    local_district_counts = Counter(obj.get("district_id") for obj in local_streets.values())
    if local_district_counts != Counter({name: 8 for name in DISTRICTS}):
        errors.append(f"local cross streets must remain eight per district: {local_district_counts}")
    for name, (district, points) in LOCAL_CROSS_STREETS.items():
        if name in local_streets and (curve_points(local_streets[name]) != points or local_streets[name].get("district_id") != district or local_streets[name].get("cyclic") is not False):
            errors.append(f"{name} local topology differs")
    if [obj for obj in objects if obj.get("asset_kind") == "canonical_route"]:
        errors.append("the business-cluster preview must not recanonize or replace the production route")

    specs = expected_label_specs()
    labels = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "business_cluster_review_label"}
    plates = {obj.get("label_id"): obj for obj in objects if obj.get("asset_kind") == "review_label_plate"}
    if set(labels) != set(specs) or set(plates) != set(specs):
        errors.append(f"review labels/plates must cover exactly 9 landmarks + 6 districts + 6 business clusters + 3 info: labels={len(labels)}, plates={len(plates)}")
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
        errors.append(f"expected exactly seven named review renders, found {[path.name for path in render_files]}")
    if BLEND_PATH.with_suffix(".blend1").exists():
        errors.append("Blender backup output is forbidden")
    if sum(view[1] == "top_down" for view in VIEWS) != 1 or sum(view[1] == "eye_level" for view in VIEWS) != 6:
        errors.append("review requires exactly one top-down and six eye-level views")
    if any(abs(view[2][2] - 1.7) > 0.001 for view in VIEWS if view[1] == "eye_level"):
        errors.append("all district cameras must remain at 1.7m")
    if VIEWS[0][5] != TOP_RENDER_SIZE or any(view[5] != EYE_RENDER_SIZE for view in VIEWS[1:]):
        errors.append("review resolutions differ from the approved high-resolution top/eye contract")
    camera_obstacles = masses + towers + [obj for obj in (park, objects.get("LANDMARK__PUBLIC_COURT")) if obj]
    for filename, view_type, location, target, _ortho, _resolution in VIEWS:
        if view_type != "eye_level":
            continue
        if location[0] * target[0] + location[1] * target[1] >= 0.0:
            errors.append(f"{filename} camera/target must frame across the central park toward its district")
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
        errors.append("vehicles are forbidden in the business-clustered mega-city preview")
    if require_manifest and not MANIFEST_PATH.exists():
        errors.append("manifest.json is missing")
    if errors:
        raise RuntimeError("\n".join(errors))
    print("ODDSWELL_SUNDALE_BUSINESS_VALIDATION|result=PASS|playable=2400x1800m|commons=600x420m|districts=6|street_masses=144|street_per_district=24|towers=60|core_towers=36|background_towers=24|required_landmarks=9|functional_locations=7|attached_kiosk=1|park=1|restaurants=24|nightlife_bar_shells=8|shopping_centers=3|furniture_showrooms=8|financial_offices=12|spokes=12|rings=3|local_streets=48|canonical_route_distance=false|labels=24|plates=24|views=1_top+6_eye|eye_height_m=1.7|camera_clearance_m=20|engine=eevee|cycles=false|external_refs=0|vehicles=0|interiors=0|gameplay_added=false")
    return district_counts, placement_counts, core_district_counts, background_sector_counts, land_use_counts


def write_manifest(district_counts, placement_counts, core_district_counts, background_sector_counts, land_use_counts):
    renders = []
    for filename, view_type, location, target, _ortho, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}", "view_type": view_type, "camera_location_m": location,
            "target_m": target, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3a business-clustered mega-city replacement preview",
        "status": "noncanonical_owner_business_clustered_mega_city_preview",
        "supersedes": "Phase 1L.3a 1400x1000m/72-mass/24-tower radial mega-city preview",
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
            "core_tower_base_count": 36,
            "skyscraper_count": len(TOWERS),
            "tower_placement_counts": dict(placement_counts),
            "core_towers_per_district": dict(core_district_counts),
            "background_towers_per_sector": dict(background_sector_counts),
            "required_landmarks": list(LANDMARK_LABELS),
            "required_landmark_structure": {"functional_building_or_location_identities": 7, "attached_apartment_management_kiosk": 1, "commons_park": 1},
            "commons_park_m": COMMONS_SIZE_M,
            "park_placeholder_roles": dict(Counter(spec[1] for spec in PARK_FEATURES)),
            "business_land_use_counts": {key: land_use_counts[key] for key in EXACT_SCENIC_LAND_USE_COUNTS},
            "restaurant_frontages_per_district": dict(Counter(obj[1] for obj in STREET_MASSES if obj[7] == "RESTAURANT_SCENIC")),
            "business_land_use_scope": "SCENIC_ARCHITECTURAL_LAND_USE_SHELLS_ONLY",
            "business_services_added": False,
            "alcohol_service_added": False,
            "purchases_or_catalog_added": False,
            "gameplay_fields": [],
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
            "eye_views_frame_park_circulation_and_district_skyline": True,
            "street_guides_visible_in_eye_views": True,
            "street_level_only_initially": True,
            "vehicles": False,
            "interiors": False,
        },
        "label_contract": {
            "top_down_only": True,
            "required_landmark_count": len(LANDMARK_LABELS),
            "district_count": len(DISTRICT_LABELS),
            "business_cluster_count": len(BUSINESS_CLUSTER_LABELS),
            "info_count": 3,
            "total": len(expected_label_specs()),
            "plate_count": len(expected_label_specs()),
            "minimum_contrast_ratio": LABEL_CONTRAST_MIN,
            "labels": {key: spec[0] for key, spec in expected_label_specs().items()},
        },
        "renders": renders,
        "external_references": [],
        "limitations": [
            "not production Unreal geometry or a production-route replacement",
            "business labels are scenic architectural/land-use shells only, not services, alcohol, purchases, catalogs, economy, or gameplay",
            "not approved final placement, capacity, travel time, interiors, facades, collision, materials, lighting, age-rating, accessibility, usability, performance, or readiness",
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
        district_counts, placement_counts, core_district_counts, background_sector_counts, land_use_counts = validate_scene(require_manifest=False)
        write_manifest(district_counts, placement_counts, core_district_counts, background_sector_counts, land_use_counts)
    else:
        district_counts, placement_counts, core_district_counts, background_sector_counts, land_use_counts = validate_scene(require_manifest=True)
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        contract = manifest.get("preview_contract", {})
        if any((
            contract.get("street_masses_per_district") != dict(district_counts),
            contract.get("tower_placement_counts") != dict(placement_counts),
            contract.get("core_towers_per_district") != dict(core_district_counts),
            contract.get("background_towers_per_sector") != dict(background_sector_counts),
            contract.get("business_land_use_counts") != {key: land_use_counts[key] for key in EXACT_SCENIC_LAND_USE_COUNTS},
        )):
            raise RuntimeError("manifest preview counts differ from the Blend")
        if manifest.get("label_contract", {}).get("labels") != {key: spec[0] for key, spec in expected_label_specs().items()}:
            raise RuntimeError("manifest label contract differs from the Blend")
        for render in manifest["renders"]:
            path = ROOT / render["file"]
            if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
                raise RuntimeError(f"render hash differs: {path.name}")
        print("ODDSWELL_SUNDALE_BUSINESS_FOCUSED|result=PASS|manifest=true|render_hashes=7|districts=6|street_masses=144|towers=60|core=36|background=24|landmarks=9|restaurants=24|nightlife_bar_shells=8|shopping_centers=3|furniture_showrooms=8|financial_offices=12|spokes=12|rings=3|locals=48|labels=24|plates=24|camera_clearance_m=20|canonical_route_distance=false|gameplay_added=false|manual_input=false")


if __name__ == "__main__":
    main()
