import bpy,array,json,hashlib,math
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric'
def digest(collection,field,width,kind='f'):
    a=array.array(kind,[0])*len(collection)*width;collection.foreach_get(field,a);return hashlib.sha256(a.tobytes()).hexdigest()
def custody(mesh,rig):
    h=hashlib.sha256()
    for v in mesh.data.vertices:
        for g in v.groups:h.update(('%d:%d:%.9g;'%(v.index,g.group,g.weight)).encode())
    return {'coordinates':digest(mesh.data.vertices,'co',3),'edges':digest(mesh.data.edges,'vertices',2,'i'),'polygon_vertex_counts':[p.loop_total for p in mesh.data.polygons],'loop_vertices':digest(mesh.data.loops,'vertex_index',1,'i'),'uvs':{u.name:digest(u.data,'uv',2) for u in mesh.data.uv_layers},'group_names':[g.name for g in mesh.vertex_groups],'weights':h.hexdigest(),'rig_rest':{b.name:[x for row in b.matrix_local for x in row] for b in rig.data.bones}}
bpy.ops.wm.open_mainfile(filepath=str(out/'EricImported.blend'));original=custody(next(o for o in bpy.context.scene.objects if o.type=='MESH'),next(o for o in bpy.context.scene.objects if o.type=='ARMATURE'))
bpy.ops.wm.open_mainfile(filepath=str(out/'ScannedHumanWalk.blend'));mesh=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig'];assert custody(mesh,rig)==original,'Unexpected vendor mesh, UV, weight or rig bind change'
textures={}
for suffix in ('dif','norm','gloss'):
    name='rp_eric_rigged_001_'+suffix+'.jpg';path=out/'EricSource/tex'/name;expected=hashlib.sha256(path.read_bytes()).hexdigest();images=[i for i in bpy.data.images if Path(i.filepath).name==name and i.packed_file];assert images and all(hashlib.sha256(bytes(i.packed_file.data)).hexdigest()==expected for i in images);textures[name]=expected
walk=json.loads((out/'walk-report.json').read_text(encoding='utf-8'));assert [r['frame'] for r in walk['frames']]==list(range(1,50))
for target in walk['mapping']:
    bone=rig.pose.bones[target]
    assert len([f for f in rig.animation_data.action.fcurves if f.data_path==bone.path_from_id('rotation_quaternion')])==4
    for curve in [f for f in rig.animation_data.action.fcurves if f.data_path==bone.path_from_id('rotation_quaternion')]:assert len(curve.keyframe_points)==49 and all(math.isfinite(k.co.y) for k in curve.keyframe_points)
with (out/'ScannedHumanWalk.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
assert sha==walk['candidate_sha256']
report={'candidate_sha256':sha,'original_vendor_mesh_topology_uv_skin_weights_bind_matrices_exact':True,'vendor_packed_texture_file_hashes_exact':textures,'mapped_bones':len(walk['mapping']),'native_key_count_per_quaternion_channel':49,'scope':'Imported source custody and finite authored rotation keys; no complete contact, foot-lock, subframe, or engine validation claim.'}
(out/'cold-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCAN_COLD_PASS',flush=True)
