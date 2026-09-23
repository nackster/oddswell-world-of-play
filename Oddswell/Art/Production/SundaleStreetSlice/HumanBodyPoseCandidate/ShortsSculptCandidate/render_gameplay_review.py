"""Render the current posed character at the retained gameplay camera."""
import bpy
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'OddsWell_Shorts_Sculpt_Candidate.blend'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='7280891086D7F947D33305C640D97A2B464F7602B2E585AB1BDF01248BE697C7'
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=48
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'Shorts_Sculpt_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('ODDSWELL_SHORTS_SCULPT_GAMEPLAY_PASS',flush=True)
