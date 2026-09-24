"""Fit an editable padded trim to the actual low-shoe opening."""
import bmesh
import bpy
import hashlib
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
source = root.parent / 'ShoulderSlopeCandidate' / 'ShoulderSlope.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == '001A7AC72CBB8B81228489DE0858ED4F9E85408930B21F459E2C6B0373171C32'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene

material = bpy.data.materials['Character | oat canvas'].copy()
material.name = 'Character | bound canvas collar'
material.diffuse_color = (.42, .40, .37, 1)
for node in material.node_tree.nodes:
    if node.type == 'MIX_RGB' and node.blend_type == 'MULTIPLY':
        node.inputs[1].default_value = material.diffuse_color

for side in ('left', 'right'):
    for old in list(scene.objects):
        if old.name.startswith('Character | shoe lace collar seam ' + side):
            bpy.data.objects.remove(old, do_unlink=True)
    upper = bpy.data.objects['Character | canvas sneaker ' + side]
    bm = bmesh.new()
    bm.from_mesh(upper.data)
    bm.verts.ensure_lookup_table()
    edges = [edge for edge in bm.edges if len(edge.link_faces) == 2 and
             {face.material_index for face in edge.link_faces} == {0, 1}]
    neighbors = {}
    for edge in edges:
        a, b = (vertex.index for vertex in edge.verts)
        neighbors.setdefault(a, []).append(b)
        neighbors.setdefault(b, []).append(a)
    assert len(edges) > 100 and len(neighbors) == len(edges)
    assert all(len(nexts) == 2 for nexts in neighbors.values())

    start = min(neighbors)
    ordered = [start]
    previous = None
    current = start
    while True:
        following = next(index for index in neighbors[current] if index != previous)
        if following == start:
            break
        assert following not in ordered, 'Collar rim crosses itself'
        ordered.append(following)
        previous, current = current, following
    assert len(ordered) == len(edges), 'Collar rim contains a disconnected loop'

    curve = bpy.data.curves.new('Fitted padded shoe collar ' + side, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = .0030
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(ordered) - 1)
    spline.use_cyclic_u = True
    for point, index in zip(spline.points, ordered):
        point.co = (*bm.verts[index].co, 1)
    curve.materials.append(material)
    trim = bpy.data.objects.new('Character | fitted padded shoe collar ' + side, curve)
    scene.collection.objects.link(trim)
    trim.matrix_world = upper.matrix_world.copy()
    print('SHOE_RIM', side, len(ordered), flush=True)
    bm.free()

scene['fitted_padded_shoe_collars'] = True

if '--render' in sys.argv:
    from mathutils import Vector
    for label, place, target, lens, width, height, samples in (
        ('Rear_Close', (-.75, -3.50, .28), (-.75, -2.4, .12), 65, 1000, 900, 24),
        ('Profile_Close', (-1.65, -2.4, .27), (-.75, -2.4, .12), 65, 1000, 900, 24),
        ('Full_Rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 1000, 1100, 24),
    ):
        data = bpy.data.cameras.new('Shoe rim ' + label)
        camera = bpy.data.objects.new('Shoe rim ' + label, data)
        scene.collection.objects.link(camera)
        camera.location = place
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        data.lens = lens
        scene.camera = camera
        scene.cycles.samples = samples
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(root / ('Shoe_Rim_' + label + '.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera, do_unlink=True)
    scene.camera = bpy.data.objects['CAM | gameplay street']

scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'ShoeRim.blend'), compress=True)
print('ODDSWELL_SHOE_RIM_CANDIDATE_PASS', flush=True)
