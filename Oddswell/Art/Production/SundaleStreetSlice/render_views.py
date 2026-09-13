"""Reopen the saved scene, verify its materials, and render two more native views."""
import bpy
import bmesh
import json
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
scene=bpy.context.scene
assert all(name in bpy.data.collections for name in ('Character','Trees and planting','Arena','Court','Architecture'))
assert len([image for image in bpy.data.images if image.source=='FILE' and image.packed_file])==6
assert sum(o.name.startswith('Character | anatomical ') for o in scene.objects)==4
assert scene.render.engine=='CYCLES'
main=scene.camera
if not scene.get('flat_court_paint',False):
    for obj in scene.objects:
        if obj.name.startswith('Court | ') and obj.type=='CURVE':
            line_z=obj.data.splines[0].points[0].co.z
            obj.scale.z=.01;obj.location.z=.08475-line_z*.01
        if obj.name.startswith('Court | painted key'):
            for vertex in obj.data.vertices:vertex.co.z=.0846+(vertex.co.z-.088)*(.0002/.007)
    scene['flat_court_paint']=True
head=bpy.data.objects.get('Character | anatomical head')
bm=bmesh.new();bm.from_mesh(head.data)
stray=[face for face in bm.faces if any(abs(vertex.co.x+.75)>=.15 or vertex.co.z<=1.59 for vertex in face.verts)]
if stray:
    bmesh.ops.delete(bm,geom=stray,context='FACES')
    bm.to_mesh(head.data)
bm.free()
# Bring the curve details along with the walking shoes/shorts in the first
# saved scene. Rebuilt scenes already contain this correction.
if not scene.get('clothing_details_posed',False):
    origin=Vector((-.75,-2.4,.06))
    for obj in scene.objects:
        if obj.type!='CURVE' or not any(obj.name.startswith('Character | '+p) for p in ('shoe lace','back pocket seam')):continue
        for spline in obj.data.splines:
            for point in spline.points:
                relative=Vector(point.co[:3])-origin
                sign=1 if relative.x>0 else -1
                pivot=Vector((sign*.13,0,.9))
                angle=sign*.14*min(1,max(0,(.95-relative.z)/.20))
                point.co=(*(pivot+Matrix.Rotation(angle,3,'X')@(relative-pivot)+origin),1)
    scene['clothing_details_posed']=True
scene.render.filepath=str(ROOT/'StreetSlice_Gameplay.png')
bpy.ops.render.render(write_still=True)
views=[
    ('Court_and_Arena',(17,-.5,2.4),(4,30,4),30),
    ('Architecture_Detail',(-1,7,2.3),(-6.2,14,3.6),31),
]
for name,pos,target,lens in ([] if '--main-only' in sys.argv else views):
    data=bpy.data.cameras.new('CAM | '+name)
    old=bpy.data.objects.get('CAM | '+name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    camera=bpy.data.objects.new('CAM | '+name,data)
    scene.collection.objects.link(camera)
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_end=500
    scene.camera=camera
    scene.view_settings.exposure=.15 if name=='Architecture_Detail' else -.9
    scene.render.resolution_x=1600;scene.render.resolution_y=900
    scene.cycles.samples=96
    scene.render.filepath=str(ROOT/('StreetSlice_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_STREET_SLICE_VIEW_PASS',name,flush=True)
scene.camera=main
scene.view_settings.exposure=-.9
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.cycles.samples=160
scene.render.filepath=str(ROOT/'StreetSlice_Gameplay.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
evidence=json.loads((ROOT/'scene-evidence.json').read_text(encoding='utf-8'))
evidence.update({'independent_reopen':'PASS','packed_texture_maps':6,'additional_views':['Court_and_Arena','Architecture_Detail'],'additional_view_resolution':[1600,900],'additional_view_samples':96,'objects':len(scene.objects),'source':'Original native scene/garments/plant geometry, CC0 MakeHuman anatomical surfaces, six CC0 Poly Haven stone/bark texture maps'})
(ROOT/'scene-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_REOPEN_PASS',flush=True)
