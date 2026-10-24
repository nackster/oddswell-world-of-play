"""Build and validate the noncanonical Phase 1L.3e street/wayfinding review board."""

import hashlib
import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleStreetWayfindingReviewBoard.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"

SAMPLE_IDS = (
    "StreetAsphaltModule",
    "CurbStraightModule",
    "CurbCornerModule",
    "SidewalkStraightModule",
    "SidewalkCornerModule",
    "PaverTransitionReference",
    "RouteMarkStraight",
    "RouteMarkTurn",
    "RouteMarkDestination",
)
ROUTE_IDS = SAMPLE_IDS[-3:]
BOARD_SIZE_M = (64.0, 64.0)
ROAD_WIDTH_M = 12.0
TRIANGLE_CEILING = 2500
REVIEW_BOUNDS_M = {"x": (-32.01, 32.01), "y": (-32.01, 32.01), "z": (-0.31, 1.51)}

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
    ("Unified_TopDown_StreetWayfinding.png", "UNIFIED_TOP", "TOP", (0.0, 0.0, 72.0), (0.0, 0.0, 0.0), 90.0, (1920, 1080)),
    ("Cardinal_North_StreetWayfinding.png", "CARDINAL", "NORTH", (0.0, -36.0, 1.7), (0.0, 0.0, 0.30), 12.0, (1600, 900)),
    ("Cardinal_East_StreetWayfinding.png", "CARDINAL", "EAST", (-36.0, 0.0, 1.7), (0.0, 0.0, 0.30), 12.0, (1600, 900)),
    ("Cardinal_South_StreetWayfinding.png", "CARDINAL", "SOUTH", (0.0, 36.0, 1.7), (0.0, 0.0, 0.30), 12.0, (1600, 900)),
    ("Cardinal_West_StreetWayfinding.png", "CARDINAL", "WEST", (36.0, 0.0, 1.7), (0.0, 0.0, 0.30), 12.0, (1600, 900)),
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
    shader.inputs["Roughness"].default_value = 0.84
    material["accepted_palette_hex"] = PALETTE[name][0]
    return material


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def tag(obj, sample_id="", role="REVIEW_SITE"):
    obj["review_sample_id"] = sample_id
    obj["review_instance_id"] = sample_id if sample_id else ""
    obj["asset_role"] = role
    obj["noncanonical"] = True
    for field in ("external_reference", "texture", "interior", "brand", "gameplay", "traffic", "vehicle"):
        obj[field] = False
    return obj


def add_root(sample_id, shape_identity=""):
    root = bpy.data.objects.new(f"SAMPLE_ROOT__{sample_id}", None)
    tag(root, sample_id, "NONCANONICAL_REVIEW_SAMPLE")
    root["shape_identity"] = shape_identity
    root["shape_distinct"] = sample_id not in ROUTE_IDS or bool(shape_identity)
    root["color_only"] = False
    SAMPLES.objects.link(root)
    return root


def add_cube(name, location, dimensions, material_name, parent, role, sample_id="", rotation_z=0.0, collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=(0.0, 0.0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, role)
    obj.parent = parent
    move_to_collection(obj, collection or SAMPLES)
    return obj


def add_cylinder(name, location, radius, depth, material_name, parent, role, sample_id, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, role)
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
    tag(obj, sample_id, role)
    obj.parent = parent
    move_to_collection(obj, SAMPLES)
    return obj


def add_triangle(name, points, z, material_name, parent, role, sample_id):
    mesh = bpy.data.meshes.new(f"{name}__MESH")
    mesh.from_pydata([(x, y, z) for x, y in points], [], [(0, 1, 2)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(MATERIALS[material_name])
    tag(obj, sample_id, role)
    obj.parent = parent
    SAMPLES.objects.link(obj)
    return obj


def build_asphalt():
    sample_id = "StreetAsphaltModule"
    root = add_root(sample_id)
    add_cube(f"{sample_id}__NORTH_SOUTH", (0.0, 0.0, 0.02), (ROAD_WIDTH_M, 64.0, 0.12), "charcoal_gray", root, "FOUR_ARM_ASPHALT", sample_id)
    add_cube(f"{sample_id}__EAST_WEST", (0.0, 0.0, 0.025), (64.0, ROAD_WIDTH_M, 0.13), "charcoal_gray", root, "FOUR_ARM_ASPHALT", sample_id)
    root["four_arm_intersection"] = True


def build_straight_curbs():
    sample_id = "CurbStraightModule"
    root = add_root(sample_id)
    for axis, fixed, span in (("X", -6.25, (-32.0, -9.0)), ("X", 6.25, (9.0, 32.0))):
        for y0, y1 in (span, (-span[1], -span[0])):
            add_cube(f"{sample_id}__{axis}_{fixed}_{y0}", (fixed, (y0 + y1) / 2, 0.18), (0.5, y1 - y0, 0.30), "sand_concrete", root, "STRAIGHT_CURB", sample_id)
    for axis, fixed, span in (("Y", -6.25, (-32.0, -9.0)), ("Y", 6.25, (9.0, 32.0))):
        for x0, x1 in (span, (-span[1], -span[0])):
            add_cube(f"{sample_id}__{axis}_{fixed}_{x0}", ((x0 + x1) / 2, fixed, 0.18), (x1 - x0, 0.5, 0.30), "sand_concrete", root, "STRAIGHT_CURB", sample_id)


def build_corner_curbs():
    sample_id = "CurbCornerModule"
    root = add_root(sample_id)
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        x, y = sx * 7.6, sy * 8.6
        add_cube(f"{sample_id}__X_{sx}_{sy}", (x, sy * 6.25, 0.18), (2.8, 0.5, 0.30), "warm_limestone", root, "L_SHAPED_CORNER_CURB", sample_id)
        add_cube(f"{sample_id}__Y_{sx}_{sy}", (sx * 6.25, y, 0.18), (0.5, 4.2, 0.30), "warm_limestone", root, "L_SHAPED_CORNER_CURB", sample_id)
    root["corner_silhouette"] = "L_SHAPE"


def build_straight_sidewalks():
    sample_id = "SidewalkStraightModule"
    root = add_root(sample_id)
    for sx in (-1, 1):
        add_cube(f"{sample_id}__VERTICAL_{sx}", (sx * 8.0, 0.0, 0.19), (3.0, 64.0, 0.22), "warm_limestone", root, "STRAIGHT_SIDEWALK", sample_id)
    for sy in (-1, 1):
        add_cube(f"{sample_id}__HORIZONTAL_{sy}", (0.0, sy * 8.0, 0.195), (64.0, 3.0, 0.23), "warm_limestone", root, "STRAIGHT_SIDEWALK", sample_id)


def build_corner_sidewalks():
    sample_id = "SidewalkCornerModule"
    root = add_root(sample_id)
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        add_cube(f"{sample_id}__CORNER_{sx}_{sy}", (sx * 9.0, sy * 9.0, 0.20), (6.0, 6.0, 0.24), "sand_concrete", root, "SQUARE_CORNER_SIDEWALK", sample_id)
    root["corner_silhouette"] = "SQUARE_APRON"


def build_pavers():
    sample_id = "PaverTransitionReference"
    root = add_root(sample_id)
    for index, offset in enumerate((-2.25, -0.75, 0.75, 2.25), 1):
        add_cube(f"{sample_id}__CROSSWALK_N_{index}", (offset, -7.95, 0.345), (1.05, 3.1, 0.05), "muted_terracotta", root, "PAVER_TRANSITION_BAND", sample_id)
        add_cube(f"{sample_id}__CROSSWALK_E_{index}", (7.95, offset, 0.35), (3.1, 1.05, 0.05), "muted_terracotta", root, "PAVER_TRANSITION_BAND", sample_id)
    root["reference_only"] = True


def build_route_straight():
    sample_id = "RouteMarkStraight"
    root = add_root(sample_id, "STRAIGHT_BAR_DOUBLE_CHEVRON")
    add_cube(f"{sample_id}__BAR", (-8.0, -22.0, 0.34), (1.1, 7.8, 0.07), "restrained_cobalt", root, "SHAPE_CODED_ROUTE_MARK", sample_id)
    for index, y in enumerate((-17.5, -14.5), 1):
        add_cube(f"{sample_id}__CHEVRON_L_{index}", (-8.65, y, 0.35), (0.36, 2.0, 0.08), "restrained_cobalt", root, "STRAIGHT_CHEVRON", sample_id, -math.radians(42))
        add_cube(f"{sample_id}__CHEVRON_R_{index}", (-7.35, y, 0.35), (0.36, 2.0, 0.08), "restrained_cobalt", root, "STRAIGHT_CHEVRON", sample_id, math.radians(42))


def build_route_turn():
    sample_id = "RouteMarkTurn"
    root = add_root(sample_id, "RIGHT_ANGLE_BAR_ARROW")
    add_cube(f"{sample_id}__LEG_Y", (8.0, -19.0, 0.35), (1.1, 7.0, 0.08), "restrained_cobalt", root, "SHAPE_CODED_ROUTE_MARK", sample_id)
    add_cube(f"{sample_id}__LEG_X", (12.0, -15.5, 0.35), (8.0, 1.1, 0.08), "restrained_cobalt", root, "TURN_LEG", sample_id)
    add_triangle(f"{sample_id}__ARROW", ((15.0, -17.2), (15.0, -13.8), (18.3, -15.5)), 0.39, "restrained_cobalt", root, "TURN_ARROWHEAD", sample_id)


def build_route_destination():
    sample_id = "RouteMarkDestination"
    root = add_root(sample_id, "CONCENTRIC_RING_TARGET")
    add_torus(f"{sample_id}__RING", (8.0, 20.5, 0.43), 2.6, 0.34, "restrained_cobalt", root, "SHAPE_CODED_ROUTE_MARK", sample_id)
    add_cylinder(f"{sample_id}__TARGET", (8.0, 20.5, 0.42), 0.72, 0.10, "restrained_cobalt", root, "DESTINATION_TARGET", sample_id, 24)
    for index, angle in enumerate((0.0, math.pi / 2, math.pi, 3 * math.pi / 2), 1):
        x = 8.0 + 3.45 * math.cos(angle)
        y = 20.5 + 3.45 * math.sin(angle)
        add_cube(f"{sample_id}__TICK_{index}", (x, y, 0.39), (0.95 if index % 2 else 0.30, 0.30 if index % 2 else 0.95, 0.08), "restrained_cobalt", root, "DESTINATION_TICK", sample_id)


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
    SITE = bpy.data.collections.new("STREET_WAYFINDING_REVIEW_SITE")
    SAMPLES = bpy.data.collections.new("NONCANONICAL_REVIEW_SAMPLES")
    bpy.context.scene.collection.children.link(SITE)
    bpy.context.scene.collection.children.link(SAMPLES)

    MATERIALS.clear()
    for name, (_hex, color) in PALETTE.items():
        MATERIALS[name] = make_material(name, color)

    site_root = bpy.data.objects.new("STREET_WAYFINDING_REVIEW_SITE_ROOT", None)
    tag(site_root, role="REVIEW_SITE")
    SITE.objects.link(site_root)
    add_cube("REVIEW_GROUND_64M", (0.0, 0.0, -0.18), (64.0, 64.0, 0.24), "sage_green", site_root, "NONPRODUCTION_REVIEW_GROUND", collection=SITE)

    build_asphalt()
    build_straight_curbs()
    build_corner_curbs()
    build_straight_sidewalks()
    build_corner_sidewalks()
    build_pavers()
    build_route_straight()
    build_route_turn()
    build_route_destination()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.world.color = (0.045, 0.060, 0.070)
    scene["phase"] = "Phase 1L.3e"
    scene["status"] = "NONCANONICAL_STREET_WAYFINDING_OWNER_REVIEW"
    scene["board_size_m"] = "64x64"
    scene["intersection_arms"] = 4
    scene["canonical"] = False
    scene["exact_distance_m"] = "null"
    scene["shape_distinct"] = True
    scene["color_only"] = False
    for field in (
        "external_refs_count",
        "textures_count",
        "interiors_count",
        "brands_count",
        "gameplay_changes_count",
        "traffic_count",
        "vehicles_count",
        "generalized_road_system_count",
    ):
        scene[field] = 0
    for field in (
        "production_catalog_changed",
        "production_map_changed",
        "production_route_changed",
        "production_collision_changed",
        "production_navigation_changed",
        "package_changed",
    ):
        scene[field] = False

    bpy.ops.object.light_add(type="AREA", location=(-8.0, -10.0, 42.0))
    key = bpy.context.object
    key.name = "LIGHT_KEY"
    key.data.energy = 2100.0
    key.data.shape = "DISK"
    key.data.size = 24.0
    point_camera(key, key.location, (0.0, 0.0, 0.0))
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 30.0))
    sun = bpy.context.object
    sun.name = "LIGHT_SUN"
    sun.rotation_euler = (0.55, -0.35, -0.45)
    sun.data.energy = 1.8

    for filename, role, direction, location, target, framing, _resolution in VIEWS:
        data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        if role == "UNIFIED_TOP":
            data.type = "ORTHO"
            data.ortho_scale = framing
        else:
            data.type = "PERSP"
            data.lens = framing
            data.clip_start = 0.1
            data.clip_end = 300.0
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", data)
        support.objects.link(camera)
        point_camera(camera, location, target)
        camera["view_role"] = role
        camera["compass_direction"] = direction
        camera["render_file"] = filename
        camera["pedestrian_eye_height_m"] = 1.7 if role == "CARDINAL" else 0.0
        camera["complete_intersection_framing_required"] = True
        camera["shape_coded_marks_visible_required"] = True

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


def validate_scene(require_outputs):
    errors = []
    objects = list(bpy.data.objects)
    roots = {obj.name: obj for obj in objects if obj.type == "EMPTY" and obj.name.startswith("SAMPLE_ROOT__")}
    if set(roots) != {f"SAMPLE_ROOT__{sample_id}" for sample_id in SAMPLE_IDS}:
        errors.append(f"exactly nine named review roots are required: {sorted(roots)}")
    counts = actual_instance_counts()
    if counts != {sample_id: 1 for sample_id in SAMPLE_IDS}:
        errors.append(f"every exact review ID must have one instance: {counts}")
    triangles = sample_triangle_counts()
    if set(triangles) != set(SAMPLE_IDS) or any(value <= 0 or value > TRIANGLE_CEILING for value in triangles.values()):
        errors.append(f"triangle ceilings differ: {triangles}")

    route_shapes = {}
    for sample_id in ROUTE_IDS:
        root = roots.get(f"SAMPLE_ROOT__{sample_id}")
        if not root or root.get("shape_distinct") is not True or root.get("color_only") is not False:
            errors.append(f"{sample_id} must be shape-distinct and not color-only")
        elif not root.get("shape_identity"):
            errors.append(f"{sample_id} is missing its shape identity")
        else:
            route_shapes[sample_id] = root.get("shape_identity")
    if len(set(route_shapes.values())) != 3:
        errors.append(f"route mark silhouettes must be distinct: {route_shapes}")

    allowed_materials = set(PALETTE)
    for obj in [candidate for candidate in objects if candidate.type == "MESH"]:
        for material in obj.data.materials:
            if material.name not in allowed_materials or material.get("accepted_palette_hex") != PALETTE[material.name][0]:
                errors.append(f"{obj.name} uses a nonaccepted material")
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            if not all(REVIEW_BOUNDS_M[axis][0] <= world[index] <= REVIEW_BOUNDS_M[axis][1] for index, axis in enumerate(("x", "y", "z"))):
                errors.append(f"{obj.name} exceeds the bounded 64x64 m board")
                break
        if any(obj.get(field) is not False for field in ("external_reference", "texture", "interior", "brand", "gameplay", "traffic", "vehicle")):
            errors.append(f"{obj.name} violates review-only metadata")

    scene = bpy.context.scene
    if scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append("renderer must remain Eevee")
    if scene.get("board_size_m") != "64x64" or scene.get("intersection_arms") != 4:
        errors.append("the board must remain one 64x64 m four-arm intersection")
    if scene.get("canonical") is not False or scene.get("exact_distance_m") != "null":
        errors.append("the review must remain noncanonical with exact_distance_m=null")
    if scene.get("shape_distinct") is not True or scene.get("color_only") is not False:
        errors.append("route wayfinding must be understandable by shape, not color alone")
    zero_fields = (
        "external_refs_count",
        "textures_count",
        "interiors_count",
        "brands_count",
        "gameplay_changes_count",
        "traffic_count",
        "vehicles_count",
        "generalized_road_system_count",
    )
    if any(scene.get(field) != 0 for field in zero_fields):
        errors.append("external references/textures/interiors/brands/gameplay/traffic/vehicles/road systems must remain zero")
    false_fields = (
        "production_catalog_changed",
        "production_map_changed",
        "production_route_changed",
        "production_collision_changed",
        "production_navigation_changed",
        "package_changed",
    )
    if any(scene.get(field) is not False for field in false_fields):
        errors.append("production catalog/map/route/collision/navigation/package must remain unchanged")
    material_names = {material.name for material in bpy.data.materials}
    if not material_names or not material_names <= set(PALETTE):
        errors.append("materials must be a nonempty subset of the accepted planning palette")
    if bpy.data.libraries or bpy.data.textures or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries, textures, and source images are forbidden")
    if any(obj.type in {"ARMATURE", "VOLUME", "META", "FONT"} for obj in objects):
        errors.append("characters, volumes, and fonts are forbidden")

    cameras = [obj for obj in objects if obj.type == "CAMERA"]
    if {camera.name for camera in cameras} != {f"CAMERA__{Path(view[0]).stem}" for view in VIEWS}:
        errors.append("camera IDs must match one top plus four compass views")
    if {camera.get("compass_direction") for camera in cameras} != {"TOP", "NORTH", "EAST", "SOUTH", "WEST"}:
        errors.append("top and four compass directions are required")
    cardinals = [camera for camera in cameras if camera.get("view_role") == "CARDINAL"]
    expected_cardinals = {f"CAMERA__{Path(view[0]).stem}": view for view in VIEWS if view[1] == "CARDINAL"}
    if len(cardinals) != 4 or any(
        camera.data.type != "PERSP"
        or tuple(round(value, 4) for value in camera.location) != expected_cardinals[camera.name][3]
        or camera.data.lens != expected_cardinals[camera.name][5]
        or camera.data.shift_y != 0.0
        or abs(camera.location.z - 1.7) > 0.0001
        or camera.get("pedestrian_eye_height_m") != 1.7
        or camera.get("complete_intersection_framing_required") is not True
        or camera.get("shape_coded_marks_visible_required") is not True
        for camera in cardinals
    ):
        errors.append("four deterministic 1.7 m compass views must frame the intersection and shape marks")

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
            for artifact in manifest["artifacts"]:
                path = ROOT / artifact["file"]
                if not path.exists() or path.stat().st_size != artifact["bytes"] or sha256(path) != artifact["sha256"]:
                    errors.append(f"artifact identity differs: {artifact['file']}")
    if errors:
        raise RuntimeError("\n".join(errors))

    print(
        "ODDSWELL_SUNDALE_STREET_WAYFINDING_VALIDATION|result=PASS|samples=9|instances=9|"
        "board_m=64x64|intersection_arms=4|views=1_top+4_cardinal_1.7m|shape_distinct=true|color_only=false|"
        "canonical=false|exact_distance_m=null|engine=eevee|native_geometry=true|external_refs=0|textures=0|"
        "interiors=0|brands=0|gameplay=0|traffic=0|vehicles=0|generalized_road_system=0|"
        "production_catalog_changed=false|production_map_changed=false|production_route_changed=false|"
        "production_collision_changed=false|production_navigation_changed=false|package_changed=false"
    )
    return triangles, counts, route_shapes


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
        "# Sundale Street, Paving, and Shape-Coded Wayfinding Review Board Provenance\n\n"
        "- Phase: Phase 1L.3e\n"
        "- Status: noncanonical owner review only\n"
        "- Builder: build_sundale_street_wayfinding.py\n"
        "- Geometry: deterministic Blender-native low-poly primitives\n"
        "- Authority: one bounded review-only 64x64 m four-arm intersection vignette; not the canonical 800 m route\n"
        "- Route distance: exact_distance_m=null; canonical=false\n"
        "- Palette: seven accepted Sundale planning colors\n"
        "- Renderer: Blender Eevee\n"
        "- External libraries, models, images, textures, fonts, brands, catalogs, frameworks, and paid inputs: none\n"
        "- Interiors, gameplay, traffic, vehicles, transit, generalized road systems, client, runtime, Unreal map, route, collision, navigation, package, test, and config changes: none\n\n"
        "The nine exact IDs are noncanonical review identities, not production catalog IDs. The cobalt straight, turn, and destination marks use distinct silhouettes and are not color-only. Production promotion, placement, collision, navigation, accessibility, route distance, performance, final art, and traffic behavior remain owner-gated.\n",
        encoding="utf-8",
    )


def artifact_record(path):
    return {"file": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_manifest():
    triangles, counts, route_shapes = validate_scene(require_outputs=False)
    artifacts = [BLEND_PATH, Path(__file__).resolve(), PROVENANCE_PATH] + [RENDER_DIR / view[0] for view in VIEWS]
    manifest = {
        "phase": "Phase 1L.3e",
        "status": "noncanonical_owner_review_board",
        "manual_input": False,
        "renderer": "BLENDER_EEVEE_NEXT",
        "authority": {
            "board_size_m": list(BOARD_SIZE_M),
            "intersection_arms": 4,
            "road_width_m": ROAD_WIDTH_M,
            "canonical": False,
            "exact_distance_m": None,
        },
        "sample_contract": {
            "sample_count": len(SAMPLE_IDS),
            "sample_ids": list(SAMPLE_IDS),
            "instance_counts": counts,
            "triangle_counts": triangles,
            "triangle_ceiling_per_sample": TRIANGLE_CEILING,
            "native_geometry_only": True,
            "production_catalog_ids": False,
            "route_shape_identities": route_shapes,
            "shape_distinct": True,
            "color_only": False,
        },
        "boundaries": {
            "external_references": 0,
            "textures": 0,
            "interiors": 0,
            "brands": 0,
            "gameplay_changes": 0,
            "traffic": 0,
            "vehicles": 0,
            "generalized_road_systems": 0,
            "production_catalog_changed": False,
            "production_map_changed": False,
            "production_route_changed": False,
            "production_collision_changed": False,
            "production_navigation_changed": False,
            "package_changed": False,
        },
        "views": [
            {
                "file": f"renders/{view[0]}",
                "role": view[1],
                "direction": view[2],
                "width": view[6][0],
                "height": view[6][1],
                "eye_height_m": 1.7 if view[1] == "CARDINAL" else None,
                "camera_location_m": list(view[3]),
                "lens_mm": view[5] if view[1] == "CARDINAL" else None,
            }
            for view in VIEWS
        ],
        "artifacts": [artifact_record(path) for path in artifacts],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest_only(label):
    validate_scene(require_outputs=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(
        f"ODDSWELL_SUNDALE_STREET_WAYFINDING_{label}|result=PASS|manifest=true|"
        f"artifact_hashes={len(manifest['artifacts'])}|render_hashes={len(manifest['views'])}|manual_input=false"
    )


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    mode = args[0] if args else "--build"
    if mode == "--build":
        build_scene()
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        print(f"ODDSWELL_SUNDALE_STREET_WAYFINDING_BUILD|result=PASS|artifacts={len(manifest['artifacts']) + 1}|manual_input=false")
    elif mode == "--validate-saved":
        validate_manifest_only("REOPEN")
    elif mode == "--focused":
        validate_manifest_only("FOCUSED")
    else:
        raise RuntimeError(f"unsupported mode: {mode}")


if __name__ == "__main__":
    main()
