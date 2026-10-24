"""Check the entire new jacket sheet/shell, anatomical fit and sewn attachments."""
import bpy
import bmesh
import json,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector

out=Path(__file__).resolve().parent
(out/'RaglanPattern-audit.json').write_text('{"result":"PENDING"}\n')
bpy.ops.wm.open_mainfile(filepath=str(out/'RaglanPattern.blend'))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
body=bpy.data.objects['Character | internal torso support']
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
subdivision=[(m,m.levels) for obj in (coat,body) for m in obj.modifiers if m.type=='SUBSURF']
for modifier,_ in subdivision:modifier.levels=max(modifier.levels,modifier.render_levels)
bpy.context.view_layer.update()
assert scene.get('raglan_panel_jacket') and scene['jacket_drape_frames']==60
packed=[im for im in bpy.data.images if im.source=='FILE' and im.packed_file]
assert len(packed)==31 and all(im.use_fake_user for im in packed)
assert body.hide_render and body.hide_get()
weights=[max((g.weight for g in v.groups if g.group==pin.index),default=0) for v in coat.data.vertices]
pinned_motion=max((v.co-p.vector).length for v,p,w in zip(coat.data.vertices,coat.data.attributes['Collision fit'].data,weights) if w>.95)
assert pinned_motion<1e-6,'Held neck, hem or cuffs moved'
bm=bmesh.new();bm.from_mesh(coat.data)
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
assert len(bm.verts)-len(bm.edges)+len(bm.faces)==-2
boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in boundary)
openings=0
while boundary:
    pending=[boundary.pop()];openings+=1
    while pending:
        v=pending.pop()
        for e in v.link_edges:
            other=e.other_vert(v)
            if e.is_boundary and other in boundary:boundary.remove(other);pending.append(other)
assert openings==4
bm.free()
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
solid.show_viewport=False
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
support=BVHTree.FromObject(body,deps)
inverse=body.matrix_world.inverted()
evaluated=coat.evaluated_get(deps)
mesh=evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
mesh.calc_loop_triangles()
points=[coat.matrix_world@v.co for v in mesh.vertices]
triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
surface=BVHTree.FromPolygons(points,triangles,all_triangles=True)
overlaps={(min(a,b),max(a,b)) for a,b in surface.overlap(surface)
          if a!=b and not set(triangles[a])&set(triangles[b])}
gaps=[];normal_alignment=[]
for vertex,p in zip(mesh.vertices,points):
    weight=max((g.weight for g in vertex.groups if g.group==pin.index),default=0)
    if weight>=.80:continue
    q=inverse@p;hit,normal,_,distance=support.find_nearest(q)
    gaps.append(((q-hit).dot(normal),p))
    normal_alignment.append((body.matrix_world.to_3x3()@normal).normalized().dot((coat.matrix_world.to_3x3()@vertex.normal).normalized()))
evaluated.to_mesh_clear()
print('RAGLAN_MID_SURFACE_OVERLAPS',len(overlaps),'FREE_CLEARANCE_M',min(g[0] for g in gaps),flush=True)
solid.show_viewport=True;bpy.context.view_layer.update()
evaluated=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
points=[coat.matrix_world@v.co for v in mesh.vertices]
triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
surface=BVHTree.FromPolygons(points,triangles,all_triangles=True)
shell_overlaps={(min(a,b),max(a,b)) for a,b in surface.overlap(surface)
                if a!=b and not set(triangles[a])&set(triangles[b])}
bm=bmesh.new();bm.from_mesh(mesh)
assert all(e.is_manifold for e in bm.edges)
volume=bm.calc_volume(signed=True);assert volume>0
bm.free();evaluated.to_mesh_clear()
if overlaps or shell_overlaps:
    centers=[sum((points[i] for i in set(triangles[a])|set(triangles[b])),Vector())/len(set(triangles[a])|set(triangles[b])) for a,b in shell_overlaps]
    groups=[]
    for p in centers:
        group=next((g for g in groups if any((p-q).length<.02 for q in g)),None)
        if group is None:groups.append([p])
        else:group.append(p)
    failure={'result':'FAIL','midsurface_pairs':len(overlaps),'shell_pairs':len(shell_overlaps),'minimum_free_clearance_m':min(g[0] for g in gaps),
             'shell_regions':[{'count':len(g),'center':list(sum(g,Vector())/len(g)),'min':[min(p[i] for p in g) for i in range(3)],'max':[max(p[i] for p in g) for i in range(3)]} for g in groups]}
    (out/'RaglanPattern-audit.json').write_text(json.dumps(failure,indent=2)+'\n')
    print('RAGLAN_RENDER_SHELL_FAILURE',json.dumps(failure),flush=True)
assert not overlaps,'Nonadjacent midsurface overlap'
assert not shell_overlaps,'Nonadjacent fabric-shell overlap'
assert min(g[0] for g in gaps)>.0035,'Evaluated cloth enters the anatomical fit margin'
control=bpy.data.objects['Body flow | stance blend']
parts=[obj for obj in scene.objects if obj.data and hasattr(obj.data,'shape_keys') and obj.data.shape_keys and 'Previous torso hip stance' in obj.data.shape_keys.key_blocks]
assert len(parts)==244
control['flow']=0;control.update_tag();bpy.context.view_layer.update()
assert all(abs(obj.data.shape_keys.key_blocks['Previous torso hip stance'].value-1)<1e-6 for obj in parts)
control['flow']=1;control.update_tag();bpy.context.view_layer.update()
assert all(abs(obj.data.shape_keys.key_blocks['Previous torso hip stance'].value)<1e-6 for obj in parts)
render_subdivision=[m.levels for m,_ in subdivision]
for modifier,level in subdivision:modifier.levels=level
bpy.context.view_layer.update()
part_sizes=[]
for obj in scene.objects:
    if not obj.name.startswith('Character | ') or obj.type not in ('MESH','CURVE') or obj.hide_render or obj.hide_get():continue
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles()
    part_sizes.append({'name':obj.name,'triangles':len(me.loop_triangles)});ev.to_mesh_clear()
report={'result':'PASS','controls':len(coat.data.vertices),'faces':len(coat.data.polygons),
        'openings':openings,'midsurface_nonadjacent_overlap_pairs':len(overlaps),
        'thick_shell_nonadjacent_overlap_pairs':len(shell_overlaps),'fabric_volume_m3':volume,
        'free_evaluated_points_checked':len(gaps),'minimum_free_evaluated_clearance_m':min(g[0] for g in gaps),
        'worst_free_point_world_m':list(min(gaps,key=lambda pair:pair[0])[1]),
        'gravity_frames':scene['jacket_drape_frames'],'maximum_gravity_motion_m':scene['jacket_drape_maximum_delta_m'],
        'mean_cloth_body_normal_alignment':sum(normal_alignment)/len(normal_alignment),
        'fully_pinned_motion_m':pinned_motion,'stance_driver_parts':len(parts),'packed_maps':len(packed),
        'cloth_and_support_checked_subdivision_levels':render_subdivision,
        'visible_character_evaluated_viewport_triangles':sum(p['triangles'] for p in part_sizes),
        'largest_character_parts':sorted(part_sizes,key=lambda p:p['triangles'],reverse=True)[:6]}
(out/'RaglanPattern-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('RAGLAN_COMPLETE_CLOTH_INSPECTION',json.dumps(report),flush=True)
