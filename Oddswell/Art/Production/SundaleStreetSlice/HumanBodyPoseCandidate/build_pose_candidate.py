"""Build an editable posed character candidate without changing the retained source."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'OddsWell_Sundale_StreetSlice.blend'
SOURCE_SHA256='0F3988395DBE747A66738D9D7BA1D86A14D2531FCF2A5592C471A01B3AFC6127'
with SOURCE.open('rb') as source_file:
    assert hashlib.file_digest(source_file,'sha256').hexdigest().upper()==SOURCE_SHA256
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
center=Vector((-.75,-2.4,0))
excluded=('anatomical legs','shorts leg','back pocket seam','fine calf hair',
          'canvas sneaker','sneaker sole','shoe lace','outsole groove',
          'foxing edge')

def smooth(t):
    t=max(0.,min(1.,t))
    return t*t*(3.-2.*t)

def warp(p):
    p=Vector(p)
    s=smooth((p.z-.90)/.38)
    theta=math.radians(3.5)*s
    dx=p.x-center.x
    dy=p.y-center.y
    shoulder_taper=smooth((abs(dx)-.15)/.18)*smooth((p.z-.94)/.36)
    x=center.x+dx*math.cos(theta)-dy*math.sin(theta)+.025*s-math.copysign(.028*shoulder_taper,dx)
    y=center.y+dx*math.sin(theta)+dy*math.cos(theta)+.050*s
    # Contralateral arm swing, feathered through the raglan shoulder.
    arm=smooth((abs(dx)-.17)/.16)*smooth((1.49-p.z)/.51)
    y-=math.copysign(.075*arm,dx)
    outer_shoulder=smooth((abs(dx)-.16)/.17)*smooth((p.z-1.28)/.18)
    return Vector((x,y,p.z-.018*outer_shoulder))

changed=0
for ob in scene.objects:
    if not ob.name.startswith('Character | ') or ob.type not in {'MESH','CURVE'}:
        continue
    if ob.name.startswith(tuple('Character | '+name for name in excluded)):
        continue
    if ob.type=='MESH':
        me=ob.data
        if me.shape_keys:
            basis=me.shape_keys.key_blocks[0]
            for key in me.shape_keys.key_blocks:
                for vert in key.data:
                    vert.co=warp(vert.co)
            for vert,keyvert in zip(me.vertices,basis.data):
                vert.co=keyvert.co
        else:
            for vert in me.vertices:
                vert.co=warp(vert.co)
        for name in ('Tailored rest','Collision fit','Gravity result'):
            attr=me.attributes.get(name)
            if attr:
                for datum in attr.data:
                    datum.vector=warp(datum.vector)
        me.update()
    else:
        for spline in ob.data.splines:
            if spline.type=='BEZIER':
                for point in spline.bezier_points:
                    point.co=warp(point.co)
                    point.handle_left=warp(point.handle_left)
                    point.handle_right=warp(point.handle_right)
            else:
                for point in spline.points:
                    point.co=(*warp(point.co[:3]),point.co.w)
    changed+=1

scene['upper_body_weight_shift_study']=True
scene['upper_body_shifted_objects']=changed
scene['upper_body_forward_lean_m']=.050
scene['upper_body_stance_lean_m']=.025
scene['upper_body_yaw_deg']=3.5
scene['upper_body_arm_swing_m']=.075
scene['upper_body_shoulder_taper_m']=.028
scene['upper_body_outer_shoulder_drop_m']=.018
scene['pose_source_sha256']=SOURCE_SHA256
coat=bpy.data.objects['Character | tailored slate jacket']
fit=coat.data.attributes['Collision fit'].data
gravity=coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m']=max((g.vector-f.vector).length for g,f in zip(gravity,fit))
bpy.context.view_layer.update()
main_camera=scene.camera
for name,position,target,lens,width,height in [
    ('Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
    ('Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100),
]:
    camera_data=bpy.data.cameras.new('Study | '+name)
    camera=bpy.data.objects.new('Study | '+name,camera_data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.lens=lens
    scene.camera=camera
    scene.render.engine='CYCLES'
    scene.cycles.samples=64
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(ROOT/('OddsWell_Body_Pose_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_BODY_POSE_RENDER',name,flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=main_camera
scene.render.filepath=str(ROOT/'OddsWell_Body_Pose_Rear.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'OddsWell_Human_Body_Pose_Candidate.blend'),compress=True)
print('ODDSWELL_BODY_POSE_CANDIDATE_PASS',changed,flush=True)
