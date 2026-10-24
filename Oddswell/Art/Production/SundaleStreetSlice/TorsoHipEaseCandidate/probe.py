import bpy,json,hashlib,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/UpperHipHandCandidate/UpperDrape.blend';report={};pairs={}
def surface(o,deps):
    ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear();return p,f,BVHTree.FromPolygons(p,f,all_triangles=True)
for label,path in [('SOURCE',source),('CANDIDATE',out/'PosedEase.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));rows=[];pairs[label]={}
    names=['Character | tailored slate jacket','Character | shorts leg continuous tailoring','Character | internal torso support','Character | anatomical legs']
    hands=[] if '--all' in sys.argv else ['Character | anatomical right hand','Character | anatomical left hand']
    if label=='CANDIDATE':names.append('Character | continuous pelvis and upper thigh fitting')
    for name in names+hands:
        for mod in bpy.data.objects[name].modifiers:
            if mod.type=='SUBSURF':mod.levels=mod.render_levels
    for frame in (range(1,50) if '--all' in sys.argv else (1,13,35)):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();surfaces={name:surface(bpy.data.objects[name],deps) for name in names+hands};row={'frame':frame};sets={}
        for name in hands:
            p,f,tree=surfaces[name];ps={(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])};sets[name+' self']=ps;row[name+' self']=len(ps)
        for clothing in names[:2]:
            p,f,tree=surfaces[clothing];self_pairs={(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])};tag=('SHORTS' if clothing==names[1] else clothing)+' self';sets[tag]=self_pairs;row[tag]=len(self_pairs)
            for skin in names[2:] if clothing==names[1] else names[2:3]:
                contacts=set(tree.overlap(surfaces[skin][2]));tag=('SHORTS' if clothing==names[1] else clothing)+' / '+skin;sets[tag]=contacts;row[tag]=len(contacts)
        pairs[label][frame]=sets
        if label=='CANDIDATE':
            p,f,tree=surfaces[names[-1]];row['continuous_skin_self']=sum(i<j and not set(f[i]).intersection(f[j]) for i,j in tree.overlap(tree))
        if label=='CANDIDATE':row['new_pairs']={tag:len(ps-pairs['SOURCE'][frame][tag]) for tag,ps in sets.items() if tag in pairs['SOURCE'][frame]}
        rows.append(row);print('POSED_EASE_PROBE',label,json.dumps(row),flush=True)
    report[label]=rows
report['scope']=('All 49 authored integer poses; no subframes. ' if '--all' in sys.argv else 'Three selected poses. ')+'Selected authored integer poses, actual evaluated render triangles: jacket/shorts/hand self pairs and recorded support contacts. Subframes, complete body contacts, nail attachment and runtime remain outside this check.'
for label,path in [('source_sha256',source),('candidate_sha256',out/'PosedEase.blend')]:
    with path.open('rb') as f:report[label]=hashlib.file_digest(f,'sha256').hexdigest()
(out/('probe-all.json' if '--all' in sys.argv else 'probe.json')).write_text(json.dumps(report,indent=2)+'\n')
print('POSED_EASE_DIAGNOSTIC_COMPLETE',flush=True)
