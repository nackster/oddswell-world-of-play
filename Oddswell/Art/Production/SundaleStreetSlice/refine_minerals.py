"""Layered native mineral relief for close-up civic stone and fired paving."""
def mineral_relief(material,pore_scale,pore_depth):
    nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes.get('Principled BSDF')
    coords=next(node for node in nodes if node.type=='TEX_COORD')
    existing=next(node for node in nodes if node.type=='BUMP')
    existing.inputs['Distance'].default_value=.003
    existing.inputs['Strength'].default_value=.22
    pores=nodes.new('ShaderNodeTexVoronoi');pores.name='Sparse mineral pores';pores.inputs['Scale'].default_value=pore_scale
    links.new(coords.outputs['Object'],pores.inputs['Vector'])
    profile=nodes.new('ShaderNodeValToRGB');profile.name='Rounded pore profile'
    profile.color_ramp.elements[0].position=.055;profile.color_ramp.elements[0].color=(0,0,0,1)
    profile.color_ramp.elements[1].position=.17;profile.color_ramp.elements[1].color=(1,1,1,1)
    profile.color_ramp.interpolation='EASE'
    links.new(pores.outputs['Distance'],profile.inputs[0])
    bump=nodes.new('ShaderNodeBump');bump.name='Mineral pits';bump.inputs['Distance'].default_value=pore_depth;bump.inputs['Strength'].default_value=.65
    links.new(profile.outputs[0],bump.inputs['Height']);links.new(existing.outputs[0],bump.inputs['Normal'])
    grain=nodes.new('ShaderNodeTexNoise');grain.name='Fine mineral grain';grain.inputs['Scale'].default_value=950;grain.inputs['Detail'].default_value=2
    links.new(coords.outputs['Object'],grain.inputs['Vector'])
    micro=nodes.new('ShaderNodeBump');micro.inputs['Strength'].default_value=.22;micro.inputs['Distance'].default_value=.00022
    links.new(grain.outputs['Fac'],micro.inputs['Height']);links.new(bump.outputs[0],micro.inputs['Normal']);links.new(micro.outputs[0],bs.inputs['Normal'])
    rough=nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.70;rough.inputs['To Max'].default_value=.96
    links.new(grain.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs['Result'],bs.inputs['Roughness'])

mineral_relief(stone,105,.0011)
for material in pavers:mineral_relief(material,155,.0007)

# Oak fibers follow the long direction of each seat slat or display shelf.
nodes,links=wood.node_tree.nodes,wood.node_tree.links
coords=next(node for node in nodes if node.type=='TEX_COORD')
noise=next(node for node in nodes if node.type=='TEX_NOISE');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=3
scale=nodes.new('ShaderNodeVectorMath');scale.name='Oak grain direction';scale.operation='MULTIPLY';scale.inputs[1].default_value=(2,65,20)
links.new(coords.outputs['Generated'],scale.inputs[0]);links.new(scale.outputs['Vector'],noise.inputs['Vector'])
bump=next(node for node in nodes if node.type=='BUMP');bump.inputs['Distance'].default_value=.00045;bump.inputs['Strength'].default_value=.2
wood_along_y=wood.copy();wood_along_y.name='OW | oak grain along shelf'
wood_along_y.node_tree.nodes['Oak grain direction'].inputs[1].default_value=(65,2,20)
