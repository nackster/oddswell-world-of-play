"""Bounded native gait study; licensed geometry remains in ignored local storage."""
import bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector, Quaternion

root = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
out = root / 'downloads/licensed-characters/RenderpeopleEric/MotionRefinement'
out.mkdir(exist_ok=True)
source = out.parent / 'OddsWellHuman.blend'

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

assert sha(source) == '3ed84ad823f809e19ff6c7bafc591109e90e20d96455b28bcd15431f82ae4485'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
rig = bpy.data.objects['Scan character | Eric rig']
body = bpy.data.objects['Scan character | Eric mesh']
holder = bpy.data.objects['Scan character | placement']

def identity():
    data = {
        'vertices': [list(v.co) for v in body.data.vertices],
        'polygons': [list(p.vertices) for p in body.data.polygons],
        'uvs': [[list(u.uv) for u in layer.data] for layer in body.data.uv_layers],
        'groups': [g.name for g in body.vertex_groups],
        'weights': [[(g.group, g.weight) for g in v.groups] for v in body.data.vertices],
        'bind': [(b.name, b.parent.name if b.parent else None, [list(r) for r in b.matrix_local]) for b in rig.data.bones],
        'maps': [(i.name, hashlib.sha256(i.packed_file.data).hexdigest()) for i in bpy.data.images if i.packed_file],
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

original_identity = identity()
names = ['hip', 'spine_01', 'spine_02', 'spine_03', 'neck', 'head', 'shoulder_l', 'shoulder_r']
names += [part + '_' + side for side in ('l', 'r') for part in ('upperarm', 'lowerarm', 'hand', 'upperleg', 'lowerleg', 'foot')]
poses, locations, old_separation = {}, {}, []
for frame in range(1, 50):
    scene.frame_set(frame)
    poses[frame] = {n: rig.pose.bones[n].rotation_quaternion.normalized() for n in names}
    locations[frame] = holder.location.copy()
    a = rig.matrix_world @ rig.pose.bones['foot_l'].head
    b = rig.matrix_world @ rig.pose.bones['foot_r'].head
    old_separation.append((a - b).length)

centers = {}
for name in names:
    reference = poses[1][name]
    values = [poses[f][name].copy() for f in range(1, 49)]
    for q in values:
        if reference.dot(q) < 0:
            q.negate()
    centers[name] = Quaternion([sum(q[i] for q in values) / len(values) for i in range(4)]).normalized()

rig.animation_data.action = rig.animation_data.action.copy()
rig.animation_data.action.name = 'OddsWell scanned human | restrained walking study'
holder.animation_data.action = holder.animation_data.action.copy()
holder.animation_data.action.name = 'OddsWell scanned human | restrained root and grounding'
mean_location = sum(locations.values(), Vector()) / len(locations)
records = []
for frame in range(1, 50):
    scene.frame_set(frame)
    for name in names:
        factor = .62 if name.startswith(('upperleg', 'lowerleg', 'foot')) else .72
        q = centers[name].slerp(poses[frame][name], factor)
        if name.startswith('upperarm'):
            # Move the source A-pose arms nearer the sides in the rig's original space.
            pb = rig.pose.bones[name]
            axis = (rig.matrix_local.to_3x3() @ pb.bone.matrix_local.to_3x3()).inverted() @ Vector((0, 1, 0))
            q = Quaternion(axis.normalized(), .18 if name.endswith('_l') else -.18) @ q
        q.normalize()
        assert all(math.isfinite(v) for v in q) and abs(q.magnitude - 1) < 1e-5
        rig.pose.bones[name].rotation_quaternion = q
        rig.pose.bones[name].keyframe_insert('rotation_quaternion', frame=frame, group=name)
    holder.location = mean_location + (locations[frame] - mean_location) * .65
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    assert all(math.isfinite(v) for p in points for v in p)
    floor = min(p.z for p in points)
    holder.location.z -= floor
    holder.keyframe_insert('location', frame=frame)
    a = rig.matrix_world @ rig.pose.bones['foot_l'].head
    b = rig.matrix_world @ rig.pose.bones['foot_r'].head
    records.append({'frame': frame, 'floor_adjustment_m': -floor, 'foot_bone_separation_m': (a - b).length})

assert identity() == original_identity
scene.frame_start, scene.frame_end, scene.render.fps = 1, 49, 24
scene.frame_set(1)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.render.resolution_percentage = 100
scene.render.use_persistent_data = True
scene.camera.data.lens = 42
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.14, .16, .18, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
# A real ground plane makes shoe height and shadow visible in the review.
bpy.ops.mesh.primitive_plane_add(size=200, location=(-.75, -2.4, -.002))
floor_obj = bpy.context.object
floor_obj.name = 'Motion review | studio ground'
mat = bpy.data.materials.new('Motion review | warm mineral floor')
mat.diffuse_color = (.32, .30, .27, 1)
mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.32, .30, .27, 1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .85
floor_obj.data.materials.append(mat)
bpy.context.preferences.filepaths.save_version = 0
native = out / 'OddsWellHumanMotion.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
bpy.ops.wm.open_mainfile(filepath=str(native))
body = bpy.data.objects['Scan character | Eric mesh']
rig = bpy.data.objects['Scan character | Eric rig']
holder = bpy.data.objects['Scan character | placement']
scene = bpy.context.scene
assert identity() == original_identity
assert len(body.data.vertices) == 10353 and len(rig.data.bones) == 88
ground_samples = []
for step in range(97):
    frame = 1 + step / 2
    scene.frame_set(int(frame), subframe=frame % 1)
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    minimum = min((evaluated.matrix_world @ v.co).z for v in mesh.vertices)
    evaluated.to_mesh_clear()
    assert math.isfinite(minimum)
    if step % 2 == 0:
        assert abs(minimum) < .0001, (frame, minimum)
    ground_samples.append({'frame': frame, 'minimum_mesh_z_m': minimum})
scene.frame_set(1)
new_max = max(r['foot_bone_separation_m'] for r in records)
assert new_max < max(old_separation), (new_max, max(old_separation))
report = {'source_sha256': sha(source), 'candidate_sha256': sha(native), 'unchanged_mesh_uv_weights_bind_and_maps_identity': original_identity,
          'modified_bones': names, 'keys_per_bone': 49, 'leg_motion_factor': .62, 'other_motion_factor': .72,
          'additional_upperarm_relaxation_radians': .18, 'root_motion_factor': .65,
          'source_max_foot_bone_separation_m': max(old_separation), 'candidate_max_foot_bone_separation_m': new_max,
          'cold_reopen_pass': True, 'frames': records, 'cold_ground_samples': ground_samples,
          'lowest_sampled_mesh_z_m': min(r['minimum_mesh_z_m'] for r in ground_samples),
          'scope': 'Offline restrained gait and arm posture study. Original source outfit and open hands remain. No planted-foot locking, complete contact proof, runtime export, or final walk acceptance.'}
(out / 'motion-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('MOTION_REFINEMENT_COLD_PASS', report['candidate_sha256'], max(old_separation), new_max, flush=True)
cam = scene.camera
def frame_camera(pos, target):
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    shift = Vector(((min(p.x for p in points) + max(p.x for p in points)) / 2 - target[0],
                    (min(p.y for p in points) + max(p.y for p in points)) / 2 - target[1], 0))
    cam.location = Vector(pos) + shift
    cam.rotation_euler = (Vector(target) + shift - cam.location).to_track_quat('-Z', 'Y').to_euler()

views = [('Full', 13, (-2.9, .4, 1.28), (-.75, -2.4, .98)),
         ('Front', 1, (-.75, .85, 1.15), (-.75, -2.4, .98)),
         ('Side', 25, (-4, -2.4, 1.15), (-.75, -2.4, .98))]
scene.render.resolution_x, scene.render.resolution_y = 760, 840
for name, frame, pos, target in views:
    scene.frame_set(frame)
    frame_camera(pos, target)
    scene.render.filepath = str(out / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    print('MOTION_RENDER', name, flush=True)
if '--preview' in sys.argv:
    frames = out / 'Frames'
    frames.mkdir(exist_ok=True)
    scene.cycles.samples = 8
    scene.render.resolution_x, scene.render.resolution_y = 640, 704
    for index, frame in enumerate(range(1, 49, 2)):
        scene.frame_set(frame)
        frame_camera(views[0][2], views[0][3])
        scene.render.filepath = str(frames / f'{index:04d}.png')
        bpy.ops.render.render(write_still=True)
        print('MOTION_PREVIEW_FRAME', frame, flush=True)
