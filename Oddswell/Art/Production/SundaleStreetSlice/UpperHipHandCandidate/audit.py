import bpy,ast,array,json,hashlib,math,struct
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';build=json.loads((out/'build-report.json').read_text());source=art/'BodyBalanceCandidate/BodyBalance.blend';candidate=out/'UpperDrape.blend'
for path,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','world','lights','lettering'))]:
    tree=ast.parse(path.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cheap_pose_custody():
    for o in bpy.context.scene.objects:
        for m in o.modifiers:m.show_viewport=False
    return custody()
def weights():
    result={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        h=hashlib.sha256()
        for v in o.data.vertices:
            for g in v.groups:h.update(struct.pack('<IIf',v.index,g.group,g.weight))
        result[o.name]=([g.name for g in o.vertex_groups],h.hexdigest())
    return result
bpy.ops.wm.open_mainfile(filepath=str(source));old_shader=materials();old_world=world();old_lights=lights();old_text=lettering();old_action=action();old_weights=weights();before=cheap_pose_custody();print('UPPER_DRAPE_SOURCE_CUSTODY',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(candidate));assert sha(source)==build['source_sha256'] and sha(candidate)==build['candidate_sha256'];new_action=action();offsets={'pose.bones["'+r['bone']+'"].rotation_euler':math.radians(r['local_x_opening_degrees']) for r in build['finger_changes']};assert len(old_action)==len(new_action)
for a,b in zip(old_action,new_action):
    assert a[:2]==b[:2]
    offset=offsets.get(a[0],0.) if a[1]==0 else 0.
    if not offset:assert a==b,('Undeclared action change',a[:2]);continue
    assert len(a[2])==len(b[2])==49
    for x,y in zip(a[2],b[2]):
        assert x[0][0]==y[0][0] and abs(y[0][1]-x[0][1]-offset)<1e-6
        assert x[1]==y[1] and x[4:]==y[4:]
        for field in (2,3):assert abs(x[field][0]-y[field][0])<1e-6 and abs(y[field][1]-x[field][1]-offset)<1e-6,('Unexpected handle',a[:2],x,y)
assert materials()==old_shader and world()==old_world and lights()==old_lights and lettering()==old_text and weights()==old_weights
rig=bpy.data.objects['Walk study | native anatomical controls'];retained=bpy.data.actions[build['original_action_retained']];rig.animation_data.action=retained;assert action()==old_action
after=cheap_pose_custody()
for name in ('Character | shorts leg continuous tailoring','Hip study | registered cloth midsurface'):after[0][name]['keys'].pop(build['hip_key'])
assert after==before,'Original controls/keys/UVs/maps/rest or retained original action changed'
bpy.context.scene.frame_set(1)
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];assert pants.data==mid.data;key=pants.data.shape_keys.key_blocks[build['hip_key']];basis=pants.data.shape_keys.key_blocks['Basis'];rows={r['id']:r for r in build['affected_controls']};assert key.relative_key==basis and key.value==1.
from mathutils import Vector
for i,v in enumerate(key.data):
    d=pants.matrix_world.inverted().to_3x3()@Vector(rows[i]['delta_world_m']) if i in rows else Vector();expected=basis.data[i].co+d;assert tuple(v.co)==tuple(expected),('Unexpected float32 shape coordinate',i,list(v.co),list(expected))
assert all(i not in rows for i in build['protected_waist_ids'])
report={'source_sha256':sha(source),'candidate_sha256':sha(candidate),'original_controls_edges_old_keys_uv_maps_rest_and_retained_six_poses_exact':True,'packed_maps':len(before[1]),'original_weights_shader_world_lights_lettering_exact':True,'original_action_retained_exact':True,'declared_24_finger_x_channels_only_offset_all_49_keys_handles_verified':True,'upper_hip_key_exact_and_160_waist_boundary_controls_fixed':True,'scope':'Cold source custody and exact declared finger keyframe shifts; surface and visual review separate. Does not certify dynamic cloth, full body contacts, subframes or runtime.'}
(out/'cold-audit.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('UPPER_DRAPE_COLD_PASS',flush=True)
