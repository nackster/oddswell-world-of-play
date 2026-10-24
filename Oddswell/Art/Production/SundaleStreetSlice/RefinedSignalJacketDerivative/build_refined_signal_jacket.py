"""Build/validate the Phase 1L.5by consolidated Signal Jacket proof."""

import hashlib, json, sys
from pathlib import Path

import bpy
import bmesh
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
SLICE = ROOT.parent
BODY_DIR = SLICE / "RefinedHumanBodyDerivative"
TOP_DIR = SLICE / "RefinedStarterTopDerivative"
BOTTOM_DIR = SLICE / "RefinedStarterBottomDerivative"
SOURCE_BLEND = SLICE / "OddsWell_Sundale_StreetSlice.blend"
BODY_BLEND = BODY_DIR / "RefinedSundaleHumanBodyNeutralBind.blend"
BODY_CUSTODY = BODY_DIR / "neutral_bind_custody.json"
TOP_BLEND = TOP_DIR / "RefinedSundaleStarterTopNeutralBind.blend"
BOTTOM_BLEND = BOTTOM_DIR / "RefinedSundaleStarterBottomNeutralBind.blend"
DEC034 = REPO / "Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json"
DEC035 = REPO / "Oddswell/Art/Production/PlayerCharacter/character_unreal_import_contract.json"
OUTPUT = ROOT / "RefinedSundaleSignalJacketNeutralBind.blend"
MANIFEST = ROOT / "signal_jacket_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
BODY_NAME = "BODY__refined_sundale_derivative_v1"
JACKET_NAME = "sundale_signal_jacket"
ARMATURE_NAME = "ARMATURE__shared_bilateral_v1"
SOURCE_SHA = "0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127"
BODY_SHA = "83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB"
BODY_CUSTODY_SHA = "2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0"
BODY_SEMANTIC_SHA = "91AAB962825784679391C85FD06239A2F8EB118FEABA906EF9C5FB373FB8CF08"
BODY_MESH_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
TOP_SHA = "B06360F355AFFCA4E18802467186B3F8CFD4D5512C2BCE1B3A9AF66165F9C935"
BOTTOM_SHA = "18103E29F0D22B14A16457F3A61D49F9EFE48E388D8BF3AFD2AB67FE4F5798CA"
ALLOWED_BONES = {"spine", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def rounded(values):
    return [round(float(v), 6) for v in values]


def mesh_semantic(obj):
    return {"vertices": [rounded(v.co) for v in obj.data.vertices], "polygons": [list(p.vertices) for p in obj.data.polygons]}


def armature_semantic(obj):
    return {b.name: {"head_m": rounded(b.head_local), "tail_m": rounded(b.tail_local), "parent": b.parent.name if b.parent else None, "connected": b.use_connect} for b in sorted(obj.data.bones, key=lambda x: x.name)}


def accepted_source(name):
    return (
        name == "Character | tailored slate jacket"
        or name == "Character | standing collar"
        or name.startswith("Character | sleeve cuff")
        or name == "Character | sewn teal rear yoke"
        or name.startswith("Character | sleeve signal yoke")
        or name.startswith("Character | front zipper tape")
        or name.startswith("Character | zipper teeth")
        or name in {"Character | zipper slider", "Character | zipper pull loop"}
        or name.startswith("Character | yoke topstitch")
        or name.startswith("Character | jacket panel seam")
        or name.startswith("Character | rear jacket seam")
        or name.startswith("Character | sleeve seam")
    )


def custody():
    actual = {"source": sha256(SOURCE_BLEND), "body": sha256(BODY_BLEND), "body_custody": sha256(BODY_CUSTODY), "starter_top_unchanged": sha256(TOP_BLEND), "starter_bottom_unchanged": sha256(BOTTOM_BLEND)}
    expected = {"source": SOURCE_SHA, "body": BODY_SHA, "body_custody": BODY_CUSTODY_SHA, "starter_top_unchanged": TOP_SHA, "starter_bottom_unchanged": BOTTOM_SHA}
    if actual != expected:
        raise RuntimeError(f"custody drift: {actual}")
    body = json.loads(BODY_CUSTODY.read_text(encoding="utf-8"))
    if body["semantic"]["identity_sha256"] != BODY_SEMANTIC_SHA or body["semantic"]["body"]["mesh_sha256"] != BODY_MESH_SHA:
        raise RuntimeError("accepted body semantic drift")
    return actual, body


def build_jacket(body, body_manifest):
    with bpy.data.libraries.load(str(SOURCE_BLEND), link=False) as (src, dst):
        source_names = tuple(sorted(name for name in src.objects if accepted_source(name)))
        dst.objects = list(source_names)
    if "Character | tailored slate jacket" not in source_names or "Character | standing collar" not in source_names:
        raise RuntimeError(f"approved main shell/collar missing: {source_names[:20]}")
    included, objects = [], []
    bpy.ops.object.select_all(action="DESELECT")
    for source_index, (source_name, obj) in enumerate(zip(source_names, dst.objects)):
        if obj is None or obj.type not in {"MESH", "CURVE"}:
            raise RuntimeError(f"approved visible surface missing or wrong type: {source_name}")
        bpy.context.collection.objects.link(obj)
        obj["source_surface"] = source_name
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.type == "CURVE":
            bpy.ops.object.convert(target="MESH")
            obj = bpy.context.object
        world = obj.matrix_world.copy()
        for vertex in obj.data.vertices:
            vertex.co = world @ vertex.co
        obj.matrix_world.identity()
        for modifier in list(obj.modifiers):
            obj.modifiers.remove(modifier)
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        obj.data.materials.clear()
        marker = bpy.data.materials.new(f"SOURCE_LEDGER__{source_index:03d}")
        obj.data.materials.append(marker)
        for polygon in obj.data.polygons:
            polygon.material_index = 0
        included.append({"name": source_name, "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons)})
        objects.append(obj)
        obj.select_set(False)
    extraction = body_manifest["semantic"]["source_extraction"]
    low, high, scale = extraction["source_bounds_min_m"], extraction["source_bounds_max_m"], extraction["uniform_scale"]
    cx, cy = (low[0] + high[0]) / 2, (low[1] + high[1]) / 2
    bpy.context.view_layer.update()
    body_tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    for obj in objects:
        source_name = obj["source_surface"]
        offset = 0.052 if any(token in source_name for token in ("zipper", "topstitch", "seam")) else 0.045
        for vertex in obj.data.vertices:
            vertex.co.x = (vertex.co.x - cx) * scale
            vertex.co.y = (vertex.co.y - cy) * scale
            vertex.co.z = (vertex.co.z - low[2]) * scale
            point, normal, _face, _distance = body_tree.find_nearest(vertex.co)
            direction = vertex.co - point
            if direction.length < 1e-8:
                direction = normal
            vertex.co = point + direction.normalized() * offset
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    jacket = bpy.context.object
    jacket.name = JACKET_NAME
    jacket.data.name = "MESH__sundale_signal_jacket_proof"
    jacket["item_id"] = JACKET_NAME
    jacket["replaces_starter_top"] = True
    jacket["technical_proof_only"] = True
    removed = 0
    for _iteration in range(4):
        bpy.context.view_layer.update()
        overlap = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get()).overlap(BVHTree.FromObject(jacket, bpy.context.evaluated_depsgraph_get()))
        indices = {pair[1] for pair in overlap}
        if not indices:
            break
        edit = bmesh.new()
        edit.from_mesh(jacket.data)
        edit.faces.ensure_lookup_table()
        doomed = [edit.faces[index] for index in sorted(indices) if index < len(edit.faces)]
        removed += len(doomed)
        bmesh.ops.delete(edit, geom=doomed, context="FACES")
        loose_vertices = [vertex for vertex in edit.verts if not vertex.link_faces]
        if loose_vertices:
            bmesh.ops.delete(edit, geom=loose_vertices, context="VERTS")
        edit.to_mesh(jacket.data)
        edit.free()
        jacket.data.update()
    jacket["penetrating_source_faces_removed"] = removed
    retained = {index: 0 for index in range(len(included))}
    for polygon in jacket.data.polygons:
        retained[polygon.material_index] += 1
    for index, item in enumerate(included):
        item["removed_polygons"] = item["polygons"] - retained[index]
        item["retained_polygons"] = retained[index]
        if item["polygons"] and not item["retained_polygons"]:
            raise RuntimeError(f"approved visible contributor removed entirely: {item['name']}")
    jacket.data.materials.clear()
    slate = bpy.data.materials.new("MAT__signal_jacket_slate_proof")
    slate.diffuse_color = (0.026, 0.039, 0.055, 1.0)
    jacket.data.materials.append(slate)
    for polygon in jacket.data.polygons:
        polygon.material_index = 0
    return jacket, included, removed


def segment_distance(point, bone):
    segment = bone.tail_local - bone.head_local
    t = max(0.0, min(1.0, (point - bone.head_local).dot(segment) / segment.length_squared))
    return (point - (bone.head_local + segment * t)).length_squared


def bind(jacket, armature):
    bones = [b for b in armature.data.bones if b.name in ALLOWED_BONES]
    groups = {b.name: jacket.vertex_groups.new(name=b.name) for b in bones}
    counts = {b.name: 0 for b in bones}
    for vertex in jacket.data.vertices:
        owner = min(bones, key=lambda b: (segment_distance(vertex.co, b), b.name)).name
        groups[owner].add([vertex.index], 1.0, "REPLACE")
        counts[owner] += 1
    if any(v == 0 for v in counts.values()):
        raise RuntimeError(f"empty accepted jacket weight group: {counts}")
    mod = jacket.modifiers.new("ARMATURE__signal_jacket_neutral_bind", "ARMATURE")
    mod.object, mod.use_vertex_groups, mod.use_bone_envelopes = armature, True, False
    return counts


def validate(body, jacket, armature, contract, import_contract, included):
    if sorted(o.name for o in bpy.data.objects if o.type == "MESH") != sorted((BODY_NAME, JACKET_NAME)):
        raise RuntimeError("extra/missing visible mesh partition or starter-top layering")
    if {b.name for b in armature.data.bones} != set(import_contract["source_to_unreal_bone_names"]):
        raise RuntimeError("accepted bone set drift")
    if armature.location.length > 0 or any(abs(v - 1) > 1e-9 for v in armature.scale):
        raise RuntimeError("unauthorized root transform")
    if bpy.data.actions or body.animation_data or jacket.animation_data or armature.animation_data:
        raise RuntimeError("Actions/animation forbidden")
    if canonical_sha256(mesh_semantic(body)) != BODY_MESH_SHA:
        raise RuntimeError("accepted body mesh drift")
    body_z = [v.co.z for v in body.data.vertices]
    if abs(min(body_z)) > 1e-6 or abs(max(body_z) - contract["body"]["stature_m"]) > 1e-6:
        raise RuntimeError("body stature drift")
    names = {g.index: g.name for g in jacket.vertex_groups}
    unweighted = non_normalized = 0
    for vertex in jacket.data.vertices:
        influences = [(names[i.group], i.weight) for i in vertex.groups]
        unweighted += not influences
        non_normalized += abs(sum(w for _n, w in influences) - 1) > 1e-6
        if any(n not in ALLOWED_BONES for n, _w in influences):
            raise RuntimeError("unauthorized jacket influence")
    if unweighted or non_normalized:
        raise RuntimeError("weight completeness/normalization failure")
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    body_tree, jacket_tree = BVHTree.FromObject(body, dg), BVHTree.FromObject(jacket, dg)
    intersections = len(body_tree.overlap(jacket_tree))
    jacket_to_body = min(body_tree.find_nearest(jacket.matrix_world @ v.co)[3] for v in jacket.data.vertices)
    body_to_jacket = min(jacket_tree.find_nearest(body.matrix_world @ v.co)[3] for v in body.data.vertices)
    clearance = min(jacket_to_body, body_to_jacket)
    if intersections or not 0.00005 <= clearance <= 0.20:
        raise RuntimeError(f"body/jacket clearance failure: intersections={intersections}, clearance={clearance}")
    z = [v.co.z for v in jacket.data.vertices]
    x = [v.co.x for v in jacket.data.vertices]
    landmarks = contract["shared_landmarks_m"]
    if min(z) > landmarks["hip"] or max(z) < landmarks["shoulder"] or min(x) > -0.25 or max(x) < 0.25:
        raise RuntimeError("jacket torso/arm coverage drift")
    evaluated = jacket.evaluated_get(dg)
    mesh = evaluated.to_mesh()
    try:
        drift = max((mesh.vertices[i].co - jacket.data.vertices[i].co).length for i in range(len(mesh.vertices)))
    finally:
        evaluated.to_mesh_clear()
    if drift > 1e-6:
        raise RuntimeError(f"neutral/rest bind drift: {drift}")
    required = ("tailored slate jacket", "standing collar", "sleeve cuff", "rear yoke", "sleeve signal yoke", "front zipper tape", "zipper teeth", "zipper slider", "zipper pull loop")
    source_names = [item["name"] for item in included]
    if any(not any(token in name for name in source_names) for token in required):
        raise RuntimeError("approved visible inclusion ledger incomplete")
    topology = bmesh.new()
    topology.from_mesh(jacket.data)
    boundary_edges = sum(1 for edge in topology.edges if len(edge.link_faces) == 1)
    non_manifold_edges = sum(1 for edge in topology.edges if len(edge.link_faces) != 2)
    wire_edges = sum(1 for edge in topology.edges if not edge.link_faces)
    isolated_vertices = sum(1 for vertex in topology.verts if not vertex.link_edges)
    topology.free()
    if wire_edges or isolated_vertices:
        raise RuntimeError(f"orphan topology remains: wire={wire_edges}, isolated={isolated_vertices}")
    return {"unweighted_vertices": unweighted, "non_normalized_vertices": non_normalized, "body_intersection_pairs": intersections, "clearance_method": "bidirectional_mesh_vertex_to_opposite_surface_bvh", "clearance_is_continuous_triangle_distance": False, "jacket_vertex_to_body_surface_min_m": round(jacket_to_body, 9), "body_vertex_to_jacket_surface_min_m": round(body_to_jacket, 9), "bidirectional_vertex_sampled_clearance_min_m": round(clearance, 9), "accepted_clearance_bounds_m": [0.00005, 0.20], "maximum_neutral_bind_drift_m": round(drift, 9), "coverage_bounds_m": {"x": [round(min(x), 6), round(max(x), 6)], "z": [round(min(z), 6), round(max(z), 6)]}, "boundary_edges": boundary_edges, "non_manifold_edges": non_manifold_edges, "wire_edges": wire_edges, "isolated_vertices": isolated_vertices}


def build():
    source, body_manifest = custody()
    contract = json.loads(DEC034.read_text(encoding="utf-8"))
    import_contract = json.loads(DEC035.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BODY_BLEND), load_ui=False)
    body, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(ARMATURE_NAME)
    jacket, included, removed_faces = build_jacket(body, body_manifest)
    counts = bind(jacket, armature)
    proof = validate(body, jacket, armature, contract, import_contract, included)
    PROVENANCE.write_text("# Sundale Signal Jacket derivative provenance\n\n- Exact retained input: approved visible main shell, collar, cuffs, rear/sleeve yokes, zipper pieces, and the three yoke topstitch objects from the immutable Sundale source Blend. The source contains no separately named jacket-panel, rear-jacket, or sleeve-seam objects.\n- Exact accepted fit reference: Phase 1L.5bv body and twelve-bone armature.\n- Output is one separately replaceable `sundale_signal_jacket`; it replaces rather than layers over `starter_offwhite_top`.\n- Offline cloth pins/supports, hidden aids, Actions, clips, FBX, Unreal import, runtime replacement, material bake, final-art, performance, and readiness claims are excluded.\n", encoding="utf-8")
    semantic = {"body_semantic_sha256": BODY_SEMANTIC_SHA, "body_mesh_sha256": BODY_MESH_SHA, "jacket": {"item_id": JACKET_NAME, "vertex_count": len(jacket.data.vertices), "polygon_count": len(jacket.data.polygons), "penetrating_source_faces_removed": removed_faces, "mesh_sha256": canonical_sha256(mesh_semantic(jacket)), "material_slots": [s.material.name for s in jacket.material_slots], "replaces_starter_top": True}, "inclusion_ledger": included, "exclusion_ledger": ["starter_offwhite_top layering", "starter_offwhite_bottom mutation", "cloth pin groups", "offline collision/fitting/support aids", "hidden anatomy", "Actions/clips"], "armature": {"bones": armature_semantic(armature), "dec035_mapping": import_contract["source_to_unreal_bone_names"]}, "weights": {"vertices_by_bone": counts, **proof}, "partitions": [BODY_NAME, JACKET_NAME], "actions": 0, "root_translation_m": rounded(armature.location)}
    semantic["identity_sha256"] = canonical_sha256(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    manifest = {"phase": "Phase 1L.5by Sundale Signal Jacket consolidated neutral-bind proof", "status": "signal_jacket_only_neutral_bind_proof_not_runtime_or_final_art", "blender_version": bpy.app.version_string, "source_custody": source, "semantic": semantic, "files": {"blend": {"file": OUTPUT.name, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}}, "boundaries": {"jacket_partitions": 1, "starter_top_layered": 0, "bottom_mutated": 0, "actions_or_clips": 0, "fbx": 0, "unreal_import": 0, "runtime_or_package_input_change": 0, "authority_change": 0, "uv_material_bake": 0, "final_art_claim": False, "performance_claim": False, "readiness_claim": False}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFINED_SIGNAL_JACKET_PASS vertices={len(jacket.data.vertices)} identity={semantic['identity_sha256']}")


def validate_saved():
    source, _body_manifest = custody()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["source_custody"] != source or manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, jacket, armature = bpy.data.objects.get(BODY_NAME), bpy.data.objects.get(JACKET_NAME), bpy.data.objects.get(ARMATURE_NAME)
    if None in (body, jacket, armature):
        raise RuntimeError("saved proof objects missing")
    validate(body, jacket, armature, json.loads(DEC034.read_text(encoding="utf-8")), json.loads(DEC035.read_text(encoding="utf-8")), manifest["semantic"]["inclusion_ledger"])
    if manifest["semantic"]["jacket"]["mesh_sha256"] != canonical_sha256(mesh_semantic(jacket)) or manifest["semantic"]["armature"]["bones"] != armature_semantic(armature):
        raise RuntimeError("saved semantic drift")
    print(f"REFINED_SIGNAL_JACKET_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


validate_saved() if "--validate" in sys.argv else build()
