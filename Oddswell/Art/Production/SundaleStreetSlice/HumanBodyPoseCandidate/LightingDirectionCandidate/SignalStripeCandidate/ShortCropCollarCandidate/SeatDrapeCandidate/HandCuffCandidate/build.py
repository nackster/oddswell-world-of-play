"""Build slimmer cuffs and anatomically guided thumbs from the retained scene."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
source=root.parent/'JacketEaseCandidate'/'OddsWell_Jacket_Ease_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='D9AF666965C9F7AAF78A27F9C119D285CD9747559F7635F58CF1DFC37B9D7E20'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def segment_distance(p,a,b):
    d=b-a
    q=a+d*max(0,min(1,(p-a).dot(d)/d.length_squared))
    return (p-q).length

original_skin_offsets={}
for side in ('left','right'):
    hand=bpy.data.objects['Character | anatomical '+side+' hand']
    surface=BVHTree.FromObject(hand,bpy.context.evaluated_depsgraph_get())
    for kind in ('nail fold','nail'):
        obj=bpy.data.objects[f'Character | {kind} {side} 1']
        transform=hand.matrix_world.inverted()@obj.matrix_world
        signed=[]
        for vertex in obj.data.vertices:
            point=transform@vertex.co
            hit,normal,_,_=surface.find_nearest(point)
            assert hit is not None
            signed.append((point-hit).dot(normal))
        original_skin_offsets[obj.name]=signed

for side in ('left','right'):
    cuff=bpy.data.objects['Character | sleeve cuff '+side]
    assert len(cuff.data.vertices)==13*384
    for k in range(13):
        ring=cuff.data.vertices[k*384:(k+1)*384]
        center=sum((vertex.co for vertex in ring),Vector())/len(ring)
        taper=1-.20*smooth((k-3)/9)
        for vertex in ring:
            vertex.co.x=center.x+(vertex.co.x-center.x)*taper
            vertex.co.y=center.y+(vertex.co.y-center.y)*taper
    cuff.data.update()

for side in ('left','right'):
    hand=bpy.data.objects['Character | anatomical '+side+' hand']
    landmarks=json.loads(hand['hand_landmarks'])
    original=[Vector(d.vector) for d in hand.data.attributes['Unposed anatomical position'].data]
    posed=[hand.matrix_world@v.co for v in hand.data.vertices]
    chains={digit:[Vector(p) for p in points] for digit,points in landmarks['digits'].items()}
    def estimate(p):
        nearest=sorted(range(len(original)),key=lambda i:(original[i]-p).length_squared)[:8]
        return sum((posed[i] for i in nearest),Vector())/len(nearest)
    root_point=estimate(chains['1'][0]);tip=estimate(chains['1'][3]);index=estimate(chains['2'][1])
    direction=tip-root_point
    wanted=direction+(index-tip)*.38
    rotation=direction.rotation_difference(wanted)
    axis=(chains['1'][3]-chains['1'][0]).normalized()
    weights=[]
    for p in original:
        thumb=min(segment_distance(p,a,b) for a,b in zip(chains['1'],chains['1'][1:]))
        others=min(segment_distance(p,a,b) for digit in ('2','3','4','5') for a,b in zip(chains[digit],chains[digit][1:]))
        progress=(p-chains['1'][0]).dot(axis)
        weight=smooth((progress+.004)/.022)*(1-smooth((thumb-.008)/.018))*smooth((others-thumb+.002)/.012)
        weights.append(weight)
    print('THUMB',side,'angle_deg',rotation.angle*180/3.14159265359,'weight_count',sum(w>.5 for w in weights),flush=True)
    pivot=hand.matrix_world.inverted()@root_point
    local_rotation=hand.matrix_world.to_quaternion().inverted()@rotation@hand.matrix_world.to_quaternion()
    for key in hand.data.shape_keys.key_blocks:
        for point,weight in zip(key.data,weights):
            p=point.co.copy()
            point.co=p.lerp(pivot+local_rotation@(p-pivot),weight)
    basis=hand.data.shape_keys.key_blocks['Basis']
    for vertex,point in zip(hand.data.vertices,basis.data):vertex.co=point.co
    hand.data.update()
    for obj in scene.objects:
        if obj.get('hand_side')!=side or obj.get('anatomical_digit')!=1 or obj.type!='MESH':continue
        for vertex in obj.data.vertices:
            world=obj.matrix_world@vertex.co
            vertex.co=obj.matrix_world.inverted()@(root_point+rotation@(world-root_point))
        obj.data.update()
    bpy.context.view_layer.update()
    surface=BVHTree.FromObject(hand,bpy.context.evaluated_depsgraph_get())
    for kind in ('nail fold','nail'):
        obj=bpy.data.objects[f'Character | {kind} {side} 1']
        to_hand=hand.matrix_world.inverted()@obj.matrix_world
        from_hand=obj.matrix_world.inverted()@hand.matrix_world
        for vertex,offset in zip(obj.data.vertices,original_skin_offsets[obj.name]):
            hit,normal,_,_=surface.find_nearest(to_hand@vertex.co)
            assert hit is not None
            vertex.co=from_hand@(hit+normal*offset)
        obj.data.update()
scene['thumb_adduction_candidate']=True
scene['cuff_taper_top_factor']=.8

out=root
for label,place,target in (
    ('Rear_Near',(-.49,-3.25,.83),(-.49,-2.50,.83)),
    ('Outer_Far',(-1.70,-2.25,.84),(-1.01,-2.25,.84)),
    ('Front_Near',(-.49,-1.65,.83),(-.49,-2.50,.83)),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97)),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0))):
    data=bpy.data.cameras.new('Thumb pose '+label)
    camera=bpy.data.objects.new('Thumb pose '+label,data);scene.collection.objects.link(camera)
    camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    close=label in ('Rear_Near','Outer_Far','Front_Near')
    data.lens=70 if close else 58 if label=='Full_Rear' else 40
    scene.camera=camera;scene.cycles.samples=64
    scene.render.resolution_x=900 if close else 1000
    scene.render.resolution_y=900 if close else 1100
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Hand_Cuff_'+label+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64;scene.render.resolution_x=1600;scene.render.resolution_y=900
scene.render.filepath=str(out/'Hand_Cuff_Gameplay.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Hand_Cuff_Candidate.blend'),compress=True)
print('ODDSWELL_HAND_CUFF_CANDIDATE_PASS',flush=True)
