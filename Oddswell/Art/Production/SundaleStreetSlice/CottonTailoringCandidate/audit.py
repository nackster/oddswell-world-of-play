"""Cold native custody, registered garment attachments and all authored walking frames."""
import bpy,ast,array,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/audit.py'
parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('digest','custody','evaluated','screen_region','leg_screen')],type_ignores=[]),str(helper),'exec'))
source=root/'Oddswell/Art/Production/SundaleStreetSlice/WaistNeckContinuityCandidate/WaistNeck.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='2900363715a0056444b9b85509a00dcc01ab6c5e5cfee4fcac32a537af513079'
bpy.ops.wm.open_mainfile(filepath=str(source));before=custody()
for mod in bpy.data.objects['Hip study | actual leg skin clearance'].modifiers:
    if mod.type=='SUBSURF':mod.levels=mod.render_levels
region=screen_region();baseline={};cache=out/'source-leg-screen.json'
if cache.exists():
    stored=json.loads(cache.read_text());assert stored['source_sha256']=='2900363715a0056444b9b85509a00dcc01ab6c5e5cfee4fcac32a537af513079' and stored['screen_version']==3
    baseline={int(k):v for k,v in stored['frames'].items()};assert set(baseline)==set(range(1,50))
else:
    for frame in range(1,50):
        bpy.context.scene.frame_set(frame);baseline[frame]=leg_screen(region);print('COTTON_SOURCE_FRAME',frame,flush=True)
    cache.write_text(json.dumps({'source_sha256':'2900363715a0056444b9b85509a00dcc01ab6c5e5cfee4fcac32a537af513079','screen_version':3,'scope':'Source-pinned rest-registered lower-leg band with actual leg skin clearance helper at render subdivision resolution','frames':baseline},indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(out/'CottonDetail.blend'));after=custody()
assert ({name:after[0][name] for name in before[0]},*after[1:])==before,'Original controls/UV/keys/maps or rig matrices changed'
scene=bpy.context.scene;pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];coat=bpy.data.objects['Character | tailored slate jacket'];band=bpy.data.objects['Character | ribbed waistband']
for obj in (pants,mid,coat,band,bpy.data.objects['Character | anatomical legs'],bpy.data.objects['Character | internal torso support'],bpy.data.objects['Hip study | actual leg skin clearance']):
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':mod.levels=mod.render_levels
followers=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and any(m.type=='NODES' and (m.name.startswith('Sewn actual cloth UV registration') or m.name=='Actual cloth UV folded hem') for m in o.modifiers)]
assert any(o.name=='Hip study | continuous turned cotton hems' for o in followers)
rest_edges={};records=[]
for frame in range(1,50):
    scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();p,faces,_=evaluated(pants,deps);pants_tree=BVHTree.FromPolygons(p,faces);details={}
    for obj in followers:
        ev=obj.evaluated_get(deps);mesh=ev.to_mesh();assert all(v.value for v in mesh.attributes['Sewn UV sample valid'].data),('Invalid registered UV',frame,obj.name);ev.to_mesh_clear()
        points,_,edges=evaluated(obj,deps);longest=max((points[a]-points[b]).length for a,b in edges)
        if frame==1:rest_edges[obj.name]=longest
        assert longest<rest_edges[obj.name]*2+.002,('Stretched attachment',frame,obj.name,longest)
        distances=[pants_tree.find_nearest(p)[3] for p in points[::8]]
        # Jacket welts have their own garment target and no pants registration.
        assert max(distances)<.004,('Detached registered shorts attachment',frame,obj.name,max(distances))
        details[obj.name]={'maximum_edge_m':longest,'maximum_sampled_cloth_distance_m':max(distances),'samples':len(distances)}
    screen=leg_screen(region);assert screen['minimum_signed_m']>=baseline[frame]['minimum_signed_m']-.001,('Leg clearance regression',frame,screen,baseline[frame])
    records.append({'frame':frame,'registered_shorts_details':details,'leg_screen':screen,'source_leg_screen':baseline[frame]});print('COTTON_COLD_FRAME',frame,flush=True)
with (out/'CottonDetail.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'cold-audit.json').write_text(json.dumps({'candidate_sha256':sha,'source_sha256':'2900363715a0056444b9b85509a00dcc01ab6c5e5cfee4fcac32a537af513079','original_mesh_curve_count':len(before[0]),'packed_maps':len(before[1]),'all_original_controls_edges_uv_keys_maps_rest_and_six_poses_exact':True,'frames':records,'scope':'All 49 authored integer frames at render subdivision levels. Registered UV validity, attachment stretch/contact and source-compared signed lower-leg band screening. Not complete collision, subframe, runtime or visual acceptance certification.'},indent=2)+'\n');print('COTTON_COLD_PASS',flush=True)
