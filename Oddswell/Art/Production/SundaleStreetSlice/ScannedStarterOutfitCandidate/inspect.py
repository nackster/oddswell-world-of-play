import bpy, json
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy'
bpy.ops.wm.open_mainfile(filepath=str(out.parent/'MotionRefinement/OddsWellHumanMotion.blend'))
scene=bpy.context.scene;scene.frame_set(1)
body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
groups=[g.name for g in body.vertex_groups]
points=[body.matrix_world@v.co for v in body.data.vertices]
rows=[]
uvs=body.data.uv_layers.active.data
for p in body.data.polygons:
    pts=[points[i] for i in p.vertices]
    weights={}
    for index in p.vertices:
        for g in body.data.vertices[index].groups:
            name=groups[g.group];weights[name]=weights.get(name,0)+g.weight/len(p.vertices)
    rows.append({'index':p.index,'z':[min(v.z for v in pts),max(v.z for v in pts)],'center':[sum(v[k] for v in pts)/len(pts) for k in range(3)],
                 'uv':[sum(uvs[i].uv[k] for i in p.loop_indices)/len(p.loop_indices) for k in range(2)],'weights':weights})
report={'vertices':len(points),'bbox':[[min(v[k] for v in points),max(v[k] for v in points)] for k in range(3)],
        'bones':{b.name:list(rig.matrix_world@b.bone.head_local) for b in rig.pose.bones},'polygons':rows}
(out/'inspection.json').write_text(json.dumps(report)+'\n',encoding='utf-8');print('STARTER_SOURCE_INSPECTED',report['bbox'],flush=True)
