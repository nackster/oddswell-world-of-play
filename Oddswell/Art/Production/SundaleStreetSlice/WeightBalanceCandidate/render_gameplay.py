"""Render and measure the retained weight-shift scene at gameplay scale."""
import bpy
import hashlib
from pathlib import Path

root=Path(__file__).resolve().parent
source=root/'WeightBalance.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='31ED385743603A1ECCADD0DEC422A0DEDE0E2EE2E2F977AAB311D4EED1C525AF'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
head=bpy.data.objects['Character | anatomical head']
head_points=[head.matrix_world@v.co for v in head.data.vertices]
head_points=[p for p in head_points if 1.55<p.z<1.78]
sole=bpy.data.objects['Character | sneaker sole right']
sole_points=[sole.matrix_world@v.co for v in sole.data.vertices]
low=min(p.z for p in sole_points)
contact=[p for p in sole_points if p.z<low+.0003]
gap=sum(p.x for p in contact)/len(contact)-sum(p.x for p in head_points)/len(head_points)
assert .09<gap<.10,gap
print('WEIGHT_BALANCE_HEAD_TO_STANCE_M',gap,flush=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=20
scene.render.resolution_x=1200;scene.render.resolution_y=675
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Weight_Balance_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('WEIGHT_BALANCE_GAMEPLAY_PASS',flush=True)
