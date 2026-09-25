"""Diagnostic native views of the hidden pelvic fit surface and posed legs."""
import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'PelvicSupport.blend'))
scene=bpy.context.scene
support=bpy.data.objects['Character | posed pelvic fitting support']
for obj in scene.objects:
    if obj.name.startswith('Character | ') and obj not in (support,bpy.data.objects['Character | anatomical legs']):obj.hide_render=True
support.hide_render=False
support.data.materials.append(bpy.data.materials['Character | warm neutral skin'])
for label,position,target in (
    ('Rear',(-.75,-3.45,.82),(-.75,-2.4,.80)),
    ('Front',(-.75,-1.32,.82),(-.75,-2.4,.80)),
    ('Profile',(-1.72,-2.4,.82),(-.75,-2.4,.80)),
):
    data=bpy.data.cameras.new('Pelvic support '+label)
    camera=bpy.data.objects.new('Pelvic support '+label,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=55;scene.camera=camera
    scene.cycles.samples=16
    scene.render.resolution_x=800;scene.render.resolution_y=800
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Pelvic_Support_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
print('PELVIC_SUPPORT_DIAGNOSTIC_RENDER_PASS',flush=True)
