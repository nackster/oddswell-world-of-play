"""Reopen and validate the scene; render gameplay and five inspection views."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
scene=bpy.context.scene
scene.cycles.device='GPU' if '--gpu' in sys.argv else 'CPU'
if '--gpu' in sys.argv:
    devices=bpy.context.preferences.addons['cycles'].preferences
    devices.compute_device_type='OPTIX';devices.get_devices()
    for device in devices.devices:device.use=device.type=='OPTIX'
assert all(name in bpy.data.collections for name in ('Character','Trees and planting','Arena','Court','Architecture'))
assert len([image for image in bpy.data.images if image.source=='FILE' and image.packed_file])==24
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
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.cycles.samples=160;scene.view_settings.exposure=0
selected=sys.argv[sys.argv.index('--view')+1] if '--view' in sys.argv else None
if selected in (None,'Gameplay'):bpy.ops.render.render(write_still=True)
views=[
    ('Court_and_Arena',(17,-.5,2.4),(4,30,4),30,1600,900),
    ('Architecture_Detail',(-1.2,1.8,2.2),(-6.2,5,2.5),31,1600,900),
    ('Character_Detail',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
    ('Landscape_Detail',(6,-4.4,1.55),(1.0,8,2.1),38,1000,1100),
    ('Character_ThreeQuarter',(1.8,.2,1.35),(-.75,-2.4,.97),58,1000,1100),
]
for name,pos,target,lens,width,height in ([] if '--main-only' in sys.argv else views):
    if selected and name!=selected:continue
    data=bpy.data.cameras.new('CAM | '+name)
    old=bpy.data.objects.get('CAM | '+name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    camera=bpy.data.objects.new('CAM | '+name,data)
    scene.collection.objects.link(camera)
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_end=500
    scene.camera=camera
    scene.view_settings.exposure=0
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.cycles.samples=96
    scene.render.filepath=str(ROOT/('StreetSlice_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_STREET_SLICE_VIEW_PASS',name,flush=True)
scene.camera=main
scene.view_settings.exposure=0
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.cycles.samples=160
scene.render.filepath=str(ROOT/'StreetSlice_Gameplay.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'),compress=True)
evidence=json.loads((ROOT/'scene-evidence.json').read_text(encoding='utf-8'))
evidence.update({'independent_reopen':'PASS','packed_texture_maps':17,'additional_views':[v[0] for v in views],'additional_view_resolutions':{v[0]:list(v[4:]) for v in views},'additional_view_samples':96,'objects':len(scene.objects),'resolution':[1920,1080],'samples':160,'source':'Native scene/garments/plant geometry, CC0 MakeHuman anatomical surfaces, six CC0 Poly Haven stone/bark texture maps and one CC0 photographed sky environment; adapted CC0 Jacaranda model with ten packed 2K maps'})
evidence['render_device']='OPTIX' if '--gpu' in sys.argv else 'CPU'
evidence['packed_texture_maps']=24
evidence['canopy']='Raised Jacaranda branching with adapted CC0 Island Tree 01 broad-leaf clusters; same leaf family in foreground shrubs'
(ROOT/'scene-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_REOPEN_PASS',flush=True)
