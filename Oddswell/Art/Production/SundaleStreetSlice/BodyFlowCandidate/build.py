"""Coherent native torso/hip stance study from the retained cotton checkpoint."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
root = Path(__file__).resolve().parents[5]
source = root / 'Oddswell/Art/Production/SundaleStreetSlice/PelvicCottonCandidate/PelvicCotton.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == 'CF4ECCDDA1AEA696C61D588B132157727FA3CF6EEB3E1152B681B061BD0FBB87'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
center = Vector((-.75, -2.4, .88))

def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)

def band(z, low, rise, fall, high):
    return smooth((z - low) / (rise - low)) * (1 - smooth((z - fall) / (high - fall)))

def warp(p):
    p = Vector(p)
    if p.z <= .56 or p.z >= 1.53:
        return p
    original = p.copy()
    dx, dy = p.x - center.x, p.y - center.y
    hips = band(p.z, .56, .78, .88, 1.07) * (1 - smooth((abs(dx) - .22) / .07))
    chest = band(p.z, .93, 1.15, 1.36, 1.53)
    theta = math.radians(-4.5 * hips + 3.5 * chest)
    p.x = center.x + dx * math.cos(theta) - dy * math.sin(theta)
    p.y = center.y + dx * math.sin(theta) + dy * math.cos(theta)
    # Pelvic obliquity and stance-side translation fade into fixed feet and neck.
    tilt = math.radians(2.5) * hips
    dx, dz = p.x - center.x, p.z - center.z
    p.x = center.x + dx * math.cos(tilt) + dz * math.sin(tilt)
    p.z = center.z - dx * math.sin(tilt) + dz * math.cos(tilt)
    hip_contour = band(original.z, .62, .74, .87, 1.0) * (1 - smooth((abs(original.x - center.x) - .225) / .035))
    p.x = center.x + (p.x - center.x) * (1 - .085 * hip_contour)
    p.y = center.y + (p.y - center.y) * (1 - .09 * hip_contour)
    p.x += .020 * band(original.z, .57, .82, .95, 1.48)
    p.z += .005 * (original.x - center.x) / .22 * chest
    # A graded waist and shallow ribcage contour shape the support and cloth together.
    torso = band(original.z, .93, 1.01, 1.25, 1.36)
    lateral = smooth((abs(original.x - center.x) - .09) / .10)
    arm_exclusion = 1 - smooth((abs(original.x - center.x) - .225) / .06)
    waist = math.exp(-((original.z - 1.06) / .13) ** 2)
    p.x -= math.copysign(.016 * torso * waist * lateral * arm_exclusion, original.x - center.x)
    front = smooth((original.y - center.y - .025) / .07)
    p.y -= .012 * torso * front * arm_exclusion * math.exp(-((original.z - 1.18) / .16) ** 2)
    return p

changes = {}
control = bpy.data.objects.new('Body flow | stance blend', None)
scene.collection.objects.link(control)
control.empty_display_type = 'PLAIN_AXES'
control.empty_display_size = .12
control.location = center
control['flow'] = 1.0
control.id_properties_ui('flow').update(min=0., max=1., description='Blend the native torso/hip study from the previous stance to the retained weight shift')
def drive(key):
    curve = key.driver_add('value')
    driver = curve.driver
    variable = driver.variables.new()
    variable.name = 'flow'
    variable.type = 'SINGLE_PROP'
    variable.targets[0].id = control
    variable.targets[0].data_path = '["flow"]'
    driver.expression = '1-flow'

for obj in list(scene.objects):
    if not obj.name.startswith('Character | ') or obj.type not in {'MESH', 'CURVE'}:
        continue
    # Preserve the existing facial controls, including unused low neck vertices.
    if obj.name == 'Character | anatomical head':
        continue
    world, inverse = obj.matrix_world, obj.matrix_world.inverted()
    if obj.type == 'MESH':
        points = [v.co.copy() for v in obj.data.vertices]
        shifts = [(warp(world @ p) - world @ p).length for p in points]
        if max(shifts, default=0) < 1e-9:
            continue
        original = obj.data.attributes.new(name='Before torso hip flow', type='FLOAT_VECTOR', domain='POINT')
        for value, p in zip(original.data, points):
            value.vector = p
        if obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                for value in key.data:
                    value.co = inverse @ warp(world @ value.co)
            for vertex, point in zip(obj.data.vertices, obj.data.shape_keys.key_blocks[0].data):
                vertex.co = point.co
        else:
            for vertex in obj.data.vertices:
                vertex.co = inverse @ warp(world @ vertex.co)
        for name in ('Tailored rest', 'Collision fit', 'Gravity result'):
            attribute = obj.data.attributes.get(name)
            if attribute:
                retained = obj.data.attributes.new(name='Before body flow ' + name, type='FLOAT_VECTOR', domain='POINT')
                for value, previous in zip(attribute.data, retained.data):
                    previous.vector = value.vector
                    value.vector = inverse @ warp(world @ value.vector)
        obj.data.update()
        if not obj.data.shape_keys:
            obj.shape_key_add(name='Basis', from_mix=False)
        previous = obj.shape_key_add(name='Previous torso hip stance', from_mix=False)
        for value, p in zip(previous.data, points):
            value.co = p
        drive(previous)
        changes[obj.name] = max(shifts)
    else:
        maximum = 0
        original_points = []
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for point in spline.bezier_points:
                    original_points.append((point.co.copy(), point.handle_left.copy(), point.handle_right.copy()))
                    for name in ('co', 'handle_left', 'handle_right'):
                        p = world @ getattr(point, name)
                        new = warp(p)
                        maximum = max(maximum, (new - p).length)
                        setattr(point, name, inverse @ new)
            else:
                for point in spline.points:
                    original_points.append((Vector(point.co[:3]),))
                    p = world @ Vector(point.co[:3])
                    new = warp(p)
                    maximum = max(maximum, (new - p).length)
                    point.co = (*(inverse @ new), point.co.w)
        if maximum > 0:
            if not obj.data.shape_keys:
                obj.shape_key_add(name='Basis', from_mix=False)
            previous = obj.shape_key_add(name='Previous torso hip stance', from_mix=False)
            assert len(previous.data) == len(original_points), obj.name
            for value, original in zip(previous.data, original_points):
                value.co = original[0]
                if len(original) == 3:
                    value.handle_left, value.handle_right = original[1:]
            drive(previous)
            changes[obj.name] = maximum

coat = bpy.data.objects['Character | tailored slate jacket']
fit = coat.data.attributes['Collision fit'].data
gravity = coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m'] = max((a.vector - b.vector).length for a, b in zip(gravity, fit))
scene['torso_hip_flow'] = True
scene['torso_hip_flow_pelvic_yaw_deg'] = -4.5
scene['torso_hip_flow_chest_yaw_deg'] = 3.5
scene['torso_hip_flow_pelvic_tilt_deg'] = 2.5
scene['torso_hip_flow_stance_shift_m'] = .020
scene['torso_hip_flow_lateral_hip_contour_fraction'] = .085
scene['torso_hip_flow_depth_hip_contour_fraction'] = .09
scene['torso_hip_flow_objects'] = json.dumps(changes, sort_keys=True)
scene['torso_hip_flow_control'] = control.name
assert .01 < max(changes.values()) < .06
bpy.context.view_layer.update()
scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'BodyFlow.blend'), compress=True)
print('BODY_FLOW_SAVED', len(changes), max(changes.values()), flush=True)
