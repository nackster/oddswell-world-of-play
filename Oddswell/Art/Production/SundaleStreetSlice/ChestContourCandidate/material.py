import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'ChestContour.blend'));coat=bpy.data.objects['Character | tailored slate jacket'];mat=coat.data.materials[0];rows=[]
for n in mat.node_tree.nodes:
    rows.append({'name':n.name,'type':n.type,'image':getattr(getattr(n,'image',None),'name',None),'inputs':{s.name:(str(s.default_value) if hasattr(s,'default_value') else None) for s in n.inputs},'links':[(l.from_node.name,l.from_socket.name,l.to_socket.name) for s in n.inputs for l in s.links]})
(out/'material-inspect.json').write_text(json.dumps({'material':mat.name,'nodes':rows},indent=2));print('MATERIAL_INSPECT_DONE',flush=True)
mat=mat.copy();mat.name='Chest study | slate spun-fiber weave';coat.data.materials[0]=mat
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');uv=nodes.get('Stable physical rest-panel weave');weave=nodes.get('Bump.001');weave.inputs['Strength'].default_value=.7;weave.inputs['Distance'].default_value=.0008;bs.inputs['Sheen Weight'].default_value=.12
noise=nodes.new('ShaderNodeTexNoise');noise.name='Rest-panel spun yarn variation';noise.inputs['Scale'].default_value=55;noise.inputs['Detail'].default_value=2;links.new(uv.outputs['UV'],noise.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB');ramp.name='Restrained cotton dye variation';ramp.color_ramp.elements[0].color=(.78,.78,.78,1);ramp.color_ramp.elements[1].color=(1.08,1.08,1.08,1);links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
color=bs.inputs['Base Color'].links[0].from_socket;multiply=nodes.new('ShaderNodeMixRGB');multiply.name='Spun-fiber dye over original slate and teal';multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1;links.new(color,multiply.inputs[1]);links.new(ramp.outputs['Color'],multiply.inputs[2]);links.new(multiply.outputs[0],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.name='Shallow spun yarn surface';bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.0005;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],weave.inputs['Normal'])
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ChestContour.blend'),compress=True)
with (out/'ChestContour.blend').open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
report=json.loads((out/'build-report.json').read_text());report['candidate_sha256']=digest;report['material']={'name':mat.name,'original_material_preserved':True,'existing_packed_weave_maps_preserved':True,'original_physical_panel_uv_preserved':True,'weave_bump_strength':.7,'weave_bump_distance_m':.0008,'sheen_weight':.12,'spun_variation_scale_per_266mm_tile':55,'variation_ramp':[.78,1.08],'noise_bump_strength':.15,'noise_bump_distance_m':.0005,'new_bitmap_assets':0};(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('CHEST_FABRIC_SAVED',digest,flush=True)
