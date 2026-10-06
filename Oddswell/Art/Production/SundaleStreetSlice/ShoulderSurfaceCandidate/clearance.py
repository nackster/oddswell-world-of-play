"""Keep rounded moving cloth outside the anatomical support with a native constraint."""
import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'RoundedShoulder.blend'))
scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];body=bpy.data.objects['Character | internal torso support']
followers=[o for o in scene.objects if any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)]
for obj in followers:
    for mod in list(obj.modifiers):
        if mod.type=='SURFACE_DEFORM' and mod.target==cage:obj.modifiers.remove(mod)
pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index
for obj in [coat,cage]:
    group=obj.vertex_groups.new(name='Free cloth anatomical clearance')
    for vertex in obj.data.vertices:
        held=max((g.weight for g in vertex.groups if g.group==pin),default=0)
        if held<.8:group.add([vertex.index],1.,'REPLACE')
    mod=obj.modifiers.new('Free cloth outside anatomical support','SHRINKWRAP');mod.target=body
    mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='OUTSIDE';mod.offset=.007;mod.vertex_group=group.name
    obj.modifiers.move(len(obj.modifiers)-1,2)
    print('CLEARANCE_MODE',obj.name,[(i.identifier,i.description) for i in mod.bl_rna.properties['wrap_mode'].enum_items],flush=True)
for obj in followers:
    mod=obj.modifiers.new('Refined sewn garment surface following','SURFACE_DEFORM');mod.target=cage;obj.modifiers.move(len(obj.modifiers)-1,0)
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.surfacedeform_bind(modifier=mod.name);assert mod.is_bound
    print('CLEARANCE_REBOUND',obj.name,flush=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'RoundedShoulder.blend'),compress=True)
print('CLEARANCE_SAVED',flush=True)
