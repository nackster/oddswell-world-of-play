"""Inspect the new pattern's openings, entire midsurface, and body clearances."""
import bpy
import bmesh
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'FourPanelCotton.blend'))
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
bm=bmesh.new();bm.from_mesh(pants.data)
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in boundary)
openings=0
while boundary:
    openings+=1;pending=[boundary.pop()]
    while pending:
        v=pending.pop()
        for e in v.link_edges:
            other=e.other_vert(v)
            if e.is_boundary and other in boundary: boundary.remove(other);pending.append(other)
assert openings==3 and len(bm.verts)-len(bm.edges)+len(bm.faces)==-1
bm.free()
solid=[m for m in pants.modifiers if m.type=='SOLIDIFY']
for m in pants.modifiers:
    if m.type=='SOLIDIFY': m.show_viewport=False
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
obj=pants.evaluated_get(deps);mesh=obj.to_mesh();mesh.calc_loop_triangles()
pts=[pants.matrix_world@v.co for v in mesh.vertices]
tris=[tuple(t.vertices) for t in mesh.loop_triangles]
tree=BVHTree.FromPolygons(pts,tris,all_triangles=True)
crossings={(min(a,b),max(a,b)) for a,b in tree.overlap(tree)
           if a!=b and not set(tris[a])&set(tris[b])}
print('MID_SURFACE_CROSSINGS',len(crossings),flush=True)
clearances={}
for label in ('anatomical legs','posed pelvic fitting support'):
    body=bpy.data.objects['Character | '+label]
    support=BVHTree.FromObject(body,deps)
    inverse=body.matrix_world.inverted()
    gaps=[]
    for i in range(len(pts)):
        p=pts[i]
        if label=='anatomical legs' and not .60<p.z<.70: continue
        if label=='posed pelvic fitting support' and not .705<p.z<.885: continue
        q=inverse@p;hit,normal,_,distance=support.find_nearest(q)
        if label=='anatomical legs' and normal.z>.85: continue  # Exclude the artificial top closure.
        gaps.append(((q-hit).dot(normal),p))
    clearances[label]={'min_m':min(g[0] for g in gaps),'inside_samples':sum(g[0]<-.002 for g in gaps),
                       'samples':len(gaps),'worst_point':list(min(gaps,key=lambda g:g[0])[1])}
obj.to_mesh_clear()
for m in solid:m.show_viewport=True
bpy.context.view_layer.update()
evaluated=pants.evaluated_get(bpy.context.evaluated_depsgraph_get())
shell=evaluated.to_mesh();shell.calc_loop_triangles()
shell_points=[pants.matrix_world@v.co for v in shell.vertices]
shell_triangles=[tuple(t.vertices) for t in shell.loop_triangles]
shell_tree=BVHTree.FromPolygons(shell_points,shell_triangles,all_triangles=True)
shell_crossings={(min(a,b),max(a,b)) for a,b in shell_tree.overlap(shell_tree)
                 if a!=b and not set(shell_triangles[a])&set(shell_triangles[b])}
cross_points=[shell_points[i] for pair in shell_crossings for face in pair for i in shell_triangles[face]]
print('SHELL_OVERLAP_BOUNDS',[[min(p[a] for p in cross_points),max(p[a] for p in cross_points)] for a in range(3)] if cross_points else [],flush=True)
print('SOLIDIFY_SETTINGS',[{p.identifier:getattr(m,p.identifier) for p in m.bl_rna.properties if any(term in p.identifier for term in ('thickness','solidify_mode','offset'))} for m in solid],flush=True)
bm=bmesh.new();bm.from_mesh(shell)
assert all(e.is_manifold for e in bm.edges)
fabric_volume=bm.calc_volume(signed=True)
assert fabric_volume>0
bm.free();evaluated.to_mesh_clear()
assert len(crossings)==0 and len(shell_crossings)==0
assert all(row['min_m']>.002 for row in clearances.values())
control=bpy.data.objects[bpy.context.scene['torso_hip_flow_control']]
changed=json.loads(bpy.context.scene['torso_hip_flow_objects'])
assert control['flow']==1 and all(bpy.data.objects[name].data.shape_keys.key_blocks.get('Previous torso hip stance') for name in changed)
states=[m.show_viewport for m in pants.modifiers]
for m in pants.modifiers:m.show_viewport=False
control['flow']=0.;control.update_tag();bpy.context.view_layer.update()
evaluated=pants.evaluated_get(bpy.context.evaluated_depsgraph_get())
check=evaluated.to_mesh()
restore_error=max((v.co-p.vector).length for v,p in zip(check.vertices,pants.data.attributes['Before torso hip flow'].data))
assert restore_error<1e-6
evaluated.to_mesh_clear()
control['flow']=1.;control.update_tag()
for m,state in zip(pants.modifiers,states):m.show_viewport=state
bpy.context.view_layer.update()
assert all(pants.data.attributes.get(name) for name in ('Four panel drafted','Four panel collision fit','Four panel gravity result'))
assert pants.data.uv_layers.get('Four cut cotton panels')
report={'result':'PASS','openings':openings,'controls':len(pants.data.vertices),'faces':len(pants.data.polygons),
        'whole_midsurface_nonadjacent_overlap_pairs':len(crossings),
        'whole_thick_shell_nonadjacent_overlap_pairs':len(shell_crossings),
        'fabric_volume_m3':fabric_volume,'clearance':clearances}
report['gravity_frames']=bpy.context.scene['four_panel_shorts_gravity_frames']
report['maximum_gravity_motion_m']=bpy.context.scene['four_panel_shorts_maximum_gravity_motion_m']
report['maximum_final_clearance_adjustment_m']=bpy.context.scene['four_panel_shorts_maximum_final_clearance_adjustment_m']
report['maximum_crotch_fillet_m']=bpy.context.scene['four_panel_shorts_crotch_fillet_maximum_m']
report['native_stance_control_driven_parts']=len(changed)
report['new_pattern_inverse_stance_restore_error_m']=restore_error
report['runtime_import_ready']=False
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
inverse=pants.matrix_world.inverted()
detail_gaps={}
for detail in bpy.context.scene.objects:
    if detail.type!='CURVE' or not detail.name.startswith('Character | '): continue
    if not any(token in detail.name for token in ('inset back pocket stitch','pocket mouth topstitch','shorts leg hem')):continue
    gaps=[]
    target=pants
    if 'pocket' in detail.name:
        side='left' if detail.name.endswith('left') else 'right'
        target=bpy.data.objects['Character | sewn cotton back pocket '+side]
    attachment=BVHTree.FromObject(target,bpy.context.evaluated_depsgraph_get())
    local=target.matrix_world.inverted()
    for spline in detail.data.splines:
        for point in spline.points:
            q=local@(detail.matrix_world@Vector(point.co[:3]))
            hit,normal,_,distance=attachment.find_nearest(q)
            gaps.append(distance)
            assert distance<.003,(detail.name,distance)
    detail_gaps[detail.name]=max(gaps)
report['maximum_sewn_detail_surface_distance_m']=detail_gaps
parts=[];materials=set()
for part in bpy.context.scene.objects:
    if not part.name.startswith('Character | ') or part.hide_render or part.type not in {'MESH','CURVE'}:continue
    evaluated=part.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    parts.append({'name':part.name,'triangles':len(mesh.loop_triangles)})
    materials.update(m.name for m in part.data.materials if m)
    evaluated.to_mesh_clear()
report['visible_character_evaluated_viewport_triangles']=sum(p['triangles'] for p in parts)
report['visible_character_objects']=len(parts)
report['visible_character_materials']=len(materials)
report['largest_character_parts']=sorted(parts,key=lambda p:p['triangles'],reverse=True)[:6]
(out/'FourPanelCotton-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('FOUR_PANEL_INSPECTION',json.dumps(report),flush=True)
