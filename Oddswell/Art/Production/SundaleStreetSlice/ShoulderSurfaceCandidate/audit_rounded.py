"""Cold motion measurements; static source preservation is separately scoped."""
import bpy,json,hashlib,array,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonTensionCandidate/CottonTension.blend'
def digest(collection,field,width):
    a=array.array('f',[0.])*len(collection)*width;collection.foreach_get(field,a)
    return hashlib.sha256(a.tobytes()).hexdigest()
def originals():
    result={}
    for obj in bpy.context.scene.objects:
        if obj.type not in {'MESH','CURVE'} or obj.name.startswith('Walk surface | '):continue
        d=obj.data
        if obj.type=='MESH':
            result[obj.name]={'controls':digest(d.vertices,'co',3),'uv':{u.name:digest(u.data,'uv',2) for u in d.uv_layers},'keys':{k.name:digest(k.data,'co',3) for k in d.shape_keys.key_blocks} if d.shape_keys else {}}
        else:
            result[obj.name]={'splines':[{'type':s.type,'controls':digest(s.bezier_points,'co',3),'left':digest(s.bezier_points,'handle_left',3),'right':digest(s.bezier_points,'handle_right',3)} if s.type=='BEZIER' else {'type':s.type,'controls':digest(s.points,'co',4)} for s in d.splines]}
    maps={i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.source=='FILE' and i.packed_file}
    return result,maps
def cloth_screen():
    deps=bpy.context.evaluated_depsgraph_get()
    body=bpy.data.objects['Character | internal torso support'];be=body.evaluated_get(deps);bm=be.to_mesh()
    bv=BVHTree.FromPolygons([be.matrix_world@v.co for v in bm.vertices],[tuple(p.vertices) for p in bm.polygons]);be.to_mesh_clear()
    jacket=bpy.data.objects['Character | tailored slate jacket'];je=jacket.evaluated_get(deps);jm=je.to_mesh()
    pin=jacket.vertex_groups['Collar zipper hem and cuff attachments'].index
    distances=[];free=[];negative=[]
    for v in list(jm.vertices)[::16]:
        p=je.matrix_world@v.co;hit=bv.find_nearest(p)
        if not hit or hit[0] is None:continue
        signed=(p-hit[0]).dot(hit[1]);distances.append(signed)
        weight=max((g.weight for g in v.groups if g.group==pin),default=0)
        if weight<.8:free.append(signed)
        if signed<0:negative.append({'vertex':v.index,'signed_m':signed,'attachment_weight':weight,'world':list(p)})
    je.to_mesh_clear()
    return {'minimum_all_signed_m':min(distances),'minimum_free_signed_m':min(free),'negative_samples':negative,'free_count':len(free),'sample_count':len(distances)}
bpy.ops.wm.open_mainfile(filepath=str(source));before,maps=originals();baseline=cloth_screen()
bpy.ops.wm.open_mainfile(filepath=str(out/'RoundedShoulder.blend'));after,newmaps=originals()
after={name:after[name] for name in before}
assert before==after,'Original mesh controls, UVs or shape-key coordinates changed'
assert maps==newmaps,'Packed source image changed'
scene=bpy.context.scene;rig=bpy.data.objects['Walk study | native anatomical controls']
land=json.loads((out/'landmarks.json').read_text());report=[]
for frame in [1,4,7,10,13,16,19,22,25,37,49]:
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    feet={}
    for side in ['neg','pos']:
        obj=bpy.data.objects[land['feet'][side]['object']];ev=obj.evaluated_get(deps);m=ev.to_mesh()
        pts=[ev.matrix_world@v.co for v in m.vertices];floor=min(p.z for p in pts)
        feet[side]={'floor_m':floor,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]}
        assert floor>.0508,('foot penetrates paving',frame,side,floor)
        ev.to_mesh_clear()
    screen=cloth_screen()
    assert screen['minimum_free_signed_m'] > 0, ('Free cloth intersects anatomy',frame,screen['minimum_free_signed_m'])
    scales={b.name:list(b.scale) for b in rig.pose.bones}
    assert max(abs(s-1) for xyz in scales.values() for s in xyz)<1e-4,'Bone scaling used to hide reach errors'
    report.append({'frame':frame,'feet':feet,'jacket_screen':screen,'bone_scales':scales})
    print('WALK_COLD_FRAME',frame,'free signed minimum',screen['minimum_free_signed_m'],flush=True)
scene.frame_set(1)
slips={}
for side,frames in [('pos',[1,4,7]),('neg',[13,16,19])]:
    bounds=[next(r for r in report if r['frame']==f)['feet'][side]['bounds'] for f in frames]
    slips[side]=max(abs(b[i][j]-bounds[0][i][j]) for b in bounds for i in [0,1] for j in [0,1])
(out/'cold-motion-audit.json').write_text(json.dumps({'original_mesh_curve_count':len(before),'packed_map_count':len(maps),'mesh_controls_uv_keys_and_curve_controls_exact':True,'packed_maps_exact':True,'source_jacket_screen':baseline,'measured_flat_stance_bounds_slip_m':slips,'diagnostic_limit':'Nearest signed-distance sample is not a complete cloth collision proof; source curves remain editable, with skinned evaluated derivatives.','frames':report},indent=2)+'\n')
print('WALK_COLD_AUDIT',len(report),flush=True)
