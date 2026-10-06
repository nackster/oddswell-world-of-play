"""Native palm/finger articulation with coupled skin, nails and cuticle folds."""
import bpy,json,hashlib,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/ShoulderSurfaceCandidate/RoundedShoulder.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='7e04b1847acdbb58096ff57c654e388768e91726808f95caaf203e8ef18f82dd'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['Walk study | native anatomical controls']
land=json.loads((root/'Oddswell/Art/Production/SundaleStreetSlice/NativeWalkingStudy/landmarks.json').read_text())
hands={s:bpy.data.objects[land['arms'][s]['object']] for s in ['neg','pos']}
worlds={o.name:o.matrix_world.copy() for o in hands.values()}
normals={};posed_landmarks={}
for side,hand in hands.items():
    anatomical=json.loads(hand['hand_landmarks']);unposed=[v.vector.copy() for v in hand.data.attributes['Unposed anatomical position'].data]
    ps=[hand.matrix_world@v.co for v in hand.data.vertices]
    def estimate(p):
        ids=sorted(range(len(unposed)),key=lambda i:(unposed[i]-p).length_squared)[:64]
        a=np.array([list(unposed[i]-p)+[1.] for i in ids]);b=np.array([list(ps[i]) for i in ids])
        weights=np.array([1/max((unposed[i]-p).length,.003) for i in ids]);weights/=weights.max()
        fit=np.linalg.lstsq(a*weights[:,None],b*weights[:,None],rcond=None)[0]
        return Vector(fit[-1])
    base=Vector(anatomical['digits']['3'][1]);d=Vector(anatomical['dorsal'])
    normals[side]=(estimate(base+d*.008)-estimate(base-d*.008)).normalized()
    posed_landmarks[side]={'wrist':estimate(Vector(anatomical['wrist'])),'digits':{digit:[estimate(Vector(p)) for p in chain] for digit,chain in anatomical['digits'].items()}}
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT');newbones={}
for side,arm in posed_landmarks.items():
    names=[];palm=rig.data.edit_bones.new(side+'.palm');palm.head=Vector(arm['wrist']);palm.tail=Vector(arm['digits']['3'][0]);palm.parent=rig.data.edit_bones[side+'.forearm'];palm.align_roll(normals[side]);names.append(palm.name)
    for digit,chain in arm['digits'].items():
        parent=palm
        for joint in range(3):
            bone=rig.data.edit_bones.new(f'{side}.digit{digit}.{joint+1}');bone.head=Vector(chain[joint]);bone.tail=Vector(chain[joint+1]);bone.parent=parent;bone.align_roll(normals[side]);parent=bone;names.append(bone.name)
    newbones[side]=names
bpy.ops.object.mode_set(mode='OBJECT')
if '--inspect-rig' in sys.argv:
    diagnostic={'rig_matrix':[list(r) for r in rig.matrix_world],'hands':{side:{'world':[list(r) for r in hand.matrix_world],'bounds':[[min((hand.matrix_world@v.co)[i] for v in hand.data.vertices),max((hand.matrix_world@v.co)[i] for v in hand.data.vertices)] for i in range(3)],'bones':{name:{'head':list(rig.data.bones[name].head_local),'tail':list(rig.data.bones[name].tail_local)} for name in names}} for side,hand in hands.items() for names in [newbones[side]]}}
    (out/'rig-inspection.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    print('HAND_RIG_INSPECTED',flush=True);sys.exit(0)
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def canonical_digit_weights(p,chains,side):
    candidates=[]
    for digit,chain in chains.items():
        arc=0.;closest=None
        for a,b in zip(chain,chain[1:]):
            delta=b-a;length=delta.length;t=max(0.,min(1.,(p-a).dot(delta)/delta.length_squared))
            distance=(p-a-t*delta).length
            if closest is None or distance<closest[0]:closest=(distance,arc+t*length)
            arc+=length
        candidates.append((closest[0],digit,closest[1]))
    distance,digit,arc=min(candidates);chain=chains[digit]
    progress=(p-chain[0]).dot((chain[1]-chain[0]).normalized())
    influence=smooth((progress+.004)/.014)*(1-smooth((distance-.009)/.009))
    lengths=[(b-a).length for a,b in zip(chain,chain[1:])]
    first=1-smooth((arc-lengths[0]+.004)/.008)
    third=smooth((arc-lengths[0]-lengths[1]+.004)/.008)
    return {side+'.palm':1-influence,f'{side}.digit{digit}.1':influence*first,f'{side}.digit{digit}.2':influence*(1-first-third),f'{side}.digit{digit}.3':influence*third}

bind_report={}
for side,hand in hands.items():
    world=worlds[hand.name];hand.parent=None;hand.parent_type='OBJECT';hand.matrix_world=world
    for name in newbones[side]:
        if name not in hand.vertex_groups:hand.vertex_groups.new(name=name)
    canonical=json.loads(hand['hand_landmarks']);chains={d:[Vector(p) for p in chain] for d,chain in canonical['digits'].items()}
    records=[canonical_digit_weights(v.vector,chains,side) for v in hand.data.attributes['Unposed anatomical position'].data]
    for i,weights in enumerate(records):
        assert abs(sum(weights.values())-1)<1e-6 and min(weights.values())>=0,('Invalid anatomical hand weights',side,i,weights)
        for name,w in weights.items():
            if w>1e-7:hand.vertex_groups[name].add([i],w,'REPLACE')
    hand.parent=rig;hand.matrix_world=world
    mod=hand.modifiers.new('Anatomical finger deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    ids=list(range(len(hand.data.vertices)));names={g.index:g.name for g in hand.vertex_groups}
    sums=[sum(g.weight for g in v.groups if names[g.group] in newbones[side]+[side+'.forearm']) for v in hand.data.vertices]
    assert min(sums)>.99,('Unbound hand',side,min(sums))
    bind_report[hand.name]={'controls':len(ids),'minimum_weight_sum':min(sums),'native_bones':newbones[side],'binding':'Retained canonical anatomical digit chains and unposed-position attribute; smooth 8 mm interphalange transitions and palm blend.'}
bpy.context.view_layer.update()

def transfer_detail(obj,hand,side):
    world=obj.matrix_world.copy();obj.parent=None;obj.parent_type='OBJECT';obj.matrix_world=world
    for mod in list(obj.modifiers):
        if mod.type=='ARMATURE':obj.modifiers.remove(mod)
    transfer=obj.modifiers.new('Couple digit surface weights','DATA_TRANSFER');transfer.object=hand;transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'}
    transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME';obj.modifiers.move(len(obj.modifiers)-1,0)
    flags=[(m,m.show_viewport) for m in obj.modifiers if m!=transfer]
    for m,_ in flags:m.show_viewport=False
    bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();names={g.index:g.name for g in obj.vertex_groups}
    # Data Transfer adds named destination groups when the evaluated layer is created.
    names={g.index:g.name for g in obj.vertex_groups}
    allowed=set(newbones[side]+[side+'.forearm'])
    records=[{names[g.group]:g.weight for g in v.groups if g.group in names and names[g.group] in allowed} for v in mesh.vertices];ev.to_mesh_clear()
    ids=list(range(len(records)))
    for group in obj.vertex_groups:
        if group.name in rig.data.bones:group.remove(ids)
    for i,weights in enumerate(records):
        total=sum(weights.values());assert total>.99,('Unbound nail detail',obj.name,i,total)
        for name,w in weights.items():
            if w>1e-7:obj.vertex_groups[name].add([i],w/total,'REPLACE')
    obj.modifiers.remove(transfer)
    for m,flag in flags:m.show_viewport=flag
    obj.parent=rig;obj.matrix_world=world
    mod=obj.modifiers.new('Anatomical finger deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;obj.modifiers.move(len(obj.modifiers)-1,0)
    return len(records)

details={}
for side,hand in hands.items():
    label='left' if 'left hand' in hand.name else 'right'
    for obj in list(scene.objects):
        if obj.type=='MESH' and obj.get('hand_side')==label and 'anatomical_digit' in obj:
            # Ensure destination names exist before the native transfer evaluates.
            for name in newbones[side]+[side+'.forearm']:
                if name not in obj.vertex_groups:obj.vertex_groups.new(name=name)
            details[obj.name]=transfer_detail(obj,hand,side)
assert len(details)==20
for side,names in newbones.items():
    for name in names:rig.pose.bones[name].rotation_mode='XYZ'
    for frame in range(1,50):
        phi=(frame-1)/24+(0 if side=='pos' else .5);pulse=(1-math.cos(math.tau*phi))*.5
        palm=rig.pose.bones[side+'.palm'];palm.rotation_euler=(0,0,math.radians(1.2)*math.sin(math.tau*phi));palm.keyframe_insert(data_path='rotation_euler',frame=frame,group=side+' hand')
        for digit in range(1,6):
            for joint in range(1,4):
                bone=rig.pose.bones[f'{side}.digit{digit}.{joint}']
                # Source fingers are already curved: add a small asynchronous resting gesture.
                strength=(.45 if digit==1 else .7+.10*digit)*([1.,.65,.35][joint-1])
                angle=math.radians(2.+5.*pulse)*strength
                bone.rotation_euler=(-angle,0,math.radians(.7)*math.sin(math.tau*phi) if joint==1 else 0)
                bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=side+' hand')
scene.frame_set(1)
rig['finger_study_notes']='Native anatomical palm and 3 phalange controls per digit; canonical anatomical hand binding and nearest-polygon nail/fold weight transfer. Offline study, not runtime rig acceptance.'
(out/'build-report.json').write_text(json.dumps({'source_sha256':'7e04b1847acdbb58096ff57c654e388768e91726808f95caaf203e8ef18f82dd','added_bones':32,'hands':bind_report,'coupled_details':details,'dorsal_world':{s:list(n) for s,n in normals.items()},'posed_landmarks':{s:{'wrist':list(a['wrist']),'digits':{d:[list(p) for p in chain] for d,chain in a['digits'].items()}} for s,a in posed_landmarks.items()}},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'HandMotion.blend'),compress=True)
print('HAND_MOTION_SAVED',len(rig.data.bones),len(details),flush=True)
