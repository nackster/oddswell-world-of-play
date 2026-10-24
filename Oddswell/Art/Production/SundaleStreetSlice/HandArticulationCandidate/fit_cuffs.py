"""Editable distal knit shaping around the actual wrist, retaining the sleeve join."""
import bpy,json,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HandMotion.blend'))
scene=bpy.context.scene;scene.frame_set(1);rig=bpy.data.objects['Walk study | native anatomical controls']
report={}
coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface']
edge_counts=Counter(tuple(sorted((a,b))) for p in coat.data.polygons for a,b in zip(p.vertices,(*p.vertices[1:],p.vertices[0])))
graph={}
for (a,b),count in edge_counts.items():
    if count==1:graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
pending=set(graph);loops=[]
while pending:
    current=min(pending);loop=[]
    while current not in loop:
        loop.append(current);pending.discard(current);remaining=graph[current]-set(loop)
        if not remaining:break
        current=min(remaining)
    loops.append(loop)
assert len(loops)==4
flags=[(m,m.show_viewport) for m in coat.modifiers if m.type in ['SUBSURF','SOLIDIFY']]
for m,_ in flags:m.show_viewport=False
bpy.context.view_layer.update();ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
opening_points=[[ev.matrix_world@mesh.vertices[i].co for i in loop] for loop in loops];ev.to_mesh_clear()
for m,flag in flags:m.show_viewport=flag
def cross(a,b):return a.x*b.y-a.y*b.x
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for cuff_label,side,hand_label in [('left','neg','right'),('right','pos','left')]:
    cuff=bpy.data.objects['Character | sleeve cuff '+cuff_label];hand=bpy.data.objects['Character | anatomical '+hand_label+' hand']
    assert len(cuff.data.vertices)==13*384
    deps=bpy.context.evaluated_depsgraph_get();ev=hand.evaluated_get(deps);mesh=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
    world=cuff.matrix_world.copy();inverse=world.inverted();ps=[world@v.co for v in cuff.data.vertices]
    centers=[sum(ps[k*384:(k+1)*384],Vector())/384 for k in range(13)];axis=(centers[-1]-centers[0]).normalized()
    wrist=rig.matrix_world@rig.pose.bones[side+'.palm'].head
    shape=cuff.shape_key_add(name='Knitted cuff wrist fit');shape.value=1.;maximum=0.;hits=0
    for k,center in enumerate(centers):
        influence=1-smooth(k/7)
        if influence==0:continue
        newcenter=wrist+axis*(center-wrist).dot(axis)
        delta_center=newcenter-center
        if delta_center.length>.014:delta_center*=.014/delta_center.length
        newcenter=center+delta_center
        ring=ps[k*384:(k+1)*384]
        for j,p in enumerate(ring):
            relative=p-center;axial=relative.dot(axis);radial=relative-axis*axial
            if radial.length<1e-8:continue
            direction=radial.normalized();hit=tree.ray_cast(newcenter+axis*axial,direction,.08)
            if hit[0] is None:continue
            radius=max(radial.length*.75,min(radial.length,hit[3]+.0035));scale=radius/radial.length
            target=newcenter+axis*axial+radial*scale
            q=p.lerp(target,influence);index=k*384+j;shape.data[index].co=inverse@q
            maximum=max(maximum,(q-p).length);hits+=1
    distal_maximum=maximum
    opening=min(opening_points,key=lambda loop:((sum(loop,Vector())/len(loop))-centers[-1]).length)
    joincenter=sum(opening,Vector())/len(opening);u=(ps[-384]-centers[-1]);u=(u-axis*u.dot(axis)).normalized();v=axis.cross(u).normalized()
    projected=[Vector(((p-joincenter).dot(u),(p-joincenter).dot(v))) for p in opening]
    join_delta=[]
    for j,p in enumerate(ps[-384:]):
        radial=p-centers[-1];direction=Vector((radial.dot(u),radial.dot(v))).normalized();intersections=[]
        for index,(a,b) in enumerate(zip(projected,projected[1:]+projected[:1])):
            edge=b-a;denominator=cross(direction,edge)
            if abs(denominator)<1e-10:continue
            distance=cross(a,edge)/denominator;t=cross(a,direction)/denominator
            if distance>0 and -.0001<=t<=1.0001:intersections.append((distance,index,max(0.,min(1.,t))))
        assert intersections,('Sleeve opening is not radially traceable',cuff.name,j)
        _,index,t=min(intersections);q=opening[index].lerp(opening[(index+1)%len(opening)],t)
        q+=(u*direction.x+v*direction.y)*.0007
        join_delta.append(q-p)
    attach=cuff.vertex_groups.new(name='Sewn sleeve attachment')
    for k in range(13):
        influence=smooth((k-5)/7)
        for j in range(384):
            index=k*384+j
            if influence>0:
                attach.add([index],influence,'REPLACE');shape.data[index].co+=inverse.to_3x3()@(join_delta[j]*influence)
                maximum=max(maximum,(world@shape.data[index].co-ps[index]).length)
    for bone in rig.data.bones:
        if bone.name not in cuff.vertex_groups:cuff.vertex_groups.new(name=bone.name)
    transfer=cuff.modifiers.new('Shared sleeve skin weights','DATA_TRANSFER');transfer.object=coat;transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'}
    transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME';cuff.modifiers.move(len(cuff.modifiers)-1,0)
    mod_flags=[(m,m.show_viewport) for m in cuff.modifiers if m!=transfer]
    for m,_ in mod_flags:m.show_viewport=False
    bpy.context.view_layer.update();ev=cuff.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();names={g.index:g.name for g in cuff.vertex_groups}
    records=[{names[g.group]:g.weight for g in vertex.groups if names[g.group] in rig.data.bones} for vertex in mesh.vertices];ev.to_mesh_clear()
    ids=list(range(len(records)))
    for group in cuff.vertex_groups:
        if group.name in rig.data.bones:group.remove(ids)
    for i,weights in enumerate(records):
        total=sum(weights.values());assert total>.99,('Sleeve weight transfer failed',cuff.name,i,total)
        influence=smooth((i//384-5)/7)
        blended={name:w/total*influence for name,w in weights.items()};blended[side+'.forearm']=blended.get(side+'.forearm',0)+1-influence
        for name,w in blended.items():
            if w>1e-7:cuff.vertex_groups[name].add([i],w,'REPLACE')
    cuff.modifiers.remove(transfer)
    for m,flag in mod_flags:m.show_viewport=flag
    cuff.parent=None;cuff.parent_type='OBJECT';cuff.parent_bone='';cuff.matrix_world=world;cuff.parent=rig;cuff.matrix_world=world
    mod=cuff.modifiers.new('Shared sleeve armature deformation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;cuff.modifiers.move(len(cuff.modifiers)-1,0)
    distal_bound=.014+.25*max((p-centers[i//384]).length for i,p in enumerate(ps))+1e-5
    assert distal_maximum<=distal_bound and maximum<.045 and hits>384,('Unbounded or incomplete cuff fit',cuff.name,distal_maximum,maximum,hits)
    report[cuff.name]={'maximum_control_delta_m':maximum,'maximum_distal_control_delta_m':distal_maximum,'ray_fitted_controls':hits,'jacket_boundary_controls':len(opening),'upper_join_weights_from':coat.name,'binding':'Shared native armature; forearm at wrist blended into nearest-polygon jacket weights at sleeve join.','maximum_distal_radius_reduction_fraction':.25,'distal_skin_offset_m':.0035,'upper_join_offset_m':.0007}
    print('CUFF_FIT',cuff.name,maximum,hits,flush=True)
(out/'cuff-report.json').write_text(json.dumps(report,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'HandMotion.blend'),compress=True)
print('CUFF_FIT_SAVED',flush=True)
