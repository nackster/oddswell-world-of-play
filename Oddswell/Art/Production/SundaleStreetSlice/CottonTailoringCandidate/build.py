"""Editable cotton folds and softly sewn pocket construction on the retained walk."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/WaistNeckContinuityCandidate/WaistNeck.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='2900363715a0056444b9b85509a00dcc01ab6c5e5cfee4fcac32a537af513079'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface']
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
uv=pants.data.uv_layers['Four cut cotton panels'];samples={v.index:[] for v in pants.data.vertices}
for poly in pants.data.polygons:
    for li in poly.loop_indices:samples[pants.data.loops[li].vertex_index].append(tuple(uv.data[li].uv))
attribute=pants.data.attributes.new(name='Cotton directional fold relief',type='FLOAT',domain='POINT')
for v,value in zip(pants.data.vertices,attribute.data):
    p=pants.matrix_world@v.co;values=[]
    for u,t in samples[v.index]:
        side=0 if u<.5 else 1;front=t<.5;across=(u-(.02 if side==0 else .50))/.48
        if side==1:across=1-across
        ridges=[(.768+.065*(across-.5),.008,.0027,.48,.28),(.711-.043*(across-.5),.009,.0018,.65,.26)] if front else [(.737+.070*(across-.5),.009,.0024,.52,.34),(.692-.040*(across-.5),.011,.0015,.72,.24)]
        relief=sum(amp*math.exp(-((p.z-height)/width)**2-((across-center)/span)**2) for height,width,amp,center,span in ridges)
        relief+=.00075*math.exp(-((p.z-(.84+.012*math.sin(across*8)))/.006)**2)*math.exp(-((across-.80)/.18)**2)
        values.append(relief*smooth((p.z-.62)/.035)*(1-smooth((p.z-.866)/.02))*smooth(across/.10)*smooth((1-across)/.10))
    value.value=sum(values)/len(values)
group=bpy.data.node_groups.new('Cotton | bounded directional sewn folds','GeometryNodeTree')
group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
n=group.nodes;l=group.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput');normal=n.new('GeometryNodeInputNormal');a=n.new('GeometryNodeInputNamedAttribute');a.data_type='FLOAT';a.inputs['Name'].default_value=attribute.name
scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';l.new(normal.outputs[0],scale.inputs[0]);l.new(a.outputs['Attribute'],scale.inputs['Scale']);setpos=n.new('GeometryNodeSetPosition');l.new(i.outputs['Geometry'],setpos.inputs['Geometry']);l.new(scale.outputs[0],setpos.inputs['Offset']);l.new(setpos.outputs['Geometry'],o.inputs['Geometry'])
for obj in (pants,mid):
    mod=obj.modifiers.new('Cotton directional compression and tension folds','NODES');mod.node_group=group;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.type=='SUBSURF'))
report={'source_sha256':hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),'directional_folds':{'attribute':attribute.name,'maximum_control_relief_m':max(v.value for v in attribute.data),'placement':'After shared armature, hip relaxation and leg clearance; before subdivision on garment and its actual registered midsurface. Outward-only, localized seat/upper-thigh ridges and small waistband gathers. Authored tailoring, not dynamic cloth simulation.'},'pockets':{}}
for side in ('left','right'):
    pocket=bpy.data.objects['Character | sewn cotton back pocket '+side];gn=next(m for m in pocket.modifiers if m.type=='NODES').node_group
    relief=pocket.data.attributes.new(name='Cotton pocket seam and ease',type='FLOAT',domain='POINT')
    for j,item in enumerate(relief.data):
        r,c=divmod(j,25);u=c/24;t=r/12
        item.value=.00045+.00105*math.sin(math.pi*u)*math.sin(math.pi*t)+.00035*math.sin(math.pi*u)**2*math.exp(-((t-.12)/.13)**2)
    scale=next(n for n in gn.nodes if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='SCALE')
    field=gn.nodes.new('GeometryNodeInputNamedAttribute');field.data_type='FLOAT';field.inputs['Name'].default_value=relief.name;gn.links.new(field.outputs['Attribute'],scale.inputs['Scale'])
    sub=pocket.modifiers.new('Soft cotton sewn pocket corners','SUBSURF');sub.levels=2;sub.render_levels=2;pocket.modifiers.move(len(pocket.modifiers)-1,1)
    solid=next(m for m in pocket.modifiers if m.type=='SOLIDIFY');solid.thickness=.00035;solid.offset=1;solid.solidify_mode='EXTRUDE';solid.use_even_offset=False
    patchmid=pocket.copy();patchmid.data=pocket.data;patchmid.name='Cotton | actual pocket sewing surface '+side;scene.collection.objects.link(patchmid)
    for m in list(patchmid.modifiers):
        if m.type=='SOLIDIFY':patchmid.modifiers.remove(m)
    patchmid.hide_render=True;patchmid.hide_set(True)
    registration=next(n.inputs['Name'].default_value for n in gn.nodes if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value.startswith('Sewn cloth registration UV'))
    atlas=pocket.data.attributes[registration]
    for prefix in ('inset back pocket stitch','pocket mouth topstitch'):
        stitch=bpy.data.objects['Walk surface | Character | '+prefix+' '+side];ng=next(m for m in stitch.modifiers if m.type=='NODES').node_group
        registered=next(n for n in ng.nodes if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value.startswith('Sewn cloth registration UV'));values=stitch.data.attributes[registered.inputs['Name'].default_value]
        path=[(r,1) for r in range(1,12)]+[(11,c) for c in range(2,24)]+[(r,23) for r in range(10,0,-1)] if prefix=='inset back pocket stitch' else [(2,c) for c in range(2,23)]
        assert len(stitch.data.vertices)==len(path)*8
        depth=stitch.data.attributes.new(name='Cotton rounded thread depth',type='FLOAT',domain='POINT')
        values=stitch.data.attributes[registered.inputs['Name'].default_value]
        for j,(r,c) in enumerate(path):
            q=atlas.data[r*25+c].vector.copy();pr,pc=path[max(0,j-1)];nr,nc=path[min(len(path)-1,j+1)]
            direction=atlas.data[nr*25+nc].vector-atlas.data[pr*25+pc].vector;perp=Vector((-direction.y,direction.x,0)).normalized()
            for k in range(8):
                angle=k*math.tau/8;values.data[j*8+k].vector=q+perp*(.00030*math.sin(angle));depth.data[j*8+k].value=.00046+.00012*math.cos(angle)
        info=next(n for n in ng.nodes if n.bl_idname=='GeometryNodeObjectInfo');info.inputs['Object'].default_value=patchmid
        for n in ng.nodes:
            if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value=='Four cut cotton panels':n.inputs['Name'].default_value=registration
        scale=next(n for n in ng.nodes if n.bl_idname=='ShaderNodeVectorMath' and n.operation=='SCALE');field=ng.nodes.new('GeometryNodeInputNamedAttribute');field.data_type='FLOAT';field.inputs['Name'].default_value=depth.name;ng.links.new(field.outputs['Attribute'],scale.inputs['Scale'])
    report['pockets'][pocket.name]={'subdivision':2,'edge_base_clearance_m':.00045,'maximum_patch_ease_m':max(v.value for v in relief.data),'thickness_m':.00035,'topstitch_surface':patchmid.name,'topstitch_clearance_range_m':[.00034,.00058],'topstitch_registration':'Inset grid and mouth paths in the actual pocket atlas, with small tangential/normal offsets retaining rounded thread cross sections; follows the softly sewn edge rather than the underlying shorts.'}
# The licensed packed cotton textures remain the source of fiber detail.
material=bpy.data.materials['Character | offwhite cotton twill'];bsdf=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Diffuse Roughness'].default_value=.30;bsdf.inputs['Sheen Weight'].default_value=.22
report['material']='Retained licensed packed cotton image textures; diffuse roughness 0.30 and fiber sheen 0.22. No new bitmap assets.'
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'CottonDetail.blend'),compress=True)
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('COTTON_DETAIL_SAVED',flush=True)
