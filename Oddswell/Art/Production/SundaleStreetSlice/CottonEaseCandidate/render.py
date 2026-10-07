import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/PromenadeLightCandidate/PromenadeLight.blend'
views=[('RearNeutral',1,(-.95,-3.45,1.02),(-.75,-2.4,.83),58,1000,900),('RearWalking',13,(-.95,-3.45,1.02),(-.75,-2.4,.83),58,1000,900),('FrontWalking',13,(-.85,-1.30,1.03),(-.75,-2.4,.80),58,1000,900),('Full',13,(-3.65,-2.4,1.16),(-.75,-2.4,.92),50,760,840)]
for prefix,path in [('Before',source),('After',out/'CottonEase.blend')]:
    if '--after-only' in sys.argv and prefix=='Before':continue
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU';scene.cycles.samples=40;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100;d=bpy.data.cameras.new('Cotton paired review');camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera)
    for label,frame,pos,target,lens,w,h in views:
        scene.frame_set(frame);phi=(frame-1)/24;shift=Vector((.012*math.sin(2*math.pi*phi)-.009*(1-math.cos(2*math.pi*phi)),bpy.data.objects['Walk study | native anatomical controls']['root_stride_m']*phi,0));scene.camera=camera;camera.location=Vector(pos)+shift;camera.rotation_euler=(Vector(target)+shift-camera.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(out/(prefix+'_'+label+'.png'));bpy.ops.render.render(write_still=True);print('COTTON_EASE_RENDER',prefix,label,flush=True)
    scene.frame_set(7);scene.camera=bpy.data.objects['CAM | gameplay street'];scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/(prefix+'_Gameplay.png'));bpy.ops.render.render(write_still=True);print('COTTON_EASE_RENDER',prefix,'Gameplay',flush=True)
with (out/'CottonEase.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','matched_views':[v[0] for v in views]+['Gameplay'],'frames':[1,7,13],'native_geometry':True},indent=2)+'\n')
