"""Soften rigid garment chest contours and fit excess front hip ease to native skin."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/SleeveContourCandidate/SleeveContour.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='127a003d16b624457dc8a8be809edbdda9666f314e892a5395102cef053c4517';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];rig=bpy.data.objects['Walk study | native anatomical controls']
coat.data=coat.data.copy();cage.data=coat.data;pants.data=pants.data.copy();mid.data=pants.data
chest=coat.data.shape_keys.key_blocks['Fitted cotton chest contours'];old_chest=chest.value;chest.value=.25
original=coat.modifiers['Front-quarter cotton tension folds'].node_group;group=original.copy();group.name='Jacket | softened front-quarter tension'
nodes=group.nodes;links=group.links;scale=next(n for n in nodes if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='SCALE');socket=scale.inputs['Scale'];source_socket=socket.links[0].from_socket
soft=nodes.new('ShaderNodeMath');soft.operation='MULTIPLY';soft.name='Reduced chest ridge prominence';soft.inputs[1].default_value=1.;links.new(source_socket,soft.inputs[0]);links.new(soft.outputs[0],socket)
chest_mask=nodes.new('GeometryNodeInputNamedAttribute');chest_mask.data_type='FLOAT';chest_mask.name='Local front chest relief mask';chest_mask.inputs['Name'].default_value='Front chest cotton bend radius'
amount=nodes.new('ShaderNodeMath');amount.operation='MULTIPLY';amount.name='Local chest relief reduction';amount.inputs[1].default_value=.65;links.new(chest_mask.outputs['Attribute'],amount.inputs[0])
factor=nodes.new('ShaderNodeMath');factor.operation='SUBTRACT';factor.name='Preserve relief outside front chest';factor.inputs[0].default_value=1.;links.new(amount.outputs[0],factor.inputs[1]);links.new(factor.outputs[0],soft.inputs[1])
for o in (coat,cage):o.modifiers['Front-quarter cotton tension folds'].node_group=group
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
def mixed(o):
    basis=o.data.shape_keys.key_blocks['Basis'];result=[]
    for i in range(len(o.data.vertices)):
        p=basis.data[i].co.copy()
        for k in o.data.shape_keys.key_blocks[1:]:
            if k.value:p+=(k.data[i].co-k.relative_key.data[i].co)*k.value
        result.append(o.matrix_world@p)
    return result
uv=coat.data.uv_layers['Cut raglan cloth panels'];panel=[[] for _ in coat.data.vertices]
for poly in coat.data.polygons:
    for li in poly.loop_indices:panel[coat.data.loops[li].vertex_index].append(float(uv.data[li].uv.x<.65 and uv.data[li].uv.y<.32))
rounding=coat.vertex_groups.new(name='Front chest cotton bend radius');pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index;chest_weights=[]
for i,p in enumerate(mixed(coat)):
    held=next((w.weight for w in coat.data.vertices[i].groups if w.group==pin),0.)
    weight=sum(panel[i])/len(panel[i])*smooth((p.z-1.205)/.065)*(1-smooth((p.z-1.39)/.045))*smooth((abs(p.x+.75)-.025)/.035)*(1-smooth((abs(p.x+.75)-.19)/.065))*(1-smooth((held-.3)/.5))
    if weight>1e-7:rounding.add([i],weight,'REPLACE');chest_weights.append({'id':i,'weight':weight})
for o in (coat,cage):
    if rounding.name not in o.vertex_groups:
        g=o.vertex_groups.new(name=rounding.name);assert g.index==rounding.index
    m=o.modifiers.new('Rounded pectoral cotton transitions','SMOOTH');m.factor=.65;m.iterations=18;m.vertex_group=rounding.name;o.modifiers.move(len(o.modifiers)-1,list(o.modifiers).index(o.modifiers['Free cloth outside anatomical support']))
# Inspect retained pelvis and lower-thigh skin in the actual armature rest state.
old_pose=rig.data.pose_position;rig.data.pose_position='REST';flags=[]
skin_names=['Character | internal torso support','Character | anatomical legs']
for name in skin_names:
    for m in bpy.data.objects[name].modifiers:
        if m.type=='SUBSURF':flags.append((m,m.levels));m.levels=m.render_levels
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();points=[];faces=[];skin_trees={}
for name in skin_names:
    o=bpy.data.objects[name];ev=o.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles();start=len(points);ps=[ev.matrix_world@v.co for v in mesh.vertices];fs=[tuple(t.vertices) for t in mesh.loop_triangles];skin_trees[name]=BVHTree.FromPolygons(ps,fs,all_triangles=True);points.extend(ps);faces.extend(tuple(start+i for i in t.vertices) for t in mesh.loop_triangles);ev.to_mesh_clear()
# Register the retained CC0 source-derived pelvis through the uncovered upper thigh.
original_bridge=bpy.data.objects['Character | posed pelvic fitting support'];bridge=original_bridge.copy();bridge.data=original_bridge.data.copy();bridge.name='Character | continuous pelvis and upper thigh fitting';bridge.data.name='Registered native pelvic anatomy';scene.collection.objects.link(bridge);bridge.hide_render=True
bridge_positions=mixed(bridge);neighbors=[set() for _ in bridge_positions]
for e in bridge.data.edges:
    a,b=e.vertices;neighbors[a].add(b);neighbors[b].add(a)
fixed={};anchors=[]
for i,p in enumerate(bridge_positions):
    target=skin_names[0] if p.z>=.875 else skin_names[1] if p.z<=.680 else None
    if target is None:continue
    hit,normal,index,distance=skin_trees[target].find_nearest(p);assert hit is not None
    fixed[i]=hit-p;anchors.append({'id':i,'target':target,'target_world_m':list(hit),'source_distance_m':distance})
assert {r['target'] for r in anchors}==set(skin_names)
displacements=[fixed.get(i,Vector()).copy() for i in range(len(bridge_positions))]
for iteration in range(600):
    updated=[fixed[i].copy() if i in fixed else sum((displacements[j] for j in neighbors[i]),Vector())/len(neighbors[i]) for i in range(len(bridge_positions))]
    residual=max((a-b).length for a,b in zip(updated,displacements));displacements=updated
    if residual<1e-7:break
bridge_basis=bridge.data.shape_keys.key_blocks['Basis'];registered=bridge.shape_key_add(name='Registered continuous pelvic skin',from_mix=False);registered.relative_key=bridge_basis;registered.value=1.;bridge_changes=[]
for i,v in enumerate(registered.data):
    local=bridge.matrix_world.inverted().to_3x3()@displacements[i];v.co=bridge_basis.data[i].co+local;bridge_changes.append({'id':i,'delta_local_m':list(local)})
bone_names=[g.name for g in bridge.vertex_groups if g.name in rig.data.bones]
for g in bridge.vertex_groups:
    if g.name in bone_names:g.remove(list(range(len(bridge_positions))))
for i,(p,delta) in enumerate(zip(bridge_positions,displacements)):
    q=p+delta;side='neg' if q.x<-.75 else 'pos';pelvic=smooth((q.z-.695)/.170)
    for name,w in [('pelvis',pelvic),(side+'.thigh',1-pelvic)]:
        if name not in bridge.vertex_groups:bridge.vertex_groups.new(name=name)
        if w:bridge.vertex_groups[name].add([i],w,'REPLACE')
bridge['source']='Character | posed pelvic fitting support / source-assets/makehuman-base.obj';bridge['license']='source-assets/MAKEHUMAN-LICENSE.ASSETS.md';bridge['registration']='Nearest retained torso/leg skin anchors in armature REST, harmonic displacement through the gap; authored continuous fitting anatomy'
skin_names.append(bridge.name);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=bridge.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles();start=len(points);points.extend(ev.matrix_world@v.co for v in mesh.vertices);faces.extend(tuple(start+i for i in t.vertices) for t in mesh.loop_triangles);ev.to_mesh_clear()
trees={s:BVHTree.FromPolygons(points,[f for f in faces if (sum(points[i].x for i in f)/3<-.75)==(s<0)],all_triangles=True) for s in (-1,1)}
uv=pants.data.uv_layers['Four cut cotton panels'];front=[[] for _ in pants.data.vertices];sides=[[] for _ in pants.data.vertices]
for poly in pants.data.polygons:
    for li in poly.loop_indices:
        i=pants.data.loops[li].vertex_index;front[i].append(float(uv.data[li].uv.y<.5));sides[i].append(-1 if uv.data[li].uv.x<.5 else 1)
positions=mixed(pants);basis=pants.data.shape_keys.key_blocks['Basis'];key=pants.shape_key_add(name='Front hip cotton anatomical ease',from_mix=False);key.value=1.;key.relative_key=basis
for i,v in enumerate(key.data):v.co=basis.data[i].co
changes=[];misses=[];observations=[]
protected_groups=[pants.vertex_groups[n].index for n in ('Lower shorts leg skin clearance','Medial thigh cotton skin fit','Cotton inner fold bend radius')]
# Protect nearby controls as well: subdivision spreads changes across adjacent faces.
import heapq
fit_neighbors=[[] for _ in positions]
for edge in pants.data.edges:
    a,b=edge.vertices;distance=(positions[a]-positions[b]).length
    fit_neighbors[a].append((b,distance));fit_neighbors[b].append((a,distance))
fit_distance=[float('inf') for _ in positions];queue=[]
for v in pants.data.vertices:
    if sum(w.weight for w in v.groups if w.group in protected_groups)>=.10:
        fit_distance[v.index]=0.;heapq.heappush(queue,(0.,v.index))
while queue:
    distance,i=heapq.heappop(queue)
    if distance!=fit_distance[i]:continue
    for j,length in fit_neighbors[i]:
        trial=distance+length
        if trial<fit_distance[j]:fit_distance[j]=trial;heapq.heappush(queue,(trial,j))
for i,p in enumerate(positions):
    mask=sum(front[i])/len(front[i])*smooth((p.z-.635)/.055)*(1-smooth((p.z-.855)/.045))*smooth((abs(p.x+.75)-.025)/.045)
    existing_fit=sum(w.weight for w in pants.data.vertices[i].groups if w.group in protected_groups);mask*=1-smooth(existing_fit/.15);mask*=smooth((fit_distance[i]-.015)/.045)
    if mask<1e-6:continue
    side=sum(sides[i])/len(sides[i])
    if abs(side)<.9:continue
    hit,normal,index,distance=trees[-1 if side<0 else 1].find_nearest(p)
    if hit is None or normal.y<-.2:misses.append(i);continue
    signed=(p-hit).dot(normal);observations.append({'id':i,'gap_m':signed,'mask':mask,'z':p.z})
    if signed<=.014:continue
    delta=hit+normal*.014-p
    if delta.length>.040:delta*=.040/delta.length
    delta*=mask;local=pants.matrix_world.inverted().to_3x3()@delta;changes.append({'id':i,'delta_local_m':list(local),'source_front_gap_m':signed,'mask':mask})
hip_neighbors=[set() for _ in positions]
for e in pants.data.edges:
    a,b=e.vertices;hip_neighbors[a].add(b);hip_neighbors[b].add(a)
raw_changes={r['id']:r for r in changes};deltas=[Vector(raw_changes[i]['delta_local_m']) if i in raw_changes else Vector() for i in range(len(positions))]
for _ in range(24):
    updated=[]
    for i,d in enumerate(deltas):
        if i not in raw_changes:updated.append(Vector());continue
        strength=.65*raw_changes[i]['mask'];average=sum((deltas[j] for j in hip_neighbors[i]),Vector())/len(hip_neighbors[i]);updated.append(d.lerp(average,strength))
    deltas=updated
for row in changes:row['raw_delta_local_m']=row['delta_local_m'];row['delta_local_m']=list(deltas[row['id']]);key.data[row['id']].co+=deltas[row['id']]
for m,level in flags:m.levels=level
rig.data.pose_position=old_pose;scene.frame_set(1);bpy.context.view_layer.update()
report={'source_sha256':expected,'chest_key_value':{'objects':[coat.name,cage.name],'key':chest.name,'old':old_chest,'new':chest.value},'tension_group':{'objects':[coat.name,cage.name],'modifier':'Front-quarter cotton tension folds','old':original.name,'new':group.name,'minimum_multiplier':.35,'mask':'Front chest cotton bend radius','outside_mask_multiplier':1.,'maximum_reduction':.65},'front_hip_key':{'objects':[pants.name,mid.name],'key':key.name,'controls':changes,'missed_skin_rays':misses,'observations':observations,'maximum_step_m':.024,'rest_front_allowance_m':.014,'method':'Only excess front-facing cotton volume moves inward along the scene front/back axis against the retained pelvis/thigh skin in armature rest state. Preserve waist, medial saddle, leg-opening and rear-panel regions through graded masks. Missing/back-facing hits remain unchanged. This is authored fitting, not physical cloth simulation.'}}
assert changes,'No front skin excess identified'
report['chest_rounding']={'objects':[coat.name,cage.name],'group':rounding.name,'weights':chest_weights,'modifier':'Rounded pectoral cotton transitions','factor':.65,'iterations':18,'placement':'Immediately before retained anatomical clearance, preserving original clearance/fold/subdivision order; front-panel, neck, zipper, shoulder and attachment fades'}
report['pelvic_continuity']={'object':bridge.name,'source_object':original_bridge.name,'key':registered.name,'controls':bridge_changes,'anchors':anchors,'harmonic_iterations':iteration+1,'residual_m':residual,'maximum_control_move_m':max(d.length for d in displacements),'weight_method':'Pelvis to corresponding native thigh, normalized smooth transition over 0.695-0.865 m in registered rest coordinates. Original fitting support is retained unchanged.','source_vertex_attribute':'MakeHuman source vertex','visible_skin_replaced':False}
report['front_hip_key'].update(maximum_step_m=.040,method='New editable front-panel rest fit to the actual retained skin plus registered source-derived upper-thigh continuity. Nearest surface is restricted to the matching native cut-panel side, with 14 mm stand-off and 40 mm capped control displacement. Graded waist, hem, medial saddle and rear protections remain. Not physical cloth simulation.')
report['rejected_posed_pelvis_fit']='The extra post-subdivision pelvis projection did not consistently improve comparative contact counts. It is not retained.'
report['rest_delta_rounding']={'passes':24,'maximum_blend':.65}
report['protected_existing_leg_fits']={'groups':['Lower shorts leg skin clearance','Medial thigh cotton skin fit','Cotton inner fold bend radius'],'method':'Retain the already fitted lower-leg/medial/fold region; fade new rest changes to zero by summed source influence 0.15. This prevents the new upper-thigh rest fit from fighting established posed leg clearance.'}
report['rejected_posed_continuous_hip_fit']='Post-subdivision projection to the continuous fitting surface introduced new cotton self-overlaps. It is rejected, not retained.'
report['protected_existing_leg_fits']['geodesic_fade_m']={'seed_influence':.10,'free_band':.015,'blend':.045}
report['chest_clearance_order']='Place new local chest rounding before retained anatomical clearance. Keep original clearance, authored relief and subdivision order on garment and sewing cage; all existing settings remain.'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'BodyBalance.blend'),compress=True);report['candidate_sha256']=sha(out/'BodyBalance.blend');(out/'build-report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('BODY_BALANCE_BUILT',len(changes),len(misses),report['candidate_sha256'],flush=True)
