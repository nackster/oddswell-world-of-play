"""Render posed knee and calf anatomy from the saved character scene."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root/'LegAxis.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='EA9524588054A81A69D5C7FC4FDC7B956DFB318DC5D9BDA4C687E22F2CFB1C4C'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
data=bpy.data.cameras.new('Knee and calf close review')
camera=bpy.data.objects.new('Knee and calf close review',data)
scene.collection.objects.link(camera)
camera.location=(-.75,-1.14,.48)
camera.rotation_euler=(Vector((-.75,-2.4,.45))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=55
scene.camera=camera
scene.cycles.samples=20
scene.render.resolution_x=900;scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Leg_Axis_Knee_Close.png')
bpy.ops.render.render(write_still=True)
print('LEG_AXIS_KNEE_CLOSE_RENDER_PASS',flush=True)
