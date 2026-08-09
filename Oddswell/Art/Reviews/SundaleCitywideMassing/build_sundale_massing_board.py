"""Build and validate the noncanonical Sundale citywide massing review board."""

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "SundaleCitywideMassing.blend"
RENDER_DIR = ROOT / "renders"
MANIFEST_PATH = ROOT / "manifest.json"
RENDER_SIZE = (1280, 900)
EYE_RENDER_HEIGHT = 480

COLORS = {
    "ground": (0.18, 0.20, 0.21, 1.0),
    "road": (0.30, 0.31, 0.32, 1.0),
    "commons": (0.73, 0.65, 0.51, 1.0),
    "route": (0.19, 0.37, 0.47, 1.0),
    "shortcut": (0.43, 0.50, 0.38, 1.0),
    "limestone": (0.85, 0.78, 0.66, 1.0),
    "terracotta": (0.65, 0.37, 0.28, 1.0),
    "charcoal": (0.25, 0.27, 0.28, 1.0),
    "orange": (0.77, 0.43, 0.23, 1.0),
    "cobalt": (0.12, 0.46, 0.63, 1.0),
    "teal": (0.08, 0.60, 0.56, 1.0),
    "court": (0.28, 0.45, 0.39, 1.0),
    "label": (0.03, 0.04, 0.05, 1.0),
}

ROUTE_POINTS = [
    (0.0, 0.0),
    (95.0, 0.0),
    (125.0, 0.0),
    (125.0, 90.0),
    (125.0, 180.0),
    (70.0, 180.0),
    (10.0, 180.0),
    (-95.0, 180.0),
    (-95.0, 160.0),
    (-95.0, 50.0),
    (-95.0, 0.0),
    (0.0, 0.0),
]

ROUTE_SEGMENTS = {
    "AUTH__ROUTE_SOUTH": ((15.0, 0.0, 0.05), (220.0, 4.0, 0.1)),
    "AUTH__ROUTE_EAST": ((125.0, 90.0, 0.05), (4.0, 180.0, 0.1)),
    "AUTH__ROUTE_NORTH": ((15.0, 180.0, 0.05), (220.0, 4.0, 0.1)),
    "AUTH__ROUTE_WEST": ((-95.0, 90.0, 0.05), (4.0, 180.0, 0.1)),
}

SHORTCUTS = {
    "AUTH__SHORTCUT_EAST_WEST": ((15.0, 90.0, 0.11), (220.0, 4.0, 0.1)),
    "AUTH__SHORTCUT_NORTH_SOUTH": ((15.0, 90.0, 0.12), (4.0, 180.0, 0.1)),
}

DESTINATIONS = {
    "STUDIO": (0.0, 0.0),
    "JOB": (95.0, 0.0),
    "CLOTHING": (125.0, 90.0),
    "ARENA": (70.0, 180.0),
    "TICKET_BOOTH": (10.0, 180.0),
    "PUBLIC_COURT": (-95.0, 160.0),
    "FURNITURE": (-95.0, 50.0),
}

EXISTING_MASSING = [
    ("AUTH__STUDIO_MASS", "STUDIO", (0.0, -30.0, 9.0), (50.0, 60.0, 18.0), "limestone"),
    ("AUTH__JOB_MASS", "JOB", (95.0, -25.0, 10.0), (50.0, 50.0, 20.0), "terracotta"),
    ("AUTH__CLOTHING_MASS", "CLOTHING", (150.0, 90.0, 12.0), (50.0, 50.0, 24.0), "limestone"),
    ("AUTH__ARENA_MASS", "ARENA", (70.0, 205.0, 12.0), (100.0, 50.0, 24.0), "limestone"),
    ("AUTH__ARENA_CANOPY", "ARENA", (70.0, 205.0, 24.75), (110.0, 60.0, 1.5), "orange"),
    ("AUTH__TICKET_BOOTH_MASS", "TICKET_BOOTH", (10.0, 205.0, 9.0), (50.0, 50.0, 18.0), "terracotta"),
    ("AUTH__FURNITURE_MASS", "FURNITURE", (-130.0, 50.0, 10.0), (50.0, 50.0, 20.0), "limestone"),
    ("AUTH__PUBLIC_COURT_SURFACE", "PUBLIC_COURT", (-79.0, 150.0, 0.12), (28.65, 15.24, 0.2), "court"),
]

SCENIC_SHELLS = [
    ("PROP__LIMESTONE_01", "limestone", (-135.0, -25.0), (30.0, 30.0), 4),
    ("PROP__LIMESTONE_02", "limestone", (155.0, 20.0), (34.0, 24.0), 5),
    ("PROP__LIMESTONE_03", "limestone", (155.0, 145.0), (34.0, 28.0), 6),
    ("PROP__LIMESTONE_04", "limestone", (-135.0, 100.0), (32.0, 30.0), 5),
    ("PROP__TERRACOTTA_01", "terracotta", (-135.0, 204.0), (30.0, 36.0), 6),
    ("PROP__TERRACOTTA_02", "terracotta", (150.0, -25.0), (40.0, 28.0), 5),
    ("PROP__TERRACOTTA_03", "terracotta", (155.0, 205.0), (36.0, 32.0), 4),
    ("PROP__CHARCOAL_01", "charcoal", (-125.0, 135.0), (30.0, 20.0), 3),
    ("PROP__CHARCOAL_02", "charcoal", (160.0, 50.0), (28.0, 20.0), 4),
    ("PROP__CHARCOAL_03", "charcoal", (-45.0, 215.0), (36.0, 20.0), 5),
]

VIEWS = [
    ("TopDown_AuthorizedAndProposed.png", "top_down", (15.0, 90.0, 420.0), (15.0, 90.0, 0.0), 520.0),
    ("EyeLevel_SouthArrival.png", "eye_level", (-55.0, 5.0, 1.7), (115.0, 160.0, 6.0), None),
    ("EyeLevel_CommonsArenaAxis.png", "eye_level", (-55.0, 50.0, 1.7), (20.0, 205.0, 6.0), None),
    ("EyeLevel_CourtToArena.png", "eye_level", (-95.0, 150.0, 1.7), (85.0, 195.0, 6.0), None),
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


def add_route_curve(collection):
    data = bpy.data.curves.new("AUTH__CANONICAL_ROUTE_DATA", "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = 0.65
    data.bevel_resolution = 0
    spline = data.splines.new("POLY")
    spline.points.add(len(ROUTE_POINTS) - 1)
    for point, (x, y) in zip(spline.points, ROUTE_POINTS):
        point.co = (x, y, 0.32, 1.0)
    obj = bpy.data.objects.new("AUTH__CANONICAL_ROUTE_800M", data)
    data.materials.append(MATERIALS["route"])
    obj["asset_kind"] = "canonical_route"
    obj["status"] = "EXISTING_AUTHORIZED"
    obj["distance_m"] = 800.0
    collection.objects.link(obj)
    return obj


def add_text(name, body, location, size, collection, color="label"):
    data = bpy.data.curves.new(f"{name}_DATA", "FONT")
    data.body = body
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = size
    data.extrude = 0.025
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    obj.data.materials.append(MATERIALS[color])
    obj["asset_kind"] = "review_label"
    collection.objects.link(obj)
    return obj


def point_camera(camera, location, target):
    camera.location = location
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.collections):
        if block.name != "Collection":
            bpy.data.collections.remove(block)
    root_collection = bpy.context.scene.collection
    default = bpy.data.collections.get("Collection")
    existing = bpy.data.collections.new("EXISTING_AUTHORIZED")
    proposed = bpy.data.collections.new("PROPOSED_SCENIC")
    guides = bpy.data.collections.new("REVIEW_GUIDES")
    root_collection.children.link(existing)
    root_collection.children.link(proposed)
    root_collection.children.link(guides)
    if default:
        root_collection.children.unlink(default)
        bpy.data.collections.remove(default)

    global MATERIALS
    MATERIALS = {name: material(f"MAT__{name.upper()}", color) for name, color in COLORS.items()}

    add_cube("AUTH__DISTRICT_340X280M", (15.0, 90.0, -0.25), (340.0, 280.0, 0.5), "ground", existing, "district", status="EXISTING_AUTHORIZED")
    add_cube("AUTH__COMMONS_140X90M", (15.0, 90.0, 0.05), (140.0, 90.0, 0.1), "commons", existing, "commons", status="EXISTING_AUTHORIZED")
    for name, (location, dimensions) in ROUTE_SEGMENTS.items():
        add_cube(name, location, dimensions, "road", existing, "route_segment", status="EXISTING_AUTHORIZED")
    for name, (location, dimensions) in SHORTCUTS.items():
        add_cube(name, location, dimensions, "shortcut", existing, "shortcut", status="EXISTING_AUTHORIZED", step_free=True)
    add_route_curve(existing)

    for name, destination, location, dimensions, color in EXISTING_MASSING:
        add_cube(name, location, dimensions, color, existing, "existing_massing", status="EXISTING_AUTHORIZED", destination_id=destination)
    for destination, (x, y) in DESTINATIONS.items():
        add_cube(f"AUTH__ANCHOR_{destination}", (x, y, 0.45), (4.0, 4.0, 0.4), "cobalt", existing, "destination_anchor", status="EXISTING_AUTHORIZED", destination_id=destination, anchor_x_m=x, anchor_y_m=y)

    for name, family, (x, y), (width, depth), stories in SCENIC_SHELLS:
        height = stories * 3.2
        add_cube(f"{name}__BASE", (x, y, 0.15), (width + 1.2, depth + 1.2, 0.3), "label", proposed, "proposal_base", status="PROPOSED_SCENIC")
        add_cube(name, (x, y, height / 2.0 + 0.3), (width, depth, height), family, proposed, "scenic_shell", status="PROPOSED_SCENIC", family=family, stories=stories, nonenterable=True)

    labels = []
    labels.append(add_text("LABEL__TITLE", "SUNDALE 1L.3a  |  NONCANONICAL MASSING REVIEW", (15.0, 249.0, 30.0), 6.0, guides, "teal"))
    labels.append(add_text("LABEL__LEGEND", "EXISTING AUTHORIZED = COBALT ANCHORS   |   PROPOSED SCENIC = CHARCOAL BASES", (15.0, -65.0, 30.0), 3.5, guides, "orange"))
    labels.append(add_text("LABEL__COMMONS", "AUTHORIZED COMMONS 140m x 90m", (15.0, 90.0, 30.0), 4.2, guides, "cobalt"))
    destination_label_positions = {
        "STUDIO": (0.0, -36.0), "JOB": (95.0, -30.0), "CLOTHING": (150.0, 90.0),
        "ARENA": (70.0, 205.0), "TICKET_BOOTH": (10.0, 205.0),
        "PUBLIC_COURT": (-79.0, 150.0), "FURNITURE": (-130.0, 50.0),
    }
    for destination, (x, y) in destination_label_positions.items():
        labels.append(add_text(f"LABEL__AUTH_{destination}", f"AUTH | {destination.replace('_', ' ')}", (x, y, 30.0), 3.2, guides, "teal"))
    for name, family, (x, y), _dimensions, stories in SCENIC_SHELLS:
        labels.append(add_text(f"LABEL__{name}", f"PROP | {family[0].upper()}{name[-2:]} | {stories}F", (x, y, 30.0), 2.5, guides, "orange"))

    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "REVIEW_CAMERA"
    camera.data.lens = 24.0
    camera.data.clip_end = 1200.0
    camera["asset_kind"] = "review_camera"
    for owner in list(camera.users_collection):
        owner.objects.unlink(camera)
    guides.objects.link(camera)
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 150.0))
    sun = bpy.context.object
    sun.name = "REVIEW_SUN"
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(132.0))
    sun.data.energy = 4.0
    sun["asset_kind"] = "review_light"
    for owner in list(sun.users_collection):
        owner.objects.unlink(sun)
    guides.objects.link(sun)

    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 150.0))
    fill = bpy.context.object
    fill.name = "REVIEW_FILL"
    fill.rotation_euler = (math.radians(42.0), math.radians(12.0), math.radians(-48.0))
    fill.data.energy = 1.5
    fill.data.use_shadow = False
    fill["asset_kind"] = "review_light"
    for owner in list(fill.users_collection):
        owner.objects.unlink(fill)
    guides.objects.link(fill)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.world.color = (0.28, 0.31, 0.36)
    scene.view_settings.exposure = 0.7
    scene["phase"] = "Phase 1L.3a"
    scene["status"] = "NONCANONICAL_REVIEW"
    scene["source_actor_count"] = 45
    scene["cycles_forbidden"] = True

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for stale in RENDER_DIR.glob("*.png"):
        stale.unlink()
    for filename, view_type, location, target, ortho_scale in VIEWS:
        for label in labels:
            label.hide_render = view_type != "top_down"
        scene.render.resolution_y = RENDER_SIZE[1] if view_type == "top_down" else EYE_RENDER_HEIGHT
        camera.data.type = "ORTHO" if view_type == "top_down" else "PERSP"
        if ortho_scale:
            camera.data.ortho_scale = ortho_scale
        point_camera(camera, location, target)
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)

    for label in labels:
        label.hide_render = False
    scene.render.resolution_y = RENDER_SIZE[1]
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = VIEWS[0][4]
    point_camera(camera, VIEWS[0][2], VIEWS[0][3])
    scene.render.filepath = str(RENDER_DIR / VIEWS[0][0])
    bpy.context.preferences.filepaths.save_version = 0
    BLEND_PATH.with_suffix(".blend1").unlink(missing_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)


def route_distance():
    return sum(math.dist(a, b) for a, b in zip(ROUTE_POINTS, ROUTE_POINTS[1:]))


def aabb_intersects_route(x, y, width, depth, clearance=2.0):
    shell = (x - width / 2.0, x + width / 2.0, y - depth / 2.0, y + depth / 2.0)
    for location, dimensions in ROUTE_SEGMENTS.values():
        rx, ry, _ = location
        rw, rd, _ = dimensions
        road = (rx - rw / 2.0 - clearance, rx + rw / 2.0 + clearance, ry - rd / 2.0 - clearance, ry + rd / 2.0 + clearance)
        if shell[0] < road[1] and shell[1] > road[0] and shell[2] < road[3] and shell[3] > road[2]:
            return True
    return False


def validate_scene(require_manifest):
    errors = []
    objects = bpy.data.objects
    expected_dimensions = {
        "AUTH__DISTRICT_340X280M": (340.0, 280.0, 0.5),
        "AUTH__COMMONS_140X90M": (140.0, 90.0, 0.1),
        **{name: dimensions for name, (_location, dimensions) in ROUTE_SEGMENTS.items()},
        **{name: dimensions for name, (_location, dimensions) in SHORTCUTS.items()},
    }
    for name, dimensions in expected_dimensions.items():
        obj = objects.get(name)
        if not obj or any(abs(actual - expected) > 0.001 for actual, expected in zip(obj.dimensions, dimensions)):
            errors.append(f"{name} dimensions must be {dimensions}")

    route = objects.get("AUTH__CANONICAL_ROUTE_800M")
    if not route or route.get("distance_m") != 800.0 or len(route.data.splines[0].points) != 12 or route_distance() != 800.0:
        errors.append("canonical route must contain 12 points and total exactly 800m")
    if len([obj for obj in objects if obj.get("asset_kind") == "route_segment"]) != 4:
        errors.append("exactly four authorized route segments are required")
    if len([obj for obj in objects if obj.get("asset_kind") == "shortcut"]) != 2:
        errors.append("exactly two authorized step-free shortcuts are required")

    anchors = {obj.get("destination_id"): (obj.get("anchor_x_m"), obj.get("anchor_y_m")) for obj in objects if obj.get("asset_kind") == "destination_anchor"}
    if anchors != DESTINATIONS:
        errors.append(f"destination anchors differ: {anchors}")

    shells = [obj for obj in objects if obj.get("asset_kind") == "scenic_shell"]
    family_counts = {family: sum(obj.get("family") == family for obj in shells) for family in ("limestone", "terracotta", "charcoal")}
    if len(shells) != 10 or family_counts != {"limestone": 4, "terracotta": 3, "charcoal": 3}:
        errors.append(f"scenic ceiling/families differ: count={len(shells)}, families={family_counts}")
    for name, _family, (x, y), (width, depth), stories in SCENIC_SHELLS:
        if stories < 3 or stories > 6:
            errors.append(f"{name} stories outside 3-6")
        if not (-155.0 <= x - width / 2.0 and x + width / 2.0 <= 185.0 and -50.0 <= y - depth / 2.0 and y + depth / 2.0 <= 230.0):
            errors.append(f"{name} outside 340x280m district")
        if aabb_intersects_route(x, y, width, depth):
            errors.append(f"{name} enters the route plus 2m review clearance")

    render_files = sorted(RENDER_DIR.glob("*.png"))
    if [path.name for path in render_files] != sorted(view[0] for view in VIEWS):
        errors.append(f"expected exactly four named render outputs, found {[path.name for path in render_files]}")
    if BLEND_PATH.with_suffix(".blend1").exists():
        errors.append("Blender backup output is forbidden; keep exactly one review source")
    if sum(view[1] == "top_down" for view in VIEWS) != 1 or sum(view[1] == "eye_level" for view in VIEWS) != 3:
        errors.append("review board requires exactly one top-down and three eye-level views")
    if any(abs(view[2][2] - 1.7) > 0.001 for view in VIEWS if view[1] == "eye_level"):
        errors.append("all eye-level cameras must stay at the approved 1.7m observer height")
    if bpy.context.scene.render.engine != "BLENDER_EEVEE_NEXT":
        errors.append(f"review engine must be Eevee, found {bpy.context.scene.render.engine}")
    if bpy.data.libraries or [image for image in bpy.data.images if image.name not in {"Render Result", "Viewer Node"}]:
        errors.append("external libraries/images are forbidden")
    if [obj for obj in objects if obj.get("asset_kind") == "character"]:
        errors.append("production character geometry is forbidden")
    if require_manifest and not MANIFEST_PATH.exists():
        errors.append("manifest.json is missing")
    if errors:
        raise RuntimeError("\n".join(errors))
    print("ODDSWELL_SUNDALE_MASSING_VALIDATION|result=PASS|district=340x280m|commons=140x90m|route=800m|route_points=12|route_segments=4|shortcuts=2|destinations=7|scenic=10|families=4,3,3|views=1_top+3_eye|eye_height_m=1.7|engine=eevee|cycles=false|external_refs=0")
    return family_counts


def write_manifest(family_counts):
    renders = []
    for filename, view_type, location, target, _ortho in VIEWS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}",
            "view_type": view_type,
            "camera_location_m": location,
            "target_m": target,
            "width": RENDER_SIZE[0],
            "height": RENDER_SIZE[1] if view_type == "top_down" else EYE_RENDER_HEIGHT,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "phase": "Phase 1L.3a",
        "status": "noncanonical_owner_review",
        "engine": "BLENDER_EEVEE_NEXT",
        "cycles": False,
        "source_authority": {
            "unreal_map": "/Game/Maps/SundaleGraybox",
            "unreal_map_sha256": "180B31BA097EE6AF6C059854C0689F698A9200036C334284A6CF9A5FC1E8C015",
            "authored_actor_count": 45,
            "district_m": [340.0, 280.0],
            "commons_m": [140.0, 90.0],
            "route_m": 800.0,
            "route_points_m": ROUTE_POINTS,
            "route_segments": 4,
            "shortcuts": 2,
            "destinations": DESTINATIONS,
        },
        "existing_authorized": {
            "massing_objects": [item[0] for item in EXISTING_MASSING],
            "destination_count": 7,
        },
        "proposed_scenic": {
            "shell_ceiling": 10,
            "family_counts": family_counts,
            "shells": [
                {"id": name, "family": family, "center_m": center, "footprint_m": footprint, "stories": stories, "status": "PROPOSED_SCENIC", "nonenterable": True}
                for name, family, center, footprint, stories in SCENIC_SHELLS
            ],
        },
        "renders": renders,
        "external_references": [],
        "limitations": [
            "not production Unreal geometry",
            "not approved scenic placement or roofline",
            "not final art, materials, lighting, readability, accessibility, usability, performance, or readiness evidence",
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
        family_counts = validate_scene(require_manifest=False)
        write_manifest(family_counts)
    else:
        family_counts = validate_scene(require_manifest=True)
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if manifest["proposed_scenic"]["family_counts"] != family_counts:
            raise RuntimeError("manifest scenic counts differ from the Blend")
        for render in manifest["renders"]:
            path = ROOT / render["file"]
            if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
                raise RuntimeError(f"render hash differs: {path.name}")
        print("ODDSWELL_SUNDALE_MASSING_FOCUSED|result=PASS|manifest=true|render_hashes=4|manual_input=false")


if __name__ == "__main__":
    main()
