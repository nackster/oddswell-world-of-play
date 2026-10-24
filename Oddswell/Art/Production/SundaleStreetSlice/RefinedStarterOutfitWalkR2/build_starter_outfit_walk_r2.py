"""Build/validate the Phase 1L.5bz-R2 bottom redesign walk proof."""

import hashlib, json, os, sys
from pathlib import Path

import bmesh, bpy

ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
R1 = SLICE / "RefinedStarterOutfitWalkRepair/build_starter_outfit_walk_repair.py"
scope = {"__file__": str(R1)}
source = R1.read_text(encoding="utf-8")
exec(source[:source.rfind('if "--validate"')], scope)

BODY, TOP, BOTTOM, ARMATURE = (scope[n] for n in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
OUTPUT = ROOT / "RefinedSundaleStarterOutfitWalkR2.blend"
MANIFEST = ROOT / "starter_outfit_walk_r2_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
FAILURE = ROOT / "starter_outfit_walk_r2_failure.json"


class R2Failure(RuntimeError):
    def __init__(self, payload):
        self.payload = payload
        super().__init__(payload["reason"])


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def make_bottom(armature):
    data = bpy.data.metaballs.new("META__starter_bottom_r2")
    data.resolution = data.render_resolution = 0.018
    source = bpy.data.objects.new("META__starter_bottom_r2", data)
    bpy.context.collection.objects.link(source)
    for co, scale in [((0, .04, .79), (.48, .40, .25)), ((.22, .04, .60), (.30, .36, .25)), ((-.22, .04, .60), (.30, .36, .25))]:
        element = data.elements.new()
        element.co, element.radius, element.stiffness, element.type = co, 1, 2, "ELLIPSOID"
        element.size_x, element.size_y, element.size_z = scale
    bpy.context.view_layer.objects.active = source
    source.select_set(True)
    bpy.ops.object.convert(target="MESH")
    bottom = bpy.context.object
    bottom.name, bottom.data.name = BOTTOM, "MESH__starter_offwhite_bottom_r2"
    topology = bmesh.new()
    topology.from_mesh(bottom.data)
    bmesh.ops.delete(topology, geom=[face for face in topology.faces if face.calc_center_median().z > .86 or face.calc_center_median().z < .62], context="FACES")
    boundary = [edge for edge in topology.edges if len(edge.link_faces) == 1]
    front = max(boundary, key=lambda edge: (edge.verts[0].co.y + edge.verts[1].co.y) / 2)
    rear = min(boundary, key=lambda edge: (edge.verts[0].co.y + edge.verts[1].co.y) / 2)
    front_pair, rear_pair = [sorted(edge.verts, key=lambda vertex: vertex.co.x) for edge in (front, rear)]
    chains = [[rear_pair[side]] for side in range(2)]
    for step in range(1, 8):
        factor = step / 8
        for side in range(2):
            co = rear_pair[side].co.lerp(front_pair[side].co, factor)
            co.x = -.04 if side == 0 else .04
            co.z = .58 + .04 * (abs(2 * factor - 1) ** 2)
            chains[side].append(topology.verts.new(co))
    for side in range(2):
        chains[side].append(front_pair[side])
    topology.verts.index_update()
    for step in range(8):
        topology.faces.new((chains[0][step], chains[1][step], chains[1][step + 1], chains[0][step + 1]))
    topology.to_mesh(bottom.data)
    topology.free()
    material = bpy.data.materials.new("MAT__starter_offwhite_bottom_proof")
    material.diffuse_color = (.9, .87, .79, 1)
    bottom.data.materials.append(material)
    groups = {name: bottom.vertex_groups.new(name=name) for name in ("root", "thigh.L", "thigh.R")}
    counts = {name: 0 for name in groups}
    for vertex in bottom.data.vertices:
        left = scope["smoothstep"]((vertex.co.x + .05) / .10)
        weights = {"root": .99, "thigh.L": .01 * left, "thigh.R": .01 * (1 - left)}
        for name, weight in weights.items():
            if weight > 1e-8:
                groups[name].add([vertex.index], weight, "REPLACE")
                counts[name] += 1
    modifier = bottom.modifiers.new("ARMATURE__starter_bottom_r2", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    bottom["item_id"], bottom["technical_proof_only"] = BOTTOM, True
    return bottom, counts


def topology_proof(bottom):
    mesh = bmesh.new()
    mesh.from_mesh(bottom.data)
    islands = 0
    remaining = set(mesh.verts)
    while remaining:
        islands += 1
        stack = [remaining.pop()]
        while stack:
            for edge in stack.pop().link_edges:
                other = edge.other_vert(edge.verts[0]) if edge.verts[0] not in remaining else edge.verts[0]
                if other in remaining:
                    remaining.remove(other)
                    stack.append(other)
    boundary = [edge for edge in mesh.edges if len(edge.link_faces) == 1]
    loops = []
    unused = set(boundary)
    while unused:
        loops.append(1)
        stack = [unused.pop()]
        while stack:
            edge = stack.pop()
            linked = {other for vertex in edge.verts for other in vertex.link_edges if other in unused and len(other.link_faces) == 1}
            unused -= linked
            stack.extend(linked)
    non_manifold = sum(1 for edge in mesh.edges if len(edge.link_faces) not in (1, 2))
    proof = {"connected_components": islands, "boundary_loops": len(loops), "non_manifold_edges_excluding_openings": non_manifold, "vertices": len(mesh.verts), "polygons": len(mesh.faces), "material_slots": [slot.material.name for slot in bottom.material_slots]}
    mesh.free()
    if proof["connected_components"] != 1 or proof["boundary_loops"] != 3 or non_manifold:
        raise R2Failure({"reason": "bounded_profile_trial_did_not_retain_two_leg_openings", "stage": "neutral_topology", "topology": proof})
    return proof


def render_reviews(body, top, bottom):
    REVIEWS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 800, 800, 100
    world = scene.world or bpy.data.worlds.new("World")
    scene.world, world.color = world, (.07, .07, .07)
    camera_data = bpy.data.cameras.new("CAMERA__r2_review")
    camera = bpy.data.objects.new("CAMERA__r2_review", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera, camera_data.type, camera_data.ortho_scale = camera, "ORTHO", 2.2
    light_data = bpy.data.lights.new("LIGHT__r2_review", "AREA")
    light_data.energy, light_data.shape, light_data.size = 1000, "DISK", 4
    light = bpy.data.objects.new("LIGHT__r2_review", light_data)
    light.location = (3, -4, 5)
    bpy.context.collection.objects.link(light)
    for name, location, rotation in [("Front", (0, -4, .9), (1.5708, 0, 0)), ("Rear", (0, 4, .9), (1.5708, 0, 3.141593)), ("Profile", (4, 0, .9), (1.5708, 0, 1.5708))]:
        camera.location, camera.rotation_euler = location, rotation
        scene.render.filepath = str(REVIEWS / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    return {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(REVIEWS.glob("*.png"))}


def build():
    accepted = scope["custody"]()
    bpy.ops.wm.open_mainfile(filepath=str(scope["BODY_BLEND"]), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, armature = bpy.data.objects[BODY], bpy.data.objects[ARMATURE]
    top = scope["append_object"](scope["TOP_BLEND"], TOP, armature)
    bottom, counts = make_bottom(armature)
    for obj in list(bpy.data.objects):
        if obj not in {body, armature, top, bottom}:
            bpy.data.objects.remove(obj, do_unlink=True)
    action = scope["append_action"](armature)
    scene = bpy.context.scene
    scene.render.fps, scene.frame_start, scene.frame_end = 28, 1, 21
    weights = scope["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})
    topology = topology_proof(bottom)
    deformation = scope["frame_proof"](scene, body, top, bottom, armature)
    scene.frame_set(1)
    reviews = render_reviews(body, top, bottom)
    for obj in list(bpy.data.objects):
        if obj.name.startswith(("CAMERA__", "LIGHT__")):
            bpy.data.objects.remove(obj, do_unlink=True)
    mesh = scope["mesh_semantic"](bottom)
    semantic = {"accepted_inputs": accepted, "accepted_source_bottom_mesh_sha256": scope["BOTTOM_MESH_SHA"], "derived_bottom_mesh_sha256": semantic_sha(mesh), "item_id": BOTTOM, "material_slot": "MAT__starter_offwhite_bottom_proof", "construction": {"method": "native_fused_upper_front_rear_saddle_with_two_leg_openings", "metaball_resolution_m": .018, "root_weight": .99, "total_thigh_weight": .01}, "topology": topology, "weights": {"groups_nonempty_vertices": counts, **weights}, "action": scope["action_semantic"](action), "deformation": deformation, "boundaries": {"body_changed": 0, "top_changed": 0, "skeleton_changed": 0, "action_changed": 0, "runtime_changed": 0, "phase_credit": 0, "final_art_claim": False, "readiness_claim": False}}
    semantic["identity_sha256"] = semantic_sha(semantic)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), check_existing=False)
    PROVENANCE.write_text("# Phase 1L.5bz-R2 provenance\n\n- Additive bottom-only derivative from the accepted 1L.5bx identity and material contract.\n- Native fused low-poly upper front/rear/saddle with two leg openings; later offline seat/gusset studies are not imported.\n- Exact accepted body, top, skeleton, DEC-035 mapping and unchanged `walk_candidate_v1` remain custody inputs.\n- Review images are proof views, not final-art or readiness evidence.\n", encoding="utf-8")
    manifest = {"phase": "Phase 1L.5bz-R2 bottom-only topology-and-weight redesign walk proof", "status": "offline_bottom_walk_proof_not_runtime_or_final_art", "semantic": semantic, "files": {"blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)}, "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))}, "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)}, "reviews": reviews}}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"STARTER_OUTFIT_WALK_R2_PASS frames=21 identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["files"]["blend"]["sha256"] != sha256(OUTPUT):
        raise RuntimeError("saved Blend custody drift")
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT), load_ui=False)
    body, top, bottom, armature = (bpy.data.objects[n] for n in (BODY, TOP, BOTTOM, ARMATURE))
    if topology_proof(bottom) != manifest["semantic"]["topology"] or scope["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}) != {k: manifest["semantic"]["weights"][k] for k in ("vertices", "unweighted", "invalid_or_non_normalized")}:
        raise RuntimeError("saved bottom proof drift")
    if scope["action_semantic"](bpy.data.actions[scope["ACTION"]]) != manifest["semantic"]["action"] or scope["frame_proof"](bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("cold replay drift")
    print(f"STARTER_OUTFIT_WALK_R2_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    try:
        build()
    except R2Failure as failure:
        receipt = {"phase": "Phase 1L.5bz-R2 bottom-only topology-and-weight redesign walk proof", "status": "BLOCKED_UNCOUNTED_FAIL_CLOSED_AT_NEUTRAL_TOPOLOGY", "source_custody": scope["custody"](), "accepted_source_bottom_mesh_sha256": scope["BOTTOM_MESH_SHA"], "authorized_single_trial": {"upper_metaball_scale_xyz_m": [.48, .40, .25], "leg_metaball_scale_xyz_m": [.30, .36, .25], "saddle_z_formula_m": ".58 + .04 * abs(2*t-1)^2", "z_face_cuts_m": [.62, .86], "root_weight": .99, "total_thigh_weight": .01}, "failure": failure.payload, "boundaries": {"derived_blend_written": 0, "review_images_accepted": 0, "accepted_inputs_mutated": 0, "runtime_change": 0, "frozen_regression_claim": 0, "brain_admin_claim": 0, "package_claim": 0, "phase_credit": 0, "notion_sync": 0, "next_phase": 0}}
        FAILURE.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("STARTER_OUTFIT_WALK_R2_FAIL stage=neutral_topology boundary_loops=1", flush=True)
        os._exit(1)
