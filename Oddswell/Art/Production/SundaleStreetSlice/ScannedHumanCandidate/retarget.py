"""Author a local motion study on the vendor skeleton without changing its skin mesh."""
import bpy,math,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric';root=next(p for p in out.parents if (p/'.git').exists())
bpy.ops.wm.open_mainfile(filepath=str(out/'ScannedHumanScene.blend'));scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['Scan character | Eric rig'];body=bpy.data.objects['Scan character | Eric mesh'];holder=bpy.data.objects['Scan character | placement'];driver=bpy.data.objects['Walk study | native anatomical controls']
# Protect the entire prior human dependency chain, including sewn followers.
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/BodyBalanceCandidate/audit.py';tree=ast.parse(helper.read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='dependencies'],type_ignores=[]),str(helper),'exec'))
seed={o.name for o in scene.objects if o.name.startswith(('Character | ','Walk surface | Character | ','Walk cage | refined jacket','Hip study | registered cloth'))}
for name in dependencies(seed):bpy.data.objects[name].hide_render=True
mat=body.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');socket=bs.inputs['Roughness'];old=socket.links[0].from_socket;clamp=nodes.new('ShaderNodeMath');clamp.operation='MAXIMUM';clamp.inputs[1].default_value=.42;links.new(old,clamp.inputs[0]);links.new(clamp.outputs[0],socket);bs.inputs['Specular IOR Level'].default_value=.3
mapping={'hip':'pelvis','spine_01':'chest','spine_02':'chest','spine_03':'chest','neck':'head','head':'head','shoulder_l':'chest','shoulder_r':'chest'}
for suffix,side in [('l','neg'),('r','pos')]:
    for target,source in [('upperarm','upperarm'),('lowerarm','forearm'),('hand','palm'),('upperleg','thigh'),('lowerleg','shin'),('foot','foot')]:mapping[target+'_'+suffix]=side+'.'+source
assert all(n in rig.pose.bones and s in driver.pose.bones for n,s in mapping.items())
bpy.context.view_layer.update();base_world={b.name:(rig.matrix_world@b.matrix).to_quaternion() for b in rig.pose.bones};static={b.name:b.matrix_basis.to_quaternion() for b in rig.pose.bones};rest={b.name:b.bone.matrix_local.to_quaternion() for b in rig.pose.bones};driver_rest={n:(driver.matrix_world@driver.data.bones[n].matrix_local).to_quaternion() for n in set(mapping.values())};driver_hip=driver.matrix_world@driver.data.bones['pelvis'].head_local;base_location=holder.location.copy();records=[]
rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new('OddsWell walk | scanned Eric skeleton study')
for b in rig.pose.bones:b.rotation_mode='QUATERNION'
ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
for frame in range(1,50):
    scene.frame_set(frame);deltas={n:(driver.matrix_world@driver.pose.bones[n].matrix).to_quaternion()@driver_rest[n].inverted() for n in driver_rest};pose={};world_inv=rig.matrix_world.to_quaternion().inverted()
    for b in ordered:
        relative=rest[b.parent.name].inverted()@rest[b.name] if b.parent else rest[b.name];parent=pose[b.parent.name] if b.parent else __import__('mathutils').Quaternion()
        basis=(parent@relative).inverted()@(world_inv@deltas[mapping[b.name]]@base_world[b.name]) if b.name in mapping else static[b.name]
        b.rotation_quaternion=basis;pose[b.name]=parent@relative@basis
        if b.name in mapping:b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
    holder.location=base_location+(driver.matrix_world@driver.pose.bones['pelvis'].head-driver_hip)
    bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();assert all(math.isfinite(x) for p in points for x in p)
    floor=min(p.z for p in points);holder.location.z-=floor;holder.keyframe_insert('location',frame=frame);records.append({'frame':frame,'grounding_adjustment_m':-floor,'height_m':max(p.z for p in points)-floor})
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ScannedHumanWalk.blend'),compress=True)
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report={'standing_source_sha256':sha(out/'ScannedHumanScene.blend'),'candidate_sha256':sha(out/'ScannedHumanWalk.blend'),'mapping':mapping,'frames':records,'method':'World rotation deltas from the retained native walk, calibrated against relaxed imported pose; vendor hierarchy/mesh/UV/weights unchanged. Per-key lowest-vertex floor correction.','scope':'49-key offline motion study. Not runtime retarget certification, foot-lock/slip proof, complete contacts, or physical clothing simulation. Source business clothing remains.'}
(out/'walk-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCAN_WALK_BUILT',report['candidate_sha256'],flush=True)
