"""Register sewn details to fixed UV locations on the actual moving cloth."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HipSeat.blend'));scene=bpy.context.scene;scene.frame_set(1)
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];solid=next(m for m in pants.modifiers if m.type=='SOLIDIFY');solid.show_viewport=False
midsurface=pants.copy();midsurface.data=pants.data;midsurface.name='Hip study | registered cloth midsurface';scene.collection.objects.link(midsurface)
for mod in list(midsurface.modifiers):
    if mod.type=='SOLIDIFY':midsurface.modifiers.remove(mod)
midsurface.hide_render=True;midsurface.hide_set(True)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=pants.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps);mesh.calc_loop_triangles()
triangles=list(mesh.loop_triangles);points=[ev.matrix_world@v.co for v in mesh.vertices];tree=BVHTree.FromPolygons(points,[tuple(t.vertices) for t in triangles],all_triangles=True);uv=mesh.uv_layers['Four cut cotton panels']
report=json.loads((out/'build-report.json').read_text())
for name,record in report['bindings'].items():
    if record['target']!=pants.name:continue
    obj=bpy.data.objects[name];pocket='sewn cotton back pocket' in name
    attribute=obj.data.attributes.new(name='Sewn cloth registration UV',type='FLOAT_VECTOR',domain='POINT')
    for v,value in zip(obj.data.vertices,attribute.data):
        p=obj.matrix_world@v.co;hit,normal,idx,distance=tree.find_nearest(p);tri=triangles[idx]
        values=[Vector((*uv.data[i].uv,0)) for i in tri.loops]
        q=barycentric_transform(hit,*(points[i] for i in tri.vertices),*values)
        center=sum(values,Vector())/3;value.vector=q.lerp(center,.01)
    for m in list(obj.modifiers):
        if m.type in ('ARMATURE','SHRINKWRAP','SURFACE_DEFORM') or (m.type=='NODES' and m.name.startswith('Sewn actual cloth UV registration')):obj.modifiers.remove(m)
    group=bpy.data.node_groups.new('Sewn UV registration | '+name,'GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes=group.nodes;links=group.links;inp=nodes.new('NodeGroupInput');output=nodes.new('NodeGroupOutput')
    source=nodes.new('GeometryNodeObjectInfo');source.transform_space='RELATIVE';source.inputs['Object'].default_value=midsurface
    source_uv=nodes.new('GeometryNodeInputNamedAttribute');source_uv.data_type='FLOAT_VECTOR';source_uv.inputs['Name'].default_value='Four cut cotton panels'
    registered=nodes.new('GeometryNodeInputNamedAttribute');registered.data_type='FLOAT_VECTOR';registered.inputs['Name'].default_value=attribute.name
    position=nodes.new('GeometryNodeInputPosition');normal=nodes.new('GeometryNodeInputNormal')
    samples=[]
    for field in (position,normal):
        sample=nodes.new('GeometryNodeSampleUVSurface');sample.data_type='FLOAT_VECTOR'
        links.new(source.outputs['Geometry'],sample.inputs['Mesh']);links.new(field.outputs[0],sample.inputs['Value']);links.new(source_uv.outputs['Attribute'],sample.inputs['UV Map']);links.new(registered.outputs['Attribute'],sample.inputs['Sample UV']);samples.append(sample)
    offset=nodes.new('ShaderNodeVectorMath');offset.operation='SCALE';offset.inputs['Scale'].default_value=.0009 if pocket else .00045;links.new(samples[1].outputs['Value'],offset.inputs[0])
    setpos=nodes.new('GeometryNodeSetPosition');links.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);links.new(samples[0].outputs['Value'],setpos.inputs['Position']);links.new(offset.outputs['Vector'],setpos.inputs['Offset']);links.new(samples[0].outputs['Is Valid'],setpos.inputs['Selection'])
    valid=nodes.new('GeometryNodeStoreNamedAttribute');valid.data_type='BOOLEAN';valid.domain='POINT';valid.inputs['Name'].default_value='Sewn UV sample valid';links.new(setpos.outputs['Geometry'],valid.inputs['Geometry']);links.new(samples[0].outputs['Is Valid'],valid.inputs['Value']);links.new(valid.outputs['Geometry'],output.inputs['Geometry'])
    mod=obj.modifiers.new('Sewn actual cloth UV registration','NODES');mod.node_group=group;obj.modifiers.move(len(obj.modifiers)-1,0)
    record['method']='Native Geometry Nodes sample the moving garment at fixed rest-registered cloth UVs, with normal offset';record['cloth_offset_m']=.0009 if pocket else .00045
ev.to_mesh_clear();solid.show_viewport=True
for name,record in report['bindings'].items():
    if record['target']!=pants.name:continue
    bpy.context.view_layer.update();obj=bpy.data.objects[name];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    valid=mesh.attributes['Sewn UV sample valid']
    if not all(v.value for v in valid.data):
        attrs=[a for a in obj.data.attributes if a.name.startswith('Sewn cloth registration UV')]
        (out/'invalid-uv.json').write_text(json.dumps({'object':name,'attributes':{a.name:[{'index':i,'uv':list(a.data[i].vector)} for i,v in enumerate(valid.data) if not v.value and i<len(a.data)] for a in attrs},'target_modifiers':[(m.type,getattr(m,'levels',None),getattr(m,'render_levels',None)) for m in midsurface.modifiers]},indent=2))
    assert all(v.value for v in valid.data),('Rest cloth UV sample invalid',name,sum(not v.value for v in valid.data),len(valid.data));ev.to_mesh_clear()
for group in list(bpy.data.node_groups):
    if group.name.startswith('Sewn UV registration | ') and group.users==0:bpy.data.node_groups.remove(group)
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'HipSeat.blend'),compress=True);print('SEWN_UV_SAVED',flush=True)
