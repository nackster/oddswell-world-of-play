"""Build and validate the noncanonical Phase 1L.3b architectural-language board."""

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleArchitecturalLanguage.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

PALETTE = {
    "warm_limestone": ("#D8C8A9", (0.847059, 0.784314, 0.662745, 1.0)),
    "muted_terracotta": ("#A65F47", (0.650980, 0.372549, 0.278431, 1.0)),
    "sand_concrete": ("#B9A783", (0.725490, 0.654902, 0.513725, 1.0)),
    "sage_green": ("#6D7F62", (0.427451, 0.498039, 0.384314, 1.0)),
    "restrained_cobalt": ("#315F79", (0.192157, 0.372549, 0.474510, 1.0)),
    "burnt_orange": ("#C46D3B", (0.768627, 0.427451, 0.231373, 1.0)),
    "charcoal_gray": ("#4D5051", (0.301961, 0.313725, 0.317647, 1.0)),
}

DISTRICTS = (
    "FINANCIAL_DOWNTOWN",
    "ARENA_ENTERTAINMENT",
    "SHOPPING_RETAIL",
    "DINING_NIGHTLIFE",
    "HOME_DESIGN_FURNITURE",
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES",
)
DISTRICT_SHORT = {
    "FINANCIAL_DOWNTOWN": "FinancialDowntown",
    "ARENA_ENTERTAINMENT": "ArenaEntertainment",
    "SHOPPING_RETAIL": "ShoppingRetail",
    "DINING_NIGHTLIFE": "DiningNightlife",
    "HOME_DESIGN_FURNITURE": "HomeDesignFurniture",
    "RESIDENTIAL_NEIGHBORHOOD_SERVICES": "ResidentialNeighborhoodServices",
}
CELL_CENTERS = {
    district: ((index % 3 - 1) * 12.0, (0.5 - index // 3) * 12.0)
    for index, district in enumerate(DISTRICTS)
}

FACADE_IDS = {district: f"FACADE_SAMPLE__{district}" for district in DISTRICTS}
TOWER_IDS = {district: f"TOWER_SILHOUETTE__{district}" for district in DISTRICTS}
FACADE_TRIANGLE_CEILING = 240
TOWER_TRIANGLE_CEILING = 96
BOARD_BOUNDS_M = {"x": (-19.01, 19.01), "y": (-13.01, 13.01), "z": (-0.51, 18.0)}

VIEWS = (
    ("Unified_SundaleArchitecturalLanguage.png", "UNIFIED_BOARD", None, (0.0, -45.0, 38.0), (0.0, 0.0, 5.5), (1920, 1080)),
    *tuple(
        (
            f"Closeup_{DISTRICT_SHORT[district]}.png",
            "DISTRICT_CLOSEUP",
            district,
            (CELL_CENTERS[district][0], CELL_CENTERS[district][1] - 28.0, 7.5),
            (CELL_CENTERS[district][0], CELL_CENTERS[district][1], 7.5),
            (1280, 720),
        )
        for district in DISTRICTS
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


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.82
    material["accepted_palette_hex"] = PALETTE[name][0]
    return material


def tag(obj, sample_id, district, role):
    obj["sample_id"] = sample_id
    obj["district_id"] = district
    obj["asset_role"] = role
    obj["low_poly"] = True
    obj["interior"] = False
    obj["gameplay"] = False
    obj["external_reference"] = False
    return obj


def add_root(name, district, role):
    root = bpy.data.objects.new(name, None)
    tag(root, name, district, role)
    GEOMETRY.objects.link(root)
    return root


def add_cube(name, location, dimensions, material_name, parent, role):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, parent.name, parent["district_id"], role)
    obj.parent = parent
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    GEOMETRY.objects.link(obj)
    return obj


def add_frustum(name, location, bottom, top, height, material_name, parent, role):
    bx, by = bottom[0] / 2.0, bottom[1] / 2.0
    tx, ty = top[0] / 2.0, top[1] / 2.0
    vertices = [
        (-bx, -by, -height / 2.0), (bx, -by, -height / 2.0),
        (bx, by, -height / 2.0), (-bx, by, -height / 2.0),
        (-tx, -ty, height / 2.0), (tx, -ty, height / 2.0),
        (tx, ty, height / 2.0), (-tx, ty, height / 2.0),
    ]
    faces = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7))
    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(MATERIALS[material_name])
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    tag(obj, parent.name, parent["district_id"], role)
    obj.parent = parent
    GEOMETRY.objects.link(obj)
    return obj


def facade_common(district, wall, accent, bay_count=3, awning=True):
    cx, cy = CELL_CENTERS[district]
    x, y = cx - 2.8, cy
    root = add_root(FACADE_IDS[district], district, "FACADE_SAMPLE")
    add_cube(f"{root.name}__MASS", (x, y, 2.5), (5.2, 3.0, 5.0), wall, root, "FACADE_MASS")
    bay_width = 3.9 / bay_count
    for index in range(bay_count):
        bay_x = x - 1.95 + bay_width * (index + 0.5)
        add_cube(f"{root.name}__BAY_{index + 1:02d}", (bay_x, y - 1.515, 1.65), (bay_width * 0.72, 0.10, 2.1), "charcoal_gray", root, "OPAQUE_FACADE_PANEL")
    if awning:
        add_cube(f"{root.name}__AWNING", (x, y - 1.83, 2.85), (4.4, 0.8, 0.28), accent, root, "AWNING")
    add_cube(f"{root.name}__PARAPET", (x, y - 1.53, 4.55), (4.7, 0.16, 0.42), accent, root, "FACADE_ACCENT")
    return root, (x, y)


def build_facades():
    root, (x, y) = facade_common("FINANCIAL_DOWNTOWN", "warm_limestone", "restrained_cobalt", 4, False)
    for offset in (-1.7, -0.55, 0.55, 1.7):
        add_cube(f"{root.name}__PILASTER_{offset:+.2f}", (x + offset, y - 1.61, 3.0), (0.18, 0.20, 4.3), "restrained_cobalt", root, "VERTICAL_PILASTER")

    root, (x, y) = facade_common("ARENA_ENTERTAINMENT", "sand_concrete", "burnt_orange", 3)
    add_cube(f"{root.name}__PORTAL", (x, y - 1.68, 3.15), (2.1, 0.34, 3.45), "muted_terracotta", root, "BROAD_PORTAL")
    add_cube(f"{root.name}__CANOPY", (x, y - 2.05, 3.3), (4.9, 1.25, 0.24), "burnt_orange", root, "ARENA_CANOPY")

    root, (x, y) = facade_common("SHOPPING_RETAIL", "warm_limestone", "restrained_cobalt", 4)
    for offset in (-1.5, -0.5, 0.5, 1.5):
        add_cube(f"{root.name}__FIN_{offset:+.1f}", (x + offset, y - 1.93, 3.05), (0.12, 0.85, 0.95), "restrained_cobalt", root, "RETAIL_AWNING_FIN")

    root, (x, y) = facade_common("DINING_NIGHTLIFE", "muted_terracotta", "burnt_orange", 3)
    add_cube(f"{root.name}__DEEP_AWNING", (x, y - 2.2, 2.8), (4.5, 1.55, 0.24), "burnt_orange", root, "DEEP_SOCIAL_AWNING")
    add_cube(f"{root.name}__PLINTH", (x, y - 1.6, 0.45), (4.8, 0.22, 0.9), "charcoal_gray", root, "FACADE_PLINTH")

    root, (x, y) = facade_common("HOME_DESIGN_FURNITURE", "sand_concrete", "sage_green", 2)
    add_cube(f"{root.name}__SHOWCASE_FRAME", (x, y - 1.62, 1.75), (4.5, 0.22, 2.75), "sage_green", root, "SHOWCASE_FRAME")
    add_cube(f"{root.name}__SHOWCASE_INSET", (x, y - 1.75, 1.75), (3.9, 0.10, 2.25), "charcoal_gray", root, "OPAQUE_FACADE_PANEL")

    root, (x, y) = facade_common("RESIDENTIAL_NEIGHBORHOOD_SERVICES", "warm_limestone", "muted_terracotta", 3, False)
    for level in (2.0, 3.35):
        add_cube(f"{root.name}__BALCONY_{level:.2f}", (x, y - 1.82, level), (4.2, 0.72, 0.16), "muted_terracotta", root, "SHALLOW_BALCONY")
    add_cube(f"{root.name}__STOOP", (x, y - 2.05, 0.35), (1.8, 1.1, 0.35), "sand_concrete", root, "STOOP")


def build_towers():
    for district in DISTRICTS:
        cx, cy = CELL_CENTERS[district]
        x, y = cx + 3.4, cy + 0.35
        root = add_root(TOWER_IDS[district], district, "TOWER_SILHOUETTE")
        if district == "FINANCIAL_DOWNTOWN":
            add_frustum(f"{root.name}__SHAFT", (x, y, 7.0), (3.2, 3.0), (2.25, 2.0), 14.0, "restrained_cobalt", root, "TOWER_MASS")
            add_cube(f"{root.name}__CROWN", (x, y, 14.5), (1.5, 1.3, 1.0), "warm_limestone", root, "TOWER_CROWN")
        elif district == "ARENA_ENTERTAINMENT":
            add_frustum(f"{root.name}__SHAFT", (x, y, 6.0), (4.2, 3.0), (3.6, 2.6), 12.0, "sand_concrete", root, "TOWER_MASS")
            add_cube(f"{root.name}__CROWN", (x, y, 12.6), (4.4, 3.1, 1.2), "burnt_orange", root, "TOWER_CROWN")
        elif district == "SHOPPING_RETAIL":
            add_cube(f"{root.name}__BASE", (x, y, 4.0), (4.0, 3.0, 8.0), "warm_limestone", root, "TOWER_MASS")
            add_cube(f"{root.name}__UPPER", (x + 0.45, y, 10.0), (2.7, 2.4, 6.0), "restrained_cobalt", root, "TOWER_SETBACK")
        elif district == "DINING_NIGHTLIFE":
            add_frustum(f"{root.name}__SHAFT", (x, y, 6.5), (3.1, 3.1), (2.2, 2.4), 13.0, "muted_terracotta", root, "TOWER_MASS")
            add_cube(f"{root.name}__TERRACE", (x - 0.55, y - 0.15, 10.2), (2.6, 2.9, 0.35), "burnt_orange", root, "TOWER_TERRACE")
        elif district == "HOME_DESIGN_FURNITURE":
            add_cube(f"{root.name}__BASE", (x, y, 3.5), (4.3, 3.2, 7.0), "sand_concrete", root, "TOWER_MASS")
            add_frustum(f"{root.name}__UPPER", (x - 0.35, y, 9.0), (3.1, 2.7), (2.6, 2.2), 4.0, "sage_green", root, "TOWER_SETBACK")
        else:
            add_cube(f"{root.name}__BASE", (x, y, 4.5), (4.0, 3.0, 9.0), "warm_limestone", root, "TOWER_MASS")
            for z in (3.0, 5.0, 7.0, 9.0):
                add_cube(f"{root.name}__BALCONY_{z:.1f}", (x, y - 1.7, z), (3.6, 0.6, 0.18), "muted_terracotta", root, "TOWER_BALCONY")


def point_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_scene():
    global GEOMETRY
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.collections):
        if block.name != "Collection":
            bpy.data.collections.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    default = bpy.data.collections.get("Collection")
    default.name = "BOARD_AND_LIGHTS"
    GEOMETRY = bpy.data.collections.new("ARCHITECTURAL_SAMPLES")
    bpy.context.scene.collection.children.link(GEOMETRY)

    MATERIALS.clear()
    for name, (_hex, color) in PALETTE.items():
        MATERIALS[name] = make_material(name, color)

    board = add_cube("REVIEW_BOARD", (0.0, 0.0, -0.25), (38.0, 26.0, 0.5), "sand_concrete", add_root("BOARD_ROOT", "", "BOARD_ROOT"), "REVIEW_BOARD")
    board["sample_id"] = ""
    for x in (-6.0, 6.0):
        divider = add_cube(f"BOARD_DIVIDER_X_{x:+.0f}", (x, 0.0, 0.03), (0.08, 25.0, 0.06), "charcoal_gray", board.parent, "BOARD_DIVIDER")
        divider["sample_id"] = ""
    divider = add_cube("BOARD_DIVIDER_Y", (0.0, 0.0, 0.03), (37.0, 0.08, 0.06), "charcoal_gray", board.parent, "BOARD_DIVIDER")
    divider["sample_id"] = ""

    build_facades()
    build_towers()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = PALETTE["sand_concrete"][1][:3]
    scene["phase"] = "Phase 1L.3b"
    scene["status"] = "NONCANONICAL_ARCHITECTURAL_LANGUAGE_REVIEW"
    scene["external_refs_count"] = 0
    scene["interiors_count"] = 0
    scene["gameplay_changes_count"] = 0
    scene["production_city_counts_changed"] = False
    scene["production_route_changed"] = False
    scene["business_behavior_changed"] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, -5.0, 25.0))
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

    for filename, view_role, district, location, target, _resolution in VIEWS:
        camera_data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", camera_data)
        default.objects.link(camera)
        point_camera(camera, location, target)
        camera.data.lens = 14.0 if view_role == "DISTRICT_CLOSEUP" else 48.0
        camera["view_role"] = view_role
        camera["district_id"] = district or ""
        camera["render_file"] = filename

    validate_scene(require_outputs=False)
    render_all()
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def sample_triangle_counts():
    counts = defaultdict(int)
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.get("sample_id"):
            counts[obj.get("sample_id")] += mesh_triangles(obj)
    return dict(counts)


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = {obj.name: obj for obj in objects if obj.type == "EMPTY"}
    facade_roots = {name: roots.get(name) for name in FACADE_IDS.values()}
    tower_roots = {name: roots.get(name) for name in TOWER_IDS.values()}
    if None in facade_roots.values() or len(facade_roots) != 6:
        errors.append("exactly six facade sample roots with deterministic IDs are required")
    if None in tower_roots.values() or len(tower_roots) != 6:
        errors.append("exactly six tower silhouette roots with deterministic IDs are required")
    for district in DISTRICTS:
        facade = roots.get(FACADE_IDS[district])
        tower = roots.get(TOWER_IDS[district])
        if not facade or facade.get("asset_role") != "FACADE_SAMPLE" or facade.get("district_id") != district:
            errors.append(f"{FACADE_IDS[district]} role/district differs")
        if not tower or tower.get("asset_role") != "TOWER_SILHOUETTE" or tower.get("district_id") != district:
            errors.append(f"{TOWER_IDS[district]} role/district differs")

    expected_sample_ids = set(FACADE_IDS.values()) | set(TOWER_IDS.values())
    sample_meshes = [obj for obj in objects if obj.type == "MESH" and obj.get("sample_id")]
    if {obj.get("sample_id") for obj in sample_meshes} != expected_sample_ids:
        errors.append("every exact sample ID must own native mesh geometry")
    if any(obj.get("district_id") not in DISTRICTS or obj.get("interior") is not False or obj.get("gameplay") is not False or obj.get("external_reference") is not False for obj in sample_meshes):
        errors.append("sample metadata must remain district-owned, exterior-only, non-gameplay, and native")

    triangles = sample_triangle_counts()
    for sample_id in FACADE_IDS.values():
        if triangles.get(sample_id, 0) <= 0 or triangles[sample_id] > FACADE_TRIANGLE_CEILING:
            errors.append(f"{sample_id} triangle count exceeds {FACADE_TRIANGLE_CEILING}: {triangles.get(sample_id, 0)}")
    for sample_id in TOWER_IDS.values():
        if triangles.get(sample_id, 0) <= 0 or triangles[sample_id] > TOWER_TRIANGLE_CEILING:
            errors.append(f"{sample_id} triangle count exceeds {TOWER_TRIANGLE_CEILING}: {triangles.get(sample_id, 0)}")

    allowed_materials = set(PALETTE)
    for obj in [obj for obj in objects if obj.type == "MESH"]:
        for material in obj.data.materials:
            if material.name not in allowed_materials or material.get("accepted_palette_hex") != PALETTE[material.name][0]:
                errors.append(f"{obj.name} uses a nonaccepted material")
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not (BOARD_BOUNDS_M["x"][0] <= world.x <= BOARD_BOUNDS_M["x"][1] and BOARD_BOUNDS_M["y"][0] <= world.y <= BOARD_BOUNDS_M["y"][1] and BOARD_BOUNDS_M["z"][0] <= world.z <= BOARD_BOUNDS_M["z"][1]):
                errors.append(f"{obj.name} exceeds review-board bounds")
                break

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    expected_camera_names = {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}
    if {camera.name for camera in cameras} != expected_camera_names:
        errors.append("camera IDs must match the exact unified plus six-closeup contract")
    if Counter(camera.get("view_role") for camera in cameras) != Counter({"UNIFIED_BOARD": 1, "DISTRICT_CLOSEUP": 6}):
        errors.append("camera roles must be one unified board and six district closeups")
    if {camera.get("district_id") for camera in cameras if camera.get("view_role") == "DISTRICT_CLOSEUP"} != set(DISTRICTS):
        errors.append("each accepted district must have one closeup camera")
    if bpy.context.scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if len(bpy.data.materials) != len(PALETTE) or {material.name for material in bpy.data.materials} != set(PALETTE):
        errors.append("the Blend must use exactly the accepted seven-color planning palette")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external Blender libraries, textures, and images are forbidden")
    if bpy.context.scene.get("external_refs_count") != 0 or bpy.context.scene.get("interiors_count") != 0 or bpy.context.scene.get("gameplay_changes_count") != 0:
        errors.append("external references, interiors, and gameplay changes must remain zero")
    if any((bpy.context.scene.get("production_city_counts_changed"), bpy.context.scene.get("production_route_changed"), bpy.context.scene.get("business_behavior_changed"))):
        errors.append("production city counts, route, and business behavior must remain unchanged")
    if any(obj.type in {"ARMATURE", "VOLUME", "META"} for obj in objects):
        errors.append("unsupported character/interior/volume geometry is forbidden")

    if require_outputs:
        render_files = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if render_files != sorted(view[0] for view in VIEWS):
            errors.append(f"expected exactly seven review PNGs, found {render_files}")
        if not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists() or not BLEND_PATH.exists():
            errors.append("Blend, manifest, and provenance are required")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("Blender backup output is forbidden")
    if errors:
        raise RuntimeError("\n".join(errors))
    print(
        "ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_VALIDATION|result=PASS|districts=6|"
        "facades=6|towers=6|views=1_unified+6_closeup|engine=eevee|palette=7_accepted|"
        f"facade_tri_ceiling={FACADE_TRIANGLE_CEILING}|tower_tri_ceiling={TOWER_TRIANGLE_CEILING}|"
        "external_refs=0|interiors=0|gameplay=0|production_counts_changed=false|route_changed=false|business_behavior_changed=false"
    )
    return triangles


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old_render in RENDER_DIR.glob("*.png"):
        old_render.unlink()
    scene = bpy.context.scene
    sample_objects = [obj for obj in bpy.data.objects if obj.get("sample_id")]
    for filename, view_role, district, _location, _target, (width, height) in VIEWS:
        for obj in sample_objects:
            obj.hide_render = bool(district and obj.get("district_id") != district)
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)
    for obj in sample_objects:
        obj.hide_render = False
    scene.camera = bpy.data.objects["CAMERA__Unified_SundaleArchitecturalLanguage"]


def write_manifest(triangles):
    renders = []
    for filename, view_role, district, location, target, (width, height) in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}",
            "role": view_role,
            "district_id": district,
            "camera_location_m": location,
            "camera_target_m": target,
            "width": width,
            "height": height,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3b Sundale architectural-language samples",
        "status": "noncanonical_owner_review_board",
        "engine": "BLENDER_EEVEE_NEXT",
        "deterministic_builder": Path(__file__).name,
        "district_ids": list(DISTRICTS),
        "sample_contract": {
            "facade_ids": list(FACADE_IDS.values()),
            "tower_ids": list(TOWER_IDS.values()),
            "facade_count": 6,
            "tower_count": 6,
            "one_pair_per_district": True,
            "triangle_counts": triangles,
            "facade_triangle_ceiling": FACADE_TRIANGLE_CEILING,
            "tower_triangle_ceiling": TOWER_TRIANGLE_CEILING,
            "bounds_m": BOARD_BOUNDS_M,
            "native_geometry_only": True,
            "opaque_exterior_samples_only": True,
        },
        "palette": {name: value[0] for name, value in PALETTE.items()},
        "renders": renders,
        "external_references": [],
        "interiors": [],
        "brands": [],
        "catalogs": [],
        "frameworks": [],
        "gameplay_changes": [],
        "production_authority_preserved": {
            "accepted_city_counts_changed": False,
            "canonical_route_changed": False,
            "business_behavior_changed": False,
            "unreal_map_changed": False,
            "client_or_runtime_changed": False,
            "test_or_config_changed": False,
        },
        "limitations": [
            "review-only low-poly exterior language samples, not production assets or approved city expansion",
            "no placement, interior, collision, performance, accessibility, branding, catalog, business, or gameplay claim",
            "promotion or expansion remains owner-gated",
        ],
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(triangles):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("district_ids") != list(DISTRICTS):
        raise RuntimeError("manifest district IDs differ")
    contract = manifest.get("sample_contract", {})
    if contract.get("facade_ids") != list(FACADE_IDS.values()) or contract.get("tower_ids") != list(TOWER_IDS.values()):
        raise RuntimeError("manifest sample IDs differ")
    if contract.get("triangle_counts") != triangles:
        raise RuntimeError("manifest triangle counts differ from the reopened Blend")
    if manifest.get("external_references") or manifest.get("interiors") or manifest.get("gameplay_changes"):
        raise RuntimeError("manifest must retain zero external references, interiors, and gameplay changes")
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
        print(f"ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_{marker}|result=PASS|manifest=true|render_hashes=7|manual_input=false")
        return
    build_scene()
    triangles = validate_scene(require_outputs=False)
    write_manifest(triangles)
    validate_scene(require_outputs=True)
    validate_manifest(triangles)
    print("ODDSWELL_SUNDALE_ARCHITECTURAL_LANGUAGE_BUILD|result=PASS|artifacts=10|manual_input=false")


if __name__ == "__main__":
    main()
