"""Fit folded cotton hem facings to the existing posed shorts legs."""
import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector

output=Path(__file__).resolve().parent
source=output.parent/'HandOrientationCandidate/HandOrientation.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='19E9D9030C71FBB78F372AA2C86C505AEFF5D83F485E518B41E790ABEF04256D'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198

# Each leg's first control rings already follow its asymmetrical pose and
# settled wrinkles. The facing uses those exact rings instead of a new oval.
vertices=[]
faces=[]
outer_top=[]
for side,offset in (('left',1438),('right',4318)):
    rings=[]
    center=[]
    for k in range(5):
        row=[pants.data.vertices[offset+k*80+j].co.copy() for j in range(80)]
        rings.append(row)
        center.append(sum(row,Vector())/80)
    start=len(vertices)
    for k,row in enumerate(rings):
        for p in row:
            radial=Vector((p.x-center[k].x,p.y-center[k].y,0)).normalized()
            outward=.0010*(1-k/4)+.0004*(k/4)
            vertices.append(p+radial*outward)
    # The lower edge turns underneath, rises inside the leg and stays open
    # at the upper facing edge, as a sewn cotton fold would.
    for k in range(5):
        prior=4-k
        for p in rings[prior]:
            radial=Vector((p.x-center[prior].x,p.y-center[prior].y,0)).normalized()
            vertices.append(p-radial*.0012)
    for k in range(9):
        for j in range(80):
            a=start+k*80+j
            b=start+k*80+(j+1)%80
            c=start+(k+1)*80+(j+1)%80
            d=start+(k+1)*80+j
            faces.append((a,b,c,d))
    outer_top.append((side,start+4*80))

mesh=bpy.data.meshes.new('Pose-fitted folded cotton hem facings')
mesh.from_pydata(vertices,[],faces)
mesh.update()
facing=bpy.data.objects.new('Character | folded cotton leg hem facings',mesh)
scene.collection.objects.link(facing)
facing.matrix_world=pants.matrix_world.copy()
facing.data.materials.append(bpy.data.materials['Character | offwhite cotton twill'])
for poly in facing.data.polygons:poly.use_smooth=True
facing['construction']='Separate double-fold cotton facing fitted to five existing garment rings'

# One visible continuous upper stitch line per leg; the existing lower
# rows are retained, avoiding a heavy decorative contrast line.
thread=bpy.data.materials['Character | matching cotton topstitch']
for side,start in outer_top:
    data=bpy.data.curves.new('Hem upper topstitch '+side,'CURVE')
    data.dimensions='3D';data.bevel_depth=.00024;data.bevel_resolution=2
    data.materials.append(thread)
    spline=data.splines.new('POLY');spline.points.add(80)
    for j,point in enumerate(spline.points):
        p=vertices[start+j]
        c=sum((vertices[start+i] for i in range(80)),Vector())/80
        radial=Vector((p.x-c.x,p.y-c.y,0)).normalized()
        point.co=(*(p+radial*.00035),1)
    spline.points[80].co=spline.points[0].co
    seam=bpy.data.objects.new('Character | sewn folded hem '+side,data)
    scene.collection.objects.link(seam)
    seam.matrix_world=pants.matrix_world.copy()
scene['folded_cotton_hem_facings']=True
print('FOLDED_HEM_MESH',len(vertices),len(faces),flush=True)

if '--render' in sys.argv:
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.75,-3.55,.72),(-.75,-2.4,.68),60,900,900),
        ('Front_Close',(-.75,-1.25,.72),(-.75,-2.4,.68),60,900,900),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ):
        camera_data=bpy.data.cameras.new('Folded hem '+label)
        camera=bpy.data.objects.new('Folded hem '+label,camera_data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        camera_data.lens=lens
        scene.camera=camera
        scene.cycles.samples=20
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Folded_Hem_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'FoldedHem.blend'),compress=True)
print('FOLDED_HEM_CANDIDATE_PASS',flush=True)
