"""Measure current anatomy and renderer capability for a native walking study."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonTensionCandidate/CottonTension.blend'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='F9A29E8B87D4F3E7B550C6E0217C2DFE9B80770CD803023E444E5AB74B91046D'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
def controls(obj):return [obj.matrix_world@v.co for v in obj.data.vertices]
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];ps=controls(pants)
waist=[p for p in ps if p.z>.86];pelvis=sum(waist,Vector())/len(waist)
legs=controls(bpy.data.objects['Character | anatomical legs'])
report={'pelvis':list(pelvis),'legs':{},'arms':{},'feet':{},'gpu':[]}
for label,sign in (('neg',-1),('pos',1)):
    side=[p for p in legs if sign*(p.x-pelvis.x)>0]
    knee=[p for p in side if .455<p.z<.515]
    ankle=[p for p in side if .12<p.z<.21]
    report['legs'][label]={'knee':list(sum(knee,Vector())/len(knee)),'ankle':list(sum(ankle,Vector())/len(ankle)),'knee_samples':len(knee),'ankle_samples':len(ankle)}
for side in ('left','right'):
    hand=bpy.data.objects['Character | anatomical '+side+' hand'];landmarks=json.loads(hand['hand_landmarks'])
    unposed=[v.vector.copy() for v in hand.data.attributes['Unposed anatomical position'].data];current=controls(hand)
    def estimate(p):
        ids=sorted(range(len(unposed)),key=lambda i:(unposed[i]-Vector(p)).length_squared)[:8]
        return sum((current[i] for i in ids),Vector())/len(ids)
    wrist=estimate(landmarks['wrist']);label='neg' if wrist.x<pelvis.x else 'pos'
    report['arms'][label]={'object':hand.name,'wrist':list(wrist),'digits':{n:[list(estimate(p)) for p in chain] for n,chain in landmarks['digits'].items()}}
for side in ('left','right'):
    obj=bpy.data.objects['Character | sneaker sole '+side];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    points=[obj.matrix_world@v.co for v in mesh.vertices];floor=min(p.z for p in points)
    contact=[p for p in points if p.z<floor+.0003];center=sum(points,Vector())/len(points)
    label='neg' if center.x<pelvis.x else 'pos'
    normal=sum((obj.matrix_world.to_3x3()@(face.normal*face.area) for face in mesh.polygons if face.normal.z<-.85),Vector()).normalized()
    report['feet'][label]={'object':obj.name,'floor':floor,'contact':list(sum(contact,Vector())/len(contact)),'bounds':[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)],'sole_angle':math.atan2(normal.y,-normal.z)}
    ev.to_mesh_clear()
curve=next(o for o in bpy.context.scene.objects if o.type=='CURVE' and o.name.startswith('Character | shoe lace'))
modifier=curve.modifiers.new('Probe native curve armature','ARMATURE');report['curve_armature_supported']=modifier.type=='ARMATURE';curve.modifiers.remove(modifier)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
report['gpu']=[{'name':d.name,'type':d.type} for d in prefs.devices]
(out/'landmarks.json').write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE_WALK_LANDMARKS',json.dumps(report),flush=True)
