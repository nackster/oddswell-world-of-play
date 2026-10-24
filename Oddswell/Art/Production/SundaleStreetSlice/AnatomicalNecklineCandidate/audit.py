"""Check the collar-facing seam, original controls and unchanged source scene."""
import bpy,bmesh,ast,array,hashlib,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
source=art/'NeckSkinUVCandidate/NeckSkinUV.blend'
(out/'AnatomicalNeckline-audit.json').write_text('{"result":"PENDING"}\n')
parsed=ast.parse((art/'NeckSkinUVCandidate/audit.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('values','state')],type_ignores=[]),'retained-scene-state','exec'))
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();baseline=state()
name='Character | collar-to-jacket facing'
old=[v.co.copy() for v in bpy.data.objects[name].data.vertices]
original_controls={n:[v.co.copy() for v in bpy.data.objects[n].data.vertices] for n in ('Character | tailored slate jacket','Character | standing collar')}
bpy.ops.wm.open_mainfile(filepath=str(out/'AnatomicalNeckline.blend'));bpy.context.view_layer.update();current=state()
changed=[n for n in baseline[0] if baseline[0][n]!=current[0].get(n)]
assert baseline[0].keys()==current[0].keys()
core={name,'Character | tailored slate jacket','Character | standing collar'}
assert core.issubset(changed)
assert all(n in core or (n.startswith('Character | ') and any(s in n for s in ('yoke','raglan topstitch','front zipper tape','front welt pocket','zipper teeth','zipper slider','zipper pull loop'))) for n in changed)
assert baseline[1]==current[1] and baseline[2]==current[2]
scene=bpy.context.scene;obj=bpy.data.objects[name];coat=bpy.data.objects['Character | tailored slate jacket'];collar=bpy.data.objects['Character | standing collar']
assert scene.get('sewn_collar_facing') and len(obj.data.vertices)==768 and len(obj.data.polygons)==512
bm=bmesh.new();bm.from_mesh(obj.data)
assert len(bm.verts)-len(bm.edges)+len(bm.faces)==0
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
assert sum(e.is_boundary for e in bm.edges)==512
bm.free()
points=[obj.matrix_world@v.co for v in obj.data.vertices];obj.data.calc_loop_triangles()
triangles=[tuple(t.vertices) for t in obj.data.loop_triangles]
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
overlaps={(min(a,b),max(a,b)) for a,b in tree.overlap(tree) if a!=b and not set(triangles[a])&set(triangles[b])}
assert not overlaps and all(face.area>1e-8 for face in obj.data.polygons)
parsed=ast.parse((out/'build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='boundary_loops'],type_ignores=[]),'current-boundaries','exec'))
# boundary_loops uses the render-resolution evaluated midsurface.
from collections import Counter
for parent in (coat,collar):
    for m in parent.modifiers:
        if m.type=='SOLIDIFY':m.show_viewport=False
        if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
outer=max(boundary_loops(coat),key=lambda ps:sum(p.z for p in ps)/len(ps))
inner=min(boundary_loops(collar),key=lambda ps:sum(p.z for p in ps)/len(ps))
center=sum(inner,Vector())/len(inner)
def rim_distance(p,ring):
    ordered=sorted(ring,key=lambda q:math.atan2(q.y-center.y,q.x-center.x))
    return min((p-a.lerp(b,max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared)))).length for a,b in zip(ordered,ordered[1:]+ordered[:1]))
inner_errors=[rim_distance(points[j*3],inner) for j in range(256)]
outer_errors=[rim_distance(points[j*3+2],outer) for j in range(256)]
old_outer_errors=[rim_distance(obj.matrix_world@old[j*3+2],outer) for j in range(256)]
assert max(inner_errors)<.0005 and max(outer_errors)<.0005
assert max(old_outer_errors)>.008 and max(outer_errors)<max(old_outer_errors)*.1
gaps={}
for skin_name in ('Character | anatomical head','Character | internal torso support'):
    skin=bpy.data.objects[skin_name]
    for m in skin.modifiers:
        if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
    bpy.context.view_layer.update();surface=BVHTree.FromObject(skin,bpy.context.evaluated_depsgraph_get());inverse=skin.matrix_world.inverted()
    distances=[]
    for p in points:
        q=inverse@p;hit,n,_,distance=surface.find_nearest(q);distances.append(((q-hit).dot(n),list(p),list(skin.matrix_world@hit),list(n)))
    gaps[skin_name]=min(d[0] for d in distances)
    print('FACING_SUPPORT_WORST',skin_name,json.dumps(min(distances,key=lambda d:d[0])),flush=True)
assert min(gaps.values())>.0005,'Facing enters skin support'
obj.data.shape_keys.key_blocks['Original floating collar facing'].value=1;bpy.context.view_layer.update()
ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
restore=max((v.co-p).length for v,p in zip(me.vertices,old));ev.to_mesh_clear();assert restore<1e-6
obj.data.shape_keys.key_blocks['Original floating collar facing'].value=0
attachment_restore={}
for part_name,key_name in (('Character | tailored slate jacket','Original low jacket neckline'),('Character | standing collar','Original low collar attachment')):
    parent=bpy.data.objects[part_name];key=parent.data.shape_keys.key_blocks[key_name]
    assert key.value==0
    visibility=[(m,m.show_viewport) for m in parent.modifiers]
    for m,_ in visibility:m.show_viewport=False
    key.value=1;bpy.context.view_layer.update()
    ev=parent.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    error=max((v.co-p).length for v,p in zip(mesh.vertices,original_controls[part_name]));ev.to_mesh_clear()
    assert error<1e-6
    attachment_restore[part_name]=error;key.value=0
    for m,visible in visibility:m.show_viewport=visible
control=bpy.data.objects['Body flow | stance blend']
parts=[o for o in scene.objects if o.data and hasattr(o.data,'shape_keys') and o.data.shape_keys and 'Previous torso hip stance' in o.data.shape_keys.key_blocks]
assert len(parts)==244
for flow in (0,1):
    control['flow']=flow;control.update_tag();bpy.context.view_layer.update()
    assert all(abs(o.data.shape_keys.key_blocks['Previous torso hip stance'].value-(1-flow))<1e-6 for o in parts)
report={'result':'PASS','changed_geometry_objects':changed,'unchanged_geometry_objects':len(baseline[0])-len(changed),'unchanged_packed_source_maps':len(baseline[2]),'unchanged_uv_layers':sum(len(v) for v in baseline[1].values()),'controls':len(points),'faces':len(obj.data.polygons),'nonadjacent_overlap_pairs':len(overlaps),'maximum_inner_rim_distance_m':max(inner_errors),'maximum_outer_rim_distance_m':max(outer_errors),'maximum_source_outer_rim_distance_m':max(old_outer_errors),'minimum_support_clearance_m':gaps,'original_facing_restore_error_m':restore,'stance_driver_parts':len(parts),'maximum_control_motion_m':scene['collar_facing_maximum_motion_m'],'runtime_claim':False}
report.update(original_attachment_restore_error_m=attachment_restore,anatomical_neckline_height_m=scene['anatomical_neckline_height_m'],jacket_neckline_maximum_attachment_motion_m=scene['jacket_neckline_maximum_attachment_motion_m'],collar_attachment_maximum_motion_m=scene['collar_fixed_bottom_error_m'])
(out/'AnatomicalNeckline-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('COLLAR_JOIN_AUDIT',json.dumps(report),flush=True)
