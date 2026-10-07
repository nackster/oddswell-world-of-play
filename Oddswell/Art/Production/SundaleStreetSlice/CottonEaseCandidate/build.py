"""Consistent contact-fitted cotton pockets and bounded upper folds."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/PromenadeLightCandidate/PromenadeLight.blend';expected='1389c758ebc819e0a78250cf02006255ad178076896cdcd4279f4d7970ca9b4d'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];rig=bpy.data.objects['Walk study | native anatomical controls']
pants.data=pants.data.copy();mid.data=pants.data
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
uv=pants.data.uv_layers['Four cut cotton panels'];samples={v.index:[] for v in pants.data.vertices}
for p in pants.data.polygons:
    for i in p.loop_indices:samples[pants.data.loops[i].vertex_index].append(tuple(uv.data[i].uv))
attr=pants.data.attributes.new(name='Upper cotton gathered ease',type='FLOAT',domain='POINT')
for v,a in zip(pants.data.vertices,attr.data):
    p=pants.matrix_world@v.co;values=[]
    for u,t in samples[v.index]:
        side=0 if u<.5 else 1;across=(u-(.02 if side==0 else .50))/.48
        if side:across=1-across
        rear=t>.5
        ridges=[(.842+.039*(across-.5),.010,.0036,.48,.29),(.805-.026*(across-.5),.009,.0024,.66,.22)] if rear else [(.847-.035*(across-.5),.010,.0030,.55,.26),(.813+.024*(across-.5),.009,.0020,.74,.21)]
        relief=sum(amp*math.exp(-((p.z-z)/w)**2-((across-c)/span)**2) for z,w,amp,c,span in ridges)
        relief+=.0013*math.exp(-((p.z-(.878+.004*math.sin(across*13)))/.006)**2)*math.exp(-((across-.72)/.20)**2)
        values.append(relief*smooth((p.z-.766)/.030)*(1-smooth((p.z-.884)/.013))*smooth(across/.12)*smooth((1-across)/.12))
    a.value=sum(values)/len(values)
g=bpy.data.node_groups.new('Cotton | soft upper gathered ease','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=g.nodes;l=g.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput');normal=n.new('GeometryNodeInputNormal');field=n.new('GeometryNodeInputNamedAttribute');field.data_type='FLOAT';field.inputs['Name'].default_value=attr.name;scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';l.new(normal.outputs[0],scale.inputs[0]);l.new(field.outputs['Attribute'],scale.inputs['Scale']);setpos=n.new('GeometryNodeSetPosition');l.new(i.outputs['Geometry'],setpos.inputs['Geometry']);l.new(scale.outputs[0],setpos.inputs['Offset']);l.new(setpos.outputs['Geometry'],o.inputs['Geometry'])
for obj in (pants,mid):
    m=obj.modifiers.new('Upper cotton gathered ease','NODES');m.node_group=g;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.type=='SUBSURF'))
# Build the patterns on evaluated first-contact cloth, not an opposing walking pose.
for mod in mid.modifiers:
    if mod.type=='SUBSURF':mod.levels=mod.render_levels
saved_pose=rig.data.pose_position;rig.data.pose_position='POSE';bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=mid.evaluated_get(deps);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps);m.calc_loop_triangles();points=[ev.matrix_world@v.co for v in m.vertices];uv=m.uv_layers['Four cut cotton panels'];triangles={s:[] for s in (-1,1)};tri_uv={s:[] for s in (-1,1)}
for tri in m.loop_triangles:
    coords=[Vector((*uv.data[j].uv,0)) for j in tri.loops];center=sum((points[j] for j in tri.vertices),Vector())/3
    if sum(v.y for v in coords)/3<.5:continue
    sign=-1 if center.x<-.75 else 1;triangles[sign].append(tuple(tri.vertices));tri_uv[sign].append(coords)
trees={s:BVHTree.FromPolygons(points,faces,all_triangles=True) for s,faces in triangles.items()};report={'source_sha256':expected,'upper_fold_attribute':attr.name,'maximum_control_relief_m':max(a.value for a in attr.data),'pockets':{}}
registration='Tailored rear cotton patch UV'
for side,sign in [('left',-1),('right',1)]:
    pocket=bpy.data.objects['Character | sewn cotton back pocket '+side];patchmid=bpy.data.objects['Cotton | actual pocket sewing surface '+side]
    flags=[(m,m.show_viewport) for m in pocket.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
    for mod,flag in flags:mod.show_viewport=False
    bpy.context.view_layer.update();pd=bpy.context.evaluated_depsgraph_get();pe=pocket.evaluated_get(pd);pm=pe.to_mesh();direction=1 if pm.vertices[24].co.x>pm.vertices[0].co.x else -1;mouth=pe.matrix_world@pm.vertices[12].co;pe.to_mesh_clear()
    for mod,flag in flags:mod.show_viewport=flag
    pocket.data=pocket.data.copy();patchmid.data=pocket.data
    for name,kind in [(registration,'FLOAT_VECTOR'),('Tailored pocket fabric ease','FLOAT'),('Tailored triangle weights','FLOAT_VECTOR')]+[('Tailored triangle vertex '+str(k),'INT') for k in range(3)]:pocket.data.attributes.new(name=name,type=kind,domain='POINT')
    atlas=pocket.data.attributes[registration];ease=pocket.data.attributes['Tailored pocket fabric ease'];weights=pocket.data.attributes['Tailored triangle weights']
    for j,(item,depth) in enumerate(zip(atlas.data,ease.data)):
        row,col=divmod(j,25);u=col/24;t=row/12
        # A shallow rounded lower edge, with restrained corner rounding.
        x=mouth.x+direction*(u-.5)*.125*(1-.09*t**6);z=mouth.z-.105*t+.004*(2*u-1)**2*t**5;query=Vector((x,-3,z));hit,normal,index,distance=trees[sign].ray_cast(query,Vector((0,1,0)));assert hit is not None,('Pocket projection misses rear cloth',side,j,list(query));ids=triangles[sign][index];a,b,c=[points[k] for k in ids];item.vector=(u,t,0);bary=barycentric_transform(hit,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));bary=Vector([max(0.,min(1.,v)) for v in bary]);weights.data[j].vector=bary/sum(bary);depth.value=.00045+.0012*math.sin(math.pi*u)*math.sin(math.pi*t)+.00028*math.sin(math.pi*u)**2*math.exp(-((t-.1)/.15)**2)
        for k in range(3):pocket.data.attributes['Tailored triangle vertex '+str(k)].data[j].value=ids[k]
    ng=bpy.data.node_groups.new('Cotton | direct triangle pocket '+side,'GeometryNodeTree');ng.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');ng.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=ng.nodes;l=ng.links;inp=n.new('NodeGroupInput');output=n.new('NodeGroupOutput');info=n.new('GeometryNodeObjectInfo');info.transform_space='RELATIVE';info.inputs['Object'].default_value=mid;position=n.new('GeometryNodeInputPosition');normal=n.new('GeometryNodeInputNormal')
    def field(name,kind):
        node=n.new('GeometryNodeInputNamedAttribute');node.data_type=kind;node.inputs['Name'].default_value=name;return node.outputs['Attribute']
    separate=n.new('ShaderNodeSeparateXYZ');l.new(field('Tailored triangle weights','FLOAT_VECTOR'),separate.inputs[0]);sums=[]
    for value in (position.outputs[0],normal.outputs[0]):
        terms=[]
        for k in range(3):
            sample=n.new('GeometryNodeSampleIndex');sample.data_type='FLOAT_VECTOR';sample.domain='POINT';l.new(info.outputs['Geometry'],sample.inputs['Geometry']);l.new(value,sample.inputs['Value']);l.new(field('Tailored triangle vertex '+str(k),'INT'),sample.inputs['Index']);scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';l.new(sample.outputs['Value'],scale.inputs[0]);l.new(separate.outputs[k],scale.inputs['Scale']);terms.append(scale.outputs[0])
        add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(terms[0],add.inputs[0]);l.new(terms[1],add.inputs[1]);add2=n.new('ShaderNodeVectorMath');add2.operation='ADD';l.new(add.outputs[0],add2.inputs[0]);l.new(terms[2],add2.inputs[1]);sums.append(add2.outputs[0])
    offset=n.new('ShaderNodeVectorMath');offset.operation='SCALE';l.new(sums[1],offset.inputs[0]);l.new(field('Tailored pocket fabric ease','FLOAT'),offset.inputs['Scale']);setpos=n.new('GeometryNodeSetPosition');l.new(inp.outputs[0],setpos.inputs['Geometry']);l.new(sums[0],setpos.inputs['Position']);l.new(offset.outputs[0],setpos.inputs['Offset']);valid=n.new('GeometryNodeStoreNamedAttribute');valid.data_type='BOOLEAN';valid.domain='POINT';valid.inputs['Name'].default_value='Sewn UV sample valid';valid.inputs['Value'].default_value=True;l.new(setpos.outputs[0],valid.inputs['Geometry']);l.new(valid.outputs[0],output.inputs[0])
    next(m for m in pocket.modifiers if m.type=='NODES').node_group=ng;next(m for m in patchmid.modifiers if m.type=='NODES').node_group=ng
    # Smoothing may lift a curved patch above the underlying cloth.
    for obj in (pocket,patchmid):
        follow=obj.modifiers.new('Tailored patch final cloth fit','SHRINKWRAP');follow.target=mid;follow.wrap_method='NEAREST_SURFACEPOINT';follow.wrap_mode='ON_SURFACE';follow.offset=.0012;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.type=='SUBSURF')+1)
    for prefix in ('inset back pocket stitch','pocket mouth topstitch'):
        stitch=bpy.data.objects['Walk surface | Character | '+prefix+' '+side];stitch.data=stitch.data.copy();values=stitch.data.attributes.new(name=registration,type='FLOAT_VECTOR',domain='POINT');mod=next(m for m in stitch.modifiers if m.type=='NODES');ng=mod.node_group.copy();mod.node_group=ng
        path=[(r,1) for r in range(1,12)]+[(11,c) for c in range(2,24)]+[(r,23) for r in range(10,0,-1)] if prefix=='inset back pocket stitch' else [(2,c) for c in range(2,23)]
        assert len(values.data)==len(path)*8
        for j,(r,c) in enumerate(path):
            q=atlas.data[r*25+c].vector.copy();pr,pc=path[max(0,j-1)];nr,nc=path[min(len(path)-1,j+1)];d=atlas.data[nr*25+nc].vector-atlas.data[pr*25+pc].vector;perp=Vector((-d.y,d.x,0)).normalized()
            for k in range(8):values.data[j*8+k].vector=q+perp*(.00030*math.sin(k*math.tau/8))
        for node in ng.nodes:
            if node.bl_idname=='GeometryNodeInputNamedAttribute' and node.inputs['Name'].default_value.startswith('Sewn cloth registration UV'):node.inputs['Name'].default_value=registration
    report['pockets'][pocket.name]={'new_registration':registration,'preserved_column_direction':direction,'nominal_contact_width_m':.125,'nominal_contact_height_m':.105,'maximum_ease_m':max(a.value for a in ease.data),'method':'Matching contact patterns at existing mouths project straight onto rear cloth and bind to evaluated triangle indices and normalized barycentric weights, followed by a 1.2 mm final surface fit. Original controls/UVs/registration preserved. Threads use a separate unique rectangular pocket atlas.','evaluated_cloth_vertex_count':len(points)}
ev.to_mesh_clear();rig.data.pose_position=saved_pose;bpy.context.view_layer.update();scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'CottonEase.blend'),compress=True)
with (out/'CottonEase.blend').open('rb') as f:report['candidate_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('COTTON_EASE_BUILT',report['maximum_control_relief_m'],report['candidate_sha256'],flush=True)
