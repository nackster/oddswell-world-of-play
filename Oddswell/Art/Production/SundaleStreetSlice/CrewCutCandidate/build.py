"""Shape the retained 72k rooted scalp strands into a short graduated crop."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parent
source = root.parent / 'WaistPatternCandidate' / 'WaistPattern.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == 'B569AECCD66394C9AAE4FB3F086A9A70D7A02FD2B92849579C77E9945C569CDA'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
hair = bpy.data.objects['Character | cropped scalp fibers']


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)


lengths = []
for strand in hair.data.splines:
    points = strand.points
    base = Vector(points[0].co[:3])
    original = (Vector(points[-1].co[:3])-base).length
    crown = smooth((base.z-1.735)/.070)
    # Restrained 3-11 mm clipper graduation, with the hair combed toward the
    # forehead instead of projecting evenly from the scalp like stubble.
    scale = 1+.85*crown
    normal = Vector((base.x+.75, (base.y+2.4)*.75, (base.z-1.69)*1.2)).normalized()
    direction = (normal*(.85-.42*crown)+Vector((0,.48*crown,.02))).normalized()
    length = min(.011, original*scale)
    lengths.append(length)
    for point, t in zip(points, (0,.55,1)):
        position = base+direction*(length*t)+normal*(.00010*t)
        point.co = (*position, 1)
hair.data.bevel_depth = .000030
scene['scalp_hair_crew_cut_min_m'] = min(lengths)
scene['scalp_hair_crew_cut_max_m'] = max(lengths)
print('CREW_CUT_LENGTHS', len(lengths), min(lengths), max(lengths), flush=True)
assert .003 < min(lengths) and max(lengths) <= .011

for label, place, target, lens, width, height in (
    ('Front', (-.75,-1.25,1.65), (-.75,-2.4,1.62), 85,900,900),
    ('Three_Quarter', (-1.35,-1.58,1.67), (-.75,-2.4,1.62), 82,900,900),
    ('Full_Rear', (-1.45,-5.85,1.25), (-.75,-2.4,.97), 58,900,990),
):
    data = bpy.data.cameras.new('Crew cut ' + label)
    camera = bpy.data.objects.new('Crew cut ' + label, data)
    scene.collection.objects.link(camera)
    camera.location = place
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens = lens
    scene.camera = camera
    scene.cycles.samples = 20
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(root/('Crew_Cut_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
scene.camera = bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'CrewCut.blend'), compress=True)
print('CREW_CUT_CANDIDATE_PASS', flush=True)
