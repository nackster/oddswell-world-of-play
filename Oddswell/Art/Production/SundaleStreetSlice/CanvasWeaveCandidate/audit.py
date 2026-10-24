"""Cold preservation and unchanged evaluated geometry for a UV/shader study."""
import bpy,ast,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py'
parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/ThighDrapeCandidate/ThighDrape.blend'
with source.open('rb') as f:source_sha=hashlib.file_digest(f,'sha256').hexdigest()
assert source_sha=='c14ec89ca354a9dbe498c6955cde745e2edcb977c9b8603d9e37080247fffeac'
names=['Character | '+part+side for side in ('left','right') for part in ('canvas sneaker ','canvas sneaker tongue ')]
def geometry():
    records={}
    for frame in (1,7,13,25,33,49):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();records[frame]={}
        for name in (*names,'Character | shorts leg continuous tailoring','Character | anatomical legs'):
            obj=bpy.data.objects[name];ev=obj.evaluated_get(deps);mesh=ev.to_mesh();records[frame][name]={'co':digest(mesh.vertices,'co',3),'edges':digest(mesh.edges,'vertices',2)};ev.to_mesh_clear()
    return records
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();old_geometry=geometry()
bpy.ops.wm.open_mainfile(filepath=str(out/'NaturalCanvas.blend'));after=custody();new_geometry=geometry();uvs={}
for name in names:
    assert set(after[0][name]['uv'])-set(before[0][name]['uv'])=={'Rest sewn canvas panels'}
    after[0][name]['uv']={n:after[0][name]['uv'][n] for n in before[0][name]['uv']}
    obj=bpy.data.objects[name];layer=obj.data.uv_layers['Rest sewn canvas panels'];obj.data.calc_loop_triangles();zero=[]
    for t in obj.data.loop_triangles:
        a,b,c=[layer.data[i].uv for i in t.loops]
        if t.area>1e-10 and abs((b-a).cross(c-a))<1e-12:zero.append(t.index)
    assert not zero;uvs[name]={'hash':digest(layer.data,'uv',2),'loop_count':len(layer.data),'triangles':len(obj.data.loop_triangles),'nondegenerate_triangles_with_zero_uv_area':0}
    for material in obj.data.materials:
        if not material.name.startswith('Canvas study | '):continue
        for node in material.node_tree.nodes:
            if node.type=='TEX_IMAGE':assert node.inputs['Vector'].is_linked and node.inputs['Vector'].links[0].from_node.type=='UVMAP' and node.inputs['Vector'].links[0].from_node.uv_map=='Rest sewn canvas panels'
assert ({name:after[0][name] for name in before[0]},*after[1:])==before,'Original controls/edges/UVs/keys/maps/rest/poses changed'
assert new_geometry==old_geometry,'Evaluated shoe/cloth/leg geometry changed'
build=json.loads((out/'build-report.json').read_text());seams=build['fitted_panel_seams'];foot_details=build['foot_detail_weights'];assert len(seams)==6 and len(foot_details)==6;seam_frames=[]
rig=bpy.data.objects['Walk study | native anatomical controls']
for name,record in foot_details.items():
    obj=bpy.data.objects[name];bone_ids={g.index:g.name for g in obj.vertex_groups if g.name in rig.data.bones}
    for vertex in obj.data.vertices:
        weights={bone_ids[w.group]:w.weight for w in vertex.groups if w.group in bone_ids and w.weight>1e-7}
        assert weights=={record['foot_bone']:1.},(name,vertex.index,weights)
for frame in range(1,50):
    bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();trees={};details={}
    sole_trees={}
    for side in ('left','right'):
        shoe=bpy.data.objects['Character | canvas sneaker '+side];ev=shoe.evaluated_get(deps);mesh=ev.to_mesh();trees[side]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
        sole=bpy.data.objects['Character | sneaker sole '+side];ev=sole.evaluated_get(deps);mesh=ev.to_mesh();sole_trees[side]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
    for name in seams:
        obj=bpy.data.objects[name];assert obj.data.shape_keys.key_blocks['Fitted canvas panel seam'].value==1
        side='left' if 'left' in name else 'right';ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];distances=[trees[side].find_nearest(p)[3] for p in points[::4]];edge=max((points[e.vertices[0]]-points[e.vertices[1]]).length for e in mesh.edges)
        assert max(distances)<.0015,('Detached shoe stitch',frame,name,max(distances));assert edge<.0066,('Stretched shoe stitch',frame,name,edge)
        details[name]={'maximum_sampled_upper_distance_m':max(distances),'maximum_edge_m':edge,'samples':len(distances)};ev.to_mesh_clear()
    weighted_details={}
    for name in foot_details:
        obj=bpy.data.objects[name];side='left' if 'left' in name else 'right';tree=trees[side] if 'heel counter' in name else sole_trees[side];ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];values=[tree.find_nearest(p)[3] for p in points[::8]]
        assert max(values)<.004,('Detached foot detail',frame,name,max(values));weighted_details[name]={'maximum_sampled_target_distance_m':max(values),'samples':len(values)};ev.to_mesh_clear()
    seam_frames.append({'frame':frame,'fitted_seams':details,'foot_weighted_details':weighted_details});print('CANVAS_SEAM_FRAME',frame,flush=True)
with (out/'NaturalCanvas.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'candidate_sha256':sha,'source_sha256':source_sha,'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'all_original_controls_edges_uv_keys_maps_rest_and_six_poses_exact':True,'six_pose_evaluated_shoe_shorts_leg_coordinates_edges_exact':True,'uvs':uvs,'evaluated_geometry':new_geometry,'fitted_seam_frames':seam_frames,'inherited_cloth_audit':'Immediate source ThighDrapeCandidate/cold-audit.json certifies its scoped 49 integer-frame shorts/leg and self-overlap checks. This footwear study does not repeat or broaden that collision claim.','scope':'Four added native footwear UV layers, copies of three canvas materials, six added curve-fitting keys and foot-bone weights for six existing heel/sole detail meshes. Original control geometry/UVs/keys/maps and full native rig rest/six-pose custody. Evaluated six-pose shoe, shorts and leg geometry remains exact; sampled seam/detail contact and bounded stitch edge checks span all 49 authored integer frames. This does not certify full-body collision freedom, animated subframes, physical cloth, final photographic realism or runtime compatibility.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('CANVAS_COLD_PASS',flush=True)
