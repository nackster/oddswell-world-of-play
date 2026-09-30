"""Relax two underarm fold throats and fit the evaluated cloth to anatomy."""
import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
out=Path(__file__).resolve().parent
root=next(p for p in Path(__file__).resolve().parents if (p/'Oddswell').is_dir() and (p/'.git').exists())
work=root/'client/OddsWell/Saved/NextTen20260912/RaglanPatternBuild'
bpy.ops.wm.open_mainfile(filepath=str(work/'RaglanDraft.blend'))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
body=bpy.data.objects['Character | internal torso support']
control=bpy.data.objects['Body flow | stance blend']
world,inverse=coat.matrix_world,coat.matrix_world.inverted()
mesh=coat.data
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
functions=ast.parse((root/'Oddswell/Art/Production/SundaleStreetSlice/BodyFlowCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in functions.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow-functions','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']
functions=ast.parse((out/'build.py').read_text())
exec(compile(ast.Module(body=[n for n in functions.body if isinstance(n,ast.FunctionDef) and n.name in ('unwarp','drive','update_points')],type_ignores=[]),'jacket-finish-functions','exec'))
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[max((g.weight for g in v.groups if g.group==pin.index),default=0) for v in mesh.vertices]
neighbors=[set() for _ in mesh.vertices]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
before=[world@v.co for v in mesh.vertices]
positions=[p.copy() for p in before]
regions=[Vector((-.8515,-2.3678,1.2463)),Vector((-.5173,-2.3695,1.2448))]
factors=[.55*max(1-smooth(sum(((p[a]-c[a])/r)**2 for a,r in enumerate((.052,.070,.064)))) for c in regions) if weights[i]<.95 else 0 for i,p in enumerate(positions)]
for _ in range(45):
    positions=[p.lerp(sum((positions[j] for j in neighbors[i]),Vector())/len(neighbors[i]),factors[i]) for i,p in enumerate(positions)]
def sync():
    for vertex,point,p in zip(mesh.vertices,mesh.shape_keys.key_blocks['Basis'].data,positions):vertex.co=inverse@p;point.co=vertex.co
    mesh.update();bpy.context.view_layer.update()
sync()
# Round tight fold creases before offsetting a physical inner cloth surface.
fold_regions=[((-.8767,-2.3141,1.2894),(.030,.032,.046)),
              ((-.8849,-2.2994,1.3441),(.026,.028,.040)),
              ((-.4634,-2.3059,1.3189),(.024,.024,.028)),
              ((-.5134,-2.3993,1.3361),(.026,.030,.034)),
              ((-.8280,-2.4290,1.3260),(.040,.038,.060)),
              ((-.8165,-2.3614,1.4553),(.018,.026,.023))]
factors=[.45*max(1-smooth(sum(((p[a]-c[a])/r[a])**2 for a in range(3))) for c,r in fold_regions) if weights[i]<.95 else 0 for i,p in enumerate(positions)]
for _ in range(30):
    positions=[p.lerp(sum((positions[j] for j in neighbors[i]),Vector())/len(neighbors[i]),factors[i]) for i,p in enumerate(positions)]
sync()
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
solid.show_viewport=False;bpy.context.view_layer.update()
subdivision=[(m,m.levels) for obj in (coat,body) for m in obj.modifiers if m.type=='SUBSURF']
for modifier,_ in subdivision:modifier.levels=max(modifier.levels,modifier.render_levels)
bpy.context.view_layer.update()
support=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
body_inverse=body.matrix_world.inverted()
free_controls=[i for i,w in enumerate(weights) if w<.95]
for iteration in range(40):
    # A control-only test misses the curved surface between held hems and free cloth.
    deps=bpy.context.evaluated_depsgraph_get()
    ev=coat.evaluated_get(deps);evaluated=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
    kd=KDTree(len(free_controls))
    for i in free_controls:kd.insert(positions[i],i)
    kd.balance()
    deltas=[Vector() for _ in positions];counts=[0.0]*len(positions);minimum=1.0
    for vertex in evaluated.vertices:
        weight=max((g.weight for g in vertex.groups if g.group==pin.index),default=0)
        if weight>=.8:continue
        p=world@vertex.co;q=body_inverse@p
        hit,normal,_,distance=support.find_nearest(q);gap=(q-hit).dot(normal)
        minimum=min(minimum,gap)
        if gap>=.004:continue
        delta=body.matrix_world.to_3x3()@(normal*(.0045-gap))
        near=[(i,1/max(d,.0005)) for _,i,d in kd.find_n(p,6) if weights[i]<.95]
        for i,w in near:deltas[i]+=delta*w;counts[i]+=w
    ev.to_mesh_clear()
    print('EVALUATED_JACKET_FIT',iteration,minimum,flush=True)
    if minimum>=.0035:break
    deltas=[d/counts[i] if counts[i] else Vector() for i,d in enumerate(deltas)]
    deltas=[d*.8+sum((deltas[j] for j in neighbors[i]),Vector())*(.2/len(neighbors[i])) if weights[i]<.95 else Vector() for i,d in enumerate(deltas)]
    positions=[p+d for p,d in zip(positions,deltas)];sync()
assert minimum>=.0035,'Render-resolution evaluated cloth does not clear anatomy'
update_points(coat,[inverse@p for p in positions])
# Trace the sewn UV edges themselves; projecting the old curve can jump across folds.
deps=bpy.context.evaluated_depsgraph_get()
ev=coat.evaluated_get(deps);evaluated=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
uv=evaluated.uv_layers['Cut raglan cloth panels']
sewn_edges={}
for side in (-1,1):
    for front in (1,-1):
        u=.01 if side<0 else .32
        v0=.01 if front==1 else .32
        selected={}
        for polygon in evaluated.polygons:
            mean=sum((uv.data[index].uv for index in polygon.loop_indices),Vector((0,0)))/len(polygon.loop_indices)
            if not u<mean.x<u+.31 or not v0<mean.y<v0+.31:continue
            for index in polygon.loop_indices:
                value=uv.data[index].uv
                if abs(value.x-u)<1e-6 and v0+.31*22/40-1e-6<=value.y<=v0+.31+1e-6:
                    vertex=evaluated.vertices[evaluated.loops[index].vertex_index]
                    selected[vertex.index]=(value.y,vertex.co.copy())
        path=[p for _,p in sorted(selected.values(),key=lambda pair:pair[0],reverse=True)]
        assert len(path)>=35,('Incomplete sewn raglan edge',side,front,len(path))
        dense=[]
        for a,b in zip(path,path[1:]):
            steps=max(1,math.ceil((a-b).length/.004))
            dense.extend(a.lerp(b,j/steps) for j in range(steps))
        dense.append(path[-1]);sewn_edges[side,front]=dense
ev.to_mesh_clear()
for modifier,level in subdivision:modifier.levels=level
bpy.context.view_layer.update()
solid.solidify_mode='NON_MANIFOLD';solid.nonmanifold_thickness_mode='CONSTRAINTS'
solid.thickness=.0012;solid.thickness_clamp=1.;solid.use_thickness_angle_clamp=True
bpy.context.view_layer.update()
surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
collar_surface=BVHTree.FromObject(bpy.data.objects['Character | standing collar'],bpy.context.evaluated_depsgraph_get())
for obj in list(scene.objects):
    if not obj.name.startswith('Character | '):continue
    if obj.type=='MESH' and 'yoke' in obj.name:
        values=[]
        for vertex in obj.data.vertices:
            q=inverse@(obj.matrix_world@vertex.co);hit,normal,_,distance=surface.find_nearest(q)
            values.append(obj.matrix_world.inverted()@(world@(hit+normal*.00035)))
        update_points(obj,values)
    elif obj.type=='CURVE' and 'raglan topstitch' in obj.name:
        side,front=map(int,obj.name.split()[-2:])
        values=[]
        for p in sewn_edges[side,front]:
            hit,normal,_,distance=surface.find_nearest(p);values.append(hit+normal*.00055)
        assert max((a-b).length for a,b in zip(values,values[1:]))<.015,'Sewn raglan edge jumped'
        data=bpy.data.curves.new('Evaluated sewn raglan edge','CURVE')
        data.dimensions='3D';data.bevel_depth=.00022;data.bevel_resolution=2
        for material in obj.data.materials:data.materials.append(material)
        spline=data.splines.new('POLY');spline.points.add(len(values)-1)
        obj.data=data;update_points(obj,values)
    elif obj.type=='CURVE' and any(s in obj.name for s in ('yoke topstitch','front zipper tape','front welt pocket')):
        values=[]
        for spline in obj.data.splines:
            for point in spline.points:
                q=inverse@(obj.matrix_world@Vector(point.co[:3]))
                hit,normal,_,distance=min((tree.find_nearest(q) for tree in (surface,collar_surface)),key=lambda result:result[3]) if 'front zipper tape' in obj.name else surface.find_nearest(q)
                offset=.00055 if 'topstitch' in obj.name else .0016
                values.append(obj.matrix_world.inverted()@(world@(hit+normal*offset)))
        update_points(obj,values)
    elif obj.type=='MESH' and obj.name.startswith('Character | zipper teeth'):
        center=sum((inverse@(obj.matrix_world@v.co) for v in obj.data.vertices),Vector())/len(obj.data.vertices)
        hit,normal,_,distance=min((tree.find_nearest(center) for tree in (surface,collar_surface)),key=lambda result:result[3])
        shift=obj.matrix_world.inverted().to_3x3()@(world.to_3x3()@(hit+normal*.0026-center))
        update_points(obj,[v.co+shift for v in obj.data.vertices])
solid.show_viewport=True
scene['raglan_underarm_relaxation_iterations']=45
scene['raglan_fold_fillet_iterations']=30
scene['raglan_final_fit_maximum_m']=max((a-b).length for a,b in zip(before,positions))
scene['raglan_evaluated_fit_minimum_m']=minimum
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'RaglanPattern.blend'),compress=True)
print('RAGLAN_FINISHED',scene['raglan_final_fit_maximum_m'],flush=True)
