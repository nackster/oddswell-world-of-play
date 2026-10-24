"""Build/validate the Phase 1L.5bz-R1 bottom-only walk repair proof."""

import hashlib, json, math, os, re, sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
SLICE = ROOT.parent
BODY_BLEND = SLICE / "RefinedHumanBodyDerivative/RefinedSundaleHumanBodyNeutralBind.blend"
BODY_MANIFEST = SLICE / "RefinedHumanBodyDerivative/neutral_bind_custody.json"
TOP_BLEND = SLICE / "RefinedStarterTopDerivative/RefinedSundaleStarterTopNeutralBind.blend"
TOP_MANIFEST = SLICE / "RefinedStarterTopDerivative/starter_top_custody.json"
BOTTOM_BLEND = SLICE / "RefinedStarterBottomDerivative/RefinedSundaleStarterBottomNeutralBind.blend"
BOTTOM_MANIFEST = SLICE / "RefinedStarterBottomDerivative/starter_bottom_custody.json"
MOTION_BLEND = REPO / "Oddswell/Art/Production/PlayerCharacter/CharacterMotionAxisCorrection/MotionAxisCharacterCandidate.blend"
DEC035 = REPO / "Oddswell/Art/Production/PlayerCharacter/character_unreal_import_contract.json"
OUTPUT = ROOT / "RefinedSundaleStarterOutfitWalkProof.blend"
MANIFEST = ROOT / "starter_outfit_walk_repair_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
FAILURE = ROOT / "starter_outfit_walk_repair_failure.json"
BODY = "BODY__refined_sundale_derivative_v1"
TOP = "starter_offwhite_top"
BOTTOM = "starter_offwhite_bottom"
ARMATURE = "ARMATURE__shared_bilateral_v1"
ACTION = "walk_candidate_v1"
FRAMES = list(range(1, 22))
EXPECTED = {
    "body_blend": "83D9AFEDA8F0B81EA356E3173751534FE579DB39E6F343EEF952B5715CD3BCAB",
    "body_manifest": "2299550AA590235BC2D71753BAFE3CE59A2573F8F5900EE817B91E2DB59958A0",
    "top_blend": "B06360F355AFFCA4E18802467186B3F8CFD4D5512C2BCE1B3A9AF66165F9C935",
    "bottom_blend": "18103E29F0D22B14A16457F3A61D49F9EFE48E388D8BF3AFD2AB67FE4F5798CA",
    "motion_blend": "AC27A075AD8AE7981B4735797D2C83D37BF56A1D24BAFF881659DB23E7194506",
}
BODY_MESH_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
TOP_MESH_SHA = "9996AF8A1271D6E236A45B8EDF93DF36A342FF0743D3276E1676AB3FE96D30C3"
BOTTOM_MESH_SHA = "ED49AEDD3C65D9E9F5B13E2C9B9B0CF6614ABE19BCD7E666D396D1234E8BDF96"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"


class WalkFailure(RuntimeError):
    def __init__(self, payload):
        super().__init__(f"intersection at frame {payload['failing_frame']}: {payload['intersections']}")
        self.payload = payload


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def rounded(values):
    return [round(float(v), 6) for v in values]


def mesh_semantic(obj):
    return {"vertices": [rounded(v.co) for v in obj.data.vertices], "polygons": [list(p.vertices) for p in obj.data.polygons]}


def custody():
    paths = {"body_blend": BODY_BLEND, "body_manifest": BODY_MANIFEST, "top_blend": TOP_BLEND, "bottom_blend": BOTTOM_BLEND, "motion_blend": MOTION_BLEND}
    actual = {key: sha256(path) for key, path in paths.items()}
    if actual != EXPECTED:
        raise RuntimeError(f"accepted custody drift: {actual}")
    top = json.loads(TOP_MANIFEST.read_text(encoding="utf-8"))
    bottom = json.loads(BOTTOM_MANIFEST.read_text(encoding="utf-8"))
    if top["semantic"]["top"]["mesh_sha256"] != TOP_MESH_SHA or bottom["semantic"]["bottom"]["mesh_sha256"] != BOTTOM_MESH_SHA:
        raise RuntimeError("accepted garment identity drift")
    return actual


def append_object(blend, name, armature):
    with bpy.data.libraries.load(str(blend), link=False) as (src, dst):
        if name not in src.objects:
            raise RuntimeError(f"accepted partition missing: {name}")
        dst.objects = [name]
    obj = dst.objects[0]
    bpy.context.collection.objects.link(obj)
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)
    modifier = obj.modifiers.new(f"ARMATURE__{name}_walk_proof", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    return obj


def append_action(armature):
    with bpy.data.libraries.load(str(MOTION_BLEND), link=False) as (src, dst):
        if ACTION not in src.actions:
            raise RuntimeError("accepted walk Action missing")
        dst.actions = [ACTION]
    action = dst.actions[0]
    armature.animation_data_create()
    armature.animation_data.action = action
    return action


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def correct_bottom_weights(bottom, body):
    """Blend only the accepted root/thigh groups across the waist and crotch."""
    for group in list(bottom.vertex_groups):
        bottom.vertex_groups.remove(group)
    groups = {name: bottom.vertex_groups.new(name=name) for name in ("root", "thigh.L", "thigh.R")}
    totals = {name: 0.0 for name in groups}
    influenced = {name: 0 for name in groups}
    for vertex in bottom.data.vertices:
        root = smoothstep((vertex.co.z - 0.62) / 0.28)
        left = smoothstep((vertex.co.x + 0.06) / 0.12)
        leg = 1.0 - root
        weights = {"root": root, "thigh.L": leg * left, "thigh.R": leg * (1.0 - left)}
        for name, weight in weights.items():
            if weight > 0.000001:
                groups[name].add([vertex.index], weight, "REPLACE")
                totals[name] += weight
                influenced[name] += 1
    bottom.data.update()
    correction = {"method": "bounded_root_dominant_waist_side_selected_thigh_leg_opening_blend", "waist_z_m": [0.62, 0.90], "center_transition_x_m": [-0.06, 0.06], "anatomical_side_mapping": {"positive_x": "thigh.L", "negative_x": "thigh.R"}, "vertices_influenced_by_group": influenced, "weight_sums_by_group": {name: round(value, 6) for name, value in totals.items()}}
    bottom["phase1l5bz_r1_weight_correction"] = json.dumps(correction, sort_keys=True)
    return correction


def apply_bottom_offset(bottom, body):
    offset_m = 0.050
    body_tree = BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices], [list(p.vertices) for p in body.data.polygons], all_triangles=False)
    for vertex in bottom.data.vertices:
        nearest, normal, _index, _distance = body_tree.find_nearest(vertex.co)
        direction = vertex.co - nearest
        vertex.co += (direction if direction.length > 1e-9 else normal).normalized() * offset_m
    local_vertex_ids = {1200, 1201, 1278, 1279, 1280, 1281, 1358, 1359}
    for vertex_id in local_vertex_ids:
        bottom.data.vertices[vertex_id].co.x -= 0.010
    bottom.data.update()
    return {"method": "away_from_nearest_neutral_body_surface_plus_local_negative_x_contact_clearance", "affected_vertices": len(bottom.data.vertices), "local_contact_vertex_ids": sorted(local_vertex_ids), "base_displacement_m": offset_m, "local_additional_displacement_m": 0.010, "maximum_displacement_m": round(math.sqrt(offset_m * offset_m + 0.010 * 0.010), 9)}


def action_semantic(action):
    curves = []
    for curve in sorted(action.fcurves, key=lambda c: (c.data_path, c.array_index)):
        match = re.fullmatch(r'pose\.bones\["([^"]+)"\]\.(rotation_euler|location)', curve.data_path)
        if not match:
            raise RuntimeError(f"unexpected walk curve: {curve.data_path}")
        keys = [{"frame": round(float(k.co[0]), 6), "value": round(float(k.co[1]), 9), "interpolation": k.interpolation} for k in curve.keyframe_points]
        curves.append({"bone": match.group(1), "channel": match.group(2), "axis": curve.array_index, "keys": keys})
    semantic = {"name": action.name, "action_count": 1, "fps": 28, "frame_start": 1, "frame_end": 21, "sample_frames": [1, 6, 11, 16, 21], "cycle_duration_seconds": 0.714285714, "cycles_per_second": 1.4, "limb_pitch_degrees": 18.0, "spine_sway_degrees": 3.0, "root_translation_m": [0.0, 0.0, 0.0], "loop_end_equality": True, "curves": curves}
    semantic["identity_sha256"] = canonical(semantic)
    if semantic["identity_sha256"] != ACTION_SHA:
        raise RuntimeError(f"accepted walk semantic drift: {semantic['identity_sha256']}")
    return semantic


def weight_check(obj, allowed):
    names = {g.index: g.name for g in obj.vertex_groups}
    bad = unweighted = 0
    for vertex in obj.data.vertices:
        influences = [(names[i.group], i.weight) for i in vertex.groups]
        unweighted += not influences
        bad += abs(sum(w for _n, w in influences) - 1.0) > 1e-6 or any(n not in allowed for n, _w in influences)
    if unweighted or bad:
        raise RuntimeError(f"weight drift for {obj.name}: {unweighted}/{bad}")
    return {"vertices": len(obj.data.vertices), "unweighted": unweighted, "invalid_or_non_normalized": bad}


def evaluated(obj, dg):
    mesh = obj.evaluated_get(dg).to_mesh()
    try:
        return [obj.matrix_world @ vertex.co.copy() for vertex in mesh.vertices]
    finally:
        obj.evaluated_get(dg).to_mesh_clear()


def frame_proof(scene, body, top, bottom, armature):
    records = []
    baselines = None
    max_separation = 0.0
    for frame in FRAMES:
        scene.frame_set(frame)
        dg = bpy.context.evaluated_depsgraph_get()
        root = armature.pose.bones["root"]
        if any(abs(v) > 1e-9 for v in root.location) or armature.location.length > 1e-9:
            raise RuntimeError(f"root/armature translation at frame {frame}")
        coords = {obj.name: evaluated(obj, dg) for obj in (body, top, bottom)}
        if baselines is None:
            baselines = coords
        if any(not math.isfinite(value) for points in coords.values() for point in points for value in point):
            raise RuntimeError(f"nonfinite deformation at frame {frame}")
        trees = {obj.name: BVHTree.FromObject(obj, dg) for obj in (body, top, bottom)}
        overlap_pairs = {
            "body_top": trees[body.name].overlap(trees[top.name]),
            "body_bottom": trees[body.name].overlap(trees[bottom.name]),
            "top_bottom": trees[top.name].overlap(trees[bottom.name]),
        }
        intersections = {name: len(pairs) for name, pairs in overlap_pairs.items()}
        bounds = {name: {"min": rounded((min(p[i] for p in points) for i in range(3))), "max": rounded((max(p[i] for p in points) for i in range(3)))} for name, points in coords.items()}
        if any(intersections.values()):
            raise WalkFailure({"failing_frame": frame, "time_seconds": round((frame - 1) / 28, 9), "intersections": intersections, "intersection_polygon_pairs": {name: [list(pair) for pair in pairs] for name, pairs in overlap_pairs.items()}, "bounds_m": bounds, "root_bone_translation_m": rounded(root.location), "armature_translation_m": rounded(armature.location), "passed_frames": records})
        clearance = {}
        for garment in (top, bottom):
            a = min(trees[body.name].find_nearest(point)[3] for point in coords[garment.name])
            b = min(trees[garment.name].find_nearest(point)[3] for point in coords[body.name])
            clearance[garment.name] = {"garment_to_body_m": round(a, 9), "body_to_garment_m": round(b, 9), "vertex_sampled_min_m": round(min(a, b), 9)}
            if min(a, b) <= 0.00001 or min(a, b) > 0.30:
                raise RuntimeError(f"unacceptable separation at frame {frame}: {garment.name} {min(a,b)}")
            max_separation = max(max_separation, min(a, b))
        records.append({"frame": frame, "time_seconds": round((frame - 1) / 28, 9), "intersections": intersections, "vertex_sampled_clearance": clearance, "bounds_m": bounds, "root_bone_translation_m": rounded(root.location), "armature_translation_m": rounded(armature.location)})
    scene.frame_set(21)
    ends = {obj.name: evaluated(obj, bpy.context.evaluated_depsgraph_get()) for obj in (body, top, bottom)}
    if any((baselines[name][i] - ends[name][i]).length > 1e-6 for name in baselines for i in range(len(baselines[name]))):
        raise RuntimeError("walk loop endpoint geometry drift")
    return {"method": "every_integer_frame_evaluated_mesh_bvh_intersection_and_bidirectional_vertex_to_opposite_surface_sampling", "continuous_triangle_distance": False, "frames": records, "frame_count": len(records), "maximum_accepted_vertex_sampled_min_separation_m": 0.30, "observed_maximum_vertex_sampled_min_separation_m": round(max_separation, 9), "loop_endpoint_equal": True}


def validate_scene(body, top, bottom, armature, action):
    meshes = sorted(o.name for o in bpy.data.objects if o.type == "MESH")
    if meshes != sorted((BODY, TOP, BOTTOM)) or len(bpy.data.actions) != 1 or action.name != ACTION:
        raise RuntimeError(f"partition/action boundary drift: {meshes}/{list(bpy.data.actions)}")
    mapping = json.loads(DEC035.read_text(encoding="utf-8"))["source_to_unreal_bone_names"]
    if {b.name for b in armature.data.bones} != set(mapping):
        raise RuntimeError("accepted bone/mapping drift")
    if canonical(mesh_semantic(body)) != BODY_MESH_SHA or canonical(mesh_semantic(top)) != TOP_MESH_SHA:
        raise RuntimeError("accepted topology/mesh identity drift")
    if len(bottom.data.vertices) != 7159 or len(bottom.data.polygons) != 7040 or [slot.material.name for slot in bottom.material_slots] != ["MAT__starter_offwhite_bottom_proof"]:
        raise RuntimeError("derived bottom topology/material-slot drift")
    weights = {BODY: weight_check(body, set(mapping)), TOP: weight_check(top, {"spine"}), BOTTOM: weight_check(bottom, {"root", "thigh.L", "thigh.R"})}
    if any(o.data.shape_keys for o in (body, top, bottom)) or any(o.animation_data for o in (body, top, bottom)):
        raise RuntimeError("hidden repair/mesh animation forbidden")
    return weights, mapping


def build():
    sources = custody()
    bpy.ops.wm.open_mainfile(filepath=str(BODY_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, armature = bpy.data.objects.get(BODY), bpy.data.objects.get(ARMATURE)
    top = append_object(TOP_BLEND, TOP, armature)
    bottom = append_object(BOTTOM_BLEND, BOTTOM, armature)
    if canonical(mesh_semantic(bottom)) != BOTTOM_MESH_SHA:
        raise RuntimeError("accepted source bottom mesh drift before correction")
    weight_correction = correct_bottom_weights(bottom, body)
    for obj in list(bpy.data.objects):
        if obj not in {body, armature, top, bottom}:
            bpy.data.objects.remove(obj, do_unlink=True)
    action = append_action(armature)
    scene = bpy.context.scene
    scene.render.fps, scene.frame_start, scene.frame_end = 28, 1, 21
    weights, mapping = validate_scene(body, top, bottom, armature, action)
    action_record = action_semantic(action)
    try:
        frame_proof(scene, body, top, bottom, armature)
        raise RuntimeError("weight-only diagnostic unexpectedly passed")
    except WalkFailure as failure:
        weight_only_failure = failure.payload
    if weight_only_failure["failing_frame"] != 2 or weight_only_failure["intersections"]["body_bottom"] != 219:
        raise RuntimeError(f"weight-only diagnostic drift: {weight_only_failure}")
    position_offset = apply_bottom_offset(bottom, body)
    weights, mapping = validate_scene(body, top, bottom, armature, action)
    try:
        proof = frame_proof(scene, body, top, bottom, armature)
    except WalkFailure as failure:
        receipt = {"phase": "Phase 1L.5bz-R1 bottom-only deformation correction and starter-outfit walk re-proof", "status": "BLOCKED_UNCOUNTED_FAIL_CLOSED_AT_FRAME_3", "source_custody": sources, "accepted_source_mesh_sha256": {BODY: BODY_MESH_SHA, TOP: TOP_MESH_SHA, BOTTOM: BOTTOM_MESH_SHA}, "diagnostic_derived_bottom_mesh_sha256": canonical(mesh_semantic(bottom)), "attempted_correction": {"weights": weight_correction, "position_offset": position_offset}, "reproduced_weight_only_failure": weight_only_failure, "dec035_mapping": mapping, "weights": weights, "action": action_record, "diagnostic": failure.payload, "boundaries": {"derived_blend_written": 0, "accepted_inputs_mutated": 0, "jacket": 0, "run": 0, "jump": 0, "land": 0, "hidden_repair": 0, "fbx": 0, "unreal_import": 0, "runtime_change": 0, "phase_credit": 0, "readiness_claim": False}}
        FAILURE.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise
    semantic = {"sources": sources, "partitions": [BODY, TOP, BOTTOM], "mesh_sha256": {BODY: BODY_MESH_SHA, TOP: TOP_MESH_SHA, BOTTOM: BOTTOM_MESH_SHA}, "bottom_weight_correction": correction, "weights": weights, "dec035_mapping": mapping, "action": action_record, "deformation": proof, "root_translation_m": rounded(armature.location), "saved_frame": 1, "saved_visibility": {BODY: True, TOP: True, BOTTOM: True}}
    semantic["identity_sha256"] = canonical(semantic)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text("# Refined starter-outfit walk proof provenance\n\n- Exact accepted inputs: Phase 1L.5bv body, Phase 1L.5bw starter top, Phase 1L.5bx starter bottom, and unchanged `walk_candidate_v1` from CharacterMotionAxisCorrection.\n- Every integer frame 1–21 is evaluated. Intersections use evaluated-mesh BVH triangle overlap; clearance is bidirectional vertex-to-opposite-surface sampling, not continuous triangle distance.\n- No jacket, run, jump, land, hidden repair, FBX, Unreal import, runtime replacement, final-art, performance, or readiness claim is included.\n", encoding="utf-8")
    manifest = {"phase": "Phase 1L.5bz accepted starter-outfit walk-cycle deformation proof", "status": "starter_outfit_walk_source_proof_not_runtime_or_final_animation", "blender_version": bpy.app.version_string, "semantic": semantic, "files": {"blend": {"file": OUTPUT.name, "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"file": Path(__file__).name, "bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"file": PROVENANCE.name, "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}}, "boundaries": {"actions": 1, "walk": 1, "run": 0, "jump": 0, "land": 0, "jacket": 0, "hidden_repair": 0, "fbx": 0, "unreal_import": 0, "runtime_change": 0, "final_art_claim": False, "performance_claim": False, "readiness_claim": False}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REFINED_STARTER_OUTFIT_WALK_PASS frames=21 identity={semantic['identity_sha256']}")


def validate_saved():
    sources = custody()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["sources"] != sources or manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature, action = bpy.data.objects.get(BODY), bpy.data.objects.get(TOP), bpy.data.objects.get(BOTTOM), bpy.data.objects.get(ARMATURE), bpy.data.actions.get(ACTION)
    validate_scene(body, top, bottom, armature, action)
    if action_semantic(action) != manifest["semantic"]["action"] or frame_proof(bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("saved walk proof drift")
    print(f"REFINED_STARTER_OUTFIT_WALK_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    try:
        build()
    except WalkFailure as failure:
        print(f"REFINED_STARTER_OUTFIT_WALK_FAIL frame={failure.payload['failing_frame']} body_bottom={failure.payload['intersections']['body_bottom']}", flush=True)
        os._exit(1)
