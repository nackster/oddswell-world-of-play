"""Widen the retained paired gusset and blend it through the leg transition."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'PanelBalanceCandidate'/'PanelBalance.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='A4790ADF03B98752780F2002B4033BFDF09282849C8D5D0ADD4E2D4BAF458EB2'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198
world,inverse=pants.matrix_world,pants.matrix_world.inverted()

changes={}
for j in range(21,60):
    arc=math.sin(math.pi*(j-20)/40)
    extra=.015*arc**1.2
    for index,sign in ((1360+2*(j-21),-1),(1361+2*(j-21),1)):
        change=Vector((sign*extra,0,0))
        vertex=pants.data.vertices[index]
        vertex.co=inverse@(world@vertex.co+change)
        changes[index]=change

left={j:1360+2*(j-21) for j in range(21,60)}
right={j:1361+2*(j-21) for j in range(21,60)}
for side,offset,bridge in ((-1,1438,left),(1,4318,right)):
    for k in range(36):
        weight=(k/36)**6
        for j in range(80):
            outer=(20<=j<=60) if side<0 else (j<=20 or j>=60)
            if outer:continue
            station=(40-j)%80 if side<0 else j
            change=changes[bridge[station]]*weight
            vertex=pants.data.vertices[offset+k*80+j]
            vertex.co=inverse@(world@vertex.co+change)
widths=[]
for j in range(21,60):
    a=world@pants.data.vertices[left[j]].co
    b=world@pants.data.vertices[right[j]].co
    widths.append((b-a).length)
assert .045<max(widths)<.055,max(widths)
pants.data.update()
scene['shorts_gusset_widening_max_m']=.015
scene['shorts_gusset_actual_width_max_m']=max(widths)
print('GUSSET_WIDTH',min(widths),max(widths),flush=True)

for label,place,target,lens,width,height in (
    ('Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52,900,900),
    ('Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52,900,900),
    ('Profile',(-1.65,-2.4,.82),(-.75,-2.4,.8),55,900,900),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
):
    if '--quick' in sys.argv and label not in ('Front','Rear'):continue
    data=bpy.data.cameras.new('Gusset width '+label)
    camera=bpy.data.objects.new('Gusset width '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(root/('Gusset_Width_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'GussetWidth.blend'),compress=True)
print('GUSSET_WIDTH_CANDIDATE_PASS',flush=True)
