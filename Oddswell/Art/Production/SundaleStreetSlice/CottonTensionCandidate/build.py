"""Develop actual sewn-cloth tension over the retained anatomical walking pose."""
import bpy,ast,math,hashlib,json,bisect
from collections import Counter
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
art=root/'Oddswell/Art/Production/SundaleStreetSlice'
source=art/'AnatomicalNecklineCandidate/AnatomicalNeckline.blend'
source_hash='C72E84C4033D6A8F86C89BECD7A1BB2736460728A32132ADEEE57C1F17932CA3'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()==source_hash
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;coat=bpy.data.objects['Character | tailored slate jacket'];body=bpy.data.objects['Character | internal torso support']
original_body_margin=body.collision.thickness_outer
control=bpy.data.objects['Body flow | stance blend']
ctx={'math':math,'Vector':Vector,'center':Vector((-.75,-2.4,.88))}
parsed=ast.parse((art/'BodyFlowCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('smooth','band','warp')],type_ignores=[]),'body-flow','exec'),ctx)
smooth,warp=ctx['smooth'],ctx['warp']
parsed=ast.parse((art/'RaglanPatternCandidate/build.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('unwarp','drive','update_points')],type_ignores=[]),'raglan-points','exec'))
mesh=coat.data;world,inverse=coat.matrix_world,coat.matrix_world.inverted()
before=[v.co.copy() for v in mesh.vertices]
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[max((g.weight for g in v.groups if g.group==pin.index),default=0) for v in mesh.vertices]
# Transfer the authored neck/shoulder changes into the original sewn rest pattern.
rest=[p.vector+v-q.vector for p,v,q in zip(mesh.attributes['Tailored rest'].data,before,mesh.attributes['Collision fit'].data)]
settings={'frames':80,'quality':10,'mass':.24,'air_damping':5,'tension':32,'compression':16,'shear':12,'bending':.4,'body_margin':.001,'cloth_margin':.002,'self_margin':.003,'collision_quality':4}
cache_key=hashlib.sha256(json.dumps({'source':source_hash,'rest':[list(p) for p in rest],'settings':settings},sort_keys=True).encode()).hexdigest()
cache=out/'drape-bake.json';cached=json.loads(cache.read_text()) if cache.exists() else None
if cached and cached['key']==cache_key:
    raw=[Vector(p) for p in cached['raw']];print('VALIDATED_DRAPE_BAKE_REUSED',flush=True)
else:
    simulated=bpy.data.objects.new('Study | post-neckline native cotton',mesh.copy());scene.collection.objects.link(simulated)
    simulated.matrix_world=world;simulated.shape_key_clear()
    for group in coat.vertex_groups:simulated.vertex_groups.new(name=group.name)
    for i,w in enumerate(weights):
        if w:simulated.vertex_groups[pin.index].add([i],w,'REPLACE')
    simulated.shape_key_add(name='Basis')
    rest_key=simulated.shape_key_add(name='Transferred sewn rest')
    for p,value in zip(rest_key.data,rest):p.co=value
    cloth=simulated.modifiers.new('Native post-neckline cotton settle','CLOTH')
    s=cloth.settings;s.quality=settings['quality'];s.mass=settings['mass'];s.air_damping=settings['air_damping']
    s.tension_stiffness=settings['tension'];s.compression_stiffness=settings['compression'];s.shear_stiffness=settings['shear'];s.bending_stiffness=settings['bending']
    s.rest_shape_key=rest_key;s.vertex_group_mass=pin.name;s.pin_stiffness=1
    c=cloth.collision_settings;c.use_collision=True;c.distance_min=settings['cloth_margin'];c.use_self_collision=True;c.self_distance_min=settings['self_margin'];c.collision_quality=settings['collision_quality']
    cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=settings['frames']
    body.hide_set(False);body.collision.thickness_outer=settings['body_margin']
    for frame in range(1,settings['frames']+1):
        scene.frame_set(frame);bpy.context.view_layer.update()
        if frame%10==0:print('POST_NECKLINE_COTTON_FRAME',frame,flush=True)
    ev=simulated.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    raw=[v.co.copy() for v in me.vertices];ev.to_mesh_clear()
    assert len(raw)==len(before)
    cache.write_text(json.dumps({'key':cache_key,'source_sha256':source_hash,'settings':settings,'raw':[list(p) for p in raw]},allow_nan=False))
    bpy.data.objects.remove(simulated,do_unlink=True)
    body.hide_set(True);scene.frame_set(1)
body.collision.thickness_outer=original_body_margin
assert max((a-b).length for a,b,w in zip(raw,before,weights) if w>.95)<.0002,'Cloth solver moved fixed attachments'
motion=max((a-b).length for a,b in zip(raw,before));print('POST_NECKLINE_RAW_MOTION_M',motion,flush=True)
assert motion<.20,'Native cloth study is unstable'
for name,values in (('Before post neckline cloth',before),('Post neckline sewn rest',rest),('Post neckline raw gravity',raw)):
    attr=mesh.attributes.new(name,'FLOAT_VECTOR','POINT')
    for datum,p in zip(attr.data,values):datum.vector=p
positions=[world@(a if w<.95 else b) for a,b,w in zip(raw,before,weights)]
neighbors=[set() for _ in positions]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
# Round only the tight creases identified by the physical shell overlap screen.
fillet_regions=[((-.8744,-2.3258,1.2734),(.036,.041,.050)),((-.4848,-2.3086,1.2633),(.024,.028,.032)),((-.4942,-2.3344,1.2339),(.027,.030,.032)),((-.5352,-2.3968,1.3219),(.025,.025,.030)),((-.4943,-2.3704,1.2055),(.018,.022,.022))]
factors=[.30*max(1-smooth(sum(((p[a]-c[a])/r[a])**2 for a in range(3))) for c,r in fillet_regions) if weights[i]<.95 else 0 for i,p in enumerate(positions)]
pre_fillet=[p.copy() for p in positions]
for _ in range(30):
    positions=[p.lerp(sum((positions[j] for j in neighbors[i]),Vector())/len(neighbors[i]),factors[i]) for i,p in enumerate(positions)]
fillet_motion=max((a-b).length for a,b in zip(positions,pre_fillet))
print('POST_NECKLINE_FOLD_FILLET_MOTION_M',fillet_motion,flush=True)
def sync():
    for v,k,p in zip(mesh.vertices,mesh.shape_keys.key_blocks['Basis'].data,positions):v.co=inverse@p;k.co=v.co
    mesh.update();bpy.context.view_layer.update()
sync()
# Reuse the evaluated anatomical fitter; do not flatten away the new drape.
finish=(art/'RaglanPatternCandidate/finish.py').read_text()
exec(compile(finish[finish.index('solid=next('):finish.index('# Trace the sewn UV edges themselves;')],'evaluated-cloth-fit','exec'))
key=coat.shape_key_add(name='Original pre-settle jacket',from_mix=False)
for datum,p in zip(key.data,before):datum.co=p
key.value=0
key=coat.shape_key_add(name='Raw post-neckline cotton settle',from_mix=False)
for datum,p in zip(key.data,raw):datum.co=p
key.value=0
exec(compile(finish[finish.index('# Trace the sewn UV edges themselves;'):finish.index("scene['raglan_underarm_relaxation_iterations']")],'sewn-cloth-trim','exec'))
# The subdivided neckline can move between held controls; keep its facing sewn.
facing=bpy.data.objects['Character | collar-to-jacket facing'];collar=bpy.data.objects['Character | standing collar']
facing_before=[v.co.copy() for v in facing.data.vertices]
attr=facing.data.attributes.new('Before post neckline drape facing','FLOAT_VECTOR','POINT')
for datum,p in zip(attr.data,facing_before):datum.vector=p
visibility=[(m,m.show_viewport,m.levels if m.type=='SUBSURF' else None) for obj in (coat,collar) for m in obj.modifiers]
for m,_,_ in visibility:
    if m.type=='SOLIDIFY':m.show_viewport=False
    if m.type=='SUBSURF':m.levels=max(m.levels,m.render_levels)
bpy.context.view_layer.update()
join=globals().copy();join['original']=facing_before
pattern=(art/'AnatomicalNecklineCandidate/build.py').read_text();parsed=ast.parse(pattern)
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('boundary_loops','sampled')],type_ignores=[]),'sewn-facing-functions','exec'),join)
parsed=ast.parse((art/'AnatomicalNecklineCandidate/fit_neckline.py').read_text())
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='clear_body'],type_ignores=[]),'facing-support','exec'),join)
exec(compile(pattern[pattern.index('outer=max('):pattern.index('retained=facing.shape_key_add')],'sewn-facing','exec'),join)
key=facing.shape_key_add(name='Original pre-settle collar facing',from_mix=False)
for datum,p in zip(key.data,facing_before):datum.co=p
key.value=0
for m,visible,level in visibility:
    m.show_viewport=visible
    if level is not None:m.levels=level
scene['post_neckline_cotton_settle']=True
scene['post_neckline_cotton_frames']=settings['frames']
scene['post_neckline_cotton_settings']=json.dumps(settings,sort_keys=True)
scene['post_neckline_raw_maximum_motion_m']=motion
scene['post_neckline_fitted_maximum_motion_m']=max((v.co-p).length for v,p in zip(mesh.vertices,before))
scene['post_neckline_minimum_evaluated_clearance_m']=minimum
scene['post_neckline_fold_fillet_maximum_motion_m']=fillet_motion
scene['post_neckline_fold_fillet_regions']=json.dumps(fillet_regions)
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CottonTension.blend'),compress=True)
print('POST_NECKLINE_DRAPE_SAVED',scene['post_neckline_fitted_maximum_motion_m'],minimum,flush=True)
