"""Native jacket drape with fixed attachments and source-derived body support.

The retained result is a static garment study, not gameplay cloth. Original
tailoring and raw simulated positions remain editable point attributes.
"""
import bpy
import bmesh
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

def jacket_anatomy(root,coat):
    vertices=[];faces=[];joints={};group=''
    for line in (Path(root)/'source-assets/makehuman-base.obj').read_text(encoding='utf-8').splitlines():
        a=line.split()
        if not a:continue
        if a[0]=='v':vertices.append(Vector(tuple(map(float,a[1:4]))))
        elif a[0]=='g':group=a[1]
        elif a[0]=='f':
            ids=[int(x.split('/')[0])-1 for x in a[1:]]
            if group=='body':faces.append(ids)
            if group.startswith('joint-'):joints.setdefault(group,set()).update(ids)
    for line in (Path(root)/'source-assets/facial-targets/caucasian-male-young.target').read_text(encoding='utf-8').splitlines():
        a=line.split()
        if a and not a[0].startswith('#'):vertices[int(a[0])]+=Vector(tuple(map(float,a[1:4])))
    used={i for f in faces for i in f};low=min(vertices[i].y for i in used);scale=1.8/(max(vertices[i].y for i in used)-low)
    vertices=[Vector((p.x*scale,p.z*scale,(p.y-low)*scale)) for p in vertices]
    def joint(n):return sum((vertices[i] for i in joints[n]),Vector())/len(joints[n])
    def smooth(t):
        t=max(0,min(1,t));return t*t*(3-2*t)
    bones={}
    for side,label in ((1,'l'),(-1,'r')):
        a,b,c=[joint('joint-'+label+'-'+n) for n in ('shoulder','elbow','hand')]
        A=Vector((side*.18,.006,1.414));B=Vector((side*.311,-.052,1.15));C=Vector((side*.35,-.015,.90))
        bones[side]=(a,b,c,A,B,C,(b-a).rotation_difference(B-A),(c-b).rotation_difference(C-B))
    posed=[]
    for p in vertices:
        side=1 if p.x>0 else -1;a,b,c,A,B,C,upper,lower=bones[side]
        arm=smooth((abs(p.x)-(.155+max(0,1.34-p.z)*.45))/.085)
        elbow=smooth(((p-b).dot((c-a).normalized())+.035)/.070)
        q=(A+upper@(p-a)).lerp(B+lower@(p-b),elbow)
        q.x-=side*.047*smooth((1.18-q.z)/.25)
        pivot=Vector((side*.23,0,1.405));bend=max(0,min(1,(1.20-q.z)/.13))
        q=B+Matrix.Rotation(.12*bend,3,'X')@(q-B)
        q=pivot+Matrix.Rotation(-side*.16,3,'X')@(q-pivot)
        p=p.lerp(q,arm)
        p.z-=.04*(1-arm)*smooth((p.z-1.15)/.30)
        chest=smooth((p.z-.98)/.22);armwidth=max(0,min(1,(abs(p.x)-.21)/.07))
        p.x*=1-.085*max(chest,armwidth)
        posed.append(p+Vector((-.75,-2.4,.06)))
    selected=[]
    for f in faces:
        if not all(.85<vertices[i].z<1.54 for i in f):continue
        if any((vertices[i]-bones[1 if vertices[i].x>0 else -1][2]).dot((bones[1 if vertices[i].x>0 else -1][2]-bones[1 if vertices[i].x>0 else -1][1]).normalized())>-.015 and abs(vertices[i].x)>.40 for i in f):continue
        selected.append(f)
    ids=sorted({i for f in selected for i in f});mapping={v:i for i,v in enumerate(ids)}
    mesh=bpy.data.meshes.new('Posed source torso and arms');mesh.from_pydata([posed[i] for i in ids],[],[[mapping[i] for i in f] for f in selected]);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new('Character | internal torso support',mesh);bpy.context.scene.collection.objects.link(obj);obj.matrix_world=coat.matrix_world.copy()
    bpy.context.view_layer.objects.active=obj
    remesh=obj.modifiers.new('Continuous anatomical support','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.008
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smoothmod=obj.modifiers.new('Relax posed joint transitions','SMOOTH');smoothmod.factor=.5;smoothmod.iterations=4;bpy.ops.object.modifier_apply(modifier=smoothmod.name)
    sub=obj.modifiers.new('Smooth anatomical contact','SUBSURF');sub.levels=2
    obj.hide_render=True;obj.display_type='WIRE';obj['source']='source-assets/makehuman-base.obj';obj['body_target']='caucasian-male-young.target';obj['purpose']='Internal cloth collision only; not a gameplay body'
    obj.modifiers.new('Anatomical cloth contact','COLLISION');obj.collision.thickness_outer=.002
    return obj

def fit_jacket_fastening():
    scene=bpy.context.scene;bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    surfaces=[BVHTree.FromObject(bpy.data.objects['Character | '+name],depsgraph) for name in ('tailored slate jacket','standing collar')]
    def front(position,offset):
        hits=[surface.ray_cast(Vector((position.x,-2.0,position.z)),Vector((0,-1,0)),.8)[0] for surface in surfaces]
        hits=[hit for hit in hits if hit is not None]
        assert hits,'Fastening lost garment contact'
        return max(hit.y for hit in hits)+offset
    for obj in scene.objects:
        if obj.name.startswith('Character | front zipper tape'):
            for spline in obj.data.splines:
                for point in spline.points:
                    p=Vector(point.co[:3]);p.y=front(p,.0016);point.co=(*p,1)
        if obj.name.startswith('Character | zipper teeth'):
            center=sum((v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
            shift=front(center,.0026)-center.y
            for vertex in obj.data.vertices:vertex.co.y+=shift
    scene['fitted_jacket_fastening']=True

def fit_jacket_seams():
    import math
    scene=bpy.context.scene;coat=bpy.data.objects['Character | tailored slate jacket']
    origin=Vector((-.75,-2.4,.06));bpy.context.view_layer.update()
    surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
    for obj in list(scene.objects):
        if obj.name.startswith('Character | ') and any(label in obj.name for label in ('yoke topstitch','raglan topstitch','sleeve seam','jacket panel seam')):
            bpy.data.objects.remove(obj,do_unlink=True)
    panels=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Character | ') and 'yoke' in o.name]
    for panel in panels:
        bpy.context.view_layer.objects.active=panel
        if not panel.get('conformed_panel'):
            sub=panel.modifiers.new('Resolve sewn panel curvature','SUBSURF');sub.levels=1
            bpy.ops.object.modifier_apply(modifier=sub.name)
            panel['conformed_panel']=True
        wrap=panel.modifiers.new('Sewn against jacket cloth','SHRINKWRAP');wrap.target=coat;wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.offset=.00035
        bpy.ops.object.modifier_apply(modifier=wrap.name)
        # Nearest-surface wrap can retain the underside sign after a new drape.
        for vertex in panel.data.vertices:
            hit,normal,_,distance=surface.find_nearest(vertex.co)
            vertex.co=hit+normal*.00035
        data=bpy.data.curves.new('Character | yoke boundary stitches','CURVE')
        data.dimensions='3D';data.bevel_depth=.00018;data.bevel_resolution=2
        bm=bmesh.new();bm.from_mesh(panel.data)
        for edge in bm.edges:
            if not edge.is_boundary:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for point,vertex in zip(spline.points,edge.verts):
                hit,normal,_,distance=surface.find_nearest(vertex.co)
                point.co=(*(vertex.co+normal*.00016),1)
        bm.free()
        obj=bpy.data.objects.new('Character | yoke topstitch '+panel.name,data)
        scene.collection.objects.link(obj);obj.matrix_world=coat.matrix_world.copy()
        data.materials.append(bpy.data.materials['Character | matching charcoal topstitch'])
    # Follow connected cloth edges around the armhole. Nearest-point
    # projection alone can jump between the torso and sleeve across the gap.
    import heapq,bisect
    from mathutils.kdtree import KDTree
    evaluated=coat.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();positions=[v.co.copy() for v in mesh.vertices]
    tree=KDTree(len(positions));adjacency=[[] for _ in positions]
    for i,p in enumerate(positions):tree.insert(p,i)
    tree.balance()
    for edge in mesh.edges:
        a,b=edge.vertices;length=(positions[a]-positions[b]).length
        adjacency[a].append((b,length));adjacency[b].append((a,length))
    for face in mesh.polygons:
        if len(face.vertices)!=4:continue
        for i,j in ((0,2),(1,3)):
            a,b=face.vertices[i],face.vertices[j];length=(positions[a]-positions[b]).length
            adjacency[a].append((b,length));adjacency[b].append((a,length))
    def path_between(start,end):
        start=tree.find(start)[1];end=tree.find(end)[1]
        costs={start:0};previous={};queue=[(0,start)]
        while queue:
            distance,vertex=heapq.heappop(queue)
            if distance!=costs[vertex]:continue
            if vertex==end:break
            for other,length in adjacency[vertex]:
                value=distance+length
                if value<costs.get(other,float('inf')):
                    costs[other]=value;previous[other]=vertex;heapq.heappush(queue,(value,other))
        assert end in costs,'Disconnected raglan path'
        indices=[end]
        while indices[-1]!=start:indices.append(previous[indices[-1]])
        return [positions[i] for i in reversed(indices)]
    for side in (-1,1):
        end=origin+Vector((side*.238,side*.031-.018,1.205))
        for front in (-1,1):
            start=origin+Vector((side*.058,front*.072,1.480))
            middle=origin+Vector((side*.170,front*.11,1.345))
            path=path_between(start,middle)+path_between(middle,end)[1:]
            lengths=[0]
            for a,b in zip(path,path[1:]):lengths.append(lengths[-1]+(a-b).length)
            count=max(2,math.ceil(lengths[-1]/.002));points=[]
            for j in range(count+1):
                distance=lengths[-1]*j/count;k=min(len(path)-2,max(0,bisect.bisect_right(lengths,distance)-1))
                points.append(path[k].lerp(path[k+1],(distance-lengths[k])/(lengths[k+1]-lengths[k])))
            for _ in range(20):points=[points[0]]+[points[j].lerp((points[j-1]+points[j+1])*.5,.5) for j in range(1,len(points)-1)]+[points[-1]]
            data=bpy.data.curves.new('Character | raglan topstitch','CURVE')
            data.dimensions='3D';data.bevel_depth=.00022;data.bevel_resolution=2
            spline=data.splines.new('POLY');spline.points.add(len(points)-1)
            for point,position in zip(spline.points,points):
                hit,normal,_,distance=surface.find_nearest(position)
                point.co=(*(hit+normal*.00055),1)
            obj=bpy.data.objects.new('Character | raglan topstitch '+str(side)+' '+str(front),data)
            scene.collection.objects.link(obj);obj.matrix_world=coat.matrix_world.copy()
            data.materials.append(bpy.data.materials['Character | matching charcoal topstitch'])
    evaluated.to_mesh_clear()
    scene['conformed_jacket_panels']=True

def settle_jacket():
    scene=bpy.context.scene
    coat=bpy.data.objects['Character | tailored slate jacket']
    bpy.context.view_layer.objects.active=coat
    remesh=coat.modifiers.new('Drape control surface','REMESH')
    remesh.mode='VOXEL';remesh.voxel_size=.010;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=coat.modifiers.new('Relax control grid','SMOOTH');smooth.factor=.6;smooth.iterations=3
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    rest=[v.co.copy() for v in coat.data.vertices]
    body=jacket_anatomy(Path(__file__).resolve().parent,coat)
    bpy.context.view_layer.update()
    support=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    pin=coat.vertex_groups.new(name='Collar zipper hem and cuff attachments')
    origin=Vector((-.75,-2.4,.06))
    for v in coat.data.vertices:
        p=v.co-origin
        neck=max(0,min(1,(p.z-1.442)/.020))
        hem=max(0,min(1,(1.02-p.z)/.03)) if abs(p.x)<.23 else 0
        cuff=max(0,min(1,(.973-p.z)/.025)) if abs(p.x)>.235 else 0
        zipper=max(0,1-abs(p.x)/.013) if p.y>.06 else 0
        weight=max(neck,hem,cuff,zipper)
        if weight:pin.add([v.index],weight,'REPLACE')
    weights=[next((g.weight for g in v.groups if g.group==pin.index),0) for v in coat.data.vertices]
    # Fixed caps at the collar/hem/cuffs stay in place; fit only free cloth.
    for v,w in zip(coat.data.vertices,weights):
        hit,normal,_,distance=support.find_nearest(v.co)
        if w<.80 and (v.co-hit).dot(normal)<.006:v.co=hit+normal*.006
    fitted=[v.co.copy() for v in coat.data.vertices]
    bpy.context.view_layer.objects.active=coat
    cloth=coat.modifiers.new('Jacket gravity and fabric ease','CLOTH')
    s=cloth.settings;s.quality=8;s.mass=.22;s.air_damping=5
    s.tension_stiffness=32;s.compression_stiffness=25;s.shear_stiffness=12;s.bending_stiffness=2.5
    s.vertex_group_mass=pin.name;s.pin_stiffness=1;s.shrink_min=0
    c=cloth.collision_settings;c.use_collision=True;c.distance_min=.003
    c.use_self_collision=True;c.self_distance_min=.003;c.collision_quality=4
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=45
    for frame in range(1,46):scene.frame_set(frame);bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier=cloth.name)
    simulated=[v.co.copy() for v in coat.data.vertices]
    maximum_delta=max((v-r).length for v,r in zip(simulated,fitted))
    assert 0<maximum_delta<.13,'Unstable jacket study'
    for label,values in (('Tailored rest',rest),('Collision fit',fitted),('Gravity result',simulated)):
        attribute=coat.data.attributes.new(label,'FLOAT_VECTOR','POINT')
        for datum,position in zip(attribute.data,values):datum.vector=position
    # Filter displacement, preserving the original shaped folds and volume.
    # Smoothing the entire mesh would shrink the cuffs and shoulder silhouette.
    delta=[v-r for v,r in zip(simulated,fitted)]
    neighbors=[[] for _ in rest]
    for edge in coat.data.edges:
        a,b=edge.vertices;neighbors[a].append(b);neighbors[b].append(a)
    for _ in range(7):
        delta=[d.lerp(sum((delta[j] for j in ns),Vector())/len(ns),.55) if ns else d for d,ns in zip(delta,neighbors)]
    # Filtering must not move pinned trim through neighboring free-cloth motion.
    for v,r,d,w in zip(coat.data.vertices,fitted,delta,weights):
        v.co=r+d*.95*(1-w)
        hit,normal,_,distance=support.find_nearest(v.co)
        if w<.80 and (v.co-hit).dot(normal)<.006:v.co=hit+normal*.006
    body.hide_set(True)
    coat.modifiers.new('Smooth garment surface','SUBSURF').levels=1
    bpy.context.view_layer.update()
    surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
    for obj in scene.objects:
        if not obj.name.startswith('Character | ') or not any(x in obj.name for x in ('yoke','jacket panel seam','sleeve seam','front welt pocket')):continue
        points=list(obj.data.vertices) if obj.type=='MESH' else [p for s in obj.data.splines for p in s.points] if obj.type=='CURVE' else []
        for p in points:
            hit,normal,_,distance=surface.find_nearest(Vector(p.co[:3]))
            assert hit is not None and distance<.08,'Jacket detail lost during drape'
            offset=.0006 if 'front welt pocket' in obj.name else .0015
            p.co=hit+normal*offset if obj.type=='MESH' else (*(hit+normal*offset),1)
    fit_jacket_seams()
    scene['jacket_drape_frames']=45
    scene['jacket_drape_controls']=len(rest)
    scene['jacket_drape_maximum_delta_m']=maximum_delta
    scene['jacket_fabric_ease']=0
    scene['anatomical_jacket_support']=True
    scene.frame_set(1)
    fit_jacket_fastening()
    print('ODDSWELL_JACKET_DRAPE_PASS',len(rest),maximum_delta,flush=True)

settle_jacket()
