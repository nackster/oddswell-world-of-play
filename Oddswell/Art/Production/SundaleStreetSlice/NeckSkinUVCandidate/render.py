"""Native close, full-figure and gameplay review of the new cotton panels."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out / 'NeckSkinUV.blend'))
scene = bpy.context.scene
views = (
    ('Front', (-.75, .4, 1.20), (-.75, -2.4, .97), 50, 760, 840),
    ('NeckFront', (-.65, -1.65, 1.51), (-.69, -2.34, 1.48), 70, 900, 900),
    ('NeckRear', (-.66, -3.03, 1.51), (-.69, -2.34, 1.48), 70, 900, 900),
)
requested = sys.argv[sys.argv.index('--view') + 1] if '--view' in sys.argv else None
for label, position, target, lens, width, height in views:
    if requested and requested != label:
        continue
    data = bpy.data.cameras.new('Neck skin review ' + label)
    camera = bpy.data.objects.new('Neck skin review ' + label, data)
    scene.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    scene.camera = camera
    scene.cycles.samples = 12
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(out / ('NeckSkinUV_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    print('NECK_COLLAR_RENDER', label, flush=True)
if requested is None or requested == 'Gameplay':
    scene.camera = bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples = 24
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = str(out / 'NeckSkinUV_Gameplay.png')
    bpy.ops.render.render(write_still=True)
    print('NECK_COLLAR_RENDER Gameplay', flush=True)
