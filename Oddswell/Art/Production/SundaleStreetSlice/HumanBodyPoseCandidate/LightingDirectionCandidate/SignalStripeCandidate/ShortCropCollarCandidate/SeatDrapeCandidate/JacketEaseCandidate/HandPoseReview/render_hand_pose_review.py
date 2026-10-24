"""Close hand and cuff views for the next joint-aware pose pass."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'OddsWell_Jacket_Ease_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='D9AF666965C9F7AAF78A27F9C119D285CD9747559F7635F58CF1DFC37B9D7E20'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
out=root
for label,place,target in (
    ('Rear_Near',(-.49,-3.25,.83),(-.49,-2.50,.83)),
    ('Outer_Far',(-1.70,-2.25,.84),(-1.01,-2.25,.84)),
    ('Front_Near',(-.49,-1.65,.83),(-.49,-2.50,.83))):
    data=bpy.data.cameras.new('Hand review '+label)
    camera=bpy.data.objects.new('Hand review '+label,data);scene.collection.objects.link(camera)
    camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=70;scene.camera=camera;scene.cycles.samples=32
    scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
print('HAND_POSE_REVIEW_PASS',flush=True)
