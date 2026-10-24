"""Build and validate the noncanonical Phase 1L.3c Central Commons review kit."""

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleCentralCommonsLandscapeKit.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

SAMPLE_IDS = (
    "CommonsPaverBrick",
    "CommonsShadeTreeRound",
    "CommonsShadeTreeWide",
    "CommonsShadeTreeColumnar",
    "CommonsLowPlanter",
    "CommonsBench",
    "CommonsPedestrianLamp",
    "CommonsLitterBin",
    "CommonsBollardEdge",
)

INSTANCE_COUNTS = {
    "CommonsPaverBrick": 2,
    "CommonsShadeTreeRound": 4,
    "CommonsShadeTreeWide": 4,
    "CommonsShadeTreeColumnar": 4,
    "CommonsLowPlanter": 8,
    "CommonsBench": 8,
    "CommonsPedestrianLamp": 12,
    "CommonsLitterBin": 4,
    "CommonsBollardEdge": 8,
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

PARK_BOUNDS_M = {"x": (-300.01, 300.01), "y": (-210.01, 210.01), "z": (-1.01, 30.0)}
PATH_WIDTH_M = 48.0
STEP_FREE_ELEVATION_M = 0.30
TREE_LIMIT = 12
PLANTER_LIMIT = 10
BENCH_LIMIT = 8
LAMP_LIMIT = 12
BIN_LIMIT = 6
TRIANGLE_CEILING = 8000

VIEWS = (
    ("Unified_TopDown_CentralCommons.png", "UNIFIED_TOP", "TOP", (0.0, 0.0, 650.0), (0.0, 0.0, 0.0), 800.0, (1920, 1080)),
    ("Cardinal_North_CentralCommons.png", "CARDINAL", "NORTH", (0.0, 50.0, 1.7), (-90.0, 145.0, 3.2), 35.0, (1600, 900)),
    ("Cardinal_East_CentralCommons.png", "CARDINAL", "EAST", (50.0, 0.0, 1.7), (145.0, 90.0, 3.2), 28.0, (1600, 900)),
    ("Cardinal_South_CentralCommons.png", "CARDINAL", "SOUTH", (0.0, -50.0, 1.7), (90.0, -145.0, 3.2), 35.0, (1600, 900)),
    ("Cardinal_West_CentralCommons.png", "CARDINAL", "WEST", (-50.0, 0.0, 1.7), (-145.0, -90.0, 3.2), 28.0, (1600, 900)),
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


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.86
    material["accepted_palette_hex"] = PALETTE[name][0]
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, sample_id="", instance_id="", role="SITE_LAYOUT"):
    obj["review_sample_id"] = sample_id
    obj["review_instance_id"] = instance_id
    obj["asset_role"] = role
    obj["noncanonical"] = True
    obj["external_reference"] = False
    obj["interior"] = False
    obj["gameplay"] = False
    return obj


def add_root(name, collection, sample_id="", role="SITE_LAYOUT"):
    obj = bpy.data.objects.new(name, None)
    tag(obj, sample_id, "", role)
    collection.objects.link(obj)
    return obj


def add_cube(name, location, dimensions, material_name, parent, role, sample_id="", instance_id="", collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, instance_id, role)
    obj.parent = parent
    move_to_collection(obj, collection or SAMPLES)
    return obj


def add_cylinder(name, location, radius, depth, material_name, parent, role, sample_id, instance_id, vertices=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, instance_id, role)
    obj.parent = parent
    move_to_collection(obj, SAMPLES)
    return obj


def add_uv_sphere(name, location, scale, material_name, parent, role, sample_id, instance_id, segments=12, rings=6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, instance_id, role)
    obj.parent = parent
    move_to_collection(obj, SAMPLES)
    return obj


def sample_root(sample_id):
    return add_root(f"SAMPLE_ROOT__{sample_id}", SAMPLES, sample_id, "NONCANONICAL_REVIEW_SAMPLE")


def build_site():
    site_root = add_root("CENTRAL_COMMONS_SITE", SITE, role="CENTRAL_COMMONS_SITE")
    add_cube("PARK_BASE_600x420M", (0.0, 0.0, -0.30), (600.0, 420.0, 0.60), "sand_concrete", site_root, "PARK_BASE", collection=SITE)

    lawns = (
        ("LAWN_NORTH_WEST", (-162.0, 117.0, 0.15)),
        ("LAWN_NORTH_EAST", (162.0, 117.0, 0.15)),
        ("LAWN_SOUTH_WEST", (-162.0, -117.0, 0.15)),
        ("LAWN_SOUTH_EAST", (162.0, -117.0, 0.15)),
    )
    for name, location in lawns:
        lawn = add_cube(name, location, (252.0, 166.0, 0.30), "sage_green", site_root, "LAWN_QUADRANT", collection=SITE)
        lawn["step_free_top_elevation_m"] = STEP_FREE_ELEVATION_M

    paver = sample_root("CommonsPaverBrick")
    paths = (
        ("PATH_EAST_WEST", (0.0, 0.0, 0.15), (600.0, PATH_WIDTH_M, 0.30)),
        ("PATH_NORTH_SOUTH", (0.0, 0.0, 0.15), (PATH_WIDTH_M, 420.0, 0.30)),
    )
    for index, (name, location, dimensions) in enumerate(paths, 1):
        path = add_cube(name, location, dimensions, "warm_limestone", paver, "BROAD_STEP_FREE_CROSS_PATH", "CommonsPaverBrick", f"CommonsPaverBrick_{index:02d}")
        path["path_width_m"] = PATH_WIDTH_M
        path["step_free"] = True
        path["top_elevation_m"] = STEP_FREE_ELEVATION_M

    center = add_cylinder("CENTRAL_PATH_INTERSECTION_MEDALLION", (0.0, 0.0, 0.31), 33.0, 0.02, "muted_terracotta", site_root, "PATH_INTERSECTION_ACCENT", "", "", vertices=32)
    tag(center, "", "", "PATH_INTERSECTION_ACCENT")
    center["blocking"] = False


def add_tree_profile(sample_id, positions, canopy_scale, crown_count):
    root = sample_root(sample_id)
    for index, (x, y) in enumerate(positions, 1):
        instance = f"{sample_id}_{index:02d}"
        add_cylinder(f"{instance}__TRUNK", (x, y, 4.5), 1.15, 9.0, "charcoal_gray", root, "TREE_TRUNK", sample_id, instance, 10)
        for crown in range(crown_count):
            offset_x = (crown - (crown_count - 1) / 2.0) * canopy_scale[0] * 0.52
            offset_z = abs(crown - (crown_count - 1) / 2.0) * -0.65
            add_uv_sphere(
                f"{instance}__CROWN_{crown + 1:02d}",
                (x + offset_x, y, 11.5 + offset_z),
                canopy_scale,
                "sage_green",
                root,
                "TREE_CANOPY",
                sample_id,
                instance,
            )


def build_trees():
    add_tree_profile("CommonsShadeTreeRound", ((-220, 145), (220, 145), (-220, -145), (220, -145)), (7.5, 7.5, 6.5), 1)
    add_tree_profile("CommonsShadeTreeWide", ((-115, 145), (115, 145), (-115, -145), (115, -145)), (6.5, 7.0, 5.8), 2)
    add_tree_profile("CommonsShadeTreeColumnar", ((-270, 70), (270, 70), (-270, -70), (270, -70)), (3.8, 4.0, 8.5), 1)


def build_planters():
    sample_id = "CommonsLowPlanter"
    root = sample_root(sample_id)
    positions = ((-82, 42), (82, 42), (-82, -42), (82, -42), (-42, 82), (42, 82), (-42, -82), (42, -82))
    for index, (x, y) in enumerate(positions, 1):
        instance = f"{sample_id}_{index:02d}"
        add_cube(f"{instance}__BODY", (x, y, 0.75), (8.0, 3.2, 1.5), "muted_terracotta", root, "LOW_PLANTER_BODY", sample_id, instance)
        add_cube(f"{instance}__PLANTING", (x, y, 1.60), (6.8, 2.2, 0.30), "sage_green", root, "LOW_PLANTER_PLANTING", sample_id, instance)


def build_benches():
    sample_id = "CommonsBench"
    root = sample_root(sample_id)
    positions = ((-95, 32, 0), (95, 32, math.pi), (-95, -32, 0), (95, -32, math.pi), (-32, 95, math.pi / 2), (32, 95, -math.pi / 2), (-32, -95, math.pi / 2), (32, -95, -math.pi / 2))
    for index, (x, y, rotation) in enumerate(positions, 1):
        instance = f"{sample_id}_{index:02d}"
        seat = add_cube(f"{instance}__SEAT", (x, y, 1.05), (4.5, 1.35, 0.25), "warm_limestone", root, "BENCH_SEAT", sample_id, instance)
        seat.rotation_euler[2] = rotation
        back = add_cube(f"{instance}__BACK", (x, y + 0.58 * math.cos(rotation), 1.80), (4.5, 0.22, 1.25), "restrained_cobalt", root, "BENCH_BACK", sample_id, instance)
        back.rotation_euler[2] = rotation


def build_lamps():
    sample_id = "CommonsPedestrianLamp"
    root = sample_root(sample_id)
    positions = ((-180, 31), (-90, 31), (0, 31), (90, 31), (180, 31), (-180, -31), (-90, -31), (0, -31), (90, -31), (180, -31), (-31, 150), (31, -150))
    for index, (x, y) in enumerate(positions, 1):
        instance = f"{sample_id}_{index:02d}"
        add_cylinder(f"{instance}__POST", (x, y, 3.5), 0.32, 7.0, "charcoal_gray", root, "PEDESTRIAN_LAMP_POST", sample_id, instance, 10)
        add_uv_sphere(f"{instance}__LANTERN", (x, y, 7.2), (0.85, 0.85, 0.75), "burnt_orange", root, "PEDESTRIAN_LAMP_HEAD", sample_id, instance, 10, 5)


def build_bins():
    sample_id = "CommonsLitterBin"
    root = sample_root(sample_id)
    for index, (x, y) in enumerate(((-68, 31), (68, 31), (-68, -31), (68, -31)), 1):
        instance = f"{sample_id}_{index:02d}"
        add_cylinder(f"{instance}__BODY", (x, y, 1.0), 0.85, 2.0, "charcoal_gray", root, "LITTER_BIN_BODY", sample_id, instance, 12)
        add_cylinder(f"{instance}__LID", (x, y, 2.08), 0.96, 0.16, "restrained_cobalt", root, "LITTER_BIN_LID", sample_id, instance, 12)


def build_bollards():
    sample_id = "CommonsBollardEdge"
    root = sample_root(sample_id)
    positions = ((-185, 190), (-165, 190), (-145, 190), (-125, 190), (125, -190), (145, -190), (165, -190), (185, -190))
    for index, (x, y) in enumerate(positions, 1):
        instance = f"{sample_id}_{index:02d}"
        bollard = add_cylinder(f"{instance}__POST", (x, y, 0.65), 0.48, 1.30, "restrained_cobalt", root, "SHORT_NONBLOCKING_EDGE_BOLLARD", sample_id, instance, 10)
        bollard["blocking"] = False
        bollard["outside_cross_paths"] = True


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
    SITE = bpy.data.collections.new("CENTRAL_COMMONS_SITE")
    SAMPLES = bpy.data.collections.new("NONCANONICAL_REVIEW_SAMPLES")
    bpy.context.scene.collection.children.link(SITE)
    bpy.context.scene.collection.children.link(SAMPLES)

    MATERIALS.clear()
    for name, (_hex, color) in PALETTE.items():
        MATERIALS[name] = make_material(name, color)

    build_site()
    build_trees()
    build_planters()
    build_benches()
    build_lamps()
    build_bins()
    build_bollards()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = (0.055, 0.072, 0.070)
    scene["phase"] = "Phase 1L.3c"
    scene["status"] = "NONCANONICAL_CENTRAL_COMMONS_REVIEW"
    scene["planning_footprint_m"] = "600x420"
    scene["lawn_quadrants"] = 4
    scene["broad_step_free_cross_paths"] = 2
    scene["external_refs_count"] = 0
    scene["interiors_count"] = 0
    scene["gameplay_changes_count"] = 0
    scene["production_catalog_changed"] = False
    scene["production_map_changed"] = False
    scene["production_route_changed"] = False

    bpy.ops.object.light_add(type="AREA", location=(0.0, -60.0, 480.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 5200.0
    key.data.shape = "DISK"
    key.data.size = 350.0
    point_camera(key, key.location, (0.0, 0.0, 0.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 300.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.55, -0.35, -0.45)
    sun.data.energy = 2.2

    for filename, role, direction, location, target, framing_value, _resolution in VIEWS:
        camera_data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        if role == "UNIFIED_TOP":
            camera_data.type = "ORTHO"
            camera_data.ortho_scale = framing_value
        else:
            camera_data.type = "PERSP"
            camera_data.lens = framing_value
            camera_data.clip_start = 0.1
            camera_data.clip_end = 1000.0
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", camera_data)
        support.objects.link(camera)
        point_camera(camera, location, target)
        camera["view_role"] = role
        camera["cardinal_direction"] = direction
        camera["render_file"] = filename
        camera["pedestrian_eye_height_m"] = 1.7 if role == "CARDINAL" else 0.0
        camera["shows_broad_cross_path"] = role == "CARDINAL"
        camera["geometry_frozen_camera_repair"] = True

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
    mins = Vector((min(corner.x for corner in corners), min(corner.y for corner in corners), min(corner.z for corner in corners)))
    maxs = Vector((max(corner.x for corner in corners), max(corner.y for corner in corners), max(corner.z for corner in corners)))
    delta = Vector(
        (
            max(mins.x - point.x, 0.0, point.x - maxs.x),
            max(mins.y - point.y, 0.0, point.y - maxs.y),
            max(mins.z - point.z, 0.0, point.z - maxs.z),
        )
    )
    return delta.length


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = {obj.name: obj for obj in objects if obj.type == "EMPTY" and obj.name.startswith("SAMPLE_ROOT__")}
    expected_roots = {f"SAMPLE_ROOT__{sample_id}" for sample_id in SAMPLE_IDS}
    if set(roots) != expected_roots:
        errors.append(f"exactly nine noncanonical sample roots are required: {sorted(roots)}")
    if any(roots[name].get("review_sample_id") not in SAMPLE_IDS or roots[name].get("asset_role") != "NONCANONICAL_REVIEW_SAMPLE" for name in roots):
        errors.append("review sample roots must retain exact IDs and noncanonical roles")

    counts = actual_instance_counts()
    if counts != INSTANCE_COUNTS:
        errors.append(f"review instance counts differ: {counts}")
    tree_count = sum(counts[sample_id] for sample_id in SAMPLE_IDS if sample_id.startswith("CommonsShadeTree"))
    if tree_count != TREE_LIMIT or counts["CommonsLowPlanter"] > PLANTER_LIMIT or counts["CommonsBench"] > BENCH_LIMIT or counts["CommonsPedestrianLamp"] > LAMP_LIMIT or counts["CommonsLitterBin"] > BIN_LIMIT:
        errors.append("landscape instance ceilings differ")

    lawns = [obj for obj in objects if obj.get("asset_role") == "LAWN_QUADRANT"]
    paths = [obj for obj in objects if obj.get("asset_role") == "BROAD_STEP_FREE_CROSS_PATH"]
    if len(lawns) != 4 or len(paths) != 2:
        errors.append("exactly four lawn quadrants and two broad cross-paths are required")
    if any(path.get("path_width_m") != PATH_WIDTH_M or path.get("step_free") is not True or path.get("top_elevation_m") != STEP_FREE_ELEVATION_M for path in paths):
        errors.append("both cross-paths must be broad and step-free at the lawn elevation")
    bollards = [obj for obj in objects if obj.get("asset_role") == "SHORT_NONBLOCKING_EDGE_BOLLARD"]
    if len(bollards) != INSTANCE_COUNTS["CommonsBollardEdge"] or any(obj.get("blocking") is not False or obj.get("outside_cross_paths") is not True for obj in bollards):
        errors.append("the bollard demonstration must remain short, nonblocking, and outside the cross-paths")

    triangles = sample_triangle_counts()
    if set(triangles) != set(SAMPLE_IDS) or any(value <= 0 or value > TRIANGLE_CEILING for value in triangles.values()):
        errors.append(f"sample triangle counts are invalid: {triangles}")

    allowed_materials = set(PALETTE)
    for obj in [candidate for candidate in objects if candidate.type == "MESH"]:
        for material in obj.data.materials:
            if material.name not in allowed_materials or material.get("accepted_palette_hex") != PALETTE[material.name][0]:
                errors.append(f"{obj.name} uses a nonaccepted material")
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not (PARK_BOUNDS_M["x"][0] <= world.x <= PARK_BOUNDS_M["x"][1] and PARK_BOUNDS_M["y"][0] <= world.y <= PARK_BOUNDS_M["y"][1] and PARK_BOUNDS_M["z"][0] <= world.z <= PARK_BOUNDS_M["z"][1]):
                errors.append(f"{obj.name} exceeds the 600x420 m review footprint")
                break
        if obj.get("review_sample_id") and (obj.get("external_reference") is not False or obj.get("interior") is not False or obj.get("gameplay") is not False):
            errors.append(f"{obj.name} violates exterior native review metadata")

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    expected_cameras = {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}
    if {camera.name for camera in cameras} != expected_cameras:
        errors.append("camera IDs must match the unified-top plus four-cardinal contract")
    if Counter(camera.get("view_role") for camera in cameras) != Counter({"UNIFIED_TOP": 1, "CARDINAL": 4}):
        errors.append("views must be one unified top and four cardinal frames")
    if {camera.get("cardinal_direction") for camera in cameras} != {"TOP", "NORTH", "EAST", "SOUTH", "WEST"}:
        errors.append("top and N/E/S/W view directions are required")
    top_camera = next((camera for camera in cameras if camera.get("view_role") == "UNIFIED_TOP"), None)
    cardinal_cameras = [camera for camera in cameras if camera.get("view_role") == "CARDINAL"]
    if not top_camera or top_camera.data.type != "ORTHO" or top_camera.data.ortho_scale != 800.0:
        errors.append("the unified top camera must retain complete orthographic planning framing")
    expected_lenses = {f"CAMERA__{Path(filename).stem}": framing for filename, role, _direction, _location, _target, framing, _resolution in VIEWS if role == "CARDINAL"}
    if any(camera.data.type != "PERSP" or camera.data.lens != expected_lenses[camera.name] or abs(camera.location.z - 1.7) > 0.0001 or camera.get("pedestrian_eye_height_m") != 1.7 or camera.get("shows_broad_cross_path") is not True for camera in cardinal_cameras):
        errors.append("all four cardinal cameras must remain deterministic 1.7 m pedestrian cross-path views")
    sample_meshes = [obj for obj in objects if obj.type == "MESH" and obj.get("review_sample_id")]
    for camera in cardinal_cameras:
        clearance = min(point_to_bounds_distance(camera.location, obj) for obj in sample_meshes)
        if clearance < 0.5:
            errors.append(f"{camera.name} is not clear of every sample AABB: {clearance:.3f} m")
        camera["minimum_sample_aabb_clearance_m"] = round(clearance, 4)

    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("review renderer must remain Eevee")
    if scene.get("planning_footprint_m") != "600x420" or scene.get("lawn_quadrants") != 4 or scene.get("broad_step_free_cross_paths") != 2:
        errors.append("accepted commons planning contract differs")
    if any((scene.get("external_refs_count"), scene.get("interiors_count"), scene.get("gameplay_changes_count"))):
        errors.append("external references, interiors, and gameplay changes must remain zero")
    if any((scene.get("production_catalog_changed"), scene.get("production_map_changed"), scene.get("production_route_changed"))):
        errors.append("production catalog, map, and route must remain unchanged")
    if len(bpy.data.materials) != len(PALETTE) or {material.name for material in bpy.data.materials} != set(PALETTE):
        errors.append("the Blend must use exactly the accepted seven-color planning palette")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, textures, and source images are forbidden")
    if any(obj.type in {"ARMATURE", "VOLUME", "META"} for obj in objects):
        errors.append("characters, interiors, and volume geometry are forbidden")

    if require_outputs:
        expected_renders = sorted(view[0] for view in VIEWS)
        actual_renders = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if actual_renders != expected_renders:
            errors.append(f"expected exactly five review PNGs, found {actual_renders}")
        if not BLEND_PATH.exists() or not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("Blend, manifest, and provenance are required")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("Blender backup output is forbidden")
        if MANIFEST_PATH.exists():
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            for artifact in manifest["artifacts"]:
                path = ROOT / artifact["file"]
                if not path.exists() or path.stat().st_size != artifact["bytes"] or sha256(path) != artifact["sha256"]:
                    errors.append(f"artifact identity differs: {artifact['file']}")
    if errors:
        raise RuntimeError("\n".join(errors))

    print(
        "ODDSWELL_SUNDALE_COMMONS_VALIDATION|result=PASS|samples=9|lawns=4|paths=2_step_free|"
        f"trees={tree_count}/{TREE_LIMIT}|planters={counts['CommonsLowPlanter']}/{PLANTER_LIMIT}|"
        f"benches={counts['CommonsBench']}/{BENCH_LIMIT}|lamps={counts['CommonsPedestrianLamp']}/{LAMP_LIMIT}|"
        f"bins={counts['CommonsLitterBin']}/{BIN_LIMIT}|bollards={counts['CommonsBollardEdge']}_nonblocking|"
        "views=1_top+4_cardinal|footprint_m=600x420|engine=eevee|external_refs=0|interiors=0|gameplay=0|"
        "production_catalog_changed=false|production_map_changed=false|production_route_changed=false"
    )
    return triangles, counts


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    expected = {view[0] for view in VIEWS}
    for existing in RENDER_DIR.glob("*.png"):
        if existing.name not in expected:
            existing.unlink()
    scene = bpy.context.scene
    for filename, _role, _direction, _location, _target, _framing_value, resolution in VIEWS:
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)


def write_provenance():
    PROVENANCE_PATH.write_text(
        "# Sundale Central Commons Landscape Kit Review Provenance\n\n"
        "- Phase: `Phase 1L.3c`\n"
        "- Status: noncanonical owner review only\n"
        "- Builder: `build_sundale_central_commons.py`\n"
        "- Geometry: deterministic Blender-native low-poly primitives\n"
        "- Palette: the seven accepted planning colors frozen in `Design/Sundale Art Direction and Core Loop.md`\n"
        "- Renderer: Blender Eevee\n"
        "- External libraries, models, images, textures, fonts, brands, catalogs, and frameworks: none\n"
        "- Interiors, gameplay, client, runtime, Unreal map, route, production-catalog, test, and config changes: none\n\n"
        "The nine exact IDs are noncanonical review identifiers, not production catalog IDs. The four lawns, two broad step-free cross-paths, landscape instances, and short edge-bollard demonstration are planning evidence only. Promotion, production modeling, collision, accessibility acceptance, placement, performance, and catalog expansion remain owner-gated.\n",
        encoding="utf-8",
    )


def artifact_record(path):
    return {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_manifest():
    triangles, counts = validate_scene(require_outputs=False)
    artifacts = [BLEND_PATH, Path(__file__).resolve(), PROVENANCE_PATH] + [RENDER_DIR / view[0] for view in VIEWS]
    manifest = {
        "phase": "Phase 1L.3c",
        "status": "noncanonical_owner_review_board",
        "manual_input": False,
        "renderer": "BLENDER_EEVEE_NEXT",
        "planning_contract": {
            "footprint_m": [600, 420],
            "lawn_quadrants": 4,
            "broad_step_free_cross_paths": 2,
            "path_width_m": PATH_WIDTH_M,
            "common_top_elevation_m": STEP_FREE_ELEVATION_M,
        },
        "sample_contract": {
            "sample_count": 9,
            "sample_ids": list(SAMPLE_IDS),
            "noncanonical_review_ids_only": True,
            "instance_counts": counts,
            "triangle_counts": triangles,
            "triangle_ceiling_per_sample": TRIANGLE_CEILING,
            "ceilings": {"trees": TREE_LIMIT, "planters": PLANTER_LIMIT, "benches": BENCH_LIMIT, "lamps": LAMP_LIMIT, "bins": BIN_LIMIT},
            "bollard_demo_nonblocking": True,
            "native_geometry_only": True,
        },
        "boundaries": {
            "external_references": 0,
            "interiors": 0,
            "gameplay_changes": 0,
            "production_catalog_changed": False,
            "production_map_changed": False,
            "production_route_changed": False,
        },
        "views": [
            {"file": f"renders/{filename}", "role": role, "direction": direction, "width": resolution[0], "height": resolution[1]}
            for filename, role, direction, _location, _target, _scale, resolution in VIEWS
        ],
        "artifacts": [artifact_record(path) for path in artifacts],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest_only(label):
    validate_scene(require_outputs=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(
        f"ODDSWELL_SUNDALE_COMMONS_{label}|result=PASS|manifest=true|"
        f"artifact_hashes={len(manifest['artifacts'])}|render_hashes={len(manifest['views'])}|manual_input=false"
    )


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    mode = args[0] if args else "--build"
    if mode == "--build":
        build_scene()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        print(f"ODDSWELL_SUNDALE_COMMONS_BUILD|result=PASS|artifacts={len(manifest['artifacts']) + 1}|manual_input=false")
    elif mode == "--validate-saved":
        validate_manifest_only("REOPEN")
    elif mode == "--focused":
        validate_manifest_only("FOCUSED")
    else:
        raise RuntimeError(f"unsupported mode: {mode}")


if __name__ == "__main__":
    main()
