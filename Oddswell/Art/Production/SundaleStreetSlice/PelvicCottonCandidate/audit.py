"""Compare local cloth crossings and sewn-pocket clearance with the source."""
import bpy
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
source=out.parent/'PelvicSupportCandidate'/'PelvicSupport.blend'
candidate=Path(sys.argv[sys.argv.index('--scene')+1]) if '--scene' in sys.argv else out/'PelvicCotton.blend'

def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    pants=bpy.data.objects['Character | shorts leg continuous tailoring']
    evaluated=pants.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
    points=[pants.matrix_world@vertex.co for vertex in mesh.vertices]
    triangles=[]
    for tri in mesh.loop_triangles:
        ids=tuple(tri.vertices)
        if all(-.86<points[i].x<-.64 and .62<points[i].z<.83 for i in ids):
            triangles.append(ids)
    tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    crossing={(min(a,b),max(a,b)) for a,b in tree.overlap(tree)
              if a!=b and not set(triangles[a])&set(triangles[b])}
    evaluated.to_mesh_clear()
    surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
    inverse=pants.matrix_world.inverted()
    pockets={}
    for side in ('left','right'):
        pocket=bpy.data.objects['Character | sewn cotton back pocket '+side]
        gaps=[]
        for vertex in pocket.data.vertices:
            p=pocket.matrix_world@vertex.co
            start=Vector((p.x,-3,p.z))
            hit,_,_,_=surface.ray_cast(inverse@start,(inverse.to_3x3()@Vector((0,1,0))).normalized())
            if hit is not None:gaps.append((pants.matrix_world@hit).y-p.y)
        gaps.sort()
        pockets[side]=(gaps[0],gaps[len(gaps)//2],gaps[-1])
    return len(crossing),pockets

baseline,baseline_pockets=inspect(source)
result,result_pockets=inspect(candidate)
print('COTTON_LOCAL_NONADJACENT_OVERLAP_PAIRS',baseline,result,flush=True)
assert result<baseline,(baseline,result)
for side in ('left','right'):
    a,b=baseline_pockets[side],result_pockets[side]
    print('COTTON_POCKET_GAP_MM',side,tuple(round(v*1000,3) for v in a),
          tuple(round(v*1000,3) for v in b),flush=True)
    assert all(abs(x-y)<.0001 for x,y in zip(a,b)),(side,a,b)
print('PELVIC_COTTON_AUDIT_PASS',flush=True)
