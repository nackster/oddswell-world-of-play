"""Surface-fitted brow grooming around the retained adult facial proportions."""
import bpy,math,random
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def refine_brow_groom():
    scene=bpy.context.scene
    assert not scene.get('brow_groom_refinement'),'Apply once to the transported source brows'
    head=bpy.data.objects['Character | anatomical head']
    keys=list(head.data.shape_keys.key_blocks);basis=keys[0]
    current=[base.co+sum(((key.data[i].co-base.co)*key.value for key in keys[1:]),Vector()) for i,base in enumerate(basis.data)]
    expression=head.shape_key_add(name='Resting eyelid openness',from_mix=False);expression.value=1
    eyes=[]
    for side in ('l','r'):
        eye=bpy.data.objects['Character | eye '+side]
        center=head.matrix_world.inverted()@eye.matrix_world@Vector(eye['support_center'])
        eyes.append((center,.00065 if side=='l' else .00045))
    for vertex,p,base in zip(expression.data,current,basis.data):
        lift=0
        for center,amount in eyes:
            offset=p-center
            front=max(0,min(1,(offset.y-.001)/.009));upper=max(0,min(1,offset.z/.003))
            lift+=amount*math.exp(-(offset.x/.014)**4-((offset.z-.0045)/.006)**2)*front*upper
        vertex.co=base.co+Vector((0,0,lift))
    maximum=max((a.co-b.co).length for a,b in zip(expression.data,basis.data))
    assert 0<maximum<.0007,'Eyelid control changed more than the intended local lift'
    bpy.context.view_layer.update()
    surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
    hair=bpy.data.materials['Character | dark brown brow hair'];materials=[]
    for label,color in (('deep',(.019,.009,.005,1)),('brown',(.040,.019,.009,1)),('warm',(.070,.035,.016,1))):
        material=hair.copy();material.name='Character | brow hair '+label
        bs=material.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.46;bs.inputs['Anisotropic'].default_value=.35
        materials.append(material)
    for sign in (-1,1):
        old=bpy.data.objects['Character | eyebrow '+str(sign)]
        transform=head.matrix_world.inverted()@old.matrix_world
        roots=[transform@Vector(s.points[0].co[:3]) for s in old.data.splines]
        xs=np.array([sign*(p.x+.75) for p in roots]);low=float(np.quantile(xs,.01));high=float(np.quantile(xs,.99))
        coefficients=np.polynomial.polynomial.polyfit((xs-low)/(high-low),[p.z for p in roots],2)
        data=bpy.data.curves.new('Character | individually groomed brow '+str(sign),'CURVE');data.dimensions='3D';data.bevel_depth=.000038;data.bevel_resolution=2
        for material in materials:data.materials.append(material)
        rng=random.Random(740+sign)
        for i in range(650):
            t=rng.random();x=sign*(low+(high-low)*t)-.75
            width=.0037*(1-.82*t)**.55
            z=float(np.polynomial.polynomial.polyval(t,coefficients))+.0006+max(-1,min(1,rng.gauss(0,.45)))*width
            length=rng.uniform(.0031,.0053)*(1-.23*t)
            spline=data.splines.new('POLY');spline.points.add(5);spline.material_index=rng.choices((0,1,2),(.55,.35,.10))[0]
            lean=rng.uniform(-.10,.10)
            for k,point in enumerate(spline.points):
                u=k/5;px=x+sign*length*(.25+.68*t+lean)*u
                pz=z+length*((.72-.90*t)*u-.16*u*u)
                hit,normal,_,_=surface.ray_cast(Vector((px,-2.08,pz)),Vector((0,-1,0)),.65)
                assert hit is not None,'Groom strand missed the facial surface'
                lift=.000075+.00026*math.sin(math.pi*u)
                point.co=(*(hit+normal*lift),1);point.radius=.10+.90*(1-u)**.6
        obj=bpy.data.objects.new('Character | groomed eyebrow '+str(sign),data);old.users_collection[0].objects.link(obj);obj.matrix_world=head.matrix_world.copy()
        bpy.data.objects.remove(old,do_unlink=True);obj.name='Character | eyebrow '+str(sign)
        obj['strand_count']=650;obj['root_halfwidth_m']=.0037
    exec(compile((ROOT/'refine_eye_margins.py').read_text(encoding='utf-8'),str(ROOT/'refine_eye_margins.py'),'exec'),globals())
    scene['brow_groom_refinement']=True
    print('ODDSWELL_BROW_GROOM_PASS',flush=True)

refine_brow_groom()
