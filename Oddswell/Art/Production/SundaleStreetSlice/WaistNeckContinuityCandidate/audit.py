"""Cold data custody, bounded jacket shell and sewn waist movement."""
import bpy,ast,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py'
parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody','evaluated')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/HipSeat.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='9775f815af14570a673dc000ea9535c05ef35f06c6b0aeea1260a3105396cb20'
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody()
bpy.ops.wm.open_mainfile(filepath=str(out/'WaistNeck.blend'));after=custody();name='Character | ribbed waistband'
assert set(after[0][name]['keys'])-set(before[0][name]['keys'])=={'Continuous knitted waist fit'}
after[0][name]['keys']={key:after[0][name]['keys'][key] for key in before[0][name]['keys']}
assert ({name:after[0][name] for name in before[0]},*after[1:])==before,'Original controls/edges/UV/keys/maps or rig matrices changed'
scene=bpy.context.scene;coat=bpy.data.objects['Character | tailored slate jacket'];band=bpy.data.objects['Character | ribbed waistband'];solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
for obj in (coat,band,bpy.data.objects['Character | internal torso support']):
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
assert solid.solidify_mode=='EXTRUDE' and not solid.use_even_offset
records=[];rest_edge=None
for frame in range(1,50):
    scene.frame_set(frame);solid.show_viewport=False;deps=bpy.context.evaluated_depsgraph_get();base,faces,_=evaluated(coat,deps)
    solid.show_viewport=True;deps=bpy.context.evaluated_depsgraph_get();shell,_,edges=evaluated(coat,deps);count=len(base)
    assert len(shell)==2*count,('Unexpected simple shell topology',frame,len(shell),count)
    maximum=max((shell[i]-shell[i+count]).length for i in range(count))
    assert maximum<=abs(solid.thickness)+2e-6,('Unbounded fabric thickness',frame,maximum)
    tree=BVHTree.FromPolygons(base,faces)
    ev=band.evaluated_get(deps);mesh=ev.to_mesh();ps=[ev.matrix_world@v.co for v in mesh.vertices];longest=max((ps[e.vertices[0]]-ps[e.vertices[1]]).length for e in mesh.edges)
    if rest_edge is None:rest_edge=longest
    assert longest<2*rest_edge+.001,('Stretched knit waist',frame,longest)
    ev.to_mesh_clear()
    # Evaluate the shape and shared armature without subdivision/thickness so
    # the original upper control ring remains directly identifiable.
    flags=[(m,m.show_viewport) for m in band.modifiers if m.type!='ARMATURE']
    for m,_ in flags:m.show_viewport=False
    ev=band.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();join=[ev.matrix_world@v.co for v in mesh.vertices[-384:]];ev.to_mesh_clear()
    for m,flag in flags:m.show_viewport=flag
    distances=[tree.find_nearest(p)[3] for p in join[::4]]
    assert max(distances)<.004,('Detached waist join',frame,max(distances))
    records.append({'frame':frame,'maximum_shell_layer_displacement_m':maximum,'maximum_knit_edge_m':longest,'maximum_sampled_upper_join_distance_m':max(distances),'join_samples':len(distances)});print('WAIST_NECK_COLD_FRAME',frame,flush=True)
with (out/'WaistNeck.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'cold-audit.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':'9775f815af14570a673dc000ea9535c05ef35f06c6b0aeea1260a3105396cb20','original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'original_controls_edges_uv_old_keys_maps_and_all_rest_six_poses_exact':True,'allowed_added_key':'Continuous knitted waist fit','frames':records,'scope':'All 49 authored integer frames at render subdivision levels: exact simple-shell layer displacement, bounded knit edges and sampled upper seam distance. Not complete garment/body collision, self-intersection or animated-subframe certification.'},indent=2)+'\n');print('WAIST_NECK_COLD_PASS',flush=True)
