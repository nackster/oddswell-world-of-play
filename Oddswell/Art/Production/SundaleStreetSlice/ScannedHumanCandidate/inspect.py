import bpy,json
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(out/'EricSource/rp_eric_rigged_001_zup_a.fbx'))
report={'objects':[],'materials':[]}
for o in bpy.context.scene.objects:
    row={'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'matrix':[list(r) for r in o.matrix_world]}
    if o.type=='MESH':row.update(vertices=len(o.data.vertices),polygons=len(o.data.polygons),uvs=[u.name for u in o.data.uv_layers],groups=[g.name for g in o.vertex_groups])
    if o.type=='ARMATURE':row['bones']=[{'name':b.name,'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones]
    report['objects'].append(row)
for m in bpy.data.materials:
    report['materials'].append({'name':m.name,'nodes':[(n.name,n.type,getattr(n,'image',None).filepath if getattr(n,'image',None) else None) for n in m.node_tree.nodes] if m.use_nodes else []})
(out/'import-inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'EricImported.blend'),compress=True)
print('SCAN_IMPORT_COMPLETE',flush=True)
