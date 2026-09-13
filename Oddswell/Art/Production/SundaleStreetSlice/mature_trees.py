"""Adapt the retained CC0 tree's native growth nodes into shared scene geometry.

The original Rico Cilliers model is unmodified on disk. These adjustments are
the OddsWell scene derivative: denser leaves, restrained color variation,
different planting proportions and orientation. See jacaranda-source.json.
"""
TREE_MESH=None

def tree(x,y,scale=1):
    global TREE_MESH
    if TREE_MESH is None:
        with bpy.data.libraries.load(str(ROOT/'source-assets/jacaranda_tree_4k.blend'),link=False) as (source,target):
            target.objects=['jacaranda_tree_geometry_nodes']
        source=target.objects[0]
        scene.collection.objects.link(source);source.location=(0,0,0)
        for modifier in source.modifiers:
            modifier['Input_4']*=1.5
            modifier['Input_5']*=1.18;modifier['Input_6']*=1.18
        bpy.context.view_layer.update()
        depsgraph=bpy.context.evaluated_depsgraph_get()
        TREE_MESH=bpy.data.meshes.new_from_object(source.evaluated_get(depsgraph),preserve_all_data_layers=True,depsgraph=depsgraph)
        TREE_MESH.name='OW | mature jacaranda shared surface'
        bpy.data.objects.remove(source,do_unlink=True)
        for image in bpy.data.images:
            if not image.name.startswith('jacaranda_tree_'):continue
            stem=image.name.rsplit('.',1)[0];ext='png' if 'alpha' in stem else 'jpg'
            image.filepath=str(ROOT/'textures/jacaranda'/(stem+'_2k.'+ext));image.reload();image.pack()
        material=bpy.data.materials['jacaranda_tree_leaves']
        group=next(node for node in material.node_tree.nodes if node.type=='GROUP')
        for name,value in [('Value',1.6),('Saturation',.9),('Translucency',.55),('Darken variation',.4),('Darken amount',.05)]:
            group.inputs[name].default_value=value
    obj=bpy.data.objects.new('Tree | mature Sundale jacaranda',TREE_MESH)
    scene.collection.objects.link(obj)
    obj.location=(x,y,.34);obj.scale=(scale*.34,scale*.34,scale*.30)
    obj.rotation_euler.z=-.6 if abs(x+2.4)<.01 and abs(y-7.5)<.01 else random.Random(int((x+30)*173+y*139)).uniform(0,math.tau)
    obj['source']='Poly Haven / Rico Cilliers / CC0'
    obj['growth_density_multiplier']=1.5;obj['leaf_size_multiplier']=1.18
    box('Tree pit stone surround',(x,y,.16),(1.6*scale,1.6*scale,.32),stone,.03)
    box('Tree pit soil',(x,y,.329),(1.33*scale,1.33*scale,.012),soil)
    return obj
