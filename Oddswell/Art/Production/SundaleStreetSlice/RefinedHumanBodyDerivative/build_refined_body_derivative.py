"""Build/validate the Phase 1L.5bv body-only neutral-bind proof."""

import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
SOURCE = ROOT.parent / "OddsWell_Sundale_StreetSlice.blend"
HANDOFF = ROOT.parent / "runtime_shared_skeleton_handoff_contract.json"
ACCEPTED = REPO / "Oddswell/Art/Production/PlayerCharacter/SkinnedSharedSkeletonCandidate/SkinnedSharedSkeletonCharacterCandidate.blend"
DEC034 = REPO / "Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json"
DEC035 = REPO / "Oddswell/Art/Production/PlayerCharacter/character_unreal_import_contract.json"
OUTPUT = ROOT / "RefinedSundaleHumanBodyNeutralBind.blend"
MANIFEST = ROOT / "neutral_bind_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
BODY_NAME = "BODY__refined_sundale_derivative_v1"
ARMATURE_NAME = "ARMATURE__shared_bilateral_v1"
SOURCE_NAMES = (
    "Character | anatomical head",
    "Character | anatomical left hand",
    "Character | anatomical legs",
    "Character | anatomical right hand",
)
SOURCE_SHA256 = "0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127"
HANDOFF_SHA256 = "9DFE96E72883BBC3BB9AFB7FAD799644C54DE817142CE625862F9BA06764926A"
ACCEPTED_SHA256 = "9CBD196FDB42FA76788673467D16954733796AE6820073075005444B0942A443"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest().upper()


def rounded(values):
    return [round(float(value), 6) for value in values]


def apply_transform(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)


def add_cube(name, location, dimensions):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transform(obj)
    return obj


def add_limb(name, start, end, radius):
    start, end = Vector(start), Vector(end)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=direction.length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    apply_transform(obj)
    return obj


def source_custody():
    actual = {"source": sha256(SOURCE), "handoff": sha256(HANDOFF), "accepted_bind": sha256(ACCEPTED)}
    expected = {"source": SOURCE_SHA256, "handoff": HANDOFF_SHA256, "accepted_bind": ACCEPTED_SHA256}
    if actual != expected:
        raise RuntimeError(f"source custody differs: {actual}")
    return actual


def clean_accepted_scene():
    bpy.ops.wm.open_mainfile(filepath=str(ACCEPTED), load_ui=False)
    armature = bpy.data.objects.get(ARMATURE_NAME)
    if armature is None or armature.type != "ARMATURE":
        raise RuntimeError("accepted shared armature missing")
    for obj in list(bpy.data.objects):
        if obj != armature:
            bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    armature.animation_data_clear()
    armature.location = (0.0, 0.0, 0.0)
    armature.rotation_euler = (0.0, 0.0, 0.0)
    armature.scale = (1.0, 1.0, 1.0)
    return armature


def append_source_parts():
    with bpy.data.libraries.load(str(SOURCE), link=False) as (available, requested):
        missing = sorted(set(SOURCE_NAMES) - set(available.objects))
        if missing:
            raise RuntimeError(f"source anatomy missing: {missing}")
        requested.objects = list(SOURCE_NAMES)
    parts = []
    for name in SOURCE_NAMES:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            raise RuntimeError(f"invalid source part: {name}")
        bpy.context.scene.collection.objects.link(obj)
        obj.data = obj.data.copy()
        obj.modifiers.clear()
        if obj.data.shape_keys:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.shape_key_remove(all=True)
            obj.select_set(False)
        apply_transform(obj)
        parts.append(obj)
    points = [vertex.co.copy() for obj in parts for vertex in obj.data.vertices]
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    scale = 1.8 / (maximum.z - minimum.z)
    center = (minimum + maximum) / 2.0
    for obj in parts:
        for vertex in obj.data.vertices:
            world = vertex.co
            vertex.co = ((world.x - center.x) * scale, (world.y - center.y) * scale, (world.z - minimum.z) * scale)
    return parts, {
        "objects": list(SOURCE_NAMES),
        "source_bounds_min_m": rounded(minimum),
        "source_bounds_max_m": rounded(maximum),
        "uniform_scale": round(scale, 9),
    }


def add_neutral_bridge(landmarks):
    shoulder, elbow, wrist = landmarks["shoulder"], landmarks["elbow"], landmarks["wrist"]
    pieces = [
        add_cube("BRIDGE__torso", (0.0, 0.0, 1.20), (0.43, 0.22, 0.48)),
        add_limb("BRIDGE__neck", (0.0, 0.0, shoulder), (0.0, 0.0, 1.57), 0.07),
    ]
    for side, suffix in ((1.0, "L"), (-1.0, "R")):
        pieces.extend((
            add_limb(f"BRIDGE__upper_arm.{suffix}", (side * 0.245, 0.0, shoulder), (side * 0.28, 0.0, elbow), 0.058),
            add_limb(f"BRIDGE__forearm.{suffix}", (side * 0.28, 0.0, elbow), (side * 0.265, 0.0, wrist), 0.05),
        ))
    return pieces


def join_body(parts, bridge):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts + bridge:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = BODY_NAME
    material = bpy.data.materials.new("MAT__refined_body_proof")
    material.diffuse_color = (0.67, 0.39, 0.25, 1.0)
    body.data.materials.clear()
    body.data.materials.append(material)
    for polygon in body.data.polygons:
        polygon.material_index = 0
    body["source_blend_sha256"] = SOURCE_SHA256
    body["body_only_derivative"] = True
    body["bridge_role"] = "neutral_bind_proxy_only"
    body["final_art"] = False
    return body


def point_segment_distance(point, head, tail):
    segment = tail - head
    t = max(0.0, min(1.0, (point - head).dot(segment) / segment.length_squared))
    return (point - (head + segment * t)).length_squared


def bind(body, armature):
    bones = sorted(armature.data.bones, key=lambda bone: bone.name)
    groups = {bone.name: body.vertex_groups.new(name=bone.name) for bone in bones}
    counts = {bone.name: 0 for bone in bones}
    owners = []
    for vertex in body.data.vertices:
        owner = min(bones, key=lambda bone: (point_segment_distance(vertex.co, bone.head_local, bone.tail_local), bone.name))
        owners.append(owner.name)
        counts[owner.name] += 1
    for bone in bones:
        if counts[bone.name]:
            continue
        midpoint = (bone.head_local + bone.tail_local) / 2.0
        index = min(
            (vertex.index for vertex in body.data.vertices if counts[owners[vertex.index]] > 1),
            key=lambda candidate: ((body.data.vertices[candidate].co - midpoint).length_squared, candidate),
        )
        counts[owners[index]] -= 1
        owners[index] = bone.name
        counts[bone.name] += 1
    for vertex, owner in zip(body.data.vertices, owners):
        groups[owner].add([vertex.index], 1.0, "REPLACE")
    if any(count == 0 for count in counts.values()):
        raise RuntimeError(f"every accepted bone must own vertices: {counts}")
    modifier = body.modifiers.new("ARMATURE__neutral_bind_proof", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    return counts


def armature_semantic(armature):
    return {
        bone.name: {
            "head_m": rounded(bone.head_local),
            "tail_m": rounded(bone.tail_local),
            "parent": bone.parent.name if bone.parent else None,
            "connected": bone.use_connect,
        }
        for bone in sorted(armature.data.bones, key=lambda bone: bone.name)
    }


def mesh_semantic(body):
    return {
        "vertices": [rounded(vertex.co) for vertex in body.data.vertices],
        "polygons": [list(polygon.vertices) for polygon in body.data.polygons],
    }


def validate(body, armature, contract, import_contract):
    expected_bones = set(import_contract["source_to_unreal_bone_names"])
    actual_bones = {bone.name for bone in armature.data.bones}
    if actual_bones != expected_bones or len(actual_bones) != 12:
        raise RuntimeError("accepted bone set drift")
    landmarks = contract["shared_landmarks_m"]
    expected_z = {
        "root": (0.0, landmarks["ankle"]),
        "spine": (landmarks["hip"], landmarks["shoulder"]),
        "neck": (landmarks["shoulder"], landmarks["head_center"]),
        "head": (landmarks["head_center"], landmarks["crown"]),
        "upper_arm.L": (landmarks["shoulder"], landmarks["elbow"]),
        "upper_arm.R": (landmarks["shoulder"], landmarks["elbow"]),
        "forearm.L": (landmarks["elbow"], landmarks["wrist"]),
        "forearm.R": (landmarks["elbow"], landmarks["wrist"]),
        "thigh.L": (landmarks["hip"], landmarks["knee"]),
        "thigh.R": (landmarks["hip"], landmarks["knee"]),
        "shin.L": (landmarks["knee"], landmarks["ankle"]),
        "shin.R": (landmarks["knee"], landmarks["ankle"]),
    }
    for bone in armature.data.bones:
        parent = bone.parent.name if bone.parent else None
        if parent != import_contract["source_bone_parents"][bone.name]:
            raise RuntimeError(f"accepted hierarchy drift: {bone.name}")
        if abs(bone.head_local.z - expected_z[bone.name][0]) > 1e-6 or abs(bone.tail_local.z - expected_z[bone.name][1]) > 1e-6:
            raise RuntimeError(f"DEC-034 landmark drift: {bone.name}")
    if armature.location.length > 0 or any(abs(value - 1.0) > 1e-9 for value in armature.scale):
        raise RuntimeError("unauthorized armature root transform")
    if bpy.data.actions or armature.animation_data or body.animation_data:
        raise RuntimeError("animation or root motion is forbidden")
    if len([obj for obj in bpy.data.objects if obj.type == "MESH"]) != 1:
        raise RuntimeError("body-only proof must contain one mesh")
    if any(token in body.name.lower() for token in ("support", "collision", "jacket", "short", "shoe")):
        raise RuntimeError("offline fitting/collision/clothing aid leaked")
    z_values = [vertex.co.z for vertex in body.data.vertices]
    if abs(min(z_values)) > 1e-6 or abs(max(z_values) - contract["body"]["stature_m"]) > 1e-6:
        raise RuntimeError("DEC-034 stature drift")
    group_names = {group.index: group.name for group in body.vertex_groups}
    unweighted = non_normalized = 0
    counts = {name: 0 for name in expected_bones}
    for vertex in body.data.vertices:
        influences = [(group_names[item.group], item.weight) for item in vertex.groups]
        if not influences:
            unweighted += 1
        if abs(sum(weight for _name, weight in influences) - 1.0) > 1e-6:
            non_normalized += 1
        for name, _weight in influences:
            counts[name] += 1
    if unweighted or non_normalized or any(value == 0 for value in counts.values()):
        raise RuntimeError("weight completeness/normalization failure")
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        drift = max((mesh.vertices[index].co - body.data.vertices[index].co).length for index in range(len(mesh.vertices)))
    finally:
        evaluated.to_mesh_clear()
    if drift > 1e-6:
        raise RuntimeError(f"neutral/rest bind drift: {drift}")
    return {"unweighted_vertices": unweighted, "non_normalized_vertices": non_normalized, "max_neutral_bind_drift_m": round(drift, 9), "vertices_by_bone": counts}


def write_provenance():
    PROVENANCE.write_text(
        "# Refined Sundale body derivative provenance\n\n"
        "- Original local source only: `../OddsWell_Sundale_StreetSlice.blend`.\n"
        "- Four anatomical source meshes are copied; the source file is never saved.\n"
        "- A low-poly neutral torso/arm bridge exists only to exercise the accepted twelve-bone rest bind.\n"
        "- Offline cloth fitting/collision aids, clothing, footwear, animation, FBX, Unreal import, and runtime replacement are excluded.\n"
        "- This is deterministic technical proof, not final art or readiness evidence.\n",
        encoding="utf-8",
    )


def build():
    custody = source_custody()
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    armature = clean_accepted_scene()
    parts, extraction = append_source_parts()
    body = join_body(parts, add_neutral_bridge(contract["shared_landmarks_m"]))
    bind(body, armature)
    proof = validate(body, armature, contract, import_contract)
    write_provenance()
    semantic = {
        "body": {"name": body.name, "vertex_count": len(body.data.vertices), "polygon_count": len(body.data.polygons), "bounds_min_m": rounded(tuple(min(vertex.co[axis] for vertex in body.data.vertices) for axis in range(3))), "bounds_max_m": rounded(tuple(max(vertex.co[axis] for vertex in body.data.vertices) for axis in range(3))), "mesh_sha256": canonical_sha256(mesh_semantic(body))},
        "source_extraction": extraction,
        "armature": {"name": armature.name, "bones": armature_semantic(armature), "dec035_mapping": import_contract["source_to_unreal_bone_names"]},
        "landmarks_m": contract["shared_landmarks_m"],
        "weights": proof,
        "actions": 0,
        "root_translation_m": rounded(armature.location),
        "excluded": ["offline fitting/collision aids", "clothing", "footwear", "actions", "FBX", "UAsset", "runtime import"],
    }
    semantic["identity_sha256"] = canonical_sha256(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    manifest = {
        "phase": "Phase 1L.5bv refined Sundale body derivative neutral-bind proof",
        "status": "body_only_derivative_neutral_bind_proof_not_runtime_or_final_art",
        "blender_version": bpy.app.version_string,
        "source_custody": custody,
        "semantic": semantic,
        "files": {"blend": {"file": OUTPUT.name, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}},
        "boundaries": {"source_mesh_mutation": 0, "clothing": 0, "actions": 0, "fbx": 0, "unreal_import": 0, "runtime_or_package_input_change": 0, "authority_change": 0, "final_art_claim": False, "readiness_claim": False},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFINED_BODY_BIND_PASS vertices={len(body.data.vertices)} bones={len(armature.data.bones)} identity={semantic['identity_sha256']}")


def validate_saved():
    custody = source_custody()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["source_custody"] != custody or manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if body is None or armature is None:
        raise RuntimeError("saved proof objects missing")
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    validate(body, armature, contract, import_contract)
    semantic = manifest["semantic"]
    if semantic["body"]["mesh_sha256"] != canonical_sha256(mesh_semantic(body)) or semantic["armature"]["bones"] != armature_semantic(armature):
        raise RuntimeError("saved semantic drift")
    print(f"REFINED_BODY_BIND_VALIDATE_PASS identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
