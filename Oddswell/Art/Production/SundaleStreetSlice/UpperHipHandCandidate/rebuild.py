"""Rebuild declared hip controls and finger offsets without evaluating every scene pose."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';report=json.loads((out/'build-report.json').read_text());source=art/'BodyBalanceCandidate/BodyBalance.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==report['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];pants.data=pants.data.copy();mid.data=pants.data;basis=pants.data.shape_keys.key_blocks['Basis'];key=pants.shape_key_add(name=report['hip_key'],from_mix=False);key.relative_key=basis;key.value=1.
for v,p in zip(key.data,basis.data):v.co=p.co
for r in report['affected_controls']:key.data[r['id']].co=basis.data[r['id']].co+pants.matrix_world.inverted().to_3x3()@Vector(r['delta_world_m'])
rig=bpy.data.objects['Walk study | native anatomical controls'];rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name=report['new_action'];offsets={'pose.bones["'+r['bone']+'"].rotation_euler':math.radians(r['local_x_opening_degrees']) for r in report['finger_changes']}
for curve in rig.animation_data.action.fcurves:
    offset=offsets.get(curve.data_path,0.) if curve.array_index==0 else 0.
    if offset:
        for k in curve.keyframe_points:k.co.y+=offset;k.handle_left.y+=offset;k.handle_right.y+=offset
bpy.context.scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'UpperDrape.blend'),compress=True)
with (out/'UpperDrape.blend').open('rb') as f:report['candidate_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
report['rebuild_method']='Declared hip key control offsets and direct finger curve translation; original action retained with fake user.'
(out/'build-report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print('UPPER_DRAPE_REBUILT',flush=True)
