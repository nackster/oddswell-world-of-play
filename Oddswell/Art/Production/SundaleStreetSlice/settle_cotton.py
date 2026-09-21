"""Settle the tailored shorts against local body proxies, then retain geometry.

Executed after posing. The study blends gravity drape with the tailored base;
this is offline garment development, not a production cloth/animation rig.
"""
from mathutils.bvhtree import BVHTree
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
rest=[v.co.copy() for v in pants.data.vertices]
colliders=[]
legs=bpy.data.objects['Character | anatomical legs']
leg_collision=legs.modifiers.new('Anatomical cloth contact','COLLISION')
legs.collision.thickness_outer=.004
for name,center,radii in [('pelvis',(0,0,.847),(.190,.105,.100)),('thigh l',(-.12,-.05,.73),(.079,.083,.145)),('thigh r',(.12,.055,.73),(.079,.083,.145))]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=origin+Vector(center))
    body=bpy.context.object;body.name='STUDY | '+name;body.scale=radii
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    body.modifiers.new('Body collision','COLLISION');body.collision.thickness_outer=.003
    colliders.append(body)
pin=pants.vertex_groups.new(name='Waist attachment')
for v in pants.data.vertices:
    weight=max(0,min(1,(v.co.z-origin.z-.875)/.025))
    if weight>0:pin.add([v.index],weight,'REPLACE')
cloth=pants.modifiers.new('Cotton gravity drape','CLOTH')
bpy.context.view_layer.objects.active=pants
for _ in range(2):bpy.ops.object.modifier_move_up(modifier=cloth.name)
s=cloth.settings;s.quality=8;s.mass=.25;s.air_damping=4
s.tension_stiffness=40;s.compression_stiffness=40;s.shear_stiffness=18;s.bending_stiffness=1.2
s.vertex_group_mass=pin.name;s.pin_stiffness=1
c=cloth.collision_settings;c.use_collision=True;c.distance_min=.003;c.use_self_collision=True;c.self_distance_min=.003;c.collision_quality=3
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=40
for frame in range(1,41):scene.frame_set(frame);bpy.context.view_layer.update()
bpy.ops.object.modifier_apply(modifier=cloth.name)
maximum_delta=max((v.co-base).length for v,base in zip(pants.data.vertices,rest))
assert maximum_delta<.12,'Unstable cloth study'
for vertex,base in zip(pants.data.vertices,rest):vertex.co=base.lerp(vertex.co,.55)
smooth=pants.modifiers.new('Relax small simulation creases','SMOOTH');smooth.factor=.45;smooth.iterations=8
for _ in range(2):bpy.ops.object.modifier_move_up(modifier=smooth.name)
bpy.ops.object.modifier_apply(modifier=smooth.name)
skin_surface=BVHTree.FromObject(legs,bpy.context.evaluated_depsgraph_get())
for vertex in pants.data.vertices:
    hit,normal,_,distance=skin_surface.find_nearest(vertex.co)
    if hit is not None and distance<.045:
        clearance=(vertex.co-hit).dot(normal)
        if clearance<.0052:
            # Move only along the skin normal. Snapping to a nearest point
            # pulled cloth down onto the cropped thigh's open top boundary.
            vertex.co+=normal*(.0052-clearance)
legs.modifiers.remove(leg_collision)
for body in colliders:bpy.data.objects.remove(body,do_unlink=True)
bpy.context.view_layer.update()
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for obj in scene.objects:
    if obj.type=='CURVE' and any(obj.name.startswith('Character | '+n) for n in ('back pocket seam','shorts leg hem')):
        for spline in obj.data.splines:
            for point in spline.points:
                hit,normal,_,distance=surface.find_nearest(Vector(point.co[:3]))
                assert hit is not None and distance<.08,'Seam lost during cloth drape'
                point.co=(*(hit+normal*.001),1)
scene['cotton_drape_frames']=40
scene['cotton_drape_maximum_delta_m']=maximum_delta
scene.frame_set(1)
print('ODDSWELL_COTTON_DRAPE_PASS',maximum_delta,flush=True)
