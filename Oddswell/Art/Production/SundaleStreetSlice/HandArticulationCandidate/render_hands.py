"""Native hand/cuff close-ups at opposing articulated walking poses."""
import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HandMotion.blend'))
scene=bpy.context.scene;rig=bpy.data.objects['Walk study | native anatomical controls']
report=json.loads((out/'build-report.json').read_text())
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU';scene.cycles.samples=20;scene.render.use_persistent_data=True
data=bpy.data.cameras.new('Articulated hand review');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
for label,frame,side,pos,target in [
    ('Left_Rear_Contact',1,'pos',(-.52,-3.25,.84),(-.49,-2.48,.81)),
    ('Left_Rear_Opposite',13,'pos',(-.52,-3.25,.84),(-.49,-2.48,.81)),
    ('Left_Front_Opposite',13,'pos',(-.49,-1.65,.84),(-.49,-2.48,.81)),
    ('Right_Outer_Contact',1,'neg',(-1.72,-2.13,.88),(-.98,-2.15,.87)),
    ('Right_Outer_Opposite',13,'neg',(-1.72,-2.13,.88),(-.98,-2.15,.87))]:
    scene.frame_set(frame);bpy.context.view_layer.update()
    shift=(rig.matrix_world@rig.pose.bones[side+'.palm'].head)-Vector(report['posed_landmarks'][side]['wrist'])
    camera.location=Vector(pos)+shift;camera.rotation_euler=(Vector(target)+shift-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=75
    scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    print('HAND_RENDER',label,flush=True)
