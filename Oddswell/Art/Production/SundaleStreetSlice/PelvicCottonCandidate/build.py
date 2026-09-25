"""Resettle the posed shorts, refit sewn details, and soften the crotch opening."""
import bpy
import hashlib
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
source=out.parent/'PelvicSupportCandidate'/'PelvicSupport.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='12D2A7382DBDAE6CDDE20D79735E07BBB4F3A7143C2E61CD44605BE1DEAB2432'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
pelvis=bpy.data.objects['Character | posed pelvic fitting support']
legs=bpy.data.objects['Character | anatomical legs']
assert len(pants.data.vertices)==7198
rest=[vertex.co.copy() for vertex in pants.data.vertices]

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def surface():
    return BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get()),pants.matrix_world.inverted()

def rear_y(position,tree,inverse):
    start=Vector((position.x,-3,position.z))
    hit,_,_,_=tree.ray_cast(inverse@start,(inverse.to_3x3()@Vector((0,1,0))).normalized())
    assert hit is not None,position
    return (pants.matrix_world@hit).y

def positions(obj):
    if obj.type=='MESH':
        return [obj.matrix_world@vertex.co for vertex in obj.data.vertices]
    return [obj.matrix_world@Vector(point.co[:3]) for spline in obj.data.splines for point in spline.points]

names=[f'Character | {kind} {side}' for side in ('left','right') for kind in (
    'sewn cotton back pocket','inset back pocket stitch','pocket mouth topstitch')]
original_tree,original_inverse=surface()
original_rear_y={name:[rear_y(p,original_tree,original_inverse) for p in positions(bpy.data.objects[name])]
                 for name in names}
del original_tree

pin=pants.vertex_groups.new(name='Pelvic cotton fixed boundaries')
for vertex in pants.data.vertices:
    z=(pants.matrix_world@vertex.co).z
    weight=max(smooth((z-.855)/.045),1-smooth((z-.625)/.045))
    if weight>0:pin.add([vertex.index],weight,'REPLACE')
collision=[]
for obj in (pelvis,legs):
    modifier=obj.modifiers.new('Pelvic cotton contact','COLLISION')
    obj.collision.thickness_outer=.003
    collision.append((obj,modifier))
cloth=pants.modifiers.new('Pelvic cotton settle','CLOTH')
bpy.context.view_layer.objects.active=pants
for _ in range(2):bpy.ops.object.modifier_move_up(modifier=cloth.name)
s=cloth.settings
s.quality=10;s.mass=.22;s.air_damping=5
s.tension_stiffness=36;s.compression_stiffness=36;s.shear_stiffness=16;s.bending_stiffness=1.1
s.vertex_group_mass=pin.name;s.pin_stiffness=1
c=cloth.collision_settings
c.use_collision=True;c.distance_min=.003;c.use_self_collision=True;c.self_distance_min=.003;c.collision_quality=4
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=45
for frame in range(1,46):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if frame%10==0:print('COTTON_FRAME',frame,flush=True)
bpy.ops.object.modifier_apply(modifier=cloth.name)
raw_delta=[(vertex.co-before).length for vertex,before in zip(pants.data.vertices,rest)]
assert max(raw_delta)<.15
for obj,modifier in collision:obj.modifiers.remove(modifier)
scene.frame_set(1)

# Retain 35% of the simulated movement in the seat, tapering it out at the waist.
for vertex,base in zip(pants.data.vertices,rest):
    z=(pants.matrix_world@base).z
    factor=.35*(1-smooth((z-.82)/.07))
    vertex.co=base.lerp(vertex.co,factor)
pants.data.update()
group=pants.vertex_groups.new(name='Gentle cotton crease relaxation')
for vertex in pants.data.vertices:
    z=(pants.matrix_world@vertex.co).z
    weight=smooth((z-.62)/.08)*(1-smooth((z-.83)/.07))
    if weight>0:group.add([vertex.index],weight,'REPLACE')
modifier=pants.modifiers.new('Relax pelvic cotton folds','SMOOTH')
modifier.factor=.4;modifier.iterations=8;modifier.vertex_group=group.name
bpy.context.view_layer.objects.active=pants
for _ in range(2):bpy.ops.object.modifier_move_up(modifier=modifier.name)
bpy.ops.object.modifier_apply(modifier=modifier.name)

# Follow the evaluated rear cloth without changing the original pocket clearance.
tree,inverse=surface()
for name in names:
    obj=bpy.data.objects[name]
    current=positions(obj)
    changes=[rear_y(p,tree,inverse)-old for p,old in zip(current,original_rear_y[name])]
    transform=obj.matrix_world.inverted()
    if obj.type=='MESH':
        for vertex,p,delta in zip(obj.data.vertices,current,changes):
            vertex.co=transform@(p+Vector((0,delta,0)))
        obj.data.update()
    else:
        points=[point for spline in obj.data.splines for point in spline.points]
        for point,p,delta in zip(points,current,changes):
            point.co=(*(transform@(p+Vector((0,delta,0)))),point.co.w)
    print('POCKET_REFIT_MAX_MM',name,round(max(abs(x) for x in changes)*1000,3),flush=True)
del tree

# Bring the paired inseam bridge inward by 4 mm at its center and fade into the legs.
world,inverse=pants.matrix_world,pants.matrix_world.inverted()
changes={}
for j in range(21,60):
    extra=-.004*math.sin(math.pi*(j-20)/40)**1.2
    for index,sign in ((1360+2*(j-21),-1),(1361+2*(j-21),1)):
        change=Vector((sign*extra,0,0))
        vertex=pants.data.vertices[index]
        vertex.co=inverse@(world@vertex.co+change)
        changes[index]=change
left={j:1360+2*(j-21) for j in range(21,60)}
right={j:1361+2*(j-21) for j in range(21,60)}
for side,offset,bridge in ((-1,1438,left),(1,4318,right)):
    for k in range(36):
        weight=(k/36)**6
        for j in range(80):
            outer=(20<=j<=60) if side<0 else (j<=20 or j>=60)
            if outer:continue
            station=(40-j)%80 if side<0 else j
            vertex=pants.data.vertices[offset+k*80+j]
            vertex.co=inverse@(world@vertex.co+changes[bridge[station]]*weight)
pants.data.update()

scene['pelvic_cotton_resettle_frames']=45
scene['pelvic_cotton_resettle_max_raw_shift_m']=max(raw_delta)
scene['pelvic_cotton_resettle_retained_fraction']=.35
scene['pelvic_cotton_pockets_refitted']=True
scene['cotton_bridge_study_widening_m']=-.004
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'PelvicCotton.blend'),compress=True)
print('PELVIC_COTTON_CANDIDATE_SAVED',flush=True)
