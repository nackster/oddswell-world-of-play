"""Build or validate the Phase 1L.5ck outer shoulder/sleeve-span proof."""

import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
SOURCE_ROOT = SLICE / "LateralWaistTaperStarterTopWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_lateral_waist_taper_starter_top_walk.py"
source_scope = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], source_scope)
base, r3, prior, renderer = (source_scope[name] for name in ("base", "r3", "prior", "renderer"))
rounded = source_scope["source_phase"]["rounded"]

BODY, TOP, BOTTOM, ARMATURE = (source_scope[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleLateralWaistTaperStarterTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "lateral_waist_taper_starter_top_walk_custody.json"
DEPTH_MANIFEST = SLICE / "CentralTorsoTaperStarterTopWalkProof/central_torso_taper_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleOuterShoulderSleeveSpanCorrectedTopWalk.blend"
MANIFEST = ROOT / "outer_shoulder_sleeve_span_correction_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "BB29047CAB30C3071FD6875A789E93CF275C2E2A44997957CFB85DCDD36FD3AB"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "38F71CB35B20672E114E27B8C79206564CAE358B5A3C053509A510D7485539FD"
SOURCE_BLEND_SHA = "5A9ED444693F30AABE68E55B29C2DA588423ED256BEDE94472FA349D48E1543B"
TARGET_RATIO = 1.399
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def receipt(path):
    return {"bytes": path.stat().st_size, "sha256": sha256(path)}


def source_custody():
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    semantic = manifest["semantic"]
    checks = (
        semantic["identity_sha256"] == SOURCE_IDENTITY,
        semantic["accepted_mesh_sha256"][BODY] == BODY_SHA,
        semantic["derived_mesh_sha256"][TOP] == SOURCE_TOP_SHA,
        semantic["accepted_mesh_sha256"][BOTTOM] == BOTTOM_SHA,
        semantic["action"]["identity_sha256"] == ACTION_SHA,
        semantic["armature"]["bone_count"] == 12,
        receipt(SOURCE_BLEND) == manifest["files"]["blend"],
        manifest["files"]["blend"]["sha256"] == SOURCE_BLEND_SHA,
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5ci custody drift")
    depth = json.loads(DEPTH_MANIFEST.read_text(encoding="utf-8"))
    if depth["semantic"]["identity_sha256"] != semantic["accepted_phase_1l5cg"]["identity_sha256"]:
        raise RuntimeError("Phase 1L.5cg depth-taper custody drift")
    return manifest, depth


def outer_span_correction(top, source_manifest, depth_manifest):
    before = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    depth_target = set(depth_manifest["semantic"]["correction"]["target_vertex_indices"])
    waist_target = set(source_manifest["semantic"]["correction"]["target_vertex_indices"])
    source_openings = set(source_manifest["semantic"]["correction"]["protected_opening_boundary_indices"])
    target = {vertex.index for vertex in top.data.vertices if abs(vertex.co.x) > 0.40}
    if not target:
        raise RuntimeError("outer shoulder/sleeve correction selected no vertices")
    if target & depth_target or target & waist_target:
        raise RuntimeError("outer span target overlaps an accepted central taper target")
    body_bounds = source_manifest["semantic"]["deformation"]["frames"][0]["bounds_m"][BODY]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    source_min = min(value[0] for value in before.values())
    source_max = max(value[0] for value in before.values())
    source_width = source_max - source_min
    source_ratio = source_width / body_width
    target_half_width = body_width * TARGET_RATIO / 2.0
    source_half_width = max(abs(source_min), abs(source_max))
    scale = target_half_width / source_half_width
    for index in target:
        vertex = top.data.vertices[index]
        vertex.co.x = math.copysign(abs(vertex.co.x) * scale, vertex.co.x)
    top.data.update()
    protected = set(before) - target
    if target & protected:
        raise RuntimeError("target/protected ledger overlap")
    if any(tuple(top.data.vertices[index].co) != before[index] for index in protected):
        raise RuntimeError("protected coordinate drift")
    if any(top.data.vertices[index].co.y != before[index][1] or top.data.vertices[index].co.z != before[index][2] for index in target):
        raise RuntimeError("target changed a non-X coordinate")
    derived_min = min(vertex.co.x for vertex in top.data.vertices)
    derived_max = max(vertex.co.x for vertex in top.data.vertices)
    derived_width = derived_max - derived_min
    derived_ratio = derived_width / body_width
    if derived_ratio > 1.4:
        raise RuntimeError(f"outer span ratio remains above contract: {derived_ratio}")
    displacement = [math.dist(before[index], top.data.vertices[index].co) for index in target]
    return {
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "protected_vertex_count": len(protected),
        "protected_vertex_indices": sorted(protected),
        "protected_depth_taper_indices": sorted(depth_target),
        "protected_waist_taper_indices": sorted(waist_target),
        "target_depth_taper_overlap_count": len(target & depth_target),
        "target_waist_taper_overlap_count": len(target & waist_target),
        "source_opening_boundary_indices": sorted(source_openings),
        "target_opening_boundary_indices": sorted(target & source_openings),
        "target_opening_boundary_count": len(target & source_openings),
        "source_target_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(target)]),
        "derived_target_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(target)]),
        "source_protected_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(protected)]),
        "derived_protected_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(protected)]),
        "source_all_yz_sha256": semantic_sha([[index, before[index][1], before[index][2]] for index in sorted(before)]),
        "derived_all_yz_sha256": semantic_sha([[vertex.index, vertex.co.y, vertex.co.z] for vertex in top.data.vertices]),
        "coordinate_axes_changed": ["x"],
        "maximum_target_vertex_displacement_m": round(max(displacement), 9),
        "source_top_width_m": round(source_width, 9),
        "derived_top_width_m": round(derived_width, 9),
        "body_width_m": round(body_width, 9),
        "source_top_to_body_width_ratio": round(source_ratio, 9),
        "derived_top_to_body_width_ratio": round(derived_ratio, 9),
        "maximum_allowed_top_to_body_width_ratio": 1.4,
        "target_top_to_body_width_ratio": TARGET_RATIO,
        "uniform_target_x_scale": round(scale, 9),
    }


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    source_receipts = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["files"]["reviews"]
    for name in VIEWS:
        path = SOURCE_ROOT / "Review" / f"After_{name}.png"
        if receipt(path) != source_receipts[f"After_{name}.png"]:
            raise RuntimeError(f"source review drift: {name}")
        shutil.copyfile(path, REVIEWS / f"Before_{name}.png")
    renderer["REVIEWS"] = REVIEWS
    renderer["render_reviews"]()
    for name in VIEWS:
        (REVIEWS / f"{name}.png").replace(REVIEWS / f"After_{name}.png")
    rows = "\n".join(
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5ci</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5ck</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5ck before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5ck outer shoulder/sleeve span correction</h1><p>Targeted correction proof only; no acceptance verdict.</p>' + rows,
        encoding="utf-8",
    )
    return {path.name: receipt(path) for path in sorted(REVIEWS.glob("*")) if path.is_file()}


def build():
    accepted, depth = source_custody()
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
        "weights": rounded["weight_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    if before["openings"] != accepted["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("accepted source opening drift")
    correction = outer_span_correction(top, accepted, depth)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "weights": rounded["weight_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
    }
    for key in ("body", "bottom", "armature", "action", "materials", "topology", "weights", "item_id"):
        if after[key] != before[key]:
            raise RuntimeError(f"non-target identity drift: {key}")
    changed_openings = [index for index, (source_opening, derived_opening) in enumerate(zip(before["openings"], after["openings"])) if source_opening != derived_opening]
    if changed_openings != [0, 3]:
        raise RuntimeError(f"unexpected opening geometry change: {changed_openings}")
    topology = {TOP: r3["topology_proof"](top, (1, 4, 0), "outer-span corrected starter top"), BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts")}
    weights = {TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}), BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    semantic = {
        "accepted_phase_1l5ci": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "uniform_outer_shoulder_sleeve_x_scale", "excluded": ["central_depth_taper", "central_waist_taper", "all_y", "all_z", "non_target_coordinates", "topology", "weights", "materials", "body", "shorts", "skeleton", "action"]},
        "topology": topology,
        "opening_geometry": {"source": before["openings"], "derived": after["openings"], "changed_loop_indices": changed_openings, "unchanged_loop_indices": [1, 2], "contract": "one component / four openings / zero other non-manifold edges"},
        "panel_roles": rounded["role_counts"](top),
        "weights": weights,
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "opening_contract_changed": 0, "arm_opening_geometry_changed": 1, "waist_opening_geometry_changed": 0, "neckline_opening_geometry_changed": 0, "target_y_changed": 0, "target_z_changed": 0, "protected_top_vertices_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False},
    }
    if correction["source_protected_coordinate_sha256"] != correction["derived_protected_coordinate_sha256"] or correction["source_all_yz_sha256"] != correction["derived_all_yz_sha256"]:
        raise RuntimeError("protected or Y/Z identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5ck provenance\n\n"
        "- Additive derivative of exact repaired Phase 1L.5ci custody after the Phase 1L.5cj rejection.\n"
        "- Only outer shoulder/sleeve X coordinates beyond |X| = 0.40 m are uniformly reduced.\n"
        "- Central depth and waist taper coordinates, all Y/Z values and every non-target coordinate remain exact.\n"
        "- Left and right arm-opening geometry changes are disclosed; waist and neckline opening geometry and the one-component/four-opening contract remain exact.\n"
        "- Before/after evidence is a correction proof, not an acceptance verdict.\n"
        "- No export, runtime, final-art, performance or readiness claim is included.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5ck outer shoulder/sleeve-span correction walk proof",
        "status": "offline_targeted_outer_span_correction_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OUTER_SPAN_CORRECTION_WALK_PASS frames=21 target={correction['target_vertex_count']} ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    accepted, depth = source_custody()
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
    if rounded["material_semantic"](top) != semantic["material_semantic"]:
        raise RuntimeError("material drift")
    if r3["topology_proof"](top, (1, 4, 0), "outer-span corrected starter top") != semantic["topology"][TOP]:
        raise RuntimeError("topology drift")
    if renderer["opening_proof"](top) != semantic["opening_geometry"]["derived"]:
        raise RuntimeError("opening geometry drift")
    correction = semantic["correction"]
    if correction["target_depth_taper_overlap_count"] or correction["target_waist_taper_overlap_count"]:
        raise RuntimeError("target/accepted taper overlap")
    if set(correction["target_vertex_indices"]) & set(correction["protected_vertex_indices"]):
        raise RuntimeError("target/protected ledger overlap")
    if set(correction["protected_depth_taper_indices"]) != set(depth["semantic"]["correction"]["target_vertex_indices"]):
        raise RuntimeError("depth-taper protection drift")
    if set(correction["protected_waist_taper_indices"]) != set(accepted["semantic"]["correction"]["target_vertex_indices"]):
        raise RuntimeError("waist-taper protection drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"OUTER_SPAN_CORRECTION_WALK_VALIDATE_PASS ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
