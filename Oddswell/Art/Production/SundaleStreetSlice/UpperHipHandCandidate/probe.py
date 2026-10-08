import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/BodyBalanceCandidate/BodyBalance.blend';report={};pairs={}
def surface(o,deps):
    ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear();return p,f,BVHTree.FromPolygons(p,f,all_triangles=True)
for label,path in [('SOURCE',source),('CANDIDATE',out/'UpperDrape.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));rows=[];pairs[label]={}
    names=['Character | tailored slate jacket','Character | shorts leg continuous tailoring','Character | internal torso support','Character | anatomical legs']
    hands=['Character | anatomical right hand','Character | anatomical left hand']
    if label=='CANDIDATE':names.append('Character | continuous pelvis and upper thigh fitting')
    for name in names+hands:
        for mod in bpy.data.objects[name].modifiers:
            if mod.type=='SUBSURF':mod.levels=mod.render_levels
    for frame in (1,7,13,17,18,32,34,35,37,41,42):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();surfaces={name:surface(bpy.data.objects[name],deps) for name in names+hands};row={'frame':frame};sets={}
        for name in hands:
            p,f,tree=surfaces[name];ps={(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])};sets[name+' self']=ps;row[name+' self']=len(ps)
        for clothing in names[:2]:
            p,f,tree=surfaces[clothing];self_pairs={(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])};sets[clothing+' self']=self_pairs;row[clothing+' self']=len(self_pairs)
            for skin in names[2:] if clothing==names[1] else names[2:3]:
                contacts=set(tree.overlap(surfaces[skin][2]));tag=clothing+' / '+skin;sets[tag]=contacts;row[tag]=len(contacts)
        pairs[label][frame]=sets
        if label=='CANDIDATE':
            p,f,tree=surfaces[names[-1]];row['continuous_skin_self']=sum(i<j and not set(f[i]).intersection(f[j]) for i,j in tree.overlap(tree))
        if label=='CANDIDATE':row['new_pairs']={tag:len(ps-pairs['SOURCE'][frame][tag]) for tag,ps in sets.items() if tag in pairs['SOURCE'][frame]}
        rows.append(row);print('UPPER_DRAPE_PROBE',label,json.dumps(row),flush=True)
    report[label]=rows
report['scope']='Eleven selected authored integer poses, actual evaluated render triangles: jacket/shorts/hand self pairs and recorded support contacts. Not all 49 poses, subframes, full body contacts, nail attachment or runtime.'
for label,path in [('source_sha256',source),('candidate_sha256',out/'UpperDrape.blend')]:
    with path.open('rb') as f:report[label]=hashlib.file_digest(f,'sha256').hexdigest()
(out/'probe.json').write_text(json.dumps(report,indent=2)+'\n')
for row in report['CANDIDATE']:
    for name in hands+names[:2]:assert row['new_pairs'][name+' self']==0,('New self contact',row['frame'],name)
    assert row['new_pairs'][names[0]+' / '+names[2]]==0
    assert row[names[1]+' / '+names[3]]==row['continuous_skin_self']==0
print('UPPER_DRAPE_SELECTED_SURFACE_PASS',flush=True)
