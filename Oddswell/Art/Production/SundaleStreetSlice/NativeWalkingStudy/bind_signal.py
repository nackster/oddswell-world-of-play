"""Keep the OddsWell signal shader on the garment's authored rest coordinates."""
import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'NativeWalk.blend'));scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];name='Walk rest surface coordinate'
attribute=coat.data.attributes.get(name) or coat.data.attributes.new(name=name,type='FLOAT_VECTOR',domain='POINT')
for v,a in zip(coat.data.vertices,attribute.data):a.vector=coat.matrix_world@v.co
material=coat.data.materials[0];tree=material.node_tree
links=[l for l in tree.links if l.from_node.type=='NEW_GEOMETRY' and l.from_socket.name=='Position']
assert links,'No geometric signal coordinate found'
node=tree.nodes.new('ShaderNodeAttribute');node.name='Native walking signal rest coordinates';node.attribute_name=name
for link in links:tree.links.new(node.outputs['Vector'],link.to_socket)
(out/'signal-bind-report.json').write_text(json.dumps({'material':material.name,'rest_attribute':name,'replaced_position_links':len(links),'reason':'The old world-space signal mask stayed in the street when the skinned jacket moved.'},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'NativeWalk.blend'),compress=True)
print('WALK_SIGNAL_BOUND',len(links),flush=True)
