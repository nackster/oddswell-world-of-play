"""Stable anatomical seam weights with native projection onto the moving jacket."""
import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HandMotion.blend'))
scene=bpy.context.scene;scene.frame_set(1);rig=bpy.data.objects['Walk study | native anatomical controls'];coat=bpy.data.objects['Character | tailored slate jacket']
report={}
for obj in scene.objects:
    if not obj.name.startswith('Walk surface | Character | raglan topstitch '):continue
    world=obj.matrix_world.copy()
    for mod in list(obj.modifiers):obj.modifiers.remove(mod)
    for bone in rig.data.bones:
        if bone.name not in obj.vertex_groups:obj.vertex_groups.new(name=bone.name)
    transfer=obj.modifiers.new('Stable sewn anatomical weights','DATA_TRANSFER');transfer.object=coat;transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'}
    transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME'
    bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();names={g.index:g.name for g in obj.vertex_groups}
    records=[{names[g.group]:g.weight for g in v.groups if names[g.group] in rig.data.bones} for v in mesh.vertices];ev.to_mesh_clear();ids=list(range(len(records)))
    for group in obj.vertex_groups:
        if group.name in rig.data.bones:group.remove(ids)
    for i,weights in enumerate(records):
        total=sum(weights.values());assert total>.99
        for name,w in weights.items():
            if w>1e-7:obj.vertex_groups[name].add([i],w/total,'REPLACE')
    obj.modifiers.remove(transfer);obj.parent=rig;obj.parent_type='OBJECT';obj.matrix_world=world
    mod=obj.modifiers.new('Stable sewn armature deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    project=obj.modifiers.new('Sewn cloth contact','SHRINKWRAP');project.target=coat;project.wrap_method='NEAREST_SURFACEPOINT';project.wrap_mode='ABOVE_SURFACE';project.offset=.00055
    report[obj.name]={'controls':len(records),'binding':'Native jacket weight transfer, armature deformation, nearest-surface projection above the actual moving jacket.','offset_m':project.offset}
assert len(report)==4
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'HandMotion.blend'),compress=True)
(out/'stitch-bind-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('STABLE_STITCHES_SAVED',flush=True)
