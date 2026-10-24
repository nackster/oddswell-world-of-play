import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'SignalJoin.blend'))
scene=bpy.context.scene
data=bpy.data.cameras.new('Signal join full rear')
camera=bpy.data.objects.new('Signal join full rear',data)
scene.collection.objects.link(camera)
camera.location=(-1.45,-5.85,1.25)
camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=58;scene.camera=camera
scene.cycles.samples=20
scene.render.resolution_x=900;scene.render.resolution_y=990
scene.render.resolution_percentage=100
scene.render.filepath=str(out/'Signal_Join_Full_Rear.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=14
scene.render.resolution_x=1280;scene.render.resolution_y=720
scene.render.filepath=str(out/'Signal_Join_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('SIGNAL_JOIN_FULL_REVIEW_PASS',flush=True)
