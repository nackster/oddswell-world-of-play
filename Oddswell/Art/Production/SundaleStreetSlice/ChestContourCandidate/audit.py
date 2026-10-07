"""Cold custody and native 49-frame jacket check for chest contour changes."""
import bpy,ast,array,json,hashlib,struct,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';edited=('Character | tailored slate jacket','Walk cage | refined jacket surface','Character | internal torso support');pair_cache={}
for helper,names in [(art/'HipSeatMotionCandidate/audit.py',('digest','custody','evaluated')),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','geometry','world','lights','lettering')),(art/'TorsoSilhouetteCandidate/audit.py',('screen',))]:
    parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
source=art/'TorsoSilhouetteCandidate/TorsoSilhouette.blend';candidate=out/'ChestContour.blend';build=json.loads((out/'build-report.json').read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)==build['source_sha256']=='3acafeea461315270a579cbddfd3031d98a4478ed2441740ae57ade55a516fe5'
def metadata():
    result={}
    for o in bpy.context.scene.objects:
        if o.type not in ('MESH','CURVE'):continue
        weights=[[(w.group,w.weight) for w in v.groups] for v in o.data.vertices] if o.type=='MESH' else []
        fields={a.name:digest(a.data,'vector',3) if a.data_type=='FLOAT_VECTOR' else digest(a.data,'value',1) for a in o.data.attributes if a.data_type in ('FLOAT','FLOAT_VECTOR')} if o.type=='MESH' else {}
        result[o.name]={'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'hidden':o.hide_render,'materials':[s.material.name if s.material else None for s in o.material_slots],'modifiers':[(m.name,m.type) for m in o.modifiers],'groups':[g.name for g in o.vertex_groups] if o.type=='MESH' else [],'weights':hashlib.sha256(json.dumps(weights).encode()).hexdigest(),'fields':fields}
    return result
bpy.ops.wm.open_mainfile(filepath=str(source));old=custody();old_meta=metadata();old_materials=materials();old_action=action();old_world=world();old_lights=lights();old_text=lettering();cage=bpy.data.objects[edited[1]]
changed=set(edited)|{'Torso fit | isolated anatomical arm contact'}|{o.name for o in bpy.context.scene.objects if any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)}|{o.name for o in bpy.context.scene.objects if o.name.startswith('Walk surface | Character | raglan topstitch ')}
names=[o.name for o in bpy.context.scene.objects if not o.hide_render and o.type in ('MESH','CURVE') and o.name.startswith(('Character | ','Walk surface | Character | ')) and o.name not in changed];old_geometry=geometry(names)
followers=[o.name for o in bpy.context.scene.objects if not o.hide_render and (('front welt' in o.name and any(m.type=='SURFACE_DEFORM' and m.target==cage for m in o.modifiers)) or o.name.startswith('Walk surface | Character | raglan topstitch '))];assert len(followers)==6
baseline=screen('SOURCE',followers)
bpy.ops.wm.open_mainfile(filepath=str(candidate));new=custody()
for name in (edited[0],edited[1],edited[2],'Torso fit | isolated anatomical arm contact'):
    key=build['objects'][edited[2] if name in (edited[2],'Torso fit | isolated anatomical arm contact') else edited[0]]['added_key'];assert set(new[0][name]['keys'])-set(old[0][name]['keys'])=={key}
    new[0][name]['keys']={k:new[0][name]['keys'][k] for k in old[0][name]['keys']}
assert new==old,'Original controls/edges/keys/UVs/maps/rest/six poses changed'
new_meta=metadata()
for name in edited[:2]:
    assert new_meta[name]['materials'][0]==build['material']['name'];new_meta[name]['materials']=old_meta[name]['materials']
assert new_meta==old_meta,'Original metadata/weights/float-vector fields changed'
new_materials=materials();assert {n:new_materials[n] for n in old_materials}==old_materials,'Original shaders changed'
assert action()==old_action and world()==old_world and lights()==old_lights and lettering()==old_text
assert geometry(names)==old_geometry,'Unedited human geometry changed'
frames=screen('CANDIDATE',followers)
for row,prior in zip(frames,baseline):
    new_pairs=pair_cache['CANDIDATE'][row['frame']]-pair_cache['SOURCE'][row['frame']];row['new_body_pair_count']=len(new_pairs);row['new_body_pair_examples']=sorted(new_pairs)[:12]
    for name,detail in row['sewn_details'].items():
        assert detail['maximum_sampled_gap_m']<prior['sewn_details'][name]['maximum_sampled_gap_m']+.003,('Sewn-detail gap regression',row['frame'],name)
        assert detail['maximum_edge_m']<prior['sewn_details'][name]['maximum_edge_m']*1.5+.002,('Sewn-detail edge regression',row['frame'],name)
report={'candidate_sha256':sha(candidate),'source_sha256':sha(source),'original_mesh_curve_count':len(old[0]),'packed_maps':len(old[1]),'original_controls_edges_old_keys_uvs_maps_rig_rest_six_poses_exact':True,'original_metadata_except_declared_material_assignment_weights_fields_shaders_walk_world_lights_text_exact':True,'unchanged_visible_human_objects':len(names),'unchanged_human_six_pose_geometry_exact':True,'source_frames':baseline,'candidate_frames':frames,'scope':'Complete jacket shell versus internal body support, nonadjacent jacket shell pairs, and six visible sewing-detail sampled contact/edge bounds at render subdivision for all 49 authored integer frames. Original support contacts are recorded. Excludes full-body collision, subframes, physical cloth simulation, photographic acceptance and runtime.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['shell_self_pairs']==0 for r in frames),'Jacket self pairs remain'
assert all(r['new_body_pair_count']==0 for r in frames),'New jacket/support pairs'
print('CHEST_CONTOUR_COLD_PASS',flush=True)
