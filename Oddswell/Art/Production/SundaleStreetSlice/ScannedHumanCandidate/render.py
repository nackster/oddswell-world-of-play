import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric';native=out/('ScannedHumanWalk.blend' if '--walk' in sys.argv else 'ScannedHumanScene.blend')
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;scene.frame_set(1);scene.cycles.device='CPU';scene.cycles.samples=12 if '--trial' in sys.argv else 40;scene.render.resolution_percentage=100;scene.render.use_persistent_data=True
# Study camera and isolated views are render-only changes.
flags={o:o.hide_render for o in scene.objects}
for o in scene.objects:
    if o.type not in ('LIGHT','CAMERA') and not o.name.startswith('Scan character | '):o.hide_render=True
d=bpy.data.cameras.new('Scanned character review');cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=[('Full',(-2.90,.40,1.28),(-.75,-2.4,.98),50,760,840),('Face',(-1.17,-1.32,1.71),(-.75,-2.4,1.65),75,900,900)]
for name,pos,target,lens,w,h in views:
    scene.frame_set(13 if '--walk' in sys.argv and name=='Full' else 1);shift=bpy.data.objects['Scan character | placement'].location-Vector((-.75,-2.4,0));shift.z=0
    cam.location=Vector(pos)+shift;cam.rotation_euler=(Vector(target)+shift-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('SCAN_RENDER',name,flush=True)
if '--preview' in sys.argv:
    (out/'Frames').mkdir(exist_ok=True);scene.cycles.samples=8;scene.render.resolution_x=640;scene.render.resolution_y=704;d.lens=50
    for frame in range(1,49,2):
        scene.frame_set(frame);shift=bpy.data.objects['Scan character | placement'].location-Vector((-.75,-2.4,0));shift.z=0;cam.location=Vector((-2.90,.40,1.28))+shift;cam.rotation_euler=(Vector((-.75,-2.4,.98))+shift-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/'Frames'/('%04d.png'%((frame-1)//2)));bpy.ops.render.render(write_still=True);print('SCAN_WALK_RENDER',frame,flush=True)
for o,hidden in flags.items():o.hide_render=hidden
if '--no-game' not in sys.argv:
    scene.frame_set(7);scene.camera=bpy.data.objects['CAM | gameplay street'];scene.cycles.samples=16;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.filepath=str(out/'Gameplay.png');bpy.ops.render.render(write_still=True);print('SCAN_RENDER Gameplay',flush=True)
with native.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'render-report.json').write_text(json.dumps({'candidate_sha256':sha,'renderer':'Blender 4.5.5 LTS / Cycles CPU','close_full_samples':12 if '--trial' in sys.argv else 40,'gameplay_samples':16,'actual_3d_mesh':True,'arguments':sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [],'poses':'Retargeted offline walk study' if '--walk' in sys.argv else 'Standing imported rig with relaxed upper arms','runtime_integrated':False},indent=2)+'\n',encoding='utf-8')
