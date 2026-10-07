"""Cold source preservation for a promenade sightline and lighting refinement."""
import bpy,ast,array,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';helper=art/'HipSeatMotionCandidate/audit.py';parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody')],type_ignores=[]),str(helper),'exec'));source=art/'ArenaArrivalCandidate/ArenaArrival.blend';candidate=out/'PromenadeLight.blend';build=json.loads((out/'build-report.json').read_text())
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='4be22d54515ef82276331c3286147e5f77dad9ddc2491d4e29d39eaf720cd524'
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
        result[frame]=row;print('PROMENADE_CHARACTER_POSE',frame,len(names),flush=True)
    return result
from mathutils import Vector,Matrix
def world():
    w=bpy.context.scene.world
    return {'nodes':[(n.name,n.type,getattr(n,'image',None).name if getattr(n,'image',None) else None,[(s.name,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]) for n in w.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in w.node_tree.links]}
def lights():
    return {o.name:(o.data.name,o.data.type,o.data.energy,list(o.data.color),getattr(o.data,'size',None),getattr(o.data,'angle',None),getattr(o.data,'shape',None)) for o in bpy.context.scene.objects if o.type=='LIGHT'}
def lettering():
    return {o.name:(o.data.body,o.data.size,o.data.extrude) for o in bpy.context.scene.objects if o.type=='FONT'}
def sightline():
    scene=bpy.context.scene;scene.frame_set(7);camera=bpy.data.objects['CAM | gameplay street'];deps=bpy.context.evaluated_depsgraph_get();rows=[]
    for kind,xs,zs,y in [('Canopy',[-.5,1.25,3,4.75,6.5],[4.50,4.72,4.94],64.94),('Doors',[0,1.5,3,4.5,6],[1.85,2.85,4.2],66.60)]:
        for x in xs:
            for z in zs:
                target=Vector((x,y,z));direction=(target-camera.location).normalized();distance=(target-camera.location).length;hit,loc,normal,index,obj,matrix=scene.ray_cast(deps,camera.location,direction,distance=distance-.005)
                rows.append({'kind':kind,'target':list(target),'blocker':obj.name if hit else None})
    return rows

bpy.ops.wm.open_mainfile(filepath=str(source));before_world=world();before_lights=lights();before_text=lettering();before_rays=sightline();before=custody();before_materials=materials();before_action=action();names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | '))];before_geometry=geometry(names);source_visibility={o.name:o.hide_render for o in bpy.context.scene.objects};source_transforms={o.name:([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone) for o in bpy.context.scene.objects}
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=custody();after_materials=materials();after_action=action();after_geometry=geometry(names)
assert ({n:after[0][n] for n in before[0]},*after[1:])==before,'Original controls/UVs/keys/maps/rig changed';assert {n:after_materials[n] for n in before_materials}==before_materials,'Original shader changed';assert before_action==after_action,'Walk animation curves changed';assert before_geometry==after_geometry,'Main character evaluated geometry changed'
bpy.context.scene.frame_set(49)
for name,record in source_transforms.items():
    o=bpy.data.objects[name];move=next((r for r in build['object_moves'] if r['name']==name),None)
    if move:
        expected_matrix=Matrix([record[0][j:j+4] for j in range(0,16,4)]);expected_matrix.translation+=Vector(move['delta'])
        assert max(abs(o.matrix_world[i][j]-expected_matrix[i][j]) for i in range(4) for j in range(4))<.00001,('Incorrect declared move',name)
        assert max(abs(o.location[i]-move['new_location'][i]) for i in range(3))<.00001
        assert (o.parent.name if o.parent else None,o.parent_type,o.parent_bone)==tuple(record[1:])
    else:assert ([v for r in o.matrix_world for v in r],o.parent.name if o.parent else None,o.parent_type,o.parent_bone)==record,('Undeclared original transform/parent changed',name)
changed=set(r['name'] for r in build['changed_visibility']);assert {n for n,v in source_visibility.items() if bpy.data.objects[n].hide_render!=v}==changed
for name in changed:assert bpy.data.objects[name].hide_render
collection=bpy.data.collections['OddsWell | promenade light refinement'];assert set(o.name for o in collection.objects)==set(build['added_objects']);assert all(not o.hide_render for o in collection.objects)
assert world()==before_world,'World lighting changed'
assert {n:lights()[n] for n in before_lights}==before_lights,'Original light data changed'
assert lettering()==before_text,'Native lettering changed'
assert len(build['object_moves'])==35
lamp_names=[r['name'] for r in build['object_moves'] if r['group']=='court-edge lamp row'];assert len(lamp_names)==27
for name in lamp_names:
    o=bpy.data.objects[name];assert max((o.matrix_world@Vector(p)).x for p in o.bound_box)<2.5,'Lamp crosses blue court edge'
tree=bpy.data.objects['Tree | mature Sundale broadleaf.007'];soil=bpy.data.objects['Tree pit soil.007'];center=sum((soil.matrix_world@Vector(p) for p in soil.bound_box),Vector())/8
assert abs(tree.location.x-center.x)<.0001 and abs(tree.location.y-center.y)<.0001,'Tree/soil moved separately'
for r in build['light_copies']:
    o=bpy.data.objects[r['new']];assert o.data.name!=r['source_data'] and o.data.energy==r['new_energy']
    assert o.matrix_world==bpy.data.objects[r['source']].matrix_world
after_rays=sightline();before_blocked=sum(r['blocker'] is not None for r in before_rays);after_blocked=sum(r['blocker'] is not None for r in after_rays)
assert after_blocked<=8 and after_blocked<before_blocked/2,('Sightline improvement insufficient',before_blocked,after_blocked)
prior=json.loads((source.parent/'cold-audit.json').read_text());assert prior['candidate_sha256']==build['source_sha256']
report={'candidate_sha256':sha(candidate),'source_sha256':build['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_keys_maps_rest_and_six_poses_exact':True,'original_shader_world_light_data_lettering_exact':True,'native_walk_keyframes_handles_interpolation_exact':True,'visible_main_character_objects':len(names),'six_pose_visible_character_coordinates_edges_world_matrices_exact':True,'original_object_transforms_exact_except_declared_moves':True,'documented_object_moves':35,'documented_visibility_changes':len(changed),'new_collection_objects':len(collection.objects),'lamps_outside_blue_court_edge':True,'tree_and_soil_center_aligned':True,'source_sightline_rays':before_rays,'candidate_sightline_rays':after_rays,'source_blocked_rays':before_blocked,'candidate_blocked_rays':after_blocked,'inherited_human_audit':'Immediate ArenaArrivalCandidate preserves the ShoulderChestCandidate human; its scoped 49-frame cloth proof is not broadened here.','scope':'Native scene composition and two copied bounce lights. Original control geometry/maps/shaders/rig/walk retained; 35 declared group translations and two original light visibility changes. Six-pose visible human exact. Thirty camera-to-arrival geometric rays are conservative, ignoring leaf alpha transparency, and do not establish full optical visibility, route clearance, runtime collision/performance or final reference fidelity.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PROMENADE_COLD_PASS',before_blocked,after_blocked,flush=True)
