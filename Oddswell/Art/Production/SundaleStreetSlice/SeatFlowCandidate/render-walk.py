"""Render actual articulated native geometry, with a following review camera."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'SeatFlow.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Walk study | native anatomical controls']
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU';scene.cycles.samples=12
scene.render.use_persistent_data=True
scene.render.resolution_percentage=100
data=bpy.data.cameras.new('Native walk review');camera=bpy.data.objects.new('Native walk review',data)
scene.collection.objects.link(camera);scene.camera=camera
def render(label,frame,position,target,lens,width,height):
    scene.frame_set(frame)
    phi=(frame-1)/24
    shift=Vector((.012*math.sin(2*math.pi*phi)-.009*(1-math.cos(2*math.pi*phi)),rig['root_stride_m']*phi,0))
    camera.location=Vector(position)+shift
    camera.rotation_euler=(Vector(target)+shift-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    print('WALK_RENDER',label,frame,flush=True)
if '--preview' in sys.argv:
    (out/'Frames').mkdir(exist_ok=True)
    scene.cycles.samples=8
    for frame in range(1,49,2):
        render('Frames/%04d'%((frame-1)//2),frame,(-2.65,-5.35,1.28),(-.73,-2.40,.98),52,640,704)
else:
    for frame,label in [(1,'Contact'),(7,'Passing'),(13,'OppositeContact')]:
        render(label+'_Profile',frame,(-3.35,-2.4,1.20),(-.75,-2.4,.97),50,760,840)
    render('Passing_Rear',7,(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,760,840)
    render('Passing_Front',7,(-.75,.4,1.20),(-.75,-2.4,.97),50,760,840)
    render('Torso_Front',13,(-.85,-.80,1.23),(-.80,-2.4,1.20),65,840,840)
    render('Hips_Rear',13,(-1.10,-4.1,1.12),(-.76,-2.4,.91),65,840,840)
    gameplay=bpy.data.objects['CAM | gameplay street'];scene.camera=gameplay;scene.frame_set(7)
    scene.cycles.samples=16;scene.render.resolution_x=1280;scene.render.resolution_y=720
    scene.render.filepath=str(out/'Gameplay.png');bpy.ops.render.render(write_still=True)
