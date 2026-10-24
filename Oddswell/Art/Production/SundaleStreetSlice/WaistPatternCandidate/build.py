"""Fit a narrower walking waist across shorts, rib and jacket together."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

scratch=Path(__file__).resolve().parent
source=scratch.parent/'PocketPanelCandidate/PocketPanel.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='F4C098DFC315FF9AF49AC3F8ABE15E60D32AF28A062F7E01F5714A24B11A9052'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
center=Vector((-.75,-2.4,0))

def smooth(t):
    t=max(0.0,min(1.0,t));return t*t*(3-2*t)
def taper(p,kind):
    if kind=='pants':weight=smooth((p.z-.785)/.11)
    elif kind=='band':weight=1.0
    else:
        weight=1-smooth((p.z-.905)/.17)
        weight*=1-smooth((abs(p.x+.75)-.25)/.12)
    factor=1-.10*weight
    p.x=center.x+(p.x-center.x)*factor
    p.y=center.y+(p.y-center.y)*factor
    return p
def warp_mesh(obj,kind):
    world=obj.matrix_world;inverse=world.inverted()
    maximum=0.0
    for vertex in obj.data.vertices:
        old=world@vertex.co
        new=taper(old.copy(),kind)
        maximum=max(maximum,(new-old).length)
        vertex.co=inverse@new
    if kind=='coat' and obj.data.attributes.get('Tailored rest'):
        for name in ('Tailored rest','Collision fit','Gravity result'):
            for datum in obj.data.attributes[name].data:
                datum.vector=inverse@taper(world@Vector(datum.vector),kind)
    obj.data.update()
    print('WAIST_PATTERN_WARP',obj.name,maximum,flush=True)

for name,kind in (
    ('shorts leg continuous tailoring','pants'),
    ('ribbed waistband','band'),
    ('tailored slate jacket','coat'),
    ('internal torso support','support'),
):warp_mesh(bpy.data.objects['Character | '+name],kind)

for obj in scene.objects:
    if not obj.name.startswith('Character | '):continue
    if not any(token in obj.name for token in ('front zipper tape','zipper teeth','rear jacket seam','jacket panel seam','front welt pocket')):continue
    if obj.type=='MESH':warp_mesh(obj,'coat')
    elif obj.type=='CURVE':
        world=obj.matrix_world;inverse=world.inverted()
        for spline in obj.data.splines:
            for point in spline.points:
                point.co=(*(inverse@taper(world@Vector(point.co[:3]),'coat')),point.co.w)

coat=bpy.data.objects['Character | tailored slate jacket']
fit=coat.data.attributes['Collision fit'].data
gravity=coat.data.attributes['Gravity result'].data
scene['jacket_drape_maximum_delta_m']=max((a.vector-b.vector).length for a,b in zip(gravity,fit))
scene['coordinated_waist_pattern_scale']=.90

pants=bpy.data.objects['Character | shorts leg continuous tailoring']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for side in ('left','right'):
    panel=bpy.data.objects['Character | sewn cotton back pocket '+side]
    world=panel.matrix_world;inverse=world.inverted()
    for i,vertex in enumerate(panel.data.vertices):
        p=taper(world@vertex.co,'pants')
        local=pants.matrix_world.inverted()@p
        hit,normal,_,_=surface.ray_cast(Vector((local.x,-3,local.z)),Vector((0,1,0)),2)
        assert hit is not None and normal.y<-.1
        u=(i%25)/24;v=(i//25)/12
        offset=.0008+.0015*math.sin(math.pi*u)*math.sin(math.pi*v)
        vertex.co=inverse@(pants.matrix_world@(hit+normal*offset))
    panel.data.update()
    panel_surface=BVHTree.FromObject(panel,bpy.context.evaluated_depsgraph_get())
    for label in ('inset back pocket stitch','pocket mouth topstitch'):
        seam=bpy.data.objects['Character | '+label+' '+side]
        transform=panel.matrix_world.inverted()@seam.matrix_world
        back=transform.inverted()
        for spline in seam.data.splines:
            for point in spline.points:
                prior=taper(transform@Vector(point.co[:3]),'pants')
                hit,normal,_,distance=panel_surface.find_nearest(prior)
                assert hit is not None and distance<.025
                point.co=(*(back@(hit+normal*.0002)),point.co.w)

for label,place,target,lens in (
    ('rear',(-.75,-3.55,.82),(-.75,-2.4,.8),52),
    ('front',(-.75,-1.25,.82),(-.75,-2.4,.8),52),
    ('profile',(-1.65,-2.4,.82),(-.75,-2.4,.8),55),
):
    data=bpy.data.cameras.new('Waist pattern '+label)
    camera=bpy.data.objects.new('Waist pattern '+label,data)
    scene.collection.objects.link(camera)
    camera.location=place
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    scene.camera=camera
    scene.cycles.samples=20
    scene.render.resolution_x=900
    scene.render.resolution_y=900
    scene.render.resolution_percentage=100
    scene.render.filepath=str(scratch/('Waist_Pattern_'+label+'.png'))
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(scratch/'WaistPattern.blend'),compress=True)
print('WAIST_PATTERN_CANDIDATE_PASS',flush=True)
