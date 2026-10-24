"""Deterministic Phase 1L.3i starter-item shape-language review builder."""

import hashlib
import json
import math
import struct
import sys
from collections import Counter
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
BLEND_PATH = ROOT / "SundaleStarterItemShapeLanguageReviewSheet.blend"
MANIFEST_PATH = ROOT / "manifest.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

ITEMS = (
    {
        "item_id": "sundale_signal_jacket",
        "display_name": "Sundale Signal Jacket",
        "category": "clothing",
        "origin_city": "Sundale",
        "slot": "outfit",
        "price_odds_bucks": 60,
        "colors_rgba": ((0.12, 0.18, 0.22, 1.0), (0.08, 0.72, 0.68, 1.0)),
        "proxy_id": "PROXY__SUNDALE_SIGNAL_JACKET",
        "dimensions_m": (0.72, 0.24, 0.84),
    },
    {
        "item_id": "sundale_modular_chair",
        "display_name": "Sundale Modular Chair",
        "category": "furniture",
        "origin_city": "Sundale",
        "snap_point_id": "studio_primary",
        "price_odds_bucks": 100,
        "colors_rgba": ((0.22, 0.25, 0.28, 1.0), (0.08, 0.72, 0.68, 1.0)),
        "proxy_id": "PROXY__MODULAR_CHAIR",
        "dimensions_m": (0.72, 0.72, 1.0),
    },
)
ITEM_BY_ID = {item["item_id"]: item for item in ITEMS}
ITEM_IDS = tuple(ITEM_BY_ID)
TRIANGLE_CEILING = 1500
MATERIAL_SLOTS_PER_PROXY = 2
UV_CHANNELS_PER_PROXY = 1
PRESENTATION_ENVELOPES = ("CharacterPresentationMasculine", "CharacterPresentationFeminine")
JACKET_REVIEW_FIT_TRANSFORM = {
    "garment_local_dimensions_m": [0.72, 0.24, 0.84],
    "garment_local_location_m": [0.0, 0.0, 1.21],
    "garment_local_rotation_deg": [0.0, 0.0, 0.0],
}
CONTACT_VIEWS = ("FRONT", "REAR", "LEFT", "RIGHT", "TOP", "PERSPECTIVE")
OUTPUTS = (
    ("Unified_StarterItemShapeLanguage.png", "UNIFIED", None),
    ("ContactSheet_SundaleSignalJacket.png", "CONTACT_SHEET", "sundale_signal_jacket"),
    ("ContactSheet_SundaleModularChair.png", "CONTACT_SHEET", "sundale_modular_chair"),
)
NODE_ALLOWLIST = {"ShaderNodeOutputMaterial", "ShaderNodeBsdfPrincipled"}
SOURCE_CONTRACT = (
    {
        "file": "client/OddsWell/Source/OddsWell/OddsBucksLedger.cpp",
        "sha256": "4281F9F9418ADCBBBA72EC8BD1C9107C5DA82D9D53A5134C5009B6D00C65C0B7",
        "lines": {
            31: "constexpr int64 SignalJacketPrice = 60;",
            32: "constexpr int64 ModularChairPrice = 100;",
            47: 'const FString SignalJacketItemId(TEXT("sundale_signal_jacket"));',
            49: 'const FString ModularChairItemId(TEXT("sundale_modular_chair"));',
        },
    },
    {
        "file": "client/OddsWell/Source/OddsWell/PlaceholderLocomotion.cpp",
        "sha256": "22E7B6FEED0E14DC23A8A900FB58E280606F9F9160ED3FE6F23D1460B99FE298",
        "lines": {
            81: "const FLinearColor SignalJacketSlate(0.12f, 0.18f, 0.22f);",
            82: "const FLinearColor SignalJacketTeal(0.08f, 0.72f, 0.68f);",
            123: 'const FName StudioPrimarySnapPointId(TEXT("studio_primary"));',
            124: "const FLinearColor ModularChairGray(0.22f, 0.25f, 0.28f);",
            125: "const FLinearColor ModularChairTeal(0.08f, 0.72f, 0.68f);",
        },
    },
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def material(name, color, item_id, role):
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    result["item_id"] = item_id
    result["material_role"] = role
    nodes = result.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.62
    if role in {"TEXT", "ACCENT"}:
        principled.inputs["Emission Color"].default_value = color
        principled.inputs["Emission Strength"].default_value = 0.8
    result.node_tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return result


def add_box(name, dimensions, location, materials, item_id="", role="REVIEW_SUPPORT", collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for assigned in materials:
        obj.data.materials.append(assigned)
    obj["item_id"] = item_id
    obj["asset_role"] = role
    obj["external_reference"] = False
    obj["image_texture"] = False
    obj["brand"] = False
    obj["catalog_addition"] = False
    obj["interior"] = False
    obj["gameplay"] = False
    if collection:
        for existing in list(obj.users_collection):
            existing.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def add_shape_proxy(item, location, materials, collection):
    """Create one disconnected low-poly mesh; each tuple is a native box part."""
    if item["item_id"] == "sundale_signal_jacket":
        parts = (
            ((0.0, 0.0, 0.46), (0.48, 0.24, 0.64), 0),
            ((-0.30, 0.0, 0.44), (0.12, 0.18, 0.68), 0),
            ((0.30, 0.0, 0.44), (0.12, 0.18, 0.68), 0),
            ((0.0, 0.0, 0.74), (0.60, 0.24, 0.20), 0),
            ((0.0, -0.115, 0.08), (0.48, 0.01, 0.16), 1),
            ((0.0, -0.115, 0.44), (0.04, 0.01, 0.56), 1),
            ((-0.08, -0.115, 0.80), (0.12, 0.01, 0.08), 1),
            ((0.08, -0.115, 0.80), (0.12, 0.01, 0.08), 1),
        )
    else:
        parts = (
            ((0.0, 0.0, 0.48), (0.72, 0.72, 0.12), 0),
            ((0.0, 0.30, 0.75), (0.72, 0.12, 0.50), 0),
            ((-0.28, -0.27, 0.22), (0.10, 0.10, 0.44), 0),
            ((0.28, -0.27, 0.22), (0.10, 0.10, 0.44), 0),
            ((-0.28, 0.27, 0.22), (0.10, 0.10, 0.44), 0),
            ((0.28, 0.27, 0.22), (0.10, 0.10, 0.44), 0),
            ((0.0, -0.02, 0.56), (0.60, 0.56, 0.08), 1),
            ((0.0, 0.235, 0.77), (0.60, 0.01, 0.36), 1),
        )
    vertices = []
    faces = []
    material_indices = []
    corners = ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
               (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))
    box_faces = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7))
    for center, dimensions, material_index in parts:
        offset = len(vertices)
        vertices.extend(tuple(center[axis] + sign[axis] * dimensions[axis] / 2.0 for axis in range(3)) for sign in corners)
        faces.extend(tuple(offset + vertex for vertex in face) for face in box_faces)
        material_indices.extend([material_index] * len(box_faces))
    mesh = bpy.data.meshes.new(f"{item['proxy_id']}__MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    for assigned in materials:
        mesh.materials.append(assigned)
    mesh.uv_layers.new(name="UV0")
    for polygon, material_index in zip(mesh.polygons, material_indices):
        polygon.material_index = material_index
    obj = bpy.data.objects.new(item["proxy_id"], mesh)
    obj.location = location
    obj["item_id"] = item["item_id"]
    obj["asset_role"] = "CANONICAL_CONCEPT_PROXY"
    obj["external_reference"] = False
    obj["image_texture"] = False
    obj["brand"] = False
    obj["catalog_addition"] = False
    obj["interior"] = False
    obj["gameplay"] = False
    collection.objects.link(obj)
    return obj


def add_text(name, body, location, size, material_value, collection, item_id="", role="REVIEW_TEXT"):
    curve = bpy.data.curves.new(f"{name}__DATA", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.space_line = 0.85
    curve.extrude = 0.004
    curve.materials.append(material_value)
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj["item_id"] = item_id
    obj["asset_role"] = role
    obj["built_in_font_only"] = True
    obj["external_reference"] = False
    collection.objects.link(obj)
    return obj


def triangle_count(obj):
    return sum(len(polygon.vertices) - 2 for polygon in obj.data.polygons)


def mesh_dimensions(obj):
    coordinates = tuple(zip(*(vertex.co[:] for vertex in obj.data.vertices)))
    return tuple(round(max(axis) - min(axis), 6) for axis in coordinates)


def world_bbox_xy(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (min(point.x for point in corners), max(point.x for point in corners),
            min(point.y for point in corners), max(point.y for point in corners))


def boxes_overlap(a, b, margin=0.0):
    return not (a[1] + margin <= b[0] or b[1] + margin <= a[0] or
                a[3] + margin <= b[2] or b[3] + margin <= a[2])


def png_dimensions(path):
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"not a PNG: {path.name}")
        length = struct.unpack(">I", handle.read(4))[0]
        if handle.read(4) != b"IHDR" or length != 13:
            raise RuntimeError(f"missing PNG header: {path.name}")
        return struct.unpack(">II", handle.read(8))


def source_records():
    records = []
    for source in SOURCE_CONTRACT:
        path = REPO / source["file"]
        lines = path.read_text(encoding="utf-8").splitlines()
        actual_hash = sha256(path)
        if actual_hash != source["sha256"]:
            raise RuntimeError(f"production source hash differs: {source['file']}")
        for number, expected in source["lines"].items():
            if lines[number - 1].strip() != expected:
                raise RuntimeError(f"production source line differs: {source['file']}:{number}")
        records.append({
            "file": source["file"], "lines": list(source["lines"]),
            "bytes": path.stat().st_size, "sha256": actual_hash,
        })
    return records


def point_camera(camera, location, target):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def linked_instance(source, name, location, rotation, role, collection, view_name=""):
    obj = source.copy()
    obj.data = source.data
    obj.name = name
    obj.location = location
    obj.rotation_euler = rotation
    obj["asset_role"] = role
    obj["view_name"] = view_name
    obj["new_catalog_identity"] = False
    collection.objects.link(obj)
    return obj


def complete_scene(proxies):
    scene = bpy.context.scene
    geometry = bpy.data.collections["REVIEW_GEOMETRY"]
    labels = bpy.data.collections["REVIEW_LABELS"]
    cameras = bpy.data.collections["REVIEW_CAMERAS"]
    board_material = bpy.data.materials["MAT__BOARD"]
    cell_material = bpy.data.materials["MAT__CELL"]
    text_material = bpy.data.materials["MAT__TEXT"]
    accent_material = bpy.data.materials["MAT__ACCENT"]

    # Presentation scaling changes only the board display; mesh-local dimensions stay exact.
    for proxy in proxies.values():
        proxy.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        proxy.scale = (3.0, 3.0, 3.0)
        proxy["presentation_scale"] = 3.0
    for fit in (obj for obj in geometry.objects if obj.get("asset_role") == "JACKET_FIT_INSTANCE"):
        fit.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        fit.scale = (1.5, 1.5, 1.5)
        fit["presentation_rotation_x_deg"] = 90.0
        fit["presentation_scale"] = 1.5

    view_rotations = {
        "FRONT": (math.radians(90.0), 0.0, 0.0),
        "REAR": (math.radians(90.0), 0.0, math.radians(180.0)),
        "LEFT": (math.radians(90.0), 0.0, math.radians(90.0)),
        "RIGHT": (math.radians(90.0), 0.0, math.radians(-90.0)),
        "TOP": (0.0, 0.0, 0.0),
        "PERSPECTIVE": (math.radians(58.0), math.radians(12.0), math.radians(-35.0)),
    }
    contact_origins = {"sundale_signal_jacket": 30.0, "sundale_modular_chair": 60.0}
    cells = ((-7.0, 2.1), (0.0, 2.1), (7.0, 2.1), (-7.0, -2.1), (0.0, -2.1), (7.0, -2.1))
    for item_id, origin_x in contact_origins.items():
        item = ITEM_BY_ID[item_id]
        add_box(f"CONTACT_BOARD__{item_id}", (22.0, 12.0, 0.08), (origin_x, 0.0, -0.08), (board_material,), collection=geometry)
        add_text(f"CONTACT_TITLE__{item_id}", f"{item['display_name'].upper()} | ID: {item_id} | PRICE: {item['price_odds_bucks']} ODDS BUCKS", (origin_x, 5.35, 0.15), 0.30, text_material, labels, item_id, "CONTACT_TITLE")
        for (x, y), view_name in zip(cells, CONTACT_VIEWS):
            cell = add_box(f"CONTACT_CELL__{item_id}__{view_name}", (6.6, 3.9, 0.04), (origin_x + x, y, 0.01), (cell_material,), item_id, "CONTACT_CELL", geometry)
            cell["view_name"] = view_name
            instance = linked_instance(
                proxies[item_id], f"CONTACT_INSTANCE__{item_id}__{view_name}",
                (origin_x + x, y + 0.45, 0.56), view_rotations[view_name], "CONTACT_VIEW_INSTANCE", geometry, view_name,
            )
            instance.scale = (1.35, 1.35, 1.35)
            dims = " x ".join(f"{value:.2f}" for value in item["dimensions_m"])
            body = f"{view_name}\n{dims} m | {triangle_count(proxies[item_id])} TRIS\n2 SLOTS | 1 UV | NONCANONICAL REVIEW"
            label = add_text(f"CONTACT_LABEL__{item_id}__{view_name}", body, (origin_x + x, y - 1.36, 0.15), 0.15, text_material, labels, item_id, "CONTACT_VIEW_LABEL")
            label["view_name"] = view_name
        add_text(f"CONTACT_FOOTER__{item_id}", "NATIVE GEOMETRY + MATERIALS + BUILT-IN TEXT | EXTERNAL 0 | IMAGE TEXTURES 0 | EXTERNAL FONTS 0 | BRANDS 0", (origin_x, -5.35, 0.15), 0.18, accent_material, labels, item_id, "CONTACT_FOOTER")

    for filename, role, item_id in OUTPUTS:
        camera_data = bpy.data.cameras.new(f"CAMERA_DATA__{Path(filename).stem}")
        camera_data.type = "ORTHO"
        camera_data.ortho_scale = 24.5
        camera = bpy.data.objects.new(f"CAMERA__{Path(filename).stem}", camera_data)
        target_x = 0.0 if role == "UNIFIED" else contact_origins[item_id]
        point_camera(camera, (target_x, 0.0, 22.0), (target_x, 0.0, 0.0))
        camera["view_role"] = role
        camera["item_id"] = item_id or ""
        cameras.objects.link(camera)

    for index, target_x in enumerate((0.0, 30.0, 60.0)):
        bpy.ops.object.light_add(type="AREA", location=(target_x, -2.0, 14.0))
        key = bpy.context.object
        key.name = f"LIGHT__KEY__{index}"
        key.data.energy = 1100.0
        key.data.shape = "RECTANGLE"
        key.data.size = 18.0
        point_camera(key, key.location, (target_x, 0.0, 0.0))


def render_all():
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    for filename, _role, _item_id in OUTPUTS:
        scene.camera = bpy.data.objects[f"CAMERA__{Path(filename).stem}"]
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(RENDER_DIR / filename)
        bpy.ops.render.render(write_still=True)


def write_provenance():
    PROVENANCE_PATH.write_text(
        "# Sundale Starter-Item Shape-Language Review Provenance\n\n"
        "- Phase: `Phase 1L.3i`\n"
        "- Status: noncanonical owner review only\n"
        "- Builder: `build_sundale_starter_item_shape_language.py`\n"
        "- Catalog identities: existing `sundale_signal_jacket` and `sundale_modular_chair` only\n"
        "- Geometry/material/text: Blender-native only; exactly one linked concept mesh and two native material slots per identity\n"
        "- Jacket fit: linked instances reuse both Phase 1L.3g presentation-envelope IDs; one identical garment-local transform is a new review-fit contract, not pre-existing Phase 1L.3g production data\n"
        "- External references, source images, image textures, external fonts, brands, catalog additions, interiors, and gameplay: none\n"
        "- Client, map, runtime, config, tests, package, prior review artifacts, and Phase 1K: unchanged\n\n"
        "The proxies are shape-language review evidence, not production assets, final art, placement, fit/deformation proof, furniture interaction, or readiness authority.\n",
        encoding="utf-8",
    )


def write_manifest(triangles):
    renders = []
    for filename, role, item_id in OUTPUTS:
        path = RENDER_DIR / filename
        renders.append({
            "file": f"renders/{filename}", "role": role, "item_id": item_id,
            "width": 1920, "height": 1080, "bytes": path.stat().st_size, "sha256": sha256(path),
            "full_framing_validated": True,
            "contact_views": list(CONTACT_VIEWS) if role == "CONTACT_SHEET" else [],
        })
    manifest = {
        "phase": "Phase 1L.3i Sundale starter-item shape-language review sheet",
        "status": "noncanonical_owner_review",
        "engine": "BLENDER_EEVEE_NEXT",
        "contract": {
            "item_ids": list(ITEM_IDS), "item_count": 2, "one_concept_proxy_mesh_per_item": True,
            "triangle_counts": triangles, "triangle_ceiling_per_proxy": TRIANGLE_CEILING,
            "native_material_slots_per_proxy": 2, "uv_channels_per_proxy": 1,
            "jacket_fit_presentation_envelope_ids": list(PRESENTATION_ENVELOPES),
            "jacket_review_fit_local_transform": JACKET_REVIEW_FIT_TRANSFORM,
            "preexisting_garment_transform_claimed": False,
            "jacket_fit_instance_count": 2, "new_catalog_identities": 0,
            "contact_views": list(CONTACT_VIEWS), "contact_view_count_per_item": 6,
            "contact_cell_count_per_item": 6, "projected_frame_safe": True,
            "projected_item_label_overlap_count": 0, "projected_cell_overlap_count": 0,
            "text_cell_contrast_ratio_minimum": 4.5,
            "required_contact_annotation": ["dimensions", "triangles", "material_slots", "uv_channels", "NONCANONICAL REVIEW"],
            "node_allowlist": sorted(NODE_ALLOWLIST), "native_geometry_material_text_only": True,
            "external_references": 0, "source_images": 0, "image_textures": 0, "external_fonts": 0,
            "brands": 0, "catalog_additions": 0, "interiors": 0, "gameplay_changes": 0,
        },
        "items": ITEMS,
        "production_sources": source_records(),
        "renders": renders,
        "production_authority_preserved": {
            "client_changed": False, "map_changed": False, "runtime_changed": False,
            "config_changed": False, "tests_changed": False, "package_changed": False,
            "prior_review_artifacts_changed": False, "phase_1k_waived": False,
        },
        "files": {
            "blend": {"file": BLEND_PATH.name, "bytes": BLEND_PATH.stat().st_size, "sha256": sha256(BLEND_PATH)},
            "script": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "lfs": {"blend_required": True, "pattern": "*.blend filter=lfs"},
        "limitations": [
            "review proxies only, not production assets or final art",
            "no deformation, accessibility, performance, interaction, placement, collision, or readiness claim",
            "owner acceptance and a separate production promotion/expansion gate remain required",
            "no roadmap Phase 2 or Version 1 authority",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(triangles):
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    contract = manifest.get("contract", {})
    if contract.get("item_ids") != list(ITEM_IDS) or contract.get("item_count") != 2 or contract.get("triangle_counts") != triangles:
        raise RuntimeError("manifest identity/triangle contract differs")
    if contract.get("triangle_ceiling_per_proxy") != 1500 or contract.get("native_material_slots_per_proxy") != 2 or contract.get("uv_channels_per_proxy") != 1:
        raise RuntimeError("manifest proxy ceiling/slot/UV contract differs")
    if contract.get("jacket_fit_presentation_envelope_ids") != list(PRESENTATION_ENVELOPES) or contract.get("jacket_review_fit_local_transform") != JACKET_REVIEW_FIT_TRANSFORM or contract.get("preexisting_garment_transform_claimed") is not False or contract.get("jacket_fit_instance_count") != 2 or contract.get("new_catalog_identities") != 0:
        raise RuntimeError("manifest jacket-fit reuse contract differs")
    if contract.get("contact_views") != list(CONTACT_VIEWS) or contract.get("contact_view_count_per_item") != 6:
        raise RuntimeError("manifest six-view contract differs")
    if contract.get("contact_cell_count_per_item") != 6 or contract.get("projected_frame_safe") is not True or contract.get("projected_item_label_overlap_count") != 0 or contract.get("projected_cell_overlap_count") != 0 or contract.get("text_cell_contrast_ratio_minimum") != 4.5:
        raise RuntimeError("manifest projected layout contract differs")
    if any(contract.get(field) != 0 for field in ("external_references", "source_images", "image_textures", "external_fonts", "brands", "catalog_additions", "interiors", "gameplay_changes")):
        raise RuntimeError("manifest zero boundary differs")
    if len(manifest.get("renders", [])) != 3 or Counter(entry.get("role") for entry in manifest["renders"]) != Counter({"CONTACT_SHEET": 2, "UNIFIED": 1}):
        raise RuntimeError("manifest render contract differs")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"] or png_dimensions(path) != (1920, 1080):
            raise RuntimeError(f"render identity differs: {path.name}")
    for key, path in (("blend", BLEND_PATH), ("script", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"artifact identity differs: {path.name}")
    if manifest.get("production_sources") != source_records():
        raise RuntimeError("production source identity differs")


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("WORLD__REVIEW")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.065, 0.075, 1.0)
    background.inputs["Strength"].default_value = 0.35
    for field in ("external_refs_count", "image_textures_count", "external_fonts_count", "brands_count", "catalog_additions_count", "interiors_count", "gameplay_changes_count"):
        scene[field] = 0
    for field in ("production_client_changed", "production_map_changed", "production_runtime_changed", "production_config_changed", "production_tests_changed", "package_changed", "phase_1k_waived"):
        scene[field] = False
    return scene


def build_scene():
    scene = reset_scene()
    geometry = bpy.data.collections.new("REVIEW_GEOMETRY")
    labels = bpy.data.collections.new("REVIEW_LABELS")
    cameras = bpy.data.collections.new("REVIEW_CAMERAS")
    scene.collection.children.link(geometry)
    scene.collection.children.link(labels)
    scene.collection.children.link(cameras)

    board_material = material("MAT__BOARD", (0.188, 0.220, 0.239, 1.0), "", "BOARD")
    cell_material = material("MAT__CELL", (0.105, 0.130, 0.145, 1.0), "", "BOARD")
    text_material = material("MAT__TEXT", (0.945, 0.906, 0.824, 1.0), "", "TEXT")
    accent_material = material("MAT__ACCENT", (0.08, 0.72, 0.68, 1.0), "", "ACCENT")
    add_box("REVIEW_BOARD", (20.0, 11.0, 0.08), (0.0, 0.0, -0.08), (board_material,), collection=geometry)

    proxies = {}
    for index, item in enumerate(ITEMS):
        primary = material(f"MAT__{item['item_id']}__PRIMARY", item["colors_rgba"][0], item["item_id"], "PRIMARY")
        secondary = material(f"MAT__{item['item_id']}__SECONDARY", item["colors_rgba"][1], item["item_id"], "SECONDARY")
        proxy = add_shape_proxy(
            item, (-3.4 if index == 0 else 3.4, 0.9, item["dimensions_m"][2] / 2.0),
            (primary, secondary), geometry,
        )
        proxy["catalog_identity_reused"] = True
        proxy["price_odds_bucks"] = item["price_odds_bucks"]
        proxy["uv_channel_count"] = UV_CHANNELS_PER_PROXY
        proxies[item["item_id"]] = proxy
        add_text(f"LABEL__{item['item_id']}", f"{item['display_name'].upper()}\nID: {item['item_id']} | PRICE: {item['price_odds_bucks']}\nNONCANONICAL REVIEW", (-3.4 if index == 0 else 3.4, -3.25, 0.15), 0.26, text_material, labels, item["item_id"], "ITEM_IDENTITY_LABEL")

    for index, envelope_id in enumerate(PRESENTATION_ENVELOPES):
        instance = proxies["sundale_signal_jacket"].copy()
        instance.data = proxies["sundale_signal_jacket"].data
        instance.name = f"JACKET_FIT_INSTANCE__{envelope_id}"
        instance.location = (-1.0 + index * 2.0, 3.95, JACKET_REVIEW_FIT_TRANSFORM["garment_local_location_m"][2])
        instance.dimensions = JACKET_REVIEW_FIT_TRANSFORM["garment_local_dimensions_m"]
        instance.rotation_euler = tuple(math.radians(value) for value in JACKET_REVIEW_FIT_TRANSFORM["garment_local_rotation_deg"])
        instance["asset_role"] = "JACKET_FIT_INSTANCE"
        instance["presentation_envelope_id"] = envelope_id
        instance["review_fit_transform_is_new"] = True
        instance["review_fit_local_transform_json"] = json.dumps(JACKET_REVIEW_FIT_TRANSFORM, sort_keys=True)
        instance["new_catalog_identity"] = False
        geometry.objects.link(instance)

    add_text("TITLE", "SUNDALE STARTER ITEM SHAPE LANGUAGE | EXACT 2 EXISTING IDENTITIES | NONCANONICAL REVIEW", (0.0, 5.0, 0.15), 0.31, text_material, labels)
    add_text("FIT_NOTE", "SIGNAL JACKET FIT: BOTH PHASE 1L.3g PRESENTATION ENVELOPES | IDENTICAL NEW REVIEW-FIT LOCAL TRANSFORM", (0.0, 2.5, 0.15), 0.18, accent_material, labels)
    return proxies


def validate_scene(require_outputs=False):
    errors = []
    proxies = [obj for obj in bpy.data.objects if obj.get("asset_role") == "CANONICAL_CONCEPT_PROXY"]
    fits = [obj for obj in bpy.data.objects if obj.get("asset_role") == "JACKET_FIT_INSTANCE"]
    if len(proxies) != 2 or {obj.get("item_id") for obj in proxies} != set(ITEM_IDS):
        errors.append("exactly two existing catalog concept proxies are required")
    for proxy in proxies:
        item = ITEM_BY_ID[proxy.get("item_id")]
        if triangle_count(proxy) > TRIANGLE_CEILING:
            errors.append(f"{proxy.name} exceeds {TRIANGLE_CEILING} triangles")
        if mesh_dimensions(proxy) != item["dimensions_m"]:
            errors.append(f"{proxy.name} mesh-local dimensions differ")
        if len(proxy.data.materials) != MATERIAL_SLOTS_PER_PROXY:
            errors.append(f"{proxy.name} must use exactly two native material slots")
        if proxy.get("uv_channel_count") != UV_CHANNELS_PER_PROXY or len(proxy.data.uv_layers) != UV_CHANNELS_PER_PROXY:
            errors.append(f"{proxy.name} UV contract differs")
        expected_colors = item["colors_rgba"]
        if any(any(abs(material_value.diffuse_color[index] - expected[index]) > 0.000001 for index in range(4)) for material_value, expected in zip(proxy.data.materials, expected_colors)):
            errors.append(f"{proxy.name} exact RGBA contract differs")
    if len(fits) != 2 or {obj.get("presentation_envelope_id") for obj in fits} != set(PRESENTATION_ENVELOPES):
        errors.append("jacket fit must reuse both Phase 1L.3g presentation envelopes")
    if any(obj.data is not bpy.data.objects[ITEM_BY_ID["sundale_signal_jacket"]["proxy_id"]].data for obj in fits):
        errors.append("jacket fit instances must reuse one proxy mesh")
    fit_signature = json.dumps(JACKET_REVIEW_FIT_TRANSFORM, sort_keys=True)
    if any(obj.get("review_fit_transform_is_new") is not True or obj.get("review_fit_local_transform_json") != fit_signature for obj in fits):
        errors.append("jacket review-fit local transforms must be identical and explicitly new")
    for material_value in bpy.data.materials:
        if material_value.use_nodes and not {node.bl_idname for node in material_value.node_tree.nodes} <= NODE_ALLOWLIST:
            errors.append(f"{material_value.name} uses a forbidden node")
    scene = bpy.context.scene
    if any(scene.get(field) != 0 for field in ("external_refs_count", "image_textures_count", "external_fonts_count", "brands_count", "catalog_additions_count", "interiors_count", "gameplay_changes_count")):
        errors.append("zero boundary differs")
    if scene.get("phase_1k_waived") is not False:
        errors.append("Phase 1K may not be waived")
    if bpy.data.libraries or bpy.data.textures or bpy.data.armatures or bpy.data.actions:
        errors.append("external library, texture, rig, or animation datablock is forbidden")
    if any(image.filepath or image.source == "FILE" for image in bpy.data.images):
        errors.append("source images are forbidden")
    if any(font.filepath not in {"", "<builtin>"} for font in bpy.data.fonts):
        errors.append("external fonts are forbidden")
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
    if len(cameras) != 3 or Counter(obj.get("view_role") for obj in cameras) != Counter({"CONTACT_SHEET": 2, "UNIFIED": 1}):
        errors.append("exactly one unified and two contact-sheet cameras are required")
    contact_instances = [obj for obj in bpy.data.objects if obj.get("asset_role") == "CONTACT_VIEW_INSTANCE"]
    if len(contact_instances) != 12 or Counter(obj.get("view_name") for obj in contact_instances) != Counter({view: 2 for view in CONTACT_VIEWS}):
        errors.append("exactly six linked view instances per item are required")
    contact_cells = [obj for obj in bpy.data.objects if obj.get("asset_role") == "CONTACT_CELL"]
    contact_labels = [obj for obj in bpy.data.objects if obj.get("asset_role") == "CONTACT_VIEW_LABEL"]
    if len(contact_cells) != 12 or len(contact_labels) != 12:
        errors.append("exactly one cell and one metadata label per contact view are required")
    bpy.context.view_layer.update()
    for item_id in ITEM_IDS:
        item_cells = [obj for obj in contact_cells if obj.get("item_id") == item_id]
        for first_index, first in enumerate(item_cells):
            for second in item_cells[first_index + 1:]:
                if boxes_overlap(world_bbox_xy(first), world_bbox_xy(second), margin=0.05):
                    errors.append(f"contact cells overlap: {first.name} / {second.name}")
        for view_name in CONTACT_VIEWS:
            cell = next((obj for obj in item_cells if obj.get("view_name") == view_name), None)
            item_display = next((obj for obj in contact_instances if obj.get("item_id") == item_id and obj.get("view_name") == view_name), None)
            label = next((obj for obj in contact_labels if obj.get("item_id") == item_id and obj.get("view_name") == view_name), None)
            if not cell or not item_display or not label:
                continue
            cell_box, item_box, label_box = world_bbox_xy(cell), world_bbox_xy(item_display), world_bbox_xy(label)
            for candidate, candidate_name in ((item_box, "item"), (label_box, "label")):
                if candidate[0] < cell_box[0] + 0.10 or candidate[1] > cell_box[1] - 0.10 or candidate[2] < cell_box[2] + 0.10 or candidate[3] > cell_box[3] - 0.10:
                    errors.append(f"{item_id}/{view_name} {candidate_name} leaves its cell: candidate={candidate}, cell={cell_box}")
            if boxes_overlap(item_box, label_box, margin=0.08):
                errors.append(f"{item_id}/{view_name} item and metadata overlap: item={item_box}, label={label_box}")
    for camera in cameras:
        target_x = 0.0 if camera.get("view_role") == "UNIFIED" else {"sundale_signal_jacket": 30.0, "sundale_modular_chair": 60.0}[camera.get("item_id")]
        half_width, half_height = (10.0, 5.5) if camera.get("view_role") == "UNIFIED" else (11.0, 6.0)
        for corner in ((target_x - half_width, -half_height, 0.0), (target_x + half_width, -half_height, 0.0), (target_x + half_width, half_height, 0.0), (target_x - half_width, half_height, 0.0)):
            projected = world_to_camera_view(scene, camera, Vector(corner))
            if not (0.02 <= projected.x <= 0.98 and 0.02 <= projected.y <= 0.98):
                errors.append(f"{camera.name} board framing differs: projected=({projected.x:.4f},{projected.y:.4f},{projected.z:.4f})")
    text_color = bpy.data.materials["MAT__TEXT"].diffuse_color[:3]
    cell_color = bpy.data.materials["MAT__CELL"].diffuse_color[:3]
    def luminance(color):
        channels = tuple(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in color)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    contrast = (max(luminance(text_color), luminance(cell_color)) + 0.05) / (min(luminance(text_color), luminance(cell_color)) + 0.05)
    if contrast < 4.5:
        errors.append("contact text/cell contrast is below 4.5:1")
    if require_outputs:
        render_names = sorted(path.name for path in RENDER_DIR.glob("*.png")) if RENDER_DIR.exists() else []
        if render_names != sorted(entry[0] for entry in OUTPUTS):
            errors.append("exactly three retained PNGs are required")
        if not BLEND_PATH.exists() or not MANIFEST_PATH.exists() or not PROVENANCE_PATH.exists():
            errors.append("required artifacts are missing")
        if BLEND_PATH.with_suffix(".blend1").exists():
            errors.append("Blender backup output is forbidden")
    if errors:
        raise RuntimeError("\n".join(errors))
    triangles = {obj.get("item_id"): triangle_count(obj) for obj in proxies}
    print(f"ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_VALIDATION|result=PASS|items=2|triangles={triangles}|slots=2|uv=1|external=0|gameplay=0")
    return triangles


def main():
    validate_only = "--validate-only" in sys.argv
    focused = "--focused-validate" in sys.argv
    if validate_only or focused:
        triangles = validate_scene(require_outputs=True)
        validate_manifest(triangles)
        marker = "FOCUSED" if "--focused-validate" in sys.argv else "REOPEN"
        print(f"ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_{marker}|result=PASS|manifest=true|render_hashes=3|manual_input=false")
        return
    proxies = build_scene()
    complete_scene(proxies)
    triangles = validate_scene()
    render_all()
    write_provenance()
    for old_blend in (BLEND_PATH, BLEND_PATH.with_suffix(".blend1")):
        if old_blend.exists():
            old_blend.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    write_manifest(triangles)
    validate_scene(require_outputs=True)
    validate_manifest(triangles)
    print("ODDSWELL_STARTER_ITEM_SHAPE_LANGUAGE_BUILD|result=PASS|artifacts=7|manual_input=false")


if __name__ == "__main__":
    main()
