"""A restrained turned cotton edge sampled from the moving cloth UVs."""
import bpy,json,array
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HipSeat.blend'));scene=bpy.context.scene;scene.frame_set(1)
source=bpy.data.objects['Character | folded cotton leg hem facings'];group=next(m.node_group for m in source.modifiers if m.type=='NODES').copy();group.name='Native turned cotton edge UV registration'
for obj in scene.objects:
    if obj.name==source.name or obj.name.startswith(('Walk surface | Character | shorts leg hem','Walk surface | Character | sewn folded hem')):obj.hide_render=True
verts=[];faces=[];uvs=[];offsets=[]
# Outer fold, lower roll and inward turn; all remain close to the cotton.
rows=[(.010,.00030),(.006,.00050),(.0001,.00030),(.0001,-.00045),(.008,-.00045)]
cols=80
for side in (0,1):
    for half in (0,1):
        base=len(verts)
        for v,offset in rows:
            for col in range(cols+1):
                u=.02+side*.48+.48*(.00001+.99998*col/cols)
                uvs.append((u,.02+half*.48+v,0));offsets.append(offset);verts.append((0,0,0))
        for row in range(len(rows)-1):
            for col in range(cols):
                a=base+row*(cols+1)+col;faces.append((a,a+1,a+cols+2,a+cols+1))
data=bpy.data.meshes.new('Turned cotton hem with inward facing');data.from_pydata(verts,[],faces);data.update()
for material in source.data.materials:data.materials.append(material)
for p in data.polygons:p.use_smooth=True
attribute=data.attributes.new(name='Sewn cloth registration UV',type='FLOAT_VECTOR',domain='POINT')
for v,p in zip(attribute.data,uvs):v.vector=p
attribute=data.attributes.new(name='Fold normal offset',type='FLOAT',domain='POINT')
for v,p in zip(attribute.data,offsets):v.value=p
for node in group.nodes:
    if node.bl_idname=='GeometryNodeInputNamedAttribute' and node.inputs['Name'].default_value.startswith('Sewn cloth registration UV'):node.inputs['Name'].default_value='Sewn cloth registration UV'
offset=group.nodes.new('GeometryNodeInputNamedAttribute');offset.data_type='FLOAT';offset.inputs['Name'].default_value='Fold normal offset'
scale=next(n for n in group.nodes if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='SCALE');group.links.new(offset.outputs['Attribute'],scale.inputs['Scale'])
obj=bpy.data.objects.new('Hip study | continuous turned cotton hems',data);scene.collection.objects.link(obj);obj.matrix_world=source.matrix_world.copy()
mod=obj.modifiers.new('Actual cloth UV folded hem','NODES');mod.node_group=group
bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Sewn UV sample valid'].data)
positions=array.array('f',[0.])*len(mesh.vertices)*3;mesh.vertices.foreach_get('co',positions);ev.to_mesh_clear();data.vertices.foreach_set('co',positions);data.update()
report=json.loads((out/'build-report.json').read_text());report['bindings'][obj.name]={'controls':len(verts),'target':'Character | shorts leg continuous tailoring','cloth_offset_m':[-.00045,.0005],'method':'Native UV-registered outer band, lower roll and inward turn; overlapping inherited hem render followers remain editable but hidden'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'HipSeat.blend'),compress=True);print('TURNED_HEM_SAVED',flush=True)
