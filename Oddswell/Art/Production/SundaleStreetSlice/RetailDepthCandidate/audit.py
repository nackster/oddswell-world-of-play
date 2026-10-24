"""Cold source preservation for a localized static storefront refinement."""
import bpy,ast,array,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';helper=art/'HipSeatMotionCandidate/audit.py';parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody')],type_ignores=[]),str(helper),'exec'));source=art/'ShoulderChestCandidate/ShoulderChest.blend';candidate=out/'RetailDepth.blend';build=json.loads((out/'build-report.json').read_text())
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='8b2f0e5634f1198bbdbb5054c961668cb86825764ada8d24355296cbc290de7a'
def value(v):
    if v is None or isinstance(v,(str,int,float,bool)):return v
    if hasattr(v,'name'):return v.name
    try:return list(v)
    except TypeError:return str(v)
def materials():
    result={}
    for mat in bpy.data.materials:
        if not mat.use_nodes:result[mat.name]={'diffuse':list(mat.diffuse_color)};continue
        result[mat.name]={'diffuse':list(mat.diffuse_color),'nodes':[{'name':n.name,'type':n.type,'operation':getattr(n,'operation',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'projection':getattr(n,'projection',None),'uv_map':getattr(n,'uv_map',None),'inputs':[(s.name,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')],'ramp':[(e.position,list(e.color)) for e in n.color_ramp.elements] if hasattr(n,'color_ramp') else None} for n in mat.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links]}
    return result
def action():
    rig=bpy.data.objects['Walk study | native anatomical controls'];a=rig.animation_data.action
    return [(f.data_path,f.array_index,[(list(k.co),k.interpolation,list(k.handle_left),list(k.handle_right),k.handle_left_type,k.handle_right_type) for k in f.keyframe_points]) for f in a.fcurves]
def geometry(names):
    result={}
    for frame in (1,7,13,25,33,49):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();row={}
        for name in names:
            obj=bpy.data.objects[name];ev=obj.evaluated_get(deps);mesh=ev.to_mesh();row[name]={'co':digest(mesh.vertices,'co',3),'edges':digest(mesh.edges,'vertices',2),'matrix_world':[v for r in ev.matrix_world for v in r]};ev.to_mesh_clear()
        result[frame]=row;print('RETAIL_CHARACTER_POSE',frame,len(names),flush=True)
    return result
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();before_materials=materials();before_action=action();names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | '))];before_geometry=geometry(names);source_visibility={o.name:o.hide_render for o in bpy.context.scene.objects};source_transforms={o.name:([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone) for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody();after_materials=materials();after_action=action();after_geometry=geometry(names)
assert ({n:after[0][n] for n in before[0]},*after[1:])==before,'Original controls/UVs/keys/maps/rig changed';assert {n:after_materials[n] for n in before_materials}==before_materials,'Original shader changed';assert before_action==after_action,'Walk animation curves changed';assert before_geometry==after_geometry,'Main character evaluated geometry changed'
bpy.context.scene.frame_set(49)
for name,record in source_transforms.items():
    o=bpy.data.objects[name];assert ([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone)==record,('Original transform/parent changed',name)
changed=set(r['name'] for r in build['changed_visibility']);assert {n for n,v in source_visibility.items() if bpy.data.objects[n].hide_render!=v}==changed
for name in changed:assert bpy.data.objects[name].hide_render
collection=bpy.data.collections['OddsWell | foreground retail refinement'];assert set(o.name for o in collection.objects)==set(build['added_objects']);assert all(not o.hide_render for o in collection.objects)
for name in ('Retail | hanging OddsWell jacket A','Retail | hanging OddsWell jacket B'):
    o=bpy.data.objects[name];assert not o.parent and not o.modifiers and o.type=='MESH';assert o.data.uv_layers['Physical rest jacket weave']
assert bpy.data.objects['Retail | hanging OddsWell jacket A'].data==bpy.data.objects['Retail | hanging OddsWell jacket B'].data
prior=json.loads((source.parent/'cold-audit.json').read_text());assert prior['candidate_sha256']==build['source_sha256'] and len(prior['frames'])==49 and max(r['shell_self_pairs'] for r in prior['frames'])==0
report={'candidate_sha256':sha(candidate),'source_sha256':build['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_keys_maps_rest_and_six_poses_exact':True,'original_shader_values_links_exact':True,'native_walk_keyframes_handles_interpolation_exact':True,'visible_main_character_objects':len(names),'six_pose_visible_character_coordinates_edges_world_matrices_exact':True,'original_object_transforms_parents_exact':True,'documented_visibility_changes':len(changed),'new_collection_objects':len(collection.objects),'shared_static_jacket_mesh':True,'inherited_human_audit':'Immediate ShoulderChestCandidate/cold-audit.json retains its scoped 49 integer-frame human jacket/cloth proof. This static room study preserves all visible character geometry in six poses and full native keyframe data; it does not repeat or broaden that physical check.','scope':'Localized static storefront room/display refinement and documented original visibility changes. All original editable sources, licensed maps, shaders, rig and visible character preserved. Does not certify walkable retail entry, shop collision/LOD/performance, full-body collision freedom, final reference fidelity, engine integration or beta readiness.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('RETAIL_COLD_PASS',flush=True)
