"""Adapt the retained CC0 tree's native growth nodes into shared scene geometry.

The original Rico Cilliers model is unmodified on disk. These adjustments are
the OddsWell scene derivative: denser leaves, restrained color variation,
different planting proportions and orientation. See jacaranda-source.json.
"""
TREE_MESHES=[]

def tree(x,y,scale=1):
    if not TREE_MESHES:
        with bpy.data.libraries.load(str(ROOT/'source-assets/jacaranda_tree_4k.blend'),link=False) as (source,target):
            target.objects=['jacaranda_tree_geometry_nodes']
        source=target.objects[0]
        scene.collection.objects.link(source);source.location=(0,0,0)
        original=[dict(modifier.items()) for modifier in source.modifiers]
        # Three retained growth variants: broad hero, upright and spreading.
        # Leaf placement is regenerated; upper branches receive a gentle lean.
        import numpy as np
        for variant,(density,leaf_size,proportions) in enumerate([
            (1.5,1.18,(1,1,1)),(1.35,1.05,(.88,.94,1.12)),(1.45,1.22,(1.10,1.03,.90)),
        ]):
            for modifier,values in zip(source.modifiers,original):
                modifier['Input_3']=values['Input_3']+variant*127
                modifier['Input_4']=values['Input_4']*density
                modifier['Input_5']=values['Input_5']*leaf_size
                modifier['Input_6']=values['Input_6']*leaf_size
            source.update_tag();bpy.context.view_layer.update()
            depsgraph=bpy.context.evaluated_depsgraph_get()
            surface=bpy.data.meshes.new_from_object(source.evaluated_get(depsgraph),preserve_all_data_layers=True,depsgraph=depsgraph)
            surface.name='OW | mature jacaranda growth %d'%variant
            if variant:
                coordinates=np.empty(len(surface.vertices)*3,dtype=np.float32)
                surface.vertices.foreach_get('co',coordinates)
                coordinates=coordinates.reshape((-1,3));upper=np.maximum(0,coordinates[:,2]-5)
                coordinates[:,0]+=(.020 if variant==1 else -.015)*upper**1.4
                coordinates*=np.array(proportions,dtype=np.float32)
                surface.vertices.foreach_set('co',coordinates.ravel());surface.update()
            TREE_MESHES.append(surface)
        bpy.data.objects.remove(source,do_unlink=True)
        for image in bpy.data.images:
            if not image.name.startswith('jacaranda_tree_'):continue
            stem=image.name.rsplit('.',1)[0];ext='png' if 'alpha' in stem else 'jpg'
            image.filepath=str(ROOT/'textures/jacaranda'/(stem+'_2k.'+ext));image.reload();image.pack()
        material=bpy.data.materials['jacaranda_tree_leaves']
        group=next(node for node in material.node_tree.nodes if node.type=='GROUP')
        for name,value in [('Value',1.6),('Saturation',.9),('Translucency',.55),('Darken variation',.4),('Darken amount',.05)]:
            group.inputs[name].default_value=value
    hero=abs(x+2.4)<.01 and abs(y-7.5)<.01
    variant=0 if hero else int(abs(x*13+y*7))%3
    obj=bpy.data.objects.new('Tree | mature Sundale jacaranda',TREE_MESHES[variant])
    scene.collection.objects.link(obj)
    obj.location=(x,y,.34);obj.scale=(scale*.34,scale*.34,scale*.30)
    obj.rotation_euler.z=-.6 if hero else random.Random(int((x+30)*173+y*139)).uniform(0,math.tau)
    obj['source']='Poly Haven / Rico Cilliers / CC0'
    obj['growth_variant']=variant
    obj['growth_density_multiplier']=(1.5,1.35,1.45)[variant];obj['leaf_size_multiplier']=(1.18,1.05,1.22)[variant]
    box('Tree pit stone surround',(x,y,.16),(1.6*scale,1.6*scale,.32),stone,.03)
    box('Tree pit soil',(x,y,.329),(1.33*scale,1.33*scale,.012),soil)
    return obj
