"""Check every authored frame for stretched or detached raglan stitching."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'HandMotion.blend'))
scene=bpy.context.scene;coat=bpy.data.objects['Character | tailored slate jacket'];seams=[o for o in scene.objects if o.name.startswith('Walk surface | Character | raglan topstitch ')]
assert len(seams)==4
for obj in [coat,bpy.data.objects['Character | internal torso support']]:
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
records=[]
for frame in range(1,50):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=coat.evaluated_get(deps);mesh=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear();details={}
    for obj in seams:
        ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices]
        longest=max((points[e.vertices[0]]-points[e.vertices[1]]).length for e in mesh.edges)
        distances=[tree.find_nearest(p)[3] for p in points[::8]]
        assert longest<.015,('Stretched raglan stitch',frame,obj.name,longest)
        assert max(distances)<.002,('Detached raglan stitch',frame,obj.name,max(distances))
        details[obj.name]={'maximum_edge_length_m':longest,'maximum_sampled_cloth_distance_m':max(distances),'distance_samples':len(distances)};ev.to_mesh_clear()
    records.append({'frame':frame,'seams':details});print('STITCH_COLD_FRAME',frame,flush=True)
with (out/'HandMotion.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'stitch-motion-audit.json').write_text(json.dumps({'candidate_sha256':sha,'authored_frames_checked':49,'render_subdivision_levels_used':True,'frames':records,'scope':'All authored integer frames at render subdivision levels; edge-length and sampled nearest-jacket distance checks, not a complete seam/self-intersection or animated-subframe proof.'},indent=2)+'\n')
print('STITCH_MOTION_AUDIT_PASS',flush=True)
