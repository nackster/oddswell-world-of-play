import bpy,json,hashlib,heapq
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';source=art/'UpperHipHandCandidate/UpperDrape.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)=='90af187cf9cfa558f4d06a4b7398d02a8097991309e06789dbf61b0ebc36afeb'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];
late=[(m,m.show_viewport) for m in pants.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
for m,_ in late:m.show_viewport=False
bpy.context.view_layer.update();ev=pants.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
for m,state in late:m.show_viewport=state
bpy.context.view_layer.update();assert len(points)==len(pants.data.vertices)
# Preserve the complete source pose/fold pipeline; add fitting immediately before subdivision.
pants.data=pants.data.copy();mid.data=pants.data;uv=pants.data.uv_layers['Four cut cotton panels'];front=[[] for _ in points];adj=[[] for _ in points];counts={tuple(sorted(e.vertices)):0 for e in pants.data.edges}
for face in pants.data.polygons:
    for a,b in zip(face.vertices,list(face.vertices[1:])+[face.vertices[0]]):counts[tuple(sorted((a,b)))]+=1
    for li in face.loop_indices:front[pants.data.loops[li].vertex_index].append(float(uv.data[li].uv.y<.5))
boundary={i for edge,c in counts.items() if c==1 for i in edge};dist=[float('inf')]*len(points);queue=[]
for i in boundary:dist[i]=0.;heapq.heappush(queue,(0.,i))
for e in pants.data.edges:
    a,b=e.vertices;d=(points[a]-points[b]).length;adj[a].append((b,d));adj[b].append((a,d))
while queue:
    d,i=heapq.heappop(queue)
    if d!=dist[i]:continue
    for j,length in adj[i]:
        if d+length<dist[j]:dist[j]=d+length;heapq.heappush(queue,(dist[j],j))
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
mask=pants.vertex_groups.new(name='Posed front thigh anatomical ease');rows=[]
for i,p in enumerate(points):
    w=sum(front[i])/len(front[i])*smooth((p.z-.625)/.060)*(1-smooth((p.z-.850)/.040))*smooth((dist[i]-.015)/.045)*smooth((abs(p.x+.75)-.025)/.030)
    if w>1e-7:mask.add([i],w,'REPLACE');rows.append({'id':i,'weight':w})
g=mid.vertex_groups.get(mask.name) or mid.vertex_groups.new(name=mask.name);assert g.index==mask.index,([g.name for g in pants.vertex_groups],[g.name for g in mid.vertex_groups])
helper=bpy.data.objects.new('Posed ease | live lower anatomical skin',bpy.data.meshes.new('Live lower anatomical skin'));scene.collection.objects.link(helper);helper.hide_render=True
join_group=bpy.data.node_groups.new('Posed ease | live leg and pelvis skin','GeometryNodeTree');join_group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');join_group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');nodes=join_group.nodes;links=join_group.links;join=nodes.new('GeometryNodeJoinGeometry');output=nodes.new('NodeGroupOutput');links.new(join.outputs['Geometry'],output.inputs['Geometry'])
for name in ('Character | anatomical legs','Character | continuous pelvis and upper thigh fitting'):
    info=nodes.new('GeometryNodeObjectInfo');info.transform_space='RELATIVE';info.inputs['Object'].default_value=bpy.data.objects[name];links.new(info.outputs['Geometry'],join.inputs['Geometry'])
mod=helper.modifiers.new('Live actual anatomical skin','NODES');mod.node_group=join_group
group=bpy.data.node_groups.new('Posed ease | front cotton skin allowance','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=group.nodes;l=group.links;inp=n.new('NodeGroupInput');op=n.new('NodeGroupOutput');position=n.new('GeometryNodeInputPosition');target=n.new('GeometryNodeObjectInfo');target.transform_space='RELATIVE';target.inputs['Object'].default_value=helper
start=n.new('ShaderNodeVectorMath');start.operation='ADD';l.new(position.outputs['Position'],start.inputs[0]);start.inputs[1].default_value=(0,1,0)
ray=n.new('GeometryNodeRaycast');ray.data_type='FLOAT';ray.mapping='INTERPOLATED';l.new(target.outputs['Geometry'],ray.inputs['Target Geometry']);l.new(start.outputs['Vector'],ray.inputs['Source Position']);ray.inputs['Ray Direction'].default_value=(0,-1,0);ray.inputs['Ray Length'].default_value=2.
hit=n.new('ShaderNodeSeparateXYZ');current=n.new('ShaderNodeSeparateXYZ');normal=n.new('ShaderNodeSeparateXYZ');l.new(ray.outputs['Hit Position'],hit.inputs['Vector']);l.new(position.outputs['Position'],current.inputs['Vector']);l.new(ray.outputs['Hit Normal'],normal.inputs['Vector'])
goal=n.new('ShaderNodeMath');goal.operation='ADD';l.new(hit.outputs['Y'],goal.inputs[0]);buffer=n.new('ShaderNodeMath');buffer.operation='DIVIDE';buffer.inputs[0].default_value=.012;l.new(normal.outputs['Y'],buffer.inputs[1]);l.new(buffer.outputs[0],goal.inputs[1]);delta=n.new('ShaderNodeMath');delta.operation='SUBTRACT';l.new(goal.outputs[0],delta.inputs[0]);l.new(current.outputs['Y'],delta.inputs[1]);upper=n.new('ShaderNodeMath');upper.operation='MINIMUM';upper.inputs[1].default_value=0.;l.new(delta.outputs[0],upper.inputs[0]);cap=n.new('ShaderNodeMath');cap.operation='MAXIMUM';cap.inputs[1].default_value=-.04;l.new(upper.outputs[0],cap.inputs[0])
field=n.new('GeometryNodeInputNamedAttribute');field.data_type='FLOAT';field.inputs['Name'].default_value=mask.name;direction=n.new('ShaderNodeMath');direction.operation='GREATER_THAN';direction.inputs[1].default_value=.2;l.new(normal.outputs['Y'],direction.inputs[0]);value=cap.outputs[0]
for factor in (field.outputs['Attribute'],ray.outputs['Is Hit'],direction.outputs[0]):
    multiply=n.new('ShaderNodeMath');multiply.operation='MULTIPLY';l.new(value,multiply.inputs[0]);l.new(factor,multiply.inputs[1]);value=multiply.outputs[0]
offset=n.new('ShaderNodeCombineXYZ');l.new(value,offset.inputs['Y']);setpos=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);l.new(offset.outputs['Vector'],setpos.inputs['Offset']);l.new(setpos.outputs['Geometry'],op.inputs['Geometry'])
for o in (pants,mid):
    m=o.modifiers.new('Posed final cotton anatomical ease','NODES');m.node_group=group;o.modifiers.move(len(o.modifiers)-1,next(i for i,m in enumerate(o.modifiers) if m.type=='SUBSURF'))
for o in (pants,mid):
    relax=o.modifiers.new('Rounded posed cotton fitting transition','SMOOTH');relax.factor=.35;relax.iterations=6;relax.vertex_group=mask.name;o.modifiers.move(len(o.modifiers)-1,next(i for i,m in enumerate(o.modifiers) if m.type=='SUBSURF'))
# Graded torso/garment waist contours in original rest geometry, before original fitting.
import math
body=bpy.data.objects['Character | internal torso support'];contact=bpy.data.objects['Torso fit | isolated anatomical arm contact'];coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface']
body.data=body.data.copy();contact.data=body.data;coat.data=coat.data.copy();cage.data=coat.data;torso_changes={}
for o,maximum in ((body,.010),(coat,.012)):
    basis=o.data.shape_keys.key_blocks['Basis'];positions=[]
    for i in range(len(o.data.vertices)):
        p=basis.data[i].co.copy()
        for old in o.data.shape_keys.key_blocks[1:]:p+=(old.data[i].co-old.relative_key.data[i].co)*old.value
        positions.append(o.matrix_world@p)
    key=o.shape_key_add(name='Natural ribcage to waist transition',from_mix=False);key.relative_key=basis;key.value=1.;changes=[]
    for i,p in enumerate(positions):
        u=abs(p.x+.75);w=math.exp(-((p.z-1.10)/.065)**2)*smooth((u-.045)/.080)*(1-smooth((u-.17)/.045))*smooth((p.z-.995)/.025)*(1-smooth((p.z-1.18)/.03))
        delta=Vector((-maximum*w*(-1 if p.x<-.75 else 1),0,0));key.data[i].co=basis.data[i].co+o.matrix_world.inverted().to_3x3()@delta
        if delta.length>1e-8:changes.append({'id':i,'delta_world_m':list(delta)})
    torso_changes[o.name]={'key':key.name,'maximum_m':max(Vector(r['delta_world_m']).length for r in changes),'controls':changes}
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'PosedEase.blend'),compress=True);r={'source_sha256':sha(source),'candidate_sha256':sha(out/'PosedEase.blend'),'torso_changes':torso_changes,'mask':mask.name,'mask_weights':rows,'boundary_ids':sorted(boundary),'body_targets':['Character | anatomical legs','Character | continuous pelvis and upper thigh fitting'],'allowance_m':.012,'allowance_method':'Y-ray allowance divided by hit normal Y, preserving nominal normal-space clearance','rounding':{'factor':.35,'iterations':6},'maximum_y_reduction_m':.04,'modifier':'Posed final cotton anatomical ease','scope':'New live final-stage cotton fitting after the retained complete source pose/fold pipeline, before subdivision. Preserves original geometry and walking construction. Contacts, sewn follower bounds and visual acceptance pending.'};(out/'build-report.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print('POSED_EASE_BUILT',r['candidate_sha256'],len(rows),flush=True)
