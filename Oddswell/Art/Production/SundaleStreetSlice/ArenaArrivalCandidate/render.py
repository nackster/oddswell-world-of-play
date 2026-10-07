import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/LayeredPlantingCandidate/LayeredPlanting.blend'
for prefix,path in [('Before',source),('After',out/'ArenaArrival.blend')]:
    if '--after-only' in sys.argv and prefix=='Before':continue
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(7);prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU';scene.cycles.samples=48;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100
    d=bpy.data.cameras.new('Arrival paired review');camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera)
    for label,pos,target,lens,w,h in [('Arena',(3,43,2.1),(3,68,5.2),38,1600,1000),('Entrance',(3,55,2.4),(3,66,3.5),34,1280,900)]:
        scene.camera=camera;camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(out/(prefix+'_'+label+'.png'));bpy.ops.render.render(write_still=True);print('ARRIVAL_RENDER',prefix,label,flush=True)
    scene.camera=bpy.data.objects['CAM | gameplay street'];scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/(prefix+'_Gameplay.png'));bpy.ops.render.render(write_still=True);print('ARRIVAL_RENDER',prefix,'Gameplay',flush=True)
with (out/'ArenaArrival.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','frame':7,'matched_views':['Arena','Entrance','Gameplay'],'native_geometry':True},indent=2)+'\n')
