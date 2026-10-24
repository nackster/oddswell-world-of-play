"""Build a short crop and fitted collar facing from the verified signal scene."""
import bpy
import bmesh
import bisect
import hashlib
import math
import random
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'OddsWell_Signal_Stripe_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='5E1875679FD06888374E420E05C038B5BD647ED00EA316AC5B36BEB140E81585'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
head=bpy.data.objects['Character | anatomical head']
hair=bpy.data.objects['Character | cropped scalp fibers']

def hairline(position):
    x=abs(position.x+.75)
    front=max(0,min(1,(position.y+2.40)/.16))
    temple=max(0,min(1,(x-.055)/.040))
    return 1.685+.085*front+.025*temple+.003*math.sin(position.x*160+position.y*65)

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

field=head.data.attributes.new('Short crop stubble field','FLOAT','POINT')
for vertex,datum in zip(head.data.vertices,field.data):
    datum.value=.58*smooth((vertex.co.z-hairline(vertex.co))/.014)
material=head.data.materials[0]
nodes=material.node_tree.nodes
links=material.node_tree.links
bs=nodes.get('Principled BSDF')
previous=bs.inputs['Base Color'].links[0].from_socket
attribute=nodes.new('ShaderNodeAttribute')
attribute.attribute_name=field.name
blend=nodes.new('ShaderNodeMixRGB')
blend.blend_type='MIX'
links.new(attribute.outputs['Fac'],blend.inputs[0])
links.new(previous,blend.inputs[1])
blend.inputs[2].default_value=(.16,.12,.082,1)
links.new(blend.outputs[0],bs.inputs['Base Color'])

rng=random.Random(9131)
for spline in hair.data.splines:
    origin=Vector(spline.points[0].co[:3])
    for point in spline.points[1:]:
        direction=Vector(point.co[:3])-origin
        point.co=(*(origin+direction*2.7),1)
    spline.material_index=rng.choices((0,1,2),weights=(3,5,2))[0]
for material,color in zip(hair.data.materials,((.09,.07,.045),(.14,.105,.07),(.21,.16,.105))):
    material.diffuse_color=(*color,1)
    material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
scene['scalp_crop_length_scale']=2.7
scene['scalp_stubble_bed']=True

coat=bpy.data.objects['Character | tailored slate jacket']
collar=bpy.data.objects['Character | standing collar']
def boundaries(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    neighbours=defaultdict(set)
    for edge in bm.edges:
        if edge.is_boundary:
            a,b=edge.verts
            neighbours[a].add(b);neighbours[b].add(a)
    parts=[];unseen=set(neighbours)
    while unseen:
        start=unseen.pop();todo=[start];part={start}
        while todo:
            for near in neighbours[todo.pop()]:
                if near in unseen:unseen.remove(near);part.add(near);todo.append(near)
        parts.append([v.co.copy() for v in part])
    bm.free()
    return parts

outer=max(boundaries(coat),key=lambda part:sum(v.z for v in part)/len(part))
inner=min(boundaries(collar),key=lambda part:sum(v.z for v in part)/len(part))
assert len(outer)==88 and len(inner)==384,'Changed neck-ring topology'
cx=sum(p.x for p in inner)/len(inner)
cy=sum(p.y for p in inner)/len(inner)
def sampled(part,theta):
    indexed=sorted(((math.atan2(p.y-cy,p.x-cx)%math.tau,p) for p in part),key=lambda item:item[0])
    angles=[item[0] for item in indexed]
    j=bisect.bisect_right(angles,theta)
    lo=indexed[j-1] if j else (indexed[-1][0]-math.tau,indexed[-1][1])
    hi=indexed[j] if j<len(indexed) else (indexed[0][0]+math.tau,indexed[0][1])
    return lo[1].lerp(hi[1],(theta-lo[0])/(hi[0]-lo[0]))

count=256
verts=[]
for j in range(count):
    theta=math.tau*j/count
    p=sampled(inner,theta);q=sampled(outer,theta)
    axis=Vector((math.cos(theta),math.sin(theta),0))
    assert .003<(q-p).dot(axis)<.03,'Collar facing crosses or leaves neckline'
    verts.extend((p-axis*.001+Vector((0,0,.0002)),
                  p.lerp(q,.5)+Vector((0,0,.0011)),
                  q+axis*.0015-Vector((0,0,.00025))))
faces=[]
for j in range(count):
    k=(j+1)%count
    for ring in range(2):
        faces.append((j*3+ring,j*3+ring+1,k*3+ring+1,k*3+ring))
mesh=bpy.data.meshes.new('Character | collar-to-jacket facing')
mesh.from_pydata(verts,[],faces);mesh.update()
mesh.materials.append(coat.data.materials[0])
for polygon in mesh.polygons:polygon.use_smooth=True
facing=bpy.data.objects.new('Character | collar-to-jacket facing',mesh)
scene.collection.objects.link(facing)
facing.matrix_world=coat.matrix_world.copy()
scene['collar_facing_fitted']=True
bm=bmesh.new();bm.from_mesh(mesh)
assert len([edge for edge in bm.edges if edge.is_boundary])==512
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges)
bm.free()

out=root
for label,place,target,lens,width,height in (
    ('Head_Rear',(-.90,-3.55,1.71),(-.75,-2.4,1.65),85,1000,1000),
    ('Head_Front',(-.75,-1.30,1.71),(-.75,-2.4,1.65),85,1000,1000),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100)):
    camera_data=bpy.data.cameras.new('Crop review '+label)
    camera=bpy.data.objects.new('Crop review '+label,camera_data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.lens=lens
    scene.camera=camera
    scene.cycles.samples=64
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Short_Crop_Collar_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.filepath=str(out/'Short_Crop_Collar_Gameplay.png')
bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Short_Crop_Collar_Candidate.blend'),compress=True)
print('ODDSWELL_SHORT_CROP_COLLAR_CANDIDATE_PASS',len(hair.data.splines),flush=True)
