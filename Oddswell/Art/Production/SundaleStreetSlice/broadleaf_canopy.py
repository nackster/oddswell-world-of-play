"""Fit retained CC0 broad-leaf clusters onto the Sundale branching family."""
with bpy.data.libraries.load(str(ROOT/'source-assets/island_tree_01_2k.blend'),link=False) as (library,loaded):
    loaded.collections=['island_tree_01_leaves_LOD1']
leaf_collection=loaded.collections[0]
scene.collection.children.link(leaf_collection)
for leaf in leaf_collection.objects:
    # Retain the scanned leaf outline and UVs at a modest cluster resolution.
    modifier=leaf.modifiers.new('Sundale leaf cluster simplification','DECIMATE');modifier.ratio=.40
    bpy.context.view_layer.objects.active=leaf
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    for vertex in leaf.data.vertices:vertex.co*=6.0
scene.collection.children.unlink(leaf_collection)
globals()['BROADLEAF_CLUSTERS']=tuple(leaf.data for leaf in leaf_collection.objects)
for modifier in source.modifiers:
    for node in modifier.node_group.nodes:
        if node.type=='COLLECTION_INFO':node.inputs['Collection'].default_value=leaf_collection
for image in bpy.data.images:
    if not image.name.startswith(('island_tree_01_leaves_','island_tree_01_branches_')):continue
    filename=Path(image.filepath).name
    image.filepath=str(ROOT/'textures/broadleaf'/filename);image.reload();image.pack()
for material in bpy.data.materials:
    if not material.name.startswith('island_tree_01_leaves'):continue
    for node in material.node_tree.nodes:
        if node.type=='GROUP':
            for name,value in [('Value',1.7),('Saturation',.85),('Translucency',.9),('Darken variation',.30),('Darken amount',.03)]:
                if node.inputs.get(name):node.inputs[name].default_value=value

# Understory leaves receive less transmitted light than the exposed canopy.
shrub_leaf=bpy.data.materials['island_tree_01_leaves'].copy()
shrub_leaf.name='OW | broadleaf understory'
for node in shrub_leaf.node_tree.nodes:
    if node.type=='GROUP':
        for name,value in [('Value',1.0),('Saturation',.92),('Translucency',.5)]:
            if node.inputs.get(name):node.inputs[name].default_value=value
shrub_clusters=[]
for original in globals()['BROADLEAF_CLUSTERS']:
    surface=original.copy();surface.name='OW | shrub leaf cluster'
    for index,material in enumerate(surface.materials):
        if material and 'island_tree_01_leaves' in material.name:surface.materials[index]=shrub_leaf
    shrub_clusters.append(surface)
globals()['SHRUB_CLUSTERS']=tuple(shrub_clusters)
