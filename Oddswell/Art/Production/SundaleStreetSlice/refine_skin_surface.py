"""Editable skin relief and nail-fold geometry over the retained source texture."""
import bpy,math,json,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

def refine_skin_surface():
    scene=bpy.context.scene
    assert not scene.get('epidermal_detail'),'Apply once to the retained skin materials'
    for name in ('Character | anatomical face skin','Character | warm neutral skin'):
        material=bpy.data.materials[name];nodes,links=material.node_tree.nodes,material.node_tree.links
        bs=nodes.get('Principled BSDF');coords=next(n for n in nodes if n.type=='TEX_COORD')
        prior=bs.inputs['Normal'].links[0].from_socket
        pores=nodes.new('ShaderNodeTexVoronoi');pores.name='Microscopic pore distribution';pores.distance='EUCLIDEAN';pores.inputs['Scale'].default_value=1900
        links.new(coords.outputs['Object'],pores.inputs['Vector'])
        shape=nodes.new('ShaderNodeMapRange');shape.name='Individual pore depressions';shape.inputs['From Min'].default_value=.025;shape.inputs['From Max'].default_value=.23;shape.inputs['To Min'].default_value=1;shape.inputs['To Max'].default_value=0
        links.new(pores.outputs['Distance'],shape.inputs['Value'])
        bump=nodes.new('ShaderNodeBump');bump.name='Fine epidermal pore relief';bump.invert=True;bump.inputs['Distance'].default_value=.000055;bump.inputs['Strength'].default_value=.65
        links.new(shape.outputs[0],bump.inputs['Height']);links.new(prior,bump.inputs['Normal']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
        bs.inputs['Specular IOR Level'].default_value=.32
        if 'face' in name:bs.inputs['Subsurface Weight'].default_value=.38
    material=bpy.data.materials['Character | warm neutral skin'].copy();material.name='Character | hand epidermis'
    nodes,links=material.node_tree.nodes,material.node_tree.links;bs=nodes.get('Principled BSDF')
    bs.inputs['Subsurface Weight'].default_value=.30
    crease=nodes.new('ShaderNodeAttribute');crease.attribute_name='Hand joint creases'
    bump=nodes.new('ShaderNodeBump');bump.name='Anatomical hand crease relief';bump.invert=True;bump.inputs['Distance'].default_value=.00020;bump.inputs['Strength'].default_value=.7
    links.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal']);links.new(crease.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    joint=nodes.new('ShaderNodeAttribute');joint.attribute_name='Hand joint vascular tone'
    amount=nodes.new('ShaderNodeMath');amount.operation='MULTIPLY';amount.inputs[1].default_value=.20;links.new(joint.outputs['Fac'],amount.inputs[0])
    tone=nodes.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[2].default_value=(1,.73,.67,1)
    links.new(bs.inputs['Base Color'].links[0].from_socket,tone.inputs[1]);links.new(amount.outputs[0],tone.inputs[0]);links.new(tone.outputs[0],bs.inputs['Base Color'])
    vessel=nodes.new('ShaderNodeAttribute');vessel.attribute_name='Dorsal vascular field'
    amount=nodes.new('ShaderNodeMath');amount.operation='MULTIPLY';amount.inputs[1].default_value=.16;links.new(vessel.outputs['Fac'],amount.inputs[0])
    tone=nodes.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[2].default_value=(.74,.88,.86,1)
    links.new(bs.inputs['Base Color'].links[0].from_socket,tone.inputs[1]);links.new(amount.outputs[0],tone.inputs[0]);links.new(tone.outputs[0],bs.inputs['Base Color'])
    for side in ('left','right'):
        hand=bpy.data.objects['Character | anatomical '+side+' hand'];hand.data.materials[0]=material
        landmarks=json.loads(hand['hand_landmarks']);dorsal=Vector(landmarks['dorsal']);wrist=Vector(landmarks['wrist'])
        digits={int(k):[Vector(p) for p in chain] for k,chain in landmarks['digits'].items()}
        vein=hand.data.attributes.new('Dorsal vascular field','FLOAT','POINT')
        shape=hand.shape_key_add(name='Dorsal vascular relief');shape.value=1
        across=(digits[5][0]-digits[2][0]).normalized();axis=digits[3][0]-wrist
        paths=[]
        for digit,offset in ((3,-.005),(4,.006)):
            start=wrist+axis*.12+across*offset;end=wrist.lerp(digits[digit][0],.90)
            middle=start.lerp(end,.53)+across*(.004 if digit==3 else -.003)
            paths.append([start*(1-t)**2+middle*2*t*(1-t)+end*t*t for t in [i/24 for i in range(25)]])
        for vertex,source,datum in zip(hand.data.vertices,hand.data.attributes['Unposed anatomical position'].data,vein.data):
            p=source.vector;strength=0
            for path in paths:
                for i,(a,b) in enumerate(zip(path,path[1:])):
                    direction=b-a;t=max(0,min(1,(p-a).dot(direction)/direction.length_squared));q=a.lerp(b,t)
                    depth=(p-q).dot(dorsal);lateral=(p-q-dorsal*depth).length
                    if depth>.002:strength=max(strength,math.exp(-(lateral/.00125)**2)*math.sin(math.pi*(i+t)/24)**.7)
            datum.value=strength
            shape.data[vertex.index].co=vertex.co+vertex.normal*(.00022*strength)
        crease=hand.data.attributes.new('Hand joint creases','FLOAT','POINT');vascular=hand.data.attributes.new('Hand joint vascular tone','FLOAT','POINT')
        for value,tone,p in zip(crease.data,vascular.data,hand.data.attributes['Unposed anatomical position'].data):
            p=p.vector;relief=0;red=0
            for digit,chain in digits.items():
                for j,center in enumerate(chain[:3]):
                    axis=(chain[j+1]-center).normalized();offset=p-center
                    along=offset.dot(axis);out=offset.dot(dorsal);across=(offset-axis*along-dorsal*out).length
                    width=.006 if j==0 else .0045
                    front=max(0,min(1,(out+.001)/.003))
                    for shift,weight in ((-.0014,.6),(0,1),(.0014,.55)):
                        relief+=weight*math.exp(-((along-shift-.00045*math.sin(across*500))/.00045)**2-(across/width)**4)*front
                    red+=math.exp(-(along/.005)**2-(across/(width*1.25))**4)*front
            value.value=min(1,relief);tone.value=min(1,red)
        bpy.context.view_layer.update();evaluated=hand.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
        triangles=list(mesh.loop_triangles);surface=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(t.vertices) for t in triangles],all_triangles=True)
        uv=mesh.uv_layers['MakeHuman source UV'].data
        for digit in range(1,6):
            nail=bpy.data.objects[f'Character | nail {side} {digit}'];points=[];normals=[]
            # The proximal half of the registered plate is the nail-fold arc.
            for j in range(49,96):
                p=nail.data.vertices[1+23*96+j].co;hit,n,_,distance=surface.find_nearest(p)
                points.append(hit+n*.000045);normals.append(n)
            vertices=[];faces=[];count=len(points);sides=8
            for i,(p,n) in enumerate(zip(points,normals)):
                tangent=(points[min(count-1,i+1)]-points[max(0,i-1)]).normalized();across=tangent.cross(n).normalized()
                radius=.00014*(.15+.85*math.sin(math.pi*i/(count-1))**.45)
                for k in range(sides):vertices.append(p+radius*(n*math.cos(k*math.tau/sides)+across*math.sin(k*math.tau/sides)))
            for i in range(count-1):
                for k in range(sides):faces.append((i*sides+k,i*sides+(k+1)%sides,(i+1)*sides+(k+1)%sides,(i+1)*sides+k))
            faces.extend((tuple(reversed(range(sides))),tuple((count-1)*sides+k for k in range(sides))))
            data=bpy.data.meshes.new(f'Character | nail fold {side} {digit}');data.from_pydata(vertices,[],faces)
            bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
            layer=data.uv_layers.new(name='MakeHuman source UV')
            for polygon in data.polygons:
                polygon.use_smooth=True
                for loop in polygon.loop_indices:
                    p=data.vertices[data.loops[loop].vertex_index].co;hit,n,index,distance=surface.find_nearest(p);tri=triangles[index]
                    a,b,c=[mesh.vertices[i].co for i in tri.vertices]
                    mapped=barycentric_transform(hit,a,b,c,*[Vector((*uv[i].uv,0)) for i in tri.loops]);layer.data[loop].uv=mapped.xy
            # Share the source-textured body material; hand-only attributes are absent.
            data.materials.append(bpy.data.materials['Character | warm neutral skin'])
            obj=bpy.data.objects.new(data.name,data);hand.users_collection[0].objects.link(obj);obj.matrix_world=hand.matrix_world.copy();obj['anatomical_digit']=digit;obj['hand_side']=side
        evaluated.to_mesh_clear()
    scene['epidermal_detail']=True
    print('ODDSWELL_EPIDERMAL_DETAIL_PASS',flush=True)

refine_skin_surface()
