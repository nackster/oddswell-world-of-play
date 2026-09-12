"""Export the existing Actions at their authored rates; keep historical FBXs intact."""
import importlib.util
import json
import math
import struct
from pathlib import Path

import bpy
from io_scene_fbx import encode_bin, parse_fbx

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "CharacterFBXExport"
spec = importlib.util.spec_from_file_location("original_export", OLD / "build_character_fbx_export.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
TICKS_PER_SECOND = 46186158000
export_duration_ticks = None
write_fbx = encode_bin.write


def write_complete_frame_span(filename, tree, version):
    # Use an outward, float32-safe span before integer-tick serialization so
    # downstream float conversion cannot discard the final frame.
    def visit(node):
        if export_duration_ticks is not None:
            if node.id == b"AnimationStack":
                properties = next(x for x in node.elems if x.id == b"Properties70")
                values = {x.props[0][4:]: x for x in properties.elems}
                for prefix in (b"Local", b"Reference"):
                    start = struct.unpack("<q", values[prefix + b"Start"].props[-1])[0] if prefix + b"Start" in values else 0
                    values[prefix + b"Stop"].props[-1] = struct.pack("<q", start + export_duration_ticks)
            elif node.id in (b"LocalTime", b"ReferenceTime"):
                start = struct.unpack("<q", node.props[0])[0]
                node.props[1] = struct.pack("<q", start + export_duration_ticks)
        for child in node.elems:
            visit(child)
    visit(tree)
    write_fbx(filename, tree, version)


encode_bin.write = write_complete_frame_span


def duration(path):
    tree, _ = parse_fbx.parse(str(path))
    objects = next(item for item in tree.elems if item.id == b"Objects")
    stack = next(item for item in objects.elems if item.id == b"AnimationStack")
    properties = next(item for item in stack.elems if item.id == b"Properties70")
    values = {item.props[0]: item.props[-1] for item in properties.elems}
    return (values[b"LocalStop"] - values[b"LocalStart"]) / TICKS_PER_SECOND


def build():
    global export_duration_ticks
    source, contract = original.source_custody()
    semantics = source["semantic"]
    actions = {semantics[key]["name"]: semantics[key] for key in (
        "preserved_walk_action", "preserved_run_action", "preserved_jump_action", "landing_action")}
    previous = json.loads((OLD / "character_fbx_export_custody.json").read_text())
    if original.sha256(OLD / "character_fbx_export_custody.json") != "81EF175D7600D188E06305FAB5DD0366BE1AD0D4093C9F77C3C8CBAF135F2433":
        raise RuntimeError("historical export manifest changed")
    for record in previous["exports"]:
        if original.sha256(OLD / record["file"]) != record["sha256"]:
            raise RuntimeError("historical export changed")
    records = []
    # Two independent scene reopens prove same-path export determinism.
    hashes = []
    for attempt in range(2):
        bpy.ops.wm.open_mainfile(filepath=str(original.SOURCE_BLEND))
        original.LAND.validate_outputs()
        armature = bpy.data.objects[contract["shared_skeleton"]["source_object"]]
        # Unreal recognizes this Blender object wrapper and excludes it from bone tracks.
        # This is not a bone rename, and the retained .blend is never saved.
        armature.name = "Armature"
        current = {}
        for partition in contract["minimum_fbx_partition"]:
            path = ROOT / partition["file"]
            contents = partition["contents"]
            if path.name.startswith("SK_"):
                export_duration_ticks = None
                original.select_only([armature, bpy.data.objects[contents[1]]])
                original.common_export(path, {"ARMATURE", "MESH"}, False)
                timing = None
            else:
                original.select_only([armature])
                action = bpy.data.actions[contents[1]]
                authored = actions[action.name]
                armature.animation_data.action = action
                bpy.context.scene.frame_start = int(action.frame_range[0])
                bpy.context.scene.frame_end = int(action.frame_range[1])
                bpy.context.scene.render.fps = authored["fps"]
                bpy.context.scene.render.fps_base = 1.0
                expected = (authored["frame_end"] - authored["frame_start"]) / authored["fps"]
                float_bits = struct.unpack("<I", struct.pack("<f", expected))[0]
                float_seconds = struct.unpack("<f", struct.pack("<I", float_bits))[0]
                if float_seconds < expected:
                    float_seconds = struct.unpack("<f", struct.pack("<I", float_bits + 1))[0]
                export_duration_ticks = math.ceil(float_seconds * TICKS_PER_SECOND)
                original.common_export(path, {"ARMATURE"}, True)
                observed = duration(path)
                if not 0 <= observed - expected < 1e-7:
                    raise RuntimeError(f"animation timing differs: {path.name}: {observed} != {expected}")
                timing = {"fps": authored["fps"], "frames": authored["frame_end"] - authored["frame_start"],
                          "seconds": observed, "authored_seconds": expected,
                          "historical_seconds": duration(OLD / path.name)}
            current[path.name] = original.sha256(path)
            if attempt == 1:
                sidecar = ROOT / partition["sha256_record"]
                sidecar.write_text(f"{current[path.name]}  {path.name}\n", encoding="ascii", newline="\n")
                records.append({**partition, "bytes": path.stat().st_size, "sha256": current[path.name], "timing": timing})
        hashes.append(current)
    if hashes[0] != hashes[1]:
        raise RuntimeError("repeat export hashes differ")
    evidence = {"source_contract_sha256": original.sha256(original.CONTRACT_PATH),
                "source_blend_sha256": original.sha256(original.SOURCE_BLEND),
                "historical_exports_preserved": True, "export_armature_object_name": "Armature",
                "repeat_hashes_equal": True, "exports": records}
    (ROOT / "timed_export_custody.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("ODDSWELL_TIMED_EXPORT_PASS " + json.dumps({r["file"]: r["timing"] for r in records if r["timing"]}))


if __name__ == "__main__":
    build()
