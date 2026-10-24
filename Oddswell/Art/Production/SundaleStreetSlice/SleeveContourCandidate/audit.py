"""Cold custody and actual-render-triangle walking checks for forearm fitting."""
import bpy,ast,array,json,hashlib,struct,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';edited=('Character | tailored slate jacket','Walk cage | refined jacket surface');pair_cache={};self_cache={}
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody','evaluated')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering')),(art/'TorsoSilhouetteCandidate/audit.py',('screen',))]:
    parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
source=art/'WaistJoinCandidate/WaistJoin.blend';candidate=out/'SleeveContour.blend';build=json.loads((out/'build-report.json').read_text())
def evaluated(obj,deps):
    ev=obj.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    points=[ev.matrix_world@v.co for v in mesh.vertices];faces=[tuple(t.vertices) for t in mesh.loop_triangles];edges=[tuple(e.vertices) for e in mesh.edges]
    ev.to_mesh_clear();return points,faces,edges

def screen(label, followers):
    scene = bpy.context.scene
    coat = bpy.data.objects[edited[0]]
    cage = bpy.data.objects[edited[1]]
    body = bpy.data.objects['Character | internal torso support']
    for o in (coat, cage, body):
        for m in o.modifiers:
            if m.type == 'SUBSURF':
                m.levels = m.render_levels
    rows = []
    pair_cache[label] = {}
    self_cache[label] = {}
    cache = out / 'source-screen-cache.json'
    if label == 'SOURCE' and cache.exists():
        saved = json.loads(cache.read_text())
        if saved.get('version') == 'render-loop-triangles-v2-self-pairs' and saved['source_sha256'] == sha(source) and (saved['followers'] == followers):
            pair_cache[label] = {int(f): set((tuple(p) for p in ps)) for f, ps in saved['pairs'].items()}
            self_cache[label] = {int(f): set((tuple(p) for p in ps)) for f, ps in saved['self_pairs'].items()}
            print('TORSO_SOURCE_SCREEN_HASH_PINNED_CACHE', flush=True)
            return saved['frames']
    for frame in range(1, 50):
        scene.frame_set(frame)
        deps = bpy.context.evaluated_depsgraph_get()
        p, f, e = evaluated(coat, deps)
        bp, bf, be = evaluated(body, deps)
        tree = BVHTree.FromPolygons(p, f)
        bt = BVHTree.FromPolygons(bp, bf)
        body_pairs = sorted(tree.overlap(bt))
        self_pairs = [(i, j) for i, j in tree.overlap(tree) if i < j and (not set(f[i]).intersection(f[j]))]
        details = {}
        for name in followers:
            points, faces, edges = evaluated(bpy.data.objects[name], deps)
            details[name] = {'maximum_sampled_gap_m': max((tree.find_nearest(v)[3] for v in points[::4])), 'maximum_edge_m': max(((points[a] - points[b]).length for a, b in edges))}
        rows.append({'frame': frame, 'shell_self_pairs': len(self_pairs), 'body_pair_count': len(body_pairs), 'body_pair_sha256': hashlib.sha256(json.dumps(body_pairs, separators=(',', ':')).encode()).hexdigest(), 'body_pair_examples': body_pairs[:12], 'sewn_details': details})
        print('TORSO_SCREEN', label, frame, len(self_pairs), len(body_pairs), flush=True)
        pair_cache[label][frame] = set(body_pairs)
        self_cache[label][frame] = set(self_pairs)
    if label == 'SOURCE':
        cache.write_text(json.dumps({'version': 'render-loop-triangles-v2-self-pairs', 'source_sha256': sha(source), 'followers': followers, 'frames': rows, 'pairs': {f: sorted(ps) for f, ps in pair_cache[label].items()},'self_pairs': {f: sorted(ps) for f, ps in self_cache[label].items()}}, indent=2) + '\n')
    return rows

def fit_weights():
    o=bpy.data.objects[edited[0]];index=o.vertex_groups[build['fit_group']].index
    return [next((w.weight for w in v.groups if w.group==index),0.) for v in o.data.vertices]

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='15eaf6cf97f43895d2fdee1f48828b5d10740d6916776a611a9c29f057ddf0d5'
def metadata():
    result={};weight_cache={};field_cache={}
    for o in bpy.context.scene.objects:
        if o.type not in ('MESH','CURVE'):continue
        excluded=o.vertex_groups[build['fit_group']].index if o.name in edited else None
        cache_key=(o.data.as_pointer(),excluded)
        if cache_key not in weight_cache:
            weights=[[(w.group,w.weight) for w in v.groups if w.group!=excluded] for v in o.data.vertices] if o.type=='MESH' else []
            weight_cache[cache_key]=hashlib.sha256(json.dumps(weights).encode()).hexdigest()
        if o.data.as_pointer() not in field_cache:
            field_cache[o.data.as_pointer()]={a.name:digest(a.data,'vector',3) if a.data_type=='FLOAT_VECTOR' else digest(a.data,'value',1) for a in o.data.attributes if a.data_type in ('FLOAT','FLOAT_VECTOR')} if o.type=='MESH' else {}
        result[o.name]={'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'hidden':o.hide_render,'materials':[s.material.name if s.material else None for s in o.material_slots],'modifiers':[(m.name,m.type) for m in o.modifiers],'groups':[g.name for g in o.vertex_groups] if o.type=='MESH' else [],'weights':weight_cache[cache_key],'fields':field_cache[o.data.as_pointer()]}
    return result

def modifier_settings():
    result={}
    for o in bpy.context.scene.objects:
        rows={}
        for m in o.modifiers:
            settings={}
            for p in m.bl_rna.properties:
                if p.is_readonly or p.identifier=='rna_type' or p.type=='COLLECTION':continue
                v=getattr(m,p.identifier)
                if p.type=='POINTER' and v is not None and not isinstance(v,bpy.types.ID):continue
                settings[p.identifier]=sorted(v) if isinstance(v,set) else value(v)
            rows[m.name]=settings
        result[o.name]=rows
    return result

bpy.ops.wm.open_mainfile(filepath=str(source));old=custody();old_fit=fit_weights();old_meta=metadata();old_modifiers=modifier_settings();old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering();cage=bpy.data.objects[edited[1]]
changed=set(edited)|set(build['body_taper']['shared_objects'])|{o.name for o in bpy.context.scene.objects if any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)}|{o.name for o in bpy.context.scene.objects if o.name.startswith('Walk surface | Character | raglan topstitch ')}
names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | ')) and o.name not in changed];old_geometry=geometry(names)
followers=[o.name for o in bpy.context.scene.objects if not o.hide_render and (('front welt' in o.name and any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)) or o.name.startswith('Walk surface | Character | raglan topstitch '))];assert len(followers)==6
baseline=screen('SOURCE',followers)
bpy.ops.wm.open_mainfile(filepath=str(candidate));new=custody()
for name in build['body_taper']['shared_objects']:
    key=build['body_taper']['added_key'];assert set(new[0][name]['keys'])-set(old[0][name]['keys'])=={key}
    new[0][name]['keys']={k:new[0][name]['keys'][k] for k in old[0][name]['keys']}
body=bpy.data.objects['Character | internal torso support'];key=body.data.shape_keys.key_blocks[build['body_taper']['added_key']];basis=body.data.shape_keys.key_blocks['Basis'];body_changes={r['id']:r for r in build['body_taper']['controls']}
assert key.value==1 and key.relative_key==basis and body.data==bpy.data.objects['Torso fit | isolated anatomical arm contact'].data
for i,v in enumerate(key.data):
    expected=body_changes[i]['delta_local_m'] if i in body_changes else (0.,0.,0.)
    expected_co=tuple(struct.unpack('f',struct.pack('f',basis.data[i].co[j]+expected[j]))[0] for j in range(3))
    assert tuple(v.co)==expected_co,('New taper key coordinate mismatch',i,tuple(v.co),expected_co)
assert new==old,'Original controls/edges/keys/UVs/maps/rest/six poses changed'
assert metadata()==old_meta,'Original metadata/unedited weights/old fields changed'
assert materials()==old_materials,'Original shaders changed'
new_fit=fit_weights();changes={r['id']:r for r in build['changed_controls']}
for i,(before,after) in enumerate(zip(old_fit,new_fit)):
    if i not in changes:assert before==after,('Undeclared fit influence change',i)
    else:
        row=changes[i];assert abs(row['old']-before)<1e-8 and abs(row['new']-after)<1e-7,('Declared influence mismatch',i)
for row in build['modifiers']:
    m=bpy.data.objects[row['object']].modifiers[row['name']]
    assert abs(m.offset-row['new_offset_m'])<1e-8 and m.target.name==row['target'] and m.vertex_group==build['fit_group']
new_modifiers=modifier_settings()
for row in build['modifiers']:
    assert abs(old_modifiers[row['object']][row['name']]['offset']-row['old_offset_m'])<1e-8
    new_modifiers[row['object']][row['name']]['offset']=old_modifiers[row['object']][row['name']]['offset']
shell=build['shell_correction']
for prop,row in shell['properties'].items():
    assert old_modifiers[shell['object']][shell['modifier']][prop]==row['old'] and new_modifiers[shell['object']][shell['modifier']][prop]==row['new']
    new_modifiers[shell['object']][shell['modifier']][prop]=row['old']
assert new_modifiers==old_modifiers,'Other editable modifier primitive/ID-reference properties changed'
assert action()==old_action and world()==old_world and lights()==old_lights and lettering()==old_text
assert geometry(names)==old_geometry,'Unedited human geometry changed'
frames=screen('CANDIDATE',followers)
for row,prior in zip(frames,baseline):
    new_self=self_cache['CANDIDATE'][row['frame']]-self_cache['SOURCE'][row['frame']];row['new_self_pair_count']=len(new_self);row['new_self_pair_examples']=sorted(new_self)[:12]
    new_pairs=pair_cache['CANDIDATE'][row['frame']]-pair_cache['SOURCE'][row['frame']];row['new_body_pair_count']=len(new_pairs);row['new_body_pair_examples']=sorted(new_pairs)[:12]
    for name,detail in row['sewn_details'].items():
        assert detail['maximum_sampled_gap_m']<prior['sewn_details'][name]['maximum_sampled_gap_m']+.003,('Sewn-detail gap regression',row['frame'],name)
        assert detail['maximum_edge_m']<prior['sewn_details'][name]['maximum_edge_m']*1.5+.002,('Sewn-detail edge regression',row['frame'],name)
report={'candidate_sha256':sha(candidate),'source_sha256':sha(source),'original_mesh_curve_count':len(old[0]),'packed_maps':len(old[1]),'original_controls_edges_old_keys_uvs_maps_rig_rest_six_poses_exact':True,'original_metadata_except_declared_fit_group_weights_fields_shaders_walk_world_lights_text_exact':True,'declared_fit_controls':len(changes),'geometry_surface_tessellation':'Blender evaluated mesh.loop_triangles at render subdivision','unchanged_visible_human_objects':len(names),'unchanged_human_six_pose_geometry_exact':True,'source_frames':baseline,'candidate_frames':frames,'scope':'Complete jacket shell versus internal body support, nonadjacent jacket shell pairs, and six visible sewing-detail sampled contact/edge bounds at render subdivision for all 49 authored integer frames. Original support contacts are recorded. Excludes full-body collision, subframes, physical cloth simulation, photographic acceptance and runtime.'}
report['declared_body_taper_controls']=len(body_changes)
report['new_body_key_deltas_and_shared_fitting_mesh_exact']=True
report['remaining_editable_modifier_primitive_id_reference_properties_exact']=True
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['new_self_pair_count']==0 for r in frames),'New jacket self pairs remain'
assert all(r['new_body_pair_count']==0 for r in frames),'New jacket/support pairs'
print('SLEEVE_CONTOUR_COLD_PASS',flush=True)
