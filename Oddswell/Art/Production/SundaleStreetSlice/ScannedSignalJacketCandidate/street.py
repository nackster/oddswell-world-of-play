import bpy, json, hashlib
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/SignalJacketStudy';root=next(p for p in out.parents if (p/'.git').exists())
scene_source=root/'client/OddsWell/Saved/NextTen20260912/ScannedHumanStudy/ScannedHumanWalk.blend'
candidate=out/'OddsWellSignalJacket.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(scene_source)=='118a64a22401e78a25c6d76ab0e38b6a03e013ff7ad31ae0830ad4ecfe07bb92'
assert sha(candidate)==json.loads((out/'jacket-report.json').read_text(encoding='utf-8'))['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(scene_source));scene=bpy.context.scene
for obj in scene.objects:
    if obj.name.startswith('Scan character | '):obj.hide_render=True
with bpy.data.libraries.load(str(candidate),link=False) as (available,loaded):
    loaded.objects=[name for name in available.objects if name.startswith(('Scan character | ','Signal Jacket | ','OddsWell wardrobe | '))]
for obj in loaded.objects:
    assert obj is not None;scene.collection.objects.link(obj);obj.hide_render=False
assert len(loaded.objects)==10,len(loaded.objects)
scene.frame_set(13);scene.camera=bpy.data.objects['CAM | gameplay street'];scene.cycles.device='CPU';scene.cycles.samples=16
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.filepath=str(out/'Gameplay.png')
bpy.ops.render.render(write_still=True)
(out/'street-report.json').write_text(json.dumps({'scene_source_sha256':sha(scene_source),'candidate_sha256':sha(candidate),'appended_actor_objects':len(loaded.objects),'frame':13,'samples':16,'render':'Native Sundale Blender gameplay-camera composition','runtime_integrated':False},indent=2)+'\n',encoding='utf-8')
print('SIGNAL_JACKET_STREET_RENDERED',flush=True)
