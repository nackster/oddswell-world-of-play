"""Verify continuous skirt UVs and exact retained scene geometry and source maps."""
import bpy,json,hashlib,array
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/ShoulderEaseCandidate/ShoulderEase.blend'
(out/'NeckSkinUV-audit.json').write_text('{"result":"PENDING"}\n')
def values(collection,field,width,kind='f'):
    data=array.array(kind,[0])* (len(collection)*width);collection.foreach_get(field,data);return data.tobytes()
def state():
    geometry={};uvs={};maps={}
    for obj in bpy.context.scene.objects:
        if obj.type not in ('MESH','CURVE'):continue
        h=hashlib.sha256();h.update(array.array('f',(x for row in obj.matrix_world for x in row)).tobytes())
        if obj.type=='MESH':
            h.update(values(obj.data.vertices,'co',3));h.update(values(obj.data.loops,'vertex_index',1,'i'))
            h.update(values(obj.data.polygons,'loop_total',1,'i'))
            uvs[obj.name]={layer.name:hashlib.sha256(values(layer.data,'uv',2)).hexdigest() for layer in obj.data.uv_layers}
        else:
            for spline in obj.data.splines:
                h.update(spline.type.encode());h.update(values(spline.points,'co',4))
                if spline.bezier_points:
                    for field in ('co','handle_left','handle_right'):h.update(values(spline.bezier_points,field,3))
        if obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                h.update(key.name.encode());h.update(array.array('f',[key.value]).tobytes());h.update(values(key.data,'co',3))
        geometry[obj.name]=h.hexdigest()
    for image in bpy.data.images:
        if image.source=='FILE':
            assert image.packed_file and image.use_fake_user
            maps[image.name]=hashlib.sha256(image.packed_file.data).hexdigest()
    return geometry,uvs,maps
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
baseline=state();old_head=bpy.data.objects['Character | anatomical head']
old_uv=[p.uv.copy() for p in old_head.data.uv_layers['MakeHuman source UV'].data]
bpy.ops.wm.open_mainfile(filepath=str(out/'NeckSkinUV.blend'));bpy.context.view_layer.update()
current=state();assert baseline[0]==current[0],'Scene geometry, transforms or shape keys changed'
assert baseline[2]==current[2] and len(current[2])==31,'Source images changed'
for obj,layers in baseline[1].items():
    for name,digest in layers.items():assert current[1][obj][name]==digest,'Original source UV changed'
head=bpy.data.objects['Character | anatomical head'];original=head.data.uv_layers['MakeHuman source UV'];uv=head.data.uv_layers['Continuous neck skin UV']
assert uv.active_render and bpy.context.scene.get('continuous_neck_texture_map')
node=head.data.materials[0].node_tree.nodes['Continuous lower neck atlas']
assert node.uv_map==uv.name
link=head.data.materials[0].node_tree.nodes['CC0 MakeHuman skin'].inputs['Vector'].links[0]
assert link.from_node==node
users=[o.name for o in bpy.context.scene.objects if o.type=='MESH' and head.data.materials[0] in list(o.data.materials)]
assert users==[head.name],'Shared material needs a separate mapping decision'
mods=[(m,m.show_viewport) for m in head.modifiers]
for m,_ in mods:m.show_viewport=False
bpy.context.view_layer.update();ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
points=[head.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
def area(layer,face):
    ps=[layer.data[i].uv for i in face.loop_indices]
    return abs(sum(a.x*b.y-a.y*b.x for a,b in zip(ps,ps[1:]+ps[:1])))*.5
strips=[face for face in head.data.polygons if max(points[i].z for i in face.vertices)-min(points[i].z for i in face.vertices)>.045 and max(points[i].z for i in face.vertices)<1.51]
assert len(strips)==50
old_areas=[area(original,f) for f in strips];new_areas=[area(uv,f) for f in strips]
assert max(old_areas)<1e-8 and min(new_areas)>1e-6,'Skirt still has collapsed texture area'
upper=[(uv.data[i].uv-original.data[i].uv).length for i,loop in enumerate(head.data.loops) if points[loop.vertex_index].z>=1.5007]
assert max(upper)==0,'Upper neck or face control UV changed'

triangle_areas=[];bottom_groups={}
for face in strips:
    ls=list(face.loop_indices);ps=[uv.data[i].uv for i in ls]
    signed=[(a.x*b.y-a.y*b.x)*.5 for j in range(1,len(ps)-1) for a,b in [(ps[j]-ps[0],ps[j+1]-ps[0])]]
    assert min(abs(v) for v in signed)>1e-8 and all(v*signed[0]>0 for v in signed),'Folded neck UV face'
    triangle_areas.extend(abs(v) for v in signed)
    for i in ls:
        vertex=head.data.loops[i].vertex_index
        if points[vertex].z<1.48:
            old=original.data[i].uv;bottom_groups.setdefault((vertex,old.x,old.y),[]).append(uv.data[i].uv.copy())
continuity=max((a-b).length for group in bottom_groups.values() for a in group for b in group)
assert continuity<1e-6,'Discontinuous repaired skirt UV edge'

for m,visible in mods:m.show_viewport=visible
report={'result':'PASS','unchanged_geometry_objects':len(current[0]),'unchanged_packed_source_maps':len(current[2]),'original_uv_layers_preserved':sum(len(v) for v in baseline[1].values()),'repaired_skirt_faces':len(strips),'maximum_old_strip_uv_area':max(old_areas),'minimum_new_strip_uv_area':min(new_areas),'upper_neck_face_uv_controls_checked':len(upper),'maximum_upper_uv_change':max(upper),'face_skin_material_users':users,'source_scene_sha256':'9A6BB3CA8D257CD7E130D0CDDC460264D7B645D4669E4D68416F7CA35E80730F','runtime_claim':False}
report.update(minimum_strip_uv_triangle_area=min(triangle_areas),maximum_bottom_uv_edge_discontinuity=continuity)
(out/'NeckSkinUV-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('NECK_UV_AUDIT',json.dumps(report),flush=True)
