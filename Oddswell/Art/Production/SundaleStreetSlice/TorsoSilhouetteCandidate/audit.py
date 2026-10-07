"""Cold torso fit custody and source/candidate 49-frame jacket checks."""
import bpy,ast,array,json,hashlib,struct
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice'
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody','evaluated')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering'))]:
    parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
source=art/'CottonEaseCandidate/CottonEase.blend';candidate=out/'TorsoSilhouette.blend';build=json.loads((out/'build-report.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='a46587e5990c80822b118c019168576708366377b37663422bde60d420d322fb'
edited=('Character | tailored slate jacket','Walk cage | refined jacket surface','Character | internal torso support')
pair_cache={}
def weights():
    result={}
    for name in edited:
        o=bpy.data.objects[name];h=hashlib.sha256()
        for v in o.data.vertices:
            old=[w for w in v.groups if o.vertex_groups[w.group].name!='Posed sleeve anatomical ease'];h.update(struct.pack('<I',len(old)))
            for w in old:h.update(struct.pack('<If',w.group,w.weight))
        result[name]=([g.name for g in o.vertex_groups if g.name!='Posed sleeve anatomical ease'],h.hexdigest())
    return result
def meta():
    return {o.name:([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone,o.hide_render,[s.material.name if s.material else None for s in o.material_slots],[(m.name,m.type,getattr(m,'node_group',None).name if getattr(m,'node_group',None) else None) for m in o.modifiers if m.name not in ('Sleeve cotton follows posed arm contours','Rounded elbow cotton compression')]) for o in bpy.context.scene.objects}
def old_fields():
    return {name:{a.name:digest(a.data,'vector',3) if a.data_type=='FLOAT_VECTOR' else digest(a.data,'value',1) for a in bpy.data.objects[name].data.attributes if a.data_type in ('FLOAT_VECTOR','FLOAT') and a.name!='Elbow cotton compression relief'} for name in edited}
def screen(label,followers):
    scene=bpy.context.scene;coat=bpy.data.objects[edited[0]];cage=bpy.data.objects[edited[1]];body=bpy.data.objects['Character | internal torso support']
    for o in (coat,cage,body):
        for m in o.modifiers:
            if m.type=='SUBSURF':m.levels=m.render_levels
    rows=[];pair_cache[label]={};cache=out/'source-screen-cache.json'
    if label=='SOURCE' and cache.exists():
        saved=json.loads(cache.read_text())
        if saved.get('version')==1 and saved['source_sha256']==sha(source) and saved['followers']==followers:
            pair_cache[label]={int(f):set(tuple(p) for p in ps) for f,ps in saved['pairs'].items()};print('TORSO_SOURCE_SCREEN_HASH_PINNED_CACHE',flush=True);return saved['frames']
    for frame in range(1,50):
        scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();p,f,e=evaluated(coat,deps);bp,bf,be=evaluated(body,deps);tree=BVHTree.FromPolygons(p,f);bt=BVHTree.FromPolygons(bp,bf);body_pairs=sorted(tree.overlap(bt));self_pairs=[(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])];details={}
        for name in followers:
            points,faces,edges=evaluated(bpy.data.objects[name],deps);details[name]={'maximum_sampled_gap_m':max(tree.find_nearest(v)[3] for v in points[::4]),'maximum_edge_m':max((points[a]-points[b]).length for a,b in edges)}
        rows.append({'frame':frame,'shell_self_pairs':len(self_pairs),'body_pair_count':len(body_pairs),'body_pair_sha256':hashlib.sha256(json.dumps(body_pairs,separators=(',',':')).encode()).hexdigest(),'body_pair_examples':body_pairs[:12],'sewn_details':details});print('TORSO_SCREEN',label,frame,len(self_pairs),len(body_pairs),flush=True)
        pair_cache[label][frame]=set(body_pairs)
    if label=='SOURCE':cache.write_text(json.dumps({'version':1,'source_sha256':sha(source),'followers':followers,'frames':rows,'pairs':{f:sorted(ps) for f,ps in pair_cache[label].items()}},indent=2)+'\n')
    return rows
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_meta=meta();old_weights=weights();old_attributes=old_fields();old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering();cage=bpy.data.objects[edited[1]]
changed={edited[0],edited[2]}|{o.name for o in bpy.context.scene.objects if any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)}
changed|={o.name for o in bpy.context.scene.objects if o.name.startswith('Walk surface | Character | raglan topstitch ')}
names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | ')) and o.name not in changed];old_geometry=geometry(names)
followers=[o.name for o in bpy.context.scene.objects if not o.hide_render and (('front welt' in o.name and any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)) or o.name.startswith('Walk surface | Character | raglan topstitch '))];assert len(followers)==6
baseline=screen('SOURCE',followers)
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody()
for name in edited[:2]:
    o=bpy.data.objects[name];m=o.modifiers['Sleeve cotton follows posed arm contours'];assert m.target.name=='Torso fit | isolated anatomical arm contact' and abs(m.offset-.012)<1e-7 and m.vertex_group=='Posed sleeve anatomical ease'
    group=o.vertex_groups['Posed sleeve anatomical ease'].index;assert all(0<=w.weight<=.850001 for v in o.data.vertices for w in v.groups if w.group==group)
for name in edited:
    allowed=set(build['body_taper']['added_keys']) if name==edited[2] else {build['added_key']}
    assert set(after[0][name]['keys'])-set(before[0][name]['keys'])==allowed;after[0][name]['keys']={k:after[0][name]['keys'][k] for k in before[0][name]['keys']}
assert ({name:after[0][name] for name in before[0]},*after[1:])==before,'Original controls/edges/old UVs/keys/maps/rest/poses changed'
after_meta=meta();assert {name:after_meta[name] for name in old_meta}==old_meta and weights()==old_weights and old_fields()==old_attributes,'Original transforms/parents/visibility/material assignments/modifier names or clothing weights/fields changed'
contact=bpy.data.objects['Torso fit | isolated anatomical arm contact'];assert contact.hide_render and contact.data==bpy.data.objects[edited[2]].data;assert set(after_meta)-set(old_meta)=={contact.name}
assert materials()==old_materials and action()==old_action and world()==old_world and lights()==old_lights and lettering()==old_text,'Shader/walk/lighting/text changed'
new_geometry=geometry(names);differences={f:[n for n in names if old_geometry[f][n]!=new_geometry[f][n]] for f in old_geometry};(out/'geometry-differences.json').write_text(json.dumps(differences,indent=2)+'\n');assert old_geometry==new_geometry,'Unchanged human geometry changed'
frames=screen('CANDIDATE',followers)
for row,old in zip(frames,baseline):
    new_pairs=pair_cache['CANDIDATE'][row['frame']]-pair_cache['SOURCE'][row['frame']];row['new_body_pairs_not_in_source_count']=len(new_pairs);row['new_body_pair_examples']=sorted(new_pairs)[:12]
    for name,d in row['sewn_details'].items():
        assert d['maximum_sampled_gap_m']<old['sewn_details'][name]['maximum_sampled_gap_m']+.003,('Welt separation regression',row['frame'],name,d)
        assert d['maximum_edge_m']<old['sewn_details'][name]['maximum_edge_m']*1.5+.002,('Welt stretch regression',row['frame'],name,d)
report={'candidate_sha256':sha(candidate),'source_sha256':build['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_old_uv_keys_maps_rest_six_poses_exact':True,'original_support_jacket_cage_weights_float_vector_fields_exact':True,'original_walk_shaders_world_lights_text_transforms_visibility_material_assignments_modifier_names_exact':True,'unchanged_visible_human_objects':len(names),'unchanged_human_six_pose_geometry_exact':True,'declared_surface_followers':sorted(changed-{edited[0],edited[2]}),'declared_deformed_support':edited[2],'added_hidden_contact_object':contact.name,'source_frames':baseline,'candidate_frames':frames,'scope':'Render-subdivision complete jacket shell versus internal body support and nonadjacent jacket self intersections in all 49 authored integer frames. Six visible sewing details (two front welts and four raglan threads) have sampled contact/edge bounds against each source frame. Existing body-support intersections are recorded and remain unproven collision-free. Excludes other detail contact, whole-body collision, animated subframes, physical simulation, final photoreal acceptance and runtime.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['shell_self_pairs']==0 for r in frames),'Jacket self-intersections remain'
assert all(r['body_pair_count']<=old['body_pair_count'] for r,old in zip(frames,baseline)),'Body-support intersection count increased'
assert all(r['new_body_pairs_not_in_source_count']==0 for r in frames),'New body-support triangle pairs introduced'
print('TORSO_SILHOUETTE_COLD_PASS',flush=True)
