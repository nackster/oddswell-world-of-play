"""Build and validate the Phase 1L.5ce targeted starter-top silhouette correction."""

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
SOURCE_ROOT = SLICE / "TailoredStarterTopWalkProof"
SOURCE_BUILDER = SOURCE_ROOT / "build_tailored_starter_top_walk.py"
source_phase = {"__file__": str(SOURCE_BUILDER)}
source = SOURCE_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], source_phase)
base, r3, prior = source_phase["base"], source_phase["r3"], source_phase["phase"]["phase"]

BODY, TOP, BOTTOM, ARMATURE = (source_phase[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SOURCE_ROOT / "RefinedSundaleTailoredStarterTopWalk.blend"
SOURCE_MANIFEST = SOURCE_ROOT / "tailored_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleRoundedStarterTopWalk.blend"
MANIFEST = ROOT / "rounded_starter_top_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BOARD = REVIEWS / "BeforeAfter.html"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
SOURCE_TOP_SHA = "20DEC799B15A77DC97EB4CCE521A84362AB952725ACD38C028918AABEC29C73C"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"
SOURCE_IDENTITY = "E56486E7D7DCB87586E6AFC9EF07E8FB85008D78F9231F75D9019B32D1D0E0C4"
VIEWS = ("Front", "Rear", "Profile", "WalkExtremeFront", "WalkExtremeRear")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_custody():
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["identity_sha256"] != SOURCE_IDENTITY:
        raise RuntimeError("Phase 1L.5cc semantic custody drift")
    expected = manifest["files"]["blend"]
    actual = {"bytes": SOURCE_BLEND.stat().st_size, "sha256": sha256(SOURCE_BLEND)}
    if actual != expected:
        raise RuntimeError(f"Phase 1L.5cc Blend custody drift: {actual}")
    semantic = manifest["semantic"]
    checks = (
        semantic["accepted_mesh_sha256"][BODY] == BODY_SHA,
        semantic["derived_mesh_sha256"][TOP] == SOURCE_TOP_SHA,
        semantic["accepted_mesh_sha256"][BOTTOM] == BOTTOM_SHA,
        semantic["action"]["identity_sha256"] == ACTION_SHA,
        semantic["armature"]["bone_count"] == 12,
    )
    if not all(checks):
        raise RuntimeError("accepted Phase 1L.5cc identity drift")
    return manifest


def boundary_index_loops(obj):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    mesh.verts.ensure_lookup_table()
    loops = []
    for vertices in source_phase["boundary_loops"](mesh):
        loops.append({vertex.index for vertex in vertices})
    mesh.free()
    return loops


def coordinates(obj, indices):
    return [[round(obj.data.vertices[index].co[axis], 9) for axis in range(3)] for index in sorted(indices)]


def material_semantic(obj):
    return [{"name": slot.material.name, "diffuse_color": [round(value, 9) for value in slot.material.diffuse_color]} for slot in obj.material_slots]


def topology_semantic(obj):
    return {
        "vertices": len(obj.data.vertices),
        "edges": [list(edge.vertices) for edge in obj.data.edges],
        "polygons": [list(polygon.vertices) for polygon in obj.data.polygons],
        "material_indices": [polygon.material_index for polygon in obj.data.polygons],
    }


def weight_semantic(obj):
    return [
        [[obj.vertex_groups[group.group].name, round(group.weight, 9)] for group in sorted(vertex.groups, key=lambda item: obj.vertex_groups[item.group].name)]
        for vertex in obj.data.vertices
    ]


def targeted_correction(top):
    loops = boundary_index_loops(top)
    waist = next(loop for loop in loops if max(abs(top.data.vertices[i].co.z - 1.0) for i in loop) < 1e-6)
    neckline = next(loop for loop in loops if min(top.data.vertices[i].co.z for i in loop) >= 1.49)
    protected = waist | neckline
    before = {vertex.index: tuple(vertex.co) for vertex in top.data.vertices}
    target = set()
    for vertex in top.data.vertices:
        x, y, z = vertex.co
        a = abs(x)
        if vertex.index in protected or a <= 0.16:
            continue
        shoulder = z > 1.34 and a > 0.16
        sleeve = z > 1.15 and a > 0.34
        side = 1.04 < z <= 1.36 and a > 0.28
        if not (shoulder or sleeve or side):
            continue
        target.add(vertex.index)
        side_weight = base["smoothstep"]((a - 0.16) / 0.44)
        height_weight = base["smoothstep"]((z - 1.04) / 0.24)
        new_a = a
        if a > 0.38:
            new_a = 0.38 + (a - 0.38) * 0.43
        elif side:
            new_a = a - (a - 0.28) * 0.10 * height_weight
        vertex.co.x = math.copysign(new_a, x)
        if shoulder:
            vertex.co.z -= 0.115 * side_weight * base["smoothstep"]((z - 1.34) / 0.20)
        vertex.co.y = 0.02 + (y - 0.02) * (1.0 - 0.17 * side_weight)
    top.data.update()
    if not target:
        raise RuntimeError("targeted silhouette correction selected no vertices")
    non_target = set(before) - target
    if any(tuple(top.data.vertices[index].co) != before[index] for index in non_target):
        raise RuntimeError("non-target top vertex drift")
    if coordinates(top, waist) != [[round(before[i][axis], 9) for axis in range(3)] for i in sorted(waist)]:
        raise RuntimeError("waist-hem boundary drift")
    if coordinates(top, neckline) != [[round(before[i][axis], 9) for axis in range(3)] for i in sorted(neckline)]:
        raise RuntimeError("neckline boundary drift")
    source_span = 2 * max(abs(coordinate[0]) for coordinate in before.values())
    derived_span = 2 * max(abs(vertex.co.x) for vertex in top.data.vertices)
    max_displacement = max(math.dist(before[index], top.data.vertices[index].co) for index in target)
    if derived_span >= source_span - 0.20 or derived_span > 1.01:
        raise RuntimeError(f"boxlike lateral span not removed: source={source_span} derived={derived_span}")
    return {
        "target_vertex_count": len(target),
        "target_vertex_indices": sorted(target),
        "non_target_vertex_count": len(non_target),
        "protected_waist_indices": sorted(waist),
        "protected_neckline_indices": sorted(neckline),
        "source_non_target_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(non_target)]),
        "derived_non_target_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(non_target)]),
        "source_target_coordinate_sha256": semantic_sha([[index, *before[index]] for index in sorted(target)]),
        "derived_target_coordinate_sha256": semantic_sha([[index, *tuple(top.data.vertices[index].co)] for index in sorted(target)]),
        "source_lateral_span_m": round(source_span, 9),
        "derived_lateral_span_m": round(derived_span, 9),
        "maximum_target_vertex_displacement_m": round(max_displacement, 9),
        "source_waist_coordinates": [[round(before[i][axis], 9) for axis in range(3)] for i in sorted(waist)],
        "source_neckline_coordinates": [[round(before[i][axis], 9) for axis in range(3)] for i in sorted(neckline)],
    }


def role_counts(top):
    roles = {name: 0 for name in ("front_panel", "rear_panel", "left_sleeve", "right_sleeve", "neckline", "side_seam", "hem")}
    for polygon in top.data.polygons:
        center = polygon.center
        roles["rear_panel" if center.y >= 0.02 else "front_panel"] += 1
        if center.x > 0.25:
            roles["left_sleeve"] += 1
        elif center.x < -0.25:
            roles["right_sleeve"] += 1
        if center.z > 1.42 and abs(center.x) < 0.22:
            roles["neckline"] += 1
        elif center.z < 1.07:
            roles["hem"] += 1
        elif 0.21 < abs(center.x) < 0.34 and center.z < 1.30:
            roles["side_seam"] += 1
    if any(value <= 0 for value in roles.values()):
        raise RuntimeError(f"role evidence incomplete: {roles}")
    return roles


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    source_receipts = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))["files"]["reviews"]
    for name in VIEWS:
        source_path = SOURCE_ROOT / "Review" / f"{name}.png"
        if {"bytes": source_path.stat().st_size, "sha256": sha256(source_path)} != source_receipts[f"{name}.png"]:
            raise RuntimeError(f"source review drift: {name}")
        shutil.copyfile(source_path, REVIEWS / f"Before_{name}.png")
    source_phase["REVIEWS"] = REVIEWS
    after = source_phase["render_reviews"]()
    for name in VIEWS:
        (REVIEWS / f"{name}.png").replace(REVIEWS / f"After_{name}.png")
    rows = "\n".join(
        f'<section><h2>{name}</h2><div><figure><figcaption>BEFORE 1L.5cc</figcaption><img src="Before_{name}.png"></figure>'
        f'<figure><figcaption>AFTER 1L.5ce</figcaption><img src="After_{name}.png"></figure></div></section>'
        for name in VIEWS
    )
    BOARD.write_text(
        '<!doctype html><meta charset="utf-8"><title>Phase 1L.5ce before / after</title>'
        '<style>body{margin:20px;background:#181a1f;color:#eee;font:16px sans-serif}section{margin-bottom:24px}'
        'section>div{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;display:block}'
        'figcaption{padding:8px;background:#30343c}h1,h2{margin:8px 0}</style>'
        '<h1>Phase 1L.5ce targeted top-silhouette correction</h1><p>Direct offline comparison; not final acceptance.</p>' + rows,
        encoding="utf-8",
    )
    receipts = {}
    for path in sorted(REVIEWS.glob("*")):
        if path.is_file():
            receipts[path.name] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    return receipts


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
        "materials": material_semantic(top),
        "topology": topology_semantic(top),
        "weights": weight_semantic(top),
        "item_id": top.get("item_id"),
    }
    if (before["body"], before["top"], before["bottom"], before["action"]["identity_sha256"]) != (BODY_SHA, SOURCE_TOP_SHA, BOTTOM_SHA, ACTION_SHA):
        raise RuntimeError("accepted source identity drift")
    correction = targeted_correction(top)
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": prior["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
        "materials": material_semantic(top),
        "topology": topology_semantic(top),
        "weights": weight_semantic(top),
        "item_id": top.get("item_id"),
    }
    if after != {key: before[key] for key in after}:
        raise RuntimeError("non-target body/bottom/armature/action/material/topology drift")
    openings = source_phase["opening_proof"](top)
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "rounded starter top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts"),
    }
    weights = {
        TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}),
        BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}),
    }
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    reviews = render_reviews()
    semantic = {
        "accepted_phase_1l5cc": {"identity_sha256": SOURCE_IDENTITY, "blend": accepted["files"]["blend"]},
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "source_mesh_sha256": {TOP: SOURCE_TOP_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "correction": correction,
        "construction": {"method": "coordinate_only_targeted_rounded_shoulder_sleeve_side_correction", "excluded": ["neckline", "waist_hem", "central_front_rear_pattern", "materials", "details", "shorts", "body", "skeleton", "action"]},
        "topology": topology,
        "declared_opening_geometry": openings,
        "panel_roles": role_counts(top),
        "weights": weights,
        "material_semantic": after["materials"],
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "materials_changed": 0, "topology_changed": 0, "non_target_top_vertices_changed": 0, "runtime_changed": 0, "final_acceptance_verdict": None, "readiness_claim": False},
    }
    if correction["source_non_target_coordinate_sha256"] != correction["derived_non_target_coordinate_sha256"]:
        raise RuntimeError("non-target coordinate identity drift")
    semantic["identity_sha256"] = semantic_sha(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5ce provenance\n\n"
        "- Additive derivative of exact Phase 1L.5cc custody after the Phase 1L.5cd visual rejection.\n"
        "- Only targeted starter-top shoulder, sleeve and side coordinates change.\n"
        "- Neckline, waist hem, central pattern, topology, weights, materials, body, shorts, armature and walk remain exact.\n"
        "- The direct before/after evidence is a correction proof, not a repeated acceptance verdict.\n"
        "- No export, runtime, final-art, performance or readiness claim is included.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5ce starter-top rounded shoulder/sleeve/side silhouette correction walk proof",
        "status": "offline_targeted_top_silhouette_correction_not_visual_acceptance_or_runtime",
        "semantic": semantic,
        "files": {
            "blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
            "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "reviews": reviews,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ROUNDED_STARTER_TOP_WALK_PASS frames=21 target={correction['target_vertex_count']} identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_custody()
    for name, path in (("blend", OUTPUT), ("builder", Path(__file__)), ("provenance", PROVENANCE)):
        if manifest["files"][name] != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"{name} custody drift")
    for name, receipt in manifest["files"]["reviews"].items():
        path = REVIEWS / name
        if receipt != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"review custody drift: {name}")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    semantic = manifest["semantic"]
    if semantic_sha(base["mesh_semantic"](body)) != BODY_SHA or semantic_sha(base["mesh_semantic"](bottom)) != BOTTOM_SHA:
        raise RuntimeError("accepted body/bottom drift")
    if semantic_sha(base["mesh_semantic"](top)) != semantic["derived_mesh_sha256"][TOP]:
        raise RuntimeError("corrected top drift")
    if material_semantic(top) != semantic["material_semantic"]:
        raise RuntimeError("saved material identity drift")
    if r3["topology_proof"](top, (1, 4, 0), "rounded starter top") != semantic["topology"][TOP]:
        raise RuntimeError("saved topology drift")
    if source_phase["opening_proof"](top) != semantic["declared_opening_geometry"]:
        raise RuntimeError("saved opening drift")
    correction = semantic["correction"]
    if coordinates(top, correction["protected_waist_indices"]) != correction["source_waist_coordinates"]:
        raise RuntimeError("saved waist-hem boundary drift")
    if coordinates(top, correction["protected_neckline_indices"]) != correction["source_neckline_coordinates"]:
        raise RuntimeError("saved neckline boundary drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    if prior["armature_semantic"](armature) != semantic["armature"]["hierarchy"]:
        raise RuntimeError("saved armature drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != semantic["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("saved action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != semantic["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"ROUNDED_STARTER_TOP_WALK_VALIDATE_PASS identity={semantic['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
