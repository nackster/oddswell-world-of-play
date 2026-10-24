"""Compare saved gusset width and fixed waist/hem controls with its source."""
import bpy
import bmesh
from pathlib import Path

root=Path(__file__).resolve().parent
source=root.parent/'PanelBalanceCandidate'/'PanelBalance.blend'
candidate=root/'GussetWidth.blend'

def sample():
    obj=bpy.data.objects['Character | shorts leg continuous tailoring']
    mesh=obj.data
    fixed=[obj.matrix_world@mesh.vertices[i].co for i in list(range(16*80,17*80))+list(range(1438,1518))+list(range(4318,4398))]
    widths=[((obj.matrix_world@mesh.vertices[1361+2*j].co)-(obj.matrix_world@mesh.vertices[1360+2*j].co)).length for j in range(39)]
    return len(mesh.vertices),len(mesh.polygons),fixed,widths

bpy.ops.wm.open_mainfile(filepath=str(source))
base=sample()
bpy.ops.wm.open_mainfile(filepath=str(candidate))
current=sample()
assert current[:2]==base[:2]==(7198,7080)
assert max((a-b).length for a,b in zip(current[2],base[2]))<.000001
assert .045<max(current[3])<.055 and max(base[3])<.025
assert all(new>=old for old,new in zip(base[3],current[3]))
assert abs(bpy.context.scene['shorts_gusset_actual_width_max_m']-max(current[3]))<.000001
bm=bmesh.new()
bm.from_mesh(bpy.data.objects['Character | shorts leg continuous tailoring'].data)
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges)
assert sum(edge.is_boundary for edge in bm.edges)==240
bm.free()
print('GUSSET_WIDTH_GEOMETRY_PASS',round(max(base[3]),4),round(max(current[3]),4),flush=True)
