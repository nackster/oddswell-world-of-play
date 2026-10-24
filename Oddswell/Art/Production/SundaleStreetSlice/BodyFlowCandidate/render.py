"""Native comparison views of the torso/hip flow study."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out / 'BodyFlow.blend'))
scene = bpy.context.scene
views = (
    ('Rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 760, 840),
    ('Front', (-.75, .4, 1.20), (-.75, -2.4, .97), 50, 760, 840),
    ('TorsoRear', (-.75, -4.1, 1.15), (-.75, -2.4, 1.11), 65, 760, 800),
    ('Profile', (-3.35, -2.4, 1.20), (-.75, -2.4, .97), 50, 760, 840),
)
requested = sys.argv[sys.argv.index('--view') + 1] if '--view' in sys.argv else None
for label, position, target, lens, width, height in views:
    if requested and requested != label:
        continue
    data = bpy.data.cameras.new('Body flow review ' + label)
    camera = bpy.data.objects.new('Body flow review ' + label, data)
    scene.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    scene.camera = camera
    scene.cycles.samples = 20
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(out / ('BodyFlow_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    print('BODY_FLOW_RENDER', label, flush=True)
if requested is None or requested == 'Gameplay':
    scene.camera = bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples = 24
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = str(out / 'BodyFlow_Gameplay.png')
    bpy.ops.render.render(write_still=True)
    print('BODY_FLOW_RENDER Gameplay', flush=True)
