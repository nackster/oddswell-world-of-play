"""Cold hand/detail contact and retained body-motion checks at eleven poses."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/ShoulderSurfaceCandidate/RoundedShoulder.blend'
frames=[1,4,7,10,13,16,19,22,25,37,49]
def surface(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    points=[ev.matrix_world@v.co for v in mesh.vertices];faces=[tuple(p.vertices) for p in mesh.polygons]
    ev.to_mesh_clear();return BVHTree.FromPolygons(points,faces),points
def contacts():
    report={}
    for label in ['left','right']:
        hand=bpy.data.objects['Character | anatomical '+label+' hand'];tree,_=surface(hand)
        for kind in ['nail','nail fold']:
            for digit in range(1,6):
                obj=bpy.data.objects[f'Character | {kind} {label} {digit}'];_,ps=surface(obj);distances=[];signed=[]
                for p in ps[::12]:
                    hit,normal,_,distance=tree.find_nearest(p);assert hit is not None
                    distances.append(distance);signed.append((p-hit).dot(normal))
                report[obj.name]={'maximum_nearest_m':max(distances),'minimum_signed_m':min(signed),'maximum_signed_m':max(signed),'samples':len(distances)}
    return report
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='7e04b1847acdbb58096ff57c654e388768e91726808f95caaf203e8ef18f82dd'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;rig=bpy.data.objects['Walk study | native anatomical controls'];original_names=[b.name for b in rig.data.bones]
rest={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
source_poses={};baseline={}
for frame in frames:
    scene.frame_set(frame);bpy.context.view_layer.update()
    source_poses[frame]={name:[list(row) for row in rig.pose.bones[name].matrix] for name in original_names}
    if frame in [1,13]:baseline[frame]=contacts()
bpy.ops.wm.open_mainfile(filepath=str(out/'HandMotion.blend'));scene=bpy.context.scene;rig=bpy.data.objects['Walk study | native anatomical controls']
assert len(rig.data.bones)==46
for name,matrix in rest.items():assert max(abs(rig.data.bones[name].matrix_local[r][c]-matrix[r][c]) for r in range(4) for c in range(4))<1e-6
scene.frame_set(1);rest_edge_lengths={}
for label in ['left','right']:
    obj=bpy.data.objects['Character | sleeve cuff '+label];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    rest_edge_lengths[label]=max((mesh.vertices[e.vertices[1]].co-mesh.vertices[e.vertices[0]].co).length for e in mesh.edges);ev.to_mesh_clear()
report=[];tips={side:[] for side in ['neg','pos']}
for frame in frames:
    scene.frame_set(frame);bpy.context.view_layer.update()
    error=max(abs(rig.pose.bones[name].matrix[r][c]-source_poses[frame][name][r][c]) for name in original_names for r in range(4) for c in range(4))
    assert error<1e-6,('Existing body action changed',frame,error)
    details=contacts()
    for name,record in details.items():assert record['maximum_nearest_m']<.0015,('Detached digit detail',frame,name,record)
    for side in tips:
        inverse=rig.pose.bones[side+'.forearm'].matrix.inverted()
        tips[side].append([list(inverse@rig.pose.bones[f'{side}.digit{digit}.3'].tail) for digit in range(1,6)])
    cuffs={}
    for label in ['left','right']:
        obj=bpy.data.objects['Character | sleeve cuff '+label];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
        areas=[(mesh.vertices[t.vertices[1]].co-mesh.vertices[t.vertices[0]].co).cross(mesh.vertices[t.vertices[2]].co-mesh.vertices[t.vertices[0]].co).length*.5 for t in mesh.loop_triangles]
        assert all(math.isfinite(a) for a in areas) and min(areas)>1e-13,('Collapsed cuff surface',frame,label,min(areas))
        longest=max((mesh.vertices[e.vertices[1]].co-mesh.vertices[e.vertices[0]].co).length for e in mesh.edges)
        assert longest<rest_edge_lengths[label]*3+.001,('Stretched cuff surface',frame,label,longest,rest_edge_lengths[label])
        cuffs[label]={'minimum_triangle_area_m2':min(areas),'triangles':len(areas),'maximum_edge_length_m':longest,'frame1_maximum_edge_length_m':rest_edge_lengths[label]};ev.to_mesh_clear()
    report.append({'frame':frame,'existing_body_pose_maximum_error':error,'digit_details':details,'cuff_surface':cuffs})
    print('HAND_COLD_FRAME',frame,'maximum detail gap',max(r['maximum_nearest_m'] for r in details.values()),flush=True)
movement={side:[max((Vector(sample[d])-Vector(tips[side][0][d])).length for sample in tips[side]) for d in range(5)] for side in tips}
assert min(value for values in movement.values() for value in values)>.0003,'Finger gesture did not actually change'
with (out/'HandMotion.blend').open('rb') as f:candidate_hash=hashlib.file_digest(f,'sha256').hexdigest()
(out/'hand-contact-audit.json').write_text(json.dumps({'candidate_sha256':candidate_hash,'source_sha256':'7e04b1847acdbb58096ff57c654e388768e91726808f95caaf203e8ef18f82dd','original_body_bones':14,'native_bones':46,'existing_rest_and_eleven_body_poses_unchanged':True,'source_detail_baselines':baseline,'fingertip_motion_relative_to_forearm_m':movement,'frames':report,'scope':'Eleven keyed poses, sampled nearest skin/detail contact, positive cuff triangle areas and bounded cuff edge lengths; not a complete hand/cloth self-intersection or every-subframe certificate.'},indent=2)+'\n')
print('HAND_COLD_AUDIT',movement,flush=True)
