"""Native fabric shading from retained CC0 surface photographs and maps.

Executed after garment construction. Box projection keeps the editable
sculpt usable before production garment UVs are authored.
"""
fabric_images={}
for material,asset in ((jacket,'terlenka'),(shorts,'denim_fabric_04'),(shoe_fabric,'denim_fabric_04')):
    nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes.get('Principled BSDF')
    coords=next(node for node in nodes if node.type=='TEX_COORD')
    mapping=nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(1/.266,)*3
    links.new(coords.outputs['Object'],mapping.inputs['Vector'])
    maps={}
    for channel,ext in (('diff','jpg'),('disp','png'),('rough','jpg')):
        name=f'{asset}_{channel}_2k.{ext}'
        if name not in fabric_images:
            im=bpy.data.images.load(str(ROOT/'textures/fabrics'/name),check_existing=True)
            im.colorspace_settings.name='sRGB' if channel=='diff' else 'Non-Color';im.pack();fabric_images[name]=im
        tex=nodes.new('ShaderNodeTexImage');tex.image=fabric_images[name]
        tex.projection='BOX';tex.projection_blend=.18
        links.new(mapping.outputs['Vector'],tex.inputs['Vector']);maps[channel]=tex
    gray=nodes.new('ShaderNodeRGBToBW');links.new(maps['diff'].outputs['Color'],gray.inputs[0])
    variation=nodes.new('ShaderNodeMapRange');variation.inputs['From Min'].default_value=.10;variation.inputs['From Max'].default_value=.80
    variation.inputs['To Min'].default_value=.80;variation.inputs['To Max'].default_value=1.10
    links.new(gray.outputs[0],variation.inputs['Value'])
    dye=nodes.new('ShaderNodeMixRGB');dye.blend_type='MULTIPLY';dye.inputs[0].default_value=1;dye.inputs[1].default_value=material.diffuse_color
    links.new(variation.outputs[0],dye.inputs[2]);links.new(dye.outputs[0],bs.inputs['Base Color'])
    rough=nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.64;rough.inputs['To Max'].default_value=.91
    if material==jacket:
        rough.inputs['To Min'].default_value=.46;rough.inputs['To Max'].default_value=.72
        bs.inputs['Specular IOR Level'].default_value=.32
    links.new(maps['rough'].outputs['Color'],rough.inputs['Value']);links.new(rough.outputs[0],bs.inputs['Roughness'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=.0007
    links.new(maps['disp'].outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Sheen Weight'].default_value=.16;bs.inputs['Sheen Roughness'].default_value=.75
scene['photographic_fabric_maps']=True
