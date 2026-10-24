"""Review the exact saved leg-axis scene at profile, full-body and gameplay scale."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root/'LegAxis.blend'
with source.open('rb') as stream:
    print('LEG_AXIS_SAVED_SHA256',hashlib.file_digest(stream,'sha256').hexdigest(),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
for label,place,target,lens,width,height in (
    ('Profile',(-1.65,-2.4,.82),(-.75,-2.4,.8),55,900,900),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ('Gameplay',None,None,None,1600,900),
):
    if place is None:camera=bpy.data.objects['CAM | gameplay street']
    else:
        data=bpy.data.cameras.new('Leg-axis review '+label)
        camera=bpy.data.objects.new('Leg-axis review '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(root/('Leg_Axis_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    if place is not None:bpy.data.objects.remove(camera,do_unlink=True)
print('LEG_AXIS_REVIEW_RENDER_PASS',flush=True)
