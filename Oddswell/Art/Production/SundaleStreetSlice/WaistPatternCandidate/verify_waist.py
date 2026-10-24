"""Check the retained coupled waist contour and fitted back pockets."""
import bmesh
import bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'WaistPattern.blend'))
scene=bpy.context.scene
assert scene['coordinated_waist_pattern_scale']==.90
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
def circumference(k):
    row=[pants.matrix_world@pants.data.vertices[k*80+j].co for j in range(80)]
    return sum((row[(j+1)%80]-row[j]).length for j in range(80))
top=circumference(16);hip=circumference(0)
assert .895<top<.925 and 1.05<hip<1.085,(top,hip)
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for side in ('left','right'):
    panel=bpy.data.objects['Character | sewn cotton back pocket '+side]
    offsets=[]
    for vertex in panel.data.vertices:
        hit,normal,_,_=surface.find_nearest(vertex.co)
        assert hit is not None
        offsets.append((vertex.co-hit).dot(normal))
    assert .0006<min(offsets) and max(offsets)<.0026,(side,min(offsets),max(offsets))
    bm=bmesh.new();bm.from_mesh(panel.data)
    assert all(e.is_manifold or e.is_boundary for e in bm.edges)
    bm.free()
print('WAIST_PATTERN_GEOMETRY_PASS',round(top,4),round(hip,4),flush=True)
