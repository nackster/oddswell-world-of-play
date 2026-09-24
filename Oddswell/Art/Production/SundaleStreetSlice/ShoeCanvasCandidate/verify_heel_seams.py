"""Check that every new heel stitch stays fitted to its canvas upper."""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'ShoeCanvas.blend'))
depsgraph=bpy.context.evaluated_depsgraph_get()
maximum=0.0
for side in ('left','right'):
    upper=bpy.data.objects['Character | canvas sneaker '+side]
    seam=bpy.data.objects['Character | sewn heel counter '+side]
    surface=BVHTree.FromObject(upper,depsgraph)
    transform=upper.matrix_world.inverted()@seam.matrix_world
    assert len(seam.data.splines)>100
    for spline in seam.data.splines:
        assert len(spline.points)==2
        for point in spline.points:
            p=transform@Vector(point.co[:3])
            hit,normal,_,distance=surface.find_nearest(p)
            assert hit is not None and normal is not None
            assert (p-hit).dot(normal)>-.0001
            maximum=max(maximum,distance)
assert maximum<.0007,maximum
print('SHOE_HEEL_STITCH_FIT_PASS',round(maximum,6),flush=True)
