"""Build or validate the Phase 1L.5ci central lateral waist-taper proof."""

import bpy
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
SOURCE_ROOT = SLICE / "CentralTorsoTaperStarterTopWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_central_torso_taper_starter_top_walk.py"
source_phase = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], source_phase)
base, r3, prior, renderer = (source_phase[name] for name in ("base", "r3", "prior", "renderer"))

BODY, TOP, BOTTOM, ARMATURE = (source_phase[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleCentralTorsoTaperStarterTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "central_torso_taper_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleLateralWaistTaperStarterTopWalk.blend"
MANIFEST = ROOT / "lateral_waist_taper_starter_top_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "1C7F8649211C44B9039F12902E266C438C5EF6DA4DF224D7FBD1FCF108AEC353"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "8B8008D832BFB0D1C1753D24AE2AF99C5CAE6CE24B8ED30439438904A0A55A61"
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
        raise RuntimeError("Phase 1L.5cg custody drift")
    return manifest


def band_half_width(obj, indices):
    return round(max(abs(obj.data.vertices[index].co.x) for index in indices), 9)


def boundary_vertex_indices(obj):
    edge_faces = {}
    for polygon in obj.data.polygons:
        vertices = polygon.vertices
        for offset, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(offset + 1) % len(vertices)])))
            edge_faces[edge] = edge_faces.get(edge, 0) + 1
    return {index for edge, faces in edge_faces.items() if faces == 1 for index in edge}


def lateral_waist_taper(top, source_manifest):
    before = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    shoulder_sleeve = {vertex.index for vertex in top.data.vertices if vertex.co.z > 1.35 or abs(vertex.co.x) > 0.40}
    inherited_opening_protection = set(source_manifest["semantic"]["correction"]["protected_opening_boundary_indices"])
    protected_openings = boundary_vertex_indices(top)
    if not inherited_opening_protection <= protected_openings:
        raise RuntimeError("inherited opening protection is not a subset of the exact source boundaries")
    target = {
        vertex.index
        for vertex in top.data.vertices
        if vertex.index not in shoulder_sleeve
        and vertex.index not in protected_openings
        and 0.999 <= vertex.co.z <= 1.35
        and abs(vertex.co.x) >= 0.197999
        and abs(vertex.co.y - 0.02) > 0.10
    }
    if not target:
        raise RuntimeError("lateral waist taper selected no vertices")
    bands = {
        "lower": {index for index in target if top.data.vertices[index].co.z <= 1.10},
        "middle": {index for index in target if 1.10 < top.data.vertices[index].co.z <= 1.25},
        "upper": {index for index in target if top.data.vertices[index].co.z > 1.25},
    }
    if any(not indices for indices in bands.values()):
        raise RuntimeError(f"waist-taper band evidence incomplete: {bands}")
    source_widths = {name: band_half_width(top, indices) for name, indices in bands.items()}
    for index in target:
        vertex = top.data.vertices[index]
        height = max(0.0, min(1.0, (vertex.co.z - 1.0) / 0.35))
        scale = 0.86 + 0.14 * (height * height * (3.0 - 2.0 * height))
        vertex.co.x = math.copysign(abs(vertex.co.x) * scale, vertex.co.x)
    top.data.update()
    protected = set(before) - target
    if target & protected or target & shoulder_sleeve or target & protected_openings:
        raise RuntimeError("target/protected ledger overlap")
    if any(tuple(top.data.vertices[index].co) != before[index] for index in protected):
        raise RuntimeError("protected coordinate drift")
    if any(top.data.vertices[index].co.y != before[index][1] or top.data.vertices[index].co.z != before[index][2] for index in target):
        raise RuntimeError("target changed a non-X coordinate")
    derived_widths = {name: band_half_width(top, indices) for name, indices in bands.items()}
    reductions = {name: round(source_widths[name] - derived_widths[name], 9) for name in bands}
    if not (reductions["lower"] > reductions["middle"] > reductions["upper"] >= 0.0):
        raise RuntimeError(f"waist taper is not monotonic: {reductions}")
    displacement = [math.dist(before[index], top.data.vertices[index].co) for index in target]
    return {
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "protected_vertex_count": len(protected),
        "protected_shoulder_sleeve_indices": sorted(shoulder_sleeve),
        "inherited_protected_opening_boundary_indices": sorted(inherited_opening_protection),
        "protected_opening_boundary_indices": sorted(protected_openings),
        "target_opening_boundary_overlap_count": len(target & protected_openings),
        "target_inherited_opening_boundary_overlap_count": len(target & inherited_opening_protection),
        "source_target_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(target)]),
        "derived_target_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(target)]),
        "source_protected_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(protected)]),
        "derived_protected_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(protected)]),
        "source_all_yz_sha256": semantic_sha([[index, before[index][1], before[index][2]] for index in sorted(before)]),
        "derived_all_yz_sha256": semantic_sha([[vertex.index, vertex.co.y, vertex.co.z] for vertex in top.data.vertices]),
        "coordinate_axes_changed": ["x"],
        "maximum_target_vertex_displacement_m": round(max(displacement), 9),
        "half_width_m": {name: {"source": source_widths[name], "derived": derived_widths[name], "reduction": reductions[name]} for name in bands},
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
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5cg</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5ci</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5ci before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5ci central lateral waist taper</h1><p>Targeted correction proof only; no acceptance verdict.</p>' + rows,
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
        "materials": source_phase["rounded"]["material_semantic"](top),
        "topology": source_phase["rounded"]["topology_semantic"](top),
        "weights": source_phase["rounded"]["weight_semantic"](top),
        "item_id": top.get("item_id"),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    correction = lateral_waist_taper(top, accepted)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": source_phase["rounded"]["material_semantic"](top),
        "topology": source_phase["rounded"]["topology_semantic"](top),
        "weights": source_phase["rounded"]["weight_semantic"](top),
        "item_id": top.get("item_id"),
    }
    if after != {key: before[key] for key in after}:
        raise RuntimeError("non-target identity drift")
    topology = {TOP: r3["topology_proof"](top, (1, 4, 0), "lateral-taper starter top"), BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts")}
    weights = {TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}), BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    opening_geometry = renderer["opening_proof"](top)
    if opening_geometry != accepted["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("source opening geometry changed")
    semantic = {
        "accepted_phase_1l5cg": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "coordinate_only_central_front_rear_lateral_waist_taper", "excluded": ["shoulders", "sleeves", "depth_y", "height_z", "topology", "weights", "materials", "body", "shorts", "skeleton", "action"]},
        "topology": topology,
        "declared_opening_geometry": opening_geometry,
        "panel_roles": source_phase["rounded"]["role_counts"](top),
        "weights": weights,
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "opening_geometry_changed": 0, "target_y_changed": 0, "target_z_changed": 0, "protected_top_vertices_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False},
    }
    if correction["source_protected_coordinate_sha256"] != correction["derived_protected_coordinate_sha256"] or correction["source_all_yz_sha256"] != correction["derived_all_yz_sha256"]:
        raise RuntimeError("protected or Y/Z identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    reviews = render_reviews()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5ci provenance\n\n"
        "- Additive derivative of exact Phase 1L.5cg custody after the Phase 1L.5ch rejection.\n"
        "- Only central front/rear starter-top lateral X coordinates taper toward the waist.\n"
        "- All exact source opening-boundary vertices are protected; target/opening overlap is zero and opening geometry reproduces exactly.\n"
        "- Shoulders, sleeves, accepted Y-depth taper, every Z coordinate, topology, weights, materials, body, shorts, armature and walk remain exact.\n"
        "- Before/after evidence is a correction proof, not an acceptance verdict.\n"
        "- No export, runtime, final-art, performance or readiness claim is included.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5ci central front/rear lateral waist-taper correction walk proof",
        "status": "offline_targeted_lateral_waist_taper_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {"blend": receipt(OUTPUT), "builder": receipt(Path(__file__)), "provenance": receipt(PROVENANCE), "reviews": reviews},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"LATERAL_WAIST_TAPER_WALK_PASS frames=21 target={correction['target_vertex_count']} identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    accepted = source_custody()
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
    if source_phase["rounded"]["material_semantic"](top) != semantic["material_semantic"]:
        raise RuntimeError("material drift")
    if r3["topology_proof"](top, (1, 4, 0), "lateral-taper starter top") != semantic["topology"][TOP]:
        raise RuntimeError("topology drift")
    opening_geometry = renderer["opening_proof"](top)
    if opening_geometry != semantic["declared_opening_geometry"] or opening_geometry != accepted["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("opening drift")
    correction = semantic["correction"]
    if correction["target_opening_boundary_overlap_count"] != 0:
        raise RuntimeError("target/opening boundary overlap")
    if correction["target_inherited_opening_boundary_overlap_count"] != 0:
        raise RuntimeError("target/inherited opening boundary overlap")
    inherited_openings = set(accepted["semantic"]["correction"]["protected_opening_boundary_indices"])
    if set(correction["inherited_protected_opening_boundary_indices"]) != inherited_openings:
        raise RuntimeError("inherited opening protection drift")
    if set(correction["protected_opening_boundary_indices"]) != boundary_vertex_indices(top):
        raise RuntimeError("source opening boundary ledger drift")
    if set(correction["target_vertex_indices"]) & set(correction["protected_opening_boundary_indices"]):
        raise RuntimeError("target/opening boundary ledger overlap")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"LATERAL_WAIST_TAPER_WALK_VALIDATE_PASS identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
