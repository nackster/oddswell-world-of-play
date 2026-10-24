"""Cold custody and bounded all-frame native cotton checks."""
import bpy,ast,array,json,hashlib,struct
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice'
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody','evaluated')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering'))]:
    parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
source=art/'ChestContourCandidate/ChestContour.blend';candidate=out/'SeatFlow.blend';build=json.loads((out/'build-report.json').read_text());pocket_build=json.loads((art/'CottonEaseCandidate/build-report.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='2cfb15e7fe5f96feff0a48e1b744a254e22ba24bbe3e330ca37c201862785cdb'
def attributes():
    result={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        rows={}
        for a in o.data.attributes:
            field,width=('vector',3) if a.data_type=='FLOAT_VECTOR' else ('value',1) if a.data_type=='FLOAT' else (None,None)
            if field:rows[a.name]=digest(a.data,field,width)
        result[o.name]=rows
    return result
def weights():
    result={};cache={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or not o.vertex_groups:continue
        if o.data.as_pointer() not in cache:
            h=hashlib.sha256()
            for v in o.data.vertices:
                h.update(struct.pack('<I',len(v.groups)))
                for w in v.groups:h.update(struct.pack('<If',w.group,w.weight))
            cache[o.data.as_pointer()]=h.hexdigest()
        result[o.name]=([g.name for g in o.vertex_groups],cache[o.data.as_pointer()])
    return result
def transforms():
    return {o.name:([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone,o.hide_render) for o in bpy.context.scene.objects}
def seat_weights():
    o=bpy.data.objects['Character | shorts leg continuous tailoring']
    return [dict((o.vertex_groups[w.group].name,w.weight) for w in v.groups if o.vertex_groups[w.group].name!='Posterior cotton finite bend radius') for v in o.data.vertices]
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_attrs=attributes();old_weights=weights();old_seat=seat_weights();old_transforms=transforms();old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering()
changed={'Character | shorts leg continuous tailoring','Character | sewn cotton back pocket left','Character | sewn cotton back pocket right'}|{'Walk surface | Character | '+prefix+' '+side for prefix in ('inset back pocket stitch','pocket mouth topstitch') for side in ('left','right')}
changed|={o.name for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='NODES' and (m.name.startswith('Sewn actual cloth UV registration') or m.name=='Actual cloth UV folded hem') for m in o.modifiers)}
names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | ')) and o.name not in changed];old_geometry=geometry(names)
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody();new_attrs=attributes()
assert before==after,'Original controls/edges/UVs/keys/maps/rest/poses changed'
assert all(all(new_attrs[n][a]==h for a,h in rows.items()) for n,rows in old_attrs.items()),'Old attributes changed'
new_weights=weights();declared={'Character | shorts leg continuous tailoring','Hip study | registered cloth midsurface'}
assert {n:w for n,w in new_weights.items() if n not in declared}=={n:w for n,w in old_weights.items() if n not in declared},'Unedited weights changed'
assert all([g for g in new_weights[n][0] if g!='Posterior cotton finite bend radius']==old_weights[n][0] for n in declared),'Old seat group names/order changed'
new_seat=seat_weights();changes={r['id']:r for r in build['controls']};allowed={'pelvis','neg.thigh','pos.thigh','neg.shin','pos.shin'}
for i,(prior,current) in enumerate(zip(old_seat,new_seat)):
    if i not in changes:assert current==prior,('Undeclared control weight change',i);continue
    assert {n:w for n,w in current.items() if n not in allowed}=={n:w for n,w in prior.items() if n not in allowed},('Unedited weight group changed',i)
    assert abs(sum(current.values())-sum(prior.values()))<1e-6,('Total influence changed',i)
    row=changes[i]
    assert abs(current.get('pelvis',0)-prior.get('pelvis',0)-row['leg_influence_to_pelvis'])<1e-6
    for n in allowed-{'pelvis'}:assert abs(current.get(n,0)-prior.get(n,0)*(1-row['mask']))<1e-6
assert transforms()==old_transforms,'Transforms, parents or visibility changed'
assert materials()==old_materials and action()==old_action and world()==old_world and lights()==old_lights and lettering()==old_text,'Original shader/animation/lighting/text changed'
new_geometry=geometry(names);differences={f:[n for n in names if old_geometry[f][n]!=new_geometry[f][n]] for f in old_geometry};(out/'geometry-differences.json').write_text(json.dumps(differences,indent=2)+'\n');assert new_geometry==old_geometry,'Unchanged human geometry changed'
scene=bpy.context.scene;pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];legs=bpy.data.objects['Character | anatomical legs'];skin=bpy.data.objects['Hip study | actual leg skin clearance']
for obj in (pants,mid,legs,skin,bpy.data.objects['Cotton | actual pocket sewing surface left'],bpy.data.objects['Cotton | actual pocket sewing surface right']):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=m.render_levels
followers=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and any(m.type=='NODES' and (m.name.startswith('Sewn actual cloth UV registration') or m.name=='Actual cloth UV folded hem') for m in o.modifiers)];assert len(followers)==10
rest_edges={};records=[]
for frame in range(1,50):
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();ps,pf,pe=evaluated(pants,deps);ls,lf,_=evaluated(legs,deps);cloth_tree=BVHTree.FromPolygons(ps,pf);leg_tree=BVHTree.FromPolygons(ls,lf)
    body_pairs=cloth_tree.overlap(leg_tree);self_pairs=[(i,j) for i,j in cloth_tree.overlap(cloth_tree) if i<j and not set(pf[i]).intersection(pf[j])];details={}
    ms,mf,me=evaluated(mid,deps)
    for obj in followers:
        if obj.name.startswith('Character | sewn cotton back pocket '):
            assert len(ms)==pocket_build['pockets'][obj.name]['evaluated_cloth_vertex_count'],'Cloth topology changed'
            for k in range(3):assert all(0<=a.value<len(ms) for a in obj.data.attributes['Tailored triangle vertex '+str(k)].data),'Triangle index out of bounds'
            assert all(min(a.vector)>-.0001 and abs(sum(a.vector)-1)<.0001 for a in obj.data.attributes['Tailored triangle weights'].data),'Invalid triangle weights'
            ev=obj.evaluated_get(deps);mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Rear pocket visible-shell projection valid'].data),('Pocket projection miss',frame,obj.name);ev.to_mesh_clear()
        else:
            ev=obj.evaluated_get(deps);mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Sewn UV sample valid'].data),('Invalid UV',frame,obj.name);ev.to_mesh_clear()
        points,faces,edges=evaluated(obj,deps);longest=max((points[a]-points[b]).length for a,b in edges)
        if frame==1:rest_edges[obj.name]=longest
        assert longest<rest_edges[obj.name]*2+.002,('Attachment stretch',frame,obj.name,longest)
        distances=[cloth_tree.find_nearest(p)[3] for p in points[::8]];assert max(distances)<.004,('Detached detail',frame,obj.name,max(distances))
        details[obj.name]={'maximum_edge_m':longest,'maximum_sampled_cloth_distance_m':max(distances),'samples':len(distances)}
        if obj.name.startswith('Character | sewn cotton back pocket '):
            pocket_tree=BVHTree.FromPolygons(points,faces);crossings=pocket_tree.overlap(cloth_tree);pocket_self=[(i,j) for i,j in pocket_tree.overlap(pocket_tree) if i<j and not set(faces[i]).intersection(faces[j])]
            details[obj.name]['complete_pocket_shell_cloth_pairs']=len(crossings);details[obj.name]['complete_pocket_shell_nonadjacent_self_pairs']=len(pocket_self)
    records.append({'frame':frame,'whole_shorts_shell_leg_intersection_pairs':len(body_pairs),'whole_shorts_shell_nonadjacent_self_intersection_pairs':len(self_pairs),'body_pair_samples':body_pairs[:12],'self_pair_samples':self_pairs[:12],'shorts_details':details});print('COTTON_COLD_FRAME',frame,len(body_pairs),len(self_pairs),flush=True)
report={'candidate_sha256':sha(candidate),'source_sha256':build['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_keys_old_attributes_maps_rest_six_poses_exact':True,'original_weights_except_declared_seat_changes_exact':True,'declared_weight_controls':len(changes),'native_walk_curves_shader_world_lights_text_transforms_visibility_exact':True,'unchanged_visible_character_objects':len(names),'unchanged_human_six_pose_geometry_exact':True,'frames':records,'scope':'49 authored integer frames at render subdivision: complete shorts shell versus actual anatomical legs including closure faces; nonadjacent shorts shell self intersections; both complete visible pocket shells versus the actual shorts shell and nonadjacent pocket self pairs; eight sewn details UV validity and two pocket triangle-index/weight validity, bounded edge stretch and sampled cloth distance. Declared seat controls preserve total influence and all unedited groups. Excludes upper pelvic anatomy, animated subframes, full body collision, physical cloth simulation, runtime and final visual acceptance.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['whole_shorts_shell_leg_intersection_pairs']==0 and r['whole_shorts_shell_nonadjacent_self_intersection_pairs']==0 for r in records),'Surface intersection; inspect counts'
assert all(d.get('complete_pocket_shell_cloth_pairs',0)==d.get('complete_pocket_shell_nonadjacent_self_pairs',0)==0 for r in records for d in r['shorts_details'].values()),'Pocket shell crossings remain'
print('SEAT_FLOW_COLD_PASS',flush=True)
