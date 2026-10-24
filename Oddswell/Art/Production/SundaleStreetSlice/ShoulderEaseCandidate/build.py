"""Round raised shoulder ease over the retained posed anatomical support."""
import bpy,ast,math,hashlib,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
source=art/'NeckCollarCandidate/NeckCollar.blend'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='1808A6254A566651C0731EE23C5E74FB7A126572863584D7366511D5336260C7'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;control=bpy.data.objects['Body flow | stance blend']
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
parsed=ast.parse((art/'BodyFlowCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']
parsed=ast.parse((art/'RaglanPatternCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('unwarp','drive','update_points')],type_ignores=[]),'raglan-points','exec'))
coat=bpy.data.objects['Character | tailored slate jacket'];body=bpy.data.objects['Character | internal torso support']
mesh=coat.data;world,inverse=coat.matrix_world,coat.matrix_world.inverted()
before=[world@v.co for v in mesh.vertices];positions=[p.copy() for p in before]
attribute=mesh.attributes.new('Before rounded shoulder ease','FLOAT_VECTOR','POINT')
for value,p in zip(attribute.data,before):value.vector=inverse@p
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[max((g.weight for g in v.groups if g.group==pin.index),default=0) for v in mesh.vertices]
neighbors=[set() for _ in positions]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
regions=[(Vector((-.822,-2.359,1.455)),Vector((.095,.105,.088))),
         (Vector((-.550,-2.347,1.441)),Vector((.088,.105,.083)))]
factors=[max(1-smooth(sum(((p[a]-c[a])/radius[a])**2 for a in range(3))) for c,radius in regions) if weights[i]<.95 else 0 for i,p in enumerate(before)]
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.show_viewport=False
subdivision=[(m,m.levels) for obj in (coat,body) for m in obj.modifiers if m.type=='SUBSURF']
for m,_ in subdivision:m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
support=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());body_inverse=body.matrix_world.inverted()
for i,p in enumerate(positions):
    q=body_inverse@p;hit,n,_,distance=support.find_nearest(q);gap=(q-hit).dot(n)
    if gap>.009:positions[i]-=body.matrix_world.to_3x3()@(n*((gap-.009)*factors[i]*.92))
for _ in range(32):
    positions=[p.lerp(sum((positions[j] for j in neighbors[i]),Vector())/len(neighbors[i]),factors[i]*.32) for i,p in enumerate(positions)]
def sync():
    for vertex,point,p in zip(mesh.vertices,mesh.shape_keys.key_blocks['Basis'].data,positions):vertex.co=inverse@p;point.co=vertex.co
    mesh.update();bpy.context.view_layer.update()
sync()
free_controls=[i for i,w in enumerate(weights) if w<.95]
for iteration in range(40):
    deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);evaluated=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    kd=KDTree(len(free_controls))
    for i in free_controls:kd.insert(positions[i],i)
    kd.balance();deltas=[Vector() for _ in positions];counts=[0.0]*len(positions);minimum=1.0
    for vertex in evaluated.vertices:
        weight=max((g.weight for g in vertex.groups if g.group==pin.index),default=0)
        if weight>=.8:continue
        p=world@vertex.co;q=body_inverse@p;hit,n,_,distance=support.find_nearest(q);gap=(q-hit).dot(n);minimum=min(minimum,gap)
        if gap>=.004:continue
        delta=body.matrix_world.to_3x3()@(n*(.0045-gap))
        for _,i,d in kd.find_n(p,6):
            w=1/max(d,.0005);deltas[i]+=delta*w;counts[i]+=w
    ev.to_mesh_clear();print('SHOULDER_EVALUATED_FIT',iteration,minimum,flush=True)
    if minimum>=.0035:break
    deltas=[d/counts[i] if counts[i] else Vector() for i,d in enumerate(deltas)]
    deltas=[d*.8+sum((deltas[j] for j in neighbors[i]),Vector())*(.2/len(neighbors[i])) if weights[i]<.95 else Vector() for i,d in enumerate(deltas)]
    positions=[p+d for p,d in zip(positions,deltas)];sync()
assert minimum>=.0035,'Rounded shoulders do not clear anatomy at render resolution'
update_points(coat,[inverse@p for p in positions])
retained=coat.shape_key_add(name='Original raised shoulders',from_mix=False)
for point,p in zip(retained.data,before):point.co=inverse@p
retained.value=0
# Reuse the sewn-UV seam tracing and fitted trim from the retained jacket builder.
finish=(art/'RaglanPatternCandidate/finish.py').read_text()
start=finish.index('# Trace the sewn UV edges themselves;')
end=finish.index("scene['raglan_underarm_relaxation_iterations']")
exec(compile(finish[start:end],'retained-jacket-trim','exec'))
scene['rounded_shoulder_ease']=True
scene['shoulder_rounding_iterations']=32
scene['shoulder_maximum_motion_m']=max((a-b).length for a,b in zip(before,positions))
scene['shoulder_evaluated_fit_minimum_m']=minimum
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ShoulderEase.blend'),compress=True)
print('ROUNDED_SHOULDER_SAVED',scene['shoulder_maximum_motion_m'],flush=True)
