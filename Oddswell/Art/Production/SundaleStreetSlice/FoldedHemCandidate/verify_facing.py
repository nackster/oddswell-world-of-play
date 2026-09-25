"""Focused geometry check for the added cotton hem facings."""
import bmesh
import bpy
from pathlib import Path

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'FoldedHem.blend'))
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
facing=bpy.data.objects['Character | folded cotton leg hem facings']
assert len(facing.data.vertices)==1600 and len(facing.data.polygons)==1440
bm=bmesh.new();bm.from_mesh(facing.data)
assert all(e.is_manifold or e.is_boundary for e in bm.edges)
assert sum(e.is_boundary for e in bm.edges)==320
bm.free()
gaps=[]
for base,offset in ((0,1438),(800,4318)):
    for k in range(5):
        for j in range(80):
            cuff=facing.data.vertices[base+k*80+j].co
            cloth=pants.data.vertices[offset+k*80+j].co
            gaps.append((cuff-cloth).length)
assert .00039<=min(gaps) and max(gaps)<=.00101,(min(gaps),max(gaps))
assert bpy.context.scene['folded_cotton_hem_facings']
print('FOLDED_HEM_FACING_FIT_PASS',len(gaps),min(gaps),max(gaps),flush=True)
