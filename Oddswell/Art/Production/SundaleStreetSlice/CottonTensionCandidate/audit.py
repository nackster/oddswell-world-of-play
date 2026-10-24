"""Verify source preservation, cloth histories, attachment restoration and facing fit."""
import bpy,bmesh,ast,array,hashlib,json,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
source=art/'AnatomicalNecklineCandidate/AnatomicalNeckline.blend'
(out/'CottonTension-audit.json').write_text('{"result":"PENDING"}\n')
parsed=ast.parse((art/'NeckSkinUVCandidate/audit.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('values','state')],type_ignores=[]),'retained-scene-state','exec'))
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();baseline=state()
coat_name='Character | tailored slate jacket';facing_name='Character | collar-to-jacket facing'
old={n:[v.co.copy() for v in bpy.data.objects[n].data.vertices] for n in (coat_name,facing_name)}
history_names=('Tailored rest','Collision fit','Gravity result','Anatomical attachment targets')
history={n:values(bpy.data.objects[coat_name].data.attributes[n].data,'vector',3) for n in history_names}
bpy.ops.wm.open_mainfile(filepath=str(out/'CottonTension.blend'));bpy.context.view_layer.update();current=state()
assert baseline[0].keys()==current[0].keys()
changed=[n for n in baseline[0] if baseline[0][n]!=current[0][n]]
core={coat_name,facing_name};assert core.issubset(changed)
assert all(n in core or (n.startswith('Character | ') and any(s in n for s in ('yoke','raglan topstitch','front zipper tape','front welt pocket','zipper teeth'))) for n in changed)
assert baseline[1]==current[1] and baseline[2]==current[2]
scene=bpy.context.scene;coat=bpy.data.objects[coat_name];facing=bpy.data.objects[facing_name];collar=bpy.data.objects['Character | standing collar']
assert history=={n:values(coat.data.attributes[n].data,'vector',3) for n in history_names}
assert scene['post_neckline_cotton_frames']==80 and scene['post_neckline_raw_maximum_motion_m']<.20
assert max((v.vector-p).length for v,p in zip(coat.data.attributes['Before post neckline cloth'].data,old[coat_name]))==0
restore={}
for name,key_name in ((coat_name,'Original pre-settle jacket'),(facing_name,'Original pre-settle collar facing')):
    obj=bpy.data.objects[name];key=obj.data.shape_keys.key_blocks[key_name];assert key.value==0
    visibility=[(m,m.show_viewport) for m in obj.modifiers]
    for m,_ in visibility:m.show_viewport=False
    key.value=1;bpy.context.view_layer.update()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    restore[name]=max((v.co-p).length for v,p in zip(mesh.vertices,old[name]));ev.to_mesh_clear()
    assert restore[name]<1e-6
    key.value=0
    for m,visible in visibility:m.show_viewport=visible
for obj in (coat,collar):
    for modifier in obj.modifiers:
        if modifier.type=='SOLIDIFY':modifier.show_viewport=False
        if modifier.type=='SUBSURF':modifier.levels=max(modifier.levels,modifier.render_levels)
bpy.context.view_layer.update()
parsed=ast.parse((art/'AnatomicalNecklineCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='boundary_loops'],type_ignores=[]),'render-boundaries','exec'))
outer=max(boundary_loops(coat),key=lambda ps:sum(p.z for p in ps)/len(ps))
inner=min(boundary_loops(collar),key=lambda ps:sum(p.z for p in ps)/len(ps))
center=sum(inner,Vector())/len(inner)
points=[facing.matrix_world@v.co for v in facing.data.vertices]
def distance(p,ring):
    ordered=sorted(ring,key=lambda q:math.atan2(q.y-center.y,q.x-center.x))
    return min((p-a.lerp(b,max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared)))).length for a,b in zip(ordered,ordered[1:]+ordered[:1]))
rim_errors={'inner':max(distance(points[j*3],inner) for j in range(256)),'outer':max(distance(points[j*3+2],outer) for j in range(256))}
assert max(rim_errors.values())<.0005
facing.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in facing.data.loop_triangles]
tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
overlaps={(min(a,b),max(a,b)) for a,b in tree.overlap(tree) if a!=b and not set(triangles[a])&set(triangles[b])}
assert not overlaps and all(p.area>1e-8 for p in facing.data.polygons)
gaps={}
for name in ('Character | anatomical head','Character | internal torso support'):
    skin=bpy.data.objects[name]
    for m in skin.modifiers:
        if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
    bpy.context.view_layer.update();tree=BVHTree.FromObject(skin,bpy.context.evaluated_depsgraph_get());inverse=skin.matrix_world.inverted()
    distances=[]
    for p in points:
        q=inverse@p;hit,n,_,d=tree.find_nearest(q);distances.append((q-hit).dot(n))
    gaps[name]=min(distances)
assert min(gaps.values())>.0005
control=bpy.data.objects['Body flow | stance blend']
parts=[o for o in scene.objects if o.data and hasattr(o.data,'shape_keys') and o.data.shape_keys and 'Previous torso hip stance' in o.data.shape_keys.key_blocks]
assert len(parts)==244
for flow in (0,1):
    control['flow']=flow;control.update_tag();bpy.context.view_layer.update()
    assert all(abs(o.data.shape_keys.key_blocks['Previous torso hip stance'].value-(1-flow))<1e-6 for o in parts)
report={'result':'PASS','changed_geometry_objects':changed,'unchanged_geometry_objects':len(baseline[0])-len(changed),'unchanged_uv_layers':sum(len(v) for v in baseline[1].values()),'unchanged_packed_maps':len(baseline[2]),'preserved_simulation_and_attachment_attributes':list(history_names),'original_control_restore_error_m':restore,'facing_maximum_rim_distance_m':rim_errors,'facing_nonadjacent_overlap_pairs':len(overlaps),'facing_minimum_anatomical_clearance_m':gaps,'stance_driver_parts':len(parts),'new_native_cloth_frames':scene['post_neckline_cotton_frames'],'raw_maximum_control_motion_m':scene['post_neckline_raw_maximum_motion_m'],'fitted_maximum_control_motion_m':scene['post_neckline_fitted_maximum_motion_m'],'runtime_claim':False}
(out/'CottonTension-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('POST_NECKLINE_CLOTH_AUDIT_PASS',len(changed),'OBJECTS',rim_errors,gaps,flush=True)
