"""Use native bone-heat skin weights and transfer them to the fitted jacket."""
import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'NativeWalk.blend'));scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['Walk study | native anatomical controls'];body=bpy.data.objects['Character | internal torso support'];coat=bpy.data.objects['Character | tailored slate jacket']
flags={b.name:b.use_deform for b in rig.data.bones}
for b in rig.data.bones:b.use_deform=b.name in ['pelvis','chest','neg.upperarm','neg.forearm','pos.upperarm','pos.forearm']
hidden=body.hide_get();body.hide_set(False)
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
world=body.matrix_world.copy();bpy.ops.object.parent_set(type='ARMATURE_AUTO');body.matrix_world=world
for b in rig.data.bones:b.use_deform=flags[b.name]
for mod in list(body.modifiers):
    if mod.type=='ARMATURE' and mod.name!='Native walk deformation':body.modifiers.remove(mod)
body.hide_set(hidden);bpy.context.view_layer.update()
def transfer_weights(obj):
    transfer=obj.modifiers.new('Transfer anatomical heat weights','DATA_TRANSFER');transfer.object=body
    transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'}
    transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME'
    obj.modifiers.move(len(obj.modifiers)-1,0)
    flags_mod=[(m,m.show_viewport) for m in obj.modifiers if m!=transfer]
    for m,_ in flags_mod:m.show_viewport=False
    bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    assert len(mesh.vertices)==len(obj.data.vertices)
    names={g.index:g.name for g in obj.vertex_groups}
    records=[{names[g.group]:g.weight for g in v.groups if names[g.group] in rig.data.bones} for v in mesh.vertices]
    ev.to_mesh_clear();ids=list(range(len(records)))
    for group in obj.vertex_groups:
        if group.name in rig.data.bones:group.remove(ids)
    for i,weights in enumerate(records):
        total=sum(weights.values());assert total>.5,('unbound garment',obj.name,i,total)
        for name,w in weights.items():
            if w>1e-7:obj.vertex_groups[name].add([i],w/total,'REPLACE')
    obj.modifiers.remove(transfer)
    for m,flag in flags_mod:m.show_viewport=flag
    return len(records)
transferred={}
for obj in list(scene.objects):
    if obj.type=='MESH' and any(m.name=='Native walk deformation' for m in obj.modifiers) and any(word in obj.name.lower() for word in ['jacket','yoke','raglan','zipper','collar','facing']):
        transferred[obj.name]=transfer_weights(obj)
scene.frame_set(1)
(out/'heat-bind-report.json').write_text(json.dumps({'method':'Native Blender armature bone heat on anatomical support, nearest-polygon interpolated vertex-weight transfer to jacket and fitted trim. Original garment attachment group preserved.','transferred_jacket_controls':transferred[coat.name],'transferred_objects':transferred,'body_controls':len(body.data.vertices)},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'NativeWalk.blend'),compress=True)
print('NATIVE_HEAT_BIND_SAVED',len(transferred),flush=True)
