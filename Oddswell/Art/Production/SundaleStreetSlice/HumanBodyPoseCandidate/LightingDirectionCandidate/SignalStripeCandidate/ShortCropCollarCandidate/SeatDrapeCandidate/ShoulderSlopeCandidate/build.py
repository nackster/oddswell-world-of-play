"""Ease the neck-to-sleeve shoulder slope of the retained walking jacket."""
import bpy
import hashlib
import sys
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root.parent/'AnkleFitCandidate'/'AnkleFit.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='25492A223A097BEAD790376C13D3F643BA9EB3A54729F97E51BF62DD66EBF376'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
coat=bpy.data.objects['Character | tailored slate jacket']
support=bpy.data.objects['Character | internal torso support']

def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)

def sculpt(p):
    lateral=abs(p.x+.75)
    slope=smooth((lateral-.075)/.180)*(1-smooth((lateral-.315)/.090))
    upper=smooth((p.z-1.270)/.140)
    return p+Vector((0,0,-.050*slope*upper))

for obj in (coat,support):
    world=obj.matrix_world;inv=world.inverted()
    for vertex in obj.data.vertices:vertex.co=inv@sculpt(world@vertex.co)
    if obj==coat:
        for name in ('Tailored rest','Collision fit','Gravity result'):
            for datum in obj.data.attributes[name].data:
                datum.vector=inv@sculpt(world@Vector(datum.vector))
    obj.data.update()
fit=coat.data.attributes['Collision fit'].data
gravity=coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m']=max((a.vector-b.vector).length for a,b in zip(gravity,fit))

original=Path('Oddswell/Art/Production/SundaleStreetSlice/settle_jacket.py').read_text(encoding='utf-8')
exec(compile(original[:original.rfind('\nsettle_jacket()')], 'settle_jacket.py', 'exec'))
fit_jacket_seams();fit_jacket_fastening()
for obj in scene.objects:
    if obj.name.startswith('Character | yoke topstitch '):obj.hide_render=True;obj.hide_set(True)
scene['shoulder_slope_candidate']=True
scene['shoulder_slope_maximum_ease_m']=.050

if '--render' in sys.argv:
    for label,place,target,lens,width,height,samples in (
        ('Front_Close',(-.75,.15,1.40),(-.75,-2.4,1.40),62,1000,900,24),
        ('Rear_Close',(-.75,-4.75,1.40),(-.75,-2.4,1.40),62,1000,900,24),
        ('Full_Front',(-.75,.7,1.25),(-.75,-2.4,1.0),40,1000,1100,32),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100,32)):
        data=bpy.data.cameras.new('Shoulder slope '+label)
        camera=bpy.data.objects.new('Shoulder slope '+label,data);scene.collection.objects.link(camera)
        camera.location=place;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens;scene.camera=camera;scene.cycles.samples=samples
        scene.render.resolution_x=width;scene.render.resolution_y=height;scene.render.resolution_percentage=100
        scene.render.filepath=str(root/('Shoulder_Slope_'+label+'.png'));bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
    scene.camera=bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples=32;scene.render.resolution_x=1600;scene.render.resolution_y=900
    scene.render.filepath=str(root/'Shoulder_Slope_Gameplay.png');bpy.ops.render.render(write_still=True)

scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'ShoulderSlope.blend'),compress=True)
print('ODDSWELL_SHOULDER_SLOPE_CANDIDATE_PASS',flush=True)
