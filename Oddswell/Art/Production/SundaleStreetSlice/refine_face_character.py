"""Editable source-based adult facial proportions with transported brow detail."""
import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

def refine_face_character():
    scene=bpy.context.scene;head=bpy.data.objects['Character | anatomical head']
    assert not scene.get('individual_facial_form'),'Apply to the retained head baseline once'
    source=head.data.attributes.get('MakeHuman source vertex')
    assert source and len(source.data)==len(head.data.vertices)
    before=head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    before.calc_loop_triangles()
    old_points=[v.co.copy() for v in before.vertices]
    triangles=[tuple(t.vertices) for t in before.loop_triangles]
    old_surface=BVHTree.FromPolygons(old_points,triangles,all_triangles=True)
    head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    head.shape_key_add(name='Basis')
    weights={'caucasian-male-young.target':.65,'head-rectangular.target':.30,'head-fat-decr.target':.22}
    deltas={}
    for filename,weight in weights.items():
        delta={}
        for line in (ROOT/'source-assets/facial-targets'/filename).read_text(encoding='utf-8').splitlines():
            parts=line.split()
            if parts and not parts[0].startswith('#'):
                x,y,z=map(float,parts[1:4]);delta[int(parts[0])]=Vector((x,z,y))*unit
        # Macro targets also move the head when body height changes. Keep
        # the head joint fixed so this pass changes local facial proportions.
        anchor=sum((delta.get(i,Vector()) for i in jointverts['joint-head']),Vector())/len(jointverts['joint-head'])
        if anchor.length>1e-8:delta={i:delta.get(i,Vector())-anchor for i in range(len(converted))}
        deltas[filename]=delta
        shape=head.shape_key_add(name=filename.removesuffix('.target'));shape.value=weight
        for vertex,identity in zip(head.data.vertices,source.data):
            # Preserve the fitted neck below the jaw and keep the collar join.
            p=vertex.co-origin
            front=max(0,min(1,(p.y-.005)/.050))
            transition=.030+.045*(1-front)
            fade=max(0,min(1,(p.z-1.545)/transition));fade=fade*fade*(3-2*fade)
            shape.data[vertex.index].co=vertex.co+delta.get(identity.value,Vector())*fade
    asymmetry=head.shape_key_add(name='Restrained facial asymmetry');asymmetry.value=1
    oil=head.data.attributes.new(name='Facial oil distribution',type='FLOAT',domain='POINT')
    for vertex,datum in zip(head.data.vertices,oil.data):
        p=vertex.co-origin
        front=max(0,min(1,(p.y-.055)/.035))
        bridge=math.exp(-(p.x/.018)**2-((p.z-1.646)/.030)**2)*front
        corner=math.exp(-((p.x-.026)/.014)**2-((p.z-1.594)/.013)**2)*front
        asymmetry.data[vertex.index].co=vertex.co+Vector((.0007*bridge,0,.0006*corner))
        forehead=math.exp(-(p.x/.060)**2-((p.z-1.727)/.033)**2)
        nose=math.exp(-(p.x/.020)**2-((p.z-1.642)/.039)**2)
        datum.value=min(1,front*(.7*forehead+nose))
    for side in ('l','r'):
        ids=jointverts['joint-'+side+'-eye']
        translation=sum((sum((deltas[name].get(i,Vector()) for i in ids),Vector())*(weight/len(ids)) for name,weight in weights.items()),Vector())
        for name in ('eye','iris','pupil'):
            obj=bpy.data.objects['Character | '+name+' '+side]
            for vertex in obj.data.vertices:vertex.co+=translation
            if name=='eye' and 'support_center' in obj:obj['support_center']=list(Vector(obj['support_center'])+translation)
    bpy.context.view_layer.update()
    after=head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    actual=[v.co.copy() for v in after.vertices];normals=[v.normal.copy() for v in after.vertices]
    assert len(actual)==len(old_points),'Facial shape changed topology'
    for brow in (o for o in scene.objects if o.name.startswith('Character | eyebrow ')):
        for spline in brow.data.splines:
            for point in spline.points:
                position=Vector(point.co[:3]);hit,_,index,distance=old_surface.find_nearest(position)
                ids=triangles[index];a,b,c=(old_points[i] for i in ids)
                mapped=barycentric_transform(hit,a,b,c,*(actual[i] for i in ids))
                normal=barycentric_transform(hit,a,b,c,*(normals[i] for i in ids)).normalized()
                point.co=(*(mapped+normal*min(distance,.0005)),1)
    head.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    material=head.data.materials[0];nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes.get('Principled BSDF');bs.inputs['Subsurface Weight'].default_value=.55
    previous=bs.inputs['Roughness'].links[0].from_socket
    attribute=nodes.new('ShaderNodeAttribute');attribute.attribute_name='Facial oil distribution'
    zone=nodes.new('ShaderNodeMapRange');zone.inputs['To Min'].default_value=1;zone.inputs['To Max'].default_value=.67
    multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY'
    links.new(attribute.outputs['Fac'],zone.inputs['Value']);links.new(zone.outputs[0],multiply.inputs[0]);links.new(previous,multiply.inputs[1]);links.new(multiply.outputs[0],bs.inputs['Roughness'])
    scene['individual_facial_form']=True;scene['head_character_targets']=json.dumps(weights,sort_keys=True)
    print('ODDSWELL_FACIAL_FORM_PASS',weights,flush=True)

refine_face_character()
