"""Build or validate the Phase 1L.5cm top-articulation correction proof."""

import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
SOURCE_ROOT = SLICE / "OuterShoulderSleeveSpanCorrectionWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_outer_shoulder_sleeve_span_correction_walk.py"
scope = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], scope)
base, r3, prior, renderer, rounded = (scope[name] for name in ("base", "r3", "prior", "renderer", "rounded"))

BODY, TOP, BOTTOM, ARMATURE = (scope[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleOuterShoulderSleeveSpanCorrectedTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "outer_shoulder_sleeve_span_correction_walk_custody.json"
DEPTH_MANIFEST = SLICE / "CentralTorsoTaperStarterTopWalkProof/central_torso_taper_starter_top_walk_custody.json"
WAIST_MANIFEST = SLICE / "LateralWaistTaperStarterTopWalkProof/lateral_waist_taper_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleShoulderSleeveHemArticulatedTopWalk.blend"
MANIFEST = ROOT / "shoulder_sleeve_hem_articulation_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "4D290EAEF2CDC94F6F68982C0166FF5E7B85C6B36200170FF2B24AFF4F379FBE"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "BB7BE19929C7C89270CC39D029FBE21D9D8140E57BB2A91B55DE96DCC75F8F18"
SOURCE_BLEND_SHA = "5A452DCF36B861D4271D6D9CD1303161330C112BCEBD32AF2548F2C2F35161C7"
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
        raise RuntimeError("Phase 1L.5ck custody drift")
    depth = json.loads(DEPTH_MANIFEST.read_text(encoding="utf-8"))
    waist = json.loads(WAIST_MANIFEST.read_text(encoding="utf-8"))
    if waist["semantic"]["identity_sha256"] != semantic["accepted_phase_1l5ci"]["identity_sha256"]:
        raise RuntimeError("waist-taper custody drift")
    if depth["semantic"]["identity_sha256"] != waist["semantic"]["accepted_phase_1l5cg"]["identity_sha256"]:
        raise RuntimeError("central taper custody drift")
    return accepted, depth, waist


def coordinates(obj, indices):
    return [[index, *[round(value, 9) for value in obj.data.vertices[index].co]] for index in sorted(indices)]


def apply_correction(top, accepted, depth, waist):
    before_coordinates = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    before_weights = rounded["weight_semantic"](top)
    depth_target = set(depth["semantic"]["correction"]["target_vertex_indices"])
    waist_target = set(waist["semantic"]["correction"]["target_vertex_indices"])
    central_tapers = depth_target | waist_target
    outer_span = set(accepted["semantic"]["correction"]["target_vertex_indices"])

    coordinate_target = {
        index for index in outer_span
        if top.data.vertices[index].co.z >= 1.30
    }
    weight_target = {
        vertex.index for vertex in top.data.vertices
        if (vertex.co.z >= 1.30 or vertex.co.z <= 1.10)
        and any(top.vertex_groups[group.group].name.startswith("upper_arm.") for group in vertex.groups)
    }
    if not coordinate_target or not weight_target:
        raise RuntimeError("articulation correction selected no vertices")
    if coordinate_target & central_tapers:
        raise RuntimeError("coordinate target overlaps an accepted central taper")

    for index in coordinate_target:
        vertex = top.data.vertices[index]
        x, y, z = vertex.co
        lateral = base["smoothstep"]((abs(x) - 0.24) / 0.24)
        vertex.co.y = 0.02 + (y - 0.02) * (0.84 - 0.12 * lateral)
        cap = 1.52 - 0.18 * lateral
        vertex.co.z = min(z, cap)
    top.data.update()

    spine = top.vertex_groups["spine"]
    left = top.vertex_groups["upper_arm.L"]
    right = top.vertex_groups["upper_arm.R"]
    for index in weight_target:
        vertex = top.data.vertices[index]
        lateral = base["smoothstep"]((abs(vertex.co.x) - 0.24) / 0.24)
        arm_weight = (0.04 + 0.08 * lateral) if vertex.co.z <= 1.10 else (0.02 + 0.12 * lateral)
        arm = left if vertex.co.x > 0 else right
        other = right if vertex.co.x > 0 else left
        spine.add([index], 1.0 - arm_weight, "REPLACE")
        arm.add([index], arm_weight, "REPLACE")
        try:
            other.remove([index])
        except RuntimeError:
            pass

    coordinate_protected = set(before_coordinates) - coordinate_target
    weight_protected = set(before_coordinates) - weight_target
    if coordinate_target & coordinate_protected or weight_target & weight_protected:
        raise RuntimeError("target/protected ledger overlap")
    if coordinates(top, coordinate_protected) != [[index, *[round(value, 9) for value in before_coordinates[index]]] for index in sorted(coordinate_protected)]:
        raise RuntimeError("protected coordinate drift")
    after_weights = rounded["weight_semantic"](top)
    if [after_weights[index] for index in sorted(weight_protected)] != [before_weights[index] for index in sorted(weight_protected)]:
        raise RuntimeError("protected weight drift")

    body_bounds = accepted["semantic"]["deformation"]["frames"][0]["bounds_m"][BODY]
    body_width = body_bounds["max"][0] - body_bounds["min"][0]
    source_width = max(value[0] for value in before_coordinates.values()) - min(value[0] for value in before_coordinates.values())
    derived_width = max(vertex.co.x for vertex in top.data.vertices) - min(vertex.co.x for vertex in top.data.vertices)
    ratio = derived_width / body_width
    if ratio > 1.4:
        raise RuntimeError(f"width ratio exceeds contract: {ratio}")

    coordinate_displacement = [math.dist(before_coordinates[index], top.data.vertices[index].co) for index in coordinate_target]
    return {
        "coordinate_target_vertex_count": len(coordinate_target),
        "coordinate_target_vertex_indices": sorted(coordinate_target),
        "coordinate_protected_vertex_count": len(coordinate_protected),
        "coordinate_protected_vertex_indices": sorted(coordinate_protected),
        "coordinate_target_protected_overlap_count": len(coordinate_target & coordinate_protected),
        "weight_target_vertex_count": len(weight_target),
        "weight_target_vertex_indices": sorted(weight_target),
        "weight_protected_vertex_count": len(weight_protected),
        "weight_protected_vertex_indices": sorted(weight_protected),
        "weight_target_protected_overlap_count": len(weight_target & weight_protected),
        "protected_depth_taper_indices": sorted(depth_target),
        "protected_waist_taper_indices": sorted(waist_target),
        "coordinate_target_depth_taper_overlap_count": len(coordinate_target & depth_target),
        "coordinate_target_waist_taper_overlap_count": len(coordinate_target & waist_target),
        "source_coordinate_target_sha256": semantic_sha(coordinates_from_map(before_coordinates, coordinate_target)),
        "derived_coordinate_target_sha256": semantic_sha(coordinates(top, coordinate_target)),
        "source_coordinate_protected_sha256": semantic_sha(coordinates_from_map(before_coordinates, coordinate_protected)),
        "derived_coordinate_protected_sha256": semantic_sha(coordinates(top, coordinate_protected)),
        "source_weight_target_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(weight_target)]),
        "derived_weight_target_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(weight_target)]),
        "source_weight_protected_sha256": semantic_sha([[index, before_weights[index]] for index in sorted(weight_protected)]),
        "derived_weight_protected_sha256": semantic_sha([[index, after_weights[index]] for index in sorted(weight_protected)]),
        "maximum_coordinate_displacement_m": round(max(coordinate_displacement), 9),
        "source_top_width_m": round(source_width, 9),
        "derived_top_width_m": round(derived_width, 9),
        "body_width_m": round(body_width, 9),
        "derived_top_to_body_width_ratio": round(ratio, 9),
        "maximum_top_to_body_width_ratio": 1.4,
    }


def coordinates_from_map(values, indices):
    return [[index, *[round(value, 9) for value in values[index]]] for index in sorted(indices)]


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
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5ck</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5cm</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5cm before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5cm shoulder-cap / sleeve / hem articulation correction</h1>'
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
        "body": semantic_sha(base["mesh_semantic"](body)),
        "top": semantic_sha(base["mesh_semantic"](top)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    correction = apply_correction(top, accepted, depth, waist)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "item_id": top.get("item_id"),
        "openings": renderer["opening_proof"](top),
    }
    for key in ("body", "bottom", "armature", "action", "materials", "topology", "item_id"):
        if after[key] != before[key]:
            raise RuntimeError(f"non-target identity drift: {key}")
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "articulated starter top"),
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
        "accepted_phase_1l5ck": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "minimum_outer_cap_coordinates_plus_normalized_spine_arm_weight_blend", "excluded": ["central_depth_taper_coordinates", "central_waist_taper_coordinates", "non_target_coordinates", "non_target_weights", "topology", "materials", "item_identity", "body", "shorts", "skeleton", "action"]},
        "topology": topology,
        "opening_geometry": {"source": before["openings"], "derived": after["openings"], "contract": "one component / four openings / zero other non-manifold edges"},
        "panel_roles": rounded["role_counts"](top),
        "weights": weights,
        "weight_semantic": rounded["weight_semantic"](top),
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "opening_contract_changed": 0, "central_taper_coordinates_changed": 0, "non_target_coordinates_changed": 0, "non_target_weights_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False, "export_import_preparation_stopped": True},
    }
    if correction["source_coordinate_protected_sha256"] != correction["derived_coordinate_protected_sha256"]:
        raise RuntimeError("protected coordinate identity drift")
    if correction["source_weight_protected_sha256"] != correction["derived_weight_protected_sha256"]:
        raise RuntimeError("protected weight identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cm provenance\n\n"
        "- Additive derivative of exact Phase 1L.5ck custody after the fail-closed Phase 1L.5cl review.\n"
        "- Changes only the minimum selected outer top coordinates and normalized spine/upper-arm weights needed for shoulder-cap, sleeve and hem articulation.\n"
        "- Central depth/waist taper coordinates, protected coordinates and weights, topology, item/material/color, body, shorts, DEC-035 and walk action remain exact.\n"
        "- Before/after neutral and opposing-extreme views are a correction proof, not a visual-acceptance verdict.\n"
        "- Export/import preparation remains stopped; no runtime, final-art or readiness claim is included.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5cm shoulder-cap/sleeve/hem articulation correction walk proof",
        "status": "offline_targeted_top_articulation_correction_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TOP_ARTICULATION_WALK_PASS frames=21 coordinates={correction['coordinate_target_vertex_count']} weights={correction['weight_target_vertex_count']} ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


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
    if rounded["material_semantic"](top) != semantic["material_semantic"]:
        raise RuntimeError("material drift")
    if r3["topology_proof"](top, (1, 4, 0), "articulated starter top") != semantic["topology"][TOP]:
        raise RuntimeError("topology drift")
    if renderer["opening_proof"](top) != semantic["opening_geometry"]["derived"]:
        raise RuntimeError("opening geometry drift")
    if rounded["weight_semantic"](top) != semantic["weight_semantic"]:
        raise RuntimeError("saved weight drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    correction = semantic["correction"]
    if correction["coordinate_target_protected_overlap_count"] or correction["weight_target_protected_overlap_count"] or correction["coordinate_target_depth_taper_overlap_count"] or correction["coordinate_target_waist_taper_overlap_count"]:
        raise RuntimeError("target/protected ledger drift")
    print(f"TOP_ARTICULATION_WALK_VALIDATE_PASS ratio={correction['derived_top_to_body_width_ratio']} identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
