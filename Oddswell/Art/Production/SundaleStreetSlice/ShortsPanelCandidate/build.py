"""Re-pattern the connected shorts and fit the ribbed waist junction."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

output=Path(__file__).resolve().parent
source=output.parent/'ShoeCanvasCandidate/ShoeCanvas.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='D2E19CB5416D9FF22B43291D1F7BAE1A704C1279513A0DC63EC986D15A723A33'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198
world=pants.matrix_world
inverse=world.inverted()

def interpolate(a,b,t):return a*(1-t)+b*t
def original_radii(t):
    upper=max(0.0,(t-.52)/.48)
    return interpolate(.215,.209,upper),interpolate(.132,.129,upper)
def pattern_radii(t):
    # Waist slopes into the anatomical pelvis; front and back remain
    # separately controlled panels instead of one oval circumference.
    if t<=.52:
        x=interpolate(.215,.207,t/.52)
        back=interpolate(.105,.097,t/.52)
    else:
        x=interpolate(.207,.198,(t-.52)/.48)
        back=interpolate(.097,.108,(t-.52)/.48)
    front=interpolate(.133,.131,t)
    return x,front,back

delta=[Vector((0,0,0)) for _ in range(1438)]
for k in range(17):
    t=k/16
    rx,ry=original_radii(t)
    target_x,front,back=pattern_radii(t)
    for j in range(80):
        a=j*math.tau/80
        ca,sa=math.cos(a),math.sin(a)
        new_y=(front if sa>=0 else back)*sa
        delta[k*80+j]=Vector(((target_x-rx)*ca,new_y-ry*sa,0))
for j in range(21,60):
    a=j*math.tau/80
    sa=math.sin(a)
    shift=((.133 if sa>=0 else .105)-.132)*sa
    for index in (1360+2*(j-21),1361+2*(j-21)):
        delta[index]=Vector((0,shift,0))

maximum=0.0
for i,change in enumerate(delta):
    vertex=pants.data.vertices[i]
    vertex.co=inverse@(world@vertex.co+change)
    maximum=max(maximum,change.length)

bridge_left={20:20,60:60}
bridge_right={20:20,60:60}
for j in range(21,60):
    bridge_left[j]=1360+2*(j-21)
    bridge_right[j]=1361+2*(j-21)
for side,offset in ((-1,1438),(1,4318)):
    top=[]
    for j in range(80):
        outer=(20<=j<=60) if side<0 else (j<=20 or j>=60)
        top.append(j if outer else bridge_left[(40-j)%80] if side<0 else bridge_right[j])
    for k in range(36):
        t=k/36
        weight=t**3
        for j in range(80):
            change=delta[top[j]]*weight
            vertex=pants.data.vertices[offset+k*80+j]
            vertex.co=inverse@(world@vertex.co+change)
            maximum=max(maximum,change.length)
pants.data.update()
bpy.context.view_layer.update()
print('SHORTS_PANEL_PATTERN',len(pants.data.vertices),maximum,flush=True)

# Pocket curves follow the modified rear panels rather than retaining their
# old 3-D positions in the air.
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
stitched=0
for seam in scene.objects:
    if seam.type!='CURVE' or not seam.name.startswith('Character | back pocket seam'):continue
    transform=pants.matrix_world.inverted()@seam.matrix_world
    back=transform.inverted()
    for spline in seam.data.splines:
        for point in spline.points:
            prior=transform@Vector(point.co[:3])
            hit,normal,_,_=surface.ray_cast(Vector((prior.x,-3.0,prior.z)),Vector((0,1,0)),2)
            assert hit is not None and normal.y<-.1
            point.co=(*(back@(hit+normal*.0013)),point.co.w)
            stitched+=1
print('SHORTS_PATTERN_STITCHES',stitched,flush=True)
scene['shorts_panel_pattern_maximum_shift_m']=maximum

# The original ribbed band protrudes after the seat is re-patterned. Grade
# its lower edge into the shorts while keeping its upper edge under the
# jacket hem, rather than making a floating dark strip at the waist.
band=bpy.data.objects['Character | ribbed waistband']
band_world=band.matrix_world;band_inverse=band_world.inverted()
def smooth(t):
    t=max(0.0,min(1.0,t))
    return t*t*(3-2*t)
band_maximum=0.0
for vertex in band.data.vertices:
    p=band_world@vertex.co
    low=1-smooth((p.z-.874)/.045)
    rear=smooth((-p.y-2.38)/.11)
    side=smooth((abs(p.x+.75)-.13)/.08)
    old=p.copy()
    p.y+=rear*(.003+.023*low)
    p.x-=math.copysign(1,p.x+.75)*side*(.002+.004*low)
    vertex.co=band_inverse@p
    band_maximum=max(band_maximum,(p-old).length)
band.data.update()
scene['shorts_waist_junction_maximum_shift_m']=band_maximum
print('SHORTS_WAIST_JUNCTION',band_maximum,flush=True)

if '--render' in sys.argv:
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.75,-3.55,.82),(-.75,-2.4,.8),52,900,900),
        ('Front_Close',(-.75,-1.25,.82),(-.75,-2.4,.8),52,900,900),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ):
        data=bpy.data.cameras.new('Shorts pattern '+label)
        camera=bpy.data.objects.new('Shorts pattern '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=20
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Shorts_Panel_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'ShortsPanel.blend'),compress=True)
print('SHORTS_PANEL_CANDIDATE_PASS',flush=True)
