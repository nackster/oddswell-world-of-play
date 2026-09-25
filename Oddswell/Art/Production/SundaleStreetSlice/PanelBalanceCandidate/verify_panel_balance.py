"""Cold-check front/rear arc balance and attached rear pocket panels."""
import bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'PanelBalance.blend'))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert .010<scene['front_rear_panel_balance_max_m']<.020

def arc(row,front):
    base=row*80
    ids=([base+j for j in range(41)] if front else [base+j for j in range(40,80)]+[base])
    points=[pants.matrix_world@pants.data.vertices[i].co for i in ids]
    return sum((b-a).length for a,b in zip(points,points[1:]))

lower_front,lower_rear=arc(0,True),arc(0,False)
upper=arc(16,True)+arc(16,False)
assert abs(lower_front-lower_rear)<.010,(lower_front,lower_rear)
assert .895<upper<.925,upper
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for side in ('left','right'):
    panel=bpy.data.objects['Character | sewn cotton back pocket '+side]
    offsets=[]
    for vertex in panel.data.vertices:
        hit,normal,_,_=surface.find_nearest(vertex.co)
        assert hit is not None
        offsets.append((vertex.co-hit).dot(normal))
    assert .0006<min(offsets) and max(offsets)<.0026,(side,min(offsets),max(offsets))
print('PANEL_BALANCE_GEOMETRY_PASS',round(lower_front,4),round(lower_rear,4),round(upper,4),flush=True)
