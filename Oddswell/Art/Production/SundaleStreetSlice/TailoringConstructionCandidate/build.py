"""Study sewn side and fly construction on the saved walking shorts."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
source=out.parent/'LegAxisCandidate/LegAxis.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='EA9524588054A81A69D5C7FC4FDC7B956DFB318DC5D9BDA4C687E22F2CFB1C4C'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
world=pants.matrix_world
inverse=world.inverted()
thread=bpy.data.materials['Character | matching cotton topstitch'].copy()
thread.name='Character | warm shorts construction thread'
thread.diffuse_color=(.40,.38,.33,1)
thread.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=thread.diffuse_color

def source_vertex(index):return world@pants.data.vertices[index].co
def path_length(points):return sum((b-a).length for a,b in zip(points,points[1:]))
def sample_polyline(points,step):
    total=path_length(points)
    sample_count=max(2,round(total/step))
    lengths=[0.0]
    for a,b in zip(points,points[1:]):lengths.append(lengths[-1]+(b-a).length)
    result=[];segment=0
    for n in range(sample_count+1):
        distance=total*n/sample_count
        while segment<len(lengths)-2 and distance>lengths[segment+1]:segment+=1
        t=(distance-lengths[segment])/max(1e-9,lengths[segment+1]-lengths[segment])
        result.append(points[segment].lerp(points[segment+1],t))
    return result
def fitted(point):
    hit,normal,_,distance=surface.find_nearest(inverse@point)
    assert hit is not None and distance<.012,(point,distance)
    return hit+normal*.00075
def stitches(name,source_points,spacing=.0038):
    points=sample_polyline(source_points,spacing/2)
    points=[fitted(p) for p in points]
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D';data.bevel_depth=.00022;data.bevel_resolution=2
    data.materials.append(thread)
    count=0
    for i in range(0,len(points)-2,2):
        spline=data.splines.new('POLY');spline.points.add(1)
        for control,position in zip(spline.points,(points[i],points[i+1])):
            control.co=(*position,1)
        count+=1
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.matrix_world=world.copy()
    print('CONSTRUCTION_STITCHES',name,count,round(path_length(source_points),4),flush=True)
    return obj

for label,column,offset in (('left',40,1438),('right',0,4318)):
    upper=[source_vertex(row*80+column) for row in range(16,-1,-1)]
    leg=[source_vertex(offset+row*80+column) for row in range(35,-1,-1)]
    print('SIDE_JOIN',label,(leg[0]-upper[-1]).length,flush=True)
    assert (leg[0]-upper[-1]).length<.035
    stitches('Character | shorts sewn side seam '+label,upper+leg)

# A short J-shaped fly follows the front panel from the waist into the saddle.
fly=[]
for row in range(16,-1,-1):
    t=1-row/16
    column=20+2*t*t
    low=int(column);fraction=column-low
    fly.append(source_vertex(row*80+low).lerp(source_vertex(row*80+low+1),fraction))
stitches('Character | shorts sewn fly topstitch',fly)
scene['sewn_shorts_side_and_fly_stitches']=True

for label,place,target,lens in (
    ('Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52),
    ('Profile',(-1.65,-2.4,.82),(-.75,-2.4,.8),55),
):
    data=bpy.data.cameras.new('Tailoring '+label)
    camera=bpy.data.objects.new('Tailoring '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Tailoring_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'TailoringConstruction.blend'),compress=True)
print('TAILORING_CONSTRUCTION_SAVED',flush=True)
