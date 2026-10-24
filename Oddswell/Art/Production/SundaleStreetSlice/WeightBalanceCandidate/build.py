"""Move the clothed upper body toward the planted right sole."""
import bpy
import hashlib
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
source=out.parent/'TailoringConstructionCandidate/TailoringConstruction.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='F3844EDB5509E0E894B97751E011BDD35DEAB814F2011DD15B979466DDF164E3'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene

def smooth(value):
    value=max(0,min(1,value))
    return value*value*(3-2*value)
def warp(point):
    point=Vector(point)
    point.x+=.045*smooth((point.z-.90)/.52)
    return point

excluded=('anatomical legs','shorts leg','fine calf hair','canvas sneaker',
          'sneaker sole','shoe lace','outsole groove','foxing edge',
          'folded cotton leg hem','sewn folded hem','shorts sewn side seam',
          'shorts sewn fly topstitch','sewn cotton back pocket',
          'inset back pocket stitch','pocket mouth topstitch')
changed=0
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'} or not obj.name.startswith('Character | '):continue
    if obj.name.startswith(tuple('Character | '+part for part in excluded)):continue
    world=obj.matrix_world.copy();inverse=world.inverted()
    def local_warp(local):return inverse@warp(world@local)
    if obj.type=='MESH':
        mesh=obj.data
        if mesh.shape_keys:
            for key in mesh.shape_keys.key_blocks:
                for point in key.data:point.co=local_warp(point.co)
            for vertex,key_point in zip(mesh.vertices,mesh.shape_keys.key_blocks[0].data):vertex.co=key_point.co
        else:
            for vertex in mesh.vertices:vertex.co=local_warp(vertex.co)
        for name in ('Tailored rest','Collision fit','Gravity result'):
            attribute=mesh.attributes.get(name)
            if attribute:
                for item in attribute.data:item.vector=local_warp(item.vector)
        mesh.update()
    else:
        for spline in obj.data.splines:
            if spline.type=='BEZIER':
                for point in spline.bezier_points:
                    point.co=local_warp(point.co)
                    point.handle_left=local_warp(point.handle_left)
                    point.handle_right=local_warp(point.handle_right)
            else:
                for point in spline.points:point.co=(*local_warp(Vector(point.co[:3])),point.co.w)
    changed+=1

head=bpy.data.objects['Character | anatomical head']
head_points=[head.matrix_world@v.co for v in head.data.vertices if 1.55<(head.matrix_world@v.co).z<1.78]
shoe=bpy.data.objects['Character | sneaker sole right']
shoe_points=[shoe.matrix_world@v.co for v in shoe.data.vertices]
low=min(p.z for p in shoe_points)
contact=[p for p in shoe_points if p.z<low+.0003]
head_x=sum(p.x for p in head_points)/len(head_points)
shoe_x=sum(p.x for p in contact)/len(contact)
print('POSE_BALANCE_SHIFTED_HEAD_X',head_x,'SOLE_X',shoe_x,'OFFSET',head_x-shoe_x,'OBJECTS',changed,flush=True)
assert .08<shoe_x-head_x<.11
scene['upper_body_stance_lean_m']=scene.get('upper_body_stance_lean_m',0)+.045
scene['lateral_weight_balance_pass_m']=.045
coat=bpy.data.objects['Character | tailored slate jacket']
fit=coat.data.attributes['Collision fit'].data
gravity=coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m']=max((g.vector-f.vector).length for g,f in zip(gravity,fit))
bpy.context.view_layer.update()

for name,place in (('Full_Rear',(-1.45,-5.85,1.25)),('Full_Front',(-1.45,1.05,1.25))):
    data=bpy.data.cameras.new('Pose balance '+name)
    camera=bpy.data.objects.new('Pose balance '+name,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector((-.75,-2.4,.97))-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=58
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900;scene.render.resolution_y=990
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/('Weight_Balance_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'WeightBalance.blend'),compress=True)
print('POSE_BALANCE_CANDIDATE_SAVED',flush=True)
