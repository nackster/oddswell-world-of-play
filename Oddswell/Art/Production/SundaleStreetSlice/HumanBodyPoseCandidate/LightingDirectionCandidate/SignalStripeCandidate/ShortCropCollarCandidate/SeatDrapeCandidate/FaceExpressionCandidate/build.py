"""Retain licensed MakeHuman facial movement targets on the walking head."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from zipfile import ZipFile
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parent
scene_root = root.parents[5]
source = root.parent / 'HeadTurnCandidate' / 'HeadTurn.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == 'DBE6D5827267B33A6F6849D34CD8B98D2518B8BD3FFB38F977D085CAAE69AA86'
archive = scene_root / 'source-assets' / 'faceunits01_cc0.zip'
with archive.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == 'D113107BD7EB59F3AF4DF6FC0EC29BFCC593F496D0B336AEC14F086A80CE7146'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
head = bpy.data.objects['Character | anatomical head']
source_ids = head.data.attributes['MakeHuman source vertex'].data
keys = head.data.shape_keys.key_blocks
basis = keys['Basis']

# Match the original hm08 body-height conversion used by build_scene.py.
obj_file = scene_root / 'source-assets' / 'makehuman-base.obj'
raw_y, body_ids, group = [], set(), ''
for line in obj_file.read_text(encoding='utf-8').splitlines():
    parts = line.split()
    if not parts:
        continue
    if parts[0] == 'v':
        raw_y.append(float(parts[2]))
    elif parts[0] == 'g':
        group = parts[1]
    elif parts[0] == 'f' and group == 'body':
        body_ids.update(int(p.split('/')[0]) - 1 for p in parts[1:])
unit = 1.8 / (max(raw_y[i] for i in body_ids) - min(raw_y[i] for i in body_ids))
rotation = Matrix.Rotation(math.radians(scene['upper_body_yaw_deg'] + scene['head_court_turn_deg']), 3, 'Z')

def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)

weights = {
    'mouthSmileLeft': .30, 'mouthSmileRight': .22,
    'cheekSquintLeft': .16, 'cheekSquintRight': .12,
}
with ZipFile(archive) as package:
    for name, weight in weights.items():
        records = package.read('targets/faceunits/' + name + '.target').decode('utf-8').splitlines()
        delta = {}
        for row in records:
            parts = row.split()
            if len(parts) == 4 and parts[0].isdigit():
                x, y, z = map(float, parts[1:])
                delta[int(parts[0])] = rotation @ (Vector((x, z, y)) * unit)
        key = head.shape_key_add(name='Faceunit ' + name, from_mix=False)
        key.value = weight
        max_weighted = 0.0
        max_eye = 0.0
        for vertex, identity in zip(head.data.vertices, source_ids):
            change = delta.get(identity.value, Vector())
            fade = smooth((vertex.co.z - 1.605) / .025)
            applied = change * fade
            key.data[vertex.index].co = basis.data[vertex.index].co + applied
            max_weighted = max(max_weighted, applied.length * weight)
            if vertex.co.z > 1.705:
                max_eye = max(max_eye, applied.length * weight)
        print('FACEUNIT', name, 'source_points', len(delta), 'weighted_max', max_weighted,
              'eye_zone_max', max_eye, flush=True)

# The cheek unit moves the eyelid tissue. Carry its attached wet margin and
# grooming back to the newly evaluated skin rather than leaving floating roots.
bpy.context.view_layer.update()
surface = BVHTree.FromObject(head, bpy.context.evaluated_depsgraph_get())
max_attachment_shift = 0.0
for side in ('l', 'r'):
    wet = bpy.data.objects['Character | lower wet margin ' + side]
    to_head = head.matrix_world.inverted() @ wet.matrix_world
    to_detail = to_head.inverted()
    for point in wet.data.splines[0].points:
        prior = to_head @ Vector(point.co[:3])
        hit, normal, _, _ = surface.find_nearest(prior)
        assert hit is not None
        fitted = hit + normal * .00009
        max_attachment_shift = max(max_attachment_shift, (fitted-prior).length)
        point.co = (*(to_detail @ fitted), point.co.w)
for label in ('eyelashes l', 'eyelashes r', 'eyebrow -1', 'eyebrow 1'):
    detail = bpy.data.objects['Character | ' + label]
    to_head = head.matrix_world.inverted() @ detail.matrix_world
    to_detail = to_head.inverted()
    for strand in detail.data.splines:
        prior = to_head @ Vector(strand.points[0].co[:3])
        hit, normal, _, _ = surface.find_nearest(prior)
        assert hit is not None
        shift = hit + normal * .00009 - prior
        max_attachment_shift = max(max_attachment_shift, shift.length)
        for point in strand.points:
            fitted = to_head @ Vector(point.co[:3]) + shift
            point.co = (*(to_detail @ fitted), point.co.w)
print('MAX_FACE_ATTACHMENT_SHIFT', max_attachment_shift, flush=True)

scene['faceunit_expression'] = ','.join(f'{name}:{weight}' for name, weight in weights.items())
if '--render' in sys.argv:
    for label, place, target, lens, width, height in (
        ('Front', (-.75, -1.25, 1.65), (-.75, -2.4, 1.62), 85, 900, 900),
        ('Three_Quarter', (-1.35, -1.58, 1.67), (-.75, -2.4, 1.62), 82, 900, 900),
        ('Full_Rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 900, 990),
    ):
        data = bpy.data.cameras.new('Face expression ' + label)
        camera = bpy.data.objects.new('Face expression ' + label, data)
        scene.collection.objects.link(camera)
        camera.location = place
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.lens = lens
        scene.camera = camera
        scene.cycles.samples = 24
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(root / ('Face_Expression_' + label + '.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera, do_unlink=True)
scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'FaceExpression.blend'), compress=True)
print('ODDSWELL_FACE_EXPRESSION_CANDIDATE_PASS', flush=True)
