"""Build and validate the Phase 1L.5bk deterministic skin-binding proof."""

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT.parent / "SharedSkeletonCandidate"
SOURCE_BLEND = SOURCE_DIR / "SharedSkeletonCharacterCandidate.blend"
SOURCE_MANIFEST = SOURCE_DIR / "manifest.json"
OUTPUT_BLEND = ROOT / "SkinnedSharedSkeletonCharacterCandidate.blend"
MANIFEST_PATH = ROOT / "skinning_custody.json"
PROVENANCE_PATH = ROOT / "PROVENANCE.md"
RENDER_DIR = ROOT / "renders"

SOURCE_BLEND_SHA256 = "27D4F7D5585B7AACD90AEF9A03D0426E5415EF2C17F002F79C832F080F9D9F80"
SOURCE_MANIFEST_SHA256 = "63A839B581E8DB21F4F98861D734372A79581126F542174022ACA950B6060A95"
SOURCE_SEMANTIC_SHA256 = "C34CD757A694EC897350350BA1B977A67EFCE6B8E959799992559DB9A0A54860"
MANNEQUIN_NAME = "MANNEQUIN__neutral_beta"
ARMATURE_NAME = "ARMATURE__shared_bilateral_v1"
MODIFIER_NAME = "ARMATURE__static_deformation_proof"
RENDER_SIZE = (720, 900)
POSE_DEGREES = {
    "upper_arm.L": -24.0,
    "forearm.L": 48.0,
    "upper_arm.R": 24.0,
    "forearm.R": -48.0,
    "thigh.L": 12.0,
    "shin.L": -28.0,
    "thigh.R": -12.0,
    "shin.R": 28.0,
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def rounded(values):
    return [round(float(value), 6) for value in values]


def png_dimensions(path):
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"not a PNG: {path}")
    return struct.unpack(">II", header[16:24])


def canonicalize_png(path):
    """Strip Blender's volatile PNG text metadata while preserving pixels."""
    data = path.read_bytes()
    output = bytearray(data[:8])
    cursor = 8
    while cursor < len(data):
        length = struct.unpack(">I", data[cursor : cursor + 4])[0]
        end = cursor + length + 12
        chunk_type = data[cursor + 4 : cursor + 8]
        if chunk_type in {b"IHDR", b"IDAT", b"IEND"}:
            output.extend(data[cursor:end])
        cursor = end
        if chunk_type == b"IEND":
            break
    path.write_bytes(output)


def source_manifest():
    return json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))


def source_custody():
    custody = {
        "blend": {"file": "../SharedSkeletonCandidate/SharedSkeletonCharacterCandidate.blend", "sha256": sha256(SOURCE_BLEND)},
        "manifest": {"file": "../SharedSkeletonCandidate/manifest.json", "sha256": sha256(SOURCE_MANIFEST)},
        "semantic_sha256": source_manifest()["semantic"]["identity_sha256"],
    }
    expected = {
        "blend": SOURCE_BLEND_SHA256,
        "manifest": SOURCE_MANIFEST_SHA256,
        "semantic": SOURCE_SEMANTIC_SHA256,
    }
    actual = {
        "blend": custody["blend"]["sha256"],
        "manifest": custody["manifest"]["sha256"],
        "semantic": custody["semantic_sha256"],
    }
    if actual != expected:
        raise RuntimeError(f"accepted Phase 1L.5bj source custody differs: {actual}")
    return custody


def find_objects():
    mannequin = bpy.data.objects.get(MANNEQUIN_NAME)
    armature = bpy.data.objects.get(ARMATURE_NAME)
    if mannequin is None or mannequin.type != "MESH":
        raise RuntimeError("accepted mannequin is missing")
    if armature is None or armature.type != "ARMATURE":
        raise RuntimeError("accepted armature is missing")
    return mannequin, armature


def mesh_signature(mannequin):
    mesh = mannequin.data
    payload = {
        "vertices": [rounded(vertex.co) for vertex in mesh.vertices],
        "edges": [list(edge.vertices) for edge in mesh.edges],
        "polygons": [list(polygon.vertices) for polygon in mesh.polygons],
        "materials": [slot.material.name for slot in mannequin.material_slots],
    }
    return canonical_sha256(payload)


def connected_components(mesh):
    neighbors = {vertex.index: set() for vertex in mesh.vertices}
    for edge in mesh.edges:
        left, right = edge.vertices
        neighbors[left].add(right)
        neighbors[right].add(left)
    remaining = set(neighbors)
    components = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component = []
        remaining.remove(start)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(neighbors[current], reverse=True):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def component_summary(mesh, indices):
    points = [mesh.vertices[index].co for index in indices]
    return {
        "first_vertex": indices[0],
        "vertex_count": len(indices),
        "center_m": rounded(sum(points, Vector()) / len(points)),
        "bounds_min_m": rounded(tuple(min(point[axis] for point in points) for axis in range(3))),
        "bounds_max_m": rounded(tuple(max(point[axis] for point in points) for axis in range(3))),
    }


def component_owner(summary):
    x, _y, z = summary["center_m"]
    if z >= 1.58:
        return "head"
    if z >= 1.43:
        return "neck"
    if abs(x) < 0.1:
        return "spine" if z >= 1.0 else "root"
    side = "L" if x > 0.0 else "R"
    if z >= 1.1:
        return f"upper_arm.{side}"
    if z >= 0.68 and abs(x) > 0.2:
        return f"forearm.{side}"
    if z >= 0.5:
        return f"thigh.{side}"
    return f"shin.{side}"


def bind_mannequin(mannequin, armature):
    if mannequin.vertex_groups or mannequin.modifiers:
        raise RuntimeError("accepted source is not an unbound mannequin")
    bone_names = sorted(bone.name for bone in armature.data.bones)
    groups = {name: mannequin.vertex_groups.new(name=name) for name in bone_names}
    component_records = []
    for indices in connected_components(mannequin.data):
        summary = component_summary(mannequin.data, indices)
        owner = component_owner(summary)
        groups[owner].add(indices, 1.0, "REPLACE")
        summary["owner"] = owner
        component_records.append(summary)
    modifier = mannequin.modifiers.new(MODIFIER_NAME, "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    modifier.use_deform_preserve_volume = False
    mannequin["skinning_phase"] = "Phase 1L.5bk"
    mannequin["weight_policy"] = "one rigid bone influence per disconnected primitive component"
    mannequin["weight_normalization"] = "exact_1.0"
    return component_records


def weight_custody(mannequin, armature, component_records):
    names = sorted(group.name for group in mannequin.vertex_groups)
    bone_names = sorted(bone.name for bone in armature.data.bones)
    if names != bone_names or len(names) != 12:
        raise RuntimeError("vertex groups must match the exact 12 armature bones")
    counts = {name: 0 for name in names}
    sums = {name: 0.0 for name in names}
    unweighted = []
    non_normalized = []
    influence_histogram = {}
    for vertex in mannequin.data.vertices:
        influences = [(names[entry.group], entry.weight) for entry in vertex.groups]
        influence_histogram[str(len(influences))] = influence_histogram.get(str(len(influences)), 0) + 1
        if not influences:
            unweighted.append(vertex.index)
            continue
        total = sum(weight for _name, weight in influences)
        if abs(total - 1.0) > 0.000001:
            non_normalized.append(vertex.index)
        for name, weight in influences:
            counts[name] += 1
            sums[name] += weight
    if unweighted or non_normalized or influence_histogram != {"1": len(mannequin.data.vertices)}:
        raise RuntimeError("weights must be complete, normalized, and single-influence")
    if any(count == 0 for count in counts.values()):
        raise RuntimeError("every accepted armature bone must own at least one vertex")
    modifiers = list(mannequin.modifiers)
    if len(modifiers) != 1 or modifiers[0].type != "ARMATURE" or modifiers[0].object != armature:
        raise RuntimeError("exactly one armature modifier is required")
    return {
        "component_count": len(component_records),
        "components": component_records,
        "groups": {name: {"vertex_count": counts[name], "weight_sum": round(sums[name], 6)} for name in names},
        "influence_histogram": influence_histogram,
        "max_influences_per_vertex": 1,
        "unweighted_vertices": 0,
        "non_normalized_vertices": 0,
        "modifier": {
            "name": modifiers[0].name,
            "type": modifiers[0].type,
            "armature": modifiers[0].object.name,
            "bone_envelopes": modifiers[0].use_bone_envelopes,
            "preserve_volume": modifiers[0].use_deform_preserve_volume,
            "vertex_groups": modifiers[0].use_vertex_groups,
        },
    }


def evaluated_coordinates(mannequin):
    bpy.context.view_layer.update()
    evaluated = mannequin.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def clear_pose(armature):
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()


def apply_diagnostic_pose(armature):
    clear_pose(armature)
    for name, degrees in POSE_DEGREES.items():
        pose_bone = armature.pose.bones[name]
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler[2] = math.radians(degrees)
    bpy.context.view_layer.update()


def deformation_proof(mannequin, armature):
    clear_pose(armature)
    rest = evaluated_coordinates(mannequin)
    apply_diagnostic_pose(armature)
    posed = evaluated_coordinates(mannequin)
    deltas = [posed[index] - rest[index] for index in range(len(rest))]
    moved = [delta for delta in deltas if delta.length > 0.000001]
    record = {
        "diagnostic_only": True,
        "pose_degrees_local_z": POSE_DEGREES,
        "joints_exercised": ["shoulders", "elbows", "hips", "knees"],
        "moved_vertex_count": len(moved),
        "max_displacement_m": round(max(delta.length for delta in moved), 6) if moved else 0.0,
        "delta_identity_sha256": canonical_sha256([rounded(delta) for delta in deltas]),
    }
    clear_pose(armature)
    restored = evaluated_coordinates(mannequin)
    if not moved or any((rest[index] - restored[index]).length > 0.000001 for index in range(len(rest))):
        raise RuntimeError("static diagnostic deformation did not move and restore deterministically")
    return record


def point_at(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_reviews(mannequin, armature):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for old in RENDER_DIR.glob("*.png"):
        old.unlink()
    scene = bpy.context.scene
    camera = scene.camera
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100

    clear_pose(armature)
    camera.location = (0.0, -6.0, 0.95)
    point_at(camera, (0.0, 0.0, 0.9))
    rest_path = RENDER_DIR / "Review_Rest.png"
    scene.render.filepath = str(rest_path)
    bpy.ops.render.render(write_still=True)
    canonicalize_png(rest_path)

    apply_diagnostic_pose(armature)
    camera.location = (4.25, -4.25, 0.95)
    point_at(camera, (0.0, 0.0, 0.9))
    posed_path = RENDER_DIR / "Review_StaticDeformation.png"
    scene.render.filepath = str(posed_path)
    bpy.ops.render.render(write_still=True)
    canonicalize_png(posed_path)
    clear_pose(armature)


def pose_is_clear(armature):
    return all(pose_bone.matrix_basis.is_identity for pose_bone in armature.pose.bones)


def armature_semantic(armature):
    return {
        bone.name: {
            "head_m": rounded(bone.head_local),
            "tail_m": rounded(bone.tail_local),
            "parent": bone.parent.name if bone.parent else None,
            "connected": bone.use_connect,
        }
        for bone in sorted(armature.data.bones, key=lambda value: value.name)
    }


def scene_semantic(mannequin, armature, geometry_sha256, weights, deformation):
    source = source_manifest()["semantic"]
    semantic = {
        "source_semantic_sha256": SOURCE_SEMANTIC_SHA256,
        "geometry_sha256": geometry_sha256,
        "mannequin": source["mannequin"],
        "armature": {
            "name": armature.name,
            "bone_count": len(armature.data.bones),
            "bones": armature_semantic(armature),
        },
        "preset_ids": source["preset_ids"],
        "materials": source["materials"],
        "neutral_horizontal_midpoints_m": source["neutral_horizontal_midpoints_m"],
        "skinning": weights,
        "static_deformation": deformation,
        "rest_pose_saved": pose_is_clear(armature),
        "object_counts": {
            "total": len(bpy.data.objects),
            "mesh": len([obj for obj in bpy.data.objects if obj.type == "MESH"]),
            "armature": len([obj for obj in bpy.data.objects if obj.type == "ARMATURE"]),
            "camera": len([obj for obj in bpy.data.objects if obj.type == "CAMERA"]),
            "light": len([obj for obj in bpy.data.objects if obj.type == "LIGHT"]),
        },
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    return semantic


def validate_boundaries(mannequin, armature):
    errors = []
    if mannequin.parent is not None:
        errors.append("object parenting is outside this proof")
    if mannequin.data.shape_keys:
        errors.append("shape keys are forbidden")
    if len(bpy.data.actions) != 0:
        errors.append("actions/motion clips are forbidden")
    if any(pose_bone.constraints for pose_bone in armature.pose.bones):
        errors.append("constraints/IK/control-rig surfaces are forbidden")
    if armature.animation_data or mannequin.animation_data:
        errors.append("animation data, NLA, and drivers are forbidden")
    if len([obj for obj in bpy.data.objects if obj.type == "MESH"]) != 1:
        errors.append("clothing or additional meshes are forbidden")
    if not pose_is_clear(armature):
        errors.append("saved source must remain in clear rest pose")
    if errors:
        raise RuntimeError("\n".join(errors))


def write_manifest(semantic, custody):
    renders = []
    for filename, role in (("Review_Rest.png", "REST"), ("Review_StaticDeformation.png", "STATIC_DIAGNOSTIC")):
        path = RENDER_DIR / filename
        width, height = png_dimensions(path)
        renders.append({"file": f"renders/{filename}", "role": role, "width": width, "height": height, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "phase": "Phase 1L.5bk deterministic mannequin skin binding and static deformation proof",
        "status": "skinned_source_static_diagnostic_only_not_animated_or_runtime",
        "blender_version": bpy.app.version_string,
        "source_custody": custody,
        "semantic": semantic,
        "renders": renders,
        "files": {
            "blend": {"file": OUTPUT_BLEND.name, "identity": "semantic_only"},
            "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"file": PROVENANCE_PATH.name, "bytes": PROVENANCE_PATH.stat().st_size, "sha256": sha256(PROVENANCE_PATH)},
        },
        "boundaries": {
            "skin_weights": "explicit_one_influence_normalized",
            "armature_modifiers": 1,
            "unweighted_vertices": 0,
            "non_normalized_vertices": 0,
            "actions": 0,
            "nla_tracks": 0,
            "motion_clips": 0,
            "control_rigs": 0,
            "ik": 0,
            "constraints": 0,
            "drivers": 0,
            "shape_keys": 0,
            "clothing_refits": 0,
            "exports": 0,
            "unreal_imports": 0,
            "runtime_changes": 0,
            "final_art_claim": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_outputs():
    custody = source_custody()
    mannequin, armature = find_objects()
    validate_boundaries(mannequin, armature)
    if not MANIFEST_PATH.exists() or not OUTPUT_BLEND.exists() or OUTPUT_BLEND.with_suffix(".blend1").exists():
        raise RuntimeError("required additive outputs are missing or a blend backup exists")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("source_custody") != custody:
        raise RuntimeError("manifest source custody differs")
    component_records = []
    for indices in connected_components(mannequin.data):
        summary = component_summary(mannequin.data, indices)
        summary["owner"] = component_owner(summary)
        component_records.append(summary)
    weights = weight_custody(mannequin, armature, component_records)
    deformation = deformation_proof(mannequin, armature)
    semantic = scene_semantic(mannequin, armature, mesh_signature(mannequin), weights, deformation)
    if manifest.get("semantic") != semantic:
        raise RuntimeError("retained semantic identity differs")
    if manifest.get("blender_version") != bpy.app.version_string:
        raise RuntimeError("Blender version differs")
    if len(manifest.get("renders", [])) != 2:
        raise RuntimeError("exact rest and diagnostic renders are required")
    for render in manifest["renders"]:
        path = ROOT / render["file"]
        if png_dimensions(path) != RENDER_SIZE or path.stat().st_size != render["bytes"] or sha256(path) != render["sha256"]:
            raise RuntimeError(f"render identity differs: {path.name}")
    for key, path in (("builder", Path(__file__)), ("provenance", PROVENANCE_PATH)):
        record = manifest["files"][key]
        if path.stat().st_size != record["bytes"] or sha256(path) != record["sha256"]:
            raise RuntimeError(f"{key} identity differs")
    print(
        "ODDSWELL_SKIN_BINDING_VALIDATION|result=PASS|mesh=1|armature=1|bones=12|groups=12|modifier=1|"
        f"vertices={len(mannequin.data.vertices)}|components={weights['component_count']}|unweighted=0|non_normalized=0|"
        f"max_influences=1|moved={deformation['moved_vertex_count']}|actions=0|nla=0|clips=0|constraints=0|ik=0|"
        "clothing=0|exports=0|imports=0|runtime=0|rest_pose_saved=true"
    )
    return semantic


def build():
    custody = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.preferences.filepaths.save_version = 0
    mannequin, armature = find_objects()
    source = source_manifest()["semantic"]
    geometry_sha256 = mesh_signature(mannequin)
    if source["armature"]["bones"] != armature_semantic(armature):
        raise RuntimeError("accepted bone names, landmarks, or hierarchy differ")
    if source["mannequin"]["vertices"] != len(mannequin.data.vertices) or source["mannequin"]["polygons"] != len(mannequin.data.polygons):
        raise RuntimeError("accepted mannequin geometry differs")
    component_records = bind_mannequin(mannequin, armature)
    weights = weight_custody(mannequin, armature, component_records)
    deformation = deformation_proof(mannequin, armature)
    render_reviews(mannequin, armature)
    validate_boundaries(mannequin, armature)
    semantic = scene_semantic(mannequin, armature, geometry_sha256, weights, deformation)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    write_manifest(semantic, custody)
    validate_outputs()
    if sha256(SOURCE_BLEND) != SOURCE_BLEND_SHA256 or sha256(SOURCE_MANIFEST) != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("accepted Phase 1L.5bj source changed during additive build")
    print(
        "ODDSWELL_SKIN_BINDING_BUILD|result=PASS|artifacts=5|"
        f"semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|manual_input=false"
    )


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if "--validate-only" in arguments or "--focused-validate" in arguments:
        semantic = validate_outputs()
        mode = "REOPEN" if "--validate-only" in arguments else "FOCUSED"
        print(f"ODDSWELL_SKIN_BINDING_{mode}|result=PASS|semantic_sha256={semantic['identity_sha256']}|manifest_sha256={sha256(MANIFEST_PATH)}|render_hashes=2")
        return
    build()


if __name__ == "__main__":
    main()
