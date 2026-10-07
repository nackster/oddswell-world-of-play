"""Anatomical sleeve ease, preserving source geometry and walking controls."""
import bpy,json,hashlib,math,heapq
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonEaseCandidate/CottonEase.blend';expected='a46587e5990c80822b118c019168576708366377b37663422bde60d420d322fb'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];body=bpy.data.objects['Character | internal torso support'];coat.data=coat.data.copy();cage.data=coat.data
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
rig=bpy.data.objects['Walk study | native anatomical controls'];body.data=body.data.copy();body_before_keys=[k.name for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [];body_positions=[]
for v in body.data.vertices:
    p=v.co.copy()
    if body.data.shape_keys:
        for k in body.data.shape_keys.key_blocks[1:]:
            if k.value:p+=(k.data[v.index].co-body.data.shape_keys.key_blocks['Basis'].data[v.index].co)*k.value
    body_positions.append(body.matrix_world@p)
if not body.data.shape_keys:body.shape_key_add(name='Basis',from_mix=False)
body_key=body.shape_key_add(name='Defined adult arm muscle taper',from_mix=False);body_key.value=1;deltas=[Vector() for v in body.data.vertices];profile={}
for side in ('neg','pos'):
    for part in ('upperarm','forearm'):
        name=side+'.'+part;bone=rig.data.bones[name];a=rig.matrix_world@bone.head_local;axis=rig.matrix_world@bone.tail_local-a;unit=axis.normalized();group=body.vertex_groups[name].index;weights=[max((w.weight for w in v.groups if w.group==group),default=0) for v in body.data.vertices];t=[(p-a).dot(axis)/axis.length_squared for p in body_positions];ids=[i for i,w in enumerate(weights) if w>.75 and -.05<t[i]<1.05];centers=[]
        for j in range(13):
            at=j/12;ws=[weights[i]**3*math.exp(-((t[i]-at)/.11)**2) for i in ids];center=sum(((body_positions[i]-a-axis*t[i])*w for i,w in zip(ids,ws)),Vector())/sum(ws);centers.append(center)
        changed=0;maximum=0.
        for i,(p,w,at) in enumerate(zip(body_positions,weights,t)):
            if w<.05 or not 0<at<1:continue
            q=at*12;j=min(11,int(q));center=a+axis*at+centers[j].lerp(centers[j+1],q-j);radial=p-center;radial-=unit*radial.dot(unit);radius=radial.length
            target=(.064-.017*at+.003*math.sin(math.pi*at)) if part=='upperarm' else (.049-.022*at+.003*math.sin(math.pi*at));mask=smooth((at-(.25 if part=='upperarm' else .05))/.18)*(1-smooth((at-.78)/.18))*w
            if radius<=target or mask<1e-6:continue
            delta=-radial.normalized()*min(.012,radius-target)*mask;deltas[i]+=delta;changed+=1;maximum=max(maximum,delta.length)
        profile[name]={'selected_controls':changed,'maximum_contribution_m':maximum,'centers_perpendicular_world_m':[list(c) for c in centers]}
body_changes=[]
for i,delta in enumerate(deltas):
    if delta.length<1e-8:continue
    if delta.length>.012:delta*=.012/delta.length
    body_key.data[i].co+=body.matrix_world.inverted().to_3x3()@delta;body_changes.append({'id':i,'move_m':delta.length})
flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='ARMATURE']
for m,v in flags:m.show_viewport=False
bpy.context.view_layer.update();tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());uv=coat.data.uv_layers['Cut raglan cloth panels'];sleeve={v.index:[] for v in coat.data.vertices}
for poly in coat.data.polygons:
    for i in poly.loop_indices:sleeve[coat.data.loops[i].vertex_index].append(float(uv.data[i].uv.x>.65))
key=coat.shape_key_add(name='Defined anatomical sleeve ease',from_mix=False);key.value=1;pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index;changes=[]
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for v in coat.data.vertices:
    local=v.co.copy()
    for old in coat.data.shape_keys.key_blocks[1:]:
        if old!=key and old.value:local+=(old.data[v.index].co-coat.data.shape_keys.key_blocks['Basis'].data[v.index].co)*old.value
    p=coat.matrix_world@local;held=max((w.weight for w in v.groups if w.group==pin),default=0);mask=sum(sleeve[v.index])/len(sleeve[v.index])*smooth((p.z-.965)/.070)*(1-smooth((p.z-1.34)/.09))
    if mask<1e-6:continue
    hit,normal,index,distance=tree.find_nearest(body.matrix_world.inverted()@p)
    if distance<=.012:continue
    delta=-(p-body.matrix_world@hit).normalized()*min(.040,distance-.012)*mask;key.data[v.index].co+=coat.matrix_world.inverted().to_3x3()@delta;changes.append({'id':v.index,'move_m':delta.length,'mask':mask,'source_rest_support_distance_m':distance,'pin_weight':held})
for m,v in flags:m.show_viewport=v
contact=body.copy();contact.data=body.data;contact.name='Torso fit | isolated anatomical arm contact';scene.collection.objects.link(contact);contact.hide_render=True;contact.hide_set(True)
for mod in list(contact.modifiers):
    if mod.type=='COLLISION':contact.modifiers.remove(mod)
isolate=bpy.data.node_groups.new('Anatomy | arm-only fitting surface','GeometryNodeTree');isolate.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');isolate.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');ns=isolate.nodes;ls=isolate.links;inp=ns.new('NodeGroupInput');output=ns.new('NodeGroupOutput');terms=[]
for name in ('neg.upperarm','neg.forearm','pos.upperarm','pos.forearm'):
    f=ns.new('GeometryNodeInputNamedAttribute');f.data_type='FLOAT';f.inputs['Name'].default_value=name;terms.append(f.outputs['Attribute'])
total=terms[0]
for term in terms[1:]:
    add=ns.new('ShaderNodeMath');add.operation='ADD';ls.new(total,add.inputs[0]);ls.new(term,add.inputs[1]);total=add.outputs[0]
below=ns.new('ShaderNodeMath');below.operation='LESS_THAN';below.inputs[1].default_value=.65;ls.new(total,below.inputs[0]);delete=ns.new('GeometryNodeDeleteGeometry');delete.domain='FACE';ls.new(inp.outputs[0],delete.inputs['Geometry']);ls.new(below.outputs[0],delete.inputs['Selection']);ls.new(delete.outputs[0],output.inputs[0]);mod=contact.modifiers.new('Retain actual arm fitting faces','NODES');mod.node_group=isolate
fit=coat.vertex_groups.new(name='Posed sleeve anatomical ease')
distances=[float('inf') for v in coat.data.vertices];neighbors=[[] for v in coat.data.vertices];seeds=[i for i,values in sleeve.items() if 0<sum(values)/len(values)<1]
assert seeds,'No connected raglan join found'
for edge in coat.data.edges:
    a,b=edge.vertices;cost=(coat.data.vertices[a].co-coat.data.vertices[b].co).length;neighbors[a].append((b,cost));neighbors[b].append((a,cost))
queue=[]
for i in seeds:distances[i]=0.;heapq.heappush(queue,(0.,i))
while queue:
    distance,i=heapq.heappop(queue)
    if distance!=distances[i]:continue
    for j,cost in neighbors[i]:
        new=distance+cost
        if new<distances[j]:distances[j]=new;heapq.heappush(queue,(new,j))
for v in coat.data.vertices:
    p=coat.matrix_world@v.co;weight=.85*sum(sleeve[v.index])/len(sleeve[v.index])*smooth((p.z-.965)/.070)*(1-smooth((p.z-1.34)/.09))*smooth((distances[v.index]-.025)/.055)
    if weight:fit.add([v.index],weight,'REPLACE')
if fit.name not in cage.vertex_groups:
    group=cage.vertex_groups.new(name=fit.name);assert group.index==fit.index
for obj in (coat,cage):
    mod=obj.modifiers.new('Sleeve cotton follows posed arm contours','SHRINKWRAP');mod.target=contact;mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='ON_SURFACE';mod.offset=.012;mod.vertex_group=fit.name;obj.modifiers.move(len(obj.modifiers)-1,next(i for i,m in enumerate(obj.modifiers) if m.name=='Free cloth outside anatomical support'))
fold=coat.data.attributes.new(name='Elbow cotton compression relief',type='FLOAT',domain='POINT')
for v,value in zip(coat.data.vertices,fold.data):
    local=v.co.copy()
    for k in coat.data.shape_keys.key_blocks[1:]:
        if k.value:local+=(k.data[v.index].co-coat.data.shape_keys.key_blocks['Basis'].data[v.index].co)*k.value
    p=coat.matrix_world@local;side='neg' if p.x<-.75 else 'pos';fore=rig.data.bones[side+'.forearm'];upper=rig.data.bones[side+'.upperarm'];a=rig.matrix_world@fore.head_local;axis=rig.matrix_world@fore.tail_local-a;t=(p-a).dot(axis)/axis.length_squared;radial=p-a-axis*t;inside=((rig.matrix_world@upper.head_local-a).normalized()+axis.normalized()).normalized();angular=smooth((radial.normalized().dot(inside)-.1)/.8)
    relief=sum(amp*math.exp(-((t-center)/width)**2) for center,width,amp in ((.075,.035,.0030),(.16,.045,.0022),(.255,.045,.0015)))
    value.value=relief*angular*sum(sleeve[v.index])/len(sleeve[v.index])*smooth((p.z-.97)/.055)
ng=bpy.data.node_groups.new('Cotton | rounded elbow compression','GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=ng.nodes;l=ng.links;inp=n.new('NodeGroupInput');output=n.new('NodeGroupOutput');normal=n.new('GeometryNodeInputNormal');field=n.new('GeometryNodeInputNamedAttribute');field.data_type='FLOAT';field.inputs['Name'].default_value=fold.name;scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';l.new(normal.outputs[0],scale.inputs[0]);l.new(field.outputs['Attribute'],scale.inputs['Scale']);position=n.new('GeometryNodeSetPosition');l.new(inp.outputs[0],position.inputs['Geometry']);l.new(scale.outputs[0],position.inputs['Offset']);l.new(position.outputs[0],output.inputs[0])
for obj in (coat,cage):
    mod=obj.modifiers.new('Rounded elbow cotton compression','NODES');mod.node_group=ng;obj.modifiers.move(len(obj.modifiers)-1,next(i for i,m in enumerate(obj.modifiers) if m.type=='SUBSURF'))
bpy.context.view_layer.update();scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'TorsoSilhouette.blend'),compress=True)
with (out/'TorsoSilhouette.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'source_sha256':expected,'candidate_sha256':sha,'added_key':key.name,'changed_controls':len(changes),'maximum_control_move_m':max(r['move_m'] for r in changes),'proposed_rest_support_standoff_m':.012,'controls':changes,'scope':'Graded sleeve cut-panel selection from lower forearm to upper arm. Reduce excessive resting support gap by up to 40 mm, protect actual shoulder/cuff spatial regions. Internal sewn panel edges may move with their cloth rather than inheriting all physical-attachment pin protection. One shared editable key on jacket and evaluated sewing cage; original controls/UVs/keys/weights/rig/animation/maps/materials retained. Proposed rest stand-off is not animated collision proof.'}
report['posed_fit']={'vertex_group':fit.name,'maximum_influence':.85,'modifier':'Sleeve cotton follows posed arm contours','target':contact.name,'offset_m':.012,'placement':'After armature and existing cloth rounding, before existing outside-body constraint. Graded forearm/elbow/upper-arm mask with shoulder and cuff spatial protection. A hidden source-sharing contact object retains faces with combined arm-bone influence at least 0.65, preventing attraction to the torso. This is authored anatomical fitting, not physical cloth simulation.'}
report['posed_fit']['raglan_join_ease']={'seed_controls':len(seeds),'protected_distance_m':.025,'graded_transition_m':.055,'method':'Shortest rest mesh-edge distance from the connected sleeve/torso join. Keep join volume free and blend anatomical fitting over the next 55 mm; cuff and shoulder spatial protections remain.'}
report['body_taper']={'added_keys':[k.name for k in body.data.shape_keys.key_blocks if k.name not in body_before_keys],'changed_controls':len(body_changes),'maximum_control_move_m':max(r['move_m'] for r in body_changes),'controls':body_changes,'profiles':profile,'method':'Native arm-weight selection; smooth perpendicular centerline from thirteen weighted cross sections along each existing bone direction. Graded inward radial excess reduction, capped at 12 mm, toward an authored adult upper-arm/forearm taper. Shoulder and wrist ends fade to zero. Original support controls/UVs/keys/weights and bones retained; no claim of measured human scan anatomy.'}
report['elbow_folds']={'attribute':fold.name,'maximum_control_relief_m':max(a.value for a in fold.data),'nonzero_controls':sum(a.value>1e-8 for a in fold.data),'method':'Three shallow outward rounded gathers on the concave elbow/upper-forearm side, before subdivision after posed anatomical fitting. Authored native cloth geometry follows the existing walk; not a physical cloth simulation.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('TORSO_SILHOUETTE_BUILT',len(changes),report['maximum_control_move_m'],sha,flush=True)
