import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'NarrowGait.blend'))
scene=bpy.context.scene
data=bpy.data.cameras.new('Narrow gait full profile')
camera=bpy.data.objects.new('Narrow gait full profile',data)
scene.collection.objects.link(camera)
camera.location=(-2.55,-2.4,1.25)
camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=55;scene.camera=camera
scene.cycles.samples=20
scene.render.resolution_x=900;scene.render.resolution_y=990
scene.render.resolution_percentage=100
scene.render.filepath=str(out/'Narrow_Gait_Profile.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.render.resolution_x=1200;scene.render.resolution_y=675
scene.render.filepath=str(out/'Narrow_Gait_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('NARROW_GAIT_ADDITIONAL_VIEWS_PASS',flush=True)
