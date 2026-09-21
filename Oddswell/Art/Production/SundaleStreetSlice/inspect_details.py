"""Fast, independent close-up renders for native geometry review."""
import bpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
scene=bpy.context.scene
scene.cycles.device='GPU' if '--gpu' in sys.argv else 'CPU'
if '--gpu' in sys.argv:
    devices=bpy.context.preferences.addons['cycles'].preferences
    devices.compute_device_type='OPTIX';devices.get_devices()
    for device in devices.devices:device.use=device.type=='OPTIX'
scene.cycles.samples=48
scene.render.resolution_x=1000;scene.render.resolution_y=1100
views=[
    ('Character_Detail',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58),
    ('Landscape_Detail',(6,-4.4,1.55),(1.0,8,2.1),38),
    ('Character_ThreeQuarter',(1.8,.2,1.35),(-.75,-2.4,.97),58),
]
if '--head-only' in sys.argv:
    views=[('Head_Front',(-.75,-1.15,1.74),(-.75,-2.36,1.69),75),('Head_Profile',(.40,-2.30,1.73),(-.75,-2.36,1.69),75)]
for name,pos,target,lens in views:
    if '--front-only' in sys.argv and name!='Character_ThreeQuarter':continue
    data=bpy.data.cameras.new('INSPECT | '+name)
    camera=bpy.data.objects.new('INSPECT | '+name,data);scene.collection.objects.link(camera)
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.render.filepath=str(ROOT/('StreetSlice_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('ODDSWELL_DETAIL_RENDER_PASS',name,flush=True)
