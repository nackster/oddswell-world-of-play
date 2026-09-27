"""Build and validate the Phase 1L.5ca connected starter-top walk proof."""

import bmesh
import bpy
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SLICE = ROOT.parent
R3_BUILDER = SLICE / "RefinedStarterOutfitWalkR3/build_starter_outfit_walk_r3.py"
scope = {"__file__": str(R3_BUILDER)}
source = R3_BUILDER.read_text(encoding="utf-8")
exec(source[: source.rfind('if "--validate"')], scope)
base = scope["scope"]

BODY, TOP, BOTTOM, ARMATURE = (scope[name] for name in ("BODY", "TOP", "BOTTOM", "ARMATURE"))
R3_BLEND = SLICE / "RefinedStarterOutfitWalkR3/RefinedSundaleStarterOutfitWalkR3.blend"
R3_MANIFEST = SLICE / "RefinedStarterOutfitWalkR3/starter_outfit_walk_r3_custody.json"
OUTPUT = ROOT / "RefinedSundaleConnectedStarterTopWalk.blend"
MANIFEST = ROOT / "connected_starter_top_walk_custody.json"
PROVENANCE = ROOT / "PROVENANCE.md"
REVIEWS = ROOT / "Review"
BODY_SHA = "F340C34B05FC4D0D20F5625E9B2F9174947B691F59420367E8B738BE1CBF03CD"
BOTTOM_SHA = "5C0357E1ADDE7B35380222BDF6AD33BFF75A59D28B1AEFDD2404AC8630083618"
ACTION_SHA = "7DD9A4E6524BCAC604AEDC755D0464FEC8C8F40BDED1BDE17E87955ED63E1020"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def semantic_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def armature_semantic(armature):
    return [
        {
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "head": base["rounded"](bone.head_local),
            "tail": base["rounded"](bone.tail_local),
            "use_deform": bone.use_deform,
        }
        for bone in sorted(armature.data.bones, key=lambda item: item.name)
    ]


def r3_custody():
    receipt = json.loads(R3_MANIFEST.read_text(encoding="utf-8"))
    expected = receipt["files"]["blend"]
    actual = {"bytes": R3_BLEND.stat().st_size, "sha256": sha256(R3_BLEND)}
    if actual != expected:
        raise RuntimeError(f"R3 Blend custody drift: {actual}")
    semantic = receipt["semantic"]
    if semantic["derived_mesh_sha256"][BOTTOM] != BOTTOM_SHA:
        raise RuntimeError("R3 bottom identity drift")
    if semantic["action"]["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("R3 action identity drift")
    return {"blend": actual, "identity_sha256": semantic["identity_sha256"]}


def make_top(armature):
    old = bpy.data.objects[TOP]
    bpy.data.objects.remove(old, do_unlink=True)
    forms = [
        {"role": "torso", "center_m": [0.00, 0.02, 1.25], "dimensions_m": [0.76, 0.58, 0.50]},
        {"role": "left_sleeve", "center_m": [0.32, 0.02, 1.28], "dimensions_m": [0.32, 0.38, 0.36]},
        {"role": "right_sleeve", "center_m": [-0.32, 0.02, 1.28], "dimensions_m": [0.32, 0.38, 0.36]},
    ]
    parts = []
    for form in forms:
        bpy.ops.mesh.primitive_cube_add(location=form["center_m"])
        part = bpy.context.object
        part.name = f"TOP_FORM__{form['role']}"
        part.dimensions = form["dimensions_m"]
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
        parts.append(part)
    top = parts[0]
    for part in parts[1:]:
        modifier = top.modifiers.new(f"UNION__{part.name}", "BOOLEAN")
        modifier.operation, modifier.solver, modifier.object = "UNION", "EXACT", part
        bpy.context.view_layer.objects.active = top
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(part, do_unlink=True)
    top.name, top.data.name = TOP, "MESH__connected_starter_top"

    mesh = bmesh.new()
    mesh.from_mesh(top.data)
    bmesh.ops.subdivide_edges(mesh, edges=list(mesh.edges), cuts=7, use_grid_fill=True)
    removed = []
    for face in mesh.faces:
        center = face.calc_center_median()
        if center.z < 1.01 and abs(center.x) < 0.32:
            removed.append(face)
        elif center.z > 1.499 and abs(center.x) < 0.19 and -0.25 < center.y < 0.36:
            removed.append(face)
        elif center.z < 1.11 and abs(center.x) > 0.16:
            removed.append(face)
    bmesh.ops.delete(mesh, geom=removed, context="FACES")
    loose = [vertex for vertex in mesh.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(mesh, geom=loose, context="VERTS")
    mesh.to_mesh(top.data)
    mesh.free()
    top.data.update()
    bevel = top.modifiers.new("BEVEL__connected_starter_top", "BEVEL")
    bevel.width, bevel.segments, bevel.limit_method = 0.025, 3, "ANGLE"
    bpy.context.view_layer.objects.active = top
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in top.data.polygons:
        polygon.use_smooth = True

    material = bpy.data.materials.new("MAT__starter_offwhite_top_proof")
    material.diffuse_color = (0.92, 0.90, 0.84, 1)
    top.data.materials.append(material)
    groups = {name: top.vertex_groups.new(name=name) for name in ("spine", "upper_arm.L", "upper_arm.R")}
    counts = {name: 0 for name in groups}
    for vertex in top.data.vertices:
        side = base["smoothstep"]((abs(vertex.co.x) - 0.16) / 0.18)
        weights = {"spine": 1 - side}
        weights["upper_arm.L" if vertex.co.x >= 0 else "upper_arm.R"] = side
        for name, weight in weights.items():
            if weight > 1e-8:
                groups[name].add([vertex.index], weight, "REPLACE")
                counts[name] += 1
    modifier = top.modifiers.new("ARMATURE__connected_starter_top", "ARMATURE")
    modifier.object, modifier.use_vertex_groups, modifier.use_bone_envelopes = armature, True, False
    top["item_id"], top["technical_proof_only"] = TOP, True
    return top, counts, forms


def top_opening_proof(obj):
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
    if len(loops) != 4:
        raise RuntimeError(f"connected starter top opening contract failed: {loops}")
    return sorted(loops, key=lambda item: (item["min"][0], item["min"][2]))


def render_reviews():
    REVIEWS.mkdir(exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    world = scene.world or bpy.data.worlds.new("World")
    scene.world, world.color = world, (0.07, 0.07, 0.07)
    camera_data = bpy.data.cameras.new("CAMERA__connected_top_review")
    camera = bpy.data.objects.new("CAMERA__connected_top_review", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera, camera_data.type, camera_data.ortho_scale = camera, "ORTHO", 2.2
    light_data = bpy.data.lights.new("LIGHT__connected_top_review", "AREA")
    light_data.energy, light_data.shape, light_data.size = 1000, "DISK", 4
    light = bpy.data.objects.new("LIGHT__connected_top_review", light_data)
    light.location = (3, -4, 5)
    bpy.context.collection.objects.link(light)
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
    for obj in (camera, light):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.frame_set(1)
    return {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(REVIEWS.glob("*.png"))}


def build():
    accepted = r3_custody()
    bpy.ops.wm.open_mainfile(filepath=str(R3_BLEND), load_ui=False)
    bpy.context.preferences.filepaths.save_version = 0
    body, bottom, armature = (bpy.data.objects[name] for name in (BODY, BOTTOM, ARMATURE))
    before = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": armature_semantic(armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if before["body"] != BODY_SHA or before["bottom"] != BOTTOM_SHA:
        raise RuntimeError("accepted R3 mesh identity drift")
    mapping = json.loads(base["DEC035"].read_text(encoding="utf-8"))["source_to_unreal_bone_names"]
    if len(before["armature"]) != 12 or {item["name"] for item in before["armature"]} != set(mapping):
        raise RuntimeError("DEC-035 hierarchy drift")
    top, counts, forms = make_top(armature)
    weights = {
        TOP: base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"}),
        BOTTOM: base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"}),
    }
    openings = top_opening_proof(top)
    topology = {
        TOP: scope["topology_proof"](top, (1, 4, 0), "connected starter top"),
        BOTTOM: scope["topology_proof"](bottom, (1, 3, 0), "accepted R3 bottom"),
    }
    deformation = base["frame_proof"](bpy.context.scene, body, top, bottom, armature)
    reviews = render_reviews()
    after = {
        "body": semantic_sha(base["mesh_semantic"](body)),
        "bottom": semantic_sha(base["mesh_semantic"](bottom)),
        "armature": armature_semantic(armature),
        "action": base["action_semantic"](bpy.data.actions[base["ACTION"]]),
    }
    if after != before:
        raise RuntimeError("accepted body/bottom/armature/action changed")
    semantic = {
        "accepted_r3": accepted,
        "accepted_mesh_sha256": {BODY: BODY_SHA, BOTTOM: BOTTOM_SHA},
        "derived_mesh_sha256": {TOP: semantic_sha(base["mesh_semantic"](top))},
        "construction": {
            "method": "native_connected_boolean_shirt_pattern_with_subdivided_neckline_and_four_declared_openings",
            "forms_xyz_m": forms,
            "bevel_width_m": 0.025,
            "bevel_segments": 3,
            "declared_openings": ["neckline", "waist_hem", "left_arm", "right_arm"],
        },
        "topology": topology,
        "declared_opening_geometry": openings,
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
        "# Phase 1L.5ca provenance\n\n"
        "- Additive connected starter-top derivative from the exact Phase 1L.5bz-R3 Blend and custody receipt.\n"
        "- The accepted body, R3 bottom, DEC-035 12-bone armature and `walk_candidate_v1` are unchanged.\n"
        "- One connected technical shirt mesh declares exactly four boundary openings: neckline, waist hem and two arm openings.\n"
        "- All 21 integer frames use evaluated-mesh BVH intersection checks and bidirectional vertex-to-surface clearance sampling.\n"
        "- Review images are offline topology/deformation proof, not runtime, final-art, performance or beta-readiness evidence.\n",
        encoding="utf-8",
    )
    manifest = {
        "phase": "Phase 1L.5ca connected starter-top pattern walk proof",
        "status": "offline_connected_top_walk_proof_not_runtime_or_final_art",
        "semantic": semantic,
        "files": {
            "blend": {"bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT)},
            "builder": {"bytes": Path(__file__).stat().st_size, "sha256": sha256(Path(__file__))},
            "provenance": {"bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "reviews": reviews,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CONNECTED_STARTER_TOP_WALK_PASS frames=21 loops=4 identity={semantic['identity_sha256']}")


def validate_saved():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["semantic"]["accepted_r3"] != r3_custody():
        raise RuntimeError("accepted R3 custody drift")
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
        TOP: scope["topology_proof"](top, (1, 4, 0), "connected starter top"),
        BOTTOM: scope["topology_proof"](bottom, (1, 3, 0), "accepted R3 bottom"),
    }
    if topology != manifest["semantic"]["topology"]:
        raise RuntimeError("saved topology drift")
    if top_opening_proof(top) != manifest["semantic"]["declared_opening_geometry"]:
        raise RuntimeError("saved top opening drift")
    base["weight_check"](top, {"spine", "upper_arm.L", "upper_arm.R"})
    base["weight_check"](bottom, {"root", "thigh.L", "thigh.R"})
    hierarchy = armature_semantic(armature)
    if hierarchy != manifest["semantic"]["armature"]["hierarchy"] or len(hierarchy) != 12:
        raise RuntimeError("saved DEC-035 hierarchy drift")
    action = base["action_semantic"](bpy.data.actions[base["ACTION"]])
    if action != manifest["semantic"]["action"] or action["identity_sha256"] != ACTION_SHA:
        raise RuntimeError("saved walk action drift")
    if base["frame_proof"](bpy.context.scene, body, top, bottom, armature) != manifest["semantic"]["deformation"]:
        raise RuntimeError("cold walk replay drift")
    print(f"CONNECTED_STARTER_TOP_WALK_VALIDATE_PASS identity={manifest['semantic']['identity_sha256']}")


if "--validate" in sys.argv:
    validate_saved()
else:
    build()
