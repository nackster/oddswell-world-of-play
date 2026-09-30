"""Draft a sewn raglan jacket instead of the source's joined volume shell."""
import bpy
import bmesh
import ast
import bisect
import math
import json
import hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
root=next(p for p in Path(__file__).resolve().parents if (p/'Oddswell').is_dir() and (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/FourPanelCottonCandidate/FourPanelCotton.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest().upper()=='39078A975AB485FDBB543A57C06C32F127A5C7BC6EDE2C3E9880A2CF0A854B20','Changed source checkpoint'
work=root/'client/OddsWell/Saved/NextTen20260912/RaglanPatternBuild'
work.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
body=bpy.data.objects['Character | internal torso support']
control=bpy.data.objects['Body flow | stance blend']
world,inverse=coat.matrix_world,coat.matrix_world.inverted()
old=coat.data
materials=list(old.materials)
functions=ast.parse((source.parent.parent/'BodyFlowCandidate/build.py').read_text())
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
exec(compile(ast.Module(body=[n for n in functions.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow-functions','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']

def unwarp(p):
    q=p.copy()
    for _ in range(24):q+=p-warp(q)
    # The new sleeve reaches the transition band where fixed-point inversion is slow.
    for _ in range(16):
        residual=p-warp(q)
        if residual.length<1e-6:break
        columns=[]
        for a in range(3):
            delta=Vector();delta[a]=.0001
            columns.append((warp(q+delta)-warp(q-delta))/.0002)
        step=Matrix(columns).transposed().inverted_safe()@residual
        for factor in (1,.5,.25,.125):
            proposed=q+step*factor
            if (warp(proposed)-p).length<residual.length:q=proposed;break
    assert (warp(q)-p).length<1e-6,(list(p),list(q),(warp(q)-p).length)
    return q

def drive(key):
    driver=key.driver_add('value').driver
    variable=driver.variables.new();variable.name='flow';variable.type='SINGLE_PROP'
    variable.targets[0].id=control;variable.targets[0].data_path='["flow"]'
    driver.expression='1-flow'

def bezier(a,b,c,d,t):
    return a*(1-t)**3+b*(3*t*(1-t)**2)+c*(3*t*t*(1-t))+d*t**3

bm=bmesh.new();bm.from_mesh(old)
boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
loops=[]
while boundary:
    start=boundary.pop();v=start;previous=None;loop=[v.index]
    while True:
        candidates=[e.other_vert(v) for e in v.link_edges if e.is_boundary and e.other_vert(v)!=previous]
        other=next((q for q in candidates if q==start or q in boundary),None)
        if other is None or other==start:break
        boundary.remove(other);loop.append(other.index);previous,v=v,other
    loops.append([world@old.vertices[i].co for i in loop])
bm.free()
assert len(loops)==4
centers=[sum(p,Vector())/len(p) for p in loops]
neck=loops[max(range(4),key=lambda i:centers[i].z)]
waist=loops[min(range(4),key=lambda i:abs(centers[i].z-.915)+abs(centers[i].x+.724))]
neckcenter=sum(neck,Vector())/len(neck)
waistcenter=sum(waist,Vector())/len(waist)
cuffs={side:min((p for p in loops if p is not neck and p is not waist),key=lambda p:-side*sum(v.x for v in p)/len(p))
       for side in (-1,1)}

def circular(points,center,axis1,axis2,t):
    pairs=sorted((math.atan2((p-center).dot(axis2),(p-center).dot(axis1))%math.tau,p) for p in points)
    pairs=[(pairs[-1][0]-math.tau,pairs[-1][1])]+pairs+[(pairs[0][0]+math.tau,pairs[0][1])]
    t%=math.tau
    k=bisect.bisect_right([a for a,_ in pairs],t)-1
    a,p=pairs[k];b,q=pairs[k+1]
    return p.lerp(q,(t-a)/(b-a))

def body_ring(points,center,t):return circular(points,center,Vector((1,0,0)),Vector((0,1,0)),t)

cols,nrows,armrow=24,40,22
va=armrow/nrows
vertices,faces,uvfaces,tokens=[],[],[],{}
grids={};boundaries=set();pin_weights={}
armcurves={}
sections=json.loads((out/'body-sections.json').read_text())
arm_guides={side:[Vector(section[0 if side<0 else -1]['center']) for z,section in sections.items() if float(z)<=1.26 and len(section)==3] for side in (-1,1)}
for side in (-1,1):
    for half in ('front','rear'):
        front=half=='front'
        start=math.pi if side<0 else 0
        direction=(-1 if front else 1) if side<0 else (1 if front else -1)
        H=lambda u:body_ring(waist,waistcenter,start+direction*math.pi*.5*u)
        W=lambda u:body_ring(neck,neckcenter,start+direction*math.pi*.5*u)
        h0,h1,w0,w1=H(0),H(1),W(0),W(1)
        underarm=arm_guides[side][-1]+Vector((-side*.038,0,0))
        sign=1 if front else -1
        def S(v):
            if v<=va:
                t=v/va
                return bezier(h0,h0.lerp(underarm,.36),underarm+Vector((-side*.01,0,-.045)),underarm,t)
            t=(v-va)/(1-va)
            return bezier(underarm,underarm+Vector((side*.014,sign*.08,.092)),
                          w0+Vector((side*.112,sign*.074,-.055)),w0,t)
        def I(v):
            return bezier(h1,h1+Vector((.016,sign*.020,.178)),
                          w1+Vector((-.004,sign*.062,-.126)),w1,v)
        grid=[]
        for row in range(nrows+1):
            v=row/nrows;line=[]
            for col in range(cols+1):
                u=col/cols
                p=((1-v)*H(u)+v*W(u)+(1-u)*S(v)+u*I(v)
                   -((1-u)*(1-v)*h0+u*(1-v)*h1+(1-u)*v*w0+u*v*w1))
                if col==0 and row<=armrow:token=('side',side,row)
                elif col==0 and row==nrows:token=('neck-side',side)
                elif col==cols:token=('center',half,row)
                else:token=(side,half,row,col)
                if token not in tokens:tokens[token]=len(vertices);vertices.append(inverse@p)
                index=tokens[token]
                assert (world@vertices[index]-p).length<1e-5,token
                line.append(index)
                weight=max(1-smooth(row/2),1-smooth((nrows-row)/2))
                pin_weights[index]=max(pin_weights.get(index,0),weight)
            grid.append(line)
        grids[side,half]=grid
        island=(0 if side<0 else 1)+(0 if front else 2)
        for row in range(nrows):
            for col in range(cols):
                ids=(grid[row][col],grid[row][col+1],grid[row+1][col+1],grid[row+1][col])
                faces.append(ids)
                uvfaces.append([((island%2+c/cols)*.31+.01,(island//2+r/nrows)*.31+.01)
                                for r,c in ((row,col),(row,col+1),(row+1,col+1),(row+1,col))])
        armcurves[side,half]=[grid[r][0] for r in range(armrow,nrows+1)]

for side in (-1,1):
    ring=armcurves[side,'front']+list(reversed(armcurves[side,'rear'][1:-1]))
    count=len(ring)
    top=[world@vertices[i] for i in ring]
    topcenter=sum(top,Vector())/count
    cuff=cuffs[side];cuffcenter=sum(cuff,Vector())/len(cuff)
    guide=[cuffcenter]+[p for p in arm_guides[side] if cuffcenter.z+.01<p.z<topcenter.z]+[topcenter]
    def center_at(v):
        z=cuffcenter.z+(topcenter.z-cuffcenter.z)*v
        k=min(len(guide)-2,max(0,bisect.bisect_right([p.z for p in guide],z)-1))
        return guide[k].lerp(guide[k+1],(z-guide[k].z)/(guide[k+1].z-guide[k].z))
    axis=(center_at(.04)-center_at(0)).normalized()
    top_axis=(center_at(1)-center_at(.96)).normalized()
    toward=top[0]-topcenter;toward-=top_axis*toward.dot(top_axis)
    toward=top_axis.rotation_difference(axis)@toward.normalized()
    tangent=top_axis.rotation_difference(axis)@(top[1]-top[0])
    front=axis.cross(toward).normalized()
    if front.dot(tangent)<0:front=-front
    hem=[circular(cuff,cuffcenter,toward,front,math.tau*j/count) for j in range(count)]
    grid=[];sleeve_rows=32
    for row in range(sleeve_rows+1):
        v=row/sleeve_rows
        center=center_at(v)
        tangent=(center_at(min(1,v+.02))-center_at(max(0,v-.02))).normalized()
        rotation=axis.rotation_difference(tangent)
        blend=smooth((v-.65)/.35)
        line=[]
        for j in range(count):
            radial=(rotation@(hem[j]-cuffcenter)).lerp(top[j]-topcenter,blend)
            p=center+radial
            if row==sleeve_rows:index=ring[j]
            else:index=len(vertices);vertices.append(inverse@p)
            line.append(index)
            pin_weights[index]=max(pin_weights.get(index,0),1-smooth(row/2))
        grid.append(line)
    for row in range(sleeve_rows):
        for j in range(count):
            k=(j+1)%count
            faces.append((grid[row][j],grid[row][k],grid[row+1][k],grid[row+1][j]))
            uvfaces.append([(.67+.31*c/count,(0 if side<0 else .5)+.48*r/sleeve_rows)
                            for r,c in ((row,j),(row,j+1),(row+1,j+1),(row+1,j))])

mesh=bpy.data.meshes.new('Cut raglan jacket | torso quarters and sleeves')
mesh.from_pydata(vertices,[],faces);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh)
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
assert len(bm.verts)-len(bm.edges)+len(bm.faces)==-2
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
bm.to_mesh(mesh);bm.free()
for material in materials:mesh.materials.append(material)
for polygon in mesh.polygons:polygon.use_smooth=True
uv=mesh.uv_layers.new(name='Cut raglan cloth panels')
for polygon,ids,coords in zip(mesh.polygons,faces,uvfaces):
    by_id=dict(zip(ids,coords))
    for loop in polygon.loop_indices:uv.data[loop].uv=by_id[mesh.loops[loop].vertex_index]
coat.data=mesh
for group in list(coat.vertex_groups):coat.vertex_groups.remove(group)
pin=coat.vertex_groups.new(name='Collar zipper hem and cuff attachments')
for index,weight in pin_weights.items():
    if weight:pin.add([index],weight,'REPLACE')
drafted=[v.co.copy() for v in mesh.vertices]
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
body_inverse=body.matrix_world.inverted()
neighbors=[set() for _ in mesh.vertices]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
for iteration in range(9):
    deltas=[]
    for vertex in mesh.vertices:
        if pin_weights.get(vertex.index,0)>.95:deltas.append(Vector());continue
        p=body_inverse@(world@vertex.co)
        hit,normal,_,distance=tree.find_nearest(p)
        gap=(p-hit).dot(normal)
        delta=body.matrix_world.to_3x3()@(normal*max(0,.012-gap))
        deltas.append(delta)
    if iteration<6:
        for _ in range(2):
            deltas=[d*.6+sum((deltas[j] for j in neighbors[i]),Vector())*(.4/len(neighbors[i])) if pin_weights.get(i,0)<.95 else Vector() for i,d in enumerate(deltas)]
    for vertex,delta in zip(mesh.vertices,deltas):vertex.co+=inverse.to_3x3()@delta
    mesh.update()
fitted=[v.co.copy() for v in mesh.vertices]
print('RAGLAN_DRAFT_FITTED',len(vertices),len(faces),max((a-b).length for a,b in zip(drafted,fitted)),flush=True)
cache_key=hashlib.sha256(json.dumps({'source':'39078A975AB485FDBB543A57C06C32F127A5C7BC6EDE2C3E9880A2CF0A854B20',
    'drafted':[list(p) for p in drafted],'fitted':[list(p) for p in fitted],'faces':faces,'pin_weights':pin_weights,
    'frames':60,'stiffness':[34,34,18,1.2],'collision':[.004,.003,.003,4]},sort_keys=True).encode()).hexdigest()
cache_file=work/'cloth-bake.json'
cached=json.loads(cache_file.read_text()) if cache_file.exists() else None
if cached and cached['key']==cache_key:
    assert len(cached['gravity'])==len(mesh.vertices)
    for vertex,p in zip(mesh.vertices,cached['gravity']):vertex.co=p
    print('RAGLAN_VALIDATED_BAKE_REUSED',flush=True)
else:

# Activate the native anatomical collider for the bake, then return it to hidden support.
    body.hide_set(False);body.collision.thickness_outer=.004
    cloth=coat.modifiers.new('Raglan cotton gravity','CLOTH')
    bpy.context.view_layer.objects.active=coat
    while list(coat.modifiers).index(cloth)>0:bpy.ops.object.modifier_move_up(modifier=cloth.name)
    s=cloth.settings;s.quality=10;s.mass=.24;s.air_damping=5
    s.tension_stiffness=34;s.compression_stiffness=34;s.shear_stiffness=18;s.bending_stiffness=1.2
    s.vertex_group_mass=pin.name;s.pin_stiffness=1
    c=cloth.collision_settings;c.use_collision=True;c.distance_min=.003
    c.use_self_collision=True;c.self_distance_min=.003;c.collision_quality=4
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=60
    for frame in range(1,61):
        scene.frame_set(frame);bpy.context.view_layer.update()
        if frame%10==0:print('RAGLAN_FRAME',frame,flush=True)
    bpy.ops.object.modifier_apply(modifier=cloth.name)
    assert coat.data==mesh
    cache_file.write_text(json.dumps({'key':cache_key,'frames':60,'gravity':[list(v.co) for v in mesh.vertices]},allow_nan=False))
    body.hide_set(True);scene.frame_set(1)
gravity=[v.co.copy() for v in mesh.vertices]
for iteration in range(5):
    for vertex in mesh.vertices:
        if pin_weights.get(vertex.index,0)>.95:continue
        p=body_inverse@(world@vertex.co)
        hit,normal,_,distance=tree.find_nearest(p)
        gap=(p-hit).dot(normal)
        if gap<.007:vertex.co+=inverse.to_3x3()@(body.matrix_world.to_3x3()@(normal*(.007-gap)))
    mesh.update()
for name,values in (('Tailored rest',drafted),('Collision fit',fitted),('Gravity result',gravity)):
    attr=mesh.attributes.new(name=name,type='FLOAT_VECTOR',domain='POINT')
    for value,p in zip(attr.data,values):value.vector=p
coat.shape_key_add(name='Basis')
previous=coat.shape_key_add(name='Previous torso hip stance')
attr=mesh.attributes.new(name='Before torso hip flow',type='FLOAT_VECTOR',domain='POINT')
for point,vertex,value in zip(previous.data,mesh.vertices,attr.data):point.co=inverse@unwarp(world@vertex.co);value.vector=point.co
drive(previous)
bpy.context.view_layer.update()

for modifier in coat.modifiers:
    if modifier.type=='SOLIDIFY':modifier.show_viewport=False
bpy.context.view_layer.update()
surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
collar_surface=BVHTree.FromObject(bpy.data.objects['Character | standing collar'],bpy.context.evaluated_depsgraph_get())

def update_points(obj,values):
    if obj.type=='MESH':
        for point,p in zip(obj.data.vertices,values):point.co=p
    else:
        for point,p in zip((p for spline in obj.data.splines for p in spline.points),values):point.co=(*p,point.co.w)
    if not obj.data.shape_keys:obj.shape_key_add(name='Basis')
    keys=obj.data.shape_keys.key_blocks
    if 'Previous torso hip stance' not in keys:drive(obj.shape_key_add(name='Previous torso hip stance'))
    for point,p in zip(keys['Basis'].data,values):point.co=p
    for point,p in zip(keys['Previous torso hip stance'].data,values):point.co=obj.matrix_world.inverted()@unwarp(obj.matrix_world@p)
    if obj.type=='MESH':
        original=obj.data.attributes.get('Before torso hip flow')
        if original:
            for value,p in zip(original.data,keys['Previous torso hip stance'].data):value.vector=p.co
    obj.data.update_tag()

# Retained teal yoke pieces follow the sewn cloth, with their existing UVs.
for obj in list(scene.objects):
    if not obj.name.startswith('Character | ') or obj.type!='MESH' or 'yoke' not in obj.name:continue
    values=[]
    for vertex in obj.data.vertices:
        q=inverse@(obj.matrix_world@vertex.co)
        hit,normal,_,distance=surface.find_nearest(q)
        values.append(obj.matrix_world.inverted()@(world@(hit+normal*.00035)))
    update_points(obj,values)
for obj in list(scene.objects):
    if obj.type!='CURVE' or not obj.name.startswith('Character | '):continue
    if not any(s in obj.name for s in ('yoke topstitch','front zipper tape','front welt pocket')):continue
    values=[]
    for spline in obj.data.splines:
        for point in spline.points:
            q=inverse@(obj.matrix_world@Vector(point.co[:3]))
            hit,normal,_,distance=min((tree.find_nearest(q) for tree in (surface,collar_surface)),key=lambda result:result[3]) if 'front zipper tape' in obj.name else surface.find_nearest(q)
            values.append(obj.matrix_world.inverted()@(world@(hit+normal*(.00055 if 'yoke' in obj.name else .0016))))
    update_points(obj,values)

for obj in scene.objects:
    if not obj.name.startswith('Character | zipper teeth') or obj.type!='MESH':continue
    center=sum((inverse@(obj.matrix_world@v.co) for v in obj.data.vertices),Vector())/len(obj.data.vertices)
    hit,normal,_,distance=min((tree.find_nearest(center) for tree in (surface,collar_surface)),key=lambda result:result[3])
    shift=obj.matrix_world.inverted().to_3x3()@(world.to_3x3()@(hit+normal*.0026-center))
    update_points(obj,[v.co+shift for v in obj.data.vertices])

for side in (-1,1):
    for half in ('front','rear'):
        front=1 if half=='front' else -1
        obj=bpy.data.objects['Character | raglan topstitch '+str(side)+' '+str(front)]
        data=bpy.data.curves.new('Raglan stitched panel edge','CURVE');data.dimensions='3D';data.bevel_depth=.00022;data.bevel_resolution=2
        for material in obj.data.materials:data.materials.append(material)
        ids=armcurves[side,half]
        values=[]
        for j in range(len(ids)-1):
            a,b=[mesh.vertices[i].co for i in ids[j:j+2]]
            for k in range(5):
                p=a.lerp(b,k/5);hit,normal,_,distance=surface.find_nearest(p)
                values.append(hit+normal*.00055)
        p=mesh.vertices[ids[-1]].co;hit,normal,_,distance=surface.find_nearest(p);values.append(hit+normal*.00055)
        # Retain the historical shared underarm endpoint at the last point.
        values.reverse()
        spline=data.splines.new('POLY');spline.points.add(len(values)-1)
        obj.data=data
        update_points(obj,values)
for modifier in coat.modifiers:
    if modifier.type=='SOLIDIFY':modifier.show_viewport=True
scene['jacket_drape_controls']=len(mesh.vertices)
scene['jacket_drape_frames']=60
scene['jacket_drape_maximum_delta_m']=max((a-b).length for a,b in zip(gravity,fitted))
scene['raglan_panel_jacket']=True
scene['raglan_panel_jacket_source']=str(source.relative_to(root))
scene['raglan_panel_jacket_armrow']=armrow
scene['raglan_panel_jacket_pinned_controls']=sum(w>.95 for w in pin_weights.values())
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(work/'RaglanDraft.blend'),compress=True)
print('RAGLAN_PATTERN_SAVED',len(mesh.vertices),scene['jacket_drape_maximum_delta_m'],flush=True)

# Finish the static cloth before delivering the native candidate.
import runpy
runpy.run_path(str(out/'finish.py'),run_name='__main__')
