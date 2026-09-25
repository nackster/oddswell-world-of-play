"""Extend the native signal material over the occluded right armhole."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=Path(__file__).resolve().parents[5]/'Oddswell/Art/Production/SundaleStreetSlice/NarrowGaitCandidate/NarrowGait.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='A07CE243DEEFD7A667D161AEA746FCBA0D267F4184838214E9D9B4CED54E3692'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
material=coat.data.materials[0]
assert material.name=='Character | slate weave with continuous teal signal'
limits=[n for n in material.node_tree.nodes if n.type=='MATH' and n.operation=='LESS_THAN' and abs(n.inputs[1].default_value+.573)<1e-6]
assert len(limits)==1
limits[0].inputs[1].default_value=-.535
scene['right_armhole_signal_limit_x_m']=-.535
upper=[n for n in material.node_tree.nodes if n.type=='MATH' and n.operation=='LESS_THAN' and abs(n.inputs[1].default_value-1.3437)<1e-5]
assert len(upper)==1
upper[0].inputs[1].default_value=1.347
scene['rear_signal_upper_cutoff_m']=1.347
print('SIGNAL_LIMIT',limits[0].name,limits[0].inputs[1].default_value,flush=True)

for label,position,target,lens in (
    ('Rear',(-.75,-3.58,1.18),(-.75,-2.4,1.18),55),
):
    data=bpy.data.cameras.new('Signal join '+label)
    camera=bpy.data.objects.new('Signal join '+label,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Signal_Join_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'SignalJoin.blend'),compress=True)
print('SIGNAL_JOIN_STUDY_SAVED',flush=True)
