import bpy,ast,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py';parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody','evaluated')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/CanvasWeaveCandidate/NaturalCanvas.blend';candidate=out/'TorsoFlow.blend'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source_sha=sha(source);assert source_sha=='a32c6cbae8fd1767da6c03559f1addd948da46259064eb0ff85e38fedad8f50a'
results={};custodies={};zip_names=[r['object'] for r in json.loads((out/'build-report.json').read_text())['fixed_collar_zipper_objects']]
for label,path in [('source',source),('candidate',candidate)]:
    bpy.ops.wm.open_mainfile(filepath=str(path));custodies[label]=custody();coat=bpy.data.objects['Character | tailored slate jacket'];body=bpy.data.objects['Character | internal torso support'];cage=bpy.data.objects['Walk cage | refined jacket surface'];collar=bpy.data.objects['Character | standing collar']
    for obj in (coat,body,cage,collar):
        for m in obj.modifiers:
            if m.type=='SUBSURF':m.levels=m.render_levels
    records=[]
    for frame in range(1,50):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();ps,pf,_=evaluated(coat,deps);bs,bf,_=evaluated(body,deps);a=BVHTree.FromPolygons(ps,pf);b=BVHTree.FromPolygons(bs,bf);pairs=sorted(a.overlap(b));selfpairs=[(i,j) for i,j in a.overlap(a) if i<j and not set(pf[i]).intersection(pf[j])];cs,cf,_=evaluated(collar,deps);ct=BVHTree.FromPolygons(cs,cf);distances={}
        for name in zip_names:
            pts,_,_=evaluated(bpy.data.objects[name],deps);distances[name]=max(ct.find_nearest(p)[3] for p in pts)
        records.append({'frame':frame,'body_pairs':pairs,'shell_self_pairs':len(selfpairs),'collar_zipper_max_distance_m':max(distances.values()),'collar_zipper_distances_m':distances});print('TORSO_COLD',label,frame,len(pairs),len(selfpairs),max(distances.values()),flush=True)
    results[label]=records
before=custodies['source'];after=custodies['candidate']
for name in ('Character | tailored slate jacket','Walk cage | refined jacket surface'):
    assert set(after[0][name]['keys'])-set(before[0][name]['keys'])=={'Anatomical upper torso jacket ease'}
    after[0][name]['keys']={k:after[0][name]['keys'][k] for k in before[0][name]['keys']}
assert ({n:after[0][n] for n in before[0]},*after[1:])==before,'Original control/UV/key/maps/rig custody changed'
pair_comparison=[]
for s,c in zip(results['source'],results['candidate']):
    old=set(map(tuple,s['body_pairs']));new=set(map(tuple,c['body_pairs']));pair_comparison.append({'frame':c['frame'],'source_body_pairs':len(old),'candidate_body_pairs':len(new),'new_body_pairs':len(new-old),'removed_body_pairs':len(old-new),'new_pair_examples':sorted(new-old)[:12],'removed_pair_examples':sorted(old-new)[:12],'source_self_pairs':s['shell_self_pairs'],'candidate_self_pairs':c['shell_self_pairs']})
    assert c['collar_zipper_max_distance_m']<.008,('Collar zipper detached',c['frame'],c['collar_zipper_max_distance_m'])
for rows in results.values():
    for row in rows:
        pairs=row.pop('body_pairs');row['body_pair_count']=len(pairs);row['body_pair_sha256']=hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest();row['body_pair_examples']=pairs[:12]
report={'candidate_sha256':sha(candidate),'source_sha256':source_sha,'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_old_keys_maps_rest_and_six_poses_exact':True,'comparison':pair_comparison,'frames':results,'scope':'All 49 authored integer frames at render subdivision. Whole jacket shell/body-support and nonadjacent shell/self surface intersections recorded against the source; inherited contacts are not claimed collision-free. Corrected collar zipper parts checked against actual standing collar. Existing shoe/shorts scoped reports remain inherited, not expanded. No subframe, physical simulation, complete human realism or runtime certificate.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('TORSO_COLD_DONE',flush=True)
