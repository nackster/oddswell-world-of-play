"""Build and validate the noncanonical Sundale Job canopy pilot."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "SundaleJobCanopy.blend"
OBJECTS = {
    "SM_JobCanopy_Pier": 0.06,
    "SM_JobCanopy_Header": 0.10,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_object(name: str, bevel_width: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name

    bevel = obj.modifiers.new(name="PilotChamfer", type="BEVEL")
    bevel.width = bevel_width
    bevel.segments = 1
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.03)
    bpy.ops.object.mode_set(mode="OBJECT")

    material = bpy.data.materials.new(name=f"{name}_PilotMaterial")
    material.diffuse_color = (0.18, 0.20, 0.22, 1.0)
    obj.data.materials.append(material)
    return obj


def validate(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data
    mesh.calc_loop_triangles()
    bounds = [round(max(point[i] for point in obj.bound_box) - min(point[i] for point in obj.bound_box), 6) for i in range(3)]
    assert obj.type == "MESH"
    assert tuple(round(value, 6) for value in obj.location) == (0.0, 0.0, 0.0)
    assert tuple(round(value, 6) for value in obj.rotation_euler) == (0.0, 0.0, 0.0)
    assert tuple(round(value, 6) for value in obj.scale) == (1.0, 1.0, 1.0)
    assert bounds == [1.0, 1.0, 1.0]
    assert len(mesh.uv_layers) == 1
    assert len(obj.material_slots) == 1
    return {
        "bounds_m": bounds,
        "material_slots": len(obj.material_slots),
        "triangles": len(mesh.loop_triangles),
        "uv_channels": len(mesh.uv_layers),
        "vertices": len(mesh.vertices),
    }


def export_fbx(obj: bpy.types.Object, path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(path),
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
        bake_anim=False,
    )


def main() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for block in list(collection):
            collection.remove(block)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    built = {name: build_object(name, bevel) for name, bevel in OBJECTS.items()}
    validation = {name: validate(obj) for name, obj in built.items()}
    assert sum(item["triangles"] for item in validation.values()) <= 512
    assert len(bpy.data.images) == 0 and len(bpy.data.libraries) == 0

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    for name, obj in built.items():
        export_fbx(obj, ROOT / f"{name}.fbx")

    manifest = {
        "asset_status": "noncanonical_pilot",
        "blender_version": bpy.app.version_string,
        "combined_triangles": sum(item["triangles"] for item in validation.values()),
        "external_references": [],
        "license": "Original OddsWell project asset; no external source material",
        "objects": {
            name: {
                **validation[name],
                "fbx": f"{name}.fbx",
                "fbx_sha256": sha256(ROOT / f"{name}.fbx"),
            }
            for name in OBJECTS
        },
        "source": {
            "blend": BLEND.name,
            "blend_sha256": sha256(BLEND),
            "script": Path(__file__).name,
            "script_sha256": sha256(Path(__file__)),
        },
        "unit_scale_m": scene.unit_settings.scale_length,
        "unit_system": scene.unit_settings.system,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Sundale Job canopy pilot failed: {error}", file=sys.stderr)
        raise
