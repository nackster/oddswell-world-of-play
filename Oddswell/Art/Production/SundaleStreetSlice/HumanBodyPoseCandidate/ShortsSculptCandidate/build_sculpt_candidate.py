"""Make an editable shorts-shape study from the exact retained gusset."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'ShortsGussetCandidate/OddsWell_Shorts_Gusset_Candidate.blend'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper() == 'DC8F2911249FA07AD128BE2C692CD5934AAAAF435C90B171B606147581F8AFAB'
if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
mesh = pants.data
before = [v.co.copy() for v in mesh.vertices]
neighbors = [set() for _ in before]
for edge in mesh.edges:
    a, b = edge.vertices
    neighbors[a].add(b)
    neighbors[b].add(a)

# Relax the most conspicuous crumpled left inseam without moving its open hem.
positions = before
for _ in range(10):
    updated = []
    for i, p in enumerate(positions):
        x = p.x + .75
        z = p.z
        region = math.exp(-((x+.105)/.115)**2 - ((z-.765)/.07)**2)
        region *= min(1, max(0, (z-.672)/.04))
        if region > .001:
            average = sum((positions[n] for n in neighbors[i]), Vector()) / len(neighbors[i])
            updated.append(p.lerp(average, .26*region))
        else:
            updated.append(p.copy())
    positions = updated

for vertex, p in zip(mesh.vertices, positions):
    x = p.x+.75
    z = p.z
    front = min(1, max(0, (p.y+2.405)/.085))
    upper = math.exp(-((z-.864)/.060)**2)
    # Shape the pocket/upper-thigh volume and a shallow sewn-fly valley in the cloth.
    fullness = .006*math.exp(-((abs(x)-.135)/.067)**2)*upper
    fly = -.003*math.exp(-((x-.005)/.013)**2)*math.exp(-((z-.877)/.061)**2)
    # One broad diagonal compression fold resolves the front panel toward the stride.
    left = math.exp(-((x+.115)/.09)**2)
    line = .835-.28*(x+.17)
    fold = .003*left*math.exp(-((z-line)/.017)**2)
    p.y += front*(fullness+fly+fold)
    vertex.co = p
mesh.update()
bpy.context.view_layer.update()
surface = BVHTree.FromObject(pants, bpy.context.evaluated_depsgraph_get())
for obj in scene.objects:
    if obj.type != 'CURVE' or not any(obj.name.startswith('Character | '+part) for part in ('back pocket seam', 'shorts leg hem')):
        continue
    for spline in obj.data.splines:
        for point in spline.points:
            hit, normal, _, distance = surface.find_nearest(Vector(point.co[:3]))
            assert hit is not None and distance < .025
            point.co = (*(hit+normal*.001), 1)

scene['shorts_sculpt_parent_sha256']='DC8F2911249FA07AD128BE2C692CD5934AAAAF435C90B171B606147581F8AFAB'
scene['shorts_sculpt_maximum_displacement_m']=max((a-b.co).length for a,b in zip(before,mesh.vertices))
out = ROOT
source_camera = scene.camera
source_filepath=scene.render.filepath
source_resolution=(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)
source_samples=scene.cycles.samples
for name, position, target, lens, width, height in [
    ('Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52,1000,1000),
    ('Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52,1000,1000),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
]:
    camera_data = bpy.data.cameras.new('Tailoring study '+name)
    camera = bpy.data.objects.new('Tailoring study '+name,camera_data)
    scene.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.lens = lens
    scene.camera = camera
    scene.cycles.samples = 48 if name in ('Front','Rear') else 64
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(out/('Shorts_Sculpt_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_SHORTS_SCULPT_RENDER',name,flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera = source_camera
scene.render.filepath=source_filepath
scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=source_resolution
scene.cycles.samples=source_samples
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Shorts_Sculpt_Candidate.blend'),compress=True)
print('ODDSWELL_SHORTS_SCULPT_PASS',scene['shorts_sculpt_maximum_displacement_m'],flush=True)
