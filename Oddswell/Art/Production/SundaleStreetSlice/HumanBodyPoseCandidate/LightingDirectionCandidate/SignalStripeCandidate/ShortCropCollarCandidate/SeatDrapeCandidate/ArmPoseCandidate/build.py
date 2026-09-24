"""Build elbow-centered walking arm motion from sleeve and wrist landmarks."""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Matrix,Vector

root=Path(__file__).resolve().parent
source=root.parent/'HandCuffCandidate'/'OddsWell_Hand_Cuff_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='F907E8E5F4807038DA9DADBBA38F7B67C12157D125E74F7844084C225EFF97D1'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

elbows={};wrists={}
coat_positions=[coat.matrix_world@v.co for v in coat.data.vertices]
for side in (-1,1):
    rows=[p for p in coat_positions if abs(p.z-1.16)<.01 and .24<side*(p.x+.75)<.48]
    assert len(rows)>20
    elbows[side]=sum(rows,Vector())/len(rows)
for label in ('left','right'):
    hand=bpy.data.objects['Character | anatomical '+label+' hand']
    landmarks=json.loads(hand['hand_landmarks'])
    source_points=[Vector(d.vector) for d in hand.data.attributes['Unposed anatomical position'].data]
    source_wrist=Vector(landmarks['wrist'])
    nearest=sorted(range(len(source_points)),key=lambda i:(source_points[i]-source_wrist).length_squared)[:8]
    wrist=sum((hand.matrix_world@hand.data.vertices[i].co for i in nearest),Vector())/len(nearest)
    wrists[-1 if wrist.x<-.75 else 1]=wrist
assert len(wrists)==2
angles={-1:.27,1:.12}
rotations={side:Matrix.Rotation(angle,3,'X') for side,angle in angles.items()}
for side in (-1,1):
    print('ARM_JOINT',side,'elbow',tuple(elbows[side]),'wrist',tuple(wrists[side]),'angle',angles[side],flush=True)

def deformed(p,rigid=False):
    side=-1 if p.x<-.75 else 1
    elbow=elbows[side];vector=wrists[side]-elbow
    t=(p-elbow).dot(vector)/vector.length_squared
    weight=1 if rigid else smooth((t+.10)/.50)*smooth((side*(p.x+.75)-.20)/.04)
    return p.lerp(elbow+rotations[side]@(p-elbow),weight)

def move_mesh(obj,rigid=False):
    mesh=obj.data;to_world=obj.matrix_world;to_local=obj.matrix_world.inverted()
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            for point in key.data:point.co=to_local@deformed(to_world@point.co,rigid)
        basis=mesh.shape_keys.key_blocks[0]
        for vertex,point in zip(mesh.vertices,basis.data):vertex.co=point.co
    else:
        for vertex in mesh.vertices:vertex.co=to_local@deformed(to_world@vertex.co,rigid)
    if obj==coat:
        for name in ('Tailored rest','Collision fit','Gravity result'):
            for datum in mesh.attributes[name].data:
                datum.vector=to_local@deformed(to_world@Vector(datum.vector),False)
    mesh.update()

move_mesh(coat)
move_mesh(bpy.data.objects['Character | internal torso support'])
for obj in scene.objects:
    if obj.type!='MESH' or not obj.name.startswith('Character | '):continue
    if any(token in obj.name for token in ('sleeve cuff ','anatomical left hand','anatomical right hand','nail left ','nail right ','nail fold left ','nail fold right ')):
        move_mesh(obj,True)
fit=coat.data.attributes['Collision fit'].data
gravity=coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m']=max((a.vector-b.vector).length for a,b in zip(gravity,fit))
scene['joint_arm_candidate']=True
scene['joint_arm_elbow_flex_radians']=json.dumps(angles)

original=Path('Oddswell/Art/Production/SundaleStreetSlice/settle_jacket.py').read_text(encoding='utf-8')
exec(compile(original[:original.rfind('\nsettle_jacket()')], 'settle_jacket.py', 'exec'))
fit_jacket_seams();fit_jacket_fastening()
for obj in scene.objects:
    if obj.name.startswith('Character | yoke topstitch '):obj.hide_render=True;obj.hide_set(True)

out=root
for label,place,target,lens in (
    ('Profile',(-2.55,-2.4,1.25),(-.75,-2.4,1.0),55),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40)):
    data=bpy.data.cameras.new('Joint arm '+label)
    camera=bpy.data.objects.new('Joint arm '+label,data);scene.collection.objects.link(camera)
    camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera;scene.cycles.samples=64
    scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Arm_Pose_'+label+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64;scene.render.resolution_x=1600;scene.render.resolution_y=900
scene.render.filepath=str(out/'Arm_Pose_Gameplay.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Arm_Pose_Candidate.blend'),compress=True)
print('ODDSWELL_ARM_POSE_CANDIDATE_PASS',flush=True)
