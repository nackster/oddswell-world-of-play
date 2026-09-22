"""Fit fine eyelashes to the visible boundary between the head and eyeball."""
import bpy,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def fit_eye_margins():
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.name.startswith(('Character | eyelashes ','Character | lower wet margin ')):bpy.data.objects.remove(obj,do_unlink=True)
    head=bpy.data.objects['Character | anatomical head']
    surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
    rng=random.Random(282);count=0
    wet=bpy.data.materials.get('Character | moist eyelid tissue') or bpy.data.materials.new('Character | moist eyelid tissue')
    wet.use_nodes=True;bs=wet.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.32,.12,.085,1)
    bs.inputs['Roughness'].default_value=.19;bs.inputs['Coat Weight'].default_value=.45
    bs.inputs['Subsurface Weight'].default_value=.12;bs.inputs['Subsurface Scale'].default_value=.0006
    for side in ('l','r'):
        eye=bpy.data.objects['Character | eye '+side]
        transform=head.matrix_world.inverted()@eye.matrix_world
        vertices=[transform@v.co for v in eye.data.vertices]
        center=sum(vertices,Vector())/len(vertices)
        radius=max((v-center).length for v in vertices)
        if 'support_center' in eye:
            center=transform@Vector(eye['support_center']);radius=eye['support_radius']
        def hit_at(dx,dz):
            return surface.ray_cast(center+Vector((dx,.12,dz)),Vector((0,-1,0)),.24)
        def visible(dx,dz):
            square=radius*radius-dx*dx-dz*dz
            if square<=0:return False
            hit,_,_,_=hit_at(dx,dz)
            return hit is not None and hit.y<center.y+math.sqrt(square)-.00002
        data=bpy.data.curves.new('Character | fine eyelash strands '+side,'CURVE')
        data.dimensions='3D';data.bevel_depth=.000035;data.bevel_resolution=2
        lower=[]
        for j in range(33):
            dx=-.0115+.023*j/32+rng.uniform(-.0001,.0001)
            samples=[-.013+.026*k/120 for k in range(121)]
            exposed=[z for z in samples if visible(dx,z)]
            if not exposed:continue
            for direction in (1,-1):
                inside=max(exposed) if direction>0 else min(exposed)
                outside=inside+direction*.026/120
                for _ in range(8):
                    middle=(inside+outside)*.5
                    if visible(dx,middle):inside=middle
                    else:outside=middle
                hit,normal,_,_=hit_at(dx,outside)
                if hit is None:continue
                root=hit+normal*.00008
                if direction<0:
                    lower.append(root)
                    if j%2:continue
                length=rng.uniform(.0030,.0042) if direction>0 else rng.uniform(.0010,.0016)
                spline=data.splines.new('POLY');spline.points.add(3)
                for k,point in enumerate(spline.points):
                    t=k/3
                    point.co=(*(root+normal*(length*.35*t)+Vector((dx*.025*t,length*.85*t,direction*length*.30*t*t))),1)
                    point.radius=(1-t)*(.95 if direction>0 else .65)+.03
                count+=1
        obj=bpy.data.objects.new('Character | eyelashes '+side,data);scene.collection.objects.link(obj)
        obj.matrix_world=head.matrix_world.copy()
        data.materials.append(bpy.data.materials['Character | dark brown brow hair'])
        if len(lower)>8:
            data=bpy.data.curves.new('Character | lower wet margin '+side,'CURVE')
            data.dimensions='3D';data.bevel_depth=.00012;data.bevel_resolution=3
            spline=data.splines.new('POLY');spline.points.add(len(lower)-1)
            for j,(point,co) in enumerate(zip(spline.points,lower)):
                point.co=(*co,1);point.radius=.2+.8*math.sin(math.pi*j/(len(lower)-1))**.5
            obj=bpy.data.objects.new('Character | lower wet margin '+side,data);scene.collection.objects.link(obj)
            obj.matrix_world=head.matrix_world.copy();data.materials.append(wet)
    assert count>=60,'Could not resolve enough visible eyelid margin'
    scene['eyelash_strands']=count
    print('ODDSWELL_EYELID_MARGIN_PASS',count,flush=True)

fit_eye_margins()
