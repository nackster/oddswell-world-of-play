"""Build or validate the Phase 1L.5cq yoke-to-cap transition/blend proof."""

from pathlib import Path


UPSTREAM = Path(__file__).resolve().parent.parent / "OuterSleeveArmholeRoundedCapWalkProof/build_outer_sleeve_armhole_rounded_cap_walk.py"
upstream_source = UPSTREAM.read_text(encoding="utf-8")
exec(upstream_source[: upstream_source.rfind('if "--validate"')], globals())

SOURCE_ROOT = SLICE / "OuterSleeveArmholeRoundedCapWalkProof"
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleOuterSleeveArmholeRoundedCapTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "outer_sleeve_armhole_rounded_cap_walk_custody.json"
DEPTH_MANIFEST = SLICE / "CentralTorsoTaperStarterTopWalkProof/central_torso_taper_starter_top_walk_custody.json"
WAIST_MANIFEST = SLICE / "LateralWaistTaperStarterTopWalkProof/lateral_waist_taper_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleYokeCapTransitionBlendedTopWalk.blend"
MANIFEST = ROOT / "yoke_cap_transition_blend_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
SOURCE_TOP_SHA = "519C4F12ADB179FDA71E1E11B043798018FF344369CCB1AE5799A7040DEF4C47"
SOURCE_IDENTITY = "2384397B3BAB50C3CC01222F8EE9EDE598A430444FC7FEC3C233CA46272CD07A"
SOURCE_BLEND_SHA = "7EF2728BF1F091FF5A4DEF57815CCF7159DCE21A19528AA5595E848B07139363"
X_MIN, X_MAX, Z_MIN, Z_MAX = 0.24, 0.389245, 1.38, 1.56


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
        raise RuntimeError("Phase 1L.5co custody drift")
    depth = json.loads(DEPTH_MANIFEST.read_text(encoding="utf-8"))
    waist = json.loads(WAIST_MANIFEST.read_text(encoding="utf-8"))
    return accepted, depth, waist


def apply_correction(top, accepted, depth, waist):
    before_coordinates = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    before_weights = rounded["weight_semantic"](top)
    before_groups = [group.name for group in top.vertex_groups]
    target = {
        index for index, (x, _, z) in before_coordinates.items()
        if X_MIN <= abs(x) < X_MAX and Z_MIN <= z <= Z_MAX
    }
    protected = set(before_coordinates) - target
    depth_target = set(depth["semantic"]["correction"]["target_vertex_indices"])
    waist_target = set(waist["semantic"]["correction"]["target_vertex_indices"])
    outer_caps = set(accepted["semantic"]["correction"]["target_vertex_indices"])
    openings = boundary_indices(top)
    if not target or target & protected or target & depth_target or target & waist_target or target & outer_caps or target & openings:
        raise RuntimeError("target overlaps a protected ledger")

    spine = top.vertex_groups["spine"]
    left = top.vertex_groups["upper_arm.L"]
    right = top.vertex_groups["upper_arm.R"]
    for index in target:
        vertex = top.data.vertices[index]
        x, y, z = vertex.co
        lateral = base["smoothstep"]((abs(x) - X_MIN) / (X_MAX - X_MIN))
        height = base["smoothstep"]((z - Z_MIN) / (Z_MAX - Z_MIN))
        vertex.co.z = z - 0.032 * lateral * (0.35 + 0.65 * height)
        vertex.co.y = 0.02 + (y - 0.02) * (1.0 - 0.08 * lateral * (0.40 + 0.60 * height))
        arm_weight = (0.018 + 0.077 * lateral) * (0.90 + 0.10 * height)
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
    if coordinates(top, protected) != coordinates_from_map(before_coordinates, protected):
        raise RuntimeError("protected coordinate drift")
    if [after_weights[index] for index in sorted(protected)] != [before_weights[index] for index in sorted(protected)]:
        raise RuntimeError("protected weight drift")
    if any(abs(sum(weight for _, weight in after_weights[index]) - 1.0) > 1e-6 for index in target):
        raise RuntimeError("target weights are not normalized")
    for index in target:
        expected_arm = "upper_arm.L" if before_coordinates[index][0] > 0 else "upper_arm.R"
        if {name for name, _ in after_weights[index]} - {"spine", expected_arm}:
            raise RuntimeError("target contains a non-matching influence")

    changed_coordinates = {index for index in target if tuple(top.data.vertices[index].co) != before_coordinates[index]}
    changed_weights = {index for index in target if after_weights[index] != before_weights[index]}
    if not changed_coordinates or not changed_weights:
        raise RuntimeError("correction changed no target coordinates or weights")
    body_bounds = accepted["semantic"]["deformation"]["frames"][0]["bounds_m"][BODY]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    source_width = max(value[0] for value in before_coordinates.values()) - min(value[0] for value in before_coordinates.values())
    derived_width = max(vertex.co.x for vertex in top.data.vertices) - min(vertex.co.x for vertex in top.data.vertices)
    ratio = derived_width / body_width
    if derived_width != source_width or round(derived_width, 9) != 0.930000007 or round(ratio, 9) != 1.377059677:
        raise RuntimeError("accepted width/ratio drift")
    coordinate_displacements = [math.dist(before_coordinates[index], top.data.vertices[index].co) for index in changed_coordinates]
    weight_deltas = [
        max(abs(dict(before_weights[index]).get(name, 0.0) - dict(after_weights[index]).get(name, 0.0)) for name in {"spine", "upper_arm.L", "upper_arm.R"})
        for index in changed_weights
    ]
    return {
        "approved_source_coordinate_window": {"absolute_x_min_m": X_MIN, "absolute_x_max_exclusive_m": X_MAX, "z_min_m": Z_MIN, "z_max_m": Z_MAX},
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "coordinate_changed_vertex_count": len(changed_coordinates),
        "coordinate_changed_vertex_indices": sorted(changed_coordinates),
        "weight_changed_vertex_count": len(changed_weights),
        "weight_changed_vertex_indices": sorted(changed_weights),
        "protected_vertex_count": len(protected),
        "protected_vertex_indices": sorted(protected),
        "target_protected_overlap_count": len(target & protected),
        "target_depth_taper_overlap_count": len(target & depth_target),
        "target_waist_taper_overlap_count": len(target & waist_target),
        "target_outer_cap_overlap_count": len(target & outer_caps),
        "target_opening_boundary_overlap_count": len(target & openings),
        "source_target_coordinates": coordinates_from_map(before_coordinates, target),
        "derived_target_coordinates": coordinates(top, target),
        "source_target_coordinate_sha256": semantic_sha(coordinates_from_map(before_coordinates, target)),
        "derived_target_coordinate_sha256": semantic_sha(coordinates(top, target)),
        "source_protected_coordinate_sha256": semantic_sha(coordinates_from_map(before_coordinates, protected)),
        "derived_protected_coordinate_sha256": semantic_sha(coordinates(top, protected)),
        "source_target_weights": [[index, before_weights[index]] for index in sorted(target)],
        "derived_target_weights": [[index, after_weights[index]] for index in sorted(target)],
        "source_target_weight_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(target)]),
        "derived_target_weight_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(target)]),
        "source_protected_weight_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(protected)]),
        "derived_protected_weight_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(protected)]),
        "vertex_groups_added": 0,
        "target_weight_sum": 1.0,
        "maximum_coordinate_displacement_m": round(max(coordinate_displacements), 9),
        "maximum_influence_delta": round(max(weight_deltas), 9),
        "source_top_width_m": round(source_width, 9),
        "derived_top_width_m": round(derived_width, 9),
        "body_width_m": round(body_width, 9),
        "derived_top_to_body_width_ratio": round(ratio, 9),
    }


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
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5co</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5cq</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5cq before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5cq yoke-to-cap transition / normalized blend correction</h1>'
        '<p>Targeted offline walk proof only; no acceptance verdict.</p>' + rows,
        encoding="utf-8",
    )
    return {path.name: receipt(path) for path in sorted(REVIEWS.glob("*")) if path.is_file()}


def build():
    accepted, depth, waist = source_custody()
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
    correction = apply_correction(top, accepted, depth, waist)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)), "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature), "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top), "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"), "openings": renderer["opening_proof"](top),
    }
    for key in ("body", "bottom", "armature", "action", "materials", "topology", "item_id", "openings"):
        if after[key] != before[key]:
            raise RuntimeError(f"non-target identity drift: {key}")
    topology = {TOP: r3["topology_proof"](top, (1, 4, 0), "yoke-cap blended starter top"), BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts")}
    weights = {TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}), BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    if any(any(value for value in row["intersections"].values()) for row in deformation["frames"]):
        raise RuntimeError("walk proof contains evaluated intersections")
    if not deformation["loop_endpoint_equal"] or any(row["root_bone_translation_m"] != [0.0, 0.0, 0.0] or row["armature_translation_m"] != [0.0, 0.0, 0.0] for row in deformation["frames"]):
        raise RuntimeError("walk translation or endpoint drift")
    semantic = {
        "accepted_phase_1l5co": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA}, "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))}, "correction": correction,
        "construction": {"method": "bounded_yoke_cap_coordinate_and_normalized_matching_arm_blend", "excluded": ["outside_window_coordinates_and_weights", "torso_depth_waist_tapers", "waist_neck_openings", "accepted_outer_caps", "topology", "item_material_color", "body", "shorts", "skeleton", "action"]},
        "topology": topology, "opening_geometry": {"source": before["openings"], "derived": after["openings"], "contract": "one component / four openings / zero other non-manifold edges"},
        "panel_roles": rounded["role_counts"](top), "weights": weights, "weight_semantic": rounded["weight_semantic"](top),
        "material_semantic": after["materials"], "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"], "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "opening_geometry_changed": 0, "outside_window_coordinates_changed": 0, "outside_window_weights_changed": 0, "depth_waist_tapers_changed": 0, "outer_caps_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False, "export_import_preparation_stopped": True},
    }
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cq provenance\n\n"
        "- Additive derivative of exact Phase 1L.5co custody after the fail-closed Phase 1L.5cp review.\n"
        "- Changes coordinates and normalized spine/matching-upper-arm weights only inside the approved yoke-to-cap source window.\n"
        "- All coordinates and weights outside the window reproduce exactly; no vertex group is added. Torso/depth/waist, waist/neck boundaries and accepted outer caps/openings remain exact.\n"
        "- Before/after neutral and opposing-extreme views are a correction proof, not a visual-acceptance verdict. Export/import preparation remains stopped.\n",
        encoding="utf-8",
    )
    manifest = {"phase": "Phase 1L.5cq yoke-to-cap transition and normalized blend correction walk proof", "status": "offline_targeted_yoke_cap_correction_not_visual_acceptance_or_runtime", "semantic": semantic, "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"YOKE_CAP_BLEND_WALK_PASS frames=21 targets={correction['target_vertex_count']} coordinates={correction['coordinate_changed_vertex_count']} weights={correction['weight_changed_vertex_count']} ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


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
    if r3["topology_proof"](top, (1, 4, 0), "yoke-cap blended starter top") != semantic["topology"][TOP] or renderer["opening_proof"](top) != semantic["opening_geometry"]["derived"]:
        raise RuntimeError("topology/opening drift")
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"] or base["action_semantic"](bpy.data.actions[base["ACTION"]]) != semantic["action"]:
        raise RuntimeError("armature/action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    correction = semantic["correction"]
    if any(correction[key] for key in ("target_protected_overlap_count", "target_depth_taper_overlap_count", "target_waist_taper_overlap_count", "target_outer_cap_overlap_count", "target_opening_boundary_overlap_count", "vertex_groups_added")):
        raise RuntimeError("target/protected ledger drift")
    if correction["source_protected_coordinate_sha256"] != correction["derived_protected_coordinate_sha256"] or correction["source_protected_weight_sha256"] != correction["derived_protected_weight_sha256"]:
        raise RuntimeError("protected identity drift")
    print(f"YOKE_CAP_BLEND_WALK_VALIDATE_PASS ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
