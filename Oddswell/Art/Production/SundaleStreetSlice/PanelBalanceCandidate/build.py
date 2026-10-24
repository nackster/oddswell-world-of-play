"""Redistribute front/rear short-panel depth without inflating the seat."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parent
source = root.parent/'CrewCutCandidate'/'CrewCut.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == '974ADD328315034C3DD09C6C4393B825E47FFC994315366552446A313AE89EE5'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
world, inverse = pants.matrix_world, pants.matrix_world.inverted()


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)


def redistribute(p):
    y = p.y+2.4
    if y >= 0:
        weight = -.10
    else:
        weight = .12
    vertical = smooth((p.z-.725)/.075)*(1-smooth((p.z-.835)/.050))
    p.y += y*weight*vertical
    return p


maximum = 0.0
for vertex in pants.data.vertices:
    old = world@vertex.co
    new = redistribute(old.copy())
    maximum = max(maximum, (new-old).length)
    vertex.co = inverse@new
pants.data.update()
assert .01 < maximum < .025, maximum
bpy.context.view_layer.update()
surface = BVHTree.FromObject(pants, bpy.context.evaluated_depsgraph_get())
for side in ('left','right'):
    panel = bpy.data.objects['Character | sewn cotton back pocket '+side]
    to_pants = inverse@panel.matrix_world
    from_pants = to_pants.inverted()
    for i, vertex in enumerate(panel.data.vertices):
        p = redistribute(to_pants@vertex.co)
        hit, normal, _, _ = surface.ray_cast(Vector((p.x,-3,p.z)),Vector((0,1,0)),2)
        assert hit is not None and normal.y<-.1
        u, v = (i%25)/24, (i//25)/12
        offset = .0008+.0015*math.sin(math.pi*u)*math.sin(math.pi*v)
        vertex.co = from_pants@(hit+normal*offset)
    panel.data.update()
    panel_surface = BVHTree.FromObject(panel,bpy.context.evaluated_depsgraph_get())
    for label in ('inset back pocket stitch','pocket mouth topstitch'):
        seam = bpy.data.objects['Character | '+label+' '+side]
        to_panel = panel.matrix_world.inverted()@seam.matrix_world
        from_panel = to_panel.inverted()
        for spline in seam.data.splines:
            for point in spline.points:
                old = to_panel@Vector(point.co[:3])
                near, normal, _, distance = panel_surface.find_nearest(old)
                assert near is not None and distance<.04
                point.co = (*(from_panel@(near+normal*.0002)),point.co.w)

def arc(row,front):
    base=row*80
    ids=([base+j for j in range(41)] if front else [base+j for j in range(40,80)]+[base])
    points=[world@pants.data.vertices[i].co for i in ids]
    return sum((b-a).length for a,b in zip(points,points[1:]))

print('PANEL_BALANCE',maximum,'lower',arc(0,True),arc(0,False),'upper',arc(16,True),arc(16,False),flush=True)
scene['front_rear_panel_balance_max_m']=maximum
views = (
    ('Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52),
    ('Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52),
    ('Profile',(-1.65,-2.4,.82),(-.75,-2.4,.8),55),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58),
)
for label,place,target,lens in views:
    if '--quick' in sys.argv and label == 'Rear':
        continue
    if '--quick' in sys.argv and label == 'Full_Rear':
        continue
    if '--full-only' in sys.argv and label not in ('Rear','Full_Rear'):
        continue
    data=bpy.data.cameras.new('Panel balance '+label)
    camera=bpy.data.objects.new('Panel balance '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900
    scene.render.resolution_y=990 if label == 'Full_Rear' else 900
    scene.render.resolution_percentage=100
    scene.render.filepath=str(root/('Panel_Balance_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'PanelBalance.blend'),compress=True)
print('PANEL_BALANCE_CANDIDATE_PASS',flush=True)
