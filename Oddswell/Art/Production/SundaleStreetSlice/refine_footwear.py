"""Replace raised construction wires with short canvas stitch runs."""
import bpy
from mathutils import Vector

canvas=bpy.data.materials['Character | oat canvas']
cap=canvas.copy();cap.name='Character | warmer canvas toe panels'
cap.diffuse_color=(.45,.42,.36,1)
for node in cap.node_tree.nodes:
    if node.type=='MIX_RGB' and node.blend_type=='MULTIPLY':
        node.inputs[1].default_value=cap.diffuse_color
thread=bpy.data.materials['Character | matching cotton topstitch'].copy()
thread.name='Character | fine warm shoe thread'
thread.diffuse_color=(.28,.26,.22,1)
thread.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=thread.diffuse_color

def stitch_seam(obj):
    old=obj.data
    path=[Vector(point.co[:3]) for point in old.splines[0].points]
    distances=[0.0]
    for a,b in zip(path,path[1:]):distances.append(distances[-1]+(b-a).length)
    def at(distance):
        for i in range(len(path)-1):
            if distance<=distances[i+1]:
                t=(distance-distances[i])/max(1e-9,distances[i+1]-distances[i])
                return path[i].lerp(path[i+1],t)
        return path[-1]
    data=bpy.data.curves.new(old.name+' fine stitch','CURVE')
    data.dimensions='3D';data.bevel_depth=.00025;data.bevel_resolution=2
    data.materials.append(thread)
    pitch=.0042
    count=max(1,int(distances[-1]/pitch))
    for i in range(count):
        start=(i+.12)*distances[-1]/count
        end=min(distances[-1],start+.0022)
        spline=data.splines.new('POLY');spline.points.add(1)
        for point,position in zip(spline.points,(at(start),at(end))):point.co=(*position,1)
    obj.data=data
    if not old.users:bpy.data.curves.remove(old)

for side in ('left','right'):
    seam=bpy.data.objects['Character | shoe lace toe cap seam '+side]
    threshold=sum(p.co.y for p in seam.data.splines[0].points)/len(seam.data.splines[0].points)
    upper=bpy.data.objects['Character | canvas sneaker '+side]
    upper.data.materials.append(cap)
    for face in upper.data.polygons:
        if face.center.y>threshold:face.material_index=len(upper.data.materials)-1
for obj in bpy.context.scene.objects:
    if obj.type=='CURVE' and obj.name.startswith('Character | shoe lace ') and any(label in obj.name for label in ('toe cap seam','quarter seam','heel seam')):
        stitch_seam(obj)
bpy.context.scene['fine_footwear_stitches']=True
