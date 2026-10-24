"""Retain a warm directional-lighting study from the exact posed character."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'ShortsSculptCandidate/OddsWell_Shorts_Sculpt_Candidate.blend'
SOURCE_SHA='7280891086D7F947D33305C640D97A2B464F7602B2E585AB1BDF01248BE697C7'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()==SOURCE_SHA
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.55
bpy.data.objects['Sundale | broad warm bounce'].data.energy=250
bpy.data.objects['Sundale | reflected courtyard light'].data.energy=700
assert bpy.data.objects['Sundale | warm afternoon sun'].data.energy==6
scene['lighting_study_source_sha256']=SOURCE_SHA
scene['lighting_study_sky_strength']=.55
scene['lighting_study_broad_bounce_energy']=250
scene['lighting_study_courtyard_bounce_energy']=700
main_camera=bpy.data.objects['CAM | gameplay street']
scene.camera=main_camera
scene.cycles.samples=64
scene.render.resolution_percentage=100
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.filepath=str(ROOT/'Sundale_Directional_Gameplay.png')
bpy.ops.render.render(write_still=True)
print('ODDSWELL_DIRECTIONAL_GAMEPLAY_PASS',flush=True)
data=bpy.data.cameras.new('Directional lighting full rear')
camera=bpy.data.objects.new('Directional lighting full rear',data)
scene.collection.objects.link(camera)
camera.location=(-1.45,-5.85,1.25)
camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
data.lens=58
scene.camera=camera
scene.render.resolution_x=1000
scene.render.resolution_y=1100
scene.render.filepath=str(ROOT/'Sundale_Directional_Full_Rear.png')
bpy.ops.render.render(write_still=True)
print('ODDSWELL_DIRECTIONAL_FULL_REAR_PASS',flush=True)
bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=main_camera
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.filepath=str(ROOT/'Sundale_Directional_Gameplay.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Sundale_Directional_Lighting_Candidate.blend'),compress=True)
print('ODDSWELL_DIRECTIONAL_LIGHTING_CANDIDATE_PASS',flush=True)
