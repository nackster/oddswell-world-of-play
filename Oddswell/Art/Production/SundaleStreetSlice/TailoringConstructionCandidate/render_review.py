"""Review saved sewn shorts at full body and gameplay scales."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root/'TailoringConstruction.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='F3844EDB5509E0E894B97751E011BDD35DEAB814F2011DD15B979466DDF164E3'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
data=bpy.data.cameras.new('Tailoring full rear review')
camera=bpy.data.objects.new('Tailoring full rear review',data)
scene.collection.objects.link(camera)
camera.location=(-1.45,-5.85,1.25)
camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=58
scene.camera=camera
scene.cycles.samples=20
scene.render.resolution_x=900;scene.render.resolution_y=990
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Tailoring_Full_Rear.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.render.resolution_x=1200;scene.render.resolution_y=675
scene.render.filepath=str(root/'Tailoring_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('TAILORING_REVIEW_PASS',flush=True)
