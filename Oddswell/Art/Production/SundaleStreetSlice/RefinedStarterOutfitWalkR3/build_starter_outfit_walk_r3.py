"""Build and validate the Phase 1L.5bz-R3 technical outfit walk proof."""

import bmesh
import bpy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
R1 = SLICE / "RefinedStarterOutfitWalkRepair/build_starter_outfit_walk_repair.py"
scope = {"__file__": str(R1)}
source = R1.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], scope)

BODY, TOP, BOTTOM, ARMATURE = (scope[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
OUTPUT = ROOT / "RefinedSundaleStarterOutfitWalkR3.blend"
MANIFEST = ROOT / "starter_outfit_walk_r3_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest().upper()


def make_top(armature):
    top = scope["append_object"](scope["TOP_BLEND"], TOP, armature)
    top.data = top.data.copy()
    for vertex in top.data.vertices:
        vertex.co.x *= 0.52
        vertex.co.y *= 0.75
    mesh = bmesh.new()
    mesh.from_mesh(top.data)
    bmesh.ops.delete(mesh, geom=[face for face in mesh.faces if abs(face.normal.x) > 0.9], context="FACES")
    mesh.to_mesh(top.data)
    mesh.free()
    top.data.name = "MESH__starter_offwhite_top_r3"
    top.data.update()
    top["technical_two_panel_drape"] = True
    return top


def make_bottom(armature):
    data = bpy.data.metaballs.new("META__starter_bottom_r3")
    data.resolution = data.render_resolution = 0.014
    source = bpy.data.objects.new("META__starter_bottom_r3", data)
    bpy.context.collection.objects.link(source)
    forms = [
        ((0, 0.04, 0.84), (0.30, 0.18, 0.14)),
        ((0.14, 0.18, 0.73), (0.16, 0.14, 0.17)),
        ((-0.14, -0.10, 0.73), (0.16, 0.14, 0.17)),
    ]
    for co, scale in forms:
        element = data.elements.new()
        element.co, element.radius, element.stiffness = co, 1, 2
        element.type = "ELLIPSOID"
        element.size_x, element.size_y, element.size_z = scale
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = source
    source.select_set(True)
    bpy.ops.object.convert(target="MESH")
    bottom = bpy.context.object
    bottom.name, bottom.data.name = BOTTOM, "MESH__starter_offwhite_bottom_r3"

    mesh = bmesh.new()
    mesh.from_mesh(bottom.data)
    outside = [face for face in mesh.faces if face.calc_center_median().z > 0.91 or face.calc_center_median().z < 0.69]
    bmesh.ops.delete(mesh, geom=outside, context="FACES")
    loose = [vertex for vertex in mesh.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(mesh, geom=loose, context="VERTS")
    mesh.to_mesh(bottom.data)
    mesh.free()

    for vertex in bottom.data.vertices:
        taper = scope["smoothstep"]((vertex.co.z - 0.70) / 0.16)
        vertex.co.x *= 1 - 0.25 * taper
    bottom.data.update()

    material = bpy.data.materials.new("MAT__starter_offwhite_bottom_proof")
    material.diffuse_color = (0.9, 0.87, 0.79, 1)
    bottom.data.materials.append(material)
    groups = {name: bottom.vertex_groups.new(name=name) for name in ("root", "thigh.L", "thigh.R")}
    counts = {name: 0 for name in groups}
    for vertex in bottom.data.vertices:
        root = scope["smoothstep"]((vertex.co.z - 0.69) / (0.91 - 0.69))
        if abs(vertex.co.x) > 0.15:
            root = max(root, scope["smoothstep"]((vertex.co.z - 0.72) / 0.08))
        left = scope["smoothstep"]((vertex.co.x + 0.05) / 0.10)
        leg = 1 - root
        weights = {"root": root, "thigh.L": leg * left, "thigh.R": leg * (1 - left)}
        for name, weight in weights.items():
            if weight > 1e-8:
                groups[name].add([vertex.index], weight, "REPLACE")
                counts[name] += 1
    modifier = bottom.modifiers.new("ARMATURE__starter_bottom_r3", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    bottom["item_id"], bottom["technical_proof_only"] = BOTTOM, True
    return bottom, counts, forms


def topology_proof(obj, expected, label):
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    remaining = set(mesh.verts)
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            vertex = stack.pop()
            linked = {edge.other_vert(vertex) for edge in vertex.link_edges} & remaining
            remaining -= linked
            stack.extend(linked)
    boundary = {edge for edge in mesh.edges if len(edge.link_faces) == 1}
    loops = 0
    while boundary:
        loops += 1
        stack = [boundary.pop()]
        while stack:
            edge = stack.pop()
            linked = {candidate for vertex in edge.verts for candidate in vertex.link_edges if candidate in boundary}
            boundary -= linked
            stack.extend(linked)
    proof = {
        "connected_components": components,
        "boundary_loops": loops,
        "non_manifold_edges_excluding_openings": sum(len(edge.link_faces) not in (1, 2) for edge in mesh.edges),
        "vertices": len(mesh.verts),
        "polygons": len(mesh.faces),
        "material_slots": [slot.material.name for slot in obj.material_slots],
    }
    mesh.free()
    if (proof["connected_components"], proof["boundary_loops"], proof["non_manifold_edges_excluding_openings"]) != expected:
        raise RuntimeError(f"{label} topology contract failed: {proof}")
    return proof


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    world = scene.world or bpy.data.worlds.new("World")
    scene.world, world.color = world, (0.07, 0.07, 0.07)
    camera_data = bpy.data.cameras.new("CAMERA__r3_review")
    camera = bpy.data.objects.new("CAMERA__r3_review", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera, camera_data.type, camera_data.ortho_scale = camera, "ORTHO", 2.2
    light_data = bpy.data.lights.new("LIGHT__r3_review", "AREA")
    light_data.energy, light_data.shape, light_data.size = 1000, "DISK", 4
    light = bpy.data.objects.new("LIGHT__r3_review", light_data)
    light.location = (3, -4, 5)
    bpy.context.collection.objects.link(light)
    views = [
        ("Front", (0, -4, 0.9), (1.5708, 0, 0)),
        ("Rear", (0, 4, 0.9), (1.5708, 0, 3.141593)),
        ("Profile", (4, 0, 0.9), (1.5708, 0, 1.5708)),
    ]
    for name, location, rotation in views:
        camera.location, camera.rotation_euler = location, rotation
        scene.render.filepath = str(REVIEWS / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    for obj in (camera, light):
        bpy.data.objects.remove(obj, do_unlink=True)
    return {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(REVIEWS.glob("*.png"))}


def build():
    accepted = scope["custody"]()
    bpy.ops.wm.open_mainfile(filepath=str(scope["BODY_BLEND"]), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, armature = bpy.data.objects[BODY], bpy.data.objects[ARMATURE]
    top = make_top(armature)
    bottom, counts, forms = make_bottom(armature)
    for obj in list(bpy.data.objects):
        if obj not in {body, armature, top, bottom}:
            bpy.data.objects.remove(obj, do_unlink=True)
    action = scope["append_action"](armature)
    scene = bpy.context.scene
    scene.render.fps, scene.frame_start, scene.frame_end = 28, 1, 21
    weights = {TOP: scope["weight_check"](top, {"spine"}), BOTTOM: scope["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    topology = {
        TOP: topology_proof(top, (2, 2, 0), "technical top panels"),
        BOTTOM: topology_proof(bottom, (1, 3, 0), "starter bottom"),
    }
    deformation = scope["frame_proof"](scene, body, top, bottom, armature)
    scene.frame_set(1)
    reviews = render_reviews()
    semantic = {
        "accepted_inputs": accepted,
        "accepted_source_mesh_sha256": {BODY: scope["BODY_MESH_SHA"], TOP: scope["TOP_MESH_SHA"], BOTTOM: scope["BOTTOM_MESH_SHA"]},
        "derived_mesh_sha256": {TOP: semantic_sha(scope["mesh_semantic"](top)), BOTTOM: semantic_sha(scope["mesh_semantic"](bottom))},
        "construction": {
            "top": {"method": "accepted_proxy_copy_narrowed_to_two_front_rear_technical_drape_panels", "x_scale": 0.52, "y_scale": 0.75, "removed_faces": "absolute_x_normal_above_0.9"},
            "bottom": {"method": "native_compact_fused_three-opening_shell_with_upper_taper_and_local_outer_root_lock", "metaball_resolution_m": 0.014, "forms_xyz_m": forms, "face_center_z_cuts_m": [0.69, 0.91], "upper_x_taper": {"start_z_m": 0.70, "range_m": 0.16, "maximum_fraction": 0.25}, "outer_root_lock": {"absolute_x_threshold_m": 0.15, "start_z_m": 0.72, "range_m": 0.08}},
        },
        "topology": topology,
        "weights": {TOP: weights[TOP], BOTTOM: {"groups_nonempty_vertices": counts, **weights[BOTTOM]}},
        "action": scope["action_semantic"](action),
        "deformation": deformation,
        "boundaries": {"body_changed": 0, "accepted_source_top_changed": 0, "accepted_source_bottom_changed": 0, "skeleton_changed": 0, "action_changed": 0, "runtime_changed": 0, "top_two_panel_limitation": True, "final_art_claim": False, "readiness_claim": False},
    }
    semantic["identity_sha256"] = semantic_sha(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text(
        "# Phase 1L.5bz-R3 provenance\n\n"
        "- Additive outfit derivative using the accepted body, source garments, skeleton, DEC-035 mapping and unchanged `walk_candidate_v1`.\n"
        "- The top is a narrowed two-panel technical drape. It is deformation evidence only, not a connected or finished shirt.\n"
        "- One connected native fused shell retains exactly three boundary loops: waist plus two leg openings.\n"
        "- Compact upper/leg forms, upper taper and a bounded outer root lock preserve clearance; the leg openings retain blended thigh response.\n"
        "- All 21 integer frames use evaluated-mesh BVH intersection checks and bidirectional vertex-to-surface clearance sampling.\n"
        "- Review images are offline proof views, not runtime, final-art, performance, or readiness evidence.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5bz-R3 corrected technical starter-outfit walk proof",
        "status": "offline_starter_outfit_walk_proof_not_runtime_or_final_art",
        "semantic": semantic,
        "files": {
            "blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
            "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "reviews": reviews,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STARTER_OUTFIT_WALK_R3_PASS frames=21 loops=3 identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["accepted_inputs"] != scope["custody"]():
        raise RuntimeError("accepted-input custody drift")
    for name, path in (("blend", OUTPUT), ("builder", Path(__file__)), ("provenance", PROVENANCE)):
        if manifest["files"][name] != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"{name} custody drift")
    for name, receipt in manifest["files"]["reviews"].items():
        path = REVIEWS / name
        if receipt != {"bytes": path.stat().st_size, "sha256": sha256(path)}:
            raise RuntimeError(f"review custody drift: {name}")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[name] for name in (BODY, TOP, BOTTOM, ARMATURE))
    if scope["canonical"](scope["mesh_semantic"](body)) != scope["BODY_MESH_SHA"]:
        raise RuntimeError("accepted body mesh drift")
    derived_meshes = {TOP: semantic_sha(scope["mesh_semantic"](top)), BOTTOM: semantic_sha(scope["mesh_semantic"](bottom))}
    if derived_meshes != manifest["semantic"]["derived_mesh_sha256"]:
        raise RuntimeError("derived outfit mesh drift")
    topology = {TOP: topology_proof(top, (2, 2, 0), "technical top panels"), BOTTOM: topology_proof(bottom, (1, 3, 0), "starter bottom")}
    if topology != manifest["semantic"]["topology"]:
        raise RuntimeError("saved topology drift")
    weight_keys = ("vertices", "unweighted", "invalid_or_non_normalized")
    saved_weights = {TOP: scope["weight_check"](top, {"spine"}), BOTTOM: scope["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})}
    expected_weights = {name: {key: manifest["semantic"]["weights"][name][key] for key in weight_keys} for name in (TOP, BOTTOM)}
    if saved_weights != expected_weights:
        raise RuntimeError("saved weight drift")
    action = bpy.data.actions[scope["ACTION"]]
    if scope["action_semantic"](action) != manifest["semantic"]["action"]:
        raise RuntimeError("walk action drift")
    if scope["frame_proof"](bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"STARTER_OUTFIT_WALK_R3_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
