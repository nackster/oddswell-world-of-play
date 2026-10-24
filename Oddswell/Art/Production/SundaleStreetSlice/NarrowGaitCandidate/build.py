"""Bring the planted and trailing lower limbs into a narrower walking track."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=Path(__file__).resolve().parents[5]/'Oddswell/Art/Production/SundaleStreetSlice/LongerShortsCandidate/LongerShorts.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='18438754398404ABE2678B5888ADE78FFFEC4706FD1F0015379322E4056814D7'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)
def warp(point):
    side=-1 if point.x<-.75 else 1
    amount=.04*(1-smooth((point.z-.58)/.22))
    return point+Vector((-side*amount,0,0))
def move_mesh(obj):
    matrix=obj.matrix_world.copy();inverse=matrix.inverted()
    def transformed(point):return inverse@warp(matrix@point)
    mesh=obj.data
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            for point in key.data:point.co=transformed(point.co)
        for vertex,point in zip(mesh.vertices,mesh.shape_keys.key_blocks[0].data):vertex.co=point.co
    else:
        for vertex in mesh.vertices:vertex.co=transformed(vertex.co)
    mesh.update()
def move_curve(obj):
    matrix=obj.matrix_world.copy();inverse=matrix.inverted()
    def transformed(point):return inverse@warp(matrix@point)
    for spline in obj.data.splines:
        if spline.type=='BEZIER':
            for point in spline.bezier_points:
                point.co=transformed(point.co)
                point.handle_left=transformed(point.handle_left)
                point.handle_right=transformed(point.handle_right)
        else:
            for point in spline.points:
                point.co=(*transformed(Vector(point.co[:3])),point.co.w)

tokens=(
    'anatomical legs','shorts leg continuous tailoring','folded cotton leg hem facings',
    'sewn folded hem','shorts leg hem','shorts sewn side seam','shorts sewn fly topstitch',
    'sewn cotton back pocket','inset back pocket stitch','pocket mouth topstitch',
    'fine calf hair','sneaker sole','canvas sneaker','shoe lace','outsole groove',
    'foxing edge','fitted padded shoe collar','sewn heel counter',
)
changed=[]
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'} or not obj.name.startswith('Character | '):continue
    if not any(obj.name.startswith('Character | '+token) for token in tokens):continue
    if obj.type=='MESH':move_mesh(obj)
    else:move_curve(obj)
    changed.append(obj.name)
assert len(changed)>70,len(changed)
scene['narrow_gait_per_side_m']=.04
print('NARROW_GAIT_OBJECTS',len(changed),flush=True)
for side,offset in (('left',1438),('right',4318)):
    pants=bpy.data.objects['Character | shorts leg continuous tailoring']
    points=[pants.matrix_world@pants.data.vertices[offset+j].co for j in range(80)]
    center=sum(points,Vector())/80
    sole=bpy.data.objects['Character | sneaker sole '+side]
    shoe_center=sum((sole.matrix_world@v.co for v in sole.data.vertices),Vector())/len(sole.data.vertices)
    print('NARROW_GAIT_CENTERS',side,'hem',tuple(round(v,5) for v in center),'sole',tuple(round(v,5) for v in shoe_center),flush=True)

for label,place,target,lens,height in (
    ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,990),
    ('Full_Front',(-1.45,1.05,1.25),(-.75,-2.4,.97),58,990),
):
    data=bpy.data.cameras.new('Narrow gait '+label)
    camera=bpy.data.objects.new('Narrow gait '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Narrow_Gait_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'NarrowGait.blend'),compress=True)
print('NARROW_GAIT_STUDY_SAVED',flush=True)
