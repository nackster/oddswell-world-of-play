"""Render the coordinated waist contour in full figure and gameplay views."""
import bpy
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'WaistPattern.blend'))
scene=bpy.context.scene
for label,place,target,lens,width,height in (
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ('Gameplay',None,None,None,1600,900),
):
    if place is None:camera=bpy.data.objects['CAM | gameplay street']
    else:
        data=bpy.data.cameras.new('Waist pattern full rear')
        camera=bpy.data.objects.new('Waist pattern full rear',data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(root/('Waist_Pattern_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    if place is not None:bpy.data.objects.remove(camera,do_unlink=True)
print('WAIST_PATTERN_FULL_RENDER_PASS',flush=True)
