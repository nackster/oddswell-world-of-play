"""Short, individually tapered scalp hair on the retained anatomical head."""
import bisect
import math
import random
import bpy
from mathutils import Vector

head=bpy.data.objects['Character | anatomical head']
evaluated=head.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh();mesh.calc_loop_triangles()

def hairline(position):
    x=abs(position.x+.75)
    front=max(0,min(1,(position.y+2.40)/.16))
    temple=max(0,min(1,(x-.055)/.040))
    return 1.685+.085*front+.025*temple+.003*math.sin(position.x*160+position.y*65)

triangles=[];areas=[];total=0.0
for tri in mesh.loop_triangles:
    p=tri.center
    if p.z<hairline(p)+.003 or tri.area<=0:continue
    triangles.append(tri);total+=tri.area;areas.append(total)
assert total>.025,'Missing usable scalp surface'
rng=random.Random(72109)
hair_count=72000
data=bpy.data.curves.new('Character | cropped scalp fibers','CURVE')
data.dimensions='3D';data.bevel_depth=.000032;data.bevel_resolution=1
for _ in range(hair_count):
    tri=triangles[bisect.bisect_left(areas,rng.random()*total)]
    u=math.sqrt(rng.random());v=rng.random()
    weights=(1-u,u*(1-v),u*v)
    position=sum((mesh.vertices[i].co*w for i,w in zip(tri.vertices,weights)),Vector())
    if position.z<hairline(position):continue
    normal=sum((mesh.vertices[i].normal*w for i,w in zip(tri.vertices,weights)),Vector()).normalized()
    flow=Vector((rng.uniform(-.16,.16),.24,.08))
    direction=(normal*.70+flow).normalized()
    length=rng.uniform(.0012,.0027)
    spline=data.splines.new('POLY');spline.points.add(2)
    for point,t in zip(spline.points,(0,.55,1)):
        point.co=(*(position+normal*.00007+direction*length*t+normal*.00010*t),1)
        point.radius=(1-t)*.95+.05
obj=bpy.data.objects.new('Character | cropped scalp fibers',data)
bpy.context.scene.collection.objects.link(obj)
obj.matrix_world=head.matrix_world.copy()
for name,color in (('brown',(.035,.022,.014)),('warm',(.060,.038,.024)),('light',(.095,.066,.044))):
    material=bpy.data.materials.new('Character | scalp fiber '+name)
    material.diffuse_color=(*color,1);material.use_nodes=True
    bs=material.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=material.diffuse_color
    bs.inputs['Roughness'].default_value=.85
    data.materials.append(material)
for spline in data.splines:
    spline.material_index=rng.choices((0,1,2),weights=(6,3,1))[0]
evaluated.to_mesh_clear()
bpy.context.scene['scalp_hair_strands']=len(data.splines)
print('ODDSWELL_SCALP_HAIR_PASS',len(data.splines),flush=True)
