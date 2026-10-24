"""Build and validate the Phase 1L.5cb starter-shorts panel walk proof."""

import bmesh
import bpy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
TOP_BUILDER = SLICE / "ConnectedStarterTopWalkProof/build_connected_starter_top_walk.py"
phase = {"__file__": str(TOP_BUILDER)}
source = TOP_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], phase)
r3, base = phase["scope"], phase["base"]

BODY, TOP, BOTTOM, ARMATURE = (phase[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
SOURCE_BLEND = SLICE / "ConnectedStarterTopWalkProof/RefinedSundaleConnectedStarterTopWalk.blend"
SOURCE_MANIFEST = SLICE / "ConnectedStarterTopWalkProof/connected_starter_top_walk_custody.json"
OUTPUT = ROOT / "RefinedSundaleStarterShortsPanelWalk.blend"
MANIFEST = ROOT / "starter_shorts_panel_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
TOP_SHA = "095929FDAE403198912D8BEC21EE0A28EB579AEB5BC2BB9BD2CC25C0A72ED54A"
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
        raise RuntimeError(f"Phase 1L.5ca Blend custody drift: {actual}")
    semantic = receipt["semantic"]
    if semantic["accepted_mesh_sha256"][BODY] != BODY_SHA:
        raise RuntimeError("accepted body identity drift")
    if semantic["derived_mesh_sha256"][TOP] != TOP_SHA:
        raise RuntimeError("accepted connected-top identity drift")
    if semantic["action"]["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("accepted walk identity drift")
    return {"blend": actual, "identity_sha256": semantic["identity_sha256"]}


def make_bottom(armature):
    bpy.data.objects.remove(bpy.data.objects[BOTTOM], do_unlink=True)
    data = bpy.data.metaballs.new("META__starter_shorts_panel_pattern")
    data.resolution = data.render_resolution = 0.010
    source = bpy.data.objects.new("META__starter_shorts_panel_pattern", data)
    bpy.context.collection.objects.link(source)
    forms = [
        {"role": "balanced_rise", "center_m": [0.00, 0.04, 0.84], "scale_m": [0.31, 0.27, 0.15]},
        {"role": "left_leg_panel", "center_m": [0.14, 0.16, 0.72], "scale_m": [0.17, 0.19, 0.20]},
        {"role": "right_leg_panel", "center_m": [-0.14, -0.08, 0.72], "scale_m": [0.17, 0.19, 0.20]},
        {"role": "crotch_gusset", "center_m": [0.00, 0.04, 0.75], "scale_m": [0.16, 0.18, 0.11]},
    ]
    for form in forms:
        element = data.elements.new()
        element.co, element.radius, element.stiffness = form["center_m"], 1, 2
        element.type = "ELLIPSOID"
        element.size_x, element.size_y, element.size_z = form["scale_m"]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = source
    source.select_set(True)
    bpy.ops.object.convert(target="MESH")
    bottom = bpy.context.object
    bottom.name, bottom.data.name = BOTTOM, "MESH__starter_shorts_panel_pattern"

    mesh = bmesh.new()
    mesh.from_mesh(bottom.data)
    removed = [face for face in mesh.faces if face.calc_center_median().z > 0.91 or face.calc_center_median().z < 0.66]
    bmesh.ops.delete(mesh, geom=removed, context="FACES")
    loose = [vertex for vertex in mesh.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(mesh, geom=loose, context="VERTS")
    boundary = {edge for edge in mesh.edges if len(edge.link_faces) == 1}
    while boundary:
        stack = [boundary.pop()]
        edges = []
        while stack:
            edge = stack.pop()
            edges.append(edge)
            linked = {candidate for vertex in edge.verts for candidate in vertex.link_edges if candidate in boundary}
            boundary -= linked
            stack.extend(linked)
        vertices = {vertex for edge in edges for vertex in edge.verts}
        target_z = 0.91 if sum(vertex.co.z for vertex in vertices) / len(vertices) > 0.80 else 0.66
        for vertex in vertices:
            vertex.co.z = target_z
    mesh.to_mesh(bottom.data)
    mesh.free()

    for vertex in bottom.data.vertices:
        if vertex.co.z >= 0.77:
            rise = min(1.0, (vertex.co.z - 0.77) / 0.14)
            half_x, half_y = 0.195 - 0.015 * rise, 0.215 - 0.035 * rise
            dy = vertex.co.y - 0.04
            radial = ((vertex.co.x / half_x) ** 2 + (dy / half_y) ** 2) ** 0.5
            vertex.co.x /= radial
            vertex.co.y = 0.04 + dy / radial
        else:
            center = (0.14, 0.16) if vertex.co.x >= 0 else (-0.14, -0.08)
            dx, dy = vertex.co.x - center[0], vertex.co.y - center[1]
            radial = ((dx / 0.075) ** 2 + (dy / 0.105) ** 2) ** 0.5
            vertex.co.x = center[0] + dx / radial
            vertex.co.y = center[1] + dy / radial
        if vertex.co.z < 0.70:
            center = (0.14, 0.16) if vertex.co.x >= 0 else (-0.14, -0.08)
            vertex.co.x = center[0] + (vertex.co.x - center[0]) * 1.035
            vertex.co.y = center[1] + (vertex.co.y - center[1]) * 1.035
    bottom.data.update()

    colors = [
        ("MAT__starter_shorts_front_panel", (0.90, 0.87, 0.79, 1)),
        ("MAT__starter_shorts_rear_panel", (0.82, 0.79, 0.72, 1)),
        ("MAT__starter_shorts_seam_band", (0.80, 0.77, 0.70, 1)),
    ]
    for name, color in colors:
        material = bpy.data.materials.new(name)
        material.diffuse_color = color
        bottom.data.materials.append(material)
    roles = {"front_panel": 0, "rear_panel": 0, "waistband": 0, "hem": 0, "inseam": 0, "outseam": 0}
    for polygon in bottom.data.polygons:
        center = polygon.center
        role = "rear_panel" if center.y >= 0.04 else "front_panel"
        polygon.material_index = 1 if role == "rear_panel" else 0
        roles[role] += 1
        if center.z > 0.89:
            roles["waistband"] += 1
            polygon.material_index = 2
        elif center.z < 0.68:
            roles["hem"] += 1
            polygon.material_index = 2
        elif abs(center.x) < 0.075 and center.z < 0.79:
            roles["inseam"] += 1
            polygon.material_index = 2
        elif abs(center.x) > 0.215:
            roles["outseam"] += 1
            polygon.material_index = 2

    groups = {name: bottom.vertex_groups.new(name=name) for name in ("root", "thigh.L", "thigh.R")}
    counts = {name: 0 for name in groups}
    for vertex in bottom.data.vertices:
        root = base["smoothstep"]((vertex.co.z - 0.64) / 0.25)
        if abs(vertex.co.x) > 0.16:
            root = max(root, base["smoothstep"]((vertex.co.z - 0.73) / 0.09))
        left = base["smoothstep"]((vertex.co.x + 0.05) / 0.10)
        leg = 1 - root
        weights = {"root": root, "thigh.L": leg * left, "thigh.R": leg * (1 - left)}
        for name, weight in weights.items():
            if weight > 1e-8:
                groups[name].add([vertex.index], weight, "REPLACE")
                counts[name] += 1
    modifier = bottom.modifiers.new("ARMATURE__starter_shorts_panel_pattern", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    bottom["item_id"], bottom["technical_panel_proof_only"] = BOTTOM, True
    return bottom, counts, forms, roles


def opening_proof(obj):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    boundary = {edge for edge in mesh.edges if len(edge.link_faces) == 1}
    loops = []
    while boundary:
        stack = [boundary.pop()]
        edges = []
        while stack:
            edge = stack.pop()
            edges.append(edge)
            linked = {candidate for vertex in edge.verts for candidate in vertex.link_edges if candidate in boundary}
            boundary -= linked
            stack.extend(linked)
        points = [vertex.co for edge in edges for vertex in edge.verts]
        loops.append({
            "edge_count": len(edges),
            "min": [round(min(point[i] for point in points), 6) for i in range(3)],
            "max": [round(max(point[i] for point in points), 6) for i in range(3)],
        })
    mesh.free()
    if len(loops) != 3:
        raise RuntimeError(f"starter shorts opening contract failed: {loops}")
    return sorted(loops, key=lambda item: (item["min"][2], item["min"][0]))


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    world = scene.world or bpy.data.worlds.new("World")
    scene.world, world.color = world, (0.07, 0.07, 0.07)
    camera_data = bpy.data.cameras.new("CAMERA__starter_shorts_panel_review")
    camera = bpy.data.objects.new("CAMERA__starter_shorts_panel_review", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera, camera_data.type, camera_data.ortho_scale = camera, "ORTHO", 2.2
    light_data = bpy.data.lights.new("LIGHT__starter_shorts_panel_review", "AREA")
    light_data.energy, light_data.shape, light_data.size = 1000, "DISK", 4
    light = bpy.data.objects.new("LIGHT__starter_shorts_panel_review", light_data)
    light.location = (3, -4, 5)
    bpy.context.collection.objects.link(light)
    fill_data = bpy.data.lights.new("LIGHT__starter_shorts_panel_fill", "AREA")
    fill_data.energy, fill_data.shape, fill_data.size = 700, "DISK", 4
    fill = bpy.data.objects.new("LIGHT__starter_shorts_panel_fill", fill_data)
    fill.location = (-3, 4, 4)
    bpy.context.collection.objects.link(fill)
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
    for obj in (camera, light, fill):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.frame_set(1)
    return {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(REVIEWS.glob("*.png"))}


def build():
    accepted = source_custody()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, top, armature = (bpy.data.objects[name] for name in (BODY, TOP, ARMATURE))
    before = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "top": semantic_sha(base["mesh_semantic"](top)),
        "armature": phase["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if before["body"] != BODY_SHA or before["top"] != TOP_SHA:
        raise RuntimeError("accepted body/top identity drift")
    bottom, counts, forms, roles = make_bottom(armature)
    openings = opening_proof(bottom)
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "accepted connected top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "starter shorts panel pattern"),
    }
    weights = {
        TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}),
        BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}),
    }
    if any(value <= 0 for value in roles.values()):
        raise RuntimeError(f"starter shorts panel-role evidence incomplete: {roles}")
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    reviews = render_reviews()
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "top": semantic_sha(base["mesh_semantic"](top)),
        "armature": phase["armature_semantic"](armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if after != before:
        raise RuntimeError("accepted body/top/armature/action changed")
    semantic = {
        "accepted_phase_1l5ca": accepted,
        "accepted_mesh_sha256": {BODY: BODY_SHA, TOP: TOP_SHA},
        "derived_mesh_sha256": {BOTTOM: semantic_sha(base["mesh_semantic"](bottom))},
        "construction": {
            "method": "native_connected_four_form_shorts_pattern_with_balanced_rise_crotch_gusset_and_material_panel_seams",
            "forms": forms,
            "metaball_resolution_m": 0.010,
            "declared_openings": ["waist", "left_leg", "right_leg"],
            "excluded": ["pockets", "fly", "logos", "extras", "cloth_physics"],
        },
        "topology": topology,
        "declared_opening_geometry": openings,
        "panel_roles": roles,
        "weights": {TOP: weights[TOP], BOTTOM: {"groups_nonempty_vertices": counts, **weights[BOTTOM]}},
        "armature": {"bone_count": 12, "hierarchy": after["armature"]},
        "action": after["action"],
        "deformation": deformation,
        "boundaries": {
            "body_changed": 0,
            "top_changed": 0,
            "skeleton_changed": 0,
            "action_changed": 0,
            "runtime_changed": 0,
            "bottom_connected": True,
            "final_art_claim": False,
            "readiness_claim": False,
        },
    }
    semantic["identity_sha256"] = semantic_sha(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5cb provenance\n\n"
        "- Additive starter-shorts derivative from the exact Phase 1L.5ca Blend and custody receipt.\n"
        "- The accepted body, connected starter top, DEC-035 12-bone armature and `walk_candidate_v1` are unchanged.\n"
        "- One connected shorts pattern declares exactly three openings and includes front/rear panels, balanced rise/crotch/gusset, waistband, hems, inseam and outseam evidence.\n"
        "- Pockets, fly, logos, extras and cloth physics remain absent.\n"
        "- All 21 integer frames use evaluated-mesh BVH intersection checks and bidirectional vertex-to-surface clearance sampling.\n"
        "- Reviews are offline pattern/deformation proof, not runtime, final-art, performance or beta-readiness evidence.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5cb believable starter-shorts panel construction walk proof",
        "status": "offline_shorts_panel_walk_proof_not_runtime_or_final_art",
        "semantic": semantic,
        "files": {
            "blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
            "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "reviews": reviews,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STARTER_SHORTS_PANEL_WALK_PASS frames=21 loops=3 identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["accepted_phase_1l5ca"] != source_custody():
        raise RuntimeError("accepted Phase 1L.5ca custody drift")
    for name, path in (("blend", OUTPUT), ("builder", Path(__file__)), ("provenance", PROVENANCE)):
        if manifest["files"][name] != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"{name} custody drift")
    for name, receipt in manifest["files"]["reviews"].items():
        path = REVIEWS / name
        if receipt != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"review custody drift: {name}")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    if semantic_sha(base["mesh_semantic"](body)) != BODY_SHA or semantic_sha(base["mesh_semantic"](top)) != TOP_SHA:
        raise RuntimeError("accepted body/top mesh drift")
    if semantic_sha(base["mesh_semantic"](bottom)) != manifest["semantic"]["derived_mesh_sha256"][BOTTOM]:
        raise RuntimeError("derived shorts mesh drift")
    topology = {
        TOP: r3["topology_proof"](top, (1, 4, 0), "accepted connected top"),
        BOTTOM: r3["topology_proof"](bottom, (1, 3, 0), "starter shorts panel pattern"),
    }
    if topology != manifest["semantic"]["topology"] or opening_proof(bottom) != manifest["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("saved topology/opening drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})
    hierarchy = phase["armature_semantic"](armature)
    if hierarchy != manifest["semantic"]["armature"]["hierarchy"] or len(hierarchy) != 12:
        raise RuntimeError("saved DEC-035 hierarchy drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != manifest["semantic"]["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("saved walk action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"STARTER_SHORTS_PANEL_WALK_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
