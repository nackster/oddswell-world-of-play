"""Seat the anatomical ankles inside the low canvas shoes without collar gaps."""
import bpy
import hashlib
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parent
source = root.parent / 'CottonResettleCandidate' / 'CottonResettle.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == '5A25F314C84DB746BE5AA5E3629D1D048EB5689C41A6C9F1611B917F553BC8E0'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
leg = bpy.data.objects['Character | anatomical legs']
hair = bpy.data.objects['Character | fine calf hair']
assert leg.data.shape_keys is None and len(hair.data.splines) == 2600

def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def seat(p):
    p = Vector(p)
    if p.z > .205 or p.z < .075:
        return p
    left = p.x < -.75
    bottom, top = (.13, .205) if left else (.09, .165)
    amount = 1 - smooth((p.z - bottom) / (top - bottom))
    if amount <= 0:
        return p
    cx, cy = (-.89, -2.682) if left else (-.61, -2.259)
    p.x = cx + (p.x - cx) * (1 - .60 * amount)
    p.y = cy + (p.y - cy) * (1 - .20 * amount)
    return p

changed = 0
leg_local = leg.matrix_world.inverted()
for vertex in leg.data.vertices:
    old = leg.matrix_world @ vertex.co
    new = seat(old)
    vertex.co = leg_local @ new
    changed += (new - old).length > 1e-8
leg.data.update()

hair_local = hair.matrix_world.inverted()
for spline in hair.data.splines:
    for point in spline.points:
        p = seat(hair.matrix_world @ Vector(point.co[:3]))
        point.co = (*(hair_local @ p), point.co.w)

# A mesh deformation moves sampled hair roots off their interpolated triangles.
# Refit each root to the evaluated skin and carry its strand by the same offset.
bpy.context.view_layer.update()
skin = BVHTree.FromObject(leg, bpy.context.evaluated_depsgraph_get())
max_root_shift = 0.0
for spline in hair.data.splines:
    root_point = Vector(spline.points[0].co[:3])
    hit, normal, _, _ = skin.find_nearest(root_point)
    assert hit is not None
    shift = hit + normal * .00008 - root_point
    max_root_shift = max(max_root_shift, shift.length)
    for point in spline.points:
        point.co = (*(Vector(point.co[:3]) + shift), point.co.w)
assert max_root_shift < .003

heel = bpy.data.materials['Character | reinforced canvas heel']
heel.diffuse_color = (.48, .46, .39, 1)
for node in heel.node_tree.nodes:
    if node.type == 'MIX_RGB' and node.blend_type == 'MULTIPLY':
        node.inputs[1].default_value = heel.diffuse_color
scene['ankle_seat_vertex_count'] = changed
scene['ankle_seat_max_hair_root_shift_m'] = max_root_shift
print('ANKLE_SEAT', changed, max_root_shift, flush=True)

if '--render' in sys.argv:
    for label, place, target, lens, width, height in (
        ('Profile_Close', (-1.65, -2.4, .27), (-.75, -2.4, .12), 65, 900, 810),
        ('Rear_Close', (-.75, -3.50, .28), (-.75, -2.4, .12), 65, 900, 810),
        ('Full_Rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 900, 990),
    ):
        data = bpy.data.cameras.new('Ankle seat ' + label)
        camera = bpy.data.objects.new('Ankle seat ' + label, data)
        scene.collection.objects.link(camera)
        camera.location = place
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.lens = lens
        scene.camera = camera
        scene.cycles.samples = 20
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(root / ('Ankle_Seat_' + label + '.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera, do_unlink=True)

scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'AnkleSeat.blend'), compress=True)
print('ODDSWELL_ANKLE_SEAT_CANDIDATE_PASS', flush=True)
