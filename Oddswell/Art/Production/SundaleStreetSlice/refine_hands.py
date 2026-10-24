"""Hand surface forms and nail plates registered to retained source landmarks."""
import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

def refine_hands():
    scene=bpy.context.scene
    assert not scene.get('hand_surface_refinement'),'Apply once to the anatomical hand baseline'
    nail=bpy.data.materials.get('Character | translucent keratin') or bpy.data.materials.new('Character | translucent keratin')
    nail.use_nodes=True;bs=nail.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.36;bs.inputs['Coat Weight'].default_value=.20
    bs.inputs['Subsurface Weight'].default_value=.13;bs.inputs['Subsurface Scale'].default_value=.0004
    color=nail.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Nail bed and free edge'
    nail.node_tree.links.new(color.outputs['Color'],bs.inputs['Base Color'])
    for side in ('left','right'):
        hand=bpy.data.objects['Character | anatomical '+side+' hand']
        landmarks=json.loads(hand['hand_landmarks']);wrist=Vector(landmarks['wrist']);dorsal=Vector(landmarks['dorsal'])
        digits={int(k):[Vector(p) for p in chain] for k,chain in landmarks['digits'].items()}
        bpy.context.view_layer.objects.active=hand
        for modifier in list(hand.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        source=[datum.vector.copy() for datum in hand.data.attributes['Unposed anatomical position'].data]
        hand.shape_key_add(name='Basis')
        shape=hand.shape_key_add(name='Hand surface anatomy');shape.value=1
        palm_axis=digits[3][0]-wrist;palm_length=palm_axis.length;palm_axis.normalize()
        palm_across=(digits[5][0]-digits[2][0]).normalized()
        for vertex,p in zip(hand.data.vertices,source):
            delta=0
            for digit,chain in digits.items():
                if digit==1:continue
                end=chain[0];start=wrist+(end-wrist)*.12
                axis=end-start;t=max(0,min(1,(p-start).dot(axis)/axis.length_squared));q=start+axis*t
                back=(p-q).dot(dorsal)
                if back<=.002:continue
                lateral=(p-q-dorsal*back).length
                delta+=.00065*math.exp(-(lateral/.0025)**2)*math.sin(math.pi*t)**1.3
                for j,joint in enumerate(chain[:3]):
                    axis=(chain[j+1]-joint).normalized();offset=p-joint
                    depth=offset.dot(dorsal)
                    planar=offset-dorsal*depth
                    delta+=(.0008 if j==0 else .00045)*math.exp(-(planar.length/(.0065 if j==0 else .0045))**2)
                    along=offset.dot(axis);cross=(planar-axis*planar.dot(axis)).length
                    delta-=.00013*math.exp(-((along-.001)/.00065)**2-(cross/.004)**4)
            rel=p-wrist
            if rel.dot(dorsal)<-.002:
                u=rel.dot(palm_across);t=rel.dot(palm_axis)/palm_length
                for crease in (.38+.11*(u/.030)**2,.69-.12*(u/.030),.85-.08*(u/.030)):
                    delta-=.00018*math.exp(-((t-crease)/.015)**2-(u/.033)**6)
            shape.data[vertex.index].co=vertex.co+vertex.normal*delta
        bpy.context.view_layer.update()
        evaluated=hand.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        evaluated.calc_loop_triangles()
        triangles=[tuple(tri.vertices) for tri in evaluated.loop_triangles]
        tree=BVHTree.FromPolygons(source,triangles,all_triangles=True)
        actual=[v.co.copy() for v in evaluated.vertices]
        normals=[v.normal.copy() for v in evaluated.vertices]
        posed_surface=BVHTree.FromPolygons(actual,triangles,all_triangles=True)
        def fit(point,normal):
            hit,_,index,_=tree.ray_cast(point+normal*.035,-normal,.07)
            assert hit is not None,('Nail sample missed original finger surface',side,digit,tuple(point),tuple(normal))
            ids=triangles[index];a,b,c=(source[i] for i in ids)
            position=barycentric_transform(hit,a,b,c,*(actual[i] for i in ids))
            outward=barycentric_transform(hit,a,b,c,*(normals[i] for i in ids)).normalized()
            return position+outward*.00016
        for digit,chain in digits.items():
            axis=(chain[3]-chain[2]).normalized()
            normal=(dorsal-axis*dorsal.dot(axis)).normalized()
            across=axis.cross(normal).normalized()
            center=chain[2].lerp(chain[3],.55)
            half_length=(chain[3]-chain[2]).length*.34
            half_width=.0037 if digit in (2,3,4) else .0030 if digit==5 else .0049
            # The source tips taper differently, particularly the thumb.
            # Keep the complete plate footprint inside that digit's surface.
            for _ in range(16):
                samples=[center+across*half_width*math.cos(j*math.tau/48)+axis*half_length*math.sin(j*math.tau/48) for j in range(48)]
                hits=[tree.ray_cast(p+normal*.035,-normal,.07) for p in samples]
                if all(h is not None and n.dot(normal)>.45 for h,n,_,_ in hits):break
                half_width*=.92;half_length*=.96
            assert half_width>.0015,'Nail footprint collapsed'
            vertices=[fit(center,normal)];tones=[(.48,.285,.235,1)];faces=[]
            rings=24;segments=96
            for k in range(1,rings+1):
                r=k/rings
                for j in range(segments):
                    angle=math.tau*j/segments
                    u=r*math.cos(angle);v=r*math.sin(angle)
                    vertices.append(fit(center+across*half_width*u+axis*half_length*v,normal))
                    edge=max(0,min(1,(v-.78)/.12))
                    tones.append(tuple(a*(1-edge)+b*edge for a,b in zip((.48,.285,.235,1),(.63,.53,.42,1))))
            faces.extend((0,1+j,1+(j+1)%segments) for j in range(segments))
            for k in range(rings-1):
                start=1+k*segments
                faces.extend((start+j,start+segments+j,start+segments+(j+1)%segments,start+(j+1)%segments) for j in range(segments))
            data=bpy.data.meshes.new(f'Character | nail {side} {digit}')
            data.from_pydata(vertices,[],faces);data.materials.append(nail)
            # Orient the fitted plate consistently with the underlying skin.
            import bmesh
            bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            outward=posed_surface.find_nearest(vertices[0])[1]
            if sum(f.normal.dot(outward) for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
            bm.to_mesh(data);bm.free()
            for polygon in data.polygons:polygon.use_smooth=True
            attribute=data.color_attributes.new(name='Nail bed and free edge',type='FLOAT_COLOR',domain='POINT')
            for datum,tone in zip(attribute.data,tones):datum.color=tone
            obj=bpy.data.objects.new(data.name,data);hand.users_collection[0].objects.link(obj);obj.matrix_world=hand.matrix_world.copy()
            solid=obj.modifiers.new('Fine keratin thickness','SOLIDIFY');solid.thickness=.00015;solid.offset=-1
            obj['anatomical_digit']=digit;obj['hand_side']=side
        hand.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    scene['hand_surface_refinement']=True
    print('ODDSWELL_HAND_SURFACE_PASS',flush=True)

refine_hands()
