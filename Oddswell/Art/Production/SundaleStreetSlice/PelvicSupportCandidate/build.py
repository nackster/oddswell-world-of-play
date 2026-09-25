"""Add a hidden source-derived pelvic fitting support to the saved walk pose."""
import bpy
import bmesh
import hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
root=Path(__file__).resolve().parents[5]
source= root/'Oddswell/Art/Production/SundaleStreetSlice/SignalJoinCandidate/SignalJoin.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='440A054D60821E8978AEFC6BB863624766C3FDE0A73CB30D691DD79DDAA4C8C8'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
obj_path=root/'Oddswell/Art/Production/SundaleStreetSlice/source-assets/makehuman-base.obj'
raw=[];faces=[];group=''
for line in obj_path.read_text(encoding='utf-8').splitlines():
    parts=line.split()
    if not parts:continue
    if parts[0]=='v':raw.append(Vector(tuple(map(float,parts[1:4]))))
    elif parts[0]=='g':group=parts[1]
    elif parts[0]=='f' and group=='body':faces.append([int(word.split('/')[0])-1 for word in parts[1:]])
used={i for face in faces for i in face}
low=min(raw[i].y for i in used)
unit=1.8/(max(raw[i].y for i in used)-low)
converted=[Vector((v.x*unit,v.z*unit,(v.y-low)*unit)) for v in raw]
origin=Vector((-.75,-2.4,.06+scene['character_ground_offset']))

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def walk(relative):
    side=1 if relative.x>0 else -1
    legy=.075 if side>0 else -.065
    ankle=Vector((side*.14,legy+.015,.14))
    knee=Vector((side*.14,legy+.035,.48))
    hip=Vector((side*.13,0,.9))
    a=(-.04 if side>0 else .20)*min(1,max(0,(.29-relative.z)/.07))
    b=(-.09 if side>0 else -.30)*min(1,max(0,(.53-relative.z)/.10))
    c=(.13 if side>0 else -.16)*min(1,max(0,(.95-relative.z)/.20))
    point=ankle+Matrix.Rotation(a,3,'X')@(relative-ankle)
    point=knee+Matrix.Rotation(b,3,'X')@(point-knee)
    point=hip+Matrix.Rotation(c,3,'X')@(point-hip)
    if side<0:point.z+=.013*min(1,max(0,(.95-relative.z)/.20))
    return point

selection=[face for face in faces if all(.64<converted[i].z<.97 for i in face)]
ids=sorted({i for face in selection for i in face})
index={source_id:local for local,source_id in enumerate(ids)}
points=[walk(converted[i])+origin for i in ids]
for point in points:
    side=1 if point.x>-.75 else -1
    point.x-=side*.04*(1-smooth((point.z-.70)/.10))
    point.y+=side*.07*(1-smooth((point.z-.70)/.16))
    if side>0:
        weight=1-smooth((point.z-.70)/.14)
        target_y=-2.29075+(point.y+2.27105)*.62
        point.y+=(target_y-point.y)*weight

legs=bpy.data.objects['Character | anatomical legs']
evaluated=legs.evaluated_get(bpy.context.evaluated_depsgraph_get())
leg_mesh=evaluated.to_mesh();leg_mesh.calc_loop_triangles()
leg_points=[legs.matrix_world@vertex.co for vertex in leg_mesh.vertices]
halves={-1:[],1:[]}
for triangle in leg_mesh.loop_triangles:
    face=tuple(triangle.vertices)
    xs=[leg_points[i].x for i in face]
    if max(xs)<-.75:halves[-1].append(face)
    elif min(xs)>-.75:halves[1].append(face)
assert all(halves.values())
leg_trees={side:BVHTree.FromPolygons(leg_points,faces,all_triangles=True) for side,faces in halves.items()}
lower_aligned=0;lower_maximum=0
for point in points:
    if point.z>=.78:continue
    side=1 if point.x>-.75 else -1
    hit,normal,_,distance=leg_trees[side].find_nearest(point)
    if hit is None:continue
    weight=1-smooth((point.z-.68)/.10)
    shift=Vector(((hit.x-point.x)*weight,(hit.y-point.y)*weight,0))
    point+=shift
    lower_maximum=max(lower_maximum,shift.length);lower_aligned+=1
evaluated.to_mesh_clear()

torso=bpy.data.objects['Character | internal torso support']
bpy.context.view_layer.update()
tree=BVHTree.FromObject(torso,bpy.context.evaluated_depsgraph_get())
inverse=torso.matrix_world.inverted()
maximum=0;aligned=0
for point in points:
    if point.z<=.82:continue
    center=Vector((-.75,-2.4,point.z))
    direction=Vector((point.x-center.x,point.y-center.y,0))
    if direction.length<1e-5:continue
    hit,normal,_,distance=tree.ray_cast(inverse@center,(inverse.to_3x3()@direction).normalized())
    if hit is None:continue
    target=torso.matrix_world@hit
    weight=smooth((point.z-.82)/.10)
    shift=(Vector((target.x,target.y,point.z))-point)*weight
    point+=shift
    maximum=max(maximum,shift.length);aligned+=1
assert aligned>100

mesh=bpy.data.meshes.new('Source-derived pelvic fitting support')
mesh.from_pydata(points,[],[[index[i] for i in reversed(face)] for face in selection])
mesh.update()
attribute=mesh.attributes.new(name='MakeHuman source vertex',type='INT',domain='POINT')
for local,source_id in enumerate(ids):attribute.data[local].value=source_id
support=bpy.data.objects.new('Character | posed pelvic fitting support',mesh)
scene.collection.objects.link(support)
support.hide_render=True;support.display_type='WIRE'
support['source']='source-assets/makehuman-base.obj'
support['license']='source-assets/MAKEHUMAN-LICENSE.ASSETS.md'
support['purpose']='Offline shorts fit reference; not visible skin or runtime anatomy'
support['registration']='Walking upper-thigh shifts plus radial fit to internal torso support'
for polygon in mesh.polygons:polygon.use_smooth=True
sub=support.modifiers.new('Smooth pelvic fitting surface','SUBSURF');sub.levels=2
bm=bmesh.new();bm.from_mesh(mesh)
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges)
components=[];unseen=set(bm.verts)
while unseen:
    seed=unseen.pop();pending=[seed];count=1
    while pending:
        vertex=pending.pop()
        for edge in vertex.link_edges:
            other=edge.other_vert(vertex)
            if other in unseen:unseen.remove(other);pending.append(other);count+=1
    components.append(count)
boundaries=sum(edge.is_boundary for edge in bm.edges)
bm.free()
print('PELVIC_SUPPORT',len(points),len(selection),'components',components,'boundary_edges',boundaries,'upper_aligned',aligned,'max_upper_registration_m',round(maximum,5),'lower_aligned',lower_aligned,'max_lower_registration_m',round(lower_maximum,5),flush=True)
assert len(components)==1
scene['pelvic_fitting_support']='source-derived diagnostic only'
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'PelvicSupport.blend'),compress=True)
print('PELVIC_SUPPORT_STUDY_SAVED',flush=True)
