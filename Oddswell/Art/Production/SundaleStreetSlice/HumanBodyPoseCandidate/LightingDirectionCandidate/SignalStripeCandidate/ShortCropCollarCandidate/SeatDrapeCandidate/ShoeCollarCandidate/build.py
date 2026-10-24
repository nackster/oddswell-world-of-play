"""Cut and stitch an anatomical heel opening into the retained walking shoes."""
import bpy
import bmesh
import hashlib
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
source=root.parent/'ArmPoseCandidate'/'OddsWell_Arm_Pose_Candidate.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='E496FF44D80DA3455BD8D9F673BFD7D8E8215233867E73D20B47E59C250912EB'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
thread=bpy.data.materials['Character | fine warm shoe thread']

for side in ('left','right'):
    upper=bpy.data.objects['Character | canvas sneaker '+side]
    points=[upper.matrix_world@v.co for v in upper.data.vertices]
    ylo=min(p.y for p in points)
    zhi=max(p.z for p in points)
    xmid=(min(p.x for p in points)+max(p.x for p in points))/2

    # A curved lower cutter face leaves a sloping, shoe-shaped ankle rim.
    nx,ny=20,28
    vertices=[]
    for top in (False,True):
        for i in range(nx+1):
            x=xmid-.085+.170*i/nx
            for j in range(ny+1):
                y=ylo-.030+.190*j/ny
                dx=(x-xmid)/.060
                dy=(y-(ylo+.040))/.060
                z=.50 if top else zhi-.060+.025*dx*dx+.025*dy*dy
                vertices.append((x,y,z))
    stride=ny+1;layer=(nx+1)*stride
    faces=[]
    for i in range(nx):
        for j in range(ny):
            a=i*stride+j;b=(i+1)*stride+j
            faces.append((a,a+1,b+1,b))
            faces.append((layer+a,layer+b,layer+b+1,layer+a+1))
    perimeter=[i*stride for i in range(nx+1)]
    perimeter += [nx*stride+j for j in range(1,ny+1)]
    perimeter += [i*stride+ny for i in range(nx-1,-1,-1)]
    perimeter += [j for j in range(ny-1,0,-1)]
    for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):faces.append((a,layer+a,layer+b,b))
    mesh=bpy.data.meshes.new('Curved collar cutter '+side)
    mesh.from_pydata(vertices,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    cutter=bpy.data.objects.new('BUILD | curved collar cutter '+side,mesh)
    scene.collection.objects.link(cutter)
    mod=upper.modifiers.new('Curved ankle opening','BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=upper
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

    # Lean the high rear canvas gently toward the ankle; the sole stays put.
    inv=upper.matrix_world.inverted()
    rear=[upper.matrix_world@v.co for v in upper.data.vertices if (upper.matrix_world@v.co).y<ylo+.04]
    bottom=min(p.z for p in rear)
    for vertex in upper.data.vertices:
        p=upper.matrix_world@vertex.co
        wy=max(0,min(1,(ylo+.105-p.y)/.105))
        wz=max(0,min(1,(p.z-bottom-.030)/.050))
        p.y+=.018*wy*wy*(3-2*wy)*wz*wz*(3-2*wz)
        vertex.co=inv@p
    upper.data.update()

    # Stitch the true heel surface instead of floating a separate patch.
    for old in list(scene.objects):
        if old.name.startswith('Character | shoe lace heel seam '+side):bpy.data.objects.remove(old,do_unlink=True)
    surface=BVHTree.FromObject(upper,bpy.context.evaluated_depsgraph_get())
    points=[v.co for v in upper.data.vertices]
    local_ylo=min(p.y for p in points)
    rear=[p for p in points if p.y<local_ylo+.04]
    local_xmid=(min(p.x for p in rear)+max(p.x for p in rear))/2
    zlo=min(p.z for p in rear)+.014
    data=bpy.data.curves.new('Fitted heel stitch '+side,'CURVE')
    data.dimensions='3D';data.bevel_depth=.00018;data.bevel_resolution=2
    data.materials.append(thread)
    count=0
    for xoff in (-.005,.005):
        for i in range(16):
            endpoints=[]
            for z in (zlo+i*.0048,zlo+i*.0048+.0024):
                hit,normal,_,_=surface.ray_cast(Vector((local_xmid+xoff,local_ylo-.04,z)),Vector((0,1,0)),.15)
                if hit is None or normal.y>-.15:break
                endpoints.append(hit+normal*.0005)
            if len(endpoints)!=2:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for point,position in zip(spline.points,endpoints):point.co=(*position,1)
            count+=1
    assert count>8,(side,count)
    obj=bpy.data.objects.new('Character | shoe lace heel seam '+side,data)
    scene.collection.objects.link(obj);obj.matrix_world=upper.matrix_world.copy()
    print('HEEL_STITCHES',side,count,flush=True)

scene['curved_heel_collar_candidate']=True
scene['heel_collar_rear_lean_m']=.018

if '--render' in sys.argv:
    for label,place,target,lens,width,height,samples in (
        ('Rear_Close',(-.75,-3.50,.28),(-.75,-2.4,.12),65,1000,900,24),
        ('Profile_Close',(-1.65,-2.4,.27),(-.75,-2.4,.12),65,1000,900,24),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100,32)):
        data=bpy.data.cameras.new('Shoe collar '+label)
        camera=bpy.data.objects.new('Shoe collar '+label,data);scene.collection.objects.link(camera)
        camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens;scene.camera=camera;scene.cycles.samples=samples
        scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
        scene.render.filepath=str(root/('Shoe_Collar_'+label+'.png'));bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
    scene.camera=bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples=32;scene.render.resolution_x=1600;scene.render.resolution_y=900
    scene.render.filepath=str(root/'Shoe_Collar_Gameplay.png');bpy.ops.render.render(write_still=True)

scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'ShoeCollar.blend'),compress=True)
print('ODDSWELL_SHOE_COLLAR_CANDIDATE_PASS',flush=True)
