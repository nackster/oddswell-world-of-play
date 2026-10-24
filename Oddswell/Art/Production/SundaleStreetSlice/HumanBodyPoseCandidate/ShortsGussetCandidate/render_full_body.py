"""Render full-body checks from the exact shorts-gusset candidate."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'OddsWell_Shorts_Gusset_Candidate.blend'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='DC8F2911249FA07AD128BE2C692CD5934AAAAF435C90B171B606147581F8AFAB'
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
original_camera=scene.camera
for name,position,target,lens in [
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40),
]:
    data=bpy.data.cameras.new('Gusset full '+name)
    camera=bpy.data.objects.new('Gusset full '+name,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=64
    scene.render.resolution_x=1000
    scene.render.resolution_y=1100
    scene.render.resolution_percentage=100
    scene.render.filepath=str(ROOT/('Shorts_Gusset_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_GUSSET_FULL_RENDER_PASS',name,flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=original_camera
