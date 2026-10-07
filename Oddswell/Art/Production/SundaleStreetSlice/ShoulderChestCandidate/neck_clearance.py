"""Fit the subdivided neckline to skin after the broader shoulder edit."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'ShoulderChest.blend'));coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];body=bpy.data.objects['Character | internal torso support'];bpy.context.scene.frame_set(1)
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for obj in (coat,cage):
    group=obj.vertex_groups.new(name='Subdivision neckline skin clearance')
    for v in obj.data.vertices:
        p=obj.matrix_world@v.co;w=smooth((p.z-1.37)/.04)*(1-smooth((abs(p.x+.70)-.13)/.045))
        if w:group.add([v.index],w,'REPLACE')
    m=obj.modifiers.new('Subdivided neckline outside actual skin','SHRINKWRAP');m.target=body;m.wrap_method='NEAREST_SURFACEPOINT';m.wrap_mode='OUTSIDE';m.offset=.0035;m.vertex_group=group.name;obj.modifiers.move(len(obj.modifiers)-1,next(i for i,m in enumerate(obj.modifiers) if m.type=='SUBSURF')+1)
for obj in (coat,body):
    for m in obj.modifiers:
        if m.type=='SUBSURF':m.levels=m.render_levels
bpy.context.scene.frame_set(13);deps=bpy.context.evaluated_depsgraph_get();a=BVHTree.FromObject(coat,deps);b=BVHTree.FromObject(body,deps);ev=coat.evaluated_get(deps);mesh=ev.to_mesh();faces=[set(p.vertices) for p in mesh.polygons];self_count=sum(i<j and not faces[i].intersection(faces[j]) for i,j in a.overlap(a));body_count=len(a.overlap(b));ev.to_mesh_clear();print('NECKLINE_CHECK',body_count,self_count,flush=True)
report=json.loads((out/'build-report.json').read_text());report['post_subdivision_neckline_clearance']={'modifier':m.name,'offset_m':.0035,'method':'Outside-body constraint after subdivision, before the shell, shared by garment and detail cage. Graded rest neck/upper-clavicle region corrects contacts introduced when interpolation pulls the fixed collar edge toward lowered shoulder controls. Original boundary controls and nominal fabric thickness retained.','frame13_body_pairs':body_count,'frame13_nonadjacent_shell_pairs':self_count};(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
next(m for m in coat.modifiers if m.type=='SUBSURF').levels=1;bpy.context.scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ShoulderChest.blend'),compress=True);print('NECKLINE_CLEARANCE_SAVED',flush=True)
