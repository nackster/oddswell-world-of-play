import bpy, ast, array, hashlib, json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
build=json.loads((out/'build-report.json').read_text(encoding='utf-8'))
for path,names in [(art/'HipSeatMotionCandidate/audit.py',('digest',)),(art/'PromenadeLightCandidate/audit.py',('value','materials','action','world','lights','lettering'))]:
    tree=ast.parse(path.read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'))
def snapshot():
    geometry={};cache={};weights={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        d=o.data
        if d.as_pointer() not in cache:
            cache[d.as_pointer()]={'co':digest(d.vertices,'co',3),'edges':digest(d.edges,'vertices',2),'uv':{u.name:digest(u.data,'uv',2) for u in d.uv_layers},'keys':{k.name:(digest(k.data,'co',3),k.value,k.relative_key.name) for k in d.shape_keys.key_blocks} if d.shape_keys else {}}
        geometry[o.name]=cache[d.as_pointer()]
        if o.name.startswith(('Character | ','Hip study | registered','Walk cage | refined','Torso fit | isolated')):
            weights[o.name]={g.name:[] for g in o.vertex_groups}
            for v in d.vertices:
                for w in v.groups:weights[o.name][o.vertex_groups[w.group].name].append((v.index,w.weight))
    maps={i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.source=='FILE' and i.packed_file}
    rig=bpy.data.objects['Walk study | native anatomical controls']
    rest={b.name:list(x for row in b.matrix_local for x in row) for b in rig.data.bones}
    return geometry,weights,maps,rest,action(),materials(),world(),lights(),lettering()
source=art/'UpperHipHandCandidate/UpperDrape.blend';candidate=out/'PosedEase.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));before=snapshot();print('EASE_SOURCE_CUSTODY',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(candidate));after=snapshot()
torso_names=['Character | internal torso support','Torso fit | isolated anatomical arm contact','Character | tailored slate jacket','Walk cage | refined jacket surface']
# Shared mesh snapshots are copied before stripping declared additions.
for name in torso_names:
    after[0][name]=dict(after[0][name]);after[0][name]['keys']=dict(after[0][name]['keys']);after[0][name]['keys'].pop('Natural ribcage to waist transition')
for name in ('Character | shorts leg continuous tailoring','Hip study | registered cloth midsurface'):
    after[1][name].pop(build['mask'])
assert {name:after[0][name] for name in before[0]}==before[0], 'Unexpected original geometry/key/UV change'
assert after[1:]==before[1:], 'Unexpected original weights/assets/rig/action/shader/scene change'
for name,row in build['torso_changes'].items():
    o=bpy.data.objects[name];basis=o.data.shape_keys.key_blocks['Basis'];key=o.data.shape_keys.key_blocks[row['key']];changes={r['id']:Vector(r['delta_world_m']) for r in row['controls']}
    assert key.value==1. and key.relative_key==basis
    for i,v in enumerate(key.data):
        expected=basis.data[i].co+o.matrix_world.inverted().to_3x3()@changes.get(i,Vector())
        assert tuple(v.co)==tuple(expected), (name,i)
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface']
assert pants.data==mid.data
expected={r['id']:r['weight'] for r in build['mask_weights']};group=pants.vertex_groups[build['mask']]
for v in pants.data.vertices:
    actual=next((g.weight for g in v.groups if g.group==group.index),0.)
    assert abs(actual-expected.get(v.index,0.))<1e-7
assert all(i not in expected for i in build['boundary_ids'])
for o in (pants,mid):
    mods=list(o.modifiers);i=next(i for i,m in enumerate(mods) if m.type=='SUBSURF')
    assert mods[i-2].name=='Posed final cotton anatomical ease' and mods[i-1].name=='Rounded posed cotton fitting transition'
    assert mods[i-1].vertex_group==build['mask'] and mods[i-1].iterations==6
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report={'source_sha256':sha(source),'candidate_sha256':sha(candidate),'original_controls_edges_old_keys_uvs_exact':True,'original_weights_31_packed_maps_rig_action_materials_world_lights_lettering_exact':True,'packed_maps':len(before[2]),'declared_torso_keys_exact_float32_coordinates':True,'cotton_mask_and_protected_boundaries_verified':True,'scope':'Cold editable source custody and declared additions. Surface contacts and visual acceptance require separate review; no runtime or physical cloth certification.'}
assert report['source_sha256']==build['source_sha256'] and report['candidate_sha256']==build['candidate_sha256']
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('EASE_COLD_PASS',flush=True)
