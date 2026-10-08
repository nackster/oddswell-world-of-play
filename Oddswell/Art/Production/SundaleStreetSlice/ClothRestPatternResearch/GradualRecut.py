"""Native physical rest-drape study; preserve original scene sources as separate editable objects."""
import bpy,bmesh,json,hashlib,ast,math
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';source=art/'UpperHipHandCandidate/UpperDrape.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)=='90af187cf9cfa558f4d06a4b7398d02a8097991309e06789dbf61b0ebc36afeb'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);rig=bpy.data.objects['Walk study | native anatomical controls'];original_action=rig.animation_data.action;original_end=scene.frame_end;pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];waist=json.loads((art/'WaistJoinCandidate/build-report.json').read_text())['waist_boundary_ids']
# Get the actual authored rest cloth before render subdivision/thickness.
flags=[(m,m.show_viewport) for m in pants.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
for m,_ in flags:m.show_viewport=False
bpy.context.view_layer.update();ev=pants.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();initial=[ev.matrix_world@v.co for v in mesh.vertices];assert len(initial)==len(pants.data.vertices);ev.to_mesh_clear()
for m,flag in flags:m.show_viewport=flag
# Close the retained source-derived lower body for the diagnostic collision volume.
points=[];faces=[];deps=bpy.context.evaluated_depsgraph_get()
for name in ('Character | anatomical legs','Character | continuous pelvis and upper thigh fitting','Character | internal torso support'):
    o=bpy.data.objects[name];ev=o.evaluated_get(deps);m=ev.to_mesh();ps=[ev.matrix_world@v.co for v in m.vertices];start=len(points);points.extend(ps)
    for f in m.polygons:
        center=sum((ps[i] for i in f.vertices),Vector())/len(f.vertices)
        if center.z<=1.03 and abs(center.x+.75)<.255:faces.append(tuple(start+i for i in f.vertices))
    ev.to_mesh_clear()
mesh=bpy.data.meshes.new('Closed licensed lower body collision volume');mesh.from_pydata(points,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
collection=bpy.data.collections.new('Recut cotton | diagnostic collider collection');scene.collection.children.link(collection);collider=bpy.data.objects.new('Recut cotton | closed lower body contact',mesh);collection.objects.link(collider);collider.hide_render=True;collider.display_type='WIRE';bpy.context.view_layer.objects.active=collider;collider.select_set(True);remesh=collider.modifiers.new('Closed continuous diagnostic skin','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.005;remesh.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=remesh.name);collider.modifiers.new('Recut cotton skin collision','COLLISION');collider.collision.thickness_outer=.002
# Physical integration runs with the exact source frame-1 body pose held still.
rig.animation_data.action=None;scene.frame_end=180
cloth=pants.copy();cloth.data=pants.data.copy();cloth.name='Character | recut settled cotton shorts';scene.collection.objects.link(cloth);cloth.parent=None;cloth.matrix_world=Matrix.Identity(4);cloth.shape_key_clear()
for m in list(cloth.modifiers):cloth.modifiers.remove(m)
for v,p in zip(cloth.data.vertices,initial):v.co=p
cloth.hide_render=False;pin=cloth.vertex_groups.new(name='Physical waist boundary pin');pin.add(waist,1.,'REPLACE')
# Exact waist and hem boundaries; grade pinning into one nearby control band.
boundary=set(waist)
edge_faces={tuple(sorted(e.vertices)):0 for e in cloth.data.edges}
for face in cloth.data.polygons:
    for a,b in zip(face.vertices,list(face.vertices[1:])+[face.vertices[0]]):edge_faces[tuple(sorted((a,b)))]+=1
for edge,count in edge_faces.items():
    if count==1:boundary.update(edge)
pin.add(sorted(boundary),1.,'REPLACE')
adj=[[] for _ in initial]
for edge in cloth.data.edges:
    a,b=edge.vertices;adj[a].append(b);adj[b].append(a)
for i in sorted({j for i in boundary for j in adj[i]}-boundary):pin.add([i],.85,'REPLACE')
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
shrink=cloth.vertex_groups.new(name='Graded upper leg pattern reduction');shrink_rows=[]
clear_group=cloth.vertex_groups.new(name='Free cloth initial skin fitting')
for i,p in enumerate(initial):
    w=smooth((p.z-.615)/.065)*(1-smooth((p.z-.825)/.065))
    if i in boundary:w=0.
    elif any(j in boundary for j in adj[i]):w*=.15
    if w>1e-7:shrink.add([i],w,'REPLACE');shrink_rows.append({'id':i,'weight':w})
    if i not in boundary and not any(j in boundary for j in adj[i]):clear_group.add([i],1.,'REPLACE')

clear=cloth.modifiers.new('Initial outside diagnostic skin','SHRINKWRAP');clear.target=collider;clear.wrap_method='NEAREST_SURFACEPOINT';clear.wrap_mode='OUTSIDE';clear.offset=.0025;clear.vertex_group=clear_group.name
physics=cloth.modifiers.new('Native cotton rest settling','CLOTH');settings=physics.settings;settings.quality=24;settings.time_scale=.25;settings.mass=.00004;settings.tension_stiffness=15;settings.compression_stiffness=15;settings.shear_stiffness=5;settings.bending_stiffness=.10;settings.tension_damping=20;settings.compression_damping=20;settings.shear_damping=20;settings.bending_damping=2;settings.air_damping=4;settings.vertex_group_mass=pin.name;settings.pin_stiffness=1;settings.vertex_group_shrink=shrink.name;settings.shrink_min=0.;settings.shrink_max=0.;settings.keyframe_insert(data_path="shrink_max",frame=1);settings.shrink_max=.08;settings.keyframe_insert(data_path="shrink_max",frame=40)
collision=physics.collision_settings;collision.collection=collection;collision.collision_quality=10;collision.distance_min=.002;collision.use_self_collision=True;collision.self_distance_min=.0015;collision.self_friction=5;collision.friction=8;physics.point_cache.frame_start=1;physics.point_cache.frame_end=180
trace=[];previous=None;final=None
for frame in range(1,181):
    scene.frame_set(frame);bpy.context.view_layer.update();ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();final=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear();assert len(final)==len(initial)
    step=max((a-b).length for a,b in zip(final,previous)) if previous else 0.;row={'frame':frame,'pattern_shrink':settings.shrink_max,'maximum_step_m':step,'maximum_from_source_m':max((a-b).length for a,b in zip(final,initial)),'waist_maximum_from_source_m':max((final[i]-initial[i]).length for i in waist),'all_boundary_maximum_from_source_m':max((final[i]-initial[i]).length for i in boundary)};trace.append(row);previous=final
    if frame==1 or frame%5==0:print('STABLE_RECUT_STEP',frame,json.dumps(row),flush=True)
# Retain the solver and its tunings, plus an editable rest result for the native walk.
clear.show_viewport=clear.show_render=False;physics.show_viewport=physics.show_render=False;cloth.shape_key_add(name='Basis');key=cloth.shape_key_add(name='Native recut settled cotton rest');key.value=1.
for v,p in zip(key.data,final):v.co=p
arm=cloth.modifiers.new('Native walk of settled cotton','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True;cloth.modifiers.move(len(cloth.modifiers)-1,0);sub=cloth.modifiers.new('Continuous recut settled cotton','SUBSURF');sub.levels=sub.render_levels=2;solid=cloth.modifiers.new('Retained cotton thickness','SOLIDIFY');old_solid=next(m for m in pants.modifiers if m.type=='SOLIDIFY');solid.thickness=old_solid.thickness;solid.offset=old_solid.offset;solid.use_even_offset=old_solid.use_even_offset;solid.thickness_clamp=old_solid.thickness_clamp
newmid=cloth.copy();newmid.data=cloth.data;newmid.name='Recut cotton | registered settled midsurface';scene.collection.objects.link(newmid);newmid.hide_render=True
for m in list(newmid.modifiers):
    if m.type in ('CLOTH','SHRINKWRAP','SOLIDIFY'):newmid.modifiers.remove(m)
# Reuse original sewing registrations on identical point/face topology and UVs.
substitutions={pants:cloth,mid:newmid};copied={};retargeted=[]
def retarget_group(original):
    if original is None:return original
    if original.as_pointer() in copied:return copied[original.as_pointer()]
    nested={n.name:retarget_group(n.node_tree) for n in original.nodes if hasattr(n,'node_tree') and n.node_tree}
    direct=any(hasattr(s,'default_value') and isinstance(s.default_value,bpy.types.Object) and s.default_value in substitutions for n in original.nodes for s in n.inputs)
    if not direct and all(nested[n.name]==n.node_tree for n in original.nodes if n.name in nested):copied[original.as_pointer()]=original;return original
    group=original.copy();group.name='Recut cotton | '+original.name;copied[original.as_pointer()]=group
    for node in group.nodes:
        if node.name in nested:node.node_tree=nested[node.name]
        for sock in node.inputs:
            if hasattr(sock,'default_value') and isinstance(sock.default_value,bpy.types.Object) and sock.default_value in substitutions:sock.default_value=substitutions[sock.default_value]
    return group
for o in list(scene.objects):
    if o in (pants,mid,cloth,newmid,collider):continue
    changed=[]
    for m in o.modifiers:
        if hasattr(m,'target') and m.target in substitutions:changed.append(m.name);m.target=substitutions[m.target]
        if m.type=='NODES':
            group=retarget_group(m.node_group)
            if group!=m.node_group:changed.append(m.name);m.node_group=group
    if changed:retargeted.append({'object':o.name,'modifiers':changed})
pants.hide_render=True;rig.animation_data.action=original_action;scene.frame_end=original_end;scene.frame_set(1);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'StableRecut.blend'),compress=True)
report={'source_sha256':sha(source),'candidate_sha256':sha(out/'StableRecut.blend'),'physical_solver':'Blender 4.5.5 native Cloth, 180 consecutive frames with source body held at frame 1','settings':{'quality':24,'time_scale':settings.time_scale,'pattern_shrink_target':.08,'ramp_frames':[1,40],'mass':settings.mass,'uniform_total_mass_kg':settings.mass*len(initial),'pattern_shrink_min':settings.shrink_min,'pattern_shrink_max':settings.shrink_max,'tension':15,'compression':15,'shear':5,'bending':settings.bending_stiffness,'collision_distance':.002,'self_distance':.0015,'collision_quality':10},'diagnostic_skin_voxel_m':.005,'collider_vertices':len(collider.data.vertices),'cloth_vertices':len(cloth.data.vertices),'waist_boundary_ids':waist,'all_pinned_boundary_ids':sorted(boundary),'shrink_weights':shrink_rows,'trace':trace,'original_action_restored':original_action.name,'original_objects_retained':[pants.name,mid.name],'visible_cloth_object':cloth.name,'registered_midsurface':newmid.name,'coupled_retargeted_objects':retargeted,'scope':'Physical rest-shape study with source rig restored and native walking applied to the settled rest shape. Solver tunings are art parameters, not calibrated material measurements. Whole-walk contacts, seam registration, visual acceptance and runtime remain unproven.'}
(out/'build-report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('STABLE_RECUT_BUILT',report['candidate_sha256'],flush=True)
