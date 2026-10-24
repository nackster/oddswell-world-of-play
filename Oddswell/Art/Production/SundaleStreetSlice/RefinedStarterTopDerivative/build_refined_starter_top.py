"""Build/validate the Phase 1L.5bw starter-top neutral-bind proof."""

import hashlib
import json
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
BODY_DIR = ROOT.parent / "RefinedHumanBodyDerivative"
BODY_BLEND = BODY_DIR / "RefinedSundaleHumanBodyNeutralBind.blend"
BODY_CUSTODY = BODY_DIR / "neutral_bind_custody.json"
DEC034 = REPO / "Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json"
DEC035 = REPO / "Oddswell/Art/Production/PlayerCharacter/character_unreal_import_contract.json"
OUTPUT = ROOT / "RefinedSundaleStarterTopNeutralBind.blend"
MANIFEST = ROOT / "starter_top_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
BODY_NAME = "BODY__refined_sundale_derivative_v1"
TOP_NAME = "starter_offwhite_top"
ARMATURE_NAME = "ARMATURE__shared_bilateral_v1"
BODY_BLEND_SHA256 = "83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB"
BODY_CUSTODY_SHA256 = "2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0"
BODY_SEMANTIC_SHA256 = "91AAB962825784679391C85FD06239A2F8EB118FEABA906EF9C5FB373FB8CF08"
BODY_MESH_SHA256 = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
ALLOWED_GROUPS = {"spine"}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


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
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=direction.length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    apply_transform(obj)
    return obj


def source_custody():
    actual = {"body_blend": sha256(BODY_BLEND), "body_custody": sha256(BODY_CUSTODY)}
    expected = {"body_blend": BODY_BLEND_SHA256, "body_custody": BODY_CUSTODY_SHA256}
    if actual != expected:
        raise RuntimeError(f"accepted body custody differs: {actual}")
    custody = json.loads(BODY_CUSTODY.read_text(encoding="utf-8"))
    if custody["semantic"]["identity_sha256"] != BODY_SEMANTIC_SHA256 or custody["semantic"]["body"]["mesh_sha256"] != BODY_MESH_SHA256:
        raise RuntimeError("accepted body semantic identity differs")
    return actual


def open_body():
    bpy.ops.wm.open_mainfile(filepath=str(BODY_BLEND), load_ui=False)
    body, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if body is None or armature is None:
        raise RuntimeError("accepted body or armature missing")
    if bpy.data.actions or body.animation_data or armature.animation_data:
        raise RuntimeError("accepted neutral source contains animation")
    return body, armature


def build_top(contract):
    top = add_cube("TOP__torso", (0.0, 0.0, 1.20), (0.76, 0.68, 0.60))
    mesh = top.data
    edit = bmesh.new()
    edit.from_mesh(mesh)
    bmesh.ops.delete(edit, geom=[face for face in edit.faces if abs(face.normal.z) > 0.9], context="FACES")
    edit.to_mesh(mesh)
    edit.free()
    top.name = TOP_NAME
    material = bpy.data.materials.new("MAT__starter_offwhite_top_proof")
    material.diffuse_color = (0.9, 0.87, 0.79, 1.0)
    top.data.materials.append(material)
    top["item_id"] = TOP_NAME
    top["technical_proof_only"] = True
    top["finished_material"] = False
    return top


def point_segment_distance(point, head, tail):
    segment = tail - head
    t = max(0.0, min(1.0, (point - head).dot(segment) / segment.length_squared))
    return (point - (head + segment * t)).length_squared


def bind(top, armature):
    bones = [bone for bone in armature.data.bones if bone.name in ALLOWED_GROUPS]
    groups = {bone.name: top.vertex_groups.new(name=bone.name) for bone in bones}
    counts = {bone.name: 0 for bone in bones}
    owners = []
    for vertex in top.data.vertices:
        owner = min(bones, key=lambda bone: (point_segment_distance(vertex.co, bone.head_local, bone.tail_local), bone.name))
        owners.append(owner.name)
        counts[owner.name] += 1
    for bone in bones:
        if counts[bone.name]:
            continue
        midpoint = (bone.head_local + bone.tail_local) / 2.0
        index = min((vertex.index for vertex in top.data.vertices if counts[owners[vertex.index]] > 1), key=lambda candidate: ((top.data.vertices[candidate].co - midpoint).length_squared, candidate))
        counts[owners[index]] -= 1
        owners[index] = bone.name
        counts[bone.name] += 1
    for vertex, owner in zip(top.data.vertices, owners):
        groups[owner].add([vertex.index], 1.0, "REPLACE")
    if any(value == 0 for value in counts.values()):
        raise RuntimeError(f"every allowed top bone must own vertices: {counts}")
    modifier = top.modifiers.new("ARMATURE__starter_top_neutral_bind", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    modifier.use_bone_envelopes = False
    return counts


def mesh_semantic(obj):
    return {"vertices": [rounded(vertex.co) for vertex in obj.data.vertices], "polygons": [list(polygon.vertices) for polygon in obj.data.polygons]}


def armature_semantic(armature):
    return {bone.name: {"head_m": rounded(bone.head_local), "tail_m": rounded(bone.tail_local), "parent": bone.parent.name if bone.parent else None, "connected": bone.use_connect} for bone in sorted(armature.data.bones, key=lambda item: item.name)}


def validate(body, top, armature, contract, import_contract):
    meshes = sorted(obj.name for obj in bpy.data.objects if obj.type == "MESH")
    if meshes != sorted((BODY_NAME, TOP_NAME)):
        raise RuntimeError(f"extra or missing mesh partition: {meshes}")
    if {bone.name for bone in armature.data.bones} != set(import_contract["source_to_unreal_bone_names"]):
        raise RuntimeError("accepted bone set drift")
    if armature.location.length > 0 or any(abs(value - 1.0) > 1e-9 for value in armature.scale):
        raise RuntimeError("unauthorized root transform")
    if bpy.data.actions or body.animation_data or top.animation_data or armature.animation_data:
        raise RuntimeError("Actions/animation/root motion are forbidden")
    if canonical_sha256(mesh_semantic(body)) != BODY_MESH_SHA256:
        raise RuntimeError("accepted body mesh drift")
    z_values = [vertex.co.z for vertex in body.data.vertices]
    if abs(min(z_values)) > 1e-6 or abs(max(z_values) - contract["body"]["stature_m"]) > 1e-6:
        raise RuntimeError("body stature drift")
    if top.name != TOP_NAME or len(top.material_slots) != 1:
        raise RuntimeError("starter top identity/material slot drift")
    group_names = {group.index: group.name for group in top.vertex_groups}
    unweighted = non_normalized = 0
    for vertex in top.data.vertices:
        influences = [(group_names[item.group], item.weight) for item in vertex.groups]
        if not influences:
            unweighted += 1
        if abs(sum(weight for _name, weight in influences) - 1.0) > 1e-6:
            non_normalized += 1
        if any(name not in ALLOWED_GROUPS for name, _weight in influences):
            raise RuntimeError("unauthorized top bone influence")
    if unweighted or non_normalized:
        raise RuntimeError("weight completeness/normalization failure")
    bpy.context.view_layer.update()
    body_tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    top_tree = BVHTree.FromObject(top, bpy.context.evaluated_depsgraph_get())
    intersections = len(body_tree.overlap(top_tree))
    top_to_body = min(body_tree.find_nearest(top.matrix_world @ vertex.co)[3] for vertex in top.data.vertices)
    body_to_top = min(top_tree.find_nearest(body.matrix_world @ vertex.co)[3] for vertex in body.data.vertices)
    clearance = min(top_to_body, body_to_top)
    if intersections or not 0.009 <= clearance <= 0.25:
        raise RuntimeError(f"body/top clearance failure: intersections={intersections}, clearance={clearance}")
    top_z = [vertex.co.z for vertex in top.data.vertices]
    landmarks = contract["shared_landmarks_m"]
    if min(top_z) > landmarks["hip"] or max(top_z) < landmarks["shoulder"]:
        raise RuntimeError("starter top torso coverage drift")
    evaluated = top.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        drift = max((mesh.vertices[index].co - top.data.vertices[index].co).length for index in range(len(mesh.vertices)))
    finally:
        evaluated.to_mesh_clear()
    if drift > 1e-6:
        raise RuntimeError(f"neutral/rest bind drift: {drift}")
    return {"unweighted_vertices": unweighted, "non_normalized_vertices": non_normalized, "body_intersection_pairs": intersections, "clearance_method": "bidirectional_mesh_vertex_to_opposite_surface_bvh", "top_vertex_to_body_surface_min_m": round(top_to_body, 9), "body_vertex_to_top_surface_min_m": round(body_to_top, 9), "bidirectional_vertex_sampled_clearance_min_m": round(clearance, 9), "accepted_clearance_bounds_m": [0.009, 0.25], "maximum_neutral_bind_drift_m": round(drift, 9), "torso_coverage_m": [round(min(top_z), 6), round(max(top_z), 6)]}


def write_provenance():
    PROVENANCE.write_text("# Starter off-white top derivative provenance\n\n- Exact input: the accepted Phase 1L.5bv body neutral-bind Blend and custody manifest.\n- Output adds exactly one native low-poly `starter_offwhite_top` mesh with one off-white proxy material.\n- The body and accepted twelve-bone armature are retained byte-semantically; no bottom, jacket, Action, FBX, Unreal import, runtime replacement, or final-art claim is included.\n", encoding="utf-8")


def build():
    custody = source_custody()
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    body, armature = open_body()
    top = build_top(contract)
    counts = bind(top, armature)
    proof = validate(body, top, armature, contract, import_contract)
    write_provenance()
    semantic = {"body_semantic_sha256": BODY_SEMANTIC_SHA256, "body_mesh_sha256": BODY_MESH_SHA256, "top": {"item_id": TOP_NAME, "vertex_count": len(top.data.vertices), "polygon_count": len(top.data.polygons), "mesh_sha256": canonical_sha256(mesh_semantic(top)), "material_slots": [slot.material.name for slot in top.material_slots]}, "armature": {"bones": armature_semantic(armature), "dec035_mapping": import_contract["source_to_unreal_bone_names"]}, "weights": {"vertices_by_bone": counts, **proof}, "partitions": [BODY_NAME, TOP_NAME], "actions": 0, "root_translation_m": rounded(armature.location)}
    semantic["identity_sha256"] = canonical_sha256(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    manifest = {"phase": "Phase 1L.5bw starter off-white top derivative neutral-bind proof", "status": "starter_top_only_neutral_bind_proof_not_runtime_or_final_art", "blender_version": bpy.app.version_string, "source_custody": custody, "semantic": semantic, "files": {"blend": {"file": OUTPUT.name, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}}, "boundaries": {"top_partitions": 1, "bottom": 0, "jacket": 0, "actions": 0, "fbx": 0, "unreal_import": 0, "runtime_or_package_input_change": 0, "authority_change": 0, "final_art_claim": False, "readiness_claim": False}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFINED_STARTER_TOP_PASS vertices={len(top.data.vertices)} identity={semantic['identity_sha256']}")


def validate_saved():
    custody = source_custody()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["source_custody"] != custody or manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(TOP_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if body is None or top is None or armature is None:
        raise RuntimeError("saved proof objects missing")
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    validate(body, top, armature, contract, import_contract)
    if manifest["semantic"]["top"]["mesh_sha256"] != canonical_sha256(mesh_semantic(top)) or manifest["semantic"]["armature"]["bones"] != armature_semantic(armature):
        raise RuntimeError("saved semantic drift")
    print(f"REFINED_STARTER_TOP_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
