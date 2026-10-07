import bpy,json,hashlib
import sys
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/RetailDepthCandidate/RetailDepth.blend'
for prefix,path in [('Before',source),('After',out/'LayeredPlanting.blend')]:
    if '--after-only' in sys.argv and prefix=='Before':continue
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(7);prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU';scene.cycles.samples=40;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100
    original=scene.camera;d=bpy.data.cameras.new('Planting paired review');camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera)
    for label,pos,target,lens in [('Planter',(-.4,-.6,1.8),(1.3,3,1.09),54),('TreeBase',(-.1,3.2,1.3),(-2.4,7.5,.48),48)]:
        scene.camera=camera;camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.filepath=str(out/(prefix+'_'+label+'.png'));bpy.ops.render.render(write_still=True);print('PLANTING_RENDER',prefix,label,flush=True)
    scene.camera=bpy.data.objects['CAM | gameplay street'];scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/(prefix+'_Gameplay.png'));bpy.ops.render.render(write_still=True);print('PLANTING_RENDER',prefix,'Gameplay',flush=True)
with (out/'LayeredPlanting.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','frame':7,'matched_views':['Planter','TreeBase','Gameplay'],'native_geometry':True},indent=2)+'\n')
