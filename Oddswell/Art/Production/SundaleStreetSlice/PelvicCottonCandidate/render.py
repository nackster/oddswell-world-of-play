"""Render the saved cotton candidate in close, full-body, and gameplay views."""
import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'PelvicCotton.blend'))
scene=bpy.context.scene
views=(
    ('Rear',(-.75,-3.45,.82),(-.75,-2.4,.80),55,800,800,16),
    ('Front',(-.75,-1.32,.82),(-.75,-2.4,.80),55,800,800,16),
    ('Profile',(-1.72,-2.4,.82),(-.75,-2.4,.80),55,800,800,16),
    ('FullRear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990,20),
)
for label,position,target,lens,width,height,samples in views:
    data=bpy.data.cameras.new('Pelvic cotton review '+label)
    camera=bpy.data.objects.new('Pelvic cotton review '+label,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.cycles.samples=samples
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('PelvicCotton_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=20
scene.render.resolution_x=1280;scene.render.resolution_y=720
scene.render.filepath=str(out/'PelvicCotton_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('PELVIC_COTTON_REVIEW_PASS',flush=True)
