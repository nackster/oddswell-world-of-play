"""Build or validate the Phase 1L.5cs side/underarm-to-hem correction proof."""

from pathlib import Path


UPSTREAM = Path(__file__).resolve().parent.parent / "YokeCapTransitionBlendCorrectionWalkProof/build_yoke_cap_transition_blend_walk.py"
upstream_source = UPSTREAM.read_text(encoding="utf-8")
exec(upstream_source[: upstream_source.rfind('if "--validate"')], globals())

SOURCE_ROOT = SLICE / "YokeCapTransitionBlendCorrectionWalkProof"
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleYokeCapTransitionBlendedTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "yoke_cap_transition_blend_walk_custody.json"
CAP_MANIFEST = SLICE / "OuterSleeveArmholeRoundedCapWalkProof/outer_sleeve_armhole_rounded_cap_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleSideUnderarmHemTransitionTopWalk.blend"
MANIFEST = ROOT / "side_underarm_hem_transition_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
SOURCE_TOP_SHA = "EAB37355BDA56874B10BCA2BEE45BD4FDAFAE9F0B7B7826BFDBA85C1BB9807E8"
SOURCE_IDENTITY = "D9ABDAF676F2352EA8629EE4FC375A1F5567830AD5D721093669D942CB91F78A"
SOURCE_BLEND_SHA = "A256E5F7B1B0750623A9B9F9B5085A45850AE1E525B0CD32F07447C791568A1E"

# Explicit bilateral source pairs. The ledger is intentionally small and fixed:
# it follows only the side transition strip from the lower torso into the underarm.
TARGET_PAIRS = (
    (29, 84), (34, 87),
    (174, 273), (178, 276),
    (180, 307), (183, 308),
    (181, 306), (185, 309),
    (182, 279), (184, 280),
    (36, 88), (37, 89),
    (153, 311), (156, 312),
    (187, 283), (188, 284),
    (38, 90), (39, 91),
    (186, 310), (189, 313),
    (191, 287), (192, 288),
    (159, 315), (160, 316),
)
TARGET = frozenset(index for pair in TARGET_PAIRS for index in pair)
HEM_WEIGHT_PAIRS = (
    (30, 85), (33, 86),
    (204, 274), (205, 275),
    (175, 302), (177, 303),
    (31, 101), (32, 102),
)
WEIGHT_TARGET = TARGET | frozenset(index for pair in HEM_WEIGHT_PAIRS for index in pair)


def source_custody():
    accepted = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    semantic = accepted["semantic"]
    checks = (
        semantic["identity_sha256"] == SOURCE_IDENTITY,
        semantic["accepted_mesh_sha256"][BODY] == BODY_SHA,
        semantic["derived_mesh_sha256"][TOP] == SOURCE_TOP_SHA,
        semantic["accepted_mesh_sha256"][BOTTOM] == BOTTOM_SHA,
        semantic["action"]["identity_sha256"] == ACTION_SHA,
        semantic["armature"]["bone_count"] == 12,
        receipt(SOURCE_BLEND) == accepted["files"]["blend"],
        accepted["files"]["blend"]["sha256"] == SOURCE_BLEND_SHA,
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5cq custody drift")
    depth = json.loads(DEPTH_MANIFEST.read_text(encoding="utf-8"))
    waist = json.loads(WAIST_MANIFEST.read_text(encoding="utf-8"))
    cap = json.loads(CAP_MANIFEST.read_text(encoding="utf-8"))
    return accepted, depth, waist, cap


def apply_correction(top, accepted, depth, waist, cap):
    before_coordinates = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    before_weights = rounded["weight_semantic"](top)
    before_groups = [group.name for group in top.vertex_groups]
    protected_coordinates = set(before_coordinates) - TARGET
    protected_weights = set(before_coordinates) - WEIGHT_TARGET
    depth_target = set(depth["semantic"]["correction"]["target_vertex_indices"])
    waist_target = set(waist["semantic"]["correction"]["target_vertex_indices"])
    cap_target = set(cap["semantic"]["correction"]["target_vertex_indices"])
    yoke_target = set(accepted["semantic"]["correction"]["target_vertex_indices"])
    openings = boundary_indices(top)
    if len(TARGET) != 48 or len(WEIGHT_TARGET) != 64 or TARGET & protected_coordinates or WEIGHT_TARGET & protected_weights or TARGET & depth_target or TARGET & cap_target or TARGET & yoke_target or TARGET & openings:
        raise RuntimeError("declared target ledger overlaps a protected feature")

    spine = top.vertex_groups["spine"]
    left = top.vertex_groups["upper_arm.L"]
    right = top.vertex_groups["upper_arm.R"]
    for index in TARGET:
        vertex = top.data.vertices[index]
        x, y, z = vertex.co
        height = base["smoothstep"]((z - 1.05) / 0.30)
        lateral = base["smoothstep"]((abs(x) - 0.22) / 0.17)
        depth_scale = 0.90 + 0.06 * height + 0.02 * lateral
        lateral_inset = 0.008 + 0.012 * lateral + 0.008 * height
        vertex.co.x = math.copysign(abs(x) - lateral_inset, x)
        vertex.co.y = 0.02 + (y - 0.02) * depth_scale
    for index in WEIGHT_TARGET:
        vertex = top.data.vertices[index]
        x, _, z = vertex.co
        if index in TARGET:
            height = base["smoothstep"]((z - 1.05) / 0.30)
            lateral = base["smoothstep"]((abs(x) - 0.22) / 0.17)
            arm_weight = 0.025 + 0.055 * lateral + 0.015 * height
        else:
            arm_weight = 0.0
        arm = left if x > 0 else right
        other = right if x > 0 else left
        spine.add([index], 1.0 - arm_weight, "REPLACE")
        arm.add([index], arm_weight, "REPLACE")
        try:
            other.remove([index])
        except RuntimeError:
            pass
    top.data.update()

    after_weights = rounded["weight_semantic"](top)
    if [group.name for group in top.vertex_groups] != before_groups:
        raise RuntimeError("vertex-group drift")
    if coordinates(top, protected_coordinates) != coordinates_from_map(before_coordinates, protected_coordinates):
        raise RuntimeError("protected coordinate drift")
    if [after_weights[index] for index in sorted(protected_weights)] != [before_weights[index] for index in sorted(protected_weights)]:
        raise RuntimeError("protected weight drift")
    if any(abs(sum(weight for _, weight in after_weights[index]) - 1.0) > 1e-6 for index in WEIGHT_TARGET):
        raise RuntimeError("target weights are not normalized")
    for left_index, right_index in TARGET_PAIRS:
        if before_coordinates[left_index][0] >= 0 or before_coordinates[right_index][0] <= 0:
            raise RuntimeError("target pair side drift")
        for index, expected_arm in ((left_index, "upper_arm.R"), (right_index, "upper_arm.L")):
            if {name for name, _ in after_weights[index]} - {"spine", expected_arm}:
                raise RuntimeError("target contains a non-matching influence")
    for left_index, right_index in HEM_WEIGHT_PAIRS:
        for index, expected_arm in ((left_index, "upper_arm.R"), (right_index, "upper_arm.L")):
            if {name for name, _ in after_weights[index]} - {"spine", expected_arm}:
                raise RuntimeError("hem target contains a non-matching influence")

    changed_coordinates = {index for index in TARGET if tuple(top.data.vertices[index].co) != before_coordinates[index]}
    changed_weights = {index for index in WEIGHT_TARGET if after_weights[index] != before_weights[index]}
    if changed_coordinates != TARGET or changed_weights != WEIGHT_TARGET:
        raise RuntimeError("every declared target must change coordinates and weights")
    if any(top.data.vertices[index].co.z != before_coordinates[index][2] for index in TARGET):
        raise RuntimeError("target changed a Z coordinate")
    if coordinates(top, depth_target) != coordinates_from_map(before_coordinates, depth_target):
        raise RuntimeError("accepted central depth taper drift")
    if any(abs(top.data.vertices[index].co.x) > abs(before_coordinates[index][0]) for index in TARGET & waist_target):
        raise RuntimeError("accepted lateral waist taper regressed outward")

    body_bounds = accepted["semantic"]["deformation"]["frames"][0]["bounds_m"][BODY]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    source_width = max(value[0] for value in before_coordinates.values()) - min(value[0] for value in before_coordinates.values())
    derived_width = max(vertex.co.x for vertex in top.data.vertices) - min(vertex.co.x for vertex in top.data.vertices)
    ratio = derived_width / body_width
    if derived_width != source_width or round(derived_width, 9) != 0.930000007 or round(ratio, 9) != 1.377059677:
        raise RuntimeError("accepted width/ratio drift")
    coordinate_displacements = [math.dist(before_coordinates[index], top.data.vertices[index].co) for index in TARGET]
    weight_deltas = [
        max(abs(dict(before_weights[index]).get(name, 0.0) - dict(after_weights[index]).get(name, 0.0)) for name in {"spine", "upper_arm.L", "upper_arm.R"})
        for index in WEIGHT_TARGET
    ]
    return {
        "approved_symmetric_target_pairs": [list(pair) for pair in TARGET_PAIRS],
        "approved_symmetric_hem_weight_pairs": [list(pair) for pair in HEM_WEIGHT_PAIRS],
        "target_vertex_count": len(TARGET),
        "target_vertex_indices": sorted(TARGET),
        "coordinate_changed_vertex_count": len(changed_coordinates),
        "coordinate_changed_vertex_indices": sorted(changed_coordinates),
        "weight_target_vertex_count": len(WEIGHT_TARGET),
        "weight_changed_vertex_count": len(changed_weights),
        "weight_changed_vertex_indices": sorted(changed_weights),
        "protected_coordinate_vertex_count": len(protected_coordinates),
        "protected_coordinate_vertex_indices": sorted(protected_coordinates),
        "protected_weight_vertex_count": len(protected_weights),
        "protected_weight_vertex_indices": sorted(protected_weights),
        "target_protected_overlap_count": len(TARGET & protected_coordinates) + len(WEIGHT_TARGET & protected_weights),
        "target_depth_taper_overlap_count": len(TARGET & depth_target),
        "target_waist_taper_overlap_count": len(TARGET & waist_target),
        "target_outer_cap_overlap_count": len(TARGET & cap_target),
        "target_yoke_overlap_count": len(TARGET & yoke_target),
        "coordinate_target_opening_boundary_overlap_count": len(TARGET & openings),
        "weight_target_opening_boundary_count": len(WEIGHT_TARGET & openings),
        "source_target_coordinates": coordinates_from_map(before_coordinates, TARGET),
        "derived_target_coordinates": coordinates(top, TARGET),
        "source_target_coordinate_sha256": semantic_sha(coordinates_from_map(before_coordinates, TARGET)),
        "derived_target_coordinate_sha256": semantic_sha(coordinates(top, TARGET)),
        "source_protected_coordinate_sha256": semantic_sha(coordinates_from_map(before_coordinates, protected_coordinates)),
        "derived_protected_coordinate_sha256": semantic_sha(coordinates(top, protected_coordinates)),
        "source_target_weights": [[index, before_weights[index]] for index in sorted(WEIGHT_TARGET)],
        "derived_target_weights": [[index, after_weights[index]] for index in sorted(WEIGHT_TARGET)],
        "source_target_weight_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(WEIGHT_TARGET)]),
        "derived_target_weight_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(WEIGHT_TARGET)]),
        "source_protected_weight_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(protected_weights)]),
        "derived_protected_weight_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(protected_weights)]),
        "vertex_groups_added": 0,
        "target_weight_sum": 1.0,
        "maximum_coordinate_displacement_m": round(max(coordinate_displacements), 9),
        "maximum_influence_delta": round(max(weight_deltas), 9),
        "source_top_width_m": round(source_width, 9),
        "derived_top_width_m": round(derived_width, 9),
        "body_width_m": round(body_width, 9),
        "derived_top_to_body_width_ratio": round(ratio, 9),
        "preserved_shape_contract": {"central_depth_target_coordinates_exact": True, "waist_taper_outward_regressions": 0, "all_target_z_exact": True},
    }


def transition_metrics(scene, top):
    hem = {index for index in boundary_indices(top) if top.data.vertices[index].co.z < 1.01}
    profile_depth = max(top.data.vertices[index].co.y for index in TARGET) - min(top.data.vertices[index].co.y for index in TARGET)
    values = {"neutral_profile_target_depth_span_m": round(profile_depth, 9)}
    for frame in (6, 16):
        scene.frame_set(frame)
        evaluated = top.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        if frame == 6:
            values["frame_6_left_target_extent_m"] = round(abs(min(evaluated[index].co.x for index in TARGET if top.data.vertices[index].co.x < 0)), 9)
        else:
            values["frame_16_right_target_extent_m"] = round(max(evaluated[index].co.x for index in TARGET if top.data.vertices[index].co.x > 0), 9)
        values[f"frame_{frame}_hem_z_range_m"] = round(max(evaluated[index].co.z for index in hem) - min(evaluated[index].co.z for index in hem), 9)
    scene.frame_set(1)
    return values


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    receipts = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["files"]["reviews"]
    for name in VIEWS:
        path = SOURCE_ROOT / "Review" / f"After_{name}.png"
        if receipt(path) != receipts[f"After_{name}.png"]:
            raise RuntimeError(f"source review drift: {name}")
        shutil.copyfile(path, REVIEWS / f"Before_{name}.png")
    renderer["REVIEWS"] = REVIEWS
    renderer["render_reviews"]()
    for name in VIEWS:
        (REVIEWS / f"{name}.png").replace(REVIEWS / f"After_{name}.png")
    rows = "\n".join(
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5cq</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5cs</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5cs before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5cs side / underarm-to-hem transition correction</h1>'
        '<p>Targeted offline walk proof only; no acceptance verdict.</p>' + rows,
        encoding="utf-8",
    )
    return {path.name: receipt(path) for path in sorted(REVIEWS.glob("*")) if path.is_file()}


def build():
    accepted, depth, waist, cap = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    before = {
        "body": semantic_sha(base["mesh_semantic"](body)), "top": semantic_sha(base["mesh_semantic"](top)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)), "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]), "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top), "item_id": top.get("item_id"), "openings": renderer["opening_proof"](top),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    source_metrics = transition_metrics(bpy.context.scene, top)
    correction = apply_correction(top, accepted, depth, waist, cap)
    derived_metrics = transition_metrics(bpy.context.scene, top)
    if any(derived_metrics[key] >= source_metrics[key] for key in source_metrics):
        raise RuntimeError("named profile/bulge/spike/hem metric did not improve")
    correction["named_issue_metrics"] = {"source": source_metrics, "derived": derived_metrics}
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)), "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature), "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top), "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"), "openings": renderer["opening_proof"](top),
    }
    for key in ("body", "bottom", "armature", "action", "materials", "topology", "item_id", "openings"):
        if after[key] != before[key]:
            raise RuntimeError(f"non-target identity drift: {key}")
    topology = {TOP: r3["topology_proof"](top, (1, 4, 0), "side-transition corrected starter top"), BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts")}
    weights = {TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}), BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    if any(any(value for value in row["intersections"].values()) for row in deformation["frames"]):
        raise RuntimeError("walk proof contains evaluated intersections")
    if not deformation["loop_endpoint_equal"] or any(row["root_bone_translation_m"] != [0.0, 0.0, 0.0] or row["armature_translation_m"] != [0.0, 0.0, 0.0] for row in deformation["frames"]):
        raise RuntimeError("walk translation or endpoint drift")
    semantic = {
        "accepted_phase_1l5cq": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA}, "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))}, "correction": correction,
        "construction": {"method": "predeclared_bilateral_side_transition_coordinate_and_normalized_matching_arm_blend", "excluded": ["target_z", "non_target_coordinates_and_weights", "central_pattern_and_depth_taper", "waist_taper_outward_regression", "neckline_yoke_outer_caps", "all_opening_geometry", "topology", "item_material_color", "body", "shorts", "skeleton", "action"]},
        "topology": topology, "opening_geometry": {"source": before["openings"], "derived": after["openings"], "contract": "one component / four openings / zero other non-manifold edges"},
        "panel_roles": rounded["role_counts"](top), "weights": weights, "weight_semantic": rounded["weight_semantic"](top),
        "material_semantic": after["materials"], "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"], "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "opening_geometry_changed": 0, "non_target_coordinates_changed": 0, "non_target_weights_changed": 0, "central_depth_taper_changed": 0, "waist_taper_outward_regressions": 0, "neckline_yoke_outer_caps_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False, "export_import_preparation_stopped": True},
    }
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cs provenance\n\n"
        "- Additive derivative of exact Phase 1L.5cq custody after the fail-closed Phase 1L.5cr review.\n"
        "- Changes only X/Y coordinates on the fixed 24-pair bilateral side/underarm strip and normalized spine/matching-upper-arm weights there plus eight paired waist-opening hem anchors.\n"
        "- Target Z, all non-target coordinates/weights, central depth taper, waist-opening geometry, neckline/yoke/caps, topology and every non-top asset remain exact; the accepted waist taper has zero outward regressions.\n"
        "- Five before/after views and the 21-frame ledger are a correction proof, not a visual-acceptance verdict. Export/import preparation remains stopped.\n",
        encoding="utf-8",
    )
    manifest = {"phase": "Phase 1L.5cs side/underarm-to-hem transition coordinate and normalized blend correction walk proof", "status": "offline_targeted_side_transition_correction_not_visual_acceptance_or_runtime", "semantic": semantic, "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SIDE_UNDERARM_HEM_WALK_PASS frames=21 targets={correction['target_vertex_count']} coordinates={correction['coordinate_changed_vertex_count']} weights={correction['weight_changed_vertex_count']} ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_custody()
    for name, path in (("blend", OUTPUT), ("builder", Path(__file__)), ("provenance", PROVENANCE)):
        if manifest["files"][name] != receipt(path):
            raise RuntimeError(f"{name} custody drift")
    for name, expected in manifest["files"]["reviews"].items():
        if receipt(REVIEWS / name) != expected:
            raise RuntimeError(f"review custody drift: {name}")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    semantic = manifest["semantic"]
    if semantic_sha(base["mesh_semantic"](body)) != BODY_SHA or semantic_sha(base["mesh_semantic"](bottom)) != BOTTOM_SHA or semantic_sha(base["mesh_semantic"](top)) != semantic["derived_mesh_sha256"][TOP]:
        raise RuntimeError("mesh drift")
    if rounded["material_semantic"](top) != semantic["material_semantic"] or rounded["weight_semantic"](top) != semantic["weight_semantic"]:
        raise RuntimeError("material or weight drift")
    if r3["topology_proof"](top, (1, 4, 0), "side-transition corrected starter top") != semantic["topology"][TOP] or renderer["opening_proof"](top) != semantic["opening_geometry"]["derived"]:
        raise RuntimeError("topology/opening drift")
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"] or base["action_semantic"](bpy.data.actions[base["ACTION"]]) != semantic["action"]:
        raise RuntimeError("armature/action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    correction = semantic["correction"]
    if transition_metrics(bpy.context.scene, top) != correction["named_issue_metrics"]["derived"]:
        raise RuntimeError("named issue metric drift")
    for key in ("target_protected_overlap_count", "target_depth_taper_overlap_count", "target_outer_cap_overlap_count", "target_yoke_overlap_count", "coordinate_target_opening_boundary_overlap_count", "vertex_groups_added"):
        if correction[key]:
            raise RuntimeError(f"target/protected ledger drift: {key}")
    if correction["source_protected_coordinate_sha256"] != correction["derived_protected_coordinate_sha256"] or correction["source_protected_weight_sha256"] != correction["derived_protected_weight_sha256"]:
        raise RuntimeError("protected identity drift")
    print(f"SIDE_UNDERARM_HEM_WALK_VALIDATE_PASS ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
