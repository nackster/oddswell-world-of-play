"""Fit the separately rebuilt shorts gusset into the verified posed scene."""
import bpy
import gzip
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'OddsWell_Human_Body_Pose_Candidate.blend'
MESH=ROOT/'gusset_mesh.json.gz'
with SOURCE.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='001FB31C1C206A4C72245873E44850718CCC5F70CB2D699888FB0E28F727DBEA'
with MESH.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='0DE28726C9091D315F7DF1E3167C8DDC97C14AF8E9B163E200722DBDBE26C41E'
with gzip.open(MESH,'rt',encoding='utf-8') as stream:
    payload=json.load(stream)
if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(payload['vertices'])==7198 and len(payload['faces'])==7080
assert (pants.location-Vector(payload['object_location'])).length<.000001
assert abs(scene['character_ground_offset']-payload['character_ground_offset'])<.000001
old=pants.data
mesh=bpy.data.meshes.new('Character | shorts with shaped gusset')
mesh.from_pydata(payload['vertices'],[],payload['faces'])
mesh.update()
for material in old.materials:mesh.materials.append(material)
for polygon in mesh.polygons:polygon.use_smooth=True
pants.data=mesh
for group in list(pants.vertex_groups):pants.vertex_groups.remove(group)
waist=pants.vertex_groups.new(name='Waist attachment')
for vertex in mesh.vertices:
    weight=max(0,min(1,(vertex.co.z-.06-.875)/.025))
    if weight>0:waist.add([vertex.index],weight,'REPLACE')
scene['cotton_drape_maximum_delta_m']=payload['cotton_drape_maximum_delta_m']
scene['short_leg_contact_corrections']=payload['short_leg_contact_corrections']
scene['anatomical_short_leg_refinement_m']=payload['anatomical_short_leg_refinement_m']
scene['shorts_gusset_width_m']=.044
scene['shorts_gusset_source_mesh_sha256']='0DE28726C9091D315F7DF1E3167C8DDC97C14AF8E9B163E200722DBDBE26C41E'
bpy.context.view_layer.update()
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
maximum_seam_adjustment=0
for obj in scene.objects:
    if obj.type!='CURVE' or not any(obj.name.startswith('Character | '+part) for part in ('back pocket seam','shorts leg hem')):
        continue
    for spline in obj.data.splines:
        for point in spline.points:
            initial=Vector(point.co[:3])
            hit,normal,_,distance=surface.find_nearest(initial)
            assert hit is not None and distance<.035,(obj.name,distance)
            point.co=(*(hit+normal*.001),1)
            maximum_seam_adjustment=max(maximum_seam_adjustment,(Vector(point.co[:3])-initial).length)
scene['shorts_gusset_maximum_seam_refit_m']=maximum_seam_adjustment

original_camera=scene.camera
for name,position in [('Front',(-.75,-1.25,.82)),('Rear',(-.75,-3.55,.82))]:
    data=bpy.data.cameras.new('Gusset study '+name)
    camera=bpy.data.objects.new('Gusset study '+name,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector((-.75,-2.4,.8))-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=52
    scene.camera=camera
    scene.cycles.samples=48
    scene.render.resolution_x=1000
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.filepath=str(ROOT/('Shorts_Gusset_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_GUSSET_CANDIDATE_RENDER',name,flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=original_camera
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'OddsWell_Shorts_Gusset_Candidate.blend'),compress=True)
print('ODDSWELL_GUSSET_CANDIDATE_PASS',maximum_seam_adjustment,flush=True)
