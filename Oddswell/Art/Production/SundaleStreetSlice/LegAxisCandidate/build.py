"""Align the shorts leg openings with the retained exposed walking thighs."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=Path(__file__).resolve().parents[5]/'Oddswell/Art/Production/SundaleStreetSlice/GussetWidthCandidate/GussetWidth.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='C9420581B4DFDF22E4E2D398F38A6A9C186AFF92D02D71BF31352E2B70B77554'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198

shifts={'left':Vector((-.004,-.002,0)),'right':Vector((.010,.034,0))}
def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)
def shift(point,side):
    return shifts[side]*(1-smooth((point.z-.715)/.085))
def move_vertex(obj,vertex,side):
    world=obj.matrix_world@vertex.co
    vertex.co=obj.matrix_world.inverted()@(world+shift(world,side))

for side,offset in (('left',1438),('right',4318)):
    for vertex in pants.data.vertices[offset:offset+36*80]:
        move_vertex(pants,vertex,side)
pants.data.update()

facing=bpy.data.objects['Character | folded cotton leg hem facings']
assert len(facing.data.vertices)==1600
for side,offset in (('left',0),('right',800)):
    for vertex in facing.data.vertices[offset:offset+800]:move_vertex(facing,vertex,side)
facing.data.update()
for side in ('left','right'):
    for prefix in ('Character | shorts leg hem','Character | sewn folded hem '):
        for obj in scene.objects:
            if obj.type!='CURVE' or not obj.name.startswith(prefix):continue
            tail=obj.name[len(prefix):].strip()
            if tail!=side and not tail.startswith(side+'.'):continue
            inverse=obj.matrix_world.inverted()
            for spline in obj.data.splines:
                for point in spline.points:
                    world=obj.matrix_world@Vector(point.co[:3])
                    point.co=(*(inverse@(world+shift(world,side))),point.co.w)

for side,offset in (('left',1438),('right',4318)):
    points=[pants.matrix_world@pants.data.vertices[offset+j].co for j in range(80)]
    center=sum(points,Vector())/len(points)
    print('LEG_AXIS_HEM_CENTER',side,tuple(round(v,4) for v in center),flush=True)
scene['walk_shorts_leg_axis_alignment_m']=.034

for label,place,target,lens in (
    ('Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52),
    ('Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52),
):
    data=bpy.data.cameras.new('Leg-axis '+label)
    camera=bpy.data.objects.new('Leg-axis '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Leg_Axis_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'LegAxis.blend'),compress=True)
print('LEG_AXIS_CANDIDATE_SAVED',flush=True)
