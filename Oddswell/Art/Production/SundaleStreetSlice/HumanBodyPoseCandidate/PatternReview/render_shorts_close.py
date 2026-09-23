"""Render the retained shorts pattern from the exact posed Blender candidate."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'OddsWell_Human_Body_Pose_Candidate.blend'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='001FB31C1C206A4C72245873E44850718CCC5F70CB2D699888FB0E28F727DBEA'
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
original_camera=scene.camera
for name,position in [('Front',(-.75,-1.25,.82)),('Rear',(-.75,-3.55,.82))]:
    data=bpy.data.cameras.new('Pattern review '+name)
    camera=bpy.data.objects.new('Pattern review '+name,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector((-.75,-2.4,.8))-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=52
    scene.camera=camera
    scene.cycles.samples=48
    scene.render.resolution_x=1000
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.filepath=str(ROOT/('Shorts_Close_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_SHORTS_CLOSE_PASS',name,flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=original_camera
