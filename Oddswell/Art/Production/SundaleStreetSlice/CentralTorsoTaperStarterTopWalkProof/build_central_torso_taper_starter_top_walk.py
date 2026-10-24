"""Build or validate the Phase 1L.5cg central torso-depth taper proof."""

import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
SOURCE_ROOT = SLICE / "RoundedStarterTopSilhouetteWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_rounded_starter_top_silhouette_walk.py"
rounded = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], rounded)
base, r3, prior = rounded["base"], rounded["r3"], rounded["prior"]
renderer = rounded["source_phase"]

BODY, TOP, BOTTOM, ARMATURE = (rounded[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleRoundedStarterTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "rounded_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleCentralTorsoTaperStarterTopWalk.blend"
MANIFEST = ROOT / "central_torso_taper_starter_top_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "A9DD780C47AC50F1383BA23F4393167E0EC51C62616D868E421C5CD5C3CAAADB"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "7F5D0C4606DF10318372771F7D431AC3884B7858F5304BB22D198BC63301F220"
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
    )
    if not all(checks):
        raise RuntimeError("Phase 1L.5ce custody drift")
    return manifest


def coordinate_rows(obj, indices):
    return [[index, *[round(obj.data.vertices[index].co[axis], 9) for axis in range(3)]] for index in sorted(indices)]


def central_torso_taper(top, source_manifest):
    prior_correction = source_manifest["semantic"]["correction"]
    protected_previous = set(prior_correction["target_vertex_indices"])
    protected_openings = set(prior_correction["protected_waist_indices"]) | set(prior_correction["protected_neckline_indices"])
    before = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    target = {
        vertex.index
        for vertex in top.data.vertices
        if vertex.index not in protected_previous
        and vertex.index not in protected_openings
        and abs(vertex.co.x) <= 0.198001
        and 1.049 <= vertex.co.z <= 1.451
        and abs(vertex.co.y - 0.02) > 0.10
    }
    if not target:
        raise RuntimeError("central torso taper selected no vertices")
    for index in target:
        vertex = top.data.vertices[index]
        vertical = max(0.0, min(1.0, (vertex.co.z - 1.05) / 0.40))
        edge_blend = 1.0 - 0.25 * min(1.0, abs(vertex.co.x) / 0.198)
        desired_scale = 0.91 + 0.07 * math.sin(math.pi * vertical)
        scale = 1.0 - (1.0 - desired_scale) * edge_blend
        vertex.co.y = 0.02 + (vertex.co.y - 0.02) * scale
    top.data.update()
    protected = set(before) - target
    if any(tuple(top.data.vertices[index].co) != before[index] for index in protected):
        raise RuntimeError("protected top coordinate drift")
    if target & protected_previous or target & protected_openings:
        raise RuntimeError("target/protected coordinate ledger overlap")
    displacement = [math.dist(before[index], top.data.vertices[index].co) for index in target]
    low = [index for index in target if top.data.vertices[index].co.z <= 1.15]
    middle = [index for index in target if 1.20 <= top.data.vertices[index].co.z <= 1.30]
    high = [index for index in target if top.data.vertices[index].co.z >= 1.35]
    reduction = lambda indices: round(sum(abs(before[i][1] - 0.02) - abs(top.data.vertices[i].co.y - 0.02) for i in indices) / len(indices), 9)
    bands = {"lower_mean_depth_reduction_m": reduction(low), "middle_mean_depth_reduction_m": reduction(middle), "upper_mean_depth_reduction_m": reduction(high)}
    if min(bands["lower_mean_depth_reduction_m"], bands["upper_mean_depth_reduction_m"]) <= bands["middle_mean_depth_reduction_m"] + 0.005:
        raise RuntimeError(f"central torso taper is not pronounced: {bands}")
    return {
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "protected_vertex_count": len(protected),
        "protected_previous_shoulder_sleeve_side_indices": sorted(protected_previous),
        "protected_opening_boundary_indices": sorted(protected_openings),
        "source_target_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(target)]),
        "derived_target_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(target)]),
        "source_protected_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(protected)]),
        "derived_protected_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(protected)]),
        "coordinate_axes_changed": ["y"],
        "maximum_target_vertex_displacement_m": round(max(displacement), 9),
        "depth_profile": bands,
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
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5ce</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5cg</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5cg before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5cg central torso-depth taper</h1><p>Targeted correction proof only; no acceptance verdict.</p>' + rows,
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
        "weights": rounded["weight_semantic"](top),
        "item_id": top.get("item_id"),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    correction = central_torso_taper(top, accepted)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": rounded["material_semantic"](top),
        "topology": rounded["topology_semantic"](top),
        "weights": rounded["weight_semantic"](top),
        "item_id": top.get("item_id"),
    }
    if after != {key: before[key] for key in after}:
        raise RuntimeError("non-target identity drift")
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "central-taper starter top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts"),
    }
    weights = {TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}), BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    semantic = {
        "accepted_phase_1l5ce": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "coordinate_only_central_front_rear_torso_depth_taper", "excluded": ["shoulders", "sleeves", "sides", "openings", "topology", "weights", "materials", "body", "shorts", "skeleton", "action"]},
        "topology": topology,
        "declared_opening_geometry": renderer["opening_proof"](top),
        "panel_roles": rounded["role_counts"](top),
        "weights": weights,
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "protected_top_vertices_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False},
    }
    if correction["source_protected_coordinate_sha256"] != correction["derived_protected_coordinate_sha256"]:
        raise RuntimeError("protected coordinate identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cg provenance\n\n"
        "- Additive derivative of exact Phase 1L.5ce custody after the Phase 1L.5cf rejection.\n"
        "- Only central front/rear starter-top torso-depth coordinates change.\n"
        "- Corrected shoulders/sleeves/sides, all openings, topology, weights, materials, body, shorts, armature and walk remain exact.\n"
        "- Before/after evidence is a correction proof, not an acceptance verdict.\n"
        "- No export, runtime, final-art, performance or readiness claim is included.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5cg starter-top central torso-depth taper correction walk proof",
        "status": "offline_targeted_central_torso_taper_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CENTRAL_TORSO_TAPER_WALK_PASS frames=21 target={correction['target_vertex_count']} identity={semantic['identity_sha256']}")


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
    if r3["topology_proof"](top, (1, 4, 0), "central-taper starter top") != semantic["topology"][TOP]:
        raise RuntimeError("topology drift")
    if renderer["opening_proof"](top) != semantic["declared_opening_geometry"]:
        raise RuntimeError("opening drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"CENTRAL_TORSO_TAPER_WALK_VALIDATE_PASS identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
