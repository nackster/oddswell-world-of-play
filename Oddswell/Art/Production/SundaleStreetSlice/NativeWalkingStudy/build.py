"""Editable offline walk study; retains the cotton source and its rest pose."""
import bpy, hashlib, json, math
from collections import Counter
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonTensionCandidate/CottonTension.blend'
with source.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest().upper()=='F9A29E8B87D4F3E7B550C6E0217C2DFE9B80770CD803023E444E5AB74B91046D'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
land=json.loads((out/'landmarks.json').read_text())
pelvis=Vector(land['pelvis']); chest=Vector((-.70,-2.36,1.31)); neck=Vector((-.687,-2.329,1.48))
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
def rotate(center,angle,axis):
    return Matrix.Translation(center)@Matrix.Rotation(angle,4,axis)@Matrix.Translation(-center)
def points(obj):
    return [obj.matrix_world@v.co for v in obj.data.vertices]
coat=points(bpy.data.objects['Character | tailored slate jacket'])
data=bpy.data.armatures.new('OddsWell offline anatomical walk')
rig=bpy.data.objects.new('Walk study | native anatomical controls',data)
scene.collection.objects.link(rig);rig.show_in_front=True
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=data.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=data.edit_bones[parent]
    return b
bone('root',pelvis-Vector((0,0,.15)),pelvis,None).use_deform=False
bone('pelvis',pelvis,pelvis+Vector((0,0,.15)),'root')
bone('chest',pelvis+Vector((0,0,.15)),neck,'pelvis')
bone('head',neck,neck+Vector((0,0,.23)),'chest')
joints={}
for side,sign in [('neg',-1),('pos',1)]:
    knee=Vector(land['legs'][side]['knee']);ankle=Vector(land['legs'][side]['ankle'])
    hip=pelvis+Vector((sign*.095,0,-.015))
    rows=[p for p in coat if abs(p.z-1.16)<.055 and .21<sign*(p.x-pelvis.x)<.55]
    assert rows, ('missing sleeve landmark',side)
    elbow=sum(rows,Vector())/len(rows)
    wrist=Vector(land['arms'][side]['wrist'])
    shoulder=Vector((chest.x+sign*.20,chest.y,1.425))
    bone(side+'.thigh',hip,knee,'pelvis');bone(side+'.shin',knee,ankle,side+'.thigh')
    bone(side+'.foot',ankle,ankle+Vector((0,.14,-.05)),side+'.shin')
    bone(side+'.upperarm',shoulder,elbow,'chest');bone(side+'.forearm',elbow,wrist,side+'.upperarm')
    joints[side]=dict(hip=hip,knee=knee,ankle=ankle,shoulder=shoulder,elbow=elbow,wrist=wrist)
bpy.ops.object.mode_set(mode='OBJECT')
rest={b.name:b.matrix_local.copy() for b in data.bones}
for b in rig.pose.bones:b.rotation_mode='QUATERNION'

def distance(p,a,b):
    d=b-a;t=max(0.,min(1.,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length,t
def weights(p,upper):
    side='neg' if p.x<pelvis.x else 'pos';j=joints[side]
    thigh=smooth((p.z-.40)/.17)
    hip=smooth((p.z-.69)/.18)
    torso=smooth((p.z-.95)/.27)
    core_distance,_=distance(p,pelvis,Vector((-.687,-2.329,1.48)))
    upper_distance,_=distance(p,j['shoulder'],j['elbow'])
    fore_distance,_=distance(p,j['elbow'],j['wrist'])
    arm=(smooth((core_distance-min(upper_distance,fore_distance)-.08)/.10)
         *smooth((p.z-.70)/.10)*(1-smooth((p.z-1.47)/.06))) if upper else 0.
    elbow=smooth((1.23-p.z)/.15)
    return {side+'.shin':(1-thigh)*(1-hip)*(1-arm),side+'.thigh':thigh*(1-hip)*(1-arm),
            'pelvis':hip*(1-torso)*(1-arm),'chest':hip*torso*(1-arm),
            side+'.upperarm':arm*(1-elbow),side+'.forearm':arm*elbow}

def rigid(obj,name):
    world=obj.matrix_world.copy();obj.parent=rig;obj.parent_type='BONE';obj.parent_bone=name
    bpy.context.view_layer.update();obj.matrix_world=world
def attachment_weights(obj,ps):
    if obj.name!='Character | tailored slate jacket':return {}
    edges=Counter(tuple(sorted((a,b))) for face in obj.data.polygons for a,b in zip(face.vertices,(*face.vertices[1:],face.vertices[0])))
    graph={}
    for (a,b),count in edges.items():
        if count==1:graph.setdefault(a,[]).append(b);graph.setdefault(b,[]).append(a)
    pending=set(graph);loops=[]
    while pending:
        start=min(pending);loop=[];prev=None;cur=start
        while cur not in loop:
            loop.append(cur);pending.discard(cur);nxt=next(n for n in graph[cur] if n!=prev);prev,cur=cur,nxt
        loops.append(loop)
    assert len(loops)==4
    centers=[sum((ps[i] for i in loop),Vector())/len(loop) for loop in loops]
    neck=max(range(4),key=lambda i:centers[i].z)
    hem=min((i for i in range(4) if i!=neck),key=lambda i:abs(centers[i].x-pelvis.x))
    labels={neck:'chest',hem:'pelvis'}
    for i in range(4):
        if i not in labels:labels[i]=('neg' if centers[i].x<pelvis.x else 'pos')+'.forearm'
    ids=[(index,labels[i]) for i,loop in enumerate(loops) for index in loop]
    tree=KDTree(len(ids))
    for j,(index,_) in enumerate(ids):tree.insert(ps[index],j)
    tree.balance();pin=obj.vertex_groups['Collar zipper hem and cuff attachments'].index;result={}
    for vertex,p in zip(obj.data.vertices,ps):
        held=max((g.weight for g in vertex.groups if g.group==pin),default=0)
        if held<=0:continue
        _,idx,d=tree.find(p)
        if d>.09:continue
        result[vertex.index]=(ids[idx][1],held*smooth((.09-d)/.065))
    return result

def bind(obj,head=False):
    names=['pelvis','chest','head']+[s+'.'+b for s in ['neg','pos'] for b in ['thigh','shin','upperarm','forearm']]
    groups={n:obj.vertex_groups.new(name='Walk '+n) for n in names}
    # Actual bone names are used by the modifier; the original groups stay intact.
    for n,g in groups.items():g.name=n
    world_points=points(obj)
    anchors=attachment_weights(obj,world_points)
    upper=max(p.z for p in world_points)>1.10 or 'zipper' in obj.name.lower()
    for v,p in zip(obj.data.vertices,world_points):
        if head:
            h=smooth((p.z-1.445)/.065);ws={'chest':1-h,'head':h}
        else:
            ws=weights(p,upper)
            if v.index in anchors:
                name,blend=anchors[v.index];ws={n:w*(1-blend) for n,w in ws.items()};ws[name]=ws.get(name,0)+blend
        for n,w in ws.items():
            if w>1e-7:groups[n].add([v.index],w,'REPLACE')
    mod=obj.modifiers.new('Native walk deformation','ARMATURE');mod.object=rig
    mod.use_deform_preserve_volume=True
    obj.modifiers.move(len(obj.modifiers)-1,0)

chars=[o for o in scene.objects if o.name.startswith('Character | ') and o.type in {'MESH','CURVE'}]
derived=[];bound=[];rigid_parts=[]
for obj in chars:
    name=obj.name.lower()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    # Bounds identify small hand/head/foot detail regardless of old left/right labels.
    corners=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    center=sum(corners,Vector())/8
    side='neg' if center.x<pelvis.x else 'pos'
    if any(t in name for t in ('sneaker','shoe lace','shoe eyelet','shoe tongue','shoe collar','shoe fox','shoe quarter','shoe toe','shoe outsole')):
        rigid(obj,side+'.foot');rigid_parts.append(obj.name);continue
    if name=='character | anatomical head':
        bind(obj,True);bound.append(obj.name);continue
    if center.z>1.49:
        rigid(obj,'head');rigid_parts.append(obj.name);continue
    wrist=joints[side]['wrist']
    if (center-wrist).length<.24 and center.z<1.03 and abs(center.x-pelvis.x)>.23:
        rigid(obj,side+'.forearm');rigid_parts.append(obj.name);continue
    if obj.type=='CURVE':
        mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
        follower=bpy.data.objects.new('Walk surface | '+obj.name,mesh)
        scene.collection.objects.link(follower);follower.matrix_world=obj.matrix_world.copy()
        follower.hide_render=obj.hide_render
        follower.hide_viewport=obj.hide_viewport
        follower['editable_curve_source']=obj.name
        obj.hide_render=True;obj.hide_set(True)
        bind(follower);derived.append(follower.name)
    else:
        bind(obj);bound.append(obj.name)
    if len(bound)%30==0:print('WALK_BIND',len(bound),len(derived),flush=True)

# Evaluated sole samples allow floor correction after pitch, rather than guessing heel height.
soles={}
for side in joints:
    ob=bpy.data.objects[land['feet'][side]['object']];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    soles[side]=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear()

def segment(name,a,b):
    old=data.bones[name];q=(old.tail_local-old.head_local).rotation_difference(b-a)
    result=q.to_matrix().to_4x4()@rest[name];result.translation=a
    return result
def solve(j,hip,ankle):
    femur=(j['knee']-j['hip']).length;shin=(j['ankle']-j['knee']).length
    d=(ankle-hip).length
    assert abs(femur-shin)<d<femur+shin, ('unreachable leg',d,femur+shin)
    u=(ankle-hip)/d;x=(femur*femur-shin*shin+d*d)/(2*d)
    old=(j['ankle']-j['hip']).normalized();bend=j['knee']-j['hip'];bend-=old*bend.dot(old)
    bend-=u*bend.dot(u);bend.normalize()
    return hip+x*u+math.sqrt(max(0.,femur*femur-x*x))*bend
stride=2*abs(joints['pos']['ankle'].y-joints['neg']['ankle'].y)
measure=[]
for frame in range(1,50):
    phi=(frame-1)/24.;wave=1-math.cos(2*math.pi*phi)
    travel=Matrix.Translation((.012*math.sin(2*math.pi*phi)-.009*wave,stride*phi,-.012*math.sin(2*math.pi*phi)**2))
    upper=Matrix.Translation((-.054*wave,0,0))
    pm=travel@rotate(pelvis,math.radians(4.5)*wave,'Z')@rotate(pelvis,math.radians(-2.5)*wave,'Y')
    cm=upper@travel@rotate(chest,math.radians(-3.5)*wave,'Z')
    desired={'root':travel@rest['root'],'pelvis':pm@rest['pelvis'],'chest':cm@rest['chest'],'head':upper@travel@rest['head']}
    fm={}
    for side,sign in [('neg',-1),('pos',1)]:
        j=joints[side];phase=phi+(.5 if side=='neg' else 0);cycle=math.floor(phase+1e-9);p=phase-cycle
        swing=smooth((p-.5)/.5)
        pitch=-.25944769118993416*smooth((p-.35)/.15) if p<=.5 else -.25944769118993416*(1-swing)+.10*math.sin(2*math.pi*(p-.5))
        initial=land['feet'][side]['sole_angle'];sole=soles[side]
        pivot=Vector((land['feet'][side]['contact'][0],max(v.y for v in sole)-.008,land['feet'][side]['floor']))
        transform=Matrix.Translation((0,stride*(cycle+swing),0))@rotate(pivot,pitch-initial,'X')
        lift=.060*math.sin(math.pi*(p-.5)/.5) if p>.5 else 0
        floor=land['feet'][side]['floor']
        transform=Matrix.Translation((0,0,floor+lift-min((transform@v).z for v in sole)))@transform
        fm[side]=transform
    drop=0.
    for side,j in joints.items():
        hip=pm@j['hip'];ankle=fm[side]@j['ankle']
        reach=(j['knee']-j['hip']).length+(j['ankle']-j['knee']).length-.001
        horizontal=(hip.x-ankle.x)**2+(hip.y-ankle.y)**2
        assert horizontal<reach*reach,('stride too long',frame,side)
        allowed_z=ankle.z+math.sqrt(reach*reach-horizontal)
        drop=max(drop,hip.z-allowed_z)
    assert drop<.08,('excessive pelvis lowering',frame,drop)
    lower=Matrix.Translation((0,0,-drop));pm=lower@pm;cm=lower@cm;travel=lower@travel
    desired={'root':travel@rest['root'],'pelvis':pm@rest['pelvis'],'chest':cm@rest['chest'],'head':upper@travel@rest['head']}
    for side,sign in [('neg',-1),('pos',1)]:
        j=joints[side];transform=fm[side]
        hip=pm@j['hip'];ankle=transform@j['ankle'];knee=solve(j,hip,ankle)
        desired[side+'.thigh']=segment(side+'.thigh',hip,knee)
        desired[side+'.shin']=segment(side+'.shin',knee,ankle)
        desired[side+'.foot']=transform@rest[side+'.foot']
        arm=cm@rotate(j['shoulder'],sign*math.radians(13)*wave,'X')
        shoulder=cm@j['shoulder']
        wrist=(arm@rotate(j['elbow'],-math.radians(7)*math.sin(math.pi*phi)**2,'X'))@j['wrist']
        # Keep hands outside the pelvis as the ribcage transfers across it.
        wrist.x-=upper.translation.x
        arm_rest={'hip':j['shoulder'],'knee':j['elbow'],'ankle':j['wrist']}
        reach=(j['elbow']-j['shoulder']).length+(j['wrist']-j['elbow']).length-.001
        direction=wrist-shoulder
        if direction.length>reach:wrist=shoulder+direction.normalized()*reach
        elbow=solve(arm_rest,shoulder,wrist)
        desired[side+'.upperarm']=segment(side+'.upperarm',shoulder,elbow)
        desired[side+'.forearm']=segment(side+'.forearm',elbow,wrist)
    for b in rig.pose.bones:
        args={'matrix':desired[b.name],'matrix_local':rest[b.name],'invert':True}
        if b.parent:args.update(parent_matrix=desired[b.parent.name],parent_matrix_local=rest[b.parent.name])
        b.matrix_basis=b.bone.convert_local_to_pose(**args)
        for prop in ['location','rotation_quaternion','scale']:b.keyframe_insert(prop,frame=frame,group=b.name)
    measure.append({'frame':frame,'root_y_m':stride*phi,'upper_body_lateral_transfer_m':-.054*wave,'reach_correction_drop_m':drop,'pelvis_yaw_delta_deg':4.5*wave,'chest_yaw_delta_deg':-3.5*wave,'feet':{s:{'floor_m':min((fm[s]@v).z for v in soles[s]),'lift_m':min((fm[s]@v).z for v in soles[s])-land['feet'][s]['floor']} for s in soles}})
    print('WALK_KEYFRAME',frame,flush=True)
scene.frame_start=1;scene.frame_end=49;scene.render.fps=24;scene.frame_set(1)
rig['study_only']=True;rig['source_sha256']='F9A29E8B87D4F3E7B550C6E0217C2DFE9B80770CD803023E444E5AB74B91046D'
rig['root_stride_m']=stride;rig['notes']='Offline anatomical study; native FK controls, analytic leg solve, rigid sole floor correction. Not runtime animation acceptance.'
(out/'build-report.json').write_text(json.dumps({'source':rig['source_sha256'],'stride_m':stride,'bound':bound,'curve_derivatives':derived,'rigid':rigid_parts,'frames':measure},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'NativeWalk.blend'),compress=True)
print('NATIVE_WALK_SAVED',len(bound),len(derived),len(rigid_parts),flush=True)
