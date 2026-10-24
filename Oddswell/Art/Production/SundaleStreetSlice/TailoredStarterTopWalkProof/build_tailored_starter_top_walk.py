"""Build and validate the Phase 1L.5cc tailored starter-top walk proof."""

import bmesh
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
BOTTOM_BUILDER = SLICE / "BelievableStarterShortsWalkProof/build_believable_starter_shorts_walk.py"
phase = {"__file__": str(BOTTOM_BUILDER)}
source = BOTTOM_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], phase)
r3, base = phase["r3"], phase["base"]

BODY, TOP, BOTTOM, ARMATURE = (phase[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SLICE / "BelievableStarterShortsWalkProof/RefinedSundaleStarterShortsPanelWalk.blend"
SOURCE_MANIFEST = SLICE / "BelievableStarterShortsWalkProof/starter_shorts_panel_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleTailoredStarterTopWalk.blend"
MANIFEST = ROOT / "tailored_starter_top_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
BOTTOM_SHA = "E626B69FA039E1E1139ACD203AB6F481CADDC49771ADA7341B8ED3A1D9C82170"
SOURCE_TOP_SHA = "095929FDAE403198912D8BEC21EE0A28EB579AEB5BC2BB9BD2CC25C0A72ED54A"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def source_custody():
    receipt = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    expected = receipt["files"]["blend"]
    actual = {"bytes": SOURCE_BLEND.stat().st_size, "sha256": sha256(SOURCE_BLEND)}
    if actual != expected:
        raise RuntimeError(f"Phase 1L.5cb Blend custody drift: {actual}")
    semantic = receipt["semantic"]
    if semantic["accepted_mesh_sha256"][BODY] != BODY_SHA:
        raise RuntimeError("accepted body identity drift")
    if semantic["accepted_mesh_sha256"][TOP] != SOURCE_TOP_SHA:
        raise RuntimeError("accepted connected-top identity drift")
    if semantic["derived_mesh_sha256"][BOTTOM] != BOTTOM_SHA:
        raise RuntimeError("accepted shorts identity drift")
    if semantic["action"]["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("accepted walk identity drift")
    return {"blend": actual, "identity_sha256": semantic["identity_sha256"]}


def boundary_loops(mesh):
    remaining = {edge for edge in mesh.edges if len(edge.link_faces) == 1}
    loops = []
    while remaining:
        stack = [remaining.pop()]
        edges = []
        while stack:
            edge = stack.pop()
            edges.append(edge)
            linked = {candidate for vertex in edge.verts for candidate in vertex.link_edges if candidate in remaining}
            remaining -= linked
            stack.extend(linked)
        loops.append({vertex for edge in edges for vertex in edge.verts})
    return loops


def make_source_top(armature):
    bpy.data.objects.remove(bpy.data.objects[TOP], do_unlink=True)
    xs = [-0.40, -0.32, -0.24, -0.16, -0.08, 0.0, 0.08, 0.16, 0.24, 0.32, 0.40]
    zs = [1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 1.56]
    cells = set()
    for ix in range(len(xs) - 1):
        for iz in range(len(zs) - 1):
            x, z = (xs[ix] + xs[ix + 1]) / 2, (zs[iz] + zs[iz + 1]) / 2
            torso = abs(x) <= 0.24 and z < 1.50
            sleeves = abs(x) <= 0.40 and 1.20 <= z < 1.50
            shoulders = 0.08 <= abs(x) <= 0.32 and z >= 1.50
            if torso or sleeves or shoulders:
                cells.add((ix, iz))

    vertices, faces, indices = [], [], {}

    def vertex(panel, ix, iz):
        key = panel, ix, iz
        if key not in indices:
            x, z = xs[ix], zs[iz]
            chest = math.sin(math.pi * max(0.0, min(1.0, (z - 1.00) / 0.56)))
            depth = 0.23 - 0.025 * (abs(x) / 0.40) + 0.060 * chest
            y = 0.02 + (depth if panel else -depth)
            indices[key] = len(vertices)
            vertices.append((x, y, z))
        return indices[key]

    edge_uses = {}
    for ix, iz in sorted(cells):
        corners = ((ix, iz), (ix + 1, iz), (ix + 1, iz + 1), (ix, iz + 1))
        faces.append(tuple(vertex(0, *corner) for corner in reversed(corners)))
        faces.append(tuple(vertex(1, *corner) for corner in corners))
        for a, b in zip(corners, corners[1:] + corners[:1]):
            edge = tuple(sorted((a, b)))
            edge_uses[edge] = edge_uses.get(edge, 0) + 1

    for (a, b), uses in sorted(edge_uses.items()):
        if uses != 1:
            continue
        (ax, az), (bx, bz) = (xs[a[0]], zs[a[1]]), (xs[b[0]], zs[b[1]])
        waist = az == bz == 1.00
        sleeve = az == bz == 1.20 and min(abs(ax), abs(bx)) >= 0.24
        neckline = max(abs(ax), abs(bx)) <= 0.081 and min(az, bz) >= 1.40
        if not (waist or sleeve or neckline):
            faces.append((vertex(0, *a), vertex(0, *b), vertex(1, *b), vertex(1, *a)))

    data = bpy.data.meshes.new("MESH__tailored_starter_top_pattern")
    data.from_pydata(vertices, [], faces)
    for vertex in data.vertices:
        vertex.co.x *= 1.50
        lower = 1 - base["smoothstep"]((vertex.co.z - 1.00) / 0.24)
        vertex.co.y = 0.02 + (vertex.co.y - 0.02) * (1 + 0.20 * lower)
    data.update()
    top = bpy.data.objects.new(TOP, data)
    bpy.context.collection.objects.link(top)
    bpy.context.view_layer.objects.active = top
    top.select_set(True)
    smooth = top.modifiers.new("SUBSURF__tailored_top", "SUBSURF")
    smooth.subdivision_type = "CATMULL_CLARK"
    smooth.levels = smooth.render_levels = 1
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    for vertex in top.data.vertices:
        vertex.co.x *= 1.10
        vertex.co.y = 0.02 + (vertex.co.y - 0.02) * 1.10
    top.data.update()
    forms = [{"role": "connected_front_rear_panel_t_shirt", "source_scene_top_sha256": SOURCE_TOP_SHA, "grid_columns": 10, "grid_rows": 6}]
    for polygon in top.data.polygons:
        polygon.use_smooth = True

    colors = [
        ("MAT__starter_top_front_panel", (0.90, 0.87, 0.79, 1)),
        ("MAT__starter_top_rear_panel", (0.83, 0.80, 0.73, 1)),
        ("MAT__starter_top_sleeve_panel", (0.87, 0.84, 0.77, 1)),
        ("MAT__starter_top_seam_band", (0.77, 0.74, 0.68, 1)),
    ]
    for name, color in colors:
        material = bpy.data.materials.new(name)
        material.diffuse_color = color
        top.data.materials.append(material)
    roles = {name: 0 for name in ("front_panel", "rear_panel", "left_sleeve", "right_sleeve", "neckline", "side_seam", "hem")}
    for polygon in top.data.polygons:
        center = polygon.center
        role = "rear_panel" if center.y >= 0.02 else "front_panel"
        roles[role] += 1
        polygon.material_index = 1 if role == "rear_panel" else 0
        if center.x > 0.25:
            roles["left_sleeve"] += 1
            polygon.material_index = 2
        elif center.x < -0.25:
            roles["right_sleeve"] += 1
            polygon.material_index = 2
        if center.z > 1.42 and abs(center.x) < 0.22:
            roles["neckline"] += 1
            polygon.material_index = 3
        elif center.z < 1.07:
            roles["hem"] += 1
            polygon.material_index = 3
        elif 0.21 < abs(center.x) < 0.34 and center.z < 1.30:
            roles["side_seam"] += 1
            polygon.material_index = 3

    groups = {name: top.vertex_groups.new(name=name) for name in ("spine", "upper_arm.L", "upper_arm.R")}
    counts = {name: 0 for name in groups}
    for vertex in top.data.vertices:
        side = base["smoothstep"]((abs(vertex.co.x) - 0.14) / 0.10)
        weights = {"spine": 1 - side}
        weights["upper_arm.L" if vertex.co.x >= 0 else "upper_arm.R"] = side
        for name, weight in weights.items():
            if weight > 1e-8:
                groups[name].add([vertex.index], weight, "REPLACE")
                counts[name] += 1
    modifier = top.modifiers.new("ARMATURE__tailored_starter_top_pattern", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    top["item_id"], top["technical_tailoring_proof_only"] = TOP, True
    return top, counts, forms, roles


def opening_proof(obj):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    loops = []
    for vertices in boundary_loops(mesh):
        points = [vertex.co for vertex in vertices]
        loops.append({
            "vertex_count": len(vertices),
            "min": [round(min(point[i] for point in points), 6) for i in range(3)],
            "max": [round(max(point[i] for point in points), 6) for i in range(3)],
        })
    mesh.free()
    if len(loops) != 4:
        raise RuntimeError(f"tailored starter top opening contract failed: {loops}")
    return sorted(loops, key=lambda item: (item["min"][0], item["min"][2]))


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    world = scene.world or bpy.data.worlds.new("World")
    scene.world, world.color = world, (0.07, 0.07, 0.07)
    camera_data = bpy.data.cameras.new("CAMERA__tailored_top_review")
    camera = bpy.data.objects.new("CAMERA__tailored_top_review", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera, camera_data.type, camera_data.ortho_scale = camera, "ORTHO", 2.2
    lights = []
    for name, energy, location in (
        ("LIGHT__tailored_top_key", 1000, (3, -4, 5)),
        ("LIGHT__tailored_top_fill", 700, (-3, 4, 4)),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", 4
        light = bpy.data.objects.new(name, data)
        light.location = location
        bpy.context.collection.objects.link(light)
        lights.append(light)
    views = [
        ("Front", 1, (0, -4, 0.9), (1.5708, 0, 0)),
        ("Rear", 1, (0, 4, 0.9), (1.5708, 0, 3.141593)),
        ("Profile", 1, (4, 0, 0.9), (1.5708, 0, 1.5708)),
        ("WalkExtremeFront", 6, (0, -4, 0.9), (1.5708, 0, 0)),
        ("WalkExtremeRear", 16, (0, 4, 0.9), (1.5708, 0, 3.141593)),
    ]
    for name, frame, location, rotation in views:
        scene.frame_set(frame)
        camera.location, camera.rotation_euler = location, rotation
        scene.render.filepath = str(REVIEWS / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    for obj in [camera, *lights]:
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.frame_set(1)
    return {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(REVIEWS.glob("*.png"))}


def build():
    accepted = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, bottom, armature = (bpy.data.objects[name] for name in (BODY, BOTTOM, ARMATURE))
    before = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": phase["phase"]["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if before["body"] != BODY_SHA or before["bottom"] != BOTTOM_SHA:
        raise RuntimeError("accepted body/bottom identity drift")
    top, counts, forms, roles = make_source_top(armature)
    openings = opening_proof(top)
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "tailored starter top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts"),
    }
    weights = {
        TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}),
        BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}),
    }
    if any(value <= 0 for value in roles.values()):
        raise RuntimeError(f"tailored starter-top role evidence incomplete: {roles}")
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    reviews = render_reviews()
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": phase["phase"]["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if after != before:
        raise RuntimeError("accepted body/bottom/armature/action changed")
    semantic = {
        "accepted_phase_1l5cb": accepted,
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "construction": {
            "method": "deterministic_connected_front_rear_panel_shirt_with_bridged_shoulders_side_seams_and_four_declared_openings",
            "forms": forms,
            "declared_openings": ["neckline", "waist_hem", "left_arm", "right_arm"],
            "excluded": ["extras", "cloth_physics", "textures", "production_uv"],
        },
        "topology": topology,
        "declared_opening_geometry": openings,
        "panel_roles": roles,
        "weights": {TOP: {"groups_nonempty_vertices": counts, **weights[TOP]}, BOTTOM: weights[BOTTOM]},
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {
            "body_changed": 0,
            "bottom_changed": 0,
            "skeleton_changed": 0,
            "action_changed": 0,
            "runtime_changed": 0,
            "top_connected": True,
            "final_art_claim": False,
            "readiness_claim": False,
        },
    }
    semantic["identity_sha256"] = semantic_sha(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cc provenance\n\n"
        "- Additive tailored starter-top derivative from exact Phase 1L.5cb Blend custody.\n"
        "- Accepted body, connected starter shorts, DEC-035 armature and `walk_candidate_v1` are unchanged.\n"
        "- One connected shirt pattern declares neckline, waist and two arm openings with explicit panel/seam roles.\n"
        "- Extras, cloth physics, textures and production UVs remain absent.\n"
        "- Reviews are offline tailoring/deformation proof, not runtime, final-art, performance or readiness evidence.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5cc believable starter-top tailoring walk proof",
        "status": "offline_tailored_top_walk_proof_not_runtime_or_final_art",
        "semantic": semantic,
        "files": {
            "blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
            "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "reviews": reviews,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TAILORED_STARTER_TOP_WALK_PASS frames=21 loops=4 identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["accepted_phase_1l5cb"] != source_custody():
        raise RuntimeError("accepted Phase 1L.5cb custody drift")
    for name, path in (("blend", OUTPUT), ("builder", Path(__file__)), ("provenance", PROVENANCE)):
        if manifest["files"][name] != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"{name} custody drift")
    for name, receipt in manifest["files"]["reviews"].items():
        path = REVIEWS / name
        if receipt != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"review custody drift: {name}")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    if semantic_sha(base["mesh_semantic"](body)) != BODY_SHA or semantic_sha(base["mesh_semantic"](bottom)) != BOTTOM_SHA:
        raise RuntimeError("accepted body/bottom mesh drift")
    if semantic_sha(base["mesh_semantic"](top)) != manifest["semantic"]["derived_mesh_sha256"][TOP]:
        raise RuntimeError("derived top mesh drift")
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "tailored starter top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "accepted starter shorts"),
    }
    if topology != manifest["semantic"]["topology"] or opening_proof(top) != manifest["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("saved topology/opening drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})
    hierarchy = phase["phase"]["armature_semantic"](armature)
    if hierarchy != manifest["semantic"]["armature"]["hierarchy"] or len(hierarchy) != 12:
        raise RuntimeError("saved DEC-035 hierarchy drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != manifest["semantic"]["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("saved walk action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"TAILORED_STARTER_TOP_WALK_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
