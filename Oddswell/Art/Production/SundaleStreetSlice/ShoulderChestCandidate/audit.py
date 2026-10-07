"""Cold native custody, physical weave UVs and complete authored-walk jacket screens."""
import bpy,ast,array,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py';parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody','evaluated')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/TorsoFlowCandidate/TorsoFlow.blend';candidate=out/'ShoulderChest.blend'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
source_sha=sha(source);assert source_sha=='3d4b732f51a6d2b79a0ed18a9b4f94b67c843cefd1b14a968bc62bf4591f4dc3';prior=json.loads((source.parent/'cold-audit.json').read_text());assert prior['candidate_sha256']==source_sha;baseline={r['frame']:r for r in prior['frames']['candidate']}
def geometry():
    results={}
    for frame in (1,7,13,25,33,49):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();results[frame]={}
        for name in ('Character | internal torso support','Character | shorts leg continuous tailoring','Character | anatomical legs','Character | canvas sneaker left','Character | canvas sneaker right'):
            ev=bpy.data.objects[name].evaluated_get(deps);mesh=ev.to_mesh();results[frame][name]={'co':digest(mesh.vertices,'co',3),'edges':digest(mesh.edges,'vertices',2)};ev.to_mesh_clear()
    return results
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_geometry=geometry();source_seams={};coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];names=[o.name for o in bpy.context.scene.objects if not o.hide_render and any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers) and ('raglan topstitch' in o.name or 'front welt' in o.name)]
for obj in (coat,cage):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=m.render_levels
for frame in (1,7,13,25,33,49):
    bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();p,f,_=evaluated(coat,deps);tree=BVHTree.FromPolygons(p,f)
    for name in names:
        pts,_,edges=evaluated(bpy.data.objects[name],deps);r=source_seams.setdefault(name,{'maximum_sampled_gap_m':0.,'maximum_edge_m':0.});r['maximum_sampled_gap_m']=max(r['maximum_sampled_gap_m'],max(tree.find_nearest(p)[3] for p in pts[::4]));r['maximum_edge_m']=max(r['maximum_edge_m'],max((pts[i]-pts[j]).length for i,j in edges))
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody();new_geometry=geometry();uv_reports={}
for name in ('Character | tailored slate jacket','Walk cage | refined jacket surface'):
    assert set(after[0][name]['keys'])-set(before[0][name]['keys'])=={'Relaxed anatomical shoulder ease'};after[0][name]['keys']={k:after[0][name]['keys'][k] for k in before[0][name]['keys']}
    assert set(after[0][name]['uv'])-set(before[0][name]['uv'])=={'Physical rest jacket weave'};after[0][name]['uv']={k:after[0][name]['uv'][k] for k in before[0][name]['uv']}
    obj=bpy.data.objects[name];obj.data.calc_loop_triangles();uv=obj.data.uv_layers['Physical rest jacket weave'];old=obj.data.uv_layers['Cut raglan cloth panels'];zeros=[];old_zeros=[]
    for tri in obj.data.loop_triangles:
        a,b,c=[uv.data[i].uv for i in tri.loops];oa,ob,oc=[old.data[i].uv for i in tri.loops]
        if tri.area>1e-10 and abs((b-a).cross(c-a))<1e-12:zeros.append(tri.index)
        if tri.area>1e-10 and abs((ob-oa).cross(oc-oa))<1e-12:old_zeros.append(tri.index)
    assert zeros==old_zeros;assert all(math.isfinite(c) for r in uv.data for c in r.uv);uv_reports[name]={'hash':digest(uv.data,'uv',2),'loops':len(uv.data),'zero_area_nondegenerate_triangles':len(zeros),'original_zero_area_triangles':len(old_zeros)}
assert ({n:after[0][n] for n in before[0]},*after[1:])==before,'Native custody changed';assert old_geometry==new_geometry,'Unedited torso support/shorts/legs/shoes evaluated geometry changed'
coat=bpy.data.objects['Character | tailored slate jacket'];body=bpy.data.objects['Character | internal torso support'];cage=bpy.data.objects['Walk cage | refined jacket surface']
for obj in (coat,body,cage):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=m.render_levels
frames=[]
for frame in range(1,50):
    bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();p,f,_=evaluated(coat,deps);bp,bf,_=evaluated(body,deps);tree=BVHTree.FromPolygons(p,f);bt=BVHTree.FromPolygons(bp,bf);body_pairs=sorted(tree.overlap(bt));selfpairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])];details={}
    for name in names:
        points,_,edges=evaluated(bpy.data.objects[name],deps);gap=max(tree.find_nearest(p)[3] for p in points[::4]);edge=max((points[i]-points[j]).length for i,j in edges);details[name]={'maximum_sampled_gap_m':gap,'maximum_edge_m':edge}
        assert gap<source_seams[name]['maximum_sampled_gap_m']+.003,('Sewn detail contact regression',frame,name,gap,source_seams[name]);assert edge<source_seams[name]['maximum_edge_m']*1.5+.002,('Sewn detail stretch regression',frame,name,edge)
    pair_sha=hashlib.sha256(json.dumps(body_pairs,separators=(',',':')).encode()).hexdigest();row={'frame':frame,'shell_self_pairs':len(selfpairs),'body_pair_count':len(body_pairs),'body_pair_sha256':pair_sha,'body_pair_examples':body_pairs[:12],'source_body_pair_count':baseline[frame]['body_pair_count'],'source_body_pair_sha256':baseline[frame]['body_pair_sha256'],'body_pairs_exact_to_source':pair_sha==baseline[frame]['body_pair_sha256'],'sewn_details':details};frames.append(row);print('SHOULDER_CHEST_COLD',frame,'SELF',len(selfpairs),'BODY',len(body_pairs),'SOURCE',baseline[frame]['body_pair_count'],flush=True)
report={'candidate_sha256':sha(candidate),'source_sha256':source_sha,'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_old_keys_maps_rest_and_six_poses_exact':True,'unedited_support_shorts_legs_shoes_six_pose_evaluated_geometry_exact':True,'uvs':uv_reports,'source_sewn_details_six_pose_bounds':source_seams,'frames':frames,'scope':'Complete evaluated jacket shell self/body-support screens at render subdivision in all 49 authored integer frames, compared with hash-pinned immediate-source cold results. Sampled visible front welt contact and edge length compared with six source poses. Preserved controls/old UVs/old keys/maps/rest/six full poses; two new UV layers and one shared shoulder key, outward front tension relief and jacket shader copy. No claim of complete-body collision freedom, animated subframes, physical cloth simulation, final photographic human realism or runtime compatibility.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n');assert max(r['shell_self_pairs'] for r in frames)==0,'Jacket shell self-intersections remain';print('SHOULDER_CHEST_COLD_PASS',flush=True)
