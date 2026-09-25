"""Check fitted cloth pocket panels and their inset stitches after reopen."""
import bmesh
import bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'PocketPanel.blend'))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
assert scene['sewn_back_pocket_panels']
for side in ('left','right'):
    assert 'Character | back pocket seam '+side not in bpy.data.objects
    panel=bpy.data.objects['Character | sewn cotton back pocket '+side]
    assert len(panel.data.vertices)==325 and len(panel.data.polygons)==288
    bm=bmesh.new();bm.from_mesh(panel.data)
    assert all(e.is_manifold or e.is_boundary for e in bm.edges)
    assert sum(e.is_boundary for e in bm.edges)==72
    bm.free()
    offsets=[]
    for vertex in panel.data.vertices:
        hit,normal,_,_=surface.find_nearest(vertex.co)
        assert hit is not None
        offsets.append((vertex.co-hit).dot(normal))
    assert .0006<min(offsets) and max(offsets)<.0025,(side,min(offsets),max(offsets))
    assert len(bpy.data.objects['Character | inset back pocket stitch '+side].data.splines)==1
    assert len(bpy.data.objects['Character | pocket mouth topstitch '+side].data.splines)==1
    print('POCKET_PANEL_FIT',side,min(offsets),max(offsets),flush=True)
print('POCKET_PANEL_GEOMETRY_PASS',flush=True)
