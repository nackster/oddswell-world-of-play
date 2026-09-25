"""Review the accepted shorts pattern close to the posed pelvis."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=Path(__file__).resolve().parents[5]/'Oddswell/Art/Production/SundaleStreetSlice/SignalJoinCandidate/SignalJoin.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='440A054D60821E8978AEFC6BB863624766C3FDE0A73CB30D691DD79DDAA4C8C8'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
for label,position,target in (
    ('Rear',(-.75,-3.45,.82),(-.75,-2.4,.80)),
    ('Front',(-.75,-1.32,.82),(-.75,-2.4,.80)),
    ('Profile',(-1.72,-2.4,.82),(-.75,-2.4,.80)),
):
    data=bpy.data.cameras.new('Upper shorts baseline '+label)
    camera=bpy.data.objects.new('Upper shorts baseline '+label,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=55;scene.camera=camera
    scene.cycles.samples=16
    scene.render.resolution_x=800;scene.render.resolution_y=800
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Upper_Shorts_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
print('UPPER_SHORTS_BASELINE_PASS',flush=True)
