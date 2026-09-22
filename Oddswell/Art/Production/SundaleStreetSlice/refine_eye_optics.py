"""Native optical eye study: recessed pigment beneath a continuous cornea."""
import bpy, bmesh, math
from mathutils import Vector

def refine_eye_optics():
    scene=bpy.context.scene
    assert not scene.get('optical_eye_study',False),'Apply optical refinement once to the anatomical baseline'
    cornea=bpy.data.materials.get('Character | transparent cornea') or bpy.data.materials.new('Character | transparent cornea')
    cornea.use_nodes=True
    bs=cornea.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(1,1,1,1)
    bs.inputs['Roughness'].default_value=.025
    bs.inputs['Transmission Weight'].default_value=1
    bs.inputs['IOR'].default_value=1.376
    white=bpy.data.materials['Character | warm sclera']
    bs=white.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.50,.47,.43,1)
    bs.inputs['Roughness'].default_value=.24
    bs.inputs['Coat Weight'].default_value=.25
    for side in ('l','r'):
        eye=bpy.data.objects['Character | eye '+side]
        points=[v.co for v in eye.data.vertices]
        center=Vector(tuple((min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)))
        radius=.0158; aperture=.0062
        # Rings begin at the corneal pole and end at the posterior pole.
        angles=[0]+[math.asin(aperture/radius)*i/24 for i in range(1,25)]
        angles += [angles[-1]+(math.pi-angles[-1])*i/72 for i in range(1,73)]
        vertices=[];faces=[];segments=128
        for angle in angles:
            r=radius*math.sin(angle);y=radius*math.cos(angle)
            if angle<=math.asin(aperture/radius)+1e-7:y+=.0011*(1-(r/aperture)**2)**2
            vertices.extend(center+Vector((r*math.cos(j*math.tau/segments),y,r*math.sin(j*math.tau/segments))) for j in range(segments))
        for k in range(len(angles)-1):
            faces.extend((k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for j in range(segments))
        data=bpy.data.meshes.new('Character | optical eye '+side)
        data.from_pydata(vertices,[],faces);data.materials.append(white);data.materials.append(cornea)
        for p in data.polygons:p.material_index=int(p.index<24*segments);p.use_smooth=True
        bm=bmesh.new();bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
        eye.data=data
        for name in ('iris','pupil'):
            obj=bpy.data.objects['Character | '+name+' '+side]
            for v in obj.data.vertices:
                p=v.co-center;scale=.68 if name=='pupil' else .92;p.x*=scale;p.z*=scale
                r=math.hypot(p.x,p.z)
                # Slightly concave iris bowl; black pupil remains at its center.
                p.y=.0141+.00045*(r/.00552)**2+(.00004 if name=='pupil' else 0)
                v.co=center+p
            bs=obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
            bs.inputs['Coat Weight'].default_value=0
            bs.inputs['Roughness'].default_value=.52
            if name=='iris':
                for datum in obj.data.color_attributes['Iris radial fibers'].data:
                    datum.color=(*(min(1,c*1.7) for c in datum.color[:3]),1)
        eye['corneal_aperture_m']=aperture
        eye['iris_recess_m']=.0028
    for name in ('Character | anatomical face skin','Character | warm neutral skin'):
        material=bpy.data.materials[name];nodes=material.node_tree.nodes
        bs=nodes.get('Principled BSDF')
        bs.inputs['Subsurface Scale'].default_value=.0012
        bs.inputs['Subsurface Radius'].default_value=(1,.42,.20)
        for bump in [n for n in nodes if n.type=='BUMP']:
            bump.inputs['Distance'].default_value=.00010
            bump.inputs['Strength'].default_value=.22
            if bump.inputs['Height'].links:
                source=bump.inputs['Height'].links[0].from_node
                if source.type=='TEX_NOISE':source.inputs['Scale'].default_value=650
    scene['optical_eye_study']=True
    print('ODDSWELL_OPTICAL_EYE_PASS',flush=True)

refine_eye_optics()
