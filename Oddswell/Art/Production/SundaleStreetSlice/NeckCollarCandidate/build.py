"""Shape a lower fitted collar and refine the retained woven-cloth response."""
import bpy,bmesh,ast,math,hashlib,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists() and (p/'Oddswell').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/RaglanPatternCandidate/RaglanPattern.blend'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='D646E3AAF1C312AF61EA03D9C2AD4A28C6074BA6B84245B6D1E31DDA9134E587'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;control=bpy.data.objects['Body flow | stance blend']
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
parsed=ast.parse((source.parent.parent/'BodyFlowCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']
parsed=ast.parse((source.parent/'build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('unwarp','drive','update_points')],type_ignores=[]),'raglan-points','exec'))
collar=bpy.data.objects['Character | standing collar']
head=bpy.data.objects['Character | anatomical head']
world,inverse=collar.matrix_world,collar.matrix_world.inverted()
original=[world@v.co for v in collar.data.vertices]
bm=bmesh.new();bm.from_mesh(collar.data)
unseen={v for e in bm.edges if e.is_boundary for v in e.verts};loops=[]
while unseen:
    pending=[unseen.pop()];ids=[]
    while pending:
        v=pending.pop();ids.append(v.index)
        for e in v.link_edges:
            q=e.other_vert(v)
            if e.is_boundary and q in unseen:unseen.remove(q);pending.append(q)
    loops.append(ids)
bm.free();assert len(loops)==2
bottom,top=sorted(loops,key=lambda ids:sum(original[i].z for i in ids)/len(ids))
center=sum((original[i] for i in bottom),Vector())/len(bottom)
def angle(p):return math.atan2(p.y-center.y,p.x-center.x)%math.tau
# Continue the existing neck below the shorter stand; the original rounded closure
# otherwise becomes the nearest surface and pulls the collar into its artificial cap.
head_modifiers=[(m,m.show_viewport) for m in head.modifiers]
for m,_ in head_modifiers:m.show_viewport=False
bpy.context.view_layer.update()
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());head_control=ev.to_mesh()
assert len(head_control.vertices)==len(head.data.vertices)
head_world=[head.matrix_world@v.co for v in head_control.vertices]
ev.to_mesh_clear()
head_original=head.data.attributes.new(name='Before lower neck continuation',type='FLOAT_VECTOR',domain='POINT')
for value,p in zip(head_original.data,head_world):value.vector=head.matrix_world.inverted()@p
neck_key=head.shape_key_add(name='Continuous lower neck',from_mix=False)
maximum_neck_extension=0
for point,p in zip(neck_key.data,head_world):
    extension=.025*smooth((1.499-p.z)/.033)
    point.co+=head.matrix_world.inverted().to_3x3()@Vector((0,0,-extension))
    maximum_neck_extension=max(maximum_neck_extension,extension)
neck_key.value=1
for m,visible in head_modifiers:m.show_viewport=visible
bpy.context.view_layer.update()
tree=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
head_inverse=head.matrix_world.inverted()
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());neck_mesh=ev.to_mesh()
neck_points=[head.matrix_world@v.co for v in neck_mesh.vertices]
section=[];neck_z=1.48
for edge in neck_mesh.edges:
    a,b=[neck_points[i] for i in edge.vertices]
    if (a.z-neck_z)*(b.z-neck_z)<0:section.append(a.lerp(b,(neck_z-a.z)/(b.z-a.z)))
assert section,'Missing anatomical neck section'
neck_center=Vector(((min(p.x for p in section)+max(p.x for p in section))*.5,(min(p.y for p in section)+max(p.y for p in section))*.5,neck_z))
ev.to_mesh_clear()
positions=[];maximum_inset=0
columns=len(bottom);rows=len(original)//columns-1
assert sorted(bottom)==list(range(columns)) and sorted(top)==list(range(rows*columns,(rows+1)*columns)),'Changed collar strip layout'
fitted_top=[]
for j in range(columns):
    b,t=original[j],original[rows*columns+j]
    theta=angle(b);radial=Vector((math.cos(theta),math.sin(theta),0))
    q=t.copy();q.z=b.z+(t.z-b.z)*.58
    start=Vector((neck_center.x,neck_center.y,q.z))
    hit,normal,_,distance=tree.ray_cast(head_inverse@start,(head_inverse.to_3x3()@radial).normalized())
    assert hit is not None and normal.dot(head_inverse.to_3x3()@radial)>.5,'Neck ray did not leave skin'
    target=head.matrix_world@hit+radial*.005;target.z=q.z
    q=q.lerp(target,.7)
    maximum_inset=max(maximum_inset,Vector((q.x-t.x,q.y-t.y,0)).length)
    fitted_top.append(q)
for row in range(rows+1):
    fraction=row/rows
    for j in range(columns):
        b,t=original[j],fitted_top[j]
        p=b.lerp(t,smooth(fraction));p.z=b.z+(t.z-b.z)*fraction
        positions.append(p)
attribute=collar.data.attributes.new(name='Before lower fitted collar',type='FLOAT_VECTOR',domain='POINT')
for value,p in zip(attribute.data,original):value.vector=inverse@p
update_points(collar,[inverse@p for p in positions])
retained=collar.shape_key_add(name='Original tall collar')
for point,p in zip(retained.data,original):point.co=inverse@p
retained.value=0
solid=next(m for m in collar.modifiers if m.type=='SOLIDIFY')
solid.solidify_mode='NON_MANIFOLD';solid.nonmanifold_thickness_mode='CONSTRAINTS'
solid.thickness_clamp=1.;solid.use_thickness_angle_clamp=True
coat=bpy.data.objects['Character | tailored slate jacket']
coat_surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
collar_surface=BVHTree.FromObject(collar,bpy.context.evaluated_depsgraph_get())
threshold=max(original[i].z for i in bottom)
def shift_height(p):
    q=p.copy()
    if p.z>threshold:q.z=threshold+(p.z-threshold)*.58
    return q
def nearest_fastening(p,offset):
    q=coat.matrix_world.inverted()@p
    hit,normal,_,distance=min((surface.find_nearest(q) for surface in (coat_surface,collar_surface)),key=lambda item:item[3])
    return coat.matrix_world@(hit+normal*offset)
for obj in list(scene.objects):
    if not obj.name.startswith('Character | '):continue
    if obj.type=='CURVE' and 'front zipper tape' in obj.name:
        values=[obj.matrix_world.inverted()@nearest_fastening(shift_height(obj.matrix_world@Vector(p.co[:3])),.0016) for s in obj.data.splines for p in s.points]
        update_points(obj,values)
    elif obj.type=='MESH' and ('zipper teeth' in obj.name or 'zipper slider' in obj.name):
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        center=sum(points,Vector())/len(points)
        if center.z>threshold:
            delta=nearest_fastening(shift_height(center),.004 if 'slider' in obj.name else .0026)-center
            update_points(obj,[obj.matrix_world.inverted()@(p+delta) for p in points])
    elif obj.type=='CURVE' and 'zipper pull loop' in obj.name:
        points=[obj.matrix_world@Vector(p.co[:3]) for s in obj.data.splines for p in s.points]
        center=sum(points,Vector())/len(points)
        delta=nearest_fastening(shift_height(center),.006)-center
        update_points(obj,[obj.matrix_world.inverted()@(p+delta) for p in points])
material=bpy.data.materials['Character | slate weave with continuous teal signal']
bs=material.node_tree.nodes['Principled BSDF']
bs.inputs['Diffuse Roughness'].default_value=.30
bs.inputs['Specular IOR Level'].default_value=.16
bs.inputs['Sheen Weight'].default_value=.18
bs.inputs['Sheen Roughness'].default_value=.8
rough=material.node_tree.nodes['Map Range.001']
rough.inputs['To Min'].default_value=.78;rough.inputs['To Max'].default_value=.94
knit=bpy.data.materials['Character | dense slate rib knit']
bs=knit.node_tree.nodes['Principled BSDF']
bs.inputs['Diffuse Roughness'].default_value=.25
bs.inputs['Specular IOR Level'].default_value=.18
bs.inputs['Sheen Weight'].default_value=.15
bs.inputs['Sheen Roughness'].default_value=.8
knit.node_tree.nodes['Bump'].inputs['Distance'].default_value=.0005
knit.node_tree.nodes['Bump'].inputs['Strength'].default_value=.18
scene['lower_fitted_collar']=True
scene['collar_height_scale']=.58
scene['collar_maximum_inset_m']=maximum_inset
scene['collar_original_mean_height_m']=sum(original[i].z for i in top)/len(top)-sum(original[i].z for i in bottom)/len(bottom)
scene['collar_new_mean_height_m']=sum(positions[i].z for i in top)/len(top)-sum(positions[i].z for i in bottom)/len(bottom)
scene['collar_fixed_bottom_error_m']=max((original[i]-positions[i]).length for i in bottom)
scene['woven_cloth_diffuse_roughness']=.30
scene['continuous_lower_neck']=True
scene['lower_neck_maximum_extension_m']=maximum_neck_extension
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'NeckCollar.blend'),compress=True)
print('NECK_COLLAR_SAVED',scene['collar_original_mean_height_m'],scene['collar_new_mean_height_m'],maximum_inset,flush=True)
