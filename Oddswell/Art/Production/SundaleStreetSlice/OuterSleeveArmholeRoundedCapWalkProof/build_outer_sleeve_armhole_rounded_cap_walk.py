"""Build or validate the Phase 1L.5co outer sleeve/armhole rounded-cap proof."""

import bmesh
import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
SOURCE_ROOT = SLICE / "ShoulderSleeveHemArticulationCorrectionWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_shoulder_sleeve_hem_articulation_walk.py"
scope = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], scope)
base, r3, prior, renderer, rounded = (scope[name] for name in ("base", "r3", "prior", "renderer", "rounded"))

BODY, TOP, BOTTOM, ARMATURE = (scope[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleShoulderSleeveHemArticulatedTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "shoulder_sleeve_hem_articulation_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleOuterSleeveArmholeRoundedCapTopWalk.blend"
MANIFEST = ROOT / "outer_sleeve_armhole_rounded_cap_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "9ED01AAA3F060F237D2CCADCD5ED7E15F65E864F013DC0BCB51266A31A34FA58"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "6E219986ED018BFF27BB61AD308346C33217795B5C883893806E661D589579B0"
SOURCE_BLEND_SHA = "10315DEC1E2F1EAB3F3D7DDA6828AB5B9867957B9D108C5A2F462201D3E059FC"
X_MIN, Z_MIN, Z_MAX = 0.389245, 1.20, 1.40
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def receipt(path):
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


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
        raise RuntimeError("Phase 1L.5cm custody drift")
    return accepted


def coordinates(obj, indices):
    return [[index, *[round(value, 9) for value in obj.data.vertices[index].co]] for index in sorted(indices)]


def coordinates_from_map(values, indices):
    return [[index, *[round(value, 9) for value in values[index]]] for index in sorted(indices)]


def boundary_indices(obj):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    mesh.verts.ensure_lookup_table()
    result = {vertex.index for edge in mesh.edges if len(edge.link_faces) == 1 for vertex in edge.verts}
    mesh.free()
    return result


def apply_correction(top, accepted):
    before_coordinates = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    before_weights = rounded["weight_semantic"](top)
    target = {
        index for index, (_, _, z) in before_coordinates.items()
        if abs(before_coordinates[index][0]) >= X_MIN and Z_MIN <= z <= Z_MAX
    }
    protected = set(before_coordinates) - target
    openings = boundary_indices(top)
    target_openings = target & openings
    waist_neck_openings = {index for index in openings if before_coordinates[index][2] <= 1.05 or before_coordinates[index][2] >= 1.45}
    if not target or not target_openings or target & protected:
        raise RuntimeError("invalid target/protected/opening ledger")
    if target & waist_neck_openings:
        raise RuntimeError("target overlaps protected waist/neckline boundary")
    if any(not (abs(before_coordinates[index][0]) >= X_MIN and Z_MIN <= before_coordinates[index][2] <= Z_MAX) for index in target):
        raise RuntimeError("target escaped approved source-coordinate bounds")

    for index in target:
        vertex = top.data.vertices[index]
        x, y, z = vertex.co
        height = max(0.0, min(1.0, (z - Z_MIN) / (Z_MAX - Z_MIN)))
        cap_limit = 0.415 + 0.050 * math.sin(math.pi * height)
        vertex.co.x = math.copysign(min(abs(x), cap_limit), x)
        depth_scale = 0.88 + 0.12 * math.sin(math.pi * height)
        vertex.co.y = 0.02 + (y - 0.02) * depth_scale
    top.data.update()

    after_weights = rounded["weight_semantic"](top)
    if after_weights != before_weights:
        raise RuntimeError("articulation weight drift")
    if coordinates(top, protected) != coordinates_from_map(before_coordinates, protected):
        raise RuntimeError("protected coordinate drift")

    changed = {index for index in target if tuple(top.data.vertices[index].co) != before_coordinates[index]}
    changed_openings = changed & target_openings
    if not changed or not changed_openings:
        raise RuntimeError("rounded-cap correction changed no arm-opening coordinates")
    body_bounds = accepted["semantic"]["deformation"]["frames"][0]["bounds_m"][BODY]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    source_width = max(value[0] for value in before_coordinates.values()) - min(value[0] for value in before_coordinates.values())
    derived_width = max(vertex.co.x for vertex in top.data.vertices) - min(vertex.co.x for vertex in top.data.vertices)
    ratio = derived_width / body_width
    if ratio > 1.4:
        raise RuntimeError(f"width ratio exceeds contract: {ratio}")
    displacements = [math.dist(before_coordinates[index], top.data.vertices[index].co) for index in changed]
    return {
        "approved_source_coordinate_bounds": {"absolute_x_min_m": X_MIN, "z_min_m": Z_MIN, "z_max_m": Z_MAX},
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "changed_vertex_count": len(changed),
        "changed_vertex_indices": sorted(changed),
        "protected_vertex_count": len(protected),
        "protected_vertex_indices": sorted(protected),
        "target_protected_overlap_count": len(target & protected),
        "source_target_sha256": semantic_sha(coordinates_from_map(before_coordinates, target)),
        "derived_target_sha256": semantic_sha(coordinates(top, target)),
        "source_protected_sha256": semantic_sha(coordinates_from_map(before_coordinates, protected)),
        "derived_protected_sha256": semantic_sha(coordinates(top, protected)),
        "source_all_weights_sha256": semantic_sha(before_weights),
        "derived_all_weights_sha256": semantic_sha(after_weights),
        "weights_changed": 0,
        "source_opening_boundary_vertex_count": len(openings),
        "target_arm_opening_boundary_vertex_count": len(target_openings),
        "target_arm_opening_boundary_vertex_indices": sorted(target_openings),
        "changed_arm_opening_boundary_vertex_count": len(changed_openings),
        "changed_arm_opening_boundary_vertex_indices": sorted(changed_openings),
        "source_target_arm_opening_boundary_coordinates": coordinates_from_map(before_coordinates, target_openings),
        "derived_target_arm_opening_boundary_coordinates": coordinates(top, target_openings),
        "source_target_arm_opening_boundary_sha256": semantic_sha(coordinates_from_map(before_coordinates, target_openings)),
        "derived_target_arm_opening_boundary_sha256": semantic_sha(coordinates(top, target_openings)),
        "protected_waist_neck_boundary_vertex_count": len(waist_neck_openings),
        "protected_waist_neck_boundary_vertex_indices": sorted(waist_neck_openings),
        "target_waist_neck_boundary_overlap_count": len(target & waist_neck_openings),
        "source_waist_neck_boundary_sha256": semantic_sha(coordinates_from_map(before_coordinates, waist_neck_openings)),
        "derived_waist_neck_boundary_sha256": semantic_sha(coordinates(top, waist_neck_openings)),
        "maximum_coordinate_displacement_m": round(max(displacements), 9),
        "source_top_width_m": round(source_width, 9),
        "derived_top_width_m": round(derived_width, 9),
        "body_width_m": round(body_width, 9),
        "derived_top_to_body_width_ratio": round(ratio, 9),
        "maximum_top_to_body_width_ratio": 1.4,
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
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5cm</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5co</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5co before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5co outer sleeve / armhole rounded-cap correction</h1>'
        '<p>Targeted offline walk proof only; no acceptance verdict.</p>' + rows,
        encoding="utf-8",
    )
    return {path.name: receipt(path) for path in sorted(REVIEWS.glob("*")) if path.is_file()}


def build():
    accepted = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    before = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "top": semantic_sha(base["mesh_semantic"](top)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
        "weights": rounded["weight_semantic"](top),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    correction = apply_correction(top, accepted)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
        "weights": rounded["weight_semantic"](top),
    }
    for key in ("body", "bottom", "armature", "action", "materials", "topology", "item_id", "weights"):
        if after[key] != before[key]:
            raise RuntimeError(f"non-target identity drift: {key}")
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "rounded-cap starter top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts"),
    }
    weights = {
        TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}),
        BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}),
    }
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    frames = deformation["frames"]
    if any(any(value for value in row["intersections"].values()) for row in frames):
        raise RuntimeError("walk proof contains evaluated intersections")
    if not deformation["loop_endpoint_equal"]:
        raise RuntimeError("walk endpoints do not match")
    if any(row["root_bone_translation_m"] != [0.0, 0.0, 0.0] or row["armature_translation_m"] != [0.0, 0.0, 0.0] for row in frames):
        raise RuntimeError("walk proof contains root or armature translation")
    semantic = {
        "accepted_phase_1l5cm": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "bounded_outer_sleeve_xz_cap_with_edge_depth_rounding", "excluded": ["all_source_coordinates_outside_approved_bounds", "all_weights", "central_torso", "depth_taper", "waist_taper", "waist_boundary", "neckline_boundary", "topology", "materials", "item_identity", "body", "shorts", "skeleton", "action"]},
        "topology": topology,
        "opening_geometry": {"source": before["openings"], "derived": after["openings"], "contract": "one component / four openings / zero other non-manifold edges"},
        "panel_roles": rounded["role_counts"](top),
        "weights": weights,
        "weight_semantic": after["weights"],
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "weights_changed": 0, "topology_changed": 0, "opening_contract_changed": 0, "outside_target_coordinates_changed": 0, "central_taper_coordinates_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False, "export_import_preparation_stopped": True},
    }
    if correction["source_protected_sha256"] != correction["derived_protected_sha256"] or correction["source_all_weights_sha256"] != correction["derived_all_weights_sha256"]:
        raise RuntimeError("protected identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5co provenance\n\n"
        "- Additive derivative of exact Phase 1L.5cm custody after the fail-closed Phase 1L.5cn review.\n"
        "- Changes only top source coordinates satisfying |X| >= 0.389245 m and 1.20 m <= Z <= 1.40 m to round the outer sleeve/armhole caps.\n"
        "- Every source coordinate outside that ledger and every articulation weight reproduce exactly; targeted arm-opening boundary coordinates are disclosed in the manifest.\n"
        "- Torso depth/waist tapers, waist/neckline boundaries, topology, item/material/color, body, shorts, DEC-035 and walk action remain protected.\n"
        "- Before/after neutral and opposing-extreme views are a correction proof, not a visual-acceptance verdict. Export/import preparation remains stopped.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5co outer sleeve/armhole rounded-cap correction walk proof",
        "status": "offline_targeted_top_rounded_cap_correction_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OUTER_SLEEVE_ROUNDED_CAP_WALK_PASS frames=21 targets={correction['target_vertex_count']} changed={correction['changed_vertex_count']} opening_changed={correction['changed_arm_opening_boundary_vertex_count']} ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


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
    if semantic_sha(base["mesh_semantic"](body)) != BODY_SHA or semantic_sha(base["mesh_semantic"](bottom)) != BOTTOM_SHA:
        raise RuntimeError("accepted body/bottom drift")
    if semantic_sha(base["mesh_semantic"](top)) != semantic["derived_mesh_sha256"][TOP]:
        raise RuntimeError("corrected top drift")
    if rounded["material_semantic"](top) != semantic["material_semantic"] or rounded["weight_semantic"](top) != semantic["weight_semantic"]:
        raise RuntimeError("material or weight drift")
    if r3["topology_proof"](top, (1, 4, 0), "rounded-cap starter top") != semantic["topology"][TOP]:
        raise RuntimeError("topology drift")
    if renderer["opening_proof"](top) != semantic["opening_geometry"]["derived"]:
        raise RuntimeError("opening geometry drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    correction = semantic["correction"]
    if correction["target_protected_overlap_count"] or correction["target_waist_neck_boundary_overlap_count"] or correction["weights_changed"] or correction["source_protected_sha256"] != correction["derived_protected_sha256"] or correction["source_all_weights_sha256"] != correction["derived_all_weights_sha256"] or correction["source_waist_neck_boundary_sha256"] != correction["derived_waist_neck_boundary_sha256"]:
        raise RuntimeError("target/protected/weight ledger drift")
    print(f"OUTER_SLEEVE_ROUNDED_CAP_WALK_VALIDATE_PASS ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
