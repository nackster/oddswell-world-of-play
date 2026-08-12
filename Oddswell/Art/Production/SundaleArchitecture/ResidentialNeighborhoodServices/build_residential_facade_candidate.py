"""Build and verify the bounded Sundale residential-facade production candidate."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
ASSET_ID = "SM_Sundale_ResidentialFacade_A"
BLEND = ROOT / f"{ASSET_ID}.blend"
FBX = ROOT / f"{ASSET_ID}.fbx"
CONTACT = ROOT / "renders" / f"{ASSET_ID}_ContactSheet.png"
MANIFEST = ROOT / "manifest.json"
PROVENANCE = ROOT / "PROVENANCE.md"
STATUS = "PRODUCTION_CANDIDATE_NOT_INTEGRATED"

PALETTE = {
    "warm_limestone": (0xD8 / 255, 0xC8 / 255, 0xA9 / 255, 1.0),
    "muted_terracotta": (0xA6 / 255, 0x5F / 255, 0x47 / 255, 1.0),
    "sand_concrete": (0xB9 / 255, 0xA7 / 255, 0x83 / 255, 1.0),
    "charcoal_gray": (0x4D / 255, 0x50 / 255, 0x51 / 255, 1.0),
}
PALETTE_HEX = {
    "warm_limestone": "#D8C8A9",
    "muted_terracotta": "#A65F47",
    "sand_concrete": "#B9A783",
    "charcoal_gray": "#4D5051",
}
ROLES = (
    ("MASS", "warm_limestone", (0.0, 0.20, 2.25), (5.20, 3.70, 4.50)),
    ("OPAQUE_BAY_01", "charcoal_gray", (-1.60, -1.74, 2.30), (1.10, 0.18, 1.70)),
    ("OPAQUE_BAY_02", "charcoal_gray", (0.00, -1.74, 2.30), (1.10, 0.18, 1.70)),
    ("OPAQUE_BAY_03", "charcoal_gray", (1.60, -1.74, 2.30), (1.10, 0.18, 1.70)),
    ("PARAPET_ACCENT", "muted_terracotta", (0.0, 0.20, 4.75), (5.20, 3.70, 0.50)),
    ("SHALLOW_BALCONY_01", "muted_terracotta", (-1.55, -1.85, 3.45), (1.45, 0.40, 0.18)),
    ("SHALLOW_BALCONY_02", "muted_terracotta", (1.55, -1.85, 3.45), (1.45, 0.40, 0.18)),
    ("STOOP", "sand_concrete", (0.0, -1.85, 0.11), (1.40, 0.40, 0.22)),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def normalize_fbx_timestamp(path: Path) -> None:
    """Remove the only time-varying FBX bytes while retaining a valid fixed timestamp."""
    data = bytearray(path.read_bytes())
    values = {"Year": 2026, "Month": 1, "Day": 1, "Hour": 0, "Minute": 0, "Second": 0, "Millisecond": 0}
    for name, value in values.items():
        marker = name.encode("ascii") + b"I"
        offset = data.find(marker, 0, 1024)
        assert offset >= 0
        struct.pack_into("<i", data, offset + len(marker), value)
    path.write_bytes(data)


def clear() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for block in list(blocks):
            blocks.remove(block)


def box_geometry(center: tuple[float, float, float], size: tuple[float, float, float]):
    cx, cy, cz = center
    sx, sy, sz = (value / 2 for value in size)
    vertices = [
        (cx - sx, cy - sy, cz - sz),
        (cx + sx, cy - sy, cz - sz),
        (cx + sx, cy + sy, cz - sz),
        (cx - sx, cy + sy, cz - sz),
        (cx - sx, cy - sy, cz + sz),
        (cx + sx, cy - sy, cz + sz),
        (cx + sx, cy + sy, cz + sz),
        (cx - sx, cy + sy, cz + sz),
    ]
    faces = (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    )
    return vertices, faces


def build_asset() -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    face_roles: list[int] = []
    face_colors: list[tuple[float, float, float, float]] = []
    for role_index, (_role, color_name, center, size) in enumerate(ROLES):
        box_vertices, box_faces = box_geometry(center, size)
        offset = len(vertices)
        vertices.extend(box_vertices)
        faces.extend(tuple(offset + index for index in face) for face in box_faces)
        face_roles.extend([role_index] * len(box_faces))
        face_colors.extend([PALETTE[color_name]] * len(box_faces))

    mesh = bpy.data.meshes.new(ASSET_ID)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(ASSET_ID, mesh)
    bpy.context.collection.objects.link(obj)

    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        for loop_index, value in zip(polygon.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[loop_index].uv = value

    colors = mesh.color_attributes.new(name="PaletteColor", type="FLOAT_COLOR", domain="CORNER")
    for polygon, color in zip(mesh.polygons, face_colors):
        for loop_index in polygon.loop_indices:
            colors.data[loop_index].color = color

    role_attribute = mesh.attributes.new(name="role_index", type="INT", domain="FACE")
    for datum, role_index in zip(role_attribute.data, face_roles):
        datum.value = role_index

    material = bpy.data.materials.new(name="M_Sundale_ResidentialFacade_VertexColor")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    vertex_color = nodes.new("ShaderNodeVertexColor")
    vertex_color.layer_name = "PaletteColor"
    material.node_tree.links.new(vertex_color.outputs["Color"], shader.inputs["Base Color"])
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    obj.data.materials.append(material)
    return obj


def asset_facts(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data
    mesh.calc_loop_triangles()
    bounds = [
        round(max(vertex.co[i] for vertex in mesh.vertices) - min(vertex.co[i] for vertex in mesh.vertices), 6)
        for i in range(3)
    ]
    role_counts = {role: sum(1 for item in ROLES if item[0].startswith(role)) for role in (
        "MASS", "OPAQUE_BAY", "PARAPET_ACCENT", "SHALLOW_BALCONY", "STOOP"
    )}
    facts = {
        "bounds_m": bounds,
        "material_slots": len(obj.material_slots),
        "triangles": len(mesh.loop_triangles),
        "uv_channels": len(mesh.uv_layers),
        "vertices": len(mesh.vertices),
        "role_counts": role_counts,
        "vertex_color_attribute": mesh.color_attributes.active_color_name,
    }
    assert obj.name == ASSET_ID and mesh.name == ASSET_ID
    assert tuple(round(value, 6) for value in obj.location) == (0.0, 0.0, 0.0)
    assert tuple(round(value, 6) for value in obj.rotation_euler) == (0.0, 0.0, 0.0)
    assert tuple(round(value, 6) for value in obj.scale) == (1.0, 1.0, 1.0)
    assert facts["bounds_m"] == [5.2, 4.1, 5.0]
    assert facts["triangles"] == 96
    assert facts["uv_channels"] == 1 and facts["material_slots"] == 1
    assert facts["vertex_color_attribute"] == "PaletteColor"
    assert facts["role_counts"] == {
        "MASS": 1,
        "OPAQUE_BAY": 3,
        "PARAPET_ACCENT": 1,
        "SHALLOW_BALCONY": 2,
        "STOOP": 1,
    }
    assert len(bpy.data.libraries) == 0
    return facts


def save_and_export(obj: bpy.types.Object) -> dict[str, str]:
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), check_existing=False)
    blend_first = sha256(BLEND)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    export_args = dict(
        filepath=str(FBX),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Y",
        axis_up="Z",
        path_mode="STRIP",
        embed_textures=False,
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        colors_type="SRGB",
        bake_anim=False,
    )
    bpy.ops.export_scene.fbx(**export_args)
    normalize_fbx_timestamp(FBX)
    fbx_first = sha256(FBX)
    bpy.ops.export_scene.fbx(**export_args)
    normalize_fbx_timestamp(FBX)
    fbx_second = sha256(FBX)
    assert fbx_first == fbx_second
    blend_second = sha256(BLEND)
    assert blend_first == blend_second
    return {
        "blend_first": blend_first,
        "blend_second": blend_second,
        "fbx_first": fbx_first,
        "fbx_second": fbx_second,
    }


def solid_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.8
    return material


def label_material(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 1.0
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def text_object(body: str, location: tuple[float, float, float], size: float, material, align="CENTER"):
    curve = bpy.data.curves.new(name=f"TXT_{body[:20]}", type="FONT")
    curve.body = body
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.002
    obj = bpy.data.objects.new(curve.name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0.0, 0.0)
    obj.data.materials.append(material)
    return obj


def render_contact_sheet(source: bpy.types.Object) -> None:
    CONTACT.parent.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 3200
    scene.render.resolution_y = 1800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(CONTACT)
    scene.render.film_transparent = False

    dark = solid_material("BoardDark", (0.025, 0.035, 0.045, 1.0))
    white = label_material("BoardWhite", (0.96, 0.98, 1.0, 1.0))
    terracotta = label_material("BoardTerracotta", (0.95, 0.55, 0.40, 1.0))
    sand = label_material("BoardSand", (0.90, 0.80, 0.65, 1.0))

    bpy.ops.mesh.primitive_cube_add(location=(0.0, 3.5, 0.0), scale=(16.0, 0.1, 9.0))
    background = bpy.context.object
    background.name = "CONTACT_SHEET_BACKGROUND"
    background.data.materials.append(dark)

    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.018, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    for location, energy, size in (((-10, -10, 12), 1800, 10), ((12, -5, 4), 1200, 8)):
        light_data = bpy.data.lights.new(name=f"ContactLight{len(bpy.data.lights)}", type="AREA")
        light_data.energy = energy
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(light_data.name, light_data)
        bpy.context.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (math.radians(70), 0, math.radians(-20))

    centers = ((-9.4, 4.15), (0.0, 4.15), (9.4, 4.15), (-9.4, -2.55), (0.0, -2.55), (9.4, -2.55))
    views = (
        ("FRONT", (0, 0, 0)),
        ("REAR", (0, 0, math.pi)),
        ("LEFT", (0, 0, math.pi / 2)),
        ("RIGHT", (0, 0, -math.pi / 2)),
        ("TOP", (-math.pi / 2, 0, 0)),
        ("PERSPECTIVE", (math.radians(-16), 0, math.radians(-28))),
    )
    source.hide_render = True
    for (label, rotation), (x, z) in zip(views, centers):
        obj = source.copy()
        obj.data = source.data.copy()
        bpy.context.collection.objects.link(obj)
        obj.name = f"CONTACT_{label}"
        obj.hide_render = False
        obj.location = (x, 0.0, z - 2.0)
        obj.rotation_euler = rotation
        obj.scale = (0.68, 0.68, 0.68)
        text_object(label, (x, -10.0, z + 1.95), 0.52, terracotta)
        text_object("5.2 x 4.1 x 5.0 m  |  96 tris", (x, -10.0, z - 4.18), 0.27, white)

    text_object(ASSET_ID, (0.0, -10.0, 8.15), 0.58, white)
    text_object("RESIDENTIAL / NEIGHBORHOOD SERVICES  |  PRODUCTION CONTACT SHEET", (0.0, -10.0, 7.36), 0.26, sand)
    ledger = (
        "1 UV  |  1 vertex-color material slot  |  warm limestone  |  muted terracotta  |  sand concrete  |  charcoal gray\n"
        "Original Blender-native geometry  |  no external references  |  source: FACADE_SAMPLE__RESIDENTIAL_NEIGHBORHOOD_SERVICES\n"
        f"STATUS: {STATUS}"
    )
    text_object(ledger, (0.0, -10.0, -7.82), 0.27, white)

    camera_data = bpy.data.cameras.new("ContactSheetCamera")
    camera = bpy.data.objects.new("ContactSheetCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, -36.0, 0.0)
    camera.rotation_euler = (math.radians(90), 0.0, 0.0)
    camera_data.type = "ORTHO"
    # Blender's horizontal sensor fit makes ortho_scale the 32 m board width.
    camera_data.sensor_fit = "HORIZONTAL"
    camera_data.ortho_scale = 32.0
    scene.camera = camera
    bpy.ops.render.render(write_still=True)


def write_manifest(facts: dict[str, object], repeated: dict[str, str]) -> None:
    manifest = {
        "asset_id": ASSET_ID,
        "status": STATUS,
        "phase": "Phase 1L.4a",
        "accepted_sample_source": "FACADE_SAMPLE__RESIDENTIAL_NEIGHBORHOOD_SERVICES",
        "district_id": "RESIDENTIAL_NEIGHBORHOOD_SERVICES",
        "geometry": facts,
        "palette": PALETTE_HEX,
        "role_ledger": [
            {"role": role, "palette": color, "center_m": center, "dimensions_m": size}
            for role, color, center, size in ROLES
        ],
        "material_contract": {
            "material": "M_Sundale_ResidentialFacade_VertexColor",
            "slots": 1,
            "vertex_color_attribute": "PaletteColor",
            "external_images": [],
        },
        "files": {
            "blend": {"file": BLEND.name, "bytes": BLEND.stat().st_size, "sha256": sha256(BLEND)},
            "fbx": {"file": FBX.name, "bytes": FBX.stat().st_size, "sha256": sha256(FBX)},
            "contact_sheet": {"file": CONTACT.relative_to(ROOT).as_posix(), "bytes": CONTACT.stat().st_size, "sha256": sha256(CONTACT), "width": 3200, "height": 1800},
            "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
        },
        "repeatability": repeated,
        "external_references": [],
        "frameworks": [],
        "production_authority": {
            "integrated_in_unreal": False,
            "production_map_changed": False,
            "runtime_or_gameplay_changed": False,
            "asset_family_expansion_authorized": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def validate_saved() -> None:
    obj = bpy.data.objects.get(ASSET_ID)
    assert obj is not None and obj.type == "MESH"
    facts = asset_facts(obj)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == STATUS
    assert manifest["geometry"] == facts
    assert manifest["files"]["blend"]["sha256"] == sha256(BLEND)
    assert manifest["files"]["fbx"]["sha256"] == sha256(FBX)
    assert manifest["files"]["contact_sheet"]["sha256"] == sha256(CONTACT)
    assert manifest["external_references"] == [] and len(bpy.data.libraries) == 0
    print(json.dumps({"status": "PASS", "asset_id": ASSET_ID, **facts}, sort_keys=True))


def main() -> None:
    if "--validate-saved" in sys.argv:
        validate_saved()
        return
    clear()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    asset = build_asset()
    facts = asset_facts(asset)
    repeated = save_and_export(asset)
    render_contact_sheet(asset)
    write_manifest(facts, repeated)
    print(json.dumps({"status": "PASS", "asset_id": ASSET_ID, **facts}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"{ASSET_ID} build failed: {error}", file=sys.stderr)
        raise
