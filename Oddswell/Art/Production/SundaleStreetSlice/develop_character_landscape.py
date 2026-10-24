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
shoe_lining=mat('Character | shadowed canvas lining',(.085,.080,.065),.95,260)
for node in sole.node_tree.nodes:
    if node.type=='BUMP':node.inputs['Distance'].default_value=.0002;node.inputs['Strength'].default_value=.12
    if node.type=='VALTORGB':
        node.color_ramp.elements[0].color=(.61,.60,.54,1)
        node.color_ramp.elements[1].color=(.65,.64,.58,1)
jacket.diffuse_color=(.026,.039,.055,1)
jacket.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value=.08
jacket.node_tree.nodes.get('Principled BSDF').inputs['Sheen Roughness'].default_value=.80
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
        # Broad panels stay quiet; cloth gathers where the waistband and
        # armholes constrain it, rather than forming full-height fluting.
        fold+=.0015*math.sin(a*15+z*4)*math.exp(-((z-1.23)/.17)**2)
        # Diagonal compression folds above the hem, terminating at side seams.
        for crest,center in ((.976,3.75),(1.025,5.3),(1.070,3.5)):
            d=z-(crest+.065*math.cos(a*2+.7))
            localized=math.exp(-((a-center)/.45)**2)
            fold+=localized*(.004*math.exp(-(d/.018)**2)-.0015*math.exp(-((d+.022)/.016)**2))
        fold+=.001*math.sin(a*8-z*21)*math.exp(-((z-1.36)/.09)**2)
        for center,height,slope in ((.72,1.04,.08),(1.8,1.015,-.065),(2.45,1.11,-.10)):
            d=z-height-slope*(a-center)
            fold+=.005*math.exp(-((a-center)/.34)**2)*(math.exp(-(d/.013)**2)-.4*math.exp(-((d+.017)/.012)**2))
        for center,height,slope,depth in ((.32,1.23,-.12,.007),(2.82,1.25,.14,.006),(3.40,1.22,-.08,.006),(6.02,1.205,.08,.005),(4.00,1.008,.052,.005),(5.40,1.036,-.034,.004),(1.00,1.025,-.085,.006),(2.1,1.015,.095,.005)):
            da=(a-center+math.pi)%math.tau-math.pi
            d=z-height-slope*da
            width=.28 if center>3.1 else .43
            fold+=depth*math.exp(-(da/width)**2)*(math.exp(-(d/.014)**2)-.42*math.exp(-((d+.021)/.016)**2))
        fold*=max(0,min(1,(z-.942)/.030))
    elif kind=='sleeve':
        gather=math.exp(-((z-1.15)/.06)**2)+.4*math.exp(-((z-.955)/.035)**2)
        fold=.004*math.sin(z*100+a*3)*gather*(.5+.5*math.sin(a+z*2))+.0006*math.sin(a*9+z*9)
        for center,height,slope,depth in ((1.5,1.13,.023,.008),(1.7,1.17,-.025,.007),(4.4,1.09,-.018,.006),(4.8,.994,.025,.007),(1.0,.974,-.020,.006)):
            da=(a-center+math.pi)%math.tau-math.pi
            d=z-height-slope*da
            fold+=depth*math.exp(-(da/.85)**2)*(math.exp(-(d/.009)**2)-.40*math.exp(-((d+.014)/.010)**2))
        fold*=max(0,min(1,(z-.945)/.035))
    elif kind=='shorts':
        fold=.0012*math.sin(a*9+z*11)
        # Local diagonal gathers interrupt the broad cotton volume; each
        # crease tapers before reaching the side seam or an adjacent fold.
        for angle,height,slope,depth in ((3.9,.83,.045,.005),(4.95,.805,-.060,.006),(5.4,.74,.045,.004),(4.2,.67,.030,.004),(5.25,.66,-.040,.003),(1.1,.78,-.055,.007),(2.1,.72,.070,.006),(.6,.66,-.055,.004),(1.65,.64,.045,.003)):
            da=(a-angle+math.pi)%math.tau-math.pi
            d=z-height-slope*da
            mask=math.exp(-(da/.42)**2-((z-height)/.13)**2)
            fold+=mask*(depth*math.exp(-(d/.009)**2)-depth*.45*math.exp(-((d+.012)/.011)**2))
    else:
        fold=.00045*math.cos(a*96)
    px=x+(rx+fold)*math.cos(a);py=y+(ry+fold)*math.sin(a)
    if kind=='shorts' and rx>.18 and math.sin(a)<0:
        py+=.018*math.exp(-(px/.050)**2)*math.exp(-((z-.825)/.065)**2)
    pz=z
    if kind=='collar':
        # Higher at the nape, lower and softer at the front of the throat.
        pz-=.012*max(0,math.sin(a))**6*max(0,min(1,(z-1.49)/.036))
    if kind=='sleeve' and z>1.38:
        side=1 if x>0 else -1
        pz-=.029*min(1,(z-1.38)/.065)*(1+side*math.cos(a))*.5
    return bodypt((px,py,pz))

def cloth(name,rings,material,kind,steps=110,sides=80):
    if kind in ('rib','collar'):sides=384
    lo,hi=rings[0][2],rings[-1][2]
    vertices=[cloth_point(rings,lo+(hi-lo)*k/steps,j*math.tau/sides,kind) for k in range(steps+1) for j in range(sides)]
    faces=[(k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j) for k in range(steps) for j in range(sides)]
    obj=mesh('Character | '+name,vertices,faces,material,True)
    sub=obj.modifiers.new('Tailoring surface','SUBSURF');sub.levels=1
    solid=obj.modifiers.new('Garment edge thickness','SOLIDIFY');solid.thickness=.0015
    return obj

coat=[(0,0,.915,.190,.114),(0,0,.95,.205,.128),(0,.006,1.02,.212,.133),(0,.012,1.15,.219,.134),(0,.014,1.31,.240,.138),(0,.012,1.395,.243,.128),(0,.007,1.43,.221,.116),(0,0,1.48,.099,.080)]
cloth('tailored slate jacket',coat,jacket,'coat')
cloth('ribbed waistband',[(0,0,.897,.194,.120),(0,0,.922,.199,.124),(0,0,.943,.207,.133)],rib,'rib',12)
collar=[(0,0,1.47,.095,.082),(0,.004,1.487,.086,.075),(0,.009,1.507,.073,.068),(0,.012,1.526,.068,.065)]
cloth('standing collar',collar,rib,'collar',24)

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
def fastening(z):
    return cloth_point(coat,z,math.pi/2,'coat') if z<=1.48 else cloth_point(collar,z,math.pi/2,'collar')
for side in (-1,1):
    tube('Character | front zipper tape',[fastening(.948+k*.00575)+Vector((side*.0026,.0016,0)) for k in range(101)],.0011,thread)
    tube('Character | front welt pocket',[cloth_point(coat,1.005+k*.004,(.72 if side>0 else math.pi-.72)+side*k*.003,'coat')+Vector((0,.0018,0)) for k in range(27)],.0015,rib)
for k in range(180):
    p=fastening(.95+k*.0032)+Vector((0,.002,0))
    box('Character | zipper teeth',p,(.005,.0015,.0012),zipper)
box('Character | zipper slider',fastening(1.517)+Vector((0,.004,0)),(.008,.004,.005),zipper,.001)
pull=[]
for x,z in [(-.0035,1.516),(-.0045,1.501),(-.003,1.498),(.003,1.498),(.0045,1.501),(.0035,1.516)]:
    pull.append(fastening(z)+Vector((x,.005,0)))
tube('Character | zipper pull loop',pull,.0008,zipper,True)

leg_profiles={}
for side in (-1,1):
    suffix=' left' if side<0 else ' right'
    sleeve=[(side*.338,-.016,.924,.038,.036),(side*.339,-.020,.947,.050,.054),(side*.34,-.026,.973,.056,.062),(side*.324,-.040,1.05,.061,.068),(side*.311,-.052,1.15,.071,.074),(side*.30,-.029,1.22,.072,.078),(side*.266,-.003,1.34,.074,.081),(side*.217,.006,1.414,.063,.061),(side*.18,.006,1.445,.046,.047),(side*.135,.006,1.455,.030,.035)]
    cloth('shaped sleeve'+suffix,sleeve,jacket,'sleeve')
    sleeve_yoke=[]
    for k in range(5):
        for j in range(41):
            a=math.pi+j*math.pi/40;z=1.329+k*.009+.008*math.cos(a*2)
            sleeve_yoke.append(cloth_point(sleeve,z,a,'sleeve')+Vector((math.cos(a),math.sin(a),0))*.0018)
    mesh('Character | sleeve signal yoke'+suffix,sleeve_yoke,[(k*41+j,k*41+j+1,(k+1)*41+j+1,(k+1)*41+j) for k in range(4) for j in range(40)],teal,True)
    cuff=[]
    for z,fit in ((.902,0),(.917,.22),(.936,.78),(.945,1)):
        x,y,_,rx,ry=ring_at(sleeve,z)
        cuff.append((x,y,z,.036*(1-fit)+(rx+.0035)*fit,.034*(1-fit)+(ry+.0035)*fit))
    cloth('sleeve cuff'+suffix,cuff,rib,'rib',12)
    # Sewn outer sleeve line is thin and rests on the displaced fabric.
    a=math.pi*1.5
    tube('Character | sleeve seam'+suffix,[cloth_point(sleeve,.95+k*.006,a,'sleeve')+Vector((0,-.001,0)) for k in range(72)],.00065,thread)
    legy=.075 if side==1 else -.065
    pants=[(side*.131,legy*.45,.604,.090,.104),(side*.13,legy*.45,.625,.095,.109),(side*.126,legy*.4,.685,.104,.116),(side*.12,legy*.25,.77,.113,.124),(side*.11,legy*.08,.85,.119,.132),(side*.106,0,.922,.115,.129)]
    leg_profiles[side]=pants
    for z in (.611,.622):
        tube('Character | shorts leg hem'+suffix,[cloth_point(pants,z,j*math.tau/80,'shorts')+Vector((math.cos(j*math.tau/80),math.sin(j*math.tau/80),0))*.001 for j in range(81)],.00065,cotton_thread)
    # Pocket curves sit on the rear quarter of each leg; no floating white V.
    pocket=[]
    corners=[(4.12,.846),(4.13,.79),(4.65,.77),(5.14,.79),(5.15,.846)]
    for start,end in zip(corners,corners[1:]):
        for k in range(12):
            t=k/12;a=start[0]*(1-t)+end[0]*t;z=start[1]*(1-t)+end[1]*t
            pocket.append(cloth_point(pants,z,a,'shorts')+Vector((0,-.0018,0)))
    a,z=corners[-1];pocket.append(cloth_point(pants,z,a,'shorts')+Vector((0,-.0018,0)))
    tube('Character | back pocket seam'+suffix,pocket,.00065,cotton_thread)

    # Low canvas shoes with a flat welt and separate heel/toe profile.
    for part,material,height in [('sneaker sole',sole,0),('canvas sneaker',shoe_fabric,1)]:
        verts=[]
        sections=[(-.130,.004,.042),(-.125,.029,.057),(-.112,.048,.082),(-.095,.056,.093),(-.04,.062,.103),(.025,.062,.080),(.10,.058,.046),(.154,.044,.031),(.165,.036,.024),(.174,.023,.019),(.179,.009,.017),(.180,.004,.017)]
        shoe_profile=[(0,0,y,w,h) for y,w,h in sections]
        stations=sorted({round(sections[0][0]+(sections[-1][0]-sections[0][0])*k/48,7) for k in range(49)}|{s[0] for s in sections})
        shoe_sides=64 if height else 68
        for yy in stations:
            _,_,_,width,h=ring_at(shoe_profile,yy)
            if height:
                for j in range(shoe_sides):
                    a=j*math.tau/shoe_sides
                    verts.append(bodypt((side*.14+width*math.cos(a),legy+yy,.080+(h+.007)*max(0,math.sin(a))+.003*min(0,math.sin(a)))))
            else:
                # Flat top/bottom and vertical sidewalls, with a 3 mm edge
                # radius. An elliptical section supported only its midline.
                rx=width+.004;r=.003
                for quadrant,(cx,cz) in enumerate(((rx-r,.088-r),(-rx+r,.088-r),(-rx+r,.058+r),(rx-r,.058+r))):
                    for j in range(17):
                        a=quadrant*math.pi/2+j*math.pi/32
                        verts.append(bodypt((side*.14+cx+r*math.cos(a),legy+.025+(yy-.025)*1.025,cz+r*math.sin(a))))
        faces=[(k*shoe_sides+j,k*shoe_sides+(j+1)%shoe_sides,(k+1)*shoe_sides+(j+1)%shoe_sides,(k+1)*shoe_sides+j) for k in range(len(stations)-1) for j in range(shoe_sides)]
        faces.extend([tuple(range(shoe_sides-1,-1,-1)),tuple((len(stations)-1)*shoe_sides+j for j in range(shoe_sides))])
        obj=mesh('Character | '+part+suffix,verts,faces,material,True)
        import bmesh
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        obj.modifiers.new('Canvas shoe surface','SUBSURF').levels=1
        if height:
            # Recess the ankle opening into the evaluated upper. The footbed
            # and inner walls close the mesh while making the collar real.
            bpy.context.view_layer.objects.active=obj
            bpy.ops.object.modifier_apply(modifier='Canvas shoe surface')
            cut_vertices=[bodypt((side*.149+.034*math.cos(j*math.tau/64),legy-.030+.044*math.sin(j*math.tau/64),z)) for z in (.120,.32) for j in range(64)]
            cut_faces=[(j,(j+1)%64,64+(j+1)%64,64+j) for j in range(64)]
            cut_faces.extend([tuple(range(63,-1,-1)),tuple(range(64,128))])
            cutter=mesh('STUDY | ankle opening',cut_vertices,cut_faces,shoe_fabric)
            recess=obj.modifiers.new('Open padded ankle collar','BOOLEAN');recess.operation='DIFFERENCE';recess.solver='EXACT';recess.object=cutter
            bpy.ops.object.modifier_apply(modifier=recess.name)
            bpy.data.objects.remove(cutter,do_unlink=True)
            obj.data.materials.append(shoe_lining)
            for polygon in obj.data.polygons:
                p=polygon.center-origin
                radial=Vector(((p.x-side*.149)/.034,(p.y-legy+.030)/.044,0))
                if radial.length<1.1 and (polygon.normal.dot(radial)<-.30 or abs(p.z-.120)<.001):polygon.material_index=1
                polygon.use_smooth=True
            edge=obj.modifiers.new('Soft canvas opening edge','BEVEL');edge.width=.0007;edge.segments=2
            edge.limit_method='ANGLE';edge.angle_limit=.60
    def shoe_top(x,y,lift=0):
        _,_,_,w,h=ring_at(shoe_profile,y)
        return bodypt((side*.14+x,legy+y,.080+(h+.007)*math.sqrt(max(0,1-(x/w)**2))+lift))
    tongue=[shoe_top(-.030+j*.005,.030+k*.0044,.0015) for k in range(21) for j in range(13)]
    tongue_mesh=mesh('Character | canvas sneaker tongue'+suffix,tongue,[(k*13+j,k*13+j+1,(k+1)*13+j+1,(k+1)*13+j) for k in range(20) for j in range(12)],shoe_fabric,True)
    tube('Character | shoe lace collar seam'+suffix,[shoe_top(side*.009+.035*math.cos(j*math.tau/96),-.030+.045*math.sin(j*math.tau/96),.001) for j in range(97)],.0012,cotton_thread)
    for k in range(4):
        yy=.035+k*.020
        if k<3:
            for diagonal in (-1,1):
                lace=tube('Character | shoe lace'+suffix,[shoe_top(diagonal*(-.030+i*.060/20),yy+.020*i/20,.001) for i in range(21)],.0012,sole)
                lace['lace_threading']=True;lace['crossing_offset_m']=.0028 if diagonal>0 else 0
        for sign in (-1,1):
            eyelet=tube('Character | shoe lace eyelet'+suffix,[shoe_top(sign*.030+.003*math.cos(a*math.tau/16),yy+.003*math.sin(a*math.tau/16),.001) for a in range(17)],.00055,zipper)
            eyelet['surface_offset_m']=.0008
    lace=tube('Character | shoe lace'+suffix,[shoe_top(-.030+i*.060/20,.095,.001) for i in range(21)],.0012,sole)
    lace['lace_threading']=True
    for sign in (-1,1):
        loop=tube('Character | shoe lace bow'+suffix,[shoe_top(sign*.014*(1-math.cos(j*math.tau/32)),.029+.009*math.sin(j*math.tau/32),.007) for j in range(33)],.0012,sole)
        loop['bow_loop']=True
        tail=tube('Character | shoe lace free end'+suffix,[shoe_top(sign*(.004+.010*j/16),.029+.027*j/16,.006) for j in range(17)],.0012,sole)
        tail['surface_offset_m']=.006;tail.data.use_fill_caps=True
    sphere('Character | canvas sneaker lace knot'+suffix,shoe_top(0,.029,.006),(.003,.003,.0025),sole,16,8)
    # A stitched toe panel, upper welt and small heel seam break up the
    # otherwise featureless canvas surface at ordinary full-body distance.
    tube('Character | shoe lace toe cap seam'+suffix,[shoe_top(-.050+i*.100/32,.119-.008*math.cos((i/32-.5)*math.pi),.0015) for i in range(33)],.00065,cotton_thread)
    for sign in (-1,1):
        tube('Character | shoe lace quarter seam'+suffix,[shoe_top(sign*.043,-.088+k*.014,.0015) for k in range(12)],.0008,cotton_thread)
    tube('Character | shoe lace heel seam'+suffix,[bodypt((side*.14,legy-.124,.103+j*.004)) for j in range(12)],.0007,cotton_thread)
    # Fit construction details to the evaluated upper, then place the heel
    # behind the ankle with more shoe length in front of the foot.
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    upper=BVHTree.FromObject(bpy.data.objects['Character | canvas sneaker'+suffix],bpy.context.evaluated_depsgraph_get())
    for detail in list(scene.objects):
        if not detail.name.split('.')[0].endswith(suffix) or not any(word in detail.name for word in ('sneaker','shoe lace')):continue
        points=list(detail.data.vertices) if detail.type=='MESH' else [p for spline in detail.data.splines for p in spline.points] if detail.type=='CURVE' else []
        for point_index,point in enumerate(points):
            p=Vector(point.co[:3])
            if detail==tongue_mesh or detail.type=='CURVE':
                location,normal,_,distance=upper.find_nearest(p)
                if location is not None and distance<.025:
                    offset=detail.get('surface_offset_m',.003 if 'lace' in detail.name and 'seam' not in detail.name else .0015)
                    if detail.get('lace_threading'):
                        offset=.0012+(.0026+detail.get('crossing_offset_m',0))*math.sin(math.pi*point_index/(len(points)-1))
                    if detail.get('bow_loop'):offset=.004+.006*math.sin(math.pi*point_index/(len(points)-1))**2
                    p=location+normal*offset
            p.y+=.035
            point.co=p if detail.type=='MESH' else (*p,1)

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

# Tailor a single open garment: the two leg loops share a curved inseam
# bridge and the hip circumference. Overlapping capped tubes left a bulge
# at the fly and a horizontal ledge around the seat after voxel union.
vertices=[];faces=[];sides=80
hip=[(0,0,.80,.215,.132),(0,0,.865,.215,.132),(0,0,.925,.209,.129)]
for k in range(17):
    z=.80+.125*k/16
    vertices.extend(cloth_point(hip,z,j*math.tau/sides,'shorts') for j in range(sides))
for k in range(16):
    faces.extend((k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j) for j in range(sides))
bridge={20:20,60:60}
for j in range(21,60):
    a=j*math.tau/sides
    bridge[j]=len(vertices)
    vertices.append(bodypt((0,.132*math.sin(a),.80+.058*math.cos(a))))
for side in (-1,1):
    top=[]
    for j in range(sides):
        outer=(20<=j<=60) if side<0 else (j<=20 or j>=60)
        top.append(j if outer else bridge[(40-j)%sides] if side<0 else bridge[j])
    previous=None
    for k in range(37):
        t=k/36;z=.609+.191*t
        blend=t**4
        ring=top if k==36 else list(range(len(vertices),len(vertices)+sides))
        if k<36:
            for j in range(sides):
                p=cloth_point(leg_profiles[side],z,j*math.tau/sides,'shorts')
                target=vertices[top[j]].copy()
                target.z-=.191*(1-t)
                vertices.append(p.lerp(target,blend))
        if previous is not None:
            faces.extend((previous[j],previous[(j+1)%sides],ring[(j+1)%sides],ring[j]) for j in range(sides))
        previous=ring
pants=mesh('Character | shorts leg continuous tailoring',vertices,faces,shorts,True)
import bmesh
bm=bmesh.new();bm.from_mesh(pants.data)
# Recalculate the shared saddle consistently before subdivision/thickness.
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges),'Non-manifold shorts tailoring'
bm.to_mesh(pants.data);bm.free();pants.data.update()
sub=pants.modifiers.new('Continuous cotton drape','SUBSURF');sub.levels=2
hem=pants.modifiers.new('Cotton hem thickness','SOLIDIFY');hem.thickness=.0015
from mathutils.bvhtree import BVHTree
bpy.context.view_layer.update()
trouser_surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for obj in scene.objects:
    if not obj.name.startswith('Character | back pocket seam'):continue
    for spline in obj.data.splines:
        for point in spline.points:
            location,normal,_,distance=trouser_surface.find_nearest(Vector(point.co[:3]))
            assert location is not None and distance<.05,'Pocket seam outside tailoring'
            point.co=(*(location+normal*.001),1)

# Small opposing arm swing and relaxed fingers produce an ordinary walking
# stance. Every visible cuff, sleeve and hand is moved together.
for obj in list(scene.objects):
    if not obj.name.startswith('Character | '):continue
    if not any(word in obj.name for word in ('sleeve','anatomical left hand','anatomical right hand')):continue
    points=list(obj.data.vertices) if obj.type=='MESH' else [p for s in obj.data.splines for p in s.points] if obj.type=='CURVE' else []
    for point in points:
        p=Vector(point.co[:3])-origin
        side=1 if p.x>0 else -1
        # Let the forearms return toward the body below the elbows. The
        # upper arm stays clear of the torso so the armpit does not web over.
        inward=max(0,min(1,(1.18-p.z)/.25));inward=inward*inward*(3-2*inward)
        p.x-=side*.047*inward
        pivot=Vector((side*.23,0,1.405))
        elbow=Vector((side*.311,-.052,1.15))
        bend=max(0,min(1,(1.20-p.z)/.13))
        p=elbow+Matrix.Rotation(.12*bend,3,'X')@(p-elbow)
        p=pivot+Matrix.Rotation(-side*.16,3,'X')@(p-pivot)
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
# Relax the narrow sleeve/torso join while retaining the lower-body folds.
shoulder=coat_surface.vertex_groups.new(name='Shoulder transition')
for vertex in coat_surface.data.vertices:
    p=vertex.co-origin
    weight=math.exp(-((p.z-1.405)/.045)**2)*min(1,abs(p.x)/.17)
    if weight>.01:shoulder.add([vertex.index],weight,'REPLACE')
smooth=coat_surface.modifiers.new('Relax shoulder cap','SMOOTH');smooth.factor=1;smooth.iterations=35;smooth.vertex_group=shoulder.name
bpy.ops.object.modifier_apply(modifier=smooth.name)
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

# Bring the padded upper-body silhouette closer to the lean reference.
# Transform cloth, fitted trim and hands together so their joins stay fitted.
for obj in scene.objects:
    if not obj.name.startswith('Character | '):continue
    if any(word in obj.name for word in ('anatomical head','anatomical legs','shorts','back pocket','sneaker','shoe lace')):continue
    points=list(obj.data.vertices) if obj.type=='MESH' else [p for spline in obj.data.splines for p in spline.points] if obj.type=='CURVE' else []
    for point in points:
        p=Vector(point.co[:3])-origin
        chest=max(0,min(1,(p.z-.98)/.22));chest=chest*chest*(3-2*chest)
        arm=max(0,min(1,(abs(p.x)-.21)/.07))
        p.x*=1-.085*max(chest,arm)
        torso=max(0,min(1,(.29-abs(p.x))/.065))
        p.y*=1-.10*torso*math.exp(-((p.z-1.16)/.18)**2)
        point.co=p+origin if obj.type=='MESH' else (*(p+origin),1)
scene['reference_upper_body_fit']=True
scene['body_refinement']='Resting finger curl, articulated arm swing, calf/ankle taper, fitted sneaker instep and localized cloth gathers'

# Layered landscape: narrow grasses, flowering stems, small groundcover and
# broad shrub leaves occupy different heights instead of one leaf cloud.
grass_mat=mat('Landscape | sage grass',(.16,.22,.060),.88)
grass_tip=mat('Landscape | dry seed tips',(.37,.31,.13),.95)
flower_mat=mat('Landscape | muted lavender flowers',(.27,.16,.32),.9)

# The close planters use stemmed broad-leaf growth from the same retained
# foliage family as the canopy, at an ordinary shrub scale.
for obj in list(scene.objects):
    if obj.name.startswith('Civic | planted shrub'):bpy.data.objects.remove(obj,do_unlink=True)
for x in (1.3,18.8):
    for y in (3,11,24,35):
        broadleaf_shrub(x,y-.52,.83,.48,.29)
        broadleaf_shrub(x,y+.48,.83,.57,.29)

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
    broadleaf_shrub(x,y,.93,.58,.38)
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
