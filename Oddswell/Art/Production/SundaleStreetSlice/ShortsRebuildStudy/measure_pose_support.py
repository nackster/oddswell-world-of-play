"""Pose the licensed MakeHuman pelvic surface and measure cotton ease."""
import bpy
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[5]
bpy.ops.wm.open_mainfile(filepath=str(root/'Oddswell/Art/Production/SundaleStreetSlice/SignalJoinCandidate/SignalJoin.blend'))
scene=bpy.context.scene
source=root/'Oddswell/Art/Production/SundaleStreetSlice/source-assets/makehuman-base.obj'
vertices=[];faces=[];group=''
for line in source.read_text(encoding='utf-8').splitlines():
    a=line.split()
    if not a:continue
    if a[0]=='v':vertices.append(Vector(tuple(map(float,a[1:4]))))
    elif a[0]=='g':group=a[1]
    elif a[0]=='f' and group=='body':faces.append([int(x.split('/')[0])-1 for x in a[1:]])
used={i for face in faces for i in face}
low=min(vertices[i].y for i in used)
unit=1.8/(max(vertices[i].y for i in used)-low)
converted=[Vector((v.x*unit,v.z*unit,(v.y-low)*unit)) for v in vertices]
origin=Vector((-.75,-2.4,.06+scene['character_ground_offset']))
def walk(relative):
    side=1 if relative.x>0 else -1
    legy=.075 if side>0 else -.065
    ankle=Vector((side*.14,legy+.015,.14))
    knee=Vector((side*.14,legy+.035,.48))
    hip=Vector((side*.13,0,.9))
    ankle_angle=(-.04 if side>0 else .20)*min(1,max(0,(.29-relative.z)/.07))
    knee_angle=(-.09 if side>0 else -.30)*min(1,max(0,(.53-relative.z)/.10))
    hip_angle=(.13 if side>0 else -.16)*min(1,max(0,(.95-relative.z)/.20))
    p=ankle+Matrix.Rotation(ankle_angle,3,'X')@(relative-ankle)
    p=knee+Matrix.Rotation(knee_angle,3,'X')@(p-knee)
    p=hip+Matrix.Rotation(hip_angle,3,'X')@(p-hip)
    if side<0:p.z+=.013*min(1,max(0,(.95-relative.z)/.20))
    return p
selection=[face for face in faces if all(.64<converted[i].z<.97 for i in face)]
ids=sorted({i for face in selection for i in face});mapping={source:index for index,source in enumerate(ids)}
points=[walk(converted[i])+origin for i in ids]
mesh=bpy.data.meshes.new('Licensed posed pelvic support');mesh.from_pydata(points,[],[[mapping[i] for i in face] for face in selection]);mesh.update()
support=bpy.data.objects.new('Character | posed pelvic support',mesh);scene.collection.objects.link(support)
support.hide_render=True;support.display_type='WIRE'
support['source']='source-assets/makehuman-base.obj'
support['purpose']='Static internal shorts fitting support'
bpy.context.view_layer.update()
body=BVHTree.FromObject(support,bpy.context.evaluated_depsgraph_get())
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
cloth=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
inv=pants.matrix_world.inverted()
print('SUPPORT',len(points),len(selection),'ground',scene['character_ground_offset'],flush=True)
for z in (.76,.78,.80,.82,.84,.86,.88,.90):
    for x in (-.84,-.75,-.66):
        start=Vector((x,-3,z));direction=Vector((0,1,0))
        skin_hit=body.ray_cast(start,direction)[0]
        cloth_hit=cloth.ray_cast(inv@start,(inv.to_3x3()@direction).normalized())[0]
        cloth_world=pants.matrix_world@cloth_hit if cloth_hit else None
        if skin_hit and cloth_world:
            print('EASE',x,z,'skin',round(skin_hit.y,4),'cloth',round(cloth_world.y,4),'gap',round(skin_hit.y-cloth_world.y,4),flush=True)
