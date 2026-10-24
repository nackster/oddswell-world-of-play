"""Fit the retained collar facing to the current evaluated sewn neckline."""
import bpy,ast,math,hashlib,json,bisect
from pathlib import Path
from collections import Counter
from mathutils import Vector,Matrix
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
source=art/'NeckSkinUVCandidate/NeckSkinUV.blend'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='D8F4CA3DCAEFE622247EB24191ACFAE68F9F3E5EAC1642EE5404D51ECBE6000B'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;control=bpy.data.objects['Body flow | stance blend']
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
parsed=ast.parse((art/'BodyFlowCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']
parsed=ast.parse((art/'RaglanPatternCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('unwarp','drive','update_points')],type_ignores=[]),'raglan-points','exec'))
coat=bpy.data.objects['Character | tailored slate jacket'];collar=bpy.data.objects['Character | standing collar']
facing=bpy.data.objects['Character | collar-to-jacket facing']
fastening_before={}
for obj in scene.objects:
    if obj.name.startswith('Character | ') and any(s in obj.name for s in ('front zipper tape','zipper teeth','zipper slider','zipper pull loop')):
        if obj.type=='MESH':fastening_before[obj.name]=[obj.matrix_world@v.co for v in obj.data.vertices]
        elif obj.type=='CURVE':fastening_before[obj.name]=[obj.matrix_world@Vector(p.co[:3]) for spline in obj.data.splines for p in spline.points]
exec(compile((out/'fit_neckline.py').read_text(),'fit-neckline','exec'))
assert len(facing.data.vertices)==768 and len(facing.data.polygons)==512
original=[v.co.copy() for v in facing.data.vertices]
attribute=facing.data.attributes.new('Before sewn collar facing','FLOAT_VECTOR','POINT')
for value,p in zip(attribute.data,original):value.vector=p
modifiers=[(m,m.show_viewport,m.levels if m.type=='SUBSURF' else None) for obj in (coat,collar) for m in obj.modifiers]
for m,_,_ in modifiers:
    if m.type=='SOLIDIFY':m.show_viewport=False
    if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
def boundary_loops(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    points=[obj.matrix_world@v.co for v in mesh.vertices]
    edges=Counter(tuple(sorted((ids[i],ids[(i+1)%len(ids)]))) for face in mesh.polygons for ids in (tuple(face.vertices),) for i in range(len(ids)))
    adjacency={}
    for (a,b),count in edges.items():
        if count==1:adjacency.setdefault(a,set()).add(b);adjacency.setdefault(b,set()).add(a)
    assert all(len(v)==2 for v in adjacency.values())
    unseen=set(adjacency);loops=[]
    while unseen:
        pending=[unseen.pop()];ids=[]
        while pending:
            i=pending.pop();ids.append(i)
            for j in adjacency[i]:
                if j in unseen:unseen.remove(j);pending.append(j)
        loops.append([points[i] for i in ids])
    ev.to_mesh_clear();return loops
outer=max(boundary_loops(coat),key=lambda ps:sum(p.z for p in ps)/len(ps))
inner=min(boundary_loops(collar),key=lambda ps:sum(p.z for p in ps)/len(ps))
center=sum(inner,Vector())/len(inner)
def sampled(part,theta):
    indexed=sorted((math.atan2(p.y-center.y,p.x-center.x)%math.tau,p) for p in part)
    angles=[a for a,p in indexed];j=bisect.bisect_right(angles,theta)
    a,p=indexed[j-1] if j else (indexed[-1][0]-math.tau,indexed[-1][1])
    b,q=indexed[j] if j<len(indexed) else (indexed[0][0]+math.tau,indexed[0][1])
    return p.lerp(q,(theta-a)/(b-a))
positions=[];radial_widths=[];old_outer_errors=[]
for j in range(256):
    theta=math.tau*j/256;axis=Vector((math.cos(theta),math.sin(theta),0))
    p,q=sampled(inner,theta),sampled(outer,theta)
    radial_widths.append((q-p).dot(axis));old_outer_errors.append((facing.matrix_world@original[j*3+2]-q).length)
    positions.extend((p-axis*.0003+Vector((0,0,-.0002)),clear_body(p.lerp(q,.5)+Vector((0,0,-.0001)),.0025),q+axis*.0003+Vector((0,0,-.0002))))
assert min(radial_widths)>.0005,'Facing rings cross'
update_points(facing,[facing.matrix_world.inverted()@p for p in positions])
retained=facing.shape_key_add(name='Original floating collar facing',from_mix=False)
for point,p in zip(retained.data,original):point.co=p
retained.value=0
for m,visible,level in modifiers:
    m.show_viewport=visible
    if level is not None:m.levels=level
facing.data.update();bpy.context.view_layer.update()
scene['sewn_collar_facing']=True
scene['collar_facing_evaluated_outer_points']=len(outer)
scene['collar_facing_evaluated_inner_points']=len(inner)
scene['collar_facing_maximum_old_outer_error_m']=max(old_outer_errors)
scene['collar_facing_maximum_motion_m']=max((a-b.co).length for a,b in zip(original,facing.data.vertices))
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'AnatomicalNeckline.blend'),compress=True)
print('COLLAR_JOIN_SAVED',min(radial_widths),max(old_outer_errors),scene['collar_facing_maximum_motion_m'],flush=True)
