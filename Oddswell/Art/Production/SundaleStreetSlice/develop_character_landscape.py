"""Native tailoring and landscape refinement, executed by build_scene.py.

All surfaces are geometry; no reference-image projection or compositing.
Dimensions are meters. The garment folds are shaped into the control mesh.
"""
from mathutils import Matrix

for obj in list(scene.objects):
    if obj.name.startswith('Character | ') and not obj.name.startswith('Character | anatomical '):
        bpy.data.objects.remove(obj,do_unlink=True)

# A quieter slate fabric and fine matching thread keep the silhouette readable.
thread=mat('Character | matching charcoal topstitch',(.042,.055,.060),.92)
cotton_thread=mat('Character | matching cotton topstitch',(.42,.40,.34),.94)
rib=mat('Character | dense slate rib knit',(.025,.035,.039),.94,340)
shoe_fabric=mat('Character | oat canvas',(.48,.46,.39),.94,260)
for material,scale,distance in ((skin,1800,.00012),(jacket,1700,.00035),(shorts,2100,.00030),(shoe_fabric,1400,.00045)):
    for node in material.node_tree.nodes:
        if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=scale
        if node.type=='BUMP':node.inputs['Distance'].default_value=distance;node.inputs['Strength'].default_value=.18
        if node.type=='VALTORGB':
            color=material.diffuse_color[:3]
            node.color_ramp.elements[0].color=(*(c*.90 for c in color),1)
            node.color_ramp.elements[1].color=(*(c*1.05 for c in color),1)

def ring_at(rings,z):
    # Smooth the tailoring profile while limiting overshoot at narrow cuffs.
    # Piecewise straight radii produced angular shoulder and hip bands.
    for index,(a,b) in enumerate(zip(rings,rings[1:])):
        if a[2]<=z<=b[2]:
            f=(z-a[2])/(b[2]-a[2])
            width=b[2]-a[2]
            result=[]
            for component in range(5):
                if component==2:result.append(z);continue
                slope=(b[component]-a[component])/width
                previous=(a[component]-rings[index-1][component])/(a[2]-rings[index-1][2]) if index else slope
                following=(rings[index+2][component]-b[component])/(rings[index+2][2]-b[2]) if index+2<len(rings) else slope
                def tangent(left,right):
                    return 0 if left*right<=0 else math.copysign(min(abs((left+right)/2),3*min(abs(left),abs(right))),left)
                ma=tangent(previous,slope)*width;mb=tangent(slope,following)*width
                result.append((2*f**3-3*f*f+1)*a[component]+(f**3-2*f*f+f)*ma+(-2*f**3+3*f*f)*b[component]+(f**3-f*f)*mb)
            return tuple(result)
    return rings[0] if z<rings[0][2] else rings[-1]

def cloth_point(rings,z,a,kind):
    x,y,_,rx,ry=ring_at(rings,z)
    if kind=='coat':
        gather=math.exp(-((z-.970)/.045)**2)
        fold=.005*math.sin(a*11+z*24)*gather
        fold+=.003*math.sin(a*15+z*4)*math.exp(-((z-1.17)/.19)**2)
        # Diagonal compression folds above the hem, terminating at side seams.
        for crest,center in ((.976,3.75),(1.025,5.3),(1.070,3.5)):
            d=z-(crest+.065*math.cos(a*2+.7))
            localized=math.exp(-((a-center)/.45)**2)
            fold+=localized*(.008*math.exp(-(d/.011)**2)-.003*math.exp(-((d+.014)/.010)**2))
        fold+=.003*math.sin(a*8-z*21)*math.exp(-((z-1.36)/.09)**2)
        fold*=max(0,min(1,(z-.942)/.030))
    elif kind=='sleeve':
        gather=math.exp(-((z-1.15)/.06)**2)+.4*math.exp(-((z-.955)/.035)**2)
        fold=.006*math.sin(z*100+a*3)*gather*(.5+.5*math.sin(a+z*2))+.0015*math.sin(a*9+z*9)
        fold*=max(0,min(1,(z-.945)/.035))
    elif kind=='shorts':
        fold=.0025*math.sin(a*9+z*11)
        fold+=.004*math.sin(z*82+a*2)*math.exp(-((z-.84)/.05)**2)
        fold+=.0025*math.sin(z*120+a*4)*math.exp(-((z-.63)/.025)**2)
    else:
        fold=.00015*math.cos(a*24)
    px=x+(rx+fold)*math.cos(a);py=y+(ry+fold)*math.sin(a)
    if kind=='shorts' and rx>.18 and math.sin(a)<0:
        py+=.045*math.exp(-(px/.050)**2)*math.exp(-((z-.825)/.065)**2)
    pz=z
    if kind=='sleeve' and z>1.38:
        side=1 if x>0 else -1
        pz-=.029*min(1,(z-1.38)/.065)*(1+side*math.cos(a))*.5
    return bodypt((px,py,pz))

def cloth(name,rings,material,kind,steps=55,sides=80):
    lo,hi=rings[0][2],rings[-1][2]
    vertices=[cloth_point(rings,lo+(hi-lo)*k/steps,j*math.tau/sides,kind) for k in range(steps+1) for j in range(sides)]
    faces=[(k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j) for k in range(steps) for j in range(sides)]
    obj=mesh('Character | '+name,vertices,faces,material,True)
    sub=obj.modifiers.new('Tailoring surface','SUBSURF');sub.levels=1
    solid=obj.modifiers.new('Garment edge thickness','SOLIDIFY');solid.thickness=.0015
    return obj

coat=[(0,0,.915,.190,.114),(0,0,.95,.209,.132),(0,.006,1.02,.222,.140),(0,.012,1.15,.239,.144),(0,.014,1.31,.253,.146),(0,.012,1.395,.250,.133),(0,.007,1.43,.231,.123),(0,0,1.48,.104,.083)]
cloth('tailored slate jacket',coat,jacket,'coat')
cloth('ribbed waistband',[(0,0,.897,.194,.120),(0,0,.922,.199,.124),(0,0,.943,.207,.133)],rib,'rib',12)
cloth('standing collar',[(0,0,1.47,.095,.082),(0,0,1.485,.091,.079),(0,0,1.526,.076,.071)],rib,'rib',14)
cloth('shorts leg hip yoke',[(0,0,.80,.190,.115),(0,0,.865,.215,.132),(0,0,.925,.209,.129)],shorts,'shorts',24)

# The yoke follows the same displaced cloth surface and has a narrow sewn edge.
verts=[]
for k in range(5):
    for j in range(81):
        a=math.pi+j*math.pi/80
        z=1.337+k*.009+.011*math.cos(a*2)
        p=cloth_point(coat,z,a,'coat')
        p+=Vector((math.cos(a),math.sin(a),0))*.0018
        verts.append(p)
mesh('Character | sewn teal rear yoke',verts,[(k*81+j,k*81+j+1,(k+1)*81+j+1,(k+1)*81+j) for k in range(4) for j in range(80)],teal,True)
for edge in (1.340,1.370):
    pts=[]
    for j in range(81):
        a=math.pi+j*math.pi/80
        pts.append(cloth_point(coat,edge+.011*math.cos(a*2),a,'coat')+Vector((math.cos(a),math.sin(a),0))*.0025)
    tube('Character | yoke topstitch',pts,.00055,thread)
for a in (math.pi*1.16,math.pi*1.84):
    tube('Character | jacket panel seam',[cloth_point(coat,.955+k*.006,a+.035*math.sin(k*.11),'coat')+Vector((math.cos(a),math.sin(a),0))*.001 for k in range(62)],.00065,thread)

# Front construction remains readable when the character turns around.
zipper=mat('Character | muted gunmetal zipper',(.065,.070,.068),.45,0,.55)
for side in (-1,1):
    tube('Character | front zipper tape',[cloth_point(coat,.948+k*.007,math.pi/2,'coat')+Vector((side*.0026,.0016,0)) for k in range(73)],.0011,thread)
    tube('Character | front welt pocket',[cloth_point(coat,1.005+k*.004,(.72 if side>0 else math.pi-.72)+side*k*.003,'coat')+Vector((0,.0018,0)) for k in range(27)],.0015,rib)
for k in range(67):
    p=cloth_point(coat,.96+k*.0074,math.pi/2,'coat')+Vector((0,.002,0))
    box('Character | zipper teeth',p,(.006,.0015,.0015),zipper)
box('Character | zipper pull',cloth_point(coat,1.432,math.pi/2,'coat')+Vector((0,.004,0)),(.011,.004,.023),zipper,.0015)

leg_profiles={}
for side in (-1,1):
    suffix=' left' if side<0 else ' right'
    sleeve=[(side*.338,-.016,.924,.054,.059),(side*.34,-.026,.973,.060,.067),(side*.324,-.040,1.05,.066,.074),(side*.311,-.052,1.15,.076,.079),(side*.30,-.029,1.22,.076,.084),(side*.273,-.003,1.34,.086,.093),(side*.229,.006,1.414,.060,.080),(side*.20,.006,1.445,.047,.064),(side*.145,.006,1.455,.035,.045)]
    cloth('shaped sleeve'+suffix,sleeve,jacket,'sleeve')
    sleeve_yoke=[]
    for k in range(5):
        for j in range(41):
            a=math.pi+j*math.pi/40;z=1.329+k*.009+.008*math.cos(a*2)
            sleeve_yoke.append(cloth_point(sleeve,z,a,'sleeve')+Vector((math.cos(a),math.sin(a),0))*.0018)
    mesh('Character | sleeve signal yoke'+suffix,sleeve_yoke,[(k*41+j,k*41+j+1,(k+1)*41+j+1,(k+1)*41+j) for k in range(4) for j in range(40)],teal,True)
    cuff=[]
    for z in (.902,.923,.945):
        x,y,_,rx,ry=ring_at(sleeve,z)
        cuff.append((x,y,z,rx+.0035,ry+.0035))
    cloth('sleeve cuff'+suffix,cuff,rib,'rib',12)
    # Sewn outer sleeve line is thin and rests on the displaced fabric.
    a=math.pi*1.5
    tube('Character | sleeve seam'+suffix,[cloth_point(sleeve,.95+k*.006,a,'sleeve')+Vector((0,-.001,0)) for k in range(72)],.00065,thread)
    legy=.075 if side==1 else -.065
    pants=[(side*.131,legy,.604,.090,.104),(side*.13,legy,.625,.095,.109),(side*.126,legy*.9,.685,.104,.116),(side*.12,legy*.6,.77,.119,.129),(side*.11,legy*.15,.85,.122,.137),(side*.106,0,.922,.115,.129)]
    leg_profiles[side]=pants
    cloth('shorts leg'+suffix,pants,shorts,'shorts',58)
    for z in (.611,.622):
        tube('Character | shorts leg hem'+suffix,[cloth_point(pants,z,j*math.tau/80,'shorts')+Vector((math.cos(j*math.tau/80),math.sin(j*math.tau/80),0))*.001 for j in range(81)],.00065,cotton_thread)
    # Pocket curves sit on the rear quarter of each leg; no floating white V.
    pocket=[]
    for a,z in [(4.12,.846),(4.13,.79),(4.65,.77),(5.14,.79),(5.15,.846)]:
        pocket.append(cloth_point(pants,z,a,'shorts')+Vector((0,-.0018,0)))
    tube('Character | back pocket seam'+suffix,pocket,.00065,cotton_thread)

    # Low canvas shoes with a flat welt and separate heel/toe profile.
    for part,material,height in [('sneaker sole',sole,0),('canvas sneaker',shoe_fabric,1)]:
        verts=[]
        sections=[(-.112,.041,.026),(-.095,.060,.046),(-.04,.063,.059),(.025,.062,.062),(.10,.061,.043),(.154,.042,.030),(.168,.012,.010)]
        for yy,width,h in sections:
            for j in range(32):
                a=j*math.tau/32
                z=.045+(.031+.018*math.sin(a) if not height else .042+h*max(0,math.sin(a)))
                verts.append(bodypt((side*.14+width*math.cos(a),legy+yy,z)))
        faces=[(k*32+j,k*32+(j+1)%32,(k+1)*32+(j+1)%32,(k+1)*32+j) for k in range(len(sections)-1) for j in range(32)]
        faces.extend([tuple(range(31,-1,-1)),tuple((len(sections)-1)*32+j for j in range(32))])
        obj=mesh('Character | '+part+suffix,verts,faces,material,True)
        obj.modifiers.new('Canvas shoe surface','SUBSURF').levels=1
    for k in range(5):
        yy=legy-.015+k*.018
        tube('Character | shoe lace'+suffix,[bodypt((side*.14-.031,yy,.136-k*.002)),bodypt((side*.14,yy+.008,.143-k*.002)),bodypt((side*.14+.031,yy+.002,.136-k*.002))],.0022,sole)
    tube('Character | shoe lace heel seam'+suffix,[bodypt((side*.14-.028,legy-.110,.089)),bodypt((side*.14,legy-.115,.111)),bodypt((side*.14+.028,legy-.110,.089))],.0009,cotton_thread)
    box('Character | canvas sneaker heel tab'+suffix,bodypt((side*.14,legy-.105,.121)),(.019,.008,.030),shoe_fabric,.003)

# Fit the covered thigh under the garment; keep exposed calf anatomy intact.
# The source thigh widens above the knee and otherwise pierces the narrow hem.
for vertex in bpy.data.objects['Character | anatomical legs'].data.vertices:
    p=vertex.co-origin
    if p.z<=.56:continue
    side=1 if p.x>0 else -1
    x,y,_,rx,ry=ring_at(leg_profiles[side],p.z)
    radius=math.sqrt(((p.x-x)/rx)**2+((p.y-y)/ry)**2)
    if radius>.90:
        blend=min(1,(p.z-.56)/.045)
        factor=1+(.90/radius-1)*blend
        p.x=x+(p.x-x)*factor;p.y=y+(p.y-y)*factor
        vertex.co=p+origin

# Fuse the closed garment volumes into one continuous pair of shorts. This
# removes the separate-tube crotch and the belt-like lower edge of the yoke.
parts=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Character | shorts leg')]
vertices=[];faces=[]
for obj in parts:
    offset=len(vertices);vertices.extend([v.co.copy() for v in obj.data.vertices])
    faces.extend([tuple(offset+i for i in p.vertices) for p in obj.data.polygons])
    sides=80;n=len(obj.data.vertices)
    faces.extend([tuple(offset+j for j in range(sides-1,-1,-1)),tuple(offset+n-sides+j for j in range(sides))])
    bpy.data.objects.remove(obj,do_unlink=True)
pants=mesh('Character | shorts leg continuous tailoring',vertices,faces,shorts,True)
remesh=pants.modifiers.new('Continuous cotton garment surface','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.003;remesh.use_smooth_shade=True
smooth=pants.modifiers.new('Soft garment joins','SMOOTH');smooth.factor=.65;smooth.iterations=4
# Apply the union before posing so folds and the crotch deform together.
bpy.context.view_layer.objects.active=pants
for modifier in list(pants.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
# Open the leg hems after the volume union. Filled end caps intersected the
# anatomical thighs and left a dark horizontal patch beneath the shorts.
import bmesh
bm=bmesh.new();bm.from_mesh(pants.data)
bottom=[v for v in bm.verts if v.co.z<origin.z+.609]
bmesh.ops.delete(bm,geom=bottom,context='VERTS')
bm.to_mesh(pants.data);bm.free();pants.data.update()
hem=pants.modifiers.new('Cotton hem thickness','SOLIDIFY');hem.thickness=.0015

# Small opposing arm swing and relaxed fingers produce an ordinary walking
# stance. Every visible cuff, sleeve and hand is moved together.
for obj in list(scene.objects):
    if not obj.name.startswith('Character | '):continue
    if not any(word in obj.name for word in ('sleeve','anatomical left hand','anatomical right hand')):continue
    points=list(obj.data.vertices) if obj.type=='MESH' else [p for s in obj.data.splines for p in s.points] if obj.type=='CURVE' else []
    for point in points:
        p=Vector(point.co[:3])-origin
        side=1 if p.x>0 else -1
        pivot=Vector((side*.23,0,1.405))
        p=pivot+Matrix.Rotation(-side*.09,3,'X')@(p-pivot)
        point.co=p+origin if obj.type=='MESH' else (*(p+origin),1)

# Fuse the posed sleeves and torso so the shoulder is one cloth surface.
# The teal panels and stitching are fitted onto the resulting geometry.
parts=[o for o in scene.objects if o.type=='MESH' and (o.name=='Character | tailored slate jacket' or o.name.startswith('Character | shaped sleeve'))]
vertices=[];faces=[]
for obj in parts:
    offset=len(vertices);vertices.extend([v.co.copy() for v in obj.data.vertices])
    faces.extend([tuple(offset+i for i in p.vertices) for p in obj.data.polygons])
    n=len(obj.data.vertices);sides=80
    faces.extend([tuple(offset+j for j in range(sides-1,-1,-1)),tuple(offset+n-sides+j for j in range(sides))])
    bpy.data.objects.remove(obj,do_unlink=True)
coat_surface=mesh('Character | tailored slate jacket',vertices,faces,jacket,True)
remesh=coat_surface.modifiers.new('Continuous jacket construction','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.0025;remesh.use_smooth_shade=True
smooth=coat_surface.modifiers.new('Soft shoulder joins','SMOOTH');smooth.factor=.45;smooth.iterations=3
bpy.context.view_layer.objects.active=coat_surface
for modifier in list(coat_surface.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
surface=BVHTree.FromObject(coat_surface,bpy.context.evaluated_depsgraph_get())
for obj in scene.objects:
    if not obj.name.startswith('Character | ') or not any(name in obj.name for name in ('yoke','jacket panel seam','sleeve seam','front welt pocket')):continue
    if obj.type=='MESH' and 'yoke' in obj.name:
        # Inner sleeve panels are buried by the torso union. Projecting those
        # hidden vertices onto the nearest exterior made a stray teal sliver.
        bm=bmesh.new();bm.from_mesh(obj.data)
        buried=[]
        for vertex in bm.verts:
            location,normal,_,distance=surface.find_nearest(vertex.co)
            if location is not None and (vertex.co-location).dot(normal)<-.006:buried.append(vertex)
        bmesh.ops.delete(bm,geom=buried,context='VERTS')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    points=list(obj.data.vertices) if obj.type=='MESH' else [p for s in obj.data.splines for p in s.points] if obj.type=='CURVE' else []
    for point in points:
        location,normal,_,distance=surface.find_nearest(Vector(point.co[:3]))
        if location is not None and distance<.04:
            value=location+normal*.0015
            point.co=value if obj.type=='MESH' else (*value,1)
scene['continuous_jacket']=True

# Layered landscape: narrow grasses, flowering stems, small groundcover and
# broad shrub leaves occupy different heights instead of one leaf cloud.
grass_mat=mat('Landscape | sage grass',(.16,.22,.060),.88)
grass_tip=mat('Landscape | dry seed tips',(.37,.31,.13),.95)
flower_mat=mat('Landscape | muted lavender flowers',(.27,.16,.32),.9)

def grasses(name,centers,basez=.83,count=110,height=.40):
    verts=[];faces=[]
    for cx,cy in centers:
        for k in range(count):
            a=random.uniform(0,math.tau);lean=random.uniform(.08,.25)
            x=cx+random.gauss(0,.09);y=cy+random.gauss(0,.09)
            h=random.uniform(.4,1)*height;w=random.uniform(.004,.012)
            n=len(verts)
            for j in range(6):
                f=j/5;xx=x+math.cos(a)*lean*f*f;yy=y+math.sin(a)*lean*f*f
                verts.extend([(xx-math.sin(a)*w*(1-f),yy+math.cos(a)*w*(1-f),basez+h*f),(xx+math.sin(a)*w*(1-f),yy-math.cos(a)*w*(1-f),basez+h*f)])
            faces.extend([(n+j*2,n+j*2+1,n+j*2+3,n+j*2+2) for j in range(5)])
    return mesh(name,verts,faces,grass_mat,True)

for x in (1.3,18.8):
    for y in (3,11,24,35):
        grasses('Civic | tufted grasses',[(x-.22,y-.83),(x+.22,y+.82)],height=.55)
        for k in range(13):
            xx=x+random.uniform(-.3,.3);yy=y+random.uniform(-.9,.9);h=random.uniform(.28,.54)
            branch('Civic | lavender stem',(xx,yy,.83),(xx+.025,yy,.83+h),.002,.001,grass_mat)
            sphere('Civic | lavender flower',(xx+.025,yy,.83+h),(.016,.016,.052),flower_mat,8,6)

# A long limestone seat anchors the foreground just as in the target image.
for y in (-.5,35.5):
    box('Civic | long seat top',(5.5,y,.50),(5.1,.72,.16),stonewall,.025)
    for x in (3.20,7.8):box('Civic | long seat leg',(x,y,.245),(.24,.70,.49),stone,.018)
    box('Civic | long seat back inlay',(5.5,y+.365,.49),(4.8,.014,.063),teal,.003)
    # Five separate oak slats preserve a tactile, crafted seat surface.
    for j in range(5):box('Civic | seat oak slat',(5.5,y-.27+j*.135,.595),(4.65,.115,.035),wood,.009)
for x,y in [(8.7,-.5),(8.7,35.5)]:
    box('Civic | garden end planter',(x,y,.46),(1.15,1.25,.92),stonewall,.035)
    box('Civic | garden end soil',(x,y,.923),(.94,1.04,.01),soil)
    box('Civic | garden end teal',(x,y-.634,.54),(1.03,.016,.075),teal,.003)
    leaf_cloud('Civic | sage shrub',[(x,y,1.13)],.50,850)
    grasses('Civic | planter grasses',[(x-.30,y-.24),(x+.30,y+.24)],.93,90,.6)

# Groundcover at tree bases and loose fallen leaves connect planting to paving.
for x,y,s in [(-2.4,7.5,1.35),(-3.8,17,1),(-3.8,28,1.1),(-3.8,38,.95),(19,4,.95),(19,15,1.1),(19,28,1),(2,40,.9),(12,40,1.05)]:
    grasses('Civic | tree pit groundcover',[(x+.5*s,y),(x-.5*s,y),(x,y+.5*s),(x,y-.5*s)],.34,75,.24)
    leaf_cloud('Civic | low tree pit foliage',[(x+.5*s,y,.49),(x-.5*s,y,.49)],.22,170)
fallen=mat('Landscape | fallen ochre leaves',(.22,.14,.055),.98)
verts=[];faces=[]
for k in range(450):
    x=random.uniform(-5.8,1.1);y=random.uniform(-4,39)
    a=random.uniform(0,math.tau);u=Vector((math.cos(a),math.sin(a),0))*.04;v=Vector((-math.sin(a),math.cos(a),0))*.021;c=Vector((x,y,.052))
    n=len(verts);verts.extend([c-u,c-v,c+u,c+v,c+Vector((0,0,.007))]);faces.extend([(n,n+1,n+4),(n+1,n+2,n+4),(n+2,n+3,n+4),(n+3,n,n+4)])
mesh('Civic | scattered fallen leaves',verts,faces,fallen)

# Balcony planting softens the sharp, repeated architectural silhouettes.
for yy in (7,15,23,31):
    for bay in (-2.12,2.12):
        box('Balcony | planted trough',(-6.45,yy+bay,4.05),(.38,1.35,.32),clay,.018)
        leaf_cloud('Civic | balcony trailing planting',[(-6.40,yy+bay-.42,4.28),(-6.4,yy+bay+.40,4.28),(-6.18,yy+bay,3.88)],.27,230)

# Real geometry in the arena gives its reflective glass something to reveal.
for z in (3.1,6.1,9.1):
    tube('Arena | interior concourse edge',[(3+14.4*math.cos(i*math.tau/128),62+9.4*math.sin(i*math.tau/128),z) for i in range(128)],.12,stone,True)
arena_bs=arena_glass.node_tree.nodes.get('Principled BSDF')
arena_bs.inputs['Metallic'].default_value=.24
arena_bs.inputs['Transmission Weight'].default_value=.30
arena_bs.inputs['Roughness'].default_value=.16

scene['character_landscape_development']='tailoring and layered landscape v2'

# Give the arena a landscaped approach and breathing room behind the court.
for obj in list(scene.objects):
    if not obj.name.startswith('Arena | '):continue
    if obj.type=='MESH':
        for v in obj.data.vertices:
            v.co.x=3+(v.co.x-3)*.88
            v.co.y=62+(v.co.y-62)*.88+13
            v.co.z*=.90
    elif obj.type=='CURVE':
        for spline in obj.data.splines:
            for p in spline.points:
                p.co.x=3+(p.co.x-3)*.88;p.co.y=62+(p.co.y-62)*.88+13;p.co.z*=.90

# A forecourt garden is divided into low, traversable islands by the broad
# central stair axis. The play surface itself remains unobstructed.
for x in (-3.5,11.5):
    for y in (46,52):
        box('Civic | forecourt garden curb',(x,y,.20),(4.3,4.3,.40),stone,.035)
        box('Civic | forecourt garden soil',(x,y,.405),(4.04,4.04,.025),soil)
        for xx in (x-1.3,x,x+1.3):
            leaf_cloud('Civic | forecourt low shrubs',[(xx,y-1.3,.65),(xx,y+1.3,.65)],.40,320)
        grasses('Civic | forecourt mixed grasses',[(x-.8,y),(x+.8,y)],.42,160,.60)
        tree(x,y,.87)
for y in (51,62):
    facade(-11.5,y,10.85,random.choice((9.0,11.7)),terra=True)
    facade(22.0,y,10.85,random.choice((10.7,12.2)),True,False)

# Irregular cypress silhouettes above roof gardens echo the reference's green
# skyline and add a second recognizable tree habit to the scene.
for x,y,z in [(-9.2,19,9.8),(-9.3,34,11.0),(22.5,22,11.0),(23,40,10.6),(20,53,12)]:
    roofs=[]
    for obj in scene.objects:
        if not obj.name.startswith('Building | masonry volume'):continue
        vs=obj.data.vertices
        if min(v.co.x for v in vs)<=x<=max(v.co.x for v in vs) and min(v.co.y for v in vs)<=y<=max(v.co.y for v in vs):
            roofs.append(max(v.co.z for v in vs))
    if not roofs:continue
    z=max(roofs)
    box('Balcony | roof tree planter',(x,y,z+.27),(1.05,1.05,.54),clay,.025)
    branch('Oak | cypress trunk',(x,y,z),(x,y,z+3.5),.075,.015,bark)
    leaf_cloud('Oak | cypress foliage',[(x,y,z+.7),(x,y,z+1.25),(x,y,z+1.8),(x,y,z+2.35),(x,y,z+2.8)],.52,750)
