"""Orient the walking hand for a relaxed readable front/rear pose."""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Quaternion,Vector

output=Path(__file__).resolve().parent
source=output.parent/'ShortsPanelCandidate/ShortsPanel.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='7DED1799872E9E8AA45FF491F94842AA433014735E7B9BCDA8B53551084535BB'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
hand=bpy.data.objects['Character | anatomical left hand']
landmarks=json.loads(hand['hand_landmarks'])
original=[Vector(d.vector) for d in hand.data.attributes['Unposed anatomical position'].data]
current=[hand.matrix_world@v.co for v in hand.data.vertices]
def estimate(p):
    nearest=sorted(range(len(original)),key=lambda i:(original[i]-p).length_squared)[:8]
    return sum((current[i] for i in nearest),Vector())/len(nearest)
wrist=estimate(Vector(landmarks['wrist']))
middle=estimate(Vector(landmarks['digits']['3'][0]))
axis=(middle-wrist).normalized()
rotation=Quaternion(axis,math.radians(-18))

def turn(p):return wrist+rotation@(p-wrist)
def move(obj):
    world=obj.matrix_world;inverse=world.inverted()
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            for point in key.data:
                point.co=inverse@turn(world@point.co)
        basis=obj.data.shape_keys.key_blocks[0]
        for vertex,point in zip(obj.data.vertices,basis.data):vertex.co=point.co
    else:
        for vertex in obj.data.vertices:
            vertex.co=inverse@turn(world@vertex.co)
    obj.data.update()

objects=[hand]+[obj for obj in scene.objects if obj.type=='MESH' and
         (obj.name.startswith('Character | nail left ') or obj.name.startswith('Character | nail fold left '))]
assert len(objects)==11
for obj in objects:move(obj)
scene['left_hand_pronation_radians']=math.radians(-18)
print('HAND_TURN18',len(objects),tuple(wrist),tuple(axis),flush=True)

if '--render' in sys.argv:
    from mathutils import Vector
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.49,-3.25,.83),(-.49,-2.50,.83),70,900,900),
        ('Front_Close',(-.49,-1.65,.83),(-.49,-2.50,.83),70,900,900),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
        ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,900,990),
    ):
        data=bpy.data.cameras.new('Hand pronation '+label)
        camera=bpy.data.objects.new('Hand pronation '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=20
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Hand_Orientation_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'HandOrientation.blend'),compress=True)
print('HAND_ORIENTATION_CANDIDATE_PASS',flush=True)
