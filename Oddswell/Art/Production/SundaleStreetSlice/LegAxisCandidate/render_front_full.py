"""Render a full-front anatomy and garment review from the saved scene."""
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
data=bpy.data.cameras.new('Full front review')
camera=bpy.data.objects.new('Full front review',data)
scene.collection.objects.link(camera)
camera.location=(-1.45,1.05,1.25)
camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=58
scene.camera=camera
scene.cycles.samples=20
scene.render.resolution_x=900;scene.render.resolution_y=990
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Leg_Axis_Full_Front.png')
bpy.ops.render.render(write_still=True)
print('LEG_AXIS_FULL_FRONT_RENDER_PASS',flush=True)
