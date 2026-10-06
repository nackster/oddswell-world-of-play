"""Cold custody, all-frame native cloth/body surface tests and sewn attachment checks."""
import bpy,ast,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py'
parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody','evaluated')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonTailoringCandidate/CottonDetail.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='9ebfbc9007d4752a568c094d988f36ee9c1fbe342f27f683d7d29d5aa24b8d6f'
def bone_totals():
    o=bpy.data.objects['Character | shorts leg continuous tailoring'];names={g.index for g in o.vertex_groups if g.name in bpy.data.objects['Walk study | native anatomical controls'].data.bones}
    return [sum(w.weight for w in v.groups if w.group in names) for v in o.data.vertices]
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_totals=bone_totals()
bpy.ops.wm.open_mainfile(filepath=str(out/'ThighDrape.blend'));after=custody();new_totals=bone_totals();maximum_bone_sum_drift=max(abs(a-b) for a,b in zip(old_totals,new_totals));assert maximum_bone_sum_drift<2e-6
for name in ('Character | shorts leg continuous tailoring','Hip study | registered cloth midsurface'):
    assert set(after[0][name]['keys'])-set(before[0][name]['keys'])=={'Anatomical inner thigh cotton ease'}
    after[0][name]['keys']={k:after[0][name]['keys'][k] for k in before[0][name]['keys']}
comparison=({name:after[0][name] for name in before[0]},*after[1:])
differences={str(section):{str(name):{'before':before[section][name],'after':comparison[section].get(name)} for name in before[section] if comparison[section].get(name)!=before[section][name]} for section in range(4)}
(out/'custody-differences.json').write_text(json.dumps(differences,indent=2)+'\n')
assert comparison==before,'Source controls/edges/UVs/old keys/maps/rest/poses changed'
scene=bpy.context.scene;pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];legs=bpy.data.objects['Character | anatomical legs'];skin=bpy.data.objects['Hip study | actual leg skin clearance']
assert pants.vertex_groups['Outer thigh cotton transition fillet'].index==mid.vertex_groups['Outer thigh cotton transition fillet'].index
targets=[o for o in scene.objects if o.name.startswith('Cotton | exact evaluated ')];assert not targets
for obj in (pants,mid,legs,skin,bpy.data.objects['Cotton | actual pocket sewing surface left'],bpy.data.objects['Cotton | actual pocket sewing surface right'],*targets):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=m.render_levels
followers=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and any(m.type=='NODES' and (m.name.startswith('Sewn actual cloth UV registration') or m.name=='Actual cloth UV folded hem') for m in o.modifiers)];assert len(followers)==10
rest_edges={};records=[]
for frame in range(1,50):
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();ps,pf,pe=evaluated(pants,deps);ls,lf,_=evaluated(legs,deps);cloth_tree=BVHTree.FromPolygons(ps,pf);leg_tree=BVHTree.FromPolygons(ls,lf)
    body_pairs=cloth_tree.overlap(leg_tree);self_pairs=[(i,j) for i,j in cloth_tree.overlap(cloth_tree) if i<j and not set(pf[i]).intersection(pf[j])]
    details={}
    for obj in followers:
        ev=obj.evaluated_get(deps);mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Sewn UV sample valid'].data),('Invalid cloth UV',frame,obj.name);ev.to_mesh_clear()
        points,faces,edges=evaluated(obj,deps);longest=max((points[a]-points[b]).length for a,b in edges)
        if frame==1:rest_edges[obj.name]=longest
        assert longest<rest_edges[obj.name]*2+.002,('Stretched attachment',frame,obj.name,longest)
        distances=[cloth_tree.find_nearest(p)[3] for p in points[::8]];assert max(distances)<.004,('Detached attachment',frame,obj.name,max(distances))
        details[obj.name]={'maximum_edge_m':longest,'maximum_sampled_cloth_distance_m':max(distances),'samples':len(distances)}
    records.append({'frame':frame,'whole_shorts_shell_leg_intersection_pairs':len(body_pairs),'whole_shorts_shell_nonadjacent_self_intersection_pairs':len(self_pairs),'self_pair_samples':self_pairs[:12],'body_pair_samples':body_pairs[:12],'shorts_details':details});print('THIGH_COLD_FRAME',frame,'BODY',len(body_pairs),'SELF',len(self_pairs),flush=True)
with (out/'ThighDrape.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'candidate_sha256':sha,'source_sha256':'9ebfbc9007d4752a568c094d988f36ee9c1fbe342f27f683d7d29d5aa24b8d6f','original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'all_original_controls_edges_uv_old_keys_maps_rest_and_six_poses_exact':True,'allowed_added_key':'Anatomical inner thigh cotton ease (shared garment/midsurface mesh)','maximum_original_bone_influence_sum_drift':maximum_bone_sum_drift,'frames':records,'scope':'All 49 authored integer frames at render subdivision resolution: complete evaluated shorts shell versus actual anatomical legs (including native closure faces), nonadjacent shell self-intersections, and ten sewn UV attachment validity/stretch/contact checks. This does not test the entire upper pelvic anatomy, every animated subframe or runtime geometry. Nearest-normal tangent distances above truncated skin boundaries are not treated as penetration or robust clearance proof.','triangle_overlap_implementation':'Blender 4.5.5 BVHTree.overlap uses isect_tri_tri_v3 in https://github.com/blender/blender/blob/v4.5.5/source/blender/python/mathutils/mathutils_bvhtree.cc#L484-L511'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['whole_shorts_shell_leg_intersection_pairs']==0 and r['whole_shorts_shell_nonadjacent_self_intersection_pairs']==0 for r in records),'Surface intersections remain; inspect retained counts before acceptance'
print('THIGH_COLD_PASS',flush=True)
