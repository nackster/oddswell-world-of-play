"""Study a longer cotton short with the saved walking leg axes and sewn hems."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=out.parent/'WeightBalanceCandidate/WeightBalance.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='31ED385743603A1ECCADD0DEC422A0DEDE0E2EE2E2F977AAB311D4EED1C525AF'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
facings=bpy.data.objects['Character | folded cotton leg hem facings']
assert len(pants.data.vertices)==7198 and len(facings.data.vertices)==1600

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)
def weight(z):return 1-smooth((z-.69)/.11)
centers={'left':Vector((-.877461,-2.465741,0)),
         'right':Vector((-.622966,-2.291251,0))}
shifts={'left':Vector((.003,-.010,0)),
        'right':Vector((-.010,-.007,0))}
def reshape(p,side):
    w=weight(p.z)
    pivot=centers[side]
    transverse=Vector((p.x-pivot.x,p.y-pivot.y,0))
    return p+shifts[side]*w+transverse*.02*w-Vector((0,0,.050*w))
def move_mesh(obj,vertices,side):
    world=obj.matrix_world;inverse=world.inverted()
    for vertex in vertices:
        p=world@vertex.co
        vertex.co=inverse@reshape(p,side)
    obj.data.update()

for side,offset in (('left',1438),('right',4318)):
    move_mesh(pants,pants.data.vertices[offset:offset+36*80],side)
for side,offset in (('left',0),('right',800)):
    move_mesh(facings,facings.data.vertices[offset:offset+800],side)

for side in ('left','right'):
    for prefix in ('Character | shorts leg hem','Character | sewn folded hem '):
        for obj in scene.objects:
            if obj.type!='CURVE' or not obj.name.startswith(prefix):continue
            tail=obj.name[len(prefix):].strip()
            if tail!=side and not tail.startswith(side+'.'):continue
            world=obj.matrix_world;inverse=world.inverted()
            for spline in obj.data.splines:
                for point in spline.points:
                    old=world@Vector(point.co[:3])
                    point.co=(*(inverse@reshape(old,side)),point.co.w)

for side,offset in (('left',1438),('right',4318)):
    points=[pants.matrix_world@pants.data.vertices[offset+j].co for j in range(80)]
    center=sum(points,Vector())/80
    print('LONGER_SHORTS_HEM',side,tuple(round(v,4) for v in center),flush=True)
scene['shorts_lower_leg_extension_m']=.05
for label,place,target,lens,height in (
    ('Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52,900),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,990),
    ('Full_Front',(-1.45,1.05,1.25),(-.75,-2.4,.97),58,990),
):
    data=bpy.data.cameras.new('Longer shorts '+label)
    camera=bpy.data.objects.new('Longer shorts '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Longer_Shorts_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.render.resolution_x=1200;scene.render.resolution_y=675
scene.render.filepath=str(out/'Longer_Shorts_Gameplay.png')
bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'LongerShorts.blend'),compress=True)
print('LONGER_SHORTS_STUDY_SAVED',flush=True)
