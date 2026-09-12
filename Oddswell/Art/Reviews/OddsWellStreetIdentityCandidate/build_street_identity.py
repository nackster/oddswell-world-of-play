"""One noncanonical, native Blender character/street composition for owner review."""
from pathlib import Path
import hashlib
import json
import math
import random
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
VAULT = ROOT.parents[2]
HERO = VAULT / "Art/Production/PlayerCharacter/CharacterMotionAxisCorrection/MotionAxisCharacterCandidate.blend"
FACADE = VAULT / "Art/Production/SundaleArchitecture/ResidentialNeighborhoodServices/SM_Sundale_ResidentialFacade_A.blend"
random.seed(42)
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb, roughness=0.85):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = roughness
    noise = m.node_tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 65
    bump = m.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.13
    bump.inputs["Distance"].default_value = 0.025
    m.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return m


stone = material("Warm limestone", (0.68, 0.59, 0.44))
terracotta = material("Muted terracotta", (0.39, 0.18, 0.105))
sand = material("Sand concrete", (0.49, 0.40, 0.28))
teal = material("Signal teal", (0.08, 0.72, 0.68))
cobalt = material("Court cobalt", (0.04, 0.12, 0.19))
charcoal = material("Charcoal", (0.07, 0.085, 0.083))
cream = material("Court chalk", (0.90, 0.87, 0.74))
leaves = [material("Sage canopy " + str(i), (0.12 + i * 0.025, 0.18 + i * 0.025, 0.09 + i * 0.012)) for i in range(4)]


def cube(name, location, scale, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new("Soft manufactured edges", "BEVEL")
        b.width, b.segments = bevel, 2
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o


def line(name, coords, mat, radius=0.025, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = radius
    data.bevel_resolution = 1
    spline = data.splines.new("POLY")
    spline.points.add(len(coords) - 1)
    for p, xyz in zip(spline.points, coords):
        p.co = (*xyz, 1)
    spline.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    data.materials.append(mat)
    return o


# Append the actual corrected character. No face, hair, or new silhouette is invented.
with bpy.data.libraries.load(str(HERO), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "Armature" or n == "MANNEQUIN__neutral_beta" or n.startswith("CLOTHING__")]
    dst.actions = ["walk_candidate_v1"]
for o in dst.objects:
    if o:
        bpy.context.collection.objects.link(o)
armature = bpy.data.objects["Armature"]
armature.animation_data.action = bpy.data.actions["walk_candidate_v1"]
bpy.context.scene.frame_set(6)
for o in dst.objects:
    if o and o.name == "CLOTHING__starter_offwhite_top":
        o.hide_render = True
    if o and o.type == "MESH":
        for m in o.data.materials:
            if m and m.use_nodes:
                shader = m.node_tree.nodes.get("Principled BSDF")
                if shader:
                    shader.inputs["Roughness"].default_value = 0.85

cube("Civic ground", (0, -13, -0.22), (36, 52, 0.4), sand)
cube("Brick promenade", (0, -14, 0), (4.4, 42, 0.06), terracotta)
for y in range(-33, 7):
    for x in range(-3, 4):
        cube("Paving joint", (x * 0.62 + (0.31 if y % 2 else 0), y * 0.85, 0.034), (0.59, 0.82, 0.012), stone if (x + y) % 7 == 0 else terracotta)
for x in (-2.28, 2.28):
    line("Promenade edge", [(x, 7, 0.07), (x, -33, 0.07)], stone, 0.07)

# Reuse the accepted small facade as a street-scale reference, not a new city layout.
with bpy.data.libraries.load(str(FACADE), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "SM_Sundale_ResidentialFacade_A"]
facade = next(o for o in dst.objects if o)
for i, y in enumerate((0, -7, -14, -21)):
    o = facade if i == 0 else facade.copy()
    bpy.context.collection.objects.link(o)
    o.location = (-7, y, 0)
    o.rotation_euler.z = math.radians(90)
    cube("Limestone upper mass", (-7.2, y, 6.4), (4.2, 5.2, 3.0), stone, 0.06)
    for z in (5.3, 7.2):
        for yy in (y - 1.5, y, y + 1.5):
            cube("Deep window", (-5.05, yy, z), (0.035, 0.74, 1.0), charcoal)
    cube("Terracotta cornice", (-7.2, y, 8.0), (4.4, 5.3, 0.22), terracotta, 0.04)

cube("Public half court", (7.8, -12, 0.055), (8.6, 15, 0.08), cobalt)
for x in (3.7, 11.9):
    line("Court sideline", [(x, -4.7, 0.104), (x, -19.3, 0.104)], cream)
for y in (-4.7, -19.3):
    line("Court baseline", [(3.7, y, 0.104), (11.9, y, 0.104)], cream)
line("Court circle", [(7.8 + 1.8 * math.cos(t * math.tau / 64), -12 + 1.8 * math.sin(t * math.tau / 64), 0.105) for t in range(64)], cream, cyclic=True)
line("Court key", [(5.9, -19.3, 0.105), (5.9, -15.5, 0.105), (9.7, -15.5, 0.105), (9.7, -19.3, 0.105)], cream)
cube("Basket post", (7.8, -20.1, 1.65), (0.12, 0.12, 3.3), charcoal, 0.02)
cube("Basket backboard", (7.8, -19.7, 3.15), (1.8, 0.09, 1.05), stone, 0.025)
line("Basket rim", [(7.8 + 0.23 * math.cos(t * math.tau / 32), -19.25 + 0.23 * math.sin(t * math.tau / 32), 2.95) for t in range(32)], terracotta, 0.025, True)

for x, y in ((3, -3), (3, -10), (3, -18), (-3.4, -5), (-3.4, -16)):
    cube("Limestone seat", (x, y, 0.35), (1.05, 1.5, 0.65), stone, 0.08)
    cube("Tree trunk", (x, y, 2), (0.23, 0.23, 3.8), charcoal, 0.05)
    for i in range(8):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(x + random.uniform(-1.2, 1.2), y + random.uniform(-1.2, 1.2), 3.8 + random.uniform(0, 1.1)))
        o = bpy.context.object
        o.name = "Faceted sage canopy"
        o.scale = (1.4, 1.4, 0.9)
        o.data.materials.append(leaves[i % 4])
for y in (-7, -16):
    cube("Court bench", (12.8, y, 0.48), (0.7, 2.2, 0.2), stone, 0.05)
    cube("Signal edge", (12.39, y, 0.47), (0.08, 2.2, 0.08), teal)

# Arena as a distant civic anchor, with ribs and two restrained horizontal bands.
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=8, depth=7, location=(1, -35, 3.5))
arena = bpy.context.object
arena.name = "Arena silhouette study"
arena.data.materials.append(cobalt)
for z in (0.5, 6.5):
    line("Arena limestone ring", [(1 + 8.2 * math.cos(t * math.tau / 64), -35 + 8.2 * math.sin(t * math.tau / 64), z) for t in range(64)], stone, 0.2, True)
for i in range(24):
    a = i * math.tau / 24
    cube("Arena rib", (1 + 8.1 * math.cos(a), -35 + 8.1 * math.sin(a), 3.5), (0.16, 0.16, 6.1), sand)

world = bpy.data.worlds.new("Warm civic afternoon")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.60, 0.72, 0.82, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
bpy.ops.object.light_add(type="SUN", location=(5, 5, 15))
sun = bpy.context.object
sun.rotation_euler = (math.radians(38), math.radians(-25), math.radians(-35))
sun.data.energy = 3.0
sun.data.angle = math.radians(4)
sun.data.color = (1.0, 0.82, 0.62)
bpy.ops.object.camera_add(location=(1.4, 4.7, 2.15))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, -11, 1.3)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 27
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1600, 900, 100
scene.view_settings.view_transform = "AgX"
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "OddsWell_Street_Identity_Candidate.png")
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "OddsWellStreetIdentityCandidate.blend"))
bpy.ops.render.render(write_still=True)
(ROOT / "provenance.json").write_text(json.dumps({"status": "OWNER_REVIEW_CANDIDATE", "cost_usd": 0,
    "scope": "Native Blender study only; generated concept has separate generation-brief.md",
    "source_character": str(HERO.relative_to(VAULT)), "source_character_sha256": hashlib.sha256(HERO.read_bytes()).hexdigest(),
    "source_facade": str(FACADE.relative_to(VAULT)), "source_facade_sha256": hashlib.sha256(FACADE.read_bytes()).hexdigest(),
    "engine_map_changed": False, "final_art_approved": False, "logos_or_identifying_text": False}, indent=2) + "\n")
print("ODDSWELL_STREET_IDENTITY_RENDER_PASS")
