"""Cold-check native shorts stitching against the saved cloth surface."""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'TailoringConstruction.blend'))
scene=bpy.context.scene
assert scene.get('sewn_shorts_side_and_fly_stitches')
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
inverse=pants.matrix_world.inverted()
expected={'Character | shorts sewn side seam left':74,
          'Character | shorts sewn side seam right':83,
          'Character | shorts sewn fly topstitch':33}
for name,count in expected.items():
    obj=bpy.data.objects[name]
    assert obj.type=='CURVE' and len(obj.data.splines)==count
    distances=[]
    for spline in obj.data.splines:
        assert len(spline.points)==2
        for point in spline.points:
            position=inverse@(obj.matrix_world@Vector(point.co[:3]))
            hit,_,_,distance=surface.find_nearest(position)
            assert hit is not None
            distances.append(distance)
    assert max(distances)<.0012,(name,max(distances))
    print('STITCH_FIT_PASS',name,count,'max_mm',round(max(distances)*1000,3),flush=True)
