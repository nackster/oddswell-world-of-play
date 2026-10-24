"""Native close, full-figure and gameplay review of the new cotton panels."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out / 'FourPanelCotton.blend'))
scene = bpy.context.scene
views = (
    ('Rear', (-1.45, -5.85, 1.25), (-.75, -2.4, .97), 58, 760, 840),
    ('Front', (-.75, .4, 1.20), (-.75, -2.4, .97), 50, 760, 840),
    ('ShortsRear', (-.75, -3.60, .88), (-.73, -2.4, .76), 58, 840, 840),
    ('Profile', (-3.35, -2.4, 1.20), (-.75, -2.4, .97), 50, 760, 840),
)
requested = sys.argv[sys.argv.index('--view') + 1] if '--view' in sys.argv else None
for label, position, target, lens, width, height in views:
    if requested and requested != label:
        continue
    data = bpy.data.cameras.new('Four panel cotton review ' + label)
    camera = bpy.data.objects.new('Four panel cotton review ' + label, data)
    scene.collection.objects.link(camera)
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.lens = lens
    scene.camera = camera
    scene.cycles.samples = 20
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(out / ('FourPanelCotton_' + label + '.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    print('FOUR_PANEL_COTTON_RENDER', label, flush=True)
if requested is None or requested == 'Gameplay':
    scene.camera = bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples = 24
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    scene.render.filepath = str(out / 'FourPanelCotton_Gameplay.png')
    bpy.ops.render.render(write_still=True)
    print('FOUR_PANEL_COTTON_RENDER Gameplay', flush=True)
