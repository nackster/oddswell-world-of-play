import bpy
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root=Path(__file__).resolve().parents[5]
bpy.ops.wm.open_mainfile(filepath=str(root/'Oddswell/Art/Production/SundaleStreetSlice/SignalJoinCandidate/SignalJoin.blend'))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
for label,position,target in (
    ('rear',(-.75,-3.45,.82),(-.75,-2.4,.80)),
    ('front',(-.75,-1.32,.82),(-.75,-2.4,.80)),
):
    data=bpy.data.cameras.new(label);camera=bpy.data.objects.new(label,data)
    scene.collection.objects.link(camera)
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=55;scene.camera=camera
    bpy.context.view_layer.update()
    for j in (21,25,30,35,40,45,50,55,59):
        for side in (0,1):
            index=1360+2*(j-21)+side
            world=pants.matrix_world@pants.data.vertices[index].co
            point=world_to_camera_view(scene,camera,world)
            print('BRIDGE',label,j,side,index,'xyz',tuple(round(v,4) for v in world),'pixel',round(point.x*800,1),round((1-point.y)*800,1),flush=True)
    bpy.data.objects.remove(camera,do_unlink=True)
