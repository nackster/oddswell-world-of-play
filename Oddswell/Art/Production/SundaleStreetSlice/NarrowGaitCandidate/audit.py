"""Audit lower-limb separation and retained stitched hems after gait narrowing."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

source=Path(sys.argv[sys.argv.index('--scene')+1]) if '--scene' in sys.argv else Path(__file__).resolve().parent/'NarrowGait.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
leg=bpy.data.objects['Character | anatomical legs']
evaluated=leg.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
points=[leg.matrix_world@v.co for v in mesh.vertices]
left=[];right=[];crossing=[]
for triangle in mesh.loop_triangles:
    ids=tuple(triangle.vertices)
    xs=[points[index].x for index in ids]
    if max(xs)<-.75:left.append(ids)
    elif min(xs)>-.75:right.append(ids)
    else:crossing.append(ids)
assert left and right and not crossing,(len(left),len(right),len(crossing))
left_tree=BVHTree.FromPolygons(points,left,all_triangles=True)
right_tree=BVHTree.FromPolygons(points,right,all_triangles=True)
intersections=left_tree.overlap(right_tree)
gaps=[]
for index,point in enumerate(points):
    if not .13<point.z<.71:continue
    tree=right_tree if point.x<-.75 else left_tree
    _,_,_,distance=tree.find_nearest(point)
    if distance is not None:gaps.append(distance)
print('GAIT_LEG_SURFACE',len(left),len(right),'OVERLAPS',len(intersections),'MIN_GAP_MM',round(min(gaps)*1000,3),flush=True)
assert not intersections and min(gaps)>.002
evaluated.to_mesh_clear()

head=bpy.data.objects['Character | anatomical head']
head_points=[head.matrix_world@vertex.co for vertex in head.data.vertices if 1.55<(head.matrix_world@vertex.co).z<1.78]
stance=bpy.data.objects['Character | sneaker sole right']
stance_points=[stance.matrix_world@vertex.co for vertex in stance.data.vertices]
low=min(point.z for point in stance_points)
contact=[point for point in stance_points if point.z<low+.0003]
head_x=sum(point.x for point in head_points)/len(head_points)
stance_x=sum(point.x for point in contact)/len(contact)
offset=abs(head_x-stance_x)
print('GAIT_HEAD_TO_STANCE_FOOT_MM',round(offset*1000,3),flush=True)
assert .04<offset<.07

pants=bpy.data.objects['Character | shorts leg continuous tailoring']
facing=bpy.data.objects['Character | folded cotton leg hem facings']
for side,pants_offset,facing_offset in (('left',1438,0),('right',4318,800)):
    gaps=[]
    for row in range(5):
        for column in range(80):
            cloth=pants.matrix_world@pants.data.vertices[pants_offset+row*80+column].co
            fold=facing.matrix_world@facing.data.vertices[facing_offset+row*80+column].co
            gaps.append((cloth-fold).length)
    print('GAIT_FACING_GAP_MM',side,round(min(gaps)*1000,3),round(max(gaps)*1000,3),flush=True)
    assert .0003<min(gaps) and max(gaps)<.0014
print('NARROW_GAIT_LOWER_BODY_AUDIT_PASS',flush=True)
