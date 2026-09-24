"""Continue the anatomical lower legs inside the retained low-shoe collars."""
import bpy
import bmesh
import hashlib
import sys
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'ShoeCollarCandidate'/'ShoeCollar.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='619BE913A7A7D6F4F94917BD133EBE1599E9AE320A55763B32F5B43D42FF5445'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
obj=bpy.data.objects['Character | anatomical legs']
assert obj.data.shape_keys is None
bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
uv=bm.loops.layers.uv['MakeHuman source UV']

for side in ('left','right'):
    edges=[e for e in bm.edges if e.is_boundary and all((obj.matrix_world@v.co).z<.25 and ((obj.matrix_world@v.co).x<-.75)==(side=='left') for v in e.verts)]
    assert len(edges)==20,(side,len(edges))
    adjacency={}
    for edge in edges:
        a,b=edge.verts;adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
    assert all(len(neighbors)==2 for neighbors in adjacency.values())
    ring=[edges[0].verts[0]]
    previous=None
    while len(ring)<len(adjacency):
        options=[v for v in adjacency[ring[-1]] if v!=previous]
        following=next((v for v in options if v not in ring),None)
        assert following is not None
        previous=ring[-1];ring.append(following)
    center=sum((v.co for v in ring),Vector())/len(ring)
    yradius=max(abs(v.co.y-center.y) for v in ring)
    skin_uv={v:next(loop[uv].uv.copy() for face in v.link_faces for loop in face.loops if loop.vert==v) for v in ring}
    previous_ring=ring
    for fraction in (.46,1):
        new_ring=[]
        for v in ring:
            p=v.co.copy();p.z-=.055*fraction
            p.x=center.x+(p.x-center.x)*(1+.05*fraction)
            p.y+=.012*fraction*(p.y-center.y)/yradius
            new_ring.append(bm.verts.new(p))
        for i in range(len(ring)):
            j=(i+1)%len(ring)
            face=bm.faces.new((previous_ring[i],previous_ring[j],new_ring[j],new_ring[i]))
            for loop in face.loops:
                index=ring.index(loop.vert) if loop.vert in ring else new_ring.index(loop.vert) if loop.vert in new_ring else previous_ring.index(loop.vert)
                loop[uv].uv=skin_uv[ring[index]]
        previous_ring=new_ring
    cap=bm.faces.new(tuple(reversed(previous_ring)))
    for loop in cap.loops:loop[uv].uv=skin_uv[ring[previous_ring.index(loop.vert)]]
    print('ANATOMICAL_ANKLE',side,'ring',len(ring),'extension_m',.055,flush=True)

bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
for face in bm.faces:face.smooth=True
bm.to_mesh(obj.data);bm.free();obj.data.update()

# Check the new join, including orientation; all boundary edges at the ankles close.
audit=bmesh.new();audit.from_mesh(obj.data)
for side in ('left','right'):
    edges=[e for e in audit.edges if all((obj.matrix_world@v.co).z<.25 and ((obj.matrix_world@v.co).x<-.75)==(side=='left') for v in e.verts)]
    assert edges and all(e.is_manifold and e.is_contiguous for e in edges),(side,'ankle join')
audit.free()
scene['anatomical_ankle_continuity']=True
scene['anatomical_ankle_extension_m']=.055

if '--render' in sys.argv:
    for label,place,target,lens,width,height,samples in (
        ('Rear_Close',(-.75,-3.50,.28),(-.75,-2.4,.12),65,1000,900,24),
        ('Profile_Close',(-1.65,-2.4,.27),(-.75,-2.4,.12),65,1000,900,24),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100,32)):
        data=bpy.data.cameras.new('Ankle fit '+label)
        camera=bpy.data.objects.new('Ankle fit '+label,data);scene.collection.objects.link(camera)
        camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens;scene.camera=camera;scene.cycles.samples=samples
        scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
        scene.render.filepath=str(root/('Ankle_Fit_'+label+'.png'));bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
    scene.camera=bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples=32;scene.render.resolution_x=1600;scene.render.resolution_y=900
    scene.render.filepath=str(root/'Ankle_Fit_Gameplay.png');bpy.ops.render.render(write_still=True)

scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'AnkleFit.blend'),compress=True)
print('ODDSWELL_ANKLE_FIT_CANDIDATE_PASS',flush=True)
