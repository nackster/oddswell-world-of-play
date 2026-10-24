"""Brighten the constructed canvas shoes and stitch the heel reinforcement."""
import bmesh
import bpy
import hashlib
import sys
from pathlib import Path
from mathutils import Vector

output=Path(__file__).resolve().parent
source=output.parent/'SeatRelaxCandidate/SeatRelax.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='9BC408AB8BEBCECD30EB6131C6C6C538B759515C30E81E907728B9A57D762A25'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
palette={
    'Character | oat canvas':(.74,.72,.66,1),
    'Character | warmer canvas toe panels':(.70,.68,.62,1),
    'Character | reinforced canvas heel':(.68,.66,.60,1),
    'Character | bound canvas collar':(.66,.64,.59,1),
}
for name,color in palette.items():
    material=bpy.data.materials[name]
    material.diffuse_color=color
    for node in material.node_tree.nodes:
        if node.type=='MIX_RGB' and node.blend_type=='MULTIPLY':
            node.inputs[1].default_value=color
    print('CANVAS_COLOR',name,color,flush=True)

thread=bpy.data.materials['Character | fine warm shoe thread'].copy()
thread.name='Character | heel reinforcement stitching'
thread.diffuse_color=(.45,.43,.38,1)
thread.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=thread.diffuse_color

for side in ('left','right'):
    upper=bpy.data.objects['Character | canvas sneaker '+side]
    bm=bmesh.new();bm.from_mesh(upper.data)
    bm.verts.ensure_lookup_table()
    edges=[e for e in bm.edges if len(e.link_faces)==2 and {f.material_index for f in e.link_faces}=={0,3}]
    neighbors={}
    for edge in edges:
        a,b=[v.index for v in edge.verts]
        neighbors.setdefault(a,[]).append(b)
        neighbors.setdefault(b,[]).append(a)
    assert len(edges)>200 and len(neighbors)==len(edges)
    assert all(len(nexts)==2 for nexts in neighbors.values())
    start=min(neighbors)
    ordered=[start]
    previous=None
    current=start
    while True:
        following=next(index for index in neighbors[current] if index!=previous)
        if following==start:break
        assert following not in ordered
        ordered.append(following)
        previous,current=current,following
    assert len(ordered)==len(edges)
    bm.free()

    vertices=upper.data.vertices
    path=[vertices[i].co.copy()+vertices[i].normal*.0003 for i in ordered]
    path.append(path[0].copy())
    distances=[0.0]
    for a,b in zip(path,path[1:]):distances.append(distances[-1]+(b-a).length)
    def point_at(distance):
        for i in range(len(path)-1):
            if distance<=distances[i+1]:
                t=(distance-distances[i])/max(1e-9,distances[i+1]-distances[i])
                return path[i].lerp(path[i+1],t)
        return path[-1]
    total=distances[-1]
    count=round(total/.0038)
    data=bpy.data.curves.new('Sewn heel counter '+side,'CURVE')
    data.dimensions='3D';data.bevel_depth=.00024;data.bevel_resolution=2
    data.materials.append(thread)
    for i in range(count):
        middle=(i+.5)*total/count
        segment=data.splines.new('POLY');segment.points.add(1)
        for vertex,position in zip(segment.points,(point_at(middle-.00115),point_at(middle+.00115))):
            vertex.co=(*position,1)
    seam=bpy.data.objects.new('Character | sewn heel counter '+side,data)
    scene.collection.objects.link(seam)
    seam.matrix_world=upper.matrix_world.copy()
    print('HEEL_COUNTER_STITCHES',side,count,round(total,4),flush=True)
scene['sewn_shoe_heel_counters']=True

if '--render' in sys.argv:
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.75,-3.50,.28),(-.75,-2.4,.12),65,900,810),
        ('Profile_Close',(-1.65,-2.4,.27),(-.75,-2.4,.12),65,900,810),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ):
        data=bpy.data.cameras.new('Canvas color '+label)
        camera=bpy.data.objects.new('Canvas color '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=20
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Shoe_Canvas_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'ShoeCanvas.blend'),compress=True)
print('SHOE_CANVAS_CANDIDATE_PASS',flush=True)
