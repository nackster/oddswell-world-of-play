"""Re-settle the posed cotton shorts with restrained retained cloth motion."""
import bpy
import hashlib
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
source=root.parent/'ShoeRimCandidate'/'ShoeRim.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='271C0FCD4AFF680541094C6B2FEFF39B5AE059AD086B3AED6F9D29F3A27C7C43'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
origin=Vector((-.75,-2.4,.06))
prior_cotton_max=scene['cotton_drape_maximum_delta_m']

# Reuse the retained collision/waist-pin setup with a softer second pass.
settle=Path('Oddswell/Art/Production/SundaleStreetSlice/settle_cotton.py').resolve()
with settle.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='6B6BA615A4ADBA5145266174BC31CF5EA23318C1857A962FA766C0C94648E68D'
script=settle.read_text(encoding='utf-8')
for before,after in (
    ('s.compression_stiffness=40','s.compression_stiffness=24'),
    ('s.bending_stiffness=1.2','s.bending_stiffness=.55'),
    ('frame_end=40','frame_end=60'),
    ('range(1,41)','range(1,61)'),
    ('base.lerp(vertex.co,.55)','base.lerp(vertex.co,.25)'),
    ('smooth.factor=.45;smooth.iterations=8','smooth.factor=.35;smooth.iterations=4'),
):
    assert script.count(before)==1,before
    script=script.replace(before,after)
exec(compile(script,str(settle),'exec'))
scene['cotton_drape_maximum_delta_m']=prior_cotton_max
scene['cotton_resettle_frames']=60
scene['cotton_resettle_raw_maximum_delta_m']=maximum_delta
scene['cotton_resettle_retained_fraction']=.25

# The older nearest-point projection can send a pocket seam into a deep
# thigh fold. Raycast from behind to land each stitch on the visible cloth.
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for seam in scene.objects:
    if not (seam.type=='CURVE' and seam.name.startswith('Character | back pocket seam')):
        continue
    for spline in seam.data.splines:
        for point in spline.points:
            prior=Vector(point.co[:3])
            hit,normal,_,_=surface.ray_cast(Vector((prior.x,-3.0,prior.z)),Vector((0,1,0)),2)
            assert hit is not None and normal.y<-.1,(seam.name,tuple(prior))
            point.co=(*(hit+normal*.0013),1)

if '--render' in sys.argv:
    for label,place,target,lens,width,height,samples in (
        ('Close_Rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52,1000,1000,24),
        ('Close_Front',(-.75,-1.25,.82),(-.75,-2.4,.8),52,1000,1000,24),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,1000,1100,24),
    ):
        data=bpy.data.cameras.new('Cotton resettle '+label)
        camera=bpy.data.objects.new('Cotton resettle '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=samples
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(root/('Cotton_Resettle_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
    scene.camera=bpy.data.objects['CAM | gameplay street']
    scene.cycles.samples=32
    scene.render.resolution_x=1600
    scene.render.resolution_y=900
    scene.render.filepath=str(root/'Cotton_Resettle_Gameplay.png')
    bpy.ops.render.render(write_still=True)

scene.camera=bpy.data.objects['CAM | gameplay street']
scene.render.filepath=str(root/'Cotton_Resettle_Gameplay.png')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'CottonResettle.blend'),compress=True)
print('ODDSWELL_COTTON_RESETTLE_CANDIDATE_PASS',flush=True)
