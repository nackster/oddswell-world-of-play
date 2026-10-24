"""Cold source custody, registered pelvic anatomy and complete integer-frame garment checks."""
import bpy,ast,array,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';build=json.loads((out/'build-report.json').read_text());source=art/'SleeveContourCandidate/SleeveContour.blend';candidate=out/'BodyBalance.blend'
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering'))]:
    tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='127a003d16b624457dc8a8be809edbdda9666f314e892a5395102cef053c4517'
assert sha(candidate)==build['candidate_sha256']
coat_names=build['chest_key_value']['objects'];pant_names=build['front_hip_key']['objects'];bridge_name=build['pelvic_continuity']['object'];group_name=build['chest_rounding']['group']
def fields(mesh):
    result={}
    for a in mesh.attributes:
        if a.data_type=='FLOAT_VECTOR':result[a.name]=digest(a.data,'vector',3)
        elif a.data_type=='FLOAT':result[a.name]=digest(a.data,'value',1)
        elif a.data_type in ('INT','BOOLEAN','INT32_2D'):
            width=2 if a.data_type=='INT32_2D' else 1;buf=array.array('i',[0])*len(a.data)*width;a.data.foreach_get('value',buf);result[a.name]=hashlib.sha256(buf.tobytes()).hexdigest()
    return result
def metadata(names,normalize=False):
    result={};data_cache={};field_cache={}
    for name in names:
        o=bpy.data.objects[name];row={'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'parent_type':o.parent_type,'parent_bone':o.parent_bone,'render_hidden':o.hide_render,'viewport_hidden':o.hide_viewport,'materials':[s.material.name if s.material else None for s in o.material_slots]}
        if o.type=='MESH':
            exclude=o.vertex_groups[group_name].index if normalize and name in coat_names else None;cache_key=(o.data.as_pointer(),exclude)
            if cache_key not in data_cache:
                h=hashlib.sha256()
                for v in o.data.vertices:
                    weights=[w for w in v.groups if w.group!=exclude];h.update(struct.pack('<I',len(weights)))
                    for w in weights:h.update(struct.pack('<If',w.group,w.weight))
                data_cache[cache_key]=h.hexdigest()
            if o.data.as_pointer() not in field_cache:field_cache[o.data.as_pointer()]=fields(o.data)
            row.update(groups=[g.name for g in o.vertex_groups if not(normalize and name in coat_names and g.name==group_name)],weights=data_cache[cache_key],fields=field_cache[o.data.as_pointer()],key_values={k.name:k.value for k in o.data.shape_keys.key_blocks} if o.data.shape_keys else {})
            if normalize and name in pant_names:row['key_values'].pop(build['front_hip_key']['key'])
            if normalize and name in coat_names:row['key_values'][build['chest_key_value']['key']]=build['chest_key_value']['old']
        mods=[]
        for m in o.modifiers:
            if normalize and name in coat_names and m.name==build['chest_rounding']['modifier']:continue
            props={}
            for p in m.bl_rna.properties:
                # is_active selects the modifier shown in Blender's properties editor; it does not affect geometry.
                if p.is_readonly or p.identifier in ('rna_type','is_active') or p.type=='COLLECTION':continue
                v=getattr(m,p.identifier)
                if p.type=='POINTER' and v is not None and not isinstance(v,bpy.types.ID):continue
                props[p.identifier]=sorted(v) if isinstance(v,set) else value(v)
            if normalize and name in coat_names and m.name==build['tension_group']['modifier']:props['node_group']=build['tension_group']['old']
            mods.append((m.name,m.type,props))
        if normalize and name in coat_names:
            outside=next(r for r in mods if r[0]=='Free cloth outside anatomical support');mods.remove(outside);mods.insert(next(i for i,r in enumerate(mods) if r[0]=='Front-quarter cotton tension folds'),outside)
        row['modifiers']=mods;result[name]=row
    return result
def dependencies(seed):
    changed=set(seed)
    def group_targets(group,visited):
        if group is None or group.as_pointer() in visited:return set()
        visited.add(group.as_pointer());targets=set()
        for node in group.nodes:
            for sock in node.inputs:
                if hasattr(sock,'default_value') and isinstance(sock.default_value,bpy.types.Object):targets.add(sock.default_value.name)
            if hasattr(node,'node_tree'):targets|=group_targets(node.node_tree,visited)
        return targets
    while True:
        prior=len(changed)
        for o in bpy.context.scene.objects:
            if o.type not in ('MESH','CURVE'):continue
            targets=set()
            for m in o.modifiers:
                if hasattr(m,'target') and isinstance(m.target,bpy.types.Object):targets.add(m.target.name)
                if m.type=='NODES':targets|=group_targets(m.node_group,set())
            if targets&changed:changed.add(o.name)
        if len(changed)==prior:return changed
bpy.ops.wm.open_mainfile(filepath=str(source));old=custody();names=[o.name for o in bpy.context.scene.objects if o.type in ('MESH','CURVE')];old_meta=metadata(names);old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering();changed=dependencies(set(coat_names)|set(pant_names));unchanged=[n for n in names if not bpy.data.objects[n].hide_render and n.startswith(('Character | ','Walk surface | Character | ')) and n not in changed];old_geometry=geometry(unchanged)
print('BODY_BALANCE_SOURCE_CUSTODY',len(names),len(unchanged),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(candidate));new=custody();new[0].pop(bridge_name)
for n in pant_names:new[0][n]['keys'].pop(build['front_hip_key']['key'])
assert new==old,'Original controls/edges/old keys/UVs/maps/rest/six poses changed'
new_meta=metadata(names,True)
def differences(a,b,path=''):
    if type(a)!=type(b):return [(path,a,b)]
    if isinstance(a,dict):
        result=[]
        for k in set(a)|set(b):
            if k not in a or k not in b:result.append((path+'/'+str(k),a.get(k),b.get(k)))
            else:result+=differences(a[k],b[k],path+'/'+str(k))
        return result
    if isinstance(a,(tuple,list)):
        if len(a)!=len(b):return [(path+'/length',len(a),len(b))]
        result=[]
        for i,(x,y) in enumerate(zip(a,b)):result+=differences(x,y,path+'/'+str(i))
        return result
    return [] if a==b else [(path,a,b)]
diff=differences(old_meta,new_meta)
(out/'metadata-diff.json').write_text(json.dumps(diff,indent=2)+'\n')
print('BODY_BALANCE_METADATA_DIFF',len(diff),diff[:12],flush=True)
assert not diff,'Undeclared original metadata/fields/weights/key values/modifier settings changed'
assert materials()==old_materials and action()==old_action and world()==old_world and lights()==old_lights and lettering()==old_text,'Original shaders/walk/world/lights/text changed'
assert geometry(unchanged)==old_geometry,'Unedited visible character geometry changed'
def exact_key(o,name,rows):
    key=o.data.shape_keys.key_blocks[name];basis=o.data.shape_keys.key_blocks['Basis'];changes={r['id']:r for r in rows};assert key.value==1 and key.relative_key==basis
    for i,v in enumerate(key.data):
        d=changes[i]['delta_local_m'] if i in changes else (0,0,0);expected=tuple(struct.unpack('f',struct.pack('f',basis.data[i].co[j]+d[j]))[0] for j in range(3));assert tuple(v.co)==expected,('Unexpected key coordinate',o.name,i)
exact_key(bpy.data.objects[pant_names[0]],build['front_hip_key']['key'],build['front_hip_key']['controls']);bridge=bpy.data.objects[bridge_name];exact_key(bridge,build['pelvic_continuity']['key'],build['pelvic_continuity']['controls'])
assert bpy.data.objects[pant_names[0]].data==bpy.data.objects[pant_names[1]].data and bpy.data.objects[coat_names[0]].data==bpy.data.objects[coat_names[1]].data
for n in coat_names:
    o=bpy.data.objects[n];assert o.data.shape_keys.key_blocks[build['chest_key_value']['key']].value==.25;weights={r['id']:r['weight'] for r in build['chest_rounding']['weights']};g=o.vertex_groups[group_name]
    for v in o.data.vertices:
        actual=next((w.weight for w in v.groups if w.group==g.index),0.);expected=struct.unpack('f',struct.pack('f',weights.get(v.index,0.)))[0];assert actual==expected
    m=o.modifiers[build['chest_rounding']['modifier']];assert m.iterations==18 and abs(m.factor-.65)<1e-7 and m.vertex_group==group_name
    group=o.modifiers[build['tension_group']['modifier']].node_group;node=group.nodes['Reduced chest ridge prominence'];assert node.operation=='MULTIPLY' and node.inputs[1].links[0].from_node.name=='Preserve relief outside front chest'
    mask=group.nodes['Local front chest relief mask'];amount=group.nodes['Local chest relief reduction'];factor=group.nodes['Preserve relief outside front chest'];assert mask.data_type=='FLOAT' and mask.inputs['Name'].default_value==group_name and amount.operation=='MULTIPLY' and abs(amount.inputs[1].default_value-.65)<1e-7 and factor.operation=='SUBTRACT' and factor.inputs[0].default_value==1.
    assert amount.inputs[0].links[0].from_node==mask and factor.inputs[1].links[0].from_node==amount
original_bridge=bpy.data.objects[build['pelvic_continuity']['source_object']];assert digest(bridge.data.vertices,'co',3)==digest(original_bridge.data.vertices,'co',3) and digest(bridge.data.edges,'vertices',2)==digest(original_bridge.data.edges,'vertices',2) and fields(bridge.data)==fields(original_bridge.data)
for k in original_bridge.data.shape_keys.key_blocks:assert digest(k.data,'co',3)==digest(bridge.data.shape_keys.key_blocks[k.name].data,'co',3)
bridge_points=[v.co.copy() for v in bridge.data.shape_keys.key_blocks['Basis'].data]
for k in bridge.data.shape_keys.key_blocks[1:]:
    if k.value:
        for i,p in enumerate(bridge_points):p+=(k.data[i].co-k.relative_key.data[i].co)*k.value
anchor_errors=[(bridge.matrix_world@bridge_points[r['id']]-Vector(r['target_world_m'])).length for r in build['pelvic_continuity']['anchors']];assert max(anchor_errors)<5e-7
for v,p in zip(bridge.data.vertices,bridge_points):
    q=bridge.matrix_world@p;t=max(0.,min(1.,(q.z-.695)/.170));pelvic=t*t*(3-2*t);side='neg' if q.x<-.75 else 'pos';weights={bridge.vertex_groups[w.group].name:w.weight for w in v.groups if bridge.vertex_groups[w.group].name in bpy.data.objects['Walk study | native anatomical controls'].data.bones};assert abs(sum(weights.values())-1)<1e-7 and abs(weights.get('pelvis',0)-pelvic)<1e-7 and abs(weights.get(side+'.thigh',0)-(1-pelvic))<1e-7
print('BODY_BALANCE_COLD_CUSTODY_PASS',flush=True)
# The surface screen is separate from custody and uses actual evaluated draw triangles.
def surface(o,deps):
    ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];e=[tuple(x.vertices) for x in m.edges];ev.to_mesh_clear();return p,f,e,BVHTree.FromPolygons(p,f,all_triangles=True)
source_pairs={};frames={}
for label,path in [('SOURCE',source),('CANDIDATE',candidate)]:
    bpy.ops.wm.open_mainfile(filepath=str(path));objects=['Character | tailored slate jacket','Character | shorts leg continuous tailoring','Character | internal torso support','Character | anatomical legs'];objects+=([bridge_name] if label=='CANDIDATE' else [])
    for n in objects+['Walk cage | refined jacket surface','Hip study | registered cloth midsurface']:
        for m in bpy.data.objects[n].modifiers:
            if m.type=='SUBSURF':m.levels=m.render_levels
    followers=sorted(n for n in changed if n not in set(coat_names)|set(pant_names) and n in bpy.data.objects and not bpy.data.objects[n].hide_render and bpy.data.objects[n].type in ('MESH','CURVE'));rows=[]
    for frame in range(1,50):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();surfaces={n:surface(bpy.data.objects[n],deps) for n in objects};row={'frame':frame};sets={}
        for clothing in objects[:2]:
            p,f,e,tree=surfaces[clothing];tag=clothing+' self';ps={(i,j) for i,j in tree.overlap(tree) if i<j and not set(f[i]).intersection(f[j])};sets[tag]=ps;row[tag]=len(ps)
            for skin in objects[2:] if clothing==objects[1] else objects[2:3]:
                tag=clothing+' / '+skin;ps=set(tree.overlap(surfaces[skin][3]));sets[tag]=ps;row[tag]=len(ps)
        details={}
        for n in followers:
            p,f,e,tree=surface(bpy.data.objects[n],deps);target=objects[1] if any(word in n.lower() for word in ('short','cotton','pocket','hem','waist')) and 'jacket' not in n.lower() and 'front welt' not in n.lower() else objects[0];details[n]={'target':target,'maximum_sampled_gap_m':max(surfaces[target][3].find_nearest(v)[3] for v in p[::4]),'maximum_edge_m':max((p[a]-p[b]).length for a,b in e)}
        row['sewn_details']=details
        if label=='SOURCE':source_pairs[frame]=sets
        else:
            row['new_pairs']={tag:len(ps-source_pairs[frame][tag]) for tag,ps in sets.items() if tag in source_pairs[frame]};p,f,e,tree=surfaces[bridge_name];row['continuous_skin_self']=sum(i<j and not set(f[i]).intersection(f[j]) for i,j in tree.overlap(tree))
        rows.append(row);print('BODY_BALANCE_FRAME',label,frame,row[objects[1]+' self'],row.get('continuous_skin_self'),flush=True)
    frames[label]=rows
(out/'surface-screen.json').write_bytes((json.dumps({'source_sha256':sha(source),'candidate_sha256':sha(candidate),'frames':frames},indent=2)+'\n').encode())
for row,prior in zip(frames['CANDIDATE'],frames['SOURCE']):
    assert row['new_pairs'][objects[0]+' self']==0 and row['new_pairs'][objects[0]+' / '+objects[2]]==0
    assert row['new_pairs'][objects[1]+' self']==0,('New shorts self pairs',row['frame'],row['new_pairs'][objects[1]+' self'])
    assert row[objects[1]+' / '+objects[3]]==row['continuous_skin_self']==0
    for n,d in row['sewn_details'].items():
        assert d['maximum_sampled_gap_m']<prior['sewn_details'][n]['maximum_sampled_gap_m']+.004,('Sewing gap',row['frame'],n)
        assert d['maximum_edge_m']<prior['sewn_details'][n]['maximum_edge_m']*1.5+.002,('Sewing edge',row['frame'],n)
report={'source_sha256':sha(source),'candidate_sha256':sha(candidate),'packed_maps':len(old[1]),'original_controls_edges_old_keys_uv_maps_rig_rest_six_poses_exact':True,'original_metadata_fields_weights_shaders_walk_world_lights_text_except_declared_changes_exact':True,'unchanged_visible_human_objects':len(unchanged),'unchanged_six_pose_geometry_exact':True,'new_shape_coordinates_and_shared_cloth_data_exact':True,'original_source_pelvis_controls_topology_keys_fields_retained':True,'pelvic_anchor_maximum_error_m':max(anchor_errors),'pelvic_weights_normalized':True,'surface_method':'Blender evaluated mesh.loop_triangles at render subdivision','source_frames':frames['SOURCE'],'candidate_frames':frames['CANDIDATE'],'sewn_follower_count':len(followers),'scope':'Complete garment self pairs, jacket versus retained torso support, shorts versus visible actual legs, continuous fitting skin self pairs and source-relative sewn follower bounds over 49 authored integer frames. Shorts versus retained torso/new fitting skin contacts are recorded, not certified collision-free. Excludes subframes, complete visible body/cloth contact, physical simulation, runtime and final photographic acceptance.'}
(out/'cold-audit.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('BODY_BALANCE_COLD_PASS',flush=True)
