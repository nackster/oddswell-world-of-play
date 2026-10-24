"""Build the connected jacket's localized back and elbow cloth-ease candidate."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
source=root.parent/'OddsWell_Seat_Drape_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='333A90FA9F860B636477A5D0BBEA41C332A9524D3A34FE27879B22BF1A1FE9C1'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
body=bpy.data.objects['Character | internal torso support']
body.hide_set(False);body.hide_viewport=False
for modifier in list(coat.modifiers):
    if modifier.type in {'SUBSURF','SOLIDIFY'}:coat.modifiers.remove(modifier)
before=[v.co.copy() for v in coat.data.vertices]

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

ease=coat.vertex_groups.new(name='Back and elbow pattern ease')
for v in coat.data.vertices:
    p=v.co;x=p.x+.75;z=(coat.matrix_world@p).z
    rear=smooth((-2.39-p.y)/.08)
    torso=(1-smooth((abs(x)-.13)/.12))*smooth((z-1.065)/.05)*(1-smooth((z-1.30)/.06))
    elbow=smooth((abs(x)-.26)/.07)*math.exp(-((z-1.16)/.09)**2)
    value=max(rear*torso,elbow)
    if value>0.001:ease.add([v.index],value,'REPLACE')
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[next((g.weight for g in v.groups if g.group==pin.index),0) for v in coat.data.vertices]

bpy.context.view_layer.objects.active=coat
cloth=coat.modifiers.new('Local pattern ease study','CLOTH')
s=cloth.settings;s.quality=10;s.mass=.22;s.air_damping=5
s.tension_stiffness=40;s.compression_stiffness=30;s.shear_stiffness=15;s.bending_stiffness=2
s.vertex_group_mass=pin.name;s.pin_stiffness=1
s.vertex_group_shrink=ease.name;s.shrink_min=-.06;s.shrink_max=0
c=cloth.collision_settings;c.use_collision=True;c.distance_min=.003
c.use_self_collision=True;c.self_distance_min=.003;c.collision_quality=4
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=60
for frame in range(1,61):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if frame%10==0:print('EASE_FRAME',frame,flush=True)
bpy.ops.object.modifier_apply(modifier=cloth.name)
simulated=[v.co.copy() for v in coat.data.vertices]
assert len(simulated)==len(before)
print('EASE_RAW_MAX',max((a-b).length for a,b in zip(before,simulated)),flush=True)
delta=[v-r for v,r in zip(simulated,before)]
neighbors=[[] for _ in before]
for edge in coat.data.edges:
    a,b=edge.vertices;neighbors[a].append(b);neighbors[b].append(a)
for _ in range(4):
    delta=[d.lerp(sum((delta[j] for j in ns),Vector())/len(ns),.50) if ns else d for d,ns in zip(delta,neighbors)]
support=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
for v,r,d,w in zip(coat.data.vertices,before,delta,weights):
    v.co=r+d*(1-w)
    hit,normal,_,_=support.find_nearest(v.co)
    if w<.80 and (v.co-hit).dot(normal)<.006:v.co=hit+normal*.006
coat.data.update()
body.hide_set(True)
coat.modifiers.new('Smooth garment surface','SUBSURF').levels=1
solid=coat.modifiers.new('Actual fabric thickness','SOLIDIFY');solid.thickness=.0012;solid.offset=-1
original=Path('Oddswell/Art/Production/SundaleStreetSlice/settle_jacket.py').read_text(encoding='utf-8')
exec(compile(original[:original.rfind('\nsettle_jacket()')], 'settle_jacket.py', 'exec'))
fit_jacket_seams();fit_jacket_fastening()
for obj in scene.objects:
    if obj.name.startswith('Character | yoke topstitch '):
        obj.hide_render=True;obj.hide_set(True)
scene['jacket_local_pattern_ease']=-.06
scene['jacket_ease_candidate']=True
scene.frame_set(1)
print('EASE_FINAL_MAX',max((a-v.co).length for a,v in zip(before,coat.data.vertices)),flush=True)

out=root
for label,place,target,lens,width,height in (
    ('Back_Close',(-.75,-4.5,1.30),(-.75,-2.4,1.21),55,900,1000),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100)):
    data=bpy.data.cameras.new('Ease study '+label)
    camera=bpy.data.objects.new('Ease study '+label,data);scene.collection.objects.link(camera)
    camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera;scene.cycles.samples=64
    scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Jacket_Ease_'+label+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64;scene.render.resolution_x=1600;scene.render.resolution_y=900
scene.render.filepath=str(out/'Jacket_Ease_Gameplay.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Jacket_Ease_Candidate.blend'),compress=True)
print('ODDSWELL_JACKET_EASE_CANDIDATE_PASS',flush=True)
