"""Fit the coupled jacket and knit neckline over the retained anatomy."""
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
body=bpy.data.objects['Character | internal torso support']
body_levels=[(m,m.levels) for m in body.modifiers if m.type=='SUBSURF']
for m,_ in body_levels:m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
support=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());body_inverse=body.matrix_world.inverted()
head=bpy.data.objects['Character | anatomical head'];skin=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get());head_inverse=head.matrix_world.inverted()
def clear_body(p,margin):
    q=body_inverse@p;hit,n,_,distance=support.find_nearest(q);gap=(q-hit).dot(n)
    return p+body.matrix_world.to_3x3()@(n*max(0,margin-gap))
collar_before=[collar.matrix_world@v.co for v in collar.data.vertices]
collar_original=collar.data.attributes.new('Before anatomical collar attachment','FLOAT_VECTOR','POINT')
for value,p in zip(collar_original.data,collar_before):value.vector=collar.matrix_world.inverted()@p
head_center=Vector((-.6873,-2.3287,0))
ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());body_mesh=ev.to_mesh()
base_height=max((body.matrix_world@v.co).z for v in body_mesh.vertices)+.0045
ev.to_mesh_clear()
def neck_at(theta,z,offset):
    radial=Vector((math.cos(theta),math.sin(theta),0));start=Vector((head_center.x,head_center.y,z))
    hit,n,_,distance=skin.ray_cast(head_inverse@start,(head_inverse.to_3x3()@radial).normalized())
    assert hit is not None,'New collar ring does not meet anatomical neck'
    return head.matrix_world@hit+radial*offset
bottom=[]
top=[]
for j,p in enumerate(collar_before[-384:]):
    theta=math.atan2(p.y-head_center.y,p.x-head_center.x)
    bottom.append(neck_at(theta,base_height,.006))
    top.append(neck_at(theta,base_height+p.z-collar_before[j].z,.007))
collar_positions=[]
for row in range(25):
    t=row/24
    for j in range(384):
        theta=math.atan2(bottom[j].y-head_center.y,bottom[j].x-head_center.x)
        p=neck_at(theta,bottom[j].z+(top[j].z-bottom[j].z)*t,.006+.001*smooth(t))
        collar_positions.append(clear_body(p,.0045))
update_points(collar,[collar.matrix_world.inverted()@p for p in collar_positions])
key=collar.shape_key_add(name='Original low collar attachment',from_mix=False)
for datum,p in zip(key.data,collar_before):datum.co=collar.matrix_world.inverted()@p
key.value=0
world,inverse=coat.matrix_world,coat.matrix_world.inverted();mesh=coat.data
before=[world@v.co for v in mesh.vertices]
attribute=mesh.attributes.new('Before anatomical jacket neckline','FLOAT_VECTOR','POINT')
for value,p in zip(attribute.data,before):value.vector=inverse@p
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[max((g.weight for g in v.groups if g.group==pin.index),default=0) for v in mesh.vertices]
neck_ids=[i for i,p in enumerate(before) if weights[i]>.95 and p.z>1.40]
assert len(neck_ids)==96
neck_targets={i:neck_at(math.atan2(before[i].y-head_center.y,before[i].x-head_center.x),base_height,.0085) for i in neck_ids}
kd=KDTree(len(neck_ids))
for i in neck_ids:kd.insert(before[i],i)
kd.balance()
positions=[]
for i,p in enumerate(before):
    if i in neck_targets:positions.append(neck_targets[i]);continue
    if weights[i]>.95:positions.append(p.copy());continue
    near=kd.find_n(p,3);radius=near[0][2]
    delta=sum(((neck_targets[j]-before[j])/max(d,.001)**2 for _,j,d in near),Vector())/sum(1/max(d,.001)**2 for _,j,d in near)
    positions.append(p+delta*(1-smooth(radius/.12)))
neighbors=[set() for _ in positions]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.show_viewport=False
subdivision=[(m,m.levels) for parent in (coat,body) for m in parent.modifiers if m.type=='SUBSURF']
for m,_ in subdivision:m.levels=max(m.levels,m.render_levels)
def sync():
    for v,k,p in zip(mesh.vertices,mesh.shape_keys.key_blocks['Basis'].data,positions):v.co=inverse@p;k.co=v.co
    mesh.update();bpy.context.view_layer.update()
sync()
free=[i for i,w in enumerate(weights) if w<.95]
for iteration in range(40):
    deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    kd=KDTree(len(free))
    for i in free:kd.insert(positions[i],i)
    kd.balance();deltas=[Vector() for _ in positions];counts=[0.0]*len(positions);minimum=1.
    for v in me.vertices:
        if max((g.weight for g in v.groups if g.group==pin.index),default=0)>=.8:continue
        p=world@v.co;q=body_inverse@p;hit,n,_,distance=support.find_nearest(q);gap=(q-hit).dot(n);minimum=min(minimum,gap)
        if gap>=.004:continue
        delta=body.matrix_world.to_3x3()@(n*(.0045-gap))
        for _,i,d in kd.find_n(p,6):
            w=1/max(d,.0005);deltas[i]+=delta*w;counts[i]+=w
    ev.to_mesh_clear();print('ANATOMICAL_NECKLINE_FIT',iteration,minimum,flush=True)
    if minimum>=.0035:break
    deltas=[d/counts[i] if counts[i] else Vector() for i,d in enumerate(deltas)]
    deltas=[d*.8+sum((deltas[j] for j in neighbors[i]),Vector())*(.2/len(neighbors[i])) if weights[i]<.95 else Vector() for i,d in enumerate(deltas)]
    positions=[p+d for p,d in zip(positions,deltas)];sync()
assert minimum>=.0035
update_points(coat,[inverse@p for p in positions])
key=coat.shape_key_add(name='Original low jacket neckline',from_mix=False)
for datum,p in zip(key.data,before):datum.co=inverse@p
key.value=0
attachments=mesh.attributes.new('Anatomical attachment targets','FLOAT_VECTOR','POINT')
for target,original in zip(attachments.data,mesh.attributes['Collision fit'].data):target.vector=original.vector
for i in neck_ids:attachments.data[i].vector=inverse@positions[i]
# Refit actual sewn raglan edges and all retained yoke/fastening trim.
finish=(art/'RaglanPatternCandidate/finish.py').read_text()
exec(compile(finish[finish.index('# Trace the sewn UV edges themselves;'):finish.index("scene['raglan_underarm_relaxation_iterations']")],'neckline-trim','exec'))
old_base=sum(p.z for p in collar_before[:384])/384
def fastening_height(p):
    q=p.copy();q.z+=(base_height-old_base)*smooth((p.z-1.26)/(old_base-1.26));return q
surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
collar_surface=BVHTree.FromObject(collar,bpy.context.evaluated_depsgraph_get())
def fastening_surface(p,offset):
    q=inverse@p;hit,n,_,distance=min((tree.find_nearest(q) for tree in (surface,collar_surface)),key=lambda item:item[3])
    return world@(hit+n*offset)
for name,ps in fastening_before.items():
    obj=bpy.data.objects[name]
    if 'front zipper tape' in name:
        update_points(obj,[obj.matrix_world.inverted()@fastening_surface(fastening_height(p),.0016) for p in ps])
    else:
        center=sum(ps,Vector())/len(ps)
        offset=.006 if 'pull loop' in name else .004 if 'slider' in name else .0026
        delta=fastening_surface(fastening_height(center),offset)-center
        update_points(obj,[obj.matrix_world.inverted()@(p+delta) for p in ps])
for m,level in body_levels:m.levels=level
scene['anatomical_neckline_attachment']=True
scene['anatomical_neckline_height_m']=base_height
scene['source_collar_fixed_bottom_error_m']=scene['collar_fixed_bottom_error_m']
scene['collar_fixed_bottom_error_m']=max((a-b).length for a,b in zip(collar_before[:384],bottom))
scene['jacket_neckline_maximum_attachment_motion_m']=max((neck_targets[i]-before[i]).length for i in neck_ids)
scene['collar_new_mean_height_m']=sum(p.z for p in collar_positions[-384:])/384-sum(p.z for p in collar_positions[:384])/384
