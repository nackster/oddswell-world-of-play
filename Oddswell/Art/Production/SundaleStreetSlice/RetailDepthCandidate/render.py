import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());offset=Vector(json.loads((out/'build-report.json').read_text())['layout_offset_m'])
for prefix,path in [('Before',root/'Oddswell/Art/Production/SundaleStreetSlice/ShoulderChestCandidate/ShoulderChest.blend'),('After',out/'RetailDepth.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.frame_set(1);prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU';scene.cycles.samples=32;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100
    data=bpy.data.cameras.new('Retail paired review');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
    for label,pos,target,lens in [('Storefront',(-2.8,-6.9,1.65),(-7.1,-1.0,1.55),42),('Interior',(-4.3,.9625,1.65),(-9.2,.9625,1.55),28)]:
        camera.location=Vector(pos)+offset;camera.rotation_euler=(Vector(target)+offset-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;scene.render.resolution_x=1280;scene.render.resolution_y=900;scene.render.filepath=str(out/(prefix+'_'+label+'.png'));bpy.ops.render.render(write_still=True);print('RETAIL_FINAL_RENDER',prefix,label,flush=True)
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(7);scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/'Gameplay.png');bpy.ops.render.render(write_still=True)
with (out/'RetailDepth.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','candidate_views':['After_Storefront','After_Interior','Gameplay'],'source_views':['Before_Storefront','Before_Interior'],'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'geometry':'Native meshes, curves, text and retained licensed textures; no generated image background'},indent=2)+'\n');print('RETAIL_FINAL_VIEWS_DONE',flush=True)
