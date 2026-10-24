"""Cold custody and bounded all-frame native cotton checks."""
import bpy,ast,array,json,hashlib,struct
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice'
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody','evaluated')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering'))]:
    parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
source=art/'PromenadeLightCandidate/PromenadeLight.blend';candidate=out/'CottonEase.blend';build=json.loads((out/'build-report.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='1389c758ebc819e0a78250cf02006255ad178076896cdcd4279f4d7970ca9b4d'
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
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_attrs=attributes();old_weights=weights();old_transforms=transforms();old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering()
changed={'Character | shorts leg continuous tailoring','Character | sewn cotton back pocket left','Character | sewn cotton back pocket right'}|{'Walk surface | Character | '+prefix+' '+side for prefix in ('inset back pocket stitch','pocket mouth topstitch') for side in ('left','right')}
changed|={o.name for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='NODES' and (m.name.startswith('Sewn actual cloth UV registration') or m.name=='Actual cloth UV folded hem') for m in o.modifiers)}
names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | ')) and o.name not in changed];old_geometry=geometry(names)
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody();new_attrs=attributes()
assert before==after,'Original controls/edges/UVs/keys/maps/rest/poses changed'
assert all(all(new_attrs[n][a]==h for a,h in rows.items()) for n,rows in old_attrs.items()),'Old attributes changed'
assert weights()==old_weights and transforms()==old_transforms,'Weights, transforms, parents or visibility changed'
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
            assert len(ms)==build['pockets'][obj.name]['evaluated_cloth_vertex_count'],'Cloth topology changed'
            for k in range(3):assert all(0<=a.value<len(ms) for a in obj.data.attributes['Tailored triangle vertex '+str(k)].data),'Triangle index out of bounds'
            assert all(min(a.vector)>-.0001 and abs(sum(a.vector)-1)<.0001 for a in obj.data.attributes['Tailored triangle weights'].data),'Invalid triangle weights'
        else:
            ev=obj.evaluated_get(deps);mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Sewn UV sample valid'].data),('Invalid UV',frame,obj.name);ev.to_mesh_clear()
        points,faces,edges=evaluated(obj,deps);longest=max((points[a]-points[b]).length for a,b in edges)
        if frame==1:rest_edges[obj.name]=longest
        assert longest<rest_edges[obj.name]*2+.002,('Attachment stretch',frame,obj.name,longest)
        distances=[cloth_tree.find_nearest(p)[3] for p in points[::8]];assert max(distances)<.004,('Detached detail',frame,obj.name,max(distances))
        details[obj.name]={'maximum_edge_m':longest,'maximum_sampled_cloth_distance_m':max(distances),'samples':len(distances)}
    records.append({'frame':frame,'whole_shorts_shell_leg_intersection_pairs':len(body_pairs),'whole_shorts_shell_nonadjacent_self_intersection_pairs':len(self_pairs),'body_pair_samples':body_pairs[:12],'self_pair_samples':self_pairs[:12],'shorts_details':details});print('COTTON_COLD_FRAME',frame,len(body_pairs),len(self_pairs),flush=True)
report={'candidate_sha256':sha(candidate),'source_sha256':build['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_keys_old_attributes_weights_maps_rest_six_poses_exact':True,'native_walk_curves_shader_world_lights_text_transforms_visibility_exact':True,'unchanged_visible_character_objects':len(names),'unchanged_human_six_pose_geometry_exact':True,'frames':records,'scope':'49 authored integer frames at render subdivision: complete shorts shell versus actual anatomical legs including closure faces; nonadjacent shell self intersections; eight sewn details UV validity and two pocket triangle-index/weight validity, bounded edge stretch and sampled cloth distance. Excludes upper pelvic anatomy, animated subframes, full body collision, physical cloth simulation, runtime and final visual acceptance.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['whole_shorts_shell_leg_intersection_pairs']==0 and r['whole_shorts_shell_nonadjacent_self_intersection_pairs']==0 for r in records),'Surface intersection; inspect counts'
print('COTTON_COLD_PASS',flush=True)
