"""Render this candidate at the original gameplay camera for scale review."""
import bpy
from pathlib import Path

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'ShoeCanvas.blend'))
scene=bpy.context.scene
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=20
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.filepath=str(root/'Shoe_Canvas_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('SHOE_CANVAS_GAMEPLAY_RENDER_PASS',flush=True)
