"""Build/validate the Phase 1L.5bx starter-bottom neutral-bind proof."""

import hashlib, json, sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
BODY_DIR = ROOT.parent / "RefinedHumanBodyDerivative"
BODY_BLEND = BODY_DIR / "RefinedSundaleHumanBodyNeutralBind.blend"
BODY_CUSTODY = BODY_DIR / "neutral_bind_custody.json"
SOURCE_BLEND = ROOT.parent / "OddsWell_Sundale_StreetSlice.blend"
DEC034 = REPO / "Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json"
DEC035 = REPO / "Oddswell/Art/Production/PlayerCharacter/character_unreal_import_contract.json"
OUTPUT = ROOT / "RefinedSundaleStarterBottomNeutralBind.blend"
MANIFEST = ROOT / "starter_bottom_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
BODY_NAME = "BODY__refined_sundale_derivative_v1"
BOTTOM_NAME = "starter_offwhite_bottom"
ARMATURE_NAME = "ARMATURE__shared_bilateral_v1"
SOURCE_OBJECT = "Character | shorts leg continuous tailoring"
BODY_BLEND_SHA256 = "83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB"
BODY_CUSTODY_SHA256 = "2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0"
SOURCE_SHA256 = "0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127"
BODY_SEMANTIC_SHA256 = "91AAB962825784679391C85FD06239A2F8EB118FEABA906EF9C5FB373FB8CF08"
BODY_MESH_SHA256 = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
ALLOWED_GROUPS = {"root", "thigh.L", "thigh.R"}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def rounded(values):
    return [round(float(value), 6) for value in values]


def mesh_semantic(obj):
    return {"vertices": [rounded(v.co) for v in obj.data.vertices], "polygons": [list(p.vertices) for p in obj.data.polygons]}


def armature_semantic(obj):
    return {b.name: {"head_m": rounded(b.head_local), "tail_m": rounded(b.tail_local), "parent": b.parent.name if b.parent else None, "connected": b.use_connect} for b in sorted(obj.data.bones, key=lambda x: x.name)}


def custody():
    actual = {"body_blend": sha256(BODY_BLEND), "body_custody": sha256(BODY_CUSTODY), "retained_source": sha256(SOURCE_BLEND)}
    expected = {"body_blend": BODY_BLEND_SHA256, "body_custody": BODY_CUSTODY_SHA256, "retained_source": SOURCE_SHA256}
    if actual != expected:
        raise RuntimeError(f"source custody drift: {actual}")
    body = json.loads(BODY_CUSTODY.read_text(encoding="utf-8"))
    if body["semantic"]["identity_sha256"] != BODY_SEMANTIC_SHA256 or body["semantic"]["body"]["mesh_sha256"] != BODY_MESH_SHA256:
        raise RuntimeError("accepted body semantic drift")
    return actual, body


def append_bottom(body_manifest, body):
    with bpy.data.libraries.load(str(SOURCE_BLEND), link=False) as (src, dst):
        if SOURCE_OBJECT not in src.objects:
            raise RuntimeError("retained shorts object missing")
        dst.objects = [SOURCE_OBJECT]
    bottom = dst.objects[0]
    bpy.context.collection.objects.link(bottom)
    if len(bottom.data.vertices) != 7159 or len(bottom.data.polygons) != 7040:
        raise RuntimeError("retained shorts topology drift")
    bottom.data = bottom.data.copy()
    world = bottom.matrix_world.copy()
    for vertex in bottom.data.vertices:
        vertex.co = world @ vertex.co
    bottom.matrix_world.identity()
    for modifier in list(bottom.modifiers):
        bottom.modifiers.remove(modifier)
    if bottom.data.shape_keys:
        bottom.shape_key_clear()
    for group in list(bottom.vertex_groups):
        bottom.vertex_groups.remove(group)
    extraction = body_manifest["semantic"]["source_extraction"]
    low, high = extraction["source_bounds_min_m"], extraction["source_bounds_max_m"]
    scale = extraction["uniform_scale"]
    center_x, center_y = (low[0] + high[0]) / 2, (low[1] + high[1]) / 2
    for vertex in bottom.data.vertices:
        vertex.co.x = (vertex.co.x - center_x) * scale
        vertex.co.y = (vertex.co.y - center_y) * scale
        vertex.co.z = (vertex.co.z - low[2]) * scale
    bpy.context.view_layer.update()
    body_tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    for vertex in bottom.data.vertices:
        point, normal, _face, _distance = body_tree.find_nearest(vertex.co)
        vertex.co = point + normal.normalized() * 0.03
    bottom.name = BOTTOM_NAME
    bottom.data.name = "MESH__starter_offwhite_bottom_proof"
    bottom.data.materials.clear()
    material = bpy.data.materials.new("MAT__starter_offwhite_bottom_proof")
    material.diffuse_color = (0.9, 0.87, 0.79, 1.0)
    bottom.data.materials.append(material)
    bottom["item_id"] = BOTTOM_NAME
    bottom["technical_proof_only"] = True
    bottom["finished_uv_or_material"] = False
    return bottom


def bind(bottom, armature):
    bones = [b for b in armature.data.bones if b.name in ALLOWED_GROUPS]
    groups = {b.name: bottom.vertex_groups.new(name=b.name) for b in bones}
    counts = {b.name: 0 for b in bones}
    for vertex in bottom.data.vertices:
        if vertex.co.z >= 0.9:
            owner = "root"
        else:
            owner = "thigh.L" if vertex.co.x < 0 else "thigh.R"
        groups[owner].add([vertex.index], 1.0, "REPLACE")
        counts[owner] += 1
    if any(v == 0 for v in counts.values()):
        raise RuntimeError(f"empty accepted weight group: {counts}")
    mod = bottom.modifiers.new("ARMATURE__starter_bottom_neutral_bind", "ARMATURE")
    mod.object, mod.use_vertex_groups, mod.use_bone_envelopes = armature, True, False
    return counts


def validate(body, bottom, armature, contract, import_contract):
    meshes = sorted(o.name for o in bpy.data.objects if o.type == "MESH")
    if meshes != sorted((BODY_NAME, BOTTOM_NAME)):
        raise RuntimeError(f"extra/missing mesh partitions: {meshes}")
    if {b.name for b in armature.data.bones} != set(import_contract["source_to_unreal_bone_names"]):
        raise RuntimeError("accepted bone set drift")
    if armature.location.length > 0 or any(abs(v - 1) > 1e-9 for v in armature.scale):
        raise RuntimeError("unauthorized root transform")
    if bpy.data.actions or body.animation_data or bottom.animation_data or armature.animation_data:
        raise RuntimeError("Actions/animation forbidden")
    if canonical_sha256(mesh_semantic(body)) != BODY_MESH_SHA256:
        raise RuntimeError("accepted body mesh drift")
    body_z = [v.co.z for v in body.data.vertices]
    if abs(min(body_z)) > 1e-6 or abs(max(body_z) - contract["body"]["stature_m"]) > 1e-6:
        raise RuntimeError("body stature drift")
    if len(bottom.data.vertices) != 7159 or len(bottom.data.polygons) != 7040 or len(bottom.material_slots) != 1:
        raise RuntimeError("bottom topology/material drift")
    names = {g.index: g.name for g in bottom.vertex_groups}
    unweighted = non_normalized = 0
    for vertex in bottom.data.vertices:
        influences = [(names[item.group], item.weight) for item in vertex.groups]
        unweighted += not influences
        non_normalized += abs(sum(w for _n, w in influences) - 1) > 1e-6
        if any(n not in ALLOWED_GROUPS for n, _w in influences):
            raise RuntimeError("unauthorized bottom influence, including cloth-only Waist attachment")
    if unweighted or non_normalized:
        raise RuntimeError("weight completeness/normalization failure")
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    body_tree, bottom_tree = BVHTree.FromObject(body, dg), BVHTree.FromObject(bottom, dg)
    intersections = len(body_tree.overlap(bottom_tree))
    bottom_to_body = min(body_tree.find_nearest(bottom.matrix_world @ v.co)[3] for v in bottom.data.vertices)
    body_to_bottom = min(bottom_tree.find_nearest(body.matrix_world @ v.co)[3] for v in body.data.vertices)
    clearance = min(bottom_to_body, body_to_bottom)
    if intersections or not 0.001 <= clearance <= 0.15:
        raise RuntimeError(f"body/bottom clearance failure: intersections={intersections}, clearance={clearance}, bounds={[min(v.co[i] for v in bottom.data.vertices) for i in range(3)]}..{[max(v.co[i] for v in bottom.data.vertices) for i in range(3)]}")
    z = [v.co.z for v in bottom.data.vertices]
    hip, knee = contract["shared_landmarks_m"]["hip"], contract["shared_landmarks_m"]["knee"]
    if min(z) > hip - 0.10 or max(z) < hip + 0.01 or min(z) < knee - 0.15:
        raise RuntimeError(f"waist/hip/upper-leg coverage drift: {min(z)}, {max(z)}")
    evaluated = bottom.evaluated_get(dg)
    mesh = evaluated.to_mesh()
    try:
        drift = max((mesh.vertices[i].co - bottom.data.vertices[i].co).length for i in range(len(mesh.vertices)))
    finally:
        evaluated.to_mesh_clear()
    if drift > 1e-6:
        raise RuntimeError(f"neutral/rest bind drift: {drift}")
    return {"unweighted_vertices": unweighted, "non_normalized_vertices": non_normalized, "body_intersection_pairs": intersections, "clearance_method": "bidirectional_mesh_vertex_to_opposite_surface_bvh", "clearance_is_continuous_triangle_distance": False, "bottom_vertex_to_body_surface_min_m": round(bottom_to_body, 9), "body_vertex_to_bottom_surface_min_m": round(body_to_bottom, 9), "bidirectional_vertex_sampled_clearance_min_m": round(clearance, 9), "accepted_clearance_bounds_m": [0.001, 0.15], "maximum_neutral_bind_drift_m": round(drift, 9), "waist_hip_upper_leg_coverage_m": [round(min(z), 6), round(max(z), 6)]}


def build():
    source, body_manifest = custody()
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BODY_BLEND), load_ui=False)
    body, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if body is None or armature is None:
        raise RuntimeError("accepted body/armature missing")
    bottom = append_bottom(body_manifest, body)
    counts = bind(bottom, armature)
    proof = validate(body, bottom, armature, contract, import_contract)
    PROVENANCE.write_text("# Starter off-white bottom derivative provenance\n\n- Exact retained input: `Character | shorts leg continuous tailoring` (7,159 vertices / 7,040 polygons).\n- Exact accepted fit reference: Phase 1L.5bv body and twelve-bone armature.\n- Output adds exactly one `starter_offwhite_bottom`; cloth-only `Waist attachment` authority is excluded.\n- Clearance is bidirectional vertex-sampled distance to the opposite surface, not continuous triangle-distance proof.\n- No jacket, Action, FBX, Unreal import, runtime replacement, finished UV/material, final-art, performance, or readiness claim is included.\n", encoding="utf-8")
    semantic = {"body_semantic_sha256": BODY_SEMANTIC_SHA256, "body_mesh_sha256": BODY_MESH_SHA256, "bottom": {"item_id": BOTTOM_NAME, "source_object": SOURCE_OBJECT, "vertex_count": len(bottom.data.vertices), "polygon_count": len(bottom.data.polygons), "mesh_sha256": canonical_sha256(mesh_semantic(bottom)), "material_slots": [s.material.name for s in bottom.material_slots]}, "armature": {"bones": armature_semantic(armature), "dec035_mapping": import_contract["source_to_unreal_bone_names"]}, "weights": {"vertices_by_bone": counts, **proof}, "partitions": [BODY_NAME, BOTTOM_NAME], "actions": 0, "root_translation_m": rounded(armature.location)}
    semantic["identity_sha256"] = canonical_sha256(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    manifest = {"phase": "Phase 1L.5bx starter off-white bottom derivative neutral-bind proof", "status": "starter_bottom_only_neutral_bind_proof_not_runtime_or_final_art", "blender_version": bpy.app.version_string, "source_custody": source, "semantic": semantic, "files": {"blend": {"file": OUTPUT.name, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}}, "boundaries": {"bottom_partitions": 1, "top": 0, "jacket": 0, "actions": 0, "fbx": 0, "unreal_import": 0, "runtime_or_package_input_change": 0, "authority_change": 0, "finished_uv_or_material": 0, "final_art_claim": False, "performance_claim": False, "readiness_claim": False}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFINED_STARTER_BOTTOM_PASS vertices={len(bottom.data.vertices)} identity={semantic['identity_sha256']}")


def validate_saved():
    source, _body_manifest = custody()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["source_custody"] != source or manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, bottom, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(BOTTOM_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if None in (body, bottom, armature):
        raise RuntimeError("saved proof objects missing")
    validate(body, bottom, armature, json.loads(DEC034.read_text(encoding="utf-8")), json.loads(DEC035.read_text(encoding="utf-8")))
    if manifest["semantic"]["bottom"]["mesh_sha256"] != canonical_sha256(mesh_semantic(bottom)) or manifest["semantic"]["armature"]["bones"] != armature_semantic(armature):
        raise RuntimeError("saved semantic drift")
    print(f"REFINED_STARTER_BOTTOM_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


validate_saved() if "--validate" in sys.argv else build()
