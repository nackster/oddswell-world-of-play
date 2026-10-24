"""Tailor outer short legs while preserving anatomical thigh clearance."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

pants=bpy.data.objects['Character | shorts leg continuous tailoring']
skin=bpy.data.objects['Character | anatomical legs']
origin=Vector((-.75,-2.4,.06))
bpy.context.view_layer.update()
skin_surface=BVHTree.FromObject(skin,bpy.context.evaluated_depsgraph_get())
maximum=0.0
corrected=0
for vertex in pants.data.vertices:
    initial=vertex.co.copy()
    p=vertex.co-origin
    if p.z>=.79:continue
    side=1 if p.x>=0 else -1
    outward=side*(p.x-side*.13)
    if outward<=0:continue
    height=max(0,min(1,(.79-p.z)/.13))
    height=height*height*(3-2*height)
    radial=max(0,min(1,outward/.07))
    radial=radial*radial*(3-2*radial)
    proposal=initial.copy();proposal.x-=side*.012*height*radial
    hit,normal,_,distance=skin_surface.find_nearest(proposal)
    if hit is not None and distance<.035:
        clearance=(proposal-hit).dot(normal)
        if clearance<.008:
            proposal+=normal*(.008-clearance)
            corrected+=1
    vertex.co=proposal
    maximum=max(maximum,(proposal-initial).length)
pants.data.update();bpy.context.view_layer.update()
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for obj in bpy.context.scene.objects:
    if obj.type!='CURVE' or not any(obj.name.startswith('Character | '+name) for name in ('back pocket seam','shorts leg hem')):continue
    for spline in obj.data.splines:
        for point in spline.points:
            position=Vector(point.co[:3])
            hit,normal,_,distance=surface.find_nearest(position)
            assert hit is not None and distance<.025,'Shorts seam lost its surface'
            point.co=(*(hit+normal*.001),1)
bpy.context.scene['anatomical_short_leg_refinement_m']=maximum
bpy.context.scene['short_leg_contact_corrections']=corrected
print('ODDSWELL_ANATOMICAL_SHORT_FIT_PASS',maximum,corrected,flush=True)
