"""Inspect the reshaped collar at render subdivision and its restored stand."""
import bpy,bmesh,json,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent
(out/'NeckCollar-audit.json').write_text('{"result":"PENDING"}\n')
bpy.ops.wm.open_mainfile(filepath=str(out/'NeckCollar.blend'))
scene=bpy.context.scene;collar=bpy.data.objects['Character | standing collar'];head=bpy.data.objects['Character | anatomical head']
bm=bmesh.new();bm.from_mesh(collar.data)
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
assert len(bm.verts)-len(bm.edges)+len(bm.faces)==0
bm.free()
for obj in (collar,head):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
solid=next(m for m in collar.modifiers if m.type=='SOLIDIFY')
solid.show_viewport=False;bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();support=BVHTree.FromObject(head,deps);inverse=head.matrix_world.inverted()
def surface_checks():
    ev=collar.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
    points=[collar.matrix_world@v.co for v in mesh.vertices];tri=[tuple(t.vertices) for t in mesh.loop_triangles]
    tree=BVHTree.FromPolygons(points,tri,all_triangles=True)
    crossing={(min(a,b),max(a,b)) for a,b in tree.overlap(tree) if a!=b and not set(tri[a])&set(tri[b])}
    gaps=[]
    for p in points:
        if p.z<1.461:continue
        q=inverse@p;hit,normal,_,distance=support.find_nearest(q)
        if abs(normal.z)<.65:gaps.append(((q-hit).dot(normal),p))
    edges=Counter(tuple(sorted((ids[i],ids[(i+1)%len(ids)]))) for face in mesh.polygons for ids in (tuple(face.vertices),) for i in range(len(ids)))
    manifold=all(count==2 for count in edges.values())
    origin=sum(points,Vector())/len(points)
    volume=math.fsum((points[a]-origin).dot((points[b]-origin).cross(points[c]-origin)) for a,b,c in tri)/6
    regions=[]
    if crossing:
        centers=[sum((points[i] for i in set(tri[a])|set(tri[b])),Vector())/len(set(tri[a])|set(tri[b])) for a,b in crossing]
        regions=[min(p[i] for p in centers) for i in range(3)]+[max(p[i] for p in centers) for i in range(3)]
    ev.to_mesh_clear()
    return {'overlap_pairs':len(crossing),'checked_skin_points':len(gaps),'minimum_skin_clearance_m':min(g[0] for g in gaps),'worst_world_point':list(min(gaps,key=lambda pair:pair[0])[1]),'fabric_volume_m3':volume if manifold else None,'closed_manifold':manifold,'overlap_bounds':regions}
mid=surface_checks()
solid.show_viewport=True;bpy.context.view_layer.update()
shell=surface_checks()
report={'result':'INSPECTION','midsurface':mid,'shell':shell,'old_mean_height_m':scene['collar_original_mean_height_m'],'new_mean_height_m':scene['collar_new_mean_height_m'],'fixed_bottom_error_m':scene['collar_fixed_bottom_error_m']}
assert mid['overlap_pairs']==0 and shell['overlap_pairs']==0
assert mid['minimum_skin_clearance_m']>.003 and shell['minimum_skin_clearance_m']>.0015
assert shell['closed_manifold'] and shell['fabric_volume_m3']>0 and report['fixed_bottom_error_m']==0
solid.show_viewport=False
mods=[(m,m.show_viewport) for m in collar.modifiers]
for m,_ in mods:m.show_viewport=False
collar.data.shape_keys.key_blocks['Original tall collar'].value=1
bpy.context.view_layer.update()
ev=collar.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
restore=max((v.co-p.vector).length for v,p in zip(mesh.vertices,collar.data.attributes['Before lower fitted collar'].data))
ev.to_mesh_clear();assert restore<1e-6
collar.data.shape_keys.key_blocks['Original tall collar'].value=0
for m,visible in mods:m.show_viewport=visible
head_modifiers=[(m,m.show_viewport) for m in head.modifiers]
for m,_ in head_modifiers:m.show_viewport=False
bpy.context.view_layer.update()
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
baseline=head.data.attributes['Before lower neck continuation'].data
face_error=max((v.co-p.vector).length for v,p in zip(mesh.vertices,baseline) if (head.matrix_world@p.vector).z>=1.499)
ev.to_mesh_clear();assert face_error<1e-6
head.data.shape_keys.key_blocks['Continuous lower neck'].value=0;bpy.context.view_layer.update()
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
neck_restore=max((v.co-p.vector).length for v,p in zip(mesh.vertices,baseline));ev.to_mesh_clear();assert neck_restore<1e-6
head.data.shape_keys.key_blocks['Continuous lower neck'].value=1
for m,visible in head_modifiers:m.show_viewport=visible
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();skin=BVHTree.FromObject(head,deps)
ev=head.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
points=[head.matrix_world@v.co for v in mesh.vertices];tri=[tuple(t.vertices) for t in mesh.loop_triangles]
tree=BVHTree.FromPolygons(points,tri,all_triangles=True)
neck_crossing={(min(a,b),max(a,b)) for a,b in tree.overlap(tree) if a!=b and not set(tri[a])&set(tri[b]) and any(points[i].z<1.51 for i in (*tri[a],*tri[b]))}
edges=Counter(tuple(sorted((ids[i],ids[(i+1)%len(ids)]))) for face in mesh.polygons for ids in (tuple(face.vertices),) for i in range(len(ids)))
assert all(count==2 for count in edges.values()) and not neck_crossing,'Broken continuous neck surface'
ev.to_mesh_clear()
coat=bpy.data.objects['Character | tailored slate jacket']
for m in coat.modifiers:
    if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
shirt_gaps=[]
for vertex in mesh.vertices:
    p=coat.matrix_world@vertex.co
    if not 1.435<p.z<1.50:continue
    q=inverse@p;hit,normal,_,distance=skin.find_nearest(q)
    shirt_gaps.append((q-hit).dot(normal))
ev.to_mesh_clear();assert min(shirt_gaps)>.0005,'Shirt fabric crosses extended neck'
report.update(result='PASS',original_collar_restore_error_m=restore,original_neck_restore_error_m=neck_restore,unchanged_upper_face_control_error_m=face_error,neck_extension_m=scene['lower_neck_maximum_extension_m'])
report.update(extended_neck_overlap_pairs=len(neck_crossing),shirt_neck_shell_points_checked=len(shirt_gaps),minimum_shirt_neck_shell_clearance_m=min(shirt_gaps))
(out/'NeckCollar-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('COLLAR_WHOLE_SURFACE',json.dumps(report),flush=True)
