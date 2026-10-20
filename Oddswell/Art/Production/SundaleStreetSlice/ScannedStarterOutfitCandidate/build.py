"""Off-white starter outfit and casual sneakers fitted to the accepted scanned human."""
import bpy, json, hashlib, math, ast, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy'
source=out.parent/'MotionRefinement/OddsWellHumanMotion.blend';jacket_source=out.parent/'SignalJacketStudy/OddsWellSignalJacket.blend'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)=='1c75042928c5df6eaa198c1fe032a5b3985224c33b766bd322b7dc10b126aca4'
assert sha(jacket_source)=='fa455707fe273b6230fd19fa7f2a934ae560d81b551fb05850d732740f3c0099'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
selection=json.loads((out/'selection.json').read_text(encoding='utf-8'));skin=set(selection['skin_faces'])
scale=body.matrix_world.to_scale().x;inverse=body.matrix_world.inverted();normal_matrix=body.matrix_world.to_3x3()
world=[body.matrix_world@v.co for v in body.data.vertices];names=[g.name for g in body.vertex_groups]
OFFWHITE=(.92,.90,.82);SLATE=(.12,.18,.22);TEAL=(.08,.72,.68)
# The off-white palette is a display colour; shading uses its linear equivalent so cotton does not render as paper white.
linear=lambda c:tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c);CLOTH=linear(OFFWHITE)
bone=lambda name:rig.matrix_world@rig.data.bones[name].head_local
neck=bone('neck');cx,cy=neck.x,neck.y

def fabric(name,color,roughness=.84,grain=2600,strength=.10):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Specular IOR Level'].default_value=.22
    bs.inputs['Sheen Weight'].default_value=.1;bs.inputs['Sheen Roughness'].default_value=.6
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=grain;tex.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.00015
    l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat
def add_folds(mat,strength):
    # Reuses the scan's packed normal map through copied source UVs; the image bytes are referenced, never edited.
    n=mat.node_tree.nodes;l=mat.node_tree.links;bump=next(x for x in n if x.type=='BUMP')
    uv=n.new('ShaderNodeUVMap');uv.uv_map='Scan fold UV';img=n.new('ShaderNodeTexImage');img.image=bpy.data.images['rp_eric_rigged_001_norm.jpg']
    nm=n.new('ShaderNodeNormalMap');nm.uv_map='Scan fold UV';nm.inputs['Strength'].default_value=strength
    l.new(uv.outputs['UV'],img.inputs['Vector']);l.new(img.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],bump.inputs['Normal'])
def ribbed(name,color):
    # Rib phase is a per-vertex column attribute, so knit ribs follow each band rather than world axes.
    mat=fabric(name,color,roughness=.88);n=mat.node_tree.nodes;l=mat.node_tree.links
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='Rib Phase'
    mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2*math.pi
    sine=n.new('ShaderNodeMath');sine.operation='SINE'
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.0006
    l.new(attr.outputs['Fac'],mul.inputs[0]);l.new(mul.outputs[0],sine.inputs[0]);l.new(sine.outputs[0],bump.inputs['Height'])
    l.new(bump.outputs['Normal'],n['Principled BSDF'].inputs['Normal'])
    return mat
fleece=fabric('OddsWell | off-white brushed fleece',CLOTH);jogger=fabric('OddsWell | off-white jogger fleece',CLOTH,grain=2200)
rib=ribbed('OddsWell | off-white rib knit',CLOTH)
canvas=fabric('OddsWell | slate sneaker canvas',SLATE,roughness=.9,grain=3400,strength=.18);sole=fabric('OddsWell | off-white rubber sole',CLOTH,roughness=.6,grain=900,strength=.05)
add_folds(fleece,.12);add_folds(jogger,.8);add_folds(canvas,.5)
lace=fabric('OddsWell | off-white flat lace',CLOTH,roughness=.8);tab=fabric('OddsWell | teal heel tab',TEAL,roughness=.7)

def poly_weights(poly):
    weights={}
    for original in poly.vertices:
        for g in body.data.vertices[original].groups:weights[g.group]=weights.get(g.group,0)+g.weight/len(poly.vertices)
    total=sum(weights.values());return {k:v/total for k,v in weights.items()}
clothed=[p.index for p in body.data.polygons if p.index not in skin]
clothed_bvh=BVHTree.FromPolygons(world,[list(body.data.polygons[i].vertices) for i in clothed],all_triangles=False)
hip=names.index('hip')
def skin_object(obj,positions,blend_hip=None):
    for g in names:obj.vertex_groups.new(name=g)
    for index,point in enumerate(positions):
        nearest=clothed_bvh.find_nearest(point);weights=poly_weights(body.data.polygons[clothed[nearest[2]]])
        if blend_hip:
            t=blend_hip(point);weights={k:v*(1-t) for k,v in weights.items()};weights[hip]=weights.get(hip,0)+t
        for group,value in weights.items():obj.vertex_groups[group].add([index],value,'REPLACE')
    obj.modifiers.new('Shared scanned skeleton','ARMATURE').object=rig
def new_object(name,positions,polygons,material):
    data=bpy.data.meshes.new(name);data.from_pydata([inverse@p for p in positions],[],polygons);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=body.parent;obj.matrix_world=body.matrix_world.copy()
    data.materials.append(material)
    for p in data.polygons:p.use_smooth=True
    return obj
def finish(obj,smooth=.22,thickness=.0025,relax=0):
    if relax:
        # Volume-preserving relaxation removes the scanned vest/collar steps without shrinking the garment.
        lap=obj.modifiers.new('Relaxed fleece drape','LAPLACIANSMOOTH');lap.iterations=relax;lap.lambda_factor=1.5;lap.use_volume_preserve=True;lap.use_normalized=True
    s=obj.modifiers.new('Soft garment transitions','SMOOTH');s.factor=smooth;s.iterations=3
    obj.modifiers.new('Rounded cloth surface','SUBSURF').levels=1
    t=obj.modifiers.new('Garment thickness','SOLIDIFY');t.thickness=thickness/scale;t.offset=1

garments=[];parts=[]
def relax(positions,normals,faces,lookup,minimum,iterations,slack=.0015):
    # Constrained relaxation: neighbours average out the scanned vest/collar steps, then any point
    # that drifted closer than its minimum clearance is projected back outside the clothed scan.
    neighbours=[set() for _ in positions]
    for f in faces:
        idx=[lookup[i] for i in body.data.polygons[f].vertices]
        for k,a in enumerate(idx):neighbours[a].update((idx[k-1],idx[(k+1)%len(idx)]))
    start=[p.copy() for p in positions]
    for _ in range(iterations):
        moved=[]
        for i,p in enumerate(positions):
            avg=sum((positions[j] for j in neighbours[i]),Vector())/len(neighbours[i]);q=p.lerp(avg,.5)
            hit=clothed_bvh.find_nearest(q);clearance=minimum(q)
            if hit[0] is not None and (q-hit[0]).dot(hit[1])<clearance:q=hit[0]+hit[1]*clearance
            # Smoothing may lift low areas over a scanned step but may not sink below the fitted offset.
            depth=(q-start[i]).dot(normals[i])
            if depth<-slack:q=q+normals[i]*(-slack-depth)
            moved.append(q)
        positions[:]=moved
def shell(name,faces,offset,material,zmax=None,blend_hip=None,keep_floor=False,relaxed=0):
    faces=[f for f in faces];verts=sorted({i for f in faces for i in body.data.polygons[f].vertices});lookup={v:i for i,v in enumerate(verts)}
    positions=[];normals=[]
    for i in verts:
        n=(normal_matrix@body.data.vertices[i].normal).normalized();p=world[i]+n*offset(world[i]);normals.append(n)
        if keep_floor and n.z<-.5:p.z=world[i].z
        if zmax:p.z=min(p.z,zmax)
        positions.append(p)
    if relaxed:relax(positions,normals,faces,lookup,lambda p:.8*offset(p),relaxed)
    obj=new_object(name,positions,[tuple(lookup[i] for i in body.data.polygons[f].vertices) for f in faces],material)
    source_uv=body.data.uv_layers.active.data;uv=obj.data.uv_layers.new(name='Scan fold UV').data
    for poly,f in zip(obj.data.polygons,faces):
        start=body.data.polygons[f].loop_start
        for k,loop in enumerate(poly.loop_indices):uv[loop].uv=source_uv[start+k].uv
    skin_object(obj,positions,blend_hip);garments.append(obj);return obj,positions

def ramp(value,a,b):return max(0.,min(1.,(value-a)/(b-a)))
top,top_points=shell('OddsWell wardrobe | starter off-white long-sleeve top',selection['top_faces'],lambda p:.0065+.0095*ramp(1.06-p.z,0,.08),fleece,zmax=1.56,relaxed=25,
                     blend_hip=lambda p:.6*ramp(1.02-p.z,0,.08))
bottom,bottom_points=shell('OddsWell wardrobe | starter off-white joggers',selection['bottom_faces'],lambda p:.007+.005*ramp(p.z,.55,.82)*(1-ramp(p.z,.88,.98)),jogger)
shoes,shoe_points=shell('OddsWell wardrobe | starter slate sneakers',selection['shoe_faces'],lambda p:.004+.003*(p.z<.03),canvas,keep_floor=True)
shoes.data.materials.append(sole)
attribute=shoes.data.attributes.new('Sole Height','FLOAT','POINT')
for i,p in enumerate(shoe_points):attribute.data[i].value=p.z
n=canvas.node_tree.nodes;l=canvas.node_tree.links
attr=n.new('ShaderNodeAttribute');attr.attribute_name='Sole Height'
edge=n.new('ShaderNodeMath');edge.operation='LESS_THAN';edge.inputs[1].default_value=.022
mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*SLATE,1);mix.inputs[2].default_value=(*CLOTH,1)
l.new(attr.outputs['Fac'],edge.inputs[0]);l.new(edge.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],n['Principled BSDF'].inputs['Base Color'])
rough=n.new('ShaderNodeMapRange');rough.inputs[3].default_value=.9;rough.inputs[4].default_value=.6
l.new(edge.outputs[0],rough.inputs[0]);l.new(rough.outputs[0],n['Principled BSDF'].inputs['Roughness'])
finish(top);finish(bottom)
finish(shoes,smooth=.12,thickness=.002)

def rest_mesh(obj):
    # Smoothed, subdivided rest surface: trims are fitted to the garment as rendered, not to its raw cage.
    hidden=[m for m in obj.modifiers if m.type in ('ARMATURE','SOLIDIFY')]
    for m in hidden:m.show_viewport=False
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    points=[ev.matrix_world@v.co for v in data.vertices];polys=[tuple(p.vertices) for p in data.polygons];ev.to_mesh_clear()
    for m in hidden:m.show_viewport=True
    return points,polys
top_points,_=rest_mesh(top);bottom_points,_=rest_mesh(bottom);shoe_points,shoe_polys=rest_mesh(shoes)
def fitted_ring(name,center,axis,heights,columns,points,rmax,gap,material,rib_mm=4.5,thickness=.0022,weights_hip=None):
    """Ring band whose radius follows the outermost nearby clothing per column."""
    axis=axis.normalized();u=axis.orthogonal().normalized();v=axis.cross(u)
    if abs(axis.z)>.7:u=Vector((0,-1,0));u=(u-axis*u.dot(axis)).normalized();v=axis.cross(u)  # seam column faces the back
    samples=[]
    for p in points:
        d=p-center;h=d.dot(axis);q=d-axis*h;r=q.length
        if r<rmax:samples.append((math.atan2(q.dot(v),q.dot(u))%(2*math.pi),h,r))
    rows=len(heights(0));radius=[[None]*columns for _ in range(rows)]
    for c in range(columns):
        a=c/columns*2*math.pi
        for row,h in enumerate(heights(c)):
            near=[r for s,hh,r in samples if abs(hh-h)<.009 and min(abs(s-a),2*math.pi-abs(s-a))<2.5*2*math.pi/columns]
            radius[row][c]=max(near) if near else None
    filled=[i for i,row in enumerate(radius) if any(r is not None for r in row)];assert filled,name
    for i,row in enumerate(radius):
        if i not in filled:row[:]=list(radius[min(filled,key=lambda j:abs(j-i))])  # rows past the cloth edge keep the nearest fitted width
    for row in radius:
        for c in range(columns):
            if row[c] is None:
                k=1
                while row[(c-k)%columns] is None and row[(c+k)%columns] is None:k+=1
                row[c]=max(r for r in (row[(c-k)%columns],row[(c+k)%columns]) if r is not None)
        dilated=[max(row[(c+k)%columns] for k in range(-2,3)) for c in range(columns)]
        row[:]=[sum(dilated[(c+k)%columns] for k in range(-2,3))/5 for c in range(columns)]
    gaps=gap if callable(gap) else (lambda h:gap)
    positions=[];phase=[]
    circumference=sum(2*math.pi*r/columns for r in radius[0])
    for row in range(rows):
        for c in range(columns+1):
            a=c/columns*2*math.pi;h=heights(c%columns)[row];r=radius[row][c%columns]+gaps(h)
            positions.append(center+axis*h+(u*math.cos(a)+v*math.sin(a))*r);phase.append(c*circumference/columns/(rib_mm/1000))
    polys=[(r*(columns+1)+c,r*(columns+1)+c+1,(r+1)*(columns+1)+c+1,(r+1)*(columns+1)+c) for r in range(rows-1) for c in range(columns)]
    obj=new_object(name,positions,polys,material);a=obj.data.attributes.new('Rib Phase','FLOAT','POINT')
    for i,value in enumerate(phase):a.data[i].value=value
    skin_object(obj,positions,weights_hip)
    sub=obj.modifiers.new('Rounded rib','SUBSURF');sub.levels=1
    t=obj.modifiers.new('Rib thickness','SOLIDIFY');t.thickness=thickness/scale;t.offset=1
    parts.append(obj);return obj

head_bones=('head','jaw','eye','eyelid','eyebrow','mouth')
def head_share(poly):return sum(v for k,v in poly_weights(poly).items() if names[k].startswith(head_bones))
# Hair and eyes are not skin-coloured, so garment fitting only samples clothing below the head.
clothing_points=[world[i] for p in body.data.polygons if p.index not in skin and head_share(p)<.3 for i in p.vertices]
# Mock-neck rib band: it rises just above the scanned shirt collar so the formal collar points never show.
collar_points=[p for p in clothing_points if p.z>1.44]+[p for p in top_points if p.z>1.44]  # shell is included so the band always clears it
top_of_collar={}
for c in range(96):
    a=c/96*2*math.pi;d=Vector((math.sin(a),-math.cos(a),0))  # column 0 at the back, matching the ring basis
    near=[p.z for p in clothing_points if p.z>1.44 and (Vector((p.x-cx,p.y-cy,0))).length<.1 and Vector((p.x-cx,p.y-cy,0)).normalized().dot(d)>.97]
    top_of_collar[c]=max(near)+.006 if near else None
known=[v for v in top_of_collar.values() if v];fallback=sum(known)/len(known)
raw=[max(top_of_collar[c] or fallback,1.5) for c in range(96)];H=max(sum(raw[(c+k)%96] for k in range(-8,9))/17 for c in range(96))
# A level mock neck, highest at the back and 14 mm lower at the throat.
collar_line=[H-.014*(1-math.cos(c/96*2*math.pi))/2 for c in range(96)]
heights=lambda c:[1.462+(collar_line[c]-1.462)*k/5-neck.z for k in range(6)]
fitted_ring('Starter top | mock-neck rib band',neck,Vector((0,0,1)),heights,96,collar_points,.1,.0055,rib)
# Rib cuffs close each sleeve at the wrist.
for side in ('l','r'):
    start=bone('lowerarm_twist_'+side);axis=bone('hand_'+side)-start
    end=max((p-start).dot(axis.normalized()) for p in top_points if (p-start).dot(axis.normalized())<.2 and (p-start-axis.normalized()*(p-start).dot(axis.normalized())).length<.07)
    sleeve=[p for p in top_points+clothing_points if abs((p-start).dot(axis.normalized())-end)<.06]
    fitted_ring('Starter top | rib cuff '+side,start,axis,lambda c,end=end:[end-.045+.0118*k for k in range(6)],48,sleeve,.065,lambda h,end=end:-.0015 if h<end-.014 else .0035-.002*ramp(h,end-.014,end+.014),rib)
# Rib hem band finishes the top over the hips.
hem=min(p.z for p in top_points if abs(p.x-cx)<.25 and abs(p.y-cy)<.25)
hips=[p for p in top_points+clothing_points if abs(p.x-cx)<.3 and abs(p.y-cy)<.3]
fitted_ring('Starter top | rib hem band',Vector((cx,cy,0)),Vector((0,0,1)),lambda c:[hem-.002+.009*k for k in range(5)],160,[p for p in top_points if p.z<hem+.05],.26,lambda h:-.004+.003*ramp(h,hem,hem+.032),rib,weights_hip=lambda p:.6)
# Gathered rib ankle cuffs make the bottoms read as casual joggers.
for side in ('l','r'):
    start=bone('foot_'+side);axis=bone('lowerleg_'+side)-start
    leg=[p for p in bottom_points if abs(p.x-start.x)<.12];low=min((p-start).dot(axis.normalized()) for p in leg)
    fitted_ring('Joggers | rib ankle cuff '+side,start,axis,lambda c,low=low:[low-.018+.013*k for k in range(5)],64,leg+[p for p in shoe_points if abs(p.x-start.x)<.12],.09,lambda h,low=low:-.0015 if h>low+.006 else .004,rib)
# Flat laces and a teal heel tab give the sneaker construction at street distance.
shoe_bvh=BVHTree.FromPolygons(shoe_points,shoe_polys,all_triangles=False)
for side in ('l','r'):
    ankle=bone('foot_'+side);ball=bone('ball_'+side);positions=[];polys=[]
    for k in range(5):
        t=.42+k*.075;x=ankle.x+(ball.x-ankle.x)*t;y=ankle.y+(ball.y-ankle.y)*t
        for dy in (-.0022,.0022):
            for dx in (-.017,.017):
                hit=shoe_bvh.ray_cast(Vector((x+dx,y+dy,.4)),Vector((0,0,-1)));assert hit[0] is not None
                positions.append(hit[0]+hit[1]*.0032)
        polys.append((4*k,4*k+1,4*k+3,4*k+2))
    laces=new_object('Sneaker | flat laces '+side,positions,polys,lace);skin_object(laces,positions);parts.append(laces)
    positions=[]
    for dx,z in ((-.011,.045),(.011,.045),(.011,.092),(-.011,.092)):
        hit=shoe_bvh.ray_cast(Vector((ankle.x+dx,ankle.y-.4,z)),Vector((0,1,0)));assert hit[0] is not None
        positions.append(hit[0]+hit[1]*.0028)
    heel=new_object('Sneaker | teal heel tab '+side,positions,[(0,1,2,3)],tab);skin_object(heel,positions);parts.append(heel)

for obj in garments+parts:
    assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
    assert all(abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in obj.data.vertices),obj.name
scene.frame_set(1);scene.cycles.device='CPU';scene.cycles.samples=32;scene.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0;native=out/'OddsWellStarterOutfit.blend';garment_names=[o.name for o in garments];part_names=[o.name for o in parts]
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/ScannedHumanMotionCandidate/refine.py';tree=ast.parse(helper.read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('identity','frame_camera')],type_ignores=[]),str(helper),'exec'))
assert identity()=='81e6d1f3433306db3909dd6dffd81b91546d7935c154d76d92ac034fda061b79'

# Finite deformation at every authored walk key; visible show-through is measured separately by coverage.py.
def evaluated(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
    points=[ev.matrix_world@v.co for v in data.vertices];ev.to_mesh_clear();return points
pose_checks=[]
for frame in range(1,50):
    scene.frame_set(frame);row={'frame':frame,'evaluated_vertex_counts':{}}
    for name in garment_names+part_names:
        points=evaluated(bpy.data.objects[name]);assert points and all(math.isfinite(c) for p in points for c in p),(frame,name)
        row['evaluated_vertex_counts'][name]=len(points)
    pose_checks.append(row)
report={'source_sha256':sha(source),'candidate_sha256':sha(native),'jacket_source_sha256':sha(jacket_source),'support_faces':{k:len(selection[k]) for k in ('top_faces','bottom_faces','shoe_faces')},
        'garments':{o:len(bpy.data.objects[o].data.vertices) for o in garment_names},'parts':part_names,'palette':{'offwhite':[*OFFWHITE,1],'slate':[*SLATE,1],'teal':[*TEAL,1]},
        'cold_reopen_pass':True,'source_mesh_uv_weights_bind_maps_preserved':True,'shared_rig':rig.name,'pose_checks':pose_checks,
        'source_outfit_remaining':'Original suit, shirt, vest, belt and dress shoes stay in the retained original mesh beneath the new garments; no underlying anatomy is invented or exposed.',
        'scope':'Separate skinned off-white mock-neck long-sleeve top, joggers, rib trims and slate sneakers. Offline wardrobe study, not cloth simulation, runtime export or final visual acceptance.'}
(out/'starter-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('STARTER_OUTFIT_BUILT',report['candidate_sha256'],flush=True)

cam=scene.camera
def render(name,frame,pos,target,lens,size=(760,840)):
    scene.frame_set(frame);frame_camera(pos,target);cam.data.lens=lens
    scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('STARTER_RENDER',name,flush=True)
only=[a.split('=',1)[1].split(',') for a in sys.argv if a.startswith('--only=')]
views=[('Full',13,(-2.90,.40,1.28),(-.75,-2.4,.98),42),('Front',1,(-.75,.85,1.15),(-.75,-2.4,.98),45),('Side',25,(-4,-2.4,1.15),(-.75,-2.4,.98),50),
       ('Back',1,(-.75,-5.4,1.15),(-.75,-2.4,.98),45),('Close',1,(-1.75,-.15,1.48),(-.75,-2.4,1.32),55),('Feet',1,(-1.45,-.75,.42),(-.75,-2.25,.08),50),('Neck',1,(-1.25,-1.15,1.62),(-.75,-2.1,1.5),85),('NeckBack',1,(-.35,-3.2,1.62),(-.75,-2.1,1.5),85)]
for view in views:
    if not only or view[0] in only[0]:render(*view)
if not only or 'Jacket' in only[0]:
    # The runtime replaces the starter top with the Signal Jacket; joggers and sneakers stay.
    with bpy.data.libraries.load(str(jacket_source),link=False) as (available,loaded):
        loaded.objects=[name for name in available.objects if name.startswith(('Signal Jacket | ','OddsWell wardrobe | Signal Jacket'))]
    for obj in loaded.objects:
        scene.collection.objects.link(obj);obj.parent=body.parent;obj.matrix_world=body.matrix_world.copy()
        for m in obj.modifiers:
            if m.type=='ARMATURE':m.object=rig
    for obj in bpy.data.objects:
        if obj.name.startswith(('OddsWell wardrobe | starter off-white long-sleeve','Starter top | ')):obj.hide_render=True
    render('Jacket',13,(-2.90,.40,1.28),(-.75,-2.4,.98),42)
if '--preview' in sys.argv:
    for obj in bpy.data.objects:obj.hide_render=obj.name.startswith(('Signal Jacket | ','OddsWell wardrobe | Signal Jacket'))
    frames=out/'Frames';frames.mkdir(exist_ok=True);scene.cycles.samples=8;scene.render.resolution_x=640;scene.render.resolution_y=704;cam.data.lens=42
    for index,frame in enumerate(range(1,49,2)):
        scene.frame_set(frame);frame_camera((-2.90,.40,1.28),(-.75,-2.4,.98));scene.render.filepath=str(frames/f'{index:04d}.png');bpy.ops.render.render(write_still=True);print('STARTER_PREVIEW_FRAME',frame,flush=True)
