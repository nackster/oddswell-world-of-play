"""Cold-check the native pose control and measure character import complexity."""
import bpy
import json
from pathlib import Path
from mathutils.bvhtree import BVHTree

out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out / 'BodyFlow.blend'))
scene = bpy.context.scene
control = bpy.data.objects[scene['torso_hip_flow_control']]
changed = json.loads(scene['torso_hip_flow_objects'])
assert control['flow'] == 1 and len(changed) > 100
assert all(bpy.data.objects[name].data.shape_keys.key_blocks.get('Previous torso hip stance') for name in changed)
maximum_restore_error = 0
names = ('tailored slate jacket', 'shorts leg continuous tailoring', 'anatomical legs',
         'internal torso support', 'posed pelvic fitting support')
for label in names:
    obj = bpy.data.objects['Character | ' + label]
    states = [m.show_viewport for m in obj.modifiers]
    for modifier in obj.modifiers:
        modifier.show_viewport = False
    control['flow'] = 0.
    control.update_tag()
    scene.frame_set(scene.frame_current)
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    original = obj.data.attributes['Before torso hip flow'].data
    assert len(mesh.vertices) == len(original)
    error = max((v.co - p.vector).length for v, p in zip(mesh.vertices, original))
    assert error < 1e-6, (label, error)
    maximum_restore_error = max(maximum_restore_error, error)
    evaluated.to_mesh_clear()
    for modifier, state in zip(obj.modifiers, states):
        modifier.show_viewport = state
control['flow'] = 1.
control.update_tag()
scene.frame_set(scene.frame_current)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
complexity = []
materials = set()
for obj in scene.objects:
    if not obj.name.startswith('Character | ') or obj.hide_render or obj.type not in {'MESH', 'CURVE'}:
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    complexity.append({'name': obj.name, 'type': obj.type, 'vertices': len(mesh.vertices),
                       'triangles': len(mesh.loop_triangles)})
    materials.update(m.name for m in obj.data.materials if m)
    evaluated.to_mesh_clear()
complexity.sort(key=lambda row: row['triangles'], reverse=True)
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
evaluated = pants.evaluated_get(depsgraph)
mesh = evaluated.to_mesh()
mesh.calc_loop_triangles()
points = [pants.matrix_world @ vertex.co for vertex in mesh.vertices]
triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles
             if all(-.86 < points[i].x < -.64 and .62 < points[i].z < .83 for i in tri.vertices)]
tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
overlaps = {(min(a, b), max(a, b)) for a, b in tree.overlap(tree)
            if a != b and not set(triangles[a]) & set(triangles[b])}
evaluated.to_mesh_clear()
assert len(overlaps) < 1290, len(overlaps)
report = {
    'result': 'PASS', 'native_control': control.name, 'driven_objects': len(changed),
    'maximum_source_restore_error_m': maximum_restore_error,
    'visible_character_objects': len(complexity),
    'visible_character_evaluated_triangles': sum(row['triangles'] for row in complexity),
    'visible_character_materials': len(materials),
    'largest_character_parts': complexity[:12],
    'scene_packed_maps': len([i for i in bpy.data.images if i.source == 'FILE' and i.packed_file]),
    'local_crotch_overlap_pairs': len(overlaps),
    'garment_intersection_free': False,
    'runtime_import_ready': False,
    'next_preparation': 'Bake hair/cloth detail, create a rigged derivative and measured LODs; compare walk deformation and engine appearance before runtime replacement.'
}
(out / 'BodyFlow-audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('BODY_FLOW_CONTROL_AND_IMPORT_AUDIT_PASS', json.dumps(report), flush=True)
