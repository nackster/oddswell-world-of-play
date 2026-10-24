"""Check that the moved openings retain their folded facings and stitches."""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'LegAxis.blend'))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
facing=bpy.data.objects['Character | folded cotton leg hem facings']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for side,pants_offset,facing_offset in (('left',1438,0),('right',4318,800)):
    gaps=[]
    for k in range(5):
        for j in range(80):
            cloth=pants.matrix_world@pants.data.vertices[pants_offset+k*80+j].co
            fold=facing.matrix_world@facing.data.vertices[facing_offset+k*80+j].co
            gaps.append((cloth-fold).length)
    print('FACING_GAP_MM',side,round(min(gaps)*1000,3),round(max(gaps)*1000,3),flush=True)
    assert .0003<min(gaps) and max(gaps)<.0013
    stitch=bpy.data.objects['Character | sewn folded hem '+side]
    seam=[]
    for spline in stitch.data.splines:
        for point in spline.points:
            world=stitch.matrix_world@Vector(point.co[:3])
            hit,_,_,dist=surface.find_nearest(pants.matrix_world.inverted()@world)
            seam.append(dist)
    print('HEM_STITCH_DIST_MM',side,round(max(seam)*1000,3),flush=True)
    assert max(seam)<.003
    legacy=[obj for obj in scene.objects if obj.type=='CURVE' and obj.name.startswith('Character | shorts leg hem '+side)]
    assert len(legacy)==2,(side,[obj.name for obj in legacy])
    for obj in legacy:
        values=[]
        for spline in obj.data.splines:
            for point in spline.points:
                world=obj.matrix_world@Vector(point.co[:3])
                _,_,_,dist=surface.find_nearest(pants.matrix_world.inverted()@world)
                values.append(dist)
        print('LEG_HEM_SEAM_DIST_MM',obj.name,round(max(values)*1000,3),flush=True)
        assert max(values)<.003
print('LEG_AXIS_HEM_CONTACT_PASS',flush=True)
