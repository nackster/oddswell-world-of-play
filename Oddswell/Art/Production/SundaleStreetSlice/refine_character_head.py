"""Retained anatomical head with fitted eyes and restrained skin variation.

Executed by build_scene.py after tailoring; the original CC0 source is intact.
"""
import bmesh

head=bpy.data.objects['Character | anatomical head']
for vertex in head.data.vertices:
    p=vertex.co-origin
    if p.y>.08:
        p.x*=1+.065*math.exp(-((p.z-1.575)/.035)**2)
        vertex.co=p+origin
bm=bmesh.new();bm.from_mesh(head.data)
# Cut away source shoulder fragments and extend a fitted neck skirt beneath
# the collar. Capping the original uneven crop left visible skin flanges.
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=bodypt((0,0,1.525)),plane_no=(0,0,1),clear_inner=True)
neck_edges=[e for e in bm.edges if e.is_boundary and all(v.co.z<origin.z+1.526 for v in e.verts)]
assert neck_edges,'Missing neck cut boundary'
skirt=bmesh.ops.extrude_edge_only(bm,edges=neck_edges)
skirt_vertices=[v for v in skirt['geom'] if isinstance(v,bmesh.types.BMVert)]
bmesh.ops.translate(bm,verts=skirt_vertices,vec=(0,0,-.035))
for vertex in bm.verts:
    p=vertex.co-origin
    if p.z>=1.545:continue
    weight=min(1,(1.545-p.z)/.020)
    radius=math.sqrt((p.x/.056)**2+((p.y-.012)/.056)**2)
    if radius>1:
        factor=1-weight+weight/radius
        p.x*=factor;p.y=.012+(p.y-.012)*factor;vertex.co=p+origin
bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary and all(v.co.z<origin.z+1.50 for v in e.verts)],sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(head.data);bm.free();head.data.update()
head['anatomical_source']='MakeHuman hm08 body; neck cut capped beneath collar'

# The native eyelid openings sit over spherical eyes placed at the retained
# source joints. Iris and pupil are curved patches on the same eye radius.
white=mat('Character | warm sclera',(.60,.58,.53),.18)
iris=mat('Character | hazel iris',(.055,.035,.017),.27,750)
pupil=mat('Character | pupil',(.002,.0025,.002),.12)
for node in iris.node_tree.nodes:
    if node.type=='BUMP':node.inputs['Distance'].default_value=.00002;node.inputs['Strength'].default_value=.12
for material in (white,iris,pupil):
    eye_bs=material.node_tree.nodes.get('Principled BSDF')
    eye_bs.inputs['Coat Weight'].default_value=.35
    eye_bs.inputs['Coat Roughness'].default_value=.07
white.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.045
white.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Scale'].default_value=.002
fibers=iris.node_tree.nodes.new('ShaderNodeVertexColor');fibers.layer_name='Iris radial fibers'
iris.node_tree.links.new(fibers.outputs['Color'],iris.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
for side in ('l','r'):
    center=joint('joint-'+side+'-eye');radius=.0158
    eye=sphere('Character | eye '+side,bodypt(center),(radius,)*3,white,48,32)
    bm=bmesh.new();bm.from_mesh(eye.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(eye.data);bm.free()
    for name,size,material in (('iris',.006,iris),('pupil',.0024,pupil)):
        offset=.00025 if name=='pupil' else .00012
        verts=[bodypt(center+Vector((0,radius+offset,0)))];faces=[]
        rings=14 if name=='iris' else 6;segments=256 if name=='iris' else 64
        colors=[(.015,.010,.005,1)]
        for k in range(1,rings+1):
            r=size*k/rings
            for j in range(segments):
                a=j*math.tau/segments
                verts.append(bodypt(center+Vector((r*math.cos(a),math.sqrt(radius*radius-r*r)+offset,r*math.sin(a)))))
                t=k/rings
                fiber=.65+.19*math.sin(a*71+.7*math.sin(t*12))+.13*math.sin(a*113+t*5)
                limbus=1-.68*max(0,min(1,(t-.79)/.21))
                inner=math.exp(-((t-.46)/.11)**2)
                colors.append(((.105+.025*inner)*fiber*limbus,(.070-.015*inner)*fiber*limbus,.025*fiber*limbus,1))
        faces.extend((0,1+j,1+(j+1)%segments) for j in range(segments))
        for k in range(rings-1):
            start=1+k*segments
            faces.extend((start+j,start+(j+1)%segments,start+segments+(j+1)%segments,start+segments+j) for j in range(segments))
        eye_part=mesh('Character | '+name+' '+side,verts,[tuple(reversed(face)) for face in faces],material,True)
        if name=='iris':
            attribute=eye_part.data.color_attributes.new(name='Iris radial fibers',type='FLOAT_COLOR',domain='POINT')
            for datum,color in zip(attribute.data,colors):datum.color=color

# Short, tapered strands follow the actual brow surface, keeping the face
# readable without drawing a solid painted stripe above each eye.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
hair=mat('Character | dark brown brow hair',(.025,.013,.008),.82)
rng=random.Random(518)
for sign in (-1,1):
    data=bpy.data.curves.new('Character | eyebrow strands','CURVE');data.dimensions='3D';data.bevel_depth=.000045;data.bevel_resolution=2
    for i in range(500):
        t=rng.random();x=sign*(.014+.044*t)
        spread=.0016*(1-.65*t)
        z=1.682+.004*math.sin(t*math.pi)-.002*t+rng.uniform(-spread,spread)
        length=rng.uniform(.0035,.0055)
        points=[]
        for k in range(4):
            u=k/3;px=x+sign*length*(.20+.75*t)*u;pz=z+length*(.80-t)*u
            hit,normal,_,_=surface.ray_cast(bodypt((px,.30,pz)),Vector((0,-1,0)),.30)
            assert hit is not None,'Eyebrow strand missed face'
            points.append(hit+normal*.00025)
        spline=data.splines.new('POLY');spline.points.add(3)
        for k,(point,position) in enumerate(zip(spline.points,points)):
            point.co=(*position,1);point.radius=(1-k/3)*.97+.03
    brow=bpy.data.objects.new('Character | eyebrow '+str(sign),data);scene.collection.objects.link(brow);data.materials.append(hair)

face_skin=skin.copy();face_skin.name='Character | anatomical face skin'
head.data.materials[0]=face_skin
nodes,links=face_skin.node_tree.nodes,face_skin.node_tree.links
bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.56
bs.inputs['Subsurface Weight'].default_value=.10
bs.inputs['Subsurface Radius'].default_value=(1,.45,.22)
bs.inputs['Subsurface Scale'].default_value=.004
# Preserve the original skin map and use its matching source UVs on every
# exposed anatomical region. Pigment, nails and scalp detail stay registered.
image=bpy.data.images.load(str(ROOT/'textures/makehuman-skin/young_lightskinned_male_diffuse.png'))
image.colorspace_settings.name='sRGB';image.pack()
for material in (skin,face_skin):
    nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes.get('Principled BSDF')
    coords=next(node for node in nodes if node.type=='TEX_COORD')
    texture=nodes.new('ShaderNodeTexImage');texture.name='CC0 MakeHuman skin';texture.image=image
    links.new(coords.outputs['UV'],texture.inputs['Vector'])
    tint=nodes.new('ShaderNodeHueSaturation');tint.inputs['Saturation'].default_value=.85;tint.inputs['Value'].default_value=.85
    links.new(texture.outputs['Color'],tint.inputs['Color']);links.new(tint.outputs['Color'],bs.inputs['Base Color'])
    roughness=nodes.new('ShaderNodeTexNoise');roughness.inputs['Scale'].default_value=85;roughness.inputs['Detail'].default_value=3
    links.new(coords.outputs['Object'],roughness.inputs['Vector'])
    rough=nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.44;rough.inputs['To Max'].default_value=.62
    links.new(roughness.outputs['Fac'],rough.inputs['Value']);links.new(rough.outputs[0],bs.inputs['Roughness'])
    bs.inputs['Subsurface Weight'].default_value=.10;bs.inputs['Subsurface Scale'].default_value=.004
scene['human_head_refinement']=True
scene['source_skin_uvs']=True
