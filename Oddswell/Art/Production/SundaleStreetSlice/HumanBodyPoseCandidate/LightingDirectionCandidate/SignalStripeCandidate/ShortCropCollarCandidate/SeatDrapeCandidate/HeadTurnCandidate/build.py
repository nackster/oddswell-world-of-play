"""Retain a small intentional head turn in the walking pose."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector

root = Path(__file__).resolve().parent
source = root.parent / 'AnkleSeatCandidate' / 'AnkleSeat.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == '3E56E25520E7811B52B761D7B4EFA2099135A86B61DEC3481664BEC78DBE4815'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene

names = {
    'Character | anatomical head',
    'Character | eye l', 'Character | iris l', 'Character | pupil l',
    'Character | eye r', 'Character | iris r', 'Character | pupil r',
    'Character | eyelashes l', 'Character | lower wet margin l',
    'Character | eyelashes r', 'Character | lower wet margin r',
    'Character | cropped scalp fibers',
    'Character | eyebrow -1', 'Character | eyebrow 1',
}
assert all(bpy.data.objects.get(name) is not None for name in names)
pivot = Vector((-.75, -2.4, 1.485))
rotation = Matrix.Rotation(math.radians(6), 3, 'Z')

def turn(p):
    return pivot + rotation @ (p - pivot)

for name in names:
    obj = bpy.data.objects[name]
    to_local = obj.matrix_world.inverted()
    if obj.type == 'MESH':
        if obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                for point in key.data:
                    point.co = to_local @ turn(obj.matrix_world @ point.co)
            for vertex, point in zip(obj.data.vertices, obj.data.shape_keys.key_blocks[0].data):
                vertex.co = point.co
        else:
            for vertex in obj.data.vertices:
                vertex.co = to_local @ turn(obj.matrix_world @ vertex.co)
        obj.data.update()
    elif obj.type == 'CURVE':
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for point in spline.bezier_points:
                    point.co = to_local @ turn(obj.matrix_world @ point.co)
                    point.handle_left = to_local @ turn(obj.matrix_world @ point.handle_left)
                    point.handle_right = to_local @ turn(obj.matrix_world @ point.handle_right)
            else:
                for point in spline.points:
                    point.co = (*(to_local @ turn(obj.matrix_world @ Vector(point.co[:3]))), point.co.w)

scene['head_court_turn_deg'] = 6
print('HEAD_TURN_OBJECTS', len(names), flush=True)

if '--render' in sys.argv:
    for label, place, target, lens, width, height in (
        ('front', (-.75, -1.25, 1.65), (-.75, -2.4, 1.62), 85, 900, 900),
        ('full-rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 900, 990),
    ):
        data = bpy.data.cameras.new('Head turn ' + label)
        camera = bpy.data.objects.new('Head turn ' + label, data)
        scene.collection.objects.link(camera)
        camera.location = place
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.lens = lens
        scene.camera = camera
        scene.cycles.samples = 20
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(root / ('Head_Turn_' + label + '.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera, do_unlink=True)

scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'HeadTurn.blend'), compress=True)
print('ODDSWELL_HEAD_TURN_CANDIDATE_PASS', flush=True)
