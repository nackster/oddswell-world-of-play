"""Build the rear-seat and upper-thigh cotton drape candidate."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
source=root.parent/'OddsWell_Short_Crop_Collar_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='B0210791690C82BFF6A67BE271F4BBFDEC2616FCE199C4237F75A1067938AD22'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
mesh=pants.data
before=[vertex.co.copy() for vertex in mesh.vertices]

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

for vertex in mesh.vertices:
    p=vertex.co.copy();x=p.x+.75;z=p.z
    rear=smooth((-2.39-p.y)/.09)
    seat=.006*math.exp(-((abs(x)-.11)/.09)**2-((z-.845)/.065)**2)
    right_line=.72+.20*x
    right=.012*math.exp(-((x-.12)/.105)**2-((z-right_line)/.013)**2)
    left_line=.73-.17*x
    left=.008*math.exp(-((x+.12)/.105)**2-((z-left_line)/.015)**2)
    hem_guard=smooth((z-.675)/.045)
    vertex.co.y-=rear*hem_guard*(seat+right+left)
mesh.update()
bpy.context.view_layer.update()
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for obj in scene.objects:
    if obj.type!='CURVE' or not obj.name.startswith('Character | back pocket seam'):
        continue
    for spline in obj.data.splines:
        for point in spline.points:
            prior=Vector(point.co[:3])
            hit,normal,_,distance=surface.ray_cast(prior+Vector((0,-.05,0)),Vector((0,1,0)),.12)
            assert hit is not None and normal.y<-.1
            point.co=(*(hit+normal*.0012),1)
scene['seat_drape_candidate']=True
scene['seat_drape_maximum_control_shift_m']=max((a-b.co).length for a,b in zip(before,mesh.vertices))
print('SEAT_DRAPE_SHIFT',scene['seat_drape_maximum_control_shift_m'],flush=True)

out=root
for label,place,target,lens,width,height in (
    ('Shorts_Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52,1000,1000),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100)):
    data=bpy.data.cameras.new('Seat drape '+label)
    camera=bpy.data.objects.new('Seat drape '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.cycles.samples=64
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Seat_Drape_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.filepath=str(out/'Seat_Drape_Gameplay.png')
bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Seat_Drape_Candidate.blend'),compress=True)
print('ODDSWELL_SEAT_DRAPE_CANDIDATE_PASS',flush=True)
