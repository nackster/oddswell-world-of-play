"""Build and validate the noncanonical Phase 1L.3d Sundale public-court review board."""

import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundalePublicCourtReviewBoard.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

SAMPLE_IDS = (
    "CourtSurface",
    "CourtLineSet",
    "CourtEdgeNorth",
    "CourtEdgeSouth",
    "CourtEdgeEast",
    "CourtEdgeWest",
    "CourtCenterTreatment",
    "CourtHoopNorth",
    "CourtHoopSouth",
    "CourtFenceModule",
    "CourtBenchClusterNorth",
    "CourtBenchClusterSouth",
)

# Mirrors the current authored Sundale court: 28.7 x 15.3 m centered at (-79, 150) m.
COURT_SIZE_M = (28.7, 15.3)
PRODUCTION_CENTER_M = (-79.0, 150.0)

PALETTE = {
    "warm_limestone": ("#D8C8A9", (0.847059, 0.784314, 0.662745, 1.0)),
    "muted_terracotta": ("#A65F47", (0.650980, 0.372549, 0.278431, 1.0)),
    "sand_concrete": ("#B9A783", (0.725490, 0.654902, 0.513725, 1.0)),
    "sage_green": ("#6D7F62", (0.427451, 0.498039, 0.384314, 1.0)),
    "restrained_cobalt": ("#315F79", (0.192157, 0.372549, 0.474510, 1.0)),
    "burnt_orange": ("#C46D3B", (0.768627, 0.427451, 0.231373, 1.0)),
    "charcoal_gray": ("#4D5051", (0.301961, 0.313725, 0.317647, 1.0)),
}

REVIEW_BOUNDS_M = {"x": (-22.01, 22.01), "y": (-15.01, 15.01), "z": (-0.21, 8.01)}
TRIANGLE_CEILING = 6000
VIEWS = (
    ("Unified_TopDown_PublicCourt.png", "UNIFIED_TOP", "TOP", (0.0, 0.0, 48.0), (0.0, 0.0, 0.0), 48.0, (1920, 1080)),
    ("Cardinal_North_PublicCourt.png", "CARDINAL", "NORTH", (11.0, -32.0, 1.7), (0.0, 0.0, 0.85), 24.0, (1600, 900)),
    ("Cardinal_East_PublicCourt.png", "CARDINAL", "EAST", (-34.0, -10.0, 1.7), (0.0, 0.0, 0.95), 28.0, (1600, 900)),
    ("Cardinal_South_PublicCourt.png", "CARDINAL", "SOUTH", (-11.0, 32.0, 1.7), (0.0, 0.0, 0.85), 24.0, (1600, 900)),
    ("Cardinal_West_PublicCourt.png", "CARDINAL", "WEST", (34.0, 10.0, 1.7), (0.0, 0.0, 0.95), 28.0, (1600, 900)),
)

MATERIALS = {}
SITE = None
SAMPLES = None


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
    shader.inputs["Roughness"].default_value = 0.82
    material["accepted_palette_hex"] = PALETTE[name][0]
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, sample_id="", instance_id="", role="REVIEW_SITE"):
    obj["review_sample_id"] = sample_id
    obj["review_instance_id"] = instance_id
    obj["asset_role"] = role
    obj["noncanonical"] = True
    obj["external_reference"] = False
    obj["interior"] = False
    obj["gameplay"] = False
    obj["collision"] = False
    obj["navigation"] = False
    return obj


def add_root(sample_id):
    root = bpy.data.objects.new(f"SAMPLE_ROOT__{sample_id}", None)
    tag(root, sample_id, "", "NONCANONICAL_REVIEW_SAMPLE")
    SAMPLES.objects.link(root)
    return root


def add_cube(name, location, dimensions, material_name, parent, role, sample_id="", collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, sample_id, role)
    obj.parent = parent
    move_to_collection(obj, collection or SAMPLES)
    return obj


def add_cylinder(name, location, radius, depth, material_name, parent, role, sample_id, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, sample_id, role)
    obj.parent = parent
    move_to_collection(obj, SAMPLES)
    return obj


def add_torus(name, location, major_radius, minor_radius, material_name, parent, role, sample_id):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=24,
        minor_segments=6,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, sample_id, role)
    obj.parent = parent
    move_to_collection(obj, SAMPLES)
    return obj


def build_surface():
    root = add_root("CourtSurface")
    surface = add_cube(
        "CourtSurface__SURFACE_28_7x15_3M",
        (0.0, 0.0, 0.10),
        (COURT_SIZE_M[0], COURT_SIZE_M[1], 0.20),
        "muted_terracotta",
        root,
        "AUTHORITATIVE_CURRENT_COURT_SURFACE",
        "CourtSurface",
    )
    surface["production_center_x_m"] = PRODUCTION_CENTER_M[0]
    surface["production_center_y_m"] = PRODUCTION_CENTER_M[1]
    surface["production_width_m"] = COURT_SIZE_M[0]
    surface["production_depth_m"] = COURT_SIZE_M[1]


def build_lines():
    sample_id = "CourtLineSet"
    root = add_root(sample_id)
    half_x, half_y = COURT_SIZE_M[0] / 2.0, COURT_SIZE_M[1] / 2.0
    width, top = 0.11, 0.215
    lines = (
        ("NORTH", (0.0, half_y - width / 2.0, top), (COURT_SIZE_M[0], width, 0.03)),
        ("SOUTH", (0.0, -half_y + width / 2.0, top), (COURT_SIZE_M[0], width, 0.03)),
        ("EAST", (half_x - width / 2.0, 0.0, top), (width, COURT_SIZE_M[1], 0.03)),
        ("WEST", (-half_x + width / 2.0, 0.0, top), (width, COURT_SIZE_M[1], 0.03)),
        ("CENTER", (0.0, 0.0, top), (width, COURT_SIZE_M[1], 0.03)),
        ("KEY_WEST", (-10.55, 0.0, top), (0.09, 4.9, 0.03)),
        ("KEY_EAST", (10.55, 0.0, top), (0.09, 4.9, 0.03)),
    )
    for name, location, dimensions in lines:
        add_cube(f"{sample_id}__{name}", location, dimensions, "warm_limestone", root, "PAINTED_LINE", sample_id)


def build_edges():
    half_x, half_y = COURT_SIZE_M[0] / 2.0, COURT_SIZE_M[1] / 2.0
    specs = (
        ("CourtEdgeNorth", (0.0, half_y + 0.18, 0.16), (COURT_SIZE_M[0] + 0.6, 0.25, 0.32)),
        ("CourtEdgeSouth", (0.0, -half_y - 0.18, 0.16), (COURT_SIZE_M[0] + 0.6, 0.25, 0.32)),
        ("CourtEdgeEast", (half_x + 0.18, 0.0, 0.16), (0.25, COURT_SIZE_M[1], 0.32)),
        ("CourtEdgeWest", (-half_x - 0.18, 0.0, 0.16), (0.25, COURT_SIZE_M[1], 0.32)),
    )
    for sample_id, location, dimensions in specs:
        root = add_root(sample_id)
        edge = add_cube(f"{sample_id}__MODULE", location, dimensions, "sand_concrete", root, "COURT_EDGE_MODULE", sample_id)
        edge["route_obstruction_claim"] = False


def build_center():
    sample_id = "CourtCenterTreatment"
    root = add_root(sample_id)
    add_cylinder(f"{sample_id}__DISC", (0.0, 0.0, 0.235), 1.75, 0.04, "burnt_orange", root, "CENTER_DISC", sample_id, 32)
    add_cylinder(f"{sample_id}__CORE", (0.0, 0.0, 0.26), 0.62, 0.05, "restrained_cobalt", root, "CENTER_CORE", sample_id, 24)


def build_hoop(sample_id, physical_end, x_sign):
    root = add_root(sample_id)
    root["orientation_role"] = "LONG_AXIS_END"
    root["physical_long_axis_end"] = physical_end
    root["geographic_side_claim"] = False
    pole_x = x_sign * 15.55
    board_x = x_sign * 13.95
    rim_x = x_sign * 13.32
    add_cylinder(f"{sample_id}__POLE", (pole_x, 0.0, 1.65), 0.17, 3.3, "charcoal_gray", root, "HOOP_POLE", sample_id, 12)
    add_cube(f"{sample_id}__ARM", ((pole_x + board_x) / 2.0, 0.0, 3.12), (abs(pole_x - board_x), 0.18, 0.18), "charcoal_gray", root, "HOOP_SUPPORT", sample_id)
    add_cube(f"{sample_id}__BACKBOARD", (board_x, 0.0, 3.05), (0.12, 1.82, 1.06), "warm_limestone", root, "HOOP_BACKBOARD", sample_id)
    add_torus(f"{sample_id}__RIM", (rim_x, 0.0, 2.90), 0.43, 0.045, "burnt_orange", root, "HOOP_RIM", sample_id)
    for index, y in enumerate((-0.30, -0.10, 0.10, 0.30), 1):
        add_cylinder(f"{sample_id}__NET_{index:02d}", (rim_x, y, 2.62), 0.018, 0.48, "warm_limestone", root, "ABSTRACT_NET_TREATMENT", sample_id, 8)


def build_fence():
    sample_id = "CourtFenceModule"
    root = add_root(sample_id)
    for end_index, x in enumerate((-18.0, 18.0), 1):
        for post_index, y in enumerate((-4.6, 0.0, 4.6), 1):
            add_cube(f"{sample_id}__POST_{end_index}_{post_index}", (x, y, 1.65), (0.12, 0.12, 3.3), "charcoal_gray", root, "FENCE_POST", sample_id)
        for rail_index, z in enumerate((0.35, 1.65, 2.95), 1):
            add_cube(f"{sample_id}__RAIL_{end_index}_{rail_index}", (x, 0.0, z), (0.10, 9.2, 0.08), "charcoal_gray", root, "OPEN_FENCE_RAIL", sample_id)
    root["route_obstruction_claim"] = False
    root["open_sightline"] = True


def build_bench_cluster(sample_id, y):
    root = add_root(sample_id)
    add_cube(f"{sample_id}__SEAT", (0.0, y, 0.55), (4.8, 0.82, 0.18), "warm_limestone", root, "BENCH_SEAT", sample_id)
    back_y = y + (-0.36 if y > 0 else 0.36)
    add_cube(f"{sample_id}__BACK", (0.0, back_y, 1.08), (4.8, 0.14, 0.96), "sage_green", root, "BENCH_BACK", sample_id)
    for index, x in enumerate((-1.75, 1.75), 1):
        add_cube(f"{sample_id}__LEG_{index}", (x, y, 0.28), (0.18, 0.55, 0.55), "charcoal_gray", root, "BENCH_LEG", sample_id)
    root["drawn_from_commons_prop_language"] = True
    root["player_rest_gameplay"] = False


def point_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def build_scene():
    global SITE, SAMPLES
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)

    support = bpy.data.collections.get("Collection")
    support.name = "CAMERAS_AND_LIGHTS"
    SITE = bpy.data.collections.new("PUBLIC_COURT_REVIEW_SITE")
    SAMPLES = bpy.data.collections.new("NONCANONICAL_REVIEW_SAMPLES")
    bpy.context.scene.collection.children.link(SITE)
    bpy.context.scene.collection.children.link(SAMPLES)

    MATERIALS.clear()
    for name, (_hex, color) in PALETTE.items():
        MATERIALS[name] = make_material(name, color)

    site_root = bpy.data.objects.new("PUBLIC_COURT_REVIEW_SITE_ROOT", None)
    tag(site_root, role="REVIEW_SITE")
    SITE.objects.link(site_root)
    add_cube("REVIEW_GROUND", (0.0, 0.0, -0.10), (44.0, 30.0, 0.20), "sage_green", site_root, "NONPRODUCTION_REVIEW_GROUND", collection=SITE)

    build_surface()
    build_lines()
    build_edges()
    build_center()
    build_hoop("CourtHoopNorth", "WEST", -1.0)
    build_hoop("CourtHoopSouth", "EAST", 1.0)
    build_fence()
    build_bench_cluster("CourtBenchClusterNorth", 10.2)
    build_bench_cluster("CourtBenchClusterSouth", -10.2)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = (0.045, 0.060, 0.070)
    scene["phase"] = "Phase 1L.3d"
    scene["status"] = "NONCANONICAL_PUBLIC_COURT_OWNER_REVIEW"
    scene["current_court_size_m"] = "28.7x15.3"
    scene["production_center_m"] = "-79,150"
    scene["review_local_center_m"] = "0,0"
    scene["external_refs_count"] = 0
    scene["textures_count"] = 0
    scene["interiors_count"] = 0
    scene["gameplay_changes_count"] = 0
    scene["production_catalog_changed"] = False
    scene["production_map_changed"] = False
    scene["production_route_changed"] = False
    scene["production_collision_changed"] = False
    scene["production_navigation_changed"] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, -8.0, 28.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 1700.0
    key.data.shape = "DISK"
    key.data.size = 18.0
    point_camera(key, key.location, (0.0, 0.0, 0.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 20.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.55, -0.35, -0.45)
    sun.data.energy = 2.0

    for filename, role, direction, location, target, framing, _resolution in VIEWS:
        data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        if role == "UNIFIED_TOP":
            data.type = "ORTHO"
            data.ortho_scale = framing
        else:
            data.type = "PERSP"
            data.lens = framing
            data.clip_start = 0.1
            data.clip_end = 250.0
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", data)
        support.objects.link(camera)
        point_camera(camera, location, target)
        camera["view_role"] = role
        camera["cardinal_direction"] = direction
        camera["render_file"] = filename
        camera["pedestrian_eye_height_m"] = 1.7 if role == "CARDINAL" else 0.0
        camera["complete_asset_framing_required"] = True
        camera["original_resolution_required"] = True

    validate_scene(require_outputs=False)
    render_all()
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    write_provenance()
    write_manifest()
    validate_scene(require_outputs=True)


def mesh_triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def sample_triangle_counts():
    counts = defaultdict(int)
    for obj in bpy.data.objects:
        sample_id = obj.get("review_sample_id")
        if obj.type == "MESH" and sample_id:
            counts[sample_id] += mesh_triangles(obj)
    return dict(counts)


def actual_instance_counts():
    instances = defaultdict(set)
    for obj in bpy.data.objects:
        sample_id = obj.get("review_sample_id")
        instance_id = obj.get("review_instance_id")
        if obj.type == "MESH" and sample_id and instance_id:
            instances[sample_id].add(instance_id)
    return {sample_id: len(instances[sample_id]) for sample_id in SAMPLE_IDS}


def point_to_bounds_distance(point, obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector(tuple(min(corner[index] for corner in corners) for index in range(3)))
    maxs = Vector(tuple(max(corner[index] for corner in corners) for index in range(3)))
    delta = Vector(tuple(max(mins[index] - point[index], 0.0, point[index] - maxs[index]) for index in range(3)))
    return delta.length


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = {obj.name: obj for obj in objects if obj.type == "EMPTY" and obj.name.startswith("SAMPLE_ROOT__")}
    expected_roots = {f"SAMPLE_ROOT__{sample_id}" for sample_id in SAMPLE_IDS}
    if set(roots) != expected_roots:
        errors.append(f"exactly twelve noncanonical sample roots are required: {sorted(roots)}")
    if any(roots[name].get("review_sample_id") not in SAMPLE_IDS or roots[name].get("asset_role") != "NONCANONICAL_REVIEW_SAMPLE" for name in roots):
        errors.append("review roots must retain exact IDs and noncanonical roles")

    counts = actual_instance_counts()
    if counts != {sample_id: 1 for sample_id in SAMPLE_IDS}:
        errors.append(f"every exact review ID must have one bounded review instance: {counts}")
    triangles = sample_triangle_counts()
    if set(triangles) != set(SAMPLE_IDS) or any(value <= 0 or value > TRIANGLE_CEILING for value in triangles.values()):
        errors.append(f"review triangle counts are invalid: {triangles}")

    surface = next((obj for obj in objects if obj.get("asset_role") == "AUTHORITATIVE_CURRENT_COURT_SURFACE"), None)
    if not surface or tuple(round(value, 4) for value in surface.dimensions[:2]) != COURT_SIZE_M:
        errors.append("current Sundale court surface must remain exactly 28.7x15.3 m")
    elif (
        surface.get("production_center_x_m") != PRODUCTION_CENTER_M[0]
        or surface.get("production_center_y_m") != PRODUCTION_CENTER_M[1]
        or surface.location.x != 0.0
        or surface.location.y != 0.0
    ):
        errors.append("production and review-local court centers differ")

    for sample_id, physical_end in (("CourtHoopNorth", "WEST"), ("CourtHoopSouth", "EAST")):
        root = roots.get(f"SAMPLE_ROOT__{sample_id}")
        if not root or root.get("orientation_role") != "LONG_AXIS_END" or root.get("physical_long_axis_end") != physical_end or root.get("geographic_side_claim") is not False:
            errors.append(f"{sample_id} must preserve its ID without a geographic-side claim")

    allowed_materials = set(PALETTE)
    for obj in [candidate for candidate in objects if candidate.type == "MESH"]:
        for material in obj.data.materials:
            if material.name not in allowed_materials or material.get("accepted_palette_hex") != PALETTE[material.name][0]:
                errors.append(f"{obj.name} uses a nonaccepted material")
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not all(REVIEW_BOUNDS_M[axis][0] <= world[index] <= REVIEW_BOUNDS_M[axis][1] for index, axis in enumerate(("x", "y", "z"))):
                errors.append(f"{obj.name} exceeds the bounded review board")
                break
        if obj.get("review_sample_id") and any(
            obj.get(field) is not False for field in ("external_reference", "interior", "gameplay", "collision", "navigation")
        ):
            errors.append(f"{obj.name} violates native exterior review metadata")

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    if {camera.name for camera in cameras} != {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}:
        errors.append("camera IDs must match one top plus four compass views")
    if Counter(camera.get("view_role") for camera in cameras) != Counter({"UNIFIED_TOP": 1, "CARDINAL": 4}):
        errors.append("views must be one unified top and four cardinal frames")
    if {camera.get("cardinal_direction") for camera in cameras} != {"TOP", "NORTH", "EAST", "SOUTH", "WEST"}:
        errors.append("top and N/E/S/W view directions are required")
    cardinal_cameras = [camera for camera in cameras if camera.get("view_role") == "CARDINAL"]
    expected_lenses = {f"CAMERA__{Path(view[0]).stem}": view[5] for view in VIEWS if view[1] == "CARDINAL"}
    if any(
        camera.data.type != "PERSP"
        or camera.data.lens != expected_lenses[camera.name]
        or abs(camera.location.z - 1.7) > 0.0001
        or camera.get("pedestrian_eye_height_m") != 1.7
        or camera.get("complete_asset_framing_required") is not True
        or camera.get("original_resolution_required") is not True
        for camera in cardinal_cameras
    ):
        errors.append("all cardinal cameras must retain deterministic complete 1.7 m framing")
    sample_meshes = [obj for obj in objects if obj.type == "MESH" and obj.get("review_sample_id")]
    for camera in cardinal_cameras:
        clearance = min(point_to_bounds_distance(camera.location, obj) for obj in sample_meshes)
        if clearance < 2.0:
            errors.append(f"{camera.name} is not clear of every review AABB: {clearance:.3f} m")
        camera["minimum_sample_aabb_clearance_m"] = round(clearance, 4)

    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if scene.get("current_court_size_m") != "28.7x15.3" or scene.get("production_center_m") != "-79,150":
        errors.append("current court authority metadata differs")
    if any((scene.get("external_refs_count"), scene.get("textures_count"), scene.get("interiors_count"), scene.get("gameplay_changes_count"))):
        errors.append("external references, textures, interiors, and gameplay changes must remain zero")
    if any(
        scene.get(field)
        for field in (
            "production_catalog_changed",
            "production_map_changed",
            "production_route_changed",
            "production_collision_changed",
            "production_navigation_changed",
        )
    ):
        errors.append("production catalog/map/route/collision/navigation must remain unchanged")
    if len(bpy.data.materials) != len(PALETTE) or {material.name for material in bpy.data.materials} != set(PALETTE):
        errors.append("the Blend must use exactly the accepted seven-color planning palette")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, textures, and source images are forbidden")
    if any(obj.type in {"ARMATURE", "VOLUME", "META"} for obj in objects):
        errors.append("characters, interiors, and volume geometry are forbidden")

    if require_outputs:
        expected = {view[0]: view[6] for view in VIEWS}
        actual = {path.name for path in RENDER_DIR.glob("*.png")} if RENDER_DIR.exists() else set()
        if actual != set(expected):
            errors.append(f"expected exactly five review PNGs, found {sorted(actual)}")
        for filename, resolution in expected.items():
            path = RENDER_DIR / filename
            if path.exists() and png_dimensions(path) != resolution:
                errors.append(f"{filename} dimensions differ")
        if not BLEND_PATH.exists() or not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("Blend, manifest, and provenance are required")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("Blender backup output is forbidden")
        if MANIFEST_PATH.exists():
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            expected_hoop_note = {
                "CourtHoopNorth": {"orientation_role": "LONG_AXIS_END", "physical_long_axis_end": "WEST", "geographic_side_claim": False},
                "CourtHoopSouth": {"orientation_role": "LONG_AXIS_END", "physical_long_axis_end": "EAST", "geographic_side_claim": False},
            }
            if manifest.get("sample_contract", {}).get("hoop_identity_note") != expected_hoop_note:
                errors.append("manifest must distinguish exact hoop IDs from physical long-axis orientation")
            for artifact in manifest["artifacts"]:
                path = ROOT / artifact["file"]
                if not path.exists() or path.stat().st_size != artifact["bytes"] or sha256(path) != artifact["sha256"]:
                    errors.append(f"artifact identity differs: {artifact['file']}")
    if errors:
        raise RuntimeError("\n".join(errors))

    print(
        "ODDSWELL_SUNDALE_PUBLIC_COURT_VALIDATION|result=PASS|samples=12|instances=12|"
        "views=1_top+4_cardinal_1.7m|court_m=28.7x15.3|production_center_m=-79,150|"
        "hoop_ids_geographic_claim=false|engine=eevee|native_geometry=true|external_refs=0|textures=0|"
        "interiors=0|gameplay=0|production_catalog_changed=false|production_map_changed=false|"
        "production_route_changed=false|production_collision_changed=false|production_navigation_changed=false"
    )
    return triangles, counts


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    expected = {view[0] for view in VIEWS}
    for existing in RENDER_DIR.glob("*.png"):
        if existing.name not in expected:
            existing.unlink()
    scene = bpy.context.scene
    for filename, _role, _direction, _location, _target, _framing, resolution in VIEWS:
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)


def write_provenance():
    PROVENANCE_PATH.write_text(
        "# Sundale Public Court Review Board Provenance\n\n"
        "- Phase: `Phase 1L.3d`\n"
        "- Status: noncanonical owner review only\n"
        "- Builder: `build_sundale_public_court.py`\n"
        "- Geometry: deterministic Blender-native low-poly primitives\n"
        "- Authority: current authored `28.7x15.3 m` Sundale court centered at production `(-79,150) m`; source is review-local at `(0,0)`\n"
        "- Palette: the seven accepted planning colors in `Design/Sundale Art Direction and Core Loop.md`\n"
        "- Renderer: Blender Eevee\n"
        "- External libraries, models, images, textures, fonts, brands, catalogs, frameworks, and paid inputs: none\n"
        "- Interiors, gameplay, client, runtime, Unreal map, route, collision, navigation, package, test, and config changes: none\n\n"
        "The twelve exact IDs are noncanonical review identities, not production catalog IDs. `CourtHoopNorth` and `CourtHoopSouth` retain their approved IDs while the assemblies occupy the west/east long-axis ends; `orientation_role=LONG_AXIS_END` makes no geographic-side claim. Production promotion, collision, navigation, accessibility, placement, performance, final art, and a second playable basketball mode remain owner-gated.\n",
        encoding="utf-8",
    )


def artifact_record(path):
    return {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_manifest():
    triangles, counts = validate_scene(require_outputs=False)
    artifacts = [BLEND_PATH, Path(__file__).resolve(), PROVENANCE_PATH] + [RENDER_DIR / view[0] for view in VIEWS]
    manifest = {
        "phase": "Phase 1L.3d",
        "status": "noncanonical_owner_review_board",
        "manual_input": False,
        "renderer": "BLENDER_EEVEE_NEXT",
        "authority": {
            "production_center_m": list(PRODUCTION_CENTER_M),
            "review_local_center_m": [0.0, 0.0],
            "court_size_m": list(COURT_SIZE_M),
            "surface_bounds_local_m": {"x": [-14.35, 14.35], "y": [-7.65, 7.65]},
        },
        "sample_contract": {
            "sample_count": len(SAMPLE_IDS),
            "sample_ids": list(SAMPLE_IDS),
            "instance_counts": counts,
            "triangle_counts": triangles,
            "triangle_ceiling_per_sample": TRIANGLE_CEILING,
            "native_geometry_only": True,
            "production_catalog_ids": False,
            "hoop_identity_note": {
                "CourtHoopNorth": {"orientation_role": "LONG_AXIS_END", "physical_long_axis_end": "WEST", "geographic_side_claim": False},
                "CourtHoopSouth": {"orientation_role": "LONG_AXIS_END", "physical_long_axis_end": "EAST", "geographic_side_claim": False},
            },
        },
        "boundaries": {
            "external_references": 0,
            "textures": 0,
            "interiors": 0,
            "gameplay_changes": 0,
            "production_catalog_changed": False,
            "production_map_changed": False,
            "production_route_changed": False,
            "production_collision_changed": False,
            "production_navigation_changed": False,
            "package_changed": False,
        },
        "views": [
            {"file": f"renders/{view[0]}", "role": view[1], "direction": view[2], "width": view[6][0], "height": view[6][1], "eye_height_m": 1.7 if view[1] == "CARDINAL" else None}
            for view in VIEWS
        ],
        "artifacts": [artifact_record(path) for path in artifacts],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest_only(label):
    validate_scene(require_outputs=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(
        f"ODDSWELL_SUNDALE_PUBLIC_COURT_{label}|result=PASS|manifest=true|"
        f"artifact_hashes={len(manifest['artifacts'])}|render_hashes={len(manifest['views'])}|manual_input=false"
    )


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    mode = args[0] if args else "--build"
    if mode == "--build":
        build_scene()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        print(f"ODDSWELL_SUNDALE_PUBLIC_COURT_BUILD|result=PASS|artifacts={len(manifest['artifacts']) + 1}|manual_input=false")
    elif mode == "--validate-saved":
        validate_manifest_only("REOPEN")
    elif mode == "--focused":
        validate_manifest_only("FOCUSED")
    else:
        raise RuntimeError(f"unsupported mode: {mode}")


if __name__ == "__main__":
    main()
