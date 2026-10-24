"""Rebuild the continuous OddsWell signal stripe on the saved jacket."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'Sundale_Directional_Lighting_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='E440EA5F632724BFD584E78E1749CBD6ACB896A22DF6137264E418D70021AE41'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
for obj in scene.objects:
    if obj.type=='MESH' and obj.name.startswith('Character | ') and 'yoke' in obj.name:
        obj.hide_render=True
        obj.hide_set(True)
    if obj.name.startswith('Character | yoke topstitch '):obj.hide_render=True
    if obj.name.startswith('Character | yoke topstitch '):obj.hide_set(True)

material=coat.data.materials[0].copy()
material.name='Character | slate weave with continuous teal signal'
coat.data.materials[0]=material
nodes=material.node_tree.nodes
links=material.node_tree.links
bs=nodes.get('Principled BSDF')
original=bs.inputs['Base Color'].links[0].from_socket
position=nodes.new('ShaderNodeNewGeometry')
axes=nodes.new('ShaderNodeSeparateXYZ')
links.new(position.outputs['Position'],axes.inputs[0])
x,y,z=(axes.outputs[key] for key in ('X','Y','Z'))

def math_node(op,a,b=None):
    node=nodes.new('ShaderNodeMath');node.operation=op
    for i,value in enumerate((a,b)):
        if value is None:continue
        if isinstance(value,(int,float)):node.inputs[i].default_value=value
        else:links.new(value,node.inputs[i])
    return node.outputs[0]

def product(*items):
    result=items[0]
    for item in items[1:]:result=math_node('MULTIPLY',result,item)
    return result

outboard=math_node('ABSOLUTE',math_node('ADD',x,.75))
shoulder=math_node('MINIMUM',1,math_node('MAXIMUM',0,
             math_node('DIVIDE',math_node('SUBTRACT',outboard,.06),.13)))
rear_height=math_node('ADD',z,math_node('MULTIPLY',shoulder,.020))
rear=product(math_node('LESS_THAN',y,-2.403),math_node('GREATER_THAN',rear_height,1.3047),
             math_node('LESS_THAN',rear_height,1.3437),math_node('GREATER_THAN',x,-.927),
             math_node('LESS_THAN',x,-.573))
side=math_node('MAXIMUM',math_node('LESS_THAN',x,-.890),math_node('GREATER_THAN',x,-.610))
zdelta=math_node('SUBTRACT',math_node('ADD',z,math_node('MULTIPLY',y,.31)),.5614)
sleeve=product(side,math_node('GREATER_THAN',y,-2.423),math_node('LESS_THAN',y,-2.325),
               math_node('LESS_THAN',math_node('ABSOLUTE',zdelta),.017))
mask=math_node('MAXIMUM',rear,sleeve)
mix=nodes.new('ShaderNodeMixRGB')
mix.blend_type='MIX'
links.new(mask,mix.inputs[0])
links.new(original,mix.inputs[1])
mix.inputs[2].default_value=(.026,.22,.21,1)
links.new(mix.outputs[0],bs.inputs['Base Color'])
scene['continuous_signal_material_candidate']=True

out=root
for label,place,target,lens,width,height in (
    ('Profile',(-2.55,-2.4,1.25),(-.75,-2.4,1.0),55,1000,1100),
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100),
    ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100)):
    data=bpy.data.cameras.new('Signal review '+label)
    camera=bpy.data.objects.new('Signal review '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.cycles.samples=64
    scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Signal_Stripe_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene.cycles.samples=64
scene.render.resolution_x=1600
scene.render.resolution_y=900
scene.render.filepath=str(out/'Signal_Stripe_Gameplay.png')
bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'OddsWell_Signal_Stripe_Candidate.blend'),compress=True)
print('ODDSWELL_SIGNAL_STRIPE_CANDIDATE_PASS',flush=True)
