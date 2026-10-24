"""Relax the shorts gusset fan and refit its stitched back pockets."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

output = Path(__file__).resolve().parent
source = output.parent / 'HumanBodyPoseCandidate/LightingDirectionCandidate/SignalStripeCandidate/ShortCropCollarCandidate/SeatDrapeCandidate/FaceExpressionCandidate/FaceExpression.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == 'BB40C6B55EA5FF69B22E93C98F92B33ACA5823F0700146EA1E3D9018DD6E64E8'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
mesh = pants.data
world = pants.matrix_world
inverse = world.inverted()
positions = [world @ v.co for v in mesh.vertices]
neighbors = [set() for _ in mesh.vertices]
for edge in mesh.edges:
    a,b = edge.vertices
    neighbors[a].add(b)
    neighbors[b].add(a)

def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)

weights=[]
for p in positions:
    x = p.x+.75
    rear = smooth((-p.y-2.397)/.085)
    heights = smooth((p.z-.712)/.026) * (1-smooth((p.z-.807)/.057))
    center = 1-smooth((abs(x)-.085)/.155)
    weights.append(rear*heights*center)
for _ in range(18):
    updated=[]
    for i,p in enumerate(positions):
        weight = weights[i]
        if weight < .0001 or not neighbors[i]:
            updated.append(p)
            continue
        average_y = sum(positions[j].y for j in neighbors[i])/len(neighbors[i])
        updated.append(Vector((p.x,p.y+(average_y-p.y)*.55*weight,p.z)))
    positions = updated

max_shift=0
changed=0
for i,p in enumerate(positions):
    before=world @ mesh.vertices[i].co
    shift=abs(p.y-before.y)
    if shift>1e-8:
        mesh.vertices[i].co=inverse@p
        max_shift=max(max_shift,shift)
        changed+=1
mesh.update()
print('SEAT_RELAX', changed, max_shift, flush=True)
assert changed>100
scene['shorts_seat_relax_max_shift_m']=max_shift
bpy.context.view_layer.update()
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
stitched=0
for seam in scene.objects:
    if seam.type!='CURVE' or not seam.name.startswith('Character | back pocket seam'):
        continue
    transform=pants.matrix_world.inverted()@seam.matrix_world
    back=transform.inverted()
    for spline in seam.data.splines:
        for point in spline.points:
            prior=transform@Vector(point.co[:3])
            hit,normal,_,_=surface.ray_cast(Vector((prior.x,-3.0,prior.z)),Vector((0,1,0)),2)
            assert hit is not None and normal.y<-.1
            point.co=(*(back@(hit+normal*.0013)),point.co.w)
            stitched+=1
assert stitched>=90
print('SEAT_RELAX_STITCH_REFIT',stitched,flush=True)

if '--render' in sys.argv:
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.75,-3.55,.82),(-.75,-2.4,.8),52,800,800),
        ('Rear_Three_Quarter',(-1.55,-3.45,.85),(-.75,-2.4,.82),52,800,800),
        ('Full_Rear',(-.75,-5.1,1.05),(-.75,-2.4,.92),51,900,1100),
    ):
        data=bpy.data.cameras.new('Seat relaxation '+label)
        camera=bpy.data.objects.new('Seat relaxation '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=16
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Seat_Relax_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'SeatRelax.blend'),compress=True)
print('SEAT_RELAX_CANDIDATE_PASS',flush=True)
