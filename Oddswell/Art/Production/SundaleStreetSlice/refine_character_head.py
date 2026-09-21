"""Retained anatomical head with fitted eyes and restrained skin variation.

Executed by build_scene.py after tailoring; the original CC0 source is intact.
"""
import bmesh

head=bpy.data.objects['Character | anatomical head']
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
white=mat('Character | warm sclera',(.55,.52,.43),.28)
iris=mat('Character | hazel iris',(.045,.025,.011),.40,750)
pupil=mat('Character | pupil',(.002,.0025,.002),.18)
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
        for k in range(1,7):
            r=size*k/6
            for j in range(64):
                a=j*math.tau/64
                verts.append(bodypt(center+Vector((r*math.cos(a),math.sqrt(radius*radius-r*r)+offset,r*math.sin(a)))))
        faces.extend((0,1+j,1+(j+1)%64) for j in range(64))
        for k in range(5):
            start=1+k*64
            faces.extend((start+j,start+(j+1)%64,start+64+(j+1)%64,start+64+j) for j in range(64))
        mesh('Character | '+name+' '+side,verts,[tuple(reversed(face)) for face in faces],material,True)

# Short, tapered strands follow the actual brow surface, keeping the face
# readable without drawing a solid painted stripe above each eye.
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
hair=mat('Character | dark brown brow hair',(.025,.013,.008),.82)
rng=random.Random(518)
for sign in (-1,1):
    data=bpy.data.curves.new('Character | eyebrow strands','CURVE');data.dimensions='3D';data.bevel_depth=.000075;data.bevel_resolution=2
    for i in range(350):
        t=rng.random();x=sign*(.014+.044*t)
        z=1.682+.004*math.sin(t*math.pi)-.002*t+rng.uniform(-.0018,.0018)
        length=rng.uniform(.0025,.004)
        points=[]
        for k in range(4):
            u=k/3;px=x+sign*.0016*u;pz=z+length*(1-.45*t)*u
            hit,normal,_,_=surface.ray_cast(bodypt((px,.30,pz)),Vector((0,-1,0)),.30)
            assert hit is not None,'Eyebrow strand missed face'
            points.append(hit+normal*.00025)
        spline=data.splines.new('POLY');spline.points.add(3)
        for k,(point,position) in enumerate(zip(spline.points,points)):
            point.co=(*position,1);point.radius=1-k*.27
    brow=bpy.data.objects.new('Character | eyebrow '+str(sign),data);scene.collection.objects.link(brow);data.materials.append(hair)

face_skin=skin.copy();face_skin.name='Character | anatomical face skin'
head.data.materials[0]=face_skin
nodes,links=face_skin.node_tree.nodes,face_skin.node_tree.links
bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.56
bs.inputs['Subsurface Weight'].default_value=.10
bs.inputs['Subsurface Radius'].default_value=(1,.45,.22)
bs.inputs['Subsurface Scale'].default_value=.004
color=head.data.color_attributes.new(name='Natural face tint',type='FLOAT_COLOR',domain='POINT')
for vertex in head.data.vertices:
    x,y,z=vertex.co-origin
    lips=math.exp(-((x/.023)**4+((z-1.599)/.009)**4))*min(1,max(0,(y-.151)/.012))
    cheeks=math.exp(-((abs(x)-.045)/.023)**2-((z-1.63)/.025)**2)*min(1,max(0,(y-.10)/.045))
    base=Vector(skin.diffuse_color[:3])
    base=base.lerp(Vector((.30,.12,.083)),lips*.65)
    base=base.lerp(Vector((.40,.21,.14)),cheeks*.20)
    color.data[vertex.index].color=(*base,1)
attribute=nodes.new('ShaderNodeVertexColor');attribute.layer_name=color.name
links.new(attribute.outputs['Color'],bs.inputs['Base Color'])
scene['human_head_refinement']=True
