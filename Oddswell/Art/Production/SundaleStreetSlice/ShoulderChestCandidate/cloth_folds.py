"""Restrained authored front-quarter tension folds on the moving native jacket."""
import bpy,json,math
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'ShoulderChest.blend'));scene=bpy.context.scene;scene.frame_set(1);coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];uv=coat.data.uv_layers['Cut raglan cloth panels'];samples=[[] for v in coat.data.vertices]
for poly in coat.data.polygons:
    for i in poly.loop_indices:samples[coat.data.loops[i].vertex_index].append(tuple(uv.data[i].uv))
field=coat.data.attributes.new(name='Jacket front-quarter tension relief',type='FLOAT',domain='POINT');pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for v,item in zip(coat.data.vertices,field.data):
    p=coat.matrix_world@v.co;across=abs(p.x+.70);front=sum(float(u<.65 and t<.32) for u,t in samples[v.index])/len(samples[v.index]);held=max((g.weight for g in v.groups if g.group==pin),default=0);outer=math.exp(-((across-.135)/.105)**2);side=.90 if p.x<-.70 else 1
    heights=[(1.315+.13*(across-.10),.011,.0030),(1.251-.22*(across-.10),.014,.0020)]
    relief=sum(amp*math.exp(-((p.z-height)/width)**2)*outer for height,width,amp in heights)
    relief+=.0018*math.exp(-((across-.092)/.012)**2)*smooth((p.z-1.04)/.025)*(1-smooth((p.z-1.19)/.045))
    item.value=relief*side*front*(1-smooth((held-.65)/.30))
group=bpy.data.node_groups.new('Jacket | front-quarter tension folds','GeometryNodeTree');group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=group.nodes;l=group.links;inp=n.new('NodeGroupInput');output=n.new('NodeGroupOutput');normal=n.new('GeometryNodeInputNormal');a=n.new('GeometryNodeInputNamedAttribute');a.data_type='FLOAT';a.inputs['Name'].default_value=field.name;scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';l.new(normal.outputs[0],scale.inputs[0]);l.new(a.outputs['Attribute'],scale.inputs['Scale']);setpos=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);l.new(scale.outputs[0],setpos.inputs['Offset']);l.new(setpos.outputs['Geometry'],output.inputs['Geometry'])
for obj in (coat,cage):
    mod=obj.modifiers.new('Front-quarter cotton tension folds','NODES');mod.node_group=group;obj.modifiers.move(len(obj.modifiers)-1,next(i for i,m in enumerate(obj.modifiers) if m.type=='SUBSURF'))
report=json.loads((out/'build-report.json').read_text());report['front_quarter_folds']={'attribute':field.name,'maximum_control_relief_m':max(v.value for v in field.data),'method':'Two oblique armhole/chest tension ridges and short local zipper/waist gathers, varying modestly by side; outward-only normal relief after anatomical clearance and before subdivision, shared by actual coat and sewn-detail cage. Authored native tailoring, not dynamic cloth.'};(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ShoulderChest.blend'),compress=True);print('JACKET_TENSION_FOLDS_SAVED',report['front_quarter_folds']['maximum_control_relief_m'],flush=True)
