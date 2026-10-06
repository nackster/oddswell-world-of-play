"""Cold source custody and all-frame shorts contact/stretch checks."""
import bpy,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/HandArticulationCandidate/HandMotion.blend'
def digest(collection,field,width):
    a=array.array('i' if field=='vertices' else 'f',[0])*len(collection)*width;collection.foreach_get(field,a);return hashlib.sha256(a.tobytes()).hexdigest()
def custody():
    controls={}
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH':
            d=obj.data;controls[obj.name]={'co':digest(d.vertices,'co',3),'edges':digest(d.edges,'vertices',2),'uv':{u.name:digest(u.data,'uv',2) for u in d.uv_layers},'keys':{k.name:digest(k.data,'co',3) for k in d.shape_keys.key_blocks} if d.shape_keys else {}}
        elif obj.type=='CURVE':controls[obj.name]=[digest(s.points,'co',4) if s.type!='BEZIER' else digest(s.bezier_points,'co',3) for s in obj.data.splines]
    maps={i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.source=='FILE' and i.packed_file}
    rig=bpy.data.objects['Walk study | native anatomical controls'];rest={b.name:list(v for row in b.matrix_local for v in row) for b in rig.data.bones};poses={}
    for frame in (1,7,13,25,33,49):
        bpy.context.scene.frame_set(frame);poses[frame]={b.name:list(v for row in b.matrix for v in row) for b in rig.pose.bones}
    return controls,maps,rest,poses
def evaluated(obj,deps):
    ev=obj.evaluated_get(deps);mesh=ev.to_mesh();points=[ev.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons];edges=[tuple(e.vertices) for e in mesh.edges];ev.to_mesh_clear();return points,faces,edges
def screen_region():
    bpy.context.scene.frame_set(1)
    for name in ('anatomical legs','shorts leg continuous tailoring'):
        for mod in bpy.data.objects['Character | '+name].modifiers:
            if mod.type=='SUBSURF':mod.levels=mod.render_levels
    deps=bpy.context.evaluated_depsgraph_get();points,_,_=evaluated(bpy.data.objects['Character | shorts leg continuous tailoring'],deps)
    ids=[i for i in range(0,len(points),16) if .60<points[i].z<.70]
    points,faces,_=evaluated(bpy.data.objects['Character | anatomical legs'],deps)
    skin_faces=[i for i,face in enumerate(faces) if abs((points[face[1]]-points[face[0]]).cross(points[face[2]]-points[face[0]]).normalized().z)<.85]
    return ids,skin_faces
def leg_screen(region):
    deps=bpy.context.evaluated_depsgraph_get();points,faces,_=evaluated(bpy.data.objects['Character | anatomical legs'],deps);tree=BVHTree.FromPolygons(points,[faces[i] for i in region[1]])
    points,_,_=evaluated(bpy.data.objects['Character | shorts leg continuous tailoring'],deps);values=[]
    for i in region[0]:
        p=points[i]
        hit=tree.find_nearest(p)
        if hit[0] is not None:values.append((p-hit[0]).dot(hit[1]))
    return {'minimum_signed_m':min(values),'negative_samples':sum(v<0 for v in values),'samples':len(values)}
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody();baseline={};region=screen_region()
cache=out/'source-leg-screen.json'
stored=json.loads(cache.read_text()) if cache.exists() else {}
if stored.get('screen_version')==2:
    assert stored['source_sha256']=='dc0b0884a33e515d982cccc89c315de5f693fd170220028d786b43af8ae90750';baseline={int(k):v for k,v in stored['frames'].items()}
else:
    for frame in range(1,50):
        bpy.context.scene.frame_set(frame);baseline[frame]=leg_screen(region);print('SOURCE_LEG_FRAME',frame,flush=True)
    cache.write_text(json.dumps({'source_sha256':'dc0b0884a33e515d982cccc89c315de5f693fd170220028d786b43af8ae90750','screen_version':2,'scope':'Rest-registered 0.60–0.70 m shorts band against skin faces, excluding artificial leg-cap faces; both objects at render subdivision levels','frames':baseline},indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(out/'HipSeat.blend'));after=custody()
assert ({name:after[0][name] for name in before[0]},*after[1:])==before,'Original controls/UV/keys/maps or rig matrices changed'
screen_region()  # Set render levels; retain the exact source-registered indices.
scene=bpy.context.scene;coat=bpy.data.objects['Character | shorts leg continuous tailoring'];names=json.loads((out/'build-report.json').read_text())['bindings'];rest_edges={};records=[]
for obj in [coat,bpy.data.objects['Character | anatomical legs']]:
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
for frame in range(1,50):
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();trees={};details={}
    for target in {r['target'] for r in names.values()}:
        points,faces,_=evaluated(bpy.data.objects[target],deps);trees[target]=BVHTree.FromPolygons(points,faces)
    for name in names:
        obj=bpy.data.objects[name]
        if any(m.type=='NODES' for m in obj.modifiers):
            ev=obj.evaluated_get(deps);m=ev.to_mesh();assert all(v.value for v in m.attributes['Sewn UV sample valid'].data),('Invalid cloth UV sample',frame,name);ev.to_mesh_clear()
        points,faces,edges=evaluated(obj,deps)
        longest=max((points[a]-points[b]).length for a,b in edges)
        if frame==1:rest_edges[name]=longest
        assert longest<rest_edges[name]*2+.002,('Stretched shorts detail',frame,name,longest,rest_edges[name])
        distances=[trees[names[name]['target']].find_nearest(p)[3] for p in points[::8]]
        assert max(distances)<.004,('Detached shorts detail',frame,name,max(distances))
        details[name]={'max_edge_m':longest,'max_sampled_cloth_distance_m':max(distances),'samples':len(distances)}
    screen=leg_screen(region)
    # The source screen can include open thigh-cap ambiguity. Record it and
    # reject a new penetration deeper than the inherited source by 1 mm.
    assert screen['minimum_signed_m']>=baseline[frame]['minimum_signed_m']-.001,('Leg clearance regression',frame,screen,baseline[frame])
    records.append({'frame':frame,'shorts_details':details,'leg_screen':screen,'source_leg_screen':baseline[frame]});print('HIP_COLD_FRAME',frame,flush=True)
with (out/'HipSeat.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'cold-audit.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':json.loads((out/'build-report.json').read_text())['source_sha256'],'original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'all_original_controls_uv_keys_maps_and_rest_six_poses_exact':True,'frames':records,'scope':'49 authored integer frames at render subdivision levels. Bounded detail edge stretch and nearest-cloth samples. Signed nearest-leg screening includes inherited ambiguities and is not complete collision or animated-subframe certification.'},indent=2)+'\n')
print('HIP_COLD_PASS',flush=True)
