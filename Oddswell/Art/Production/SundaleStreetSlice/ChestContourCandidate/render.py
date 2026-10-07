import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/TorsoSilhouetteCandidate/TorsoSilhouette.blend'
views=[('SideTorso',13,(-2.55,-2.4,1.26),(-.75,-2.4,1.25),70,1000,900),('FrontTorso',13,(-.85,-.95,1.28),(-.75,-2.4,1.23),58,1000,900),('RearTorso',1,(-.95,-3.85,1.26),(-.75,-2.4,1.25),58,1000,900),('Full',13,(-3.65,-2.4,1.16),(-.75,-2.4,.92),50,760,840)]
if '--body' in sys.argv:views=views[:2]
for prefix,path in [('Before',source),('After',out/'ChestContour.blend')]:
    if '--after-only' in sys.argv and prefix=='Before':continue
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    if '--body' in sys.argv:
        prefix+='Body';bpy.data.objects['Character | tailored slate jacket'].hide_render=True;body=bpy.data.objects['Character | internal torso support'];body.hide_render=False;body.data=body.data.copy();mat=bpy.data.materials.new('Temporary anatomy diagnostic clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.18,.11,1);bs.inputs['Roughness'].default_value=.8;body.data.materials.clear();body.data.materials.append(mat)
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU';scene.cycles.samples=40;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100;d=bpy.data.cameras.new('Torso silhouette paired review');camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera)
    for label,frame,pos,target,lens,w,h in views:
        scene.frame_set(frame);phi=(frame-1)/24;shift=Vector((.012*math.sin(2*math.pi*phi)-.009*(1-math.cos(2*math.pi*phi)),bpy.data.objects['Walk study | native anatomical controls']['root_stride_m']*phi,0));scene.camera=camera;camera.location=Vector(pos)+shift;camera.rotation_euler=(Vector(target)+shift-camera.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(out/(prefix+'_'+label+'.png'));bpy.ops.render.render(write_still=True);print('TORSO_SILHOUETTE_RENDER',prefix,label,flush=True)
    if '--body' not in sys.argv:
        scene.frame_set(7);scene.camera=bpy.data.objects['CAM | gameplay street'];scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/(prefix+'_Gameplay.png'));bpy.ops.render.render(write_still=True);print('TORSO_SILHOUETTE_RENDER',prefix,'Gameplay',flush=True)
with (out/'ChestContour.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
if '--body' not in sys.argv:(out/'render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','matched_views':[v[0] for v in views]+['Gameplay'],'frames':[1,7,13],'native_geometry':True},indent=2)+'\n')
else:(out/'body-render-provenance.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','matched_views':[v[0] for v in views],'frames':[13],'native_geometry':True,'temporary_diagnostic_material':{'base_color':[.32,.18,.11,1],'roughness':.8},'saved_native_materials_and_visibility_changed':False},indent=2)+'\n')
