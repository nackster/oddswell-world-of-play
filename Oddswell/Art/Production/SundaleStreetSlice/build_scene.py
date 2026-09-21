"""Editable OddsWell street slice, modeled locally from the accepted image direction.

Blender 4.5: --background --python build_scene.py -- --preview
Omit --preview for the saved 1920x1080 Cycles render.
"""
import bpy
import math
import random
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
random.seed(218)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'


def mat(name, color, rough=.75, grain=0, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bs = nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if grain:
        tex = nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = grain
        tex.inputs['Detail'].default_value = 4
        coords = nodes.new('ShaderNodeTexCoord')
        links.new(coords.outputs['Object'], tex.inputs['Vector'])
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .12
        ramp.color_ramp.elements[0].color = (*(c*.67 for c in color), 1)
        ramp.color_ramp.elements[1].position = .88
        ramp.color_ramp.elements[1].color = (*(min(1,c*1.18) for c in color), 1)
        links.new(tex.outputs['Fac'], ramp.inputs[0])
        links.new(ramp.outputs[0], bs.inputs['Base Color'])
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .24
        bump.inputs['Distance'].default_value = .015 if grain < 100 else .002
        links.new(tex.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs[0], bs.inputs['Normal'])
    return m


stone = mat('OW | honed warm limestone', (.59,.46,.32), .83, 14)
plaster = mat('OW | mineral ivory plaster', (.69,.59,.46), .88, 26)
clay = mat('OW | terracotta ceramic', (.43,.21,.12), .78, 32)
mortar = mat('OW | recessed sand joints', (.23,.19,.14), .95, 35)
dark = mat('OW | graphite anodized frames', (.038,.048,.046), .36, 0, .65)
teal = mat('OW | restrained signal teal', (.026,.22,.21), .65, 900)
wood = mat('OW | oiled oak', (.25,.12,.049), .62, 13)
shopback = mat('OW | deep retail interior', (.023,.015,.008), .9, 18)
chalk = mat('OW | court warm white', (.77,.77,.65), .86)
court = mat('OW | blue mineral court', (.040,.120,.190), .92, 140)
courtkey = mat('OW | deep blue key', (.020,.065,.105), .92, 140)
soil = mat('OW | planted soil', (.073,.053,.026), 1, 45)
bark = mat('OW | rough oak bark', (.145,.093,.045), .96, 24)
glass = mat('OW | clear shop glazing', (.82,.88,.88), .055, 0, 0)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value = .97
glass.node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value = 1.46
shopglass=mat('OW | thin clear display glazing',(.03,.045,.045),.07,0,.5)
nodes,links=shopglass.node_tree.nodes,shopglass.node_tree.links
clear=nodes.new('ShaderNodeBsdfTransparent')
mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.08
links.new(clear.outputs[0],mix.inputs[1]);links.new(nodes.get('Principled BSDF').outputs[0],mix.inputs[2])
links.new(mix.outputs[0],nodes.get('Material Output').inputs['Surface'])
arena_glass = mat('OW | blue arena curtain wall', (.055,.12,.16), .20, 0, .65)
lamp = mat('OW | amber lamps', (.92,.63,.29), .3)
bs = lamp.node_tree.nodes.get('Principled BSDF')
bs.inputs['Emission Color'].default_value = (1,.61,.22,1)
bs.inputs['Emission Strength'].default_value = 2
leaves = []
for i in range(6):
    m = mat('OW | leaf tone %d' % i, (.055+i*.012,.12+i*.022,.018+i*.009), .75)
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Subsurface Weight'].default_value = .12
    translucent=m.node_tree.nodes.new('ShaderNodeBsdfTranslucent')
    translucent.inputs['Color'].default_value=m.diffuse_color
    mixleaf=m.node_tree.nodes.new('ShaderNodeMixShader');mixleaf.inputs[0].default_value=.27
    m.node_tree.links.new(bs.outputs[0],mixleaf.inputs[1]);m.node_tree.links.new(translucent.outputs[0],mixleaf.inputs[2])
    m.node_tree.links.new(mixleaf.outputs[0],m.node_tree.nodes.get('Material Output').inputs['Surface'])
    leaves.append(m)
pavers = [mat('OW | fired brick %02d' % i, (.31+i*.012,.16+i*.008,.085+i*.005), .9, 22) for i in range(12)]

# A real scanned mineral surface supplies the irregular grain missing in the
# first procedural pass. Sources and exact bytes are recorded beside the maps.
stonewall = mat('OW | scanned sandstone masonry',(.6,.48,.33),.9)
def scanned_surface(material,asset,repeat,height):
    nodes,links=material.node_tree.nodes,material.node_tree.links
    coords=nodes.new('ShaderNodeTexCoord')
    scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=repeat
    links.new(coords.outputs['Object'],scale.inputs[0])
    maps={}
    for channel in ('diff','disp','rough'):
        image=bpy.data.images.load(str(ROOT/'textures'/f'{asset}_{channel}_4k.jpg'))
        image.colorspace_settings.name='sRGB' if channel=='diff' else 'Non-Color'
        image.pack()
        tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.projection='BOX';tex.projection_blend=.12
        links.new(scale.outputs['Vector'],tex.inputs['Vector']);maps[channel]=tex
    bs=nodes.get('Principled BSDF')
    links.new(maps['diff'].outputs['Color'],bs.inputs['Base Color'])
    links.new(maps['rough'].outputs['Color'],bs.inputs['Roughness'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.6;bump.inputs['Distance'].default_value=height
    links.new(maps['disp'].outputs['Color'],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Normal'])
scanned_surface(stonewall,'sandstone_blocks_08',1/3,.06)
scanned_surface(bark,'bark_brown_01',1.1,.035)
exec(compile((ROOT/'refine_minerals.py').read_text(encoding='utf-8'),str(ROOT/'refine_minerals.py'),'exec'))


def mesh(name, verts, faces, material, smooth=False):
    d = bpy.data.meshes.new(name)
    d.from_pydata(verts, [], faces)
    d.materials.append(material)
    d.update()
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    if smooth:
        for p in d.polygons:
            p.use_smooth = True
    return o


def box(name, pos, size, material, bevel=0):
    if material==wood and size[1]>size[0]:material=wood_along_y
    x,y,z = pos
    a,b,c = (s/2 for s in size)
    verts = [(x+dx,y+dy,z+dz) for dx,dy,dz in [(-a,-b,-c),(-a,-b,c),(-a,b,-c),(-a,b,c),(a,-b,-c),(a,-b,c),(a,b,-c),(a,b,c)]]
    o = mesh(name, verts, [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)], material)
    if bevel:
        mod = o.modifiers.new('Soft edge', 'BEVEL')
        mod.width, mod.segments = bevel, 2
        o.modifiers.new('Corner normals', 'WEIGHTED_NORMAL')
    return o


def tube(name, points, radius, material, closed=False):
    d = bpy.data.curves.new(name, 'CURVE')
    d.dimensions = '3D'
    d.bevel_depth = radius
    d.bevel_resolution = 2
    s = d.splines.new('POLY')
    s.points.add(len(points)-1)
    for p, co in zip(s.points, points):
        p.co = (*co,1)
    s.use_cyclic_u = closed
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    d.materials.append(material)
    return o


def sphere(name, pos, scale, material, segments=16, rings=10):
    # Native datablocks avoid a full scene dependency update for every flower.
    verts=[(pos[0]+scale[0]*math.sin(math.pi*k/rings)*math.cos(math.tau*j/segments),pos[1]+scale[1]*math.sin(math.pi*k/rings)*math.sin(math.tau*j/segments),pos[2]+scale[2]*math.cos(math.pi*k/rings)) for k in range(rings+1) for j in range(segments)]
    faces=[(k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j) for k in range(rings) for j in range(segments)]
    return mesh(name,verts,faces,material,True)


def branch(name, a, b, ra, rb, material=bark):
    direction = Vector(b)-Vector(a)
    rotation = direction.to_track_quat('Z','Y')
    verts = [Vector(center)+rotation@Vector((radius*math.cos(i*math.tau/10),radius*math.sin(i*math.tau/10),0)) for center,radius in ((a,ra),(b,rb)) for i in range(10)]
    faces = [tuple(range(9,-1,-1)),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
    return mesh(name,verts,faces,material,True)


def leaf_cloud(name, centers, radius=1, count=230):
    verts, faces, indices = [], [], []
    for center in centers:
        for i in range(count):
            v = Vector((random.gauss(0,.43),random.gauss(0,.43),random.gauss(0,.42))) * radius
            v += Vector(center)
            angle = random.uniform(0,math.tau)
            length = random.uniform(.052,.112) * radius**.15
            u = Vector((math.cos(angle),math.sin(angle),random.uniform(-.45,.45))) * length
            w = Vector((-math.sin(angle),math.cos(angle),random.uniform(-.6,.6))) * length*.43
            # Curved, elliptical leaf blade: an actual surface with a raised
            # midrib, rounded shoulders and pointed tip, rather than diamonds.
            start = len(verts)
            for t in range(7):
                f=t/6
                width=math.sin(math.pi*f)**.72
                centerline=v+u*(2*f-1)+Vector((0,0,.014*math.sin(math.pi*f)))
                verts.extend([centerline-w*width,centerline+Vector((0,0,.004*width)),centerline+w*width])
            for t in range(6):
                for side in range(2):
                    n=start+t*3+side
                    faces.append((n,n+3,n+4,n+1))
            indices.extend([random.randrange(6)]*12)
    o = mesh(name, verts, faces, leaves[0],True)
    for m in leaves[1:]: o.data.materials.append(m)
    for p,index in zip(o.data.polygons,indices): p.material_index=index
    return o


# Shared mature tree geometry, adapted from the retained CC0 native source.
exec(compile((ROOT/'mature_trees.py').read_text(encoding='utf-8'),str(ROOT/'mature_trees.py'),'exec'))


# Real paver geometry, with variation in color and height, grouped into one mesh.
box('Street foundation',(3,25,-.113),(60,100,.3),mortar)
pv,pf,pi=[],[],[]
for row in range(340):
    y=-8+row*.17
    for col in range(152):
        x=-6.2+col*.175
        if 1.9<x<18.2 and 4.7<y<33.3:continue
        # Alternating paired runs produce a basket-weave civic brick pattern.
        vertical=(col//2+row//2)%2 == 0
        if (vertical and row%2) or (not vertical and col%2): continue
        sx,sy=(.170,.335) if vertical else (.345,.165)
        xx=x if vertical else x+.0875
        yy=y+.085 if vertical else y
        z=random.uniform(-.004,.004)
        n=len(pv)
        pv.extend([(xx+dx*sx/2,yy+dy*sy/2,z+dz) for dx,dy,dz in [(-1,-1,0),(-1,1,0),(1,1,0),(1,-1,0),(-1,-1,.045),(-1,1,.045),(1,1,.045),(1,-1,.045)]])
        pf.extend([tuple(n+i for i in f) for f in [(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]])
        pi.extend([random.randrange(12)]*5)
o=mesh('Promenade | individually laid fired bricks',pv,pf,pavers[0])
for m in pavers[1:]: o.data.materials.append(m)
for p,i in zip(o.data.polygons,pi):p.material_index=i
be=o.modifiers.new('Worn paver arris','BEVEL');be.width=.0025;be.segments=1
for x in (-6.5,1.9):
    box('Promenade limestone border',(x,20,.035),(.22,58,.085),stone,.018)


def facade(front, y, width, height, right=False, terra=False):
    sign=1 if right else -1
    material=clay if terra else stonewall
    box('Building | masonry volume',(front+sign*3.1,y,(height+3.4)/2),(6.2,width,height-3.4),material,.045)
    box('Building | retail rear volume',(front+sign*3.85,y,1.7),(4.7,width,3.4),material,.025)
    # Deep exterior storefront recess; dark backing and glass with visible retail fittings.
    for yy in (y-width*.25,y+width*.25):
        box('Shop | recessed interior',(front+sign*1.48,yy,1.65),(.035,width*.44,2.95),shopback)
        box('Shop | interior floor',(front+sign*.70,yy,.11),(1.55,width*.44,.12),wood,.012)
        box('Shop | interior ceiling',(front+sign*.70,yy,3.10),(1.55,width*.44,.12),plaster,.012)
        box('Shop | glazing',(front-sign*.20,yy,1.65),(.018,width*.41,2.8),shopglass)
        for z in (.14,3.12):box('Shop | frame',(front-sign*.23,yy,z),(.07,width*.44,.065),dark,.012)
        for dy in (-width*.22,0,width*.22):box('Shop | mullion',(front-sign*.24,yy+dy,1.64),(.07,.045,3.05),dark,.01)
        for z in (.55,1.05,1.55):
            box('Shop | oak display shelf',(front+sign*.85,yy,z),(.65,width*.36,.045),wood,.01)
            for item in range(6):
                box('Shop | display goods',(front+sign*.80,yy-width*.14+item*width*.058,z+.12),(.20,.13,random.uniform(.10,.23)),stone if item%2 else clay,.012)
        sphere('Shop | pendant',(front+sign*.60,yy,2.75),(.14,.14,.065),lamp)
        lightdata=bpy.data.lights.new('Shop | warm display light','POINT');lightdata.energy=85;lightdata.color=(1,.64,.32);lightdata.shadow_soft_size=.18
        lightobj=bpy.data.objects.new('Shop | warm display light',lightdata);scene.collection.objects.link(lightobj);lightobj.location=(front+sign*.60,yy,2.67)
        for offset in (-.62,.35):
            coords=[(-.20,.33),(-.38,.21),(-.31,.02),(-.19,.08),(-.20,-.37),(.20,-.37),(.19,.08),(.31,.02),(.38,.21),(.20,.33),(.08,.28),(-.08,.28)]
            garment=mesh('Shop | hanging garment',[(front+sign*.37,yy+offset+a,2.10+b) for a,b in coords],[tuple(range(len(coords)))],teal if offset>0 else stone)
            garment.modifiers.new('Display cloth thickness','SOLIDIFY').thickness=.07
            bevel=garment.modifiers.new('Soft folded garment edge','BEVEL');bevel.width=.025;bevel.segments=3
            tube('Shop | brass hanger',[(front+sign*.37,yy+offset-.18,2.40),(front+sign*.37,yy+offset,2.53),(front+sign*.37,yy+offset+.18,2.40)],.007,wood)
    for yy in (y-width/2+.15,y+width/2-.15):
        box('Building | stone pier',(front-sign*.25,yy,1.7),(.54,.34,3.4),stone,.025)
    box('Building | floor band',(front-sign*.18,y,3.45),(.40,width+.10,.20),stone,.025)
    # Sloped charcoal fabric awnings and scalloped edge.
    aw=mesh('Shop | charcoal fabric awning',[(front-sign*.30,y-width/2,3.43),(front-sign*.30,y+width/2,3.43),(front-sign*1.65,y+width/2,2.98),(front-sign*1.65,y-width/2,2.98)],[(0,1,2,3)],dark)
    sol=aw.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.02
    box('Shop | awning valance',(front-sign*1.65,y,2.92),(.025,width,.14),dark)
    for yy in (y-width*.27,y+width*.27):
        for z in (4.8,7.4,10.0):
            if z+1>height: continue
            box('Window | deep graphite reveal',(front-sign*.015,yy,z),(.06,1.4,1.85),dark)
            box('Window | blue glass',(front-sign*.09,yy,z),(.02,1.17,1.63),arena_glass)
            for dy in (-.73,.73):box('Window | limestone jamb',(front-sign*.12,yy+dy,z),(.22,.13,2.05),stone,.02)
            for zz in (z-.99,z+.99):box('Window | limestone lintel',(front-sign*.13,yy,zz),(.25,1.59,.13),stone,.02)
            box('Window | vertical sash',(front-sign*.14,yy,z),(.055,.045,1.65),dark)
            if int(y+z)%3:
                box('Balcony | stone slab',(front-sign*.54,yy,z-.98),(1.2,2.0,.14),stone,.035)
                tube('Balcony | top rail',[(front-sign*1.10,yy-1,z-.12),(front-sign*1.10,yy+1,z-.12)],.025,dark)
                for n in range(13):
                    tube('Balcony | baluster',[(front-sign*1.10,yy-.95+n*.158,z-.92),(front-sign*1.10,yy-.95+n*.158,z-.12)],.012,dark)
    box('Building | roof coping',(front,y,height+.06),(.38,width+.10,.22),stone,.025)
    for row,zz in enumerate([3.8+i*.49 for i in range(int((height-3.8)/.49))] if terra else []):
        box('Masonry | fine horizontal course',(front-sign*.015,y,zz),(.012,width,.012),mortar)
        for j in range(int(width/1.15)):
            yy=y-width/2+j*1.15+(row%2)*.575
            # Joints are only on solid wall bays, so they never cross window glass.
            if min(abs(yy-(y-width*.27)),abs(yy-(y+width*.27)))>.86:
                box('Masonry | staggered head joint',(front-sign*.02,yy,zz+.245),(.014,.009,.47),mortar)


for index,y in enumerate((-1,7,15,23,31,39)):
    facade(-6.0 if index==0 else -7.2,y,7.85,random.choice((9.0,10.7,11.7)),terra=index%3==1)
for index,y in enumerate((2,11,20,29,38)):
    facade(20.4,y,8.85,random.choice((9.0,10.7,11.7)),True,index%3==0)

# Court dimensions and regulation-height baskets, white painted geometry.
box('Court | slab',(10,19,.005),(15.5,28.5,.12),stone,.07)
box('Court | blue surface',(10,19,.072),(15,28,.025),court)
for y in (5.25,32.75):
    tube('Court | baseline',[(2.65,y,.09),(17.35,y,.09)],.024,chalk)
for x in (2.65,17.35):tube('Court | sideline',[(x,5.25,.09),(x,32.75,.09)],.024,chalk)
tube('Court | half line',[(2.65,19,.09),(17.35,19,.09)],.024,chalk)
def arc(name,x,y,r,z,material=chalk,start=0,end=math.tau):
    return tube(name,[(x+r*math.cos(start+(end-start)*i/96),y+r*math.sin(start+(end-start)*i/96),z) for i in range(97)],.023,material)
arc('Court | center circle',10,19,1.8,.09)
for y,sign in ((5.25,1),(32.75,-1)):
    box('Court | painted key',(10,y+sign*2.7,.088),(4.9,5.4,.007),courtkey)
    for x in (7.55,12.45):tube('Court | key line',[(x,y,.10),(x,y+sign*5.4,.10)],.024,chalk)
    tube('Court | foul line',[(7.55,y+sign*5.4,.10),(12.45,y+sign*5.4,.10)],.024,chalk)
    arc('Court | free throw circle',10,y+sign*5.4,1.8,.10)
    arc('Court | three point arc',10,y+sign*1.5,6.7,.10,start=0 if sign>0 else math.pi,end=math.pi if sign>0 else math.tau)
    by=y+sign*1.15
    branch('Basket | upright',(10,y-sign*.7,0),(10,y-sign*.7,3.65),.065,.065,dark)
    branch('Basket | cantilever',(10,y-sign*.7,3.55),(10,by,3.55),.055,.055,dark)
    box('Basket | transparent backboard',(10,by,3.45),(1.83,.028,1.07),glass,.012)
    for z in (2.91,3.99):tube('Basket | board frame',[(9.085,by,z),(10.915,by,z)],.024,chalk)
    for x in (9.085,10.915):tube('Basket | board frame',[(x,by,2.91),(x,by,3.99)],.024,chalk)
    tube('Basket | target square',[(9.70,by-sign*.03,3.05),(9.70,by-sign*.03,3.50),(10.30,by-sign*.03,3.50),(10.30,by-sign*.03,3.05)],.018,chalk)
    ry=by+sign*.37
    arc('Basket | orange rim',10,ry,.23,3.05,clay)
    for j in range(12):
        a=j*math.tau/12
        tube('Basket | woven net',[(10+(.23-k*.013)*math.cos(a+k*.10),ry+(.23-k*.013)*math.sin(a+k*.10),3.04-k*.05) for k in range(8)],.0035,chalk)

# Court paint is submillimeter relief, not raised tubing.
for obj in scene.objects:
    if obj.name.startswith('Court | ') and obj.type=='CURVE':
        line_z=obj.data.splines[0].points[0].co.z
        obj.scale.z=.01;obj.location.z=.08475-line_z*.01
    if obj.name.startswith('Court | painted key'):
        for vertex in obj.data.vertices:vertex.co.z=.0846+(vertex.co.z-.088)*(.0002/.007)
scene['flat_court_paint']=True

# Stone seats and planters repeat the same restrained band seen on the jacket.
for x in (1.3,18.8):
    for y in (3,11,24,35):
        box('Civic | limestone planter',(x,y,.40),(1.05,2.5,.8),stone,.055)
        box('Civic | teal ceramic inlay',(x-.532,y,.50),(.015,2.36,.095),teal,.004)
        box('Civic | soil',(x,y,.804),(.85,2.25,.025),soil)
        leaf_cloud('Civic | planted shrub',[(x,y-.6,1),(x,y+.6,1)],.42,220)
        box('Civic | oak bench',(x,y+2.1,.48),(1.05,1.3,.14),wood,.045)
        for yy in (y+1.62,y+2.55):box('Civic | bench support',(x,yy,.23),(.9,.12,.46),stone,.018)
for x,y,s in [(-2.4,7.5,1.35),(-3.8,17,1),(-3.8,28,1.1),(-3.8,38,.95),(19,4,.95),(19,15,1.1),(19,28,1),(2,40,.9),(12,40,1.05)]:
    tree(x,y,s)
for x in (-3,1.6,18.5):
    for y in (8,21,34):
        box('Civic light | base',(x,y,.1),(.35,.35,.2),dark,.035)
        box('Civic light | mast',(x,y,2.0),(.13,.13,3.8),dark,.016)
        box('Civic light | signal band',(x,y,2.8),(.15,.15,.12),teal,.012)
        box('Civic light | lantern',(x,y,4.03),(.24,.24,.53),lamp,.016)
        box('Civic light | cap',(x,y,4.33),(.29,.29,.075),dark,.025)
        for dx in (-.12,.12):
            for dy in (-.12,.12):box('Civic light | lantern frame',(x+dx,y+dy,4.03),(.025,.025,.55),dark,.004)

# Arena approach, wide steps, glazed elliptical bowl and layered limestone roof.
for i in range(12):
    box('Arena | approach step',(3,42+i*.58,.09+i*.07),(23, .60,.18+i*.14),stone,.018)
box('Arena | upper terrace',(3,52,1.68),(30,9,.30),stone,.03)
cx,cy=3,62
for i in range(96):
    a,b=i*math.tau/96,(i+1)*math.tau/96
    verts=[(cx+rx*math.cos(t),cy+ry*math.sin(t),z) for rx,ry,z,t in [(15,10,1.8,a),(15,10,1.8,b),(17,11,11,b),(17,11,11,a)]]
    mesh('Arena | curtain wall panel',verts,[(0,1,2,3)],arena_glass)
    if i%4==0:
        branch('Arena | limestone angled column',verts[0],verts[3],.22,.28,stone)
    else:tube('Arena | curtain wall mullion',[verts[0],verts[3]],.022,dark)
for z,rx,ry,radius in ((2,15,10,.20),(5,15.7,10.4,.06),(8,16.35,10.7,.06),(10.9,17,11,.32),(11.45,17.5,11.4,.24)):
    tube('Arena | horizontal ring',[(cx+rx*math.cos(i*math.tau/128),cy+ry*math.sin(i*math.tau/128),z) for i in range(128)],radius,stone if radius>.1 else dark,True)
verts=[(cx,cy,11.48)]+[(cx+17.5*math.cos(i*math.tau/128),cy+11.4*math.sin(i*math.tau/128),11.48) for i in range(128)]
mesh('Arena | floating roof',verts,[(0,i+1,(i+1)%128+1) for i in range(128)],stone)
tube('Arena | signal course',[(cx+15.2*math.cos(i*math.tau/128),cy+10.2*math.sin(i*math.tau/128),2.4) for i in range(128)],.09,teal,True)

# New offline character study: cloth-shaped lofts instead of the runtime boxes.
skin=mat('Character | warm neutral skin',(.39,.255,.15),.7,170)
jacket=mat('Character | slate woven jacket',(.024,.039,.049),.83,220)
shorts=mat('Character | offwhite cotton twill',(.62,.60,.50),.9,190)
sole=mat('Character | warm rubber sole',(.73,.72,.64),.8,90)
seam=mat('Character | seam thread',(.095,.12,.13),.85)
origin=Vector((-.75,-2.4,.06))
for material in (jacket,shorts):
    material.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.14


def bodypt(p):return Vector(p)+origin


def loft(name, rings, material, sides=32):
    verts=[]
    for k,(x,y,z,rx,ry) in enumerate(rings):
        for j in range(sides):
            a=j*math.tau/sides
            wrinkle=1+.035*math.sin(j*2.5+k*2.1)
            verts.append(bodypt((x+rx*math.cos(a)*wrinkle,y+ry*math.sin(a)*wrinkle,z)))
    faces=[tuple(range(sides-1,-1,-1))]
    for k in range(len(rings)-1):
        for j in range(sides):faces.append((k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j))
    faces.append(tuple((len(rings)-1)*sides+j for j in range(sides)))
    o=mesh(name,verts,faces,material,True)
    sub=o.modifiers.new('Cloth surface subdivision','SUBSURF');sub.levels=2
    return o


torso=[(0,0,.90,.20,.12),(0,0,.92,.215,.13),(0,0,.97,.22,.145),(0,.015,1.12,.245,.153),(0,.014,1.32,.259,.15),(0,.012,1.41,.248,.139),(0,.005,1.46,.20,.12),(0,0,1.49,.105,.091)]
loft('Character | tailored slate jacket',torso,jacket)
loft('Character | ribbed waistband',[(0,0,.90,.198,.122),(0,0,.92,.215,.132),(0,0,.95,.213,.134)],jacket)
loft('Character | standing collar',[(0,0,1.46,.10,.085),(0,0,1.49,.106,.092),(0,0,1.53,.09,.08)],jacket)
# Rear yoke band follows the jacket surface, not a floating rectangular primitive.
verts=[]
for z in (1.333,1.384):
    for j in range(25):
        a=math.pi+j*math.pi/24
        verts.append(bodypt((.260*math.cos(a),.014+.154*math.sin(a),z)))
mesh('Character | teal rear yoke',verts,[(j,j+1,j+26,j+25) for j in range(24)],teal,True)
for side in (-1,1):
    sx=side*.245
    loft('Character | shaped sleeve',[(sx,0,1.40,.086,.10),(side*.265,.005,1.32,.093,.105),(side*.295,-.025,1.21,.080,.085),(side*.32,-.045,1.17,.087,.093),(side*.325,-.070,1.13,.073,.081),(side*.33,-.055,1.10,.082,.084),(side*.34,-.035,1.00,.065,.077),(side*.35,-.015,.94,.073,.077),(side*.35,-.015,.91,.062,.068)],jacket)
    loft('Character | sleeve cuff',[(side*.35,-.015,.90,.062,.065),(side*.35,-.015,.94,.069,.075)],jacket)
    sphere('Character | relaxed hand',bodypt((side*.35,-.008,.837)),(.047,.039,.09),skin)
    sphere('Character | thumb',bodypt((side*.313,.01,.85)),(.024,.027,.055),skin)
    # Slight stagger makes the static study read as a walking pose.
    legy=.075 if side==1 else -.065
    loft('Character | shorts leg',[(side*.112,0,.93,.126,.138),(side*.115,legy*.3,.82,.13,.14),(side*.125,legy,.65,.116,.13),(side*.13,legy,.60,.113,.12)],shorts)
    loft('Character | bare lower leg',[(side*.13,legy,.64,.081,.087),(side*.132,legy,.56,.076,.080),(side*.137,legy,.43,.078,.079),(side*.14,legy,.27,.053,.058),(side*.14,legy,.14,.043,.05)],skin)
    sphere('Character | sneaker sole',bodypt((side*.14,legy+.032,.067)),(.071,.145,.028),sole)
    sphere('Character | canvas sneaker',bodypt((side*.14,legy+.033,.105)),(.067,.13,.055),shorts)
    for k in range(4):tube('Character | shoe lace',[bodypt((side*.14-.034,legy+.01+k*.016,.15-k*.004)),bodypt((side*.14+.034,legy+.02+k*.016,.15-k*.004))],.003,sole)
    tube('Character | back pocket seam',[bodypt((side*.065,-.134,.83)),bodypt((side*.075,-.137,.75)),bodypt((side*.165,-.123,.75)),bodypt((side*.175,-.12,.83))],.0025,sole)
branch('Character | neck',bodypt((0,0,1.48)),bodypt((0,0,1.62)),.064,.063,skin)
sphere('Character | faceless head',bodypt((0,.005,1.682)),(.087,.098,.13),skin,24,16)
for side in (-1,1):sphere('Character | ear',bodypt((side*.086,.005,1.669)),(.016,.028,.04),skin)
for x in (-.13,.13):tube('Character | rear jacket seam',[bodypt((x,-.122,.96)),bodypt((x*1.1,-.142,1.13)),bodypt((x*1.1,-.132,1.32))],.0018,seam)

# Use the CC0 hm08 anatomical surface for exposed skin. Only the head/neck,
# lower legs and hands are retained in this clothed scene. The original source
# and license are preserved, and no game skeleton or animation is replaced.
for obj in list(scene.objects):
    if any(obj.name.startswith('Character | '+n) for n in ('bare lower leg','relaxed hand','thumb','neck','faceless head','ear')):
        bpy.data.objects.remove(obj,do_unlink=True)
rawverts=[];rawuvs=[];bodyfaces=[];bodyfaceuvs=[];jointverts={};group=''
for line in (ROOT/'source-assets/makehuman-base.obj').read_text(encoding='utf-8').splitlines():
    parts=line.split()
    if not parts:continue
    if parts[0]=='v':rawverts.append(Vector(tuple(map(float,parts[1:4]))))
    elif parts[0]=='vt':rawuvs.append(tuple(map(float,parts[1:3])))
    elif parts[0]=='g':group=parts[1]
    elif parts[0]=='f':
        ids=[int(p.split('/')[0])-1 for p in parts[1:]]
        if group=='body':
            bodyfaces.append(ids)
            bodyfaceuvs.append([rawuvs[int(p.split('/')[1])-1] for p in parts[1:]])
        if group.startswith('joint-'):jointverts.setdefault(group,set()).update(ids)
used={i for face in bodyfaces for i in face}
low=min(rawverts[i].y for i in used);high=max(rawverts[i].y for i in used)
unit=1.8/(high-low)
def convert(v):return Vector((v.x*unit,v.z*unit,(v.y-low)*unit))
converted=[convert(v) for v in rawverts]
def joint(name):return sum((converted[i] for i in jointverts[name]),Vector())/len(jointverts[name])
for region in ('head','legs','left hand','right hand'):
    vertices=[];faces=[];faceuvs=[];indices={}
    sign=1 if region=='left hand' else -1
    if 'hand' in region:
        side='l' if sign==1 else 'r'
        wrist=joint('joint-'+side+'-hand');elbow=joint('joint-'+side+'-elbow')
        target=Vector((sign*.35,-.015,.90))
        rotation=(wrist-elbow).rotation_difference(Vector((sign*.03,.04,-.25)))
        knuckle=joint('joint-'+side+'-finger-3-1')
        finger_axis=(knuckle-wrist).normalized()
        across=(joint('joint-'+side+'-finger-5-1')-joint('joint-'+side+'-finger-2-1')).normalized()
        palm_normal=across.cross(finger_axis).normalized()
        if (rotation@palm_normal).x*sign<0:palm_normal=-palm_normal
    for face,source_uvs in zip(bodyfaces,bodyfaceuvs):
        vs=[converted[i] for i in face]
        keep=all(v.z>1.485 for v in vs) if region=='head' else all(.13<v.z<.705 for v in vs) if region=='legs' else all(v.x*sign>.375 and v.z<1.26 and (v-wrist).dot(finger_axis)>-.035 for v in vs)
        if not keep:continue
        newface=[]
        for index in face:
            if index not in indices:
                v=converted[index].copy()
                if region=='legs':
                    side=1 if v.x>0 else -1
                    # Preserve calf width while correcting the base mesh's
                    # outward A-pose stance. Uniform X scaling made thin shins.
                    width=1.06+.07*math.exp(-((v.z-.37)/.11)**2)
                    v.x=side*.14+(v.x-side*(.248-.145*v.z))*width
                    v.y+=.075 if v.x>0 else -.065
                elif 'hand' in region:
                    # Smooth resting curl beyond the knuckles, preserving
                    # source topology/UVs and the wrist attachment.
                    length=max(0,(v-knuckle).dot(finger_axis))
                    angle=length*9
                    v+=finger_axis*(math.sin(angle)/9-length)-palm_normal*((1-math.cos(angle))/9)
                    v=target+rotation@((v-wrist)*.94)
                    v.x=target.x+(v.x-target.x)*.85
                indices[index]=len(vertices);vertices.append(bodypt(v))
            newface.append(indices[index])
        faces.append(newface)
        faceuvs.append(source_uvs)
    anatomy=mesh('Character | anatomical '+region,vertices,faces,skin,True)
    uv=anatomy.data.uv_layers.new(name='MakeHuman source UV')
    for polygon,source_uvs in zip(anatomy.data.polygons,faceuvs):
        for loop_index,coord in zip(polygon.loop_indices,source_uvs):uv.data[loop_index].uv=coord
    mod=anatomy.modifiers.new('Anatomical surface','SUBSURF');mod.levels=2 if region=='head' else 1
skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.08

# Authored tailoring, layered planting and surface details share the helpers
# above and remain ordinary editable meshes in the resulting Blender file.
exec(compile((ROOT/'develop_character_landscape.py').read_text(encoding='utf-8'),str(ROOT/'develop_character_landscape.py'),'exec'))
exec(compile((ROOT/'refine_character_head.py').read_text(encoding='utf-8'),str(ROOT/'refine_character_head.py'),'exec'))

# Pose the clothed lower body for a short walking stride in this static study.
from mathutils import Matrix
for obj in list(scene.objects):
    if obj.type!='MESH' or not any(obj.name.startswith('Character | '+p) for p in ('anatomical legs','shorts leg','sneaker sole','canvas sneaker')):continue
    for vertex in obj.data.vertices:
        worldpoint=obj.matrix_world@vertex.co
        relative=worldpoint-origin
        sign=1 if relative.x>0 else -1
        pivot=Vector((sign*.13,0,.9))
        angle=sign*.14*min(1,max(0,(.95-relative.z)/.20))
        posed=pivot+Matrix.Rotation(angle,3,'X')@(relative-pivot)
        vertex.co=obj.matrix_world.inverted()@(posed+origin)
for obj in scene.objects:
    if obj.type!='CURVE' or not any(obj.name.startswith('Character | '+p) for p in ('shoe lace','back pocket seam','shorts leg hem')):continue
    for spline in obj.data.splines:
        for point in spline.points:
            relative=Vector(point.co[:3])-origin
            sign=1 if relative.x>0 else -1
            pivot=Vector((sign*.13,0,.9))
            angle=sign*.14*min(1,max(0,(.95-relative.z)/.20))
            point.co=(*(pivot+Matrix.Rotation(angle,3,'X')@(relative-pivot)+origin),1)
scene['clothing_details_posed']=True

# Plant the stance foot on the brick surface after the walking deformation.
# Inspect evaluated soles so subdivision cannot leave the entire figure afloat.
bpy.context.view_layer.update()
depsgraph=bpy.context.evaluated_depsgraph_get()
foot_min=min((obj.evaluated_get(depsgraph).matrix_world@v.co).z for obj in scene.objects if obj.name.startswith('Character | sneaker sole') for v in obj.evaluated_get(depsgraph).data.vertices)
ground_offset=.051-foot_min
for obj in scene.objects:
    if obj.name.startswith('Character | '):obj.location.z+=ground_offset
scene['character_ground_offset']=ground_offset

# Physical daylight and photographic contrast, without a generated background.
world=bpy.data.worlds.new('Sundale | late afternoon sky')
world.use_nodes=True
scene.world=world
nodes=world.node_tree.nodes
sky=nodes.new('ShaderNodeTexEnvironment')
sky.image=bpy.data.images.load(str(ROOT/'textures/kloppenheim_06_puresky_4k.exr'));sky.image.pack()
coords=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2]=math.radians(125)
world.node_tree.links.new(coords.outputs['Generated'],mapping.inputs['Vector'])
world.node_tree.links.new(mapping.outputs['Vector'],sky.inputs['Vector'])
world.node_tree.links.new(sky.outputs[0],nodes.get('Background').inputs[0])
nodes.get('Background').inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN',location=(-10,5,15))
sun=bpy.context.object;sun.name='Sundale | warm afternoon sun'
sun.rotation_euler=(math.radians(52),math.radians(-25),math.radians(-155))
sun.data.energy=6;sun.data.color=(1,.76,.52);sun.data.angle=math.radians(.8)
bpy.ops.object.light_add(type='AREA',location=(-1,-3,7))
fill=bpy.context.object;fill.name='Sundale | broad warm bounce'
fill.data.energy=700;fill.data.shape='DISK';fill.data.size=10;fill.data.color=(1,.88,.75)
fill.rotation_euler=(Vector((0,9,1.5))-fill.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.lights.new('Sundale | reflected courtyard light','AREA')
data.energy=2100;data.shape='DISK';data.size=12;data.color=(1,.80,.58)
bounce=bpy.data.objects.new('Sundale | reflected courtyard light',data);scene.collection.objects.link(bounce)
bounce.location=(8,7,8);bounce.rotation_euler=(Vector((-5,8,3))-bounce.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-.2,-6.9,1.60))
camera=bpy.context.object;camera.name='CAM | gameplay street'
camera.rotation_euler=(Vector((2,34,1.0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens=28;camera.data.clip_end=500
scene.camera=camera
scene.render.engine='CYCLES'
scene.cycles.device='GPU' if '--gpu' in sys.argv else 'CPU'
if '--gpu' in sys.argv:
    devices=bpy.context.preferences.addons['cycles'].preferences
    devices.compute_device_type='OPTIX';devices.get_devices()
    for device in devices.devices:device.use=device.type=='OPTIX'
scene.cycles.samples=32 if '--preview' in sys.argv else 160
scene.cycles.use_denoising=True
scene.cycles.max_bounces=8
scene.cycles.transparent_max_bounces=16
scene.render.resolution_x=1100 if '--preview' in sys.argv else 1920
scene.render.resolution_y=619 if '--preview' in sys.argv else 1080
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=0
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT / ('StreetSlice_Preview.png' if '--preview' in sys.argv else 'StreetSlice_Gameplay.png'))
# Named collections keep the actual model editable by asset family.
groups={}
for obj in list(scene.objects):
    prefix=obj.name.split(' | ')[0]
    group='Character' if prefix=='Character' else 'Trees and planting' if prefix in ('Oak','Tree','Tree pit soil','Tree pit stone surround') else 'Arena' if prefix=='Arena' else 'Court' if prefix in ('Court','Basket') else 'Architecture' if prefix in ('Building','Window','Balcony','Shop','Masonry') else 'Civic and paving' if prefix in ('Civic','Civic light','Promenade') else 'Lighting and cameras'
    if group not in groups:
        groups[group]=bpy.data.collections.new(group);scene.collection.children.link(groups[group])
    for collection in list(obj.users_collection):collection.objects.unlink(obj)
    groups[group].objects.link(obj)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'),compress=True)
print('ODDSWELL_STREET_SLICE_MODELED',len(scene.objects),flush=True)
bpy.ops.render.render(write_still=True)
(ROOT/'scene-evidence.json').write_text(json.dumps({'source':'Authored native architecture, garments, paving and understory; CC0 MakeHuman anatomical surfaces; adapted CC0 Jacaranda geometry; packed Poly Haven stone, bark, tree and sky maps','reference':'../../Reviews/OddsWellStreetIdentityCandidate/OddsWell_Visual_Direction_Concept.png','objects':len(scene.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'packed_texture_maps':len([i for i in bpy.data.images if i.source=='FILE' and i.packed_file]),'mature_tree_instances':sum(o.name.startswith('Tree | mature Sundale') for o in scene.objects),'seed':218,'render_engine':'Cycles','samples':scene.cycles.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'runtime_integrated':False,'character':'Static tailored study with grounded stance and continuous shorts; current game rig unchanged','character_ground_offset_m':scene['character_ground_offset'],'no_generated_background':True,'quality_goal':'Active; reference fidelity and final art approval remain open'},indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_RENDER_PASS',flush=True)
