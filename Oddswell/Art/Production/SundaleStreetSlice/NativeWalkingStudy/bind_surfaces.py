"""Native surface bindings keep sewn details on their actual moving garments."""
import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'NativeWalk.blend'));scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];pants=bpy.data.objects['Character | shorts leg continuous tailoring']
def cage(source,label):
    obj=source.copy();obj.data=source.data;obj.name='Walk cage | '+label;scene.collection.objects.link(obj)
    for mod in list(obj.modifiers):
        if mod.type!='ARMATURE':obj.modifiers.remove(mod)
    obj.modifiers.new('Stable triangular garment surface','TRIANGULATE')
    obj.hide_render=True;obj.hide_set(False)
    return obj
upper=cage(coat,'jacket');lower=cage(pants,'shorts');bound={}
for obj in list(scene.objects):
    if obj.type!='MESH' or obj in [coat,pants,upper,lower] or obj.hide_render:continue
    if not obj.name.startswith(('Character | ','Walk surface | ')):continue
    name=obj.name.lower()
    if any(t in name for t in ['shorts','cotton','pocket seam','folded hem']):target=lower
    elif any(t in name for t in ['yoke','raglan','zipper','welt']):target=upper
    else:continue
    for mod in list(obj.modifiers):
        if mod.type=='ARMATURE':obj.modifiers.remove(mod)
    mod=obj.modifiers.new('Sewn garment surface following','SURFACE_DEFORM');mod.target=target
    obj.modifiers.move(len(obj.modifiers)-1,0)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
    assert mod.is_bound,('surface bind failed',obj.name)
    bound[obj.name]=target.name
    print('NATIVE_SURFACE_BOUND',obj.name,flush=True)
for obj in [upper,lower]:obj.hide_set(True)
(out/'surface-bind-report.json').write_text(json.dumps({'method':'Native Surface Deform bindings on triangulated garment control cages. Original curves remain editable; evaluated mesh followers carry sewn details.','bindings':bound},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'NativeWalk.blend'),compress=True)
print('NATIVE_SURFACES_SAVED',len(bound),flush=True)
