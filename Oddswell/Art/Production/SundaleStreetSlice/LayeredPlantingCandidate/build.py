"""Native layered planting, preserving the retained scene and licensed sources."""
import bpy,ast,hashlib,json,math,random
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';source=art/'RetailDepthCandidate/RetailDepth.blend';expected='6c799e05c928b6feae19a257144b6e47cdaff5539dda3a6e4a22b64599290b91'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(7);old=set(bpy.data.objects)
parsed=ast.parse((art/'build_scene.py').read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('mesh','tube')],type_ignores=[]),str(art/'build_scene.py'),'exec'))
collection=bpy.data.collections.new('OddsWell | layered civic planting');scene.collection.children.link(collection)
hidden=[]
prefixes=('Civic | shrub woody stem','Civic | broadleaf shrub cluster','Civic | tufted grasses','Civic | lavender stem','Civic | lavender flower','Civic | planter grasses','Civic | tree pit groundcover')
for o in scene.objects:
    if o.name.startswith(prefixes) and not o.hide_render:
        hidden.append({'name':o.name,'old_hide_render':False});o.hide_render=True;o.hide_set(True)

def material(name,color,rough=.72,leaf=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough;n.inputs['Specular IOR Level'].default_value=.25
    if leaf:n.inputs['Subsurface Weight'].default_value=.04;n.inputs['Subsurface Radius'].default_value=(.12,.22,.07)
    return m
foliage=[material('Planting | living leaf '+str(i),c,.62,True) for i,c in enumerate(((.035,.075,.018),(.056,.105,.025),(.085,.135,.032),(.105,.145,.042),(.065,.102,.040)))]
sage=material('Planting | bent sage blades',(.060,.105,.029),.8,True);bloom=material('Planting | small lavender florets',(.24,.12,.29),.82);mulch=material('Planting | dark leaf litter',(.068,.043,.022),.97)
bark=bpy.data.materials['OW | rough oak bark']
rng=random.Random(61026);stats=[]

def leaves(name,items):
    verts=[];faces=[];indices=[]
    for center,length,width,angle,tilt,color in items:
        u=Vector((math.cos(angle)*math.cos(tilt),math.sin(angle)*math.cos(tilt),math.sin(tilt)));v=Vector((-math.sin(angle),math.cos(angle),0));base=len(verts)
        for j in range(7):
            t=j/6;w=math.sin(math.pi*t)**.75*width;mid=center+u*length*(t-.13)+Vector((0,0,.009*math.sin(math.pi*t)))
            verts.extend((mid-v*w,mid+Vector((0,0,.0025*math.sin(math.pi*t))),mid+v*w))
        for j in range(6):
            for k in range(2):n=base+3*j+k;faces.append((n,n+3,n+4,n+1));indices.append(color)
    o=mesh(name,verts,faces,foliage[0],True)
    for m in foliage[1:]:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,indices):p.material_index=i
    o['authored_leaf_count']=len(items);return o

def branches(name,segments):
    verts=[];faces=[]
    for a,b,ra,rb in segments:
        rot=(b-a).to_track_quat('Z','Y');n=len(verts)
        verts.extend(center+rot@Vector((radius*math.cos(j*math.tau/6),radius*math.sin(j*math.tau/6),0)) for center,radius in ((a,ra),(b,rb)) for j in range(6))
        faces.extend([(n+j,n+(j+1)%6,n+(j+1)%6+6,n+j+6) for j in range(6)])
        faces.extend((tuple(n+j for j in range(5,-1,-1)),tuple(n+6+j for j in range(6))))
    return mesh(name,verts,faces,bark,True)

def grasses(name,centers,z):
    verts=[];faces=[]
    for cx,cy,height in centers:
        for k in range(52):
            a=rng.uniform(0,math.tau);h=height*rng.uniform(.5,1.1);lean=h*rng.uniform(.28,.75);w=rng.uniform(.002,.0045);x=cx+rng.gauss(0,.035);y=cy+rng.gauss(0,.035);n=len(verts)
            for j in range(9):
                t=j/8;c=Vector((x+math.cos(a)*lean*t*t,y+math.sin(a)*lean*t*t,z+h*t-h*.15*t**4));v=Vector((-math.sin(a),math.cos(a),0))*w*(1-t)**.7;verts.extend((c-v,c+v))
            faces.extend((n+j*2,n+j*2+1,n+j*2+3,n+j*2+2) for j in range(8))
    return mesh(name,verts,faces,sage,True)

def flowers(name,centers,z):
    stems=[];verts=[];faces=[]
    for x,y in centers:
        h=rng.uniform(.20,.31);base=Vector((x,y,z));tip=base+Vector((rng.uniform(-.04,.04),rng.uniform(-.04,.04),h));stems.append((base,tip,.0014,.0006))
        for k in range(14):
            a=k*2.39996;f=k/13;r=.009*(.4+math.sin(math.pi*f));c=tip+Vector((r*math.cos(a),r*math.sin(a),f*.035));n=len(verts)
            verts.append(c+Vector((0,0,.0025)))
            verts.extend(c+Vector((.0038*math.cos(j*math.tau/5),.0038*math.sin(j*math.tau/5),-.001)) for j in range(5))
            faces.extend((n,n+1+j,n+1+(j+1)%5) for j in range(5))
    stem=branches(name+' stems',stems);stem.data.materials.clear();stem.data.materials.append(sage)
    return mesh(name+' florets',verts,faces,bloom,True)

def bed(label,x,y,hx,hy,z,tree=False):
    segments=[];upper=[];low=[]
    centers=[(x-hx*.27,y-hy*.50,.37),(x+hx*.12,y+hy*.02,.49),(x-hx*.12,y+hy*.52,.40)] if not tree else []
    for bx,by,nominal in centers:
        height=nominal*rng.uniform(.86,1.12);root=Vector((bx,by,z))
        for k in range(24):
            a=k*2.39996+rng.uniform(-.3,.3);reach=rng.uniform(.10,.22);top=root+Vector((math.cos(a)*reach,math.sin(a)*reach,height*rng.uniform(.65,1)));bend=root.lerp(top,.50)+Vector((0,0,.025));segments.extend(((root,bend,.0045,.0025),(bend,top,.0025,.0010)))
            for j in range(7):
                f=.22+j*.12;c=bend.lerp(top,(f-.5)/.5) if f>.5 else root.lerp(bend,f/.5)
                for side in (-1,1):
                    la=a+side*rng.uniform(.85,1.7);endpoint=c+Vector((math.cos(la)*.045,math.sin(la)*.045,.015));segments.append((c,endpoint,.0008,.0003));upper.append((endpoint,rng.uniform(.048,.075),rng.uniform(.016,.025),la,rng.uniform(-.15,.50),rng.randrange(5)))
            for j in range(18):
                c=top+Vector((rng.uniform(-.075,.075),rng.uniform(-.075,.075),rng.uniform(-.11,.01)));upper.append((c,rng.uniform(.05,.078),rng.uniform(.018,.026),rng.uniform(0,math.tau),rng.uniform(-.3,.6),rng.randrange(5)))
    if segments:branches(label+' branching shrubs',segments);leaves(label+' shrub leaves',upper)
    # Separate patches leave visible soil and root space rather than filling a rectangle.
    patches=[(x-hx*.53,y-hy*.70),(x+hx*.50,y+hy*.51),(x-hx*.49,y+hy*.23),(x+hx*.43,y-hy*.23),(x-hx*.45,y-hy*.30),(x+hx*.47,y+hy*.01),(x-hx*.12,y+hy*.75)]
    for px,py in patches:
        for k in range(70):
            cx=px+rng.gauss(0,hx*.20);cy=py+rng.gauss(0,hy*.12)
            if abs(cx-x)>hx*.88 or abs(cy-y)>hy*.9:continue
            if tree and math.hypot(cx-x,cy-y)<.38:continue
            base=Vector((cx,cy,z+.012))
            for j in range(6):
                a=j*math.tau/6+rng.uniform(-.15,.15);low.append((base+Vector((0,0,rng.uniform(.006,.045))),rng.uniform(.040,.066),rng.uniform(.015,.024),a,rng.uniform(.08,.30),rng.randrange(5)))
    leaves(label+' groundcover rosettes',low)
    grasses(label+' curved grass tufts',[(x+hx*.48,y-hy*.72,.22),(x-hx*.44,y+hy*.72,.27)],z)
    if not tree:flowers(label+' lavender',[(x+rng.uniform(-hx*.55,hx*.55),y+rng.uniform(-hy*.85,hy*.85)) for k in range(20)],z)
    litter=[]
    for k in range(210):
        xx=x+rng.uniform(-hx*.9,hx*.9);yy=y+rng.uniform(-hy*.9,hy*.9)
        if tree and math.hypot(xx-x,yy-y)<.38:continue
        litter.append((Vector((xx,yy,z+.003)),rng.uniform(.018,.045),rng.uniform(.006,.012),rng.uniform(0,math.tau),0,0))
    o=leaves(label+' soil leaf litter',litter);o.data.materials.clear();o.data.materials.append(mulch)
    for p in o.data.polygons:p.material_index=0
    stats.append({'bed':label,'soil_center':[x,y,z],'soil_half_size':[hx,hy],'shrub_leaves':len(upper),'groundcover_leaves':len(low),'litter_leaves':len(litter)})

for o in list(scene.objects):
    if o.name.startswith(('Civic | soil','Civic | garden end soil','Tree pit soil')):
        b=[o.matrix_world@Vector(p) for p in o.bound_box];lo=Vector(tuple(min(p[i] for p in b) for i in range(3)));hi=Vector(tuple(max(p[i] for p in b) for i in range(3)));c=(lo+hi)/2
        if o.name.startswith('Tree pit soil') and c.z>1:continue
        bed('Planting | '+o.name,c.x,c.y,(hi.x-lo.x)/2,(hi.y-lo.y)/2,hi.z+.0007,o.name.startswith('Tree pit soil'))
added=[o for o in bpy.data.objects if o not in old]
for o in added:
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o)
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(7);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'LayeredPlanting.blend'),compress=True)
with (out/'LayeredPlanting.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'candidate_sha256':sha,'source_sha256':expected,'changed_visibility':hidden,'added_objects':[o.name for o in added],'beds':stats,'new_bitmap_assets':0,'seed':61026,'scope':'Native branching shrubs, low rosettes, curved grass, small florets and leaf litter. Original plants retained hidden; original soil, planters, trees, architecture, retail, human and lighting untouched.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PLANTING_BUILT',len(added),len(hidden),len(stats),sha,flush=True)
