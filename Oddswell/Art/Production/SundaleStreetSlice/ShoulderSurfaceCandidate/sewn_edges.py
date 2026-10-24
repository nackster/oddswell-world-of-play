"""Rebuild raglan stitching from the actual subdivided cloth-panel edges."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'RoundedShoulder.blend'))
scene=bpy.context.scene;scene.frame_set(1);coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface']
sub=next(m for m in coat.modifiers if m.type=='SUBSURF');level=sub.levels;sub.levels=2
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.show_viewport=False
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
uv=mesh.uv_layers['Cut raglan cloth panels'];paths={}
for side in (-1,1):
    for front in (1,-1):
        u=.01 if side<0 else .32;v0=.01 if front==1 else .32;selected={}
        for polygon in mesh.polygons:
            mean=sum((uv.data[i].uv for i in polygon.loop_indices),Vector((0,0)))/len(polygon.loop_indices)
            if not u<mean.x<u+.31 or not v0<mean.y<v0+.31:continue
            for i in polygon.loop_indices:
                value=uv.data[i].uv
                if abs(value.x-u)<1e-6 and v0+.31*22/40-1e-6<=value.y<=v0+.31+1e-6:
                    vertex=mesh.vertices[mesh.loops[i].vertex_index];selected[vertex.index]=(value.y,vertex.co.copy()+vertex.normal*.00055)
        graph={i:set() for i in selected}
        for edge in mesh.edges:
            a,b=edge.vertices
            if a in selected and b in selected:graph[a].add(b);graph[b].add(a)
        pending=set(selected);components=[]
        while pending:
            queue=[pending.pop()];component=set(queue)
            while queue:
                for i in graph[queue.pop()]:
                    if i in pending:pending.remove(i);component.add(i);queue.append(i)
            components.append(component)
        component=max(components,key=len);ends=[i for i in component if len(graph[i])==1]
        assert len(ends)==2,('Sewn edge is not a simple path',side,front,len(ends))
        current=max(ends,key=lambda i:selected[i][0]);indices=[]
        while current not in indices:
            indices.append(current);remaining=graph[current]-set(indices)
            if not remaining:break
            assert len(remaining)==1;current=remaining.pop()
        assert len(indices)==len(component)
        path=[selected[i][1] for i in indices]
        print('SEWN_COMPONENTS',side,front,sorted(map(len,components)),flush=True)
        steps=[(a-b).length for a,b in zip(path,path[1:])]
        longest=steps.index(max(steps))
        print('SEWN_LONGEST',side,front,max(steps),list(path[longest]),list(path[longest+1]),flush=True)
        assert len(path)>=35;assert max(steps)<.035,('Unexpected cloth-edge span',side,front,max(steps))
        dense=[]
        for a,b in zip(path,path[1:]):
            count=max(1,math.ceil((a-b).length/.004))
            dense.extend(a.lerp(b,j/count) for j in range(count))
        dense.append(path[-1]);path=dense
        assert max((a-b).length for a,b in zip(path,path[1:]))<.00401
        paths[side,front]=path
ev.to_mesh_clear();sub.levels=level;solid.show_viewport=True
report={}
for (side,front),path in paths.items():
    name=f'Character | raglan topstitch {side} {front}';obj=bpy.data.objects['Walk surface | '+name]
    for m in list(obj.modifiers):obj.modifiers.remove(m)
    data=bpy.data.curves.new('Refined sewn UV edge','CURVE');data.dimensions='3D';data.bevel_depth=.00022;data.bevel_resolution=2
    for material in bpy.data.objects[name].data.materials:data.materials.append(material)
    s=data.splines.new('POLY');s.points.add(len(path)-1)
    for p,q in zip(s.points,path):p.co=(*q,1)
    curve=bpy.data.objects.new('Editable refined seam | '+name,data);scene.collection.objects.link(curve);curve.matrix_world=coat.matrix_world.copy();curve.hide_render=True
    bpy.context.view_layer.update();obj.data=bpy.data.meshes.new_from_object(curve.evaluated_get(bpy.context.evaluated_depsgraph_get()));obj.matrix_world=curve.matrix_world.copy();curve.hide_set(True)
    mod=obj.modifiers.new('Refined sewn garment surface following','SURFACE_DEFORM');mod.target=cage
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.surfacedeform_bind(modifier=mod.name);assert mod.is_bound
    report[obj.name]={'edge_points':len(path),'maximum_edge_step_m':max((a-b).length for a,b in zip(path,path[1:]))}
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'RoundedShoulder.blend'),compress=True)
(out/'sewn-edge-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('SEWN_EDGES_SAVED',flush=True)
