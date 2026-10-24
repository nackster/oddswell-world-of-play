"""Molded foxing and outsole lines fitted to the posed canvas soles."""
import bpy
from mathutils import Vector

upper_line=bpy.data.materials.new('Character | warm rubber foxing edge')
upper_line.diffuse_color=(.51,.49,.44,1)
upper_line.use_nodes=True
upper_line.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=upper_line.diffuse_color
upper_line.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
lower_line=upper_line.copy();lower_line.name='Character | recessed outsole groove'
lower_line.diffuse_color=(.39,.38,.35,1)
lower_line.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=lower_line.diffuse_color
heel_canvas=bpy.data.materials['Character | oat canvas'].copy()
heel_canvas.name='Character | reinforced canvas heel'
heel_canvas.diffuse_color=(.43,.40,.35,1)
for node in heel_canvas.node_tree.nodes:
    if node.type=='MIX_RGB' and node.blend_type=='MULTIPLY':
        node.inputs[1].default_value=heel_canvas.diffuse_color

for side in ('left','right'):
    sole=bpy.data.objects['Character | sneaker sole '+side]
    upper=bpy.data.objects['Character | canvas sneaker '+side]
    heel_limit=min(v.co.y for v in upper.data.vertices)+.062
    upper.data.materials.append(heel_canvas)
    for face in upper.data.polygons:
        if face.material_index==0 and face.center.y<heel_limit:
            face.material_index=len(upper.data.materials)-1
    assert len(sole.data.vertices)%68==0
    count=len(sole.data.vertices)//68
    def perimeter(right,left):
        points=[sole.data.vertices[68*k+right].co.copy() for k in range(count)]
        a,b=points[-1],sole.data.vertices[68*(count-1)+left].co
        points.extend(a.lerp(b,j/12) for j in range(1,13))
        points.extend(sole.data.vertices[68*k+left].co.copy() for k in range(count-2,-1,-1))
        a,b=points[-1],points[0]
        points.extend(a.lerp(b,j/12) for j in range(1,12))
        return points
    for label,indices,material,radius in (
        ('foxing edge',(0,33),upper_line,.00032),
        ('outsole groove',(67,34),lower_line,.00022),
    ):
        path=perimeter(*indices)
        data=bpy.data.curves.new('Character | '+label+' '+side,'CURVE')
        data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
        spline=data.splines.new('POLY');spline.points.add(len(path)-1);spline.use_cyclic_u=True
        for point,position in zip(spline.points,path):point.co=(*position,1)
        obj=bpy.data.objects.new('Character | '+label+' '+side,data)
        bpy.context.scene.collection.objects.link(obj)
        obj.matrix_world=sole.matrix_world.copy()
        data.materials.append(material)
bpy.context.scene['molded_sole_details']=True
