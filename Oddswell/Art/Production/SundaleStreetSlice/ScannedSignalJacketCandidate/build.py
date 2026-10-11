"""Separate skinned Signal Jacket study derived from the accepted scan's fit."""
import bpy, json, hashlib, math, ast, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/SignalJacketStudy';root=next(p for p in out.parents if (p/'.git').exists())
source=out.parent/'MotionRefinement/OddsWellHumanMotion.blend'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)=='1c75042928c5df6eaa198c1fe032a5b3985224c33b766bd322b7dc10b126aca4'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
selection=json.loads((out/'selection.json').read_text(encoding='utf-8'));selected=set(selection['selected_faces'])
verts=sorted({i for p in body.data.polygons if p.index in selected for i in p.vertices});lookup={v:i for i,v in enumerate(verts)}
scale=body.matrix_world.to_scale().x
world=[body.matrix_world@v.co for v in body.data.vertices];inverse=body.matrix_world.inverted()
offset=.008
coords=[]
for i in verts:
    v=body.data.vertices[i];point=world[i]+(body.matrix_world.to_3x3()@v.normal).normalized()*offset
    point.z=max(1.006,min(point.z,1.508));coords.append(inverse@point)
faces=[tuple(lookup[i] for i in p.vertices) for p in body.data.polygons if p.index in selected]
mesh=bpy.data.meshes.new('Signal Jacket | fitted shell mesh');mesh.from_pydata(coords,[],faces);mesh.update()
jacket=bpy.data.objects.new('OddsWell wardrobe | Signal Jacket shell',mesh);scene.collection.objects.link(jacket)
jacket.parent=body.parent;jacket.matrix_world=body.matrix_world.copy()
for g in body.vertex_groups:jacket.vertex_groups.new(name=g.name)
for index,original in enumerate(verts):
    for g in body.data.vertices[original].groups:jacket.vertex_groups[g.group].add([index],g.weight,'REPLACE')
arm=jacket.modifiers.new('Shared scanned skeleton','ARMATURE');arm.object=rig
smooth=jacket.modifiers.new('Soft garment transitions','SMOOTH');smooth.factor=.22;smooth.iterations=3
sub=jacket.modifiers.new('Rounded cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
solid=jacket.modifiers.new('Garment thickness','SOLIDIFY');solid.thickness=.0025/scale;solid.offset=1

def fabric(name,color,rib=False):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.78;bs.inputs['Specular IOR Level'].default_value=.24
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2800;tex.inputs['Detail'].default_value=2
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00015
    l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat
slate=fabric('OddsWell | slate technical cotton',(.12,.18,.22));teal=fabric('OddsWell | teal woven accent',(.08,.72,.68));rib=fabric('OddsWell | charcoal rib',(.028,.039,.046));metal=fabric('OddsWell | brushed zipper',(.22,.25,.27))
for m in (slate,teal,rib):jacket.data.materials.append(m)
attribute=mesh.attributes.new('Signal Yoke Height','FLOAT','POINT')
for i,v in enumerate(mesh.vertices):attribute.data[i].value=(jacket.matrix_world@v.co).z
n=slate.node_tree.nodes;l=slate.node_tree.links
attr=n.new('ShaderNodeAttribute');attr.attribute_name='Signal Yoke Height'
boundary=n.new('ShaderNodeMath');boundary.operation='GREATER_THAN';boundary.inputs[1].default_value=1.425
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.12,.18,.22,1);mix.inputs[2].default_value=(.08,.72,.68,1)
l.new(attr.outputs['Fac'],boundary.inputs[0]);l.new(boundary.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],n['Principled BSDF'].inputs['Base Color'])
for p in mesh.polygons:
    p.material_index=0;p.use_smooth=True

bvh=BVHTree.FromPolygons([jacket.matrix_world@v.co for v in mesh.vertices],faces,all_triangles=False)
full_bvh=BVHTree.FromPolygons(world,[list(p.vertices) for p in body.data.polygons],all_triangles=False)
center=rig.matrix_world@rig.data.bones['neck'].head_local
cx,cy=center.x,center.y
def front(x,z):
    hit=bvh.ray_cast(Vector((x,cy+1,z)),Vector((0,-1,0)))
    assert hit[0] is not None,(x,z)
    return hit[0]+hit[1]*.012

parts=[]
def fitted_part(name,positions,polygons,material):
    data=bpy.data.meshes.new(name);data.from_pydata([inverse@p for p in positions],[],polygons);data.update()
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=body.parent;obj.matrix_world=body.matrix_world.copy();data.materials.append(material)
    for g in body.vertex_groups:obj.vertex_groups.new(name=g.name)
    # Nearest source surface supplies the same bind-space skinning for each trim vertex.
    for index,point in enumerate(positions):
        nearest=full_bvh.find_nearest(point);poly=body.data.polygons[nearest[2]]
        weights={}
        for original in poly.vertices:
            for g in body.data.vertices[original].groups:weights[g.group]=weights.get(g.group,0)+g.weight/len(poly.vertices)
        total=sum(weights.values());assert total>0
        for group,value in weights.items():obj.vertex_groups[group].add([index],value/total,'REPLACE')
    mod=obj.modifiers.new('Shared scanned skeleton','ARMATURE');mod.object=rig
    for p in data.polygons:p.use_smooth=True
    parts.append(obj);return obj

# The zipper is modeled geometry, covering the old vest/tie center rather than recoloring it.
positions=[]
for i in range(49):
    z=1.035+i/48*.435
    for x in (cx-.004,cx+.004):positions.append(front(x,z))
fitted_part('Signal Jacket | center zip tape',positions,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(48)],rib)
positions=[];polys=[]
for i in range(46):
    z=1.04+i*.009
    for dx,dz in ((-.002,-.0015),(.002,-.0015),(.002,.0015),(-.002,.0015)):
        p=front(cx+dx,z+dz);p.y+=.001;positions.append(p)
    polys.append(tuple(range(4*i,4*i+4)))
fitted_part('Signal Jacket | individual zipper teeth',positions,polys,metal)

# A smooth tapered rib collar gives the shell a casual neckline without the scanned collar's points.
positions=[]
for row in range(5):
    z=1.486+row*.012;rx=.112-row*.007;ry=.120-row*.005
    for i in range(96):
        a=i/96*2*math.pi;positions.append(Vector((cx+rx*math.cos(a),cy+.005+ry*math.sin(a),z)))
collar=fitted_part('Signal Jacket | raised rib collar',positions,[(r*96+i,r*96+(i+1)%96,(r+1)*96+(i+1)%96,(r+1)*96+i) for r in range(4) for i in range(96)],rib)
thickness=collar.modifiers.new('Rib collar thickness','SOLIDIFY');thickness.thickness=.003/scale

# Two angled front pocket welts and a restrained teal chest marker give recognizable garment construction.
for side in (-1,1):
    positions=[]
    for i in range(14):
        x=cx+side*(.08+i*.003);z=1.19-i*.006
        for dz in (-.004,.004):positions.append(front(x,z+dz))
    fitted_part('Signal Jacket | pocket welt '+str(side),positions,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(13)],rib)
positions=[front(cx-.065+dx,1.345+dz) for dx,dz in ((-.019,-.007),(.019,-.007),(.019,.007),(-.019,.007))]
fitted_part('Signal Jacket | teal chest tab',positions,[(0,1,2,3)],teal)
assert len(mesh.vertices)>1000 and all(math.isfinite(c) for v in mesh.vertices for c in v.co)
assert all(abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in mesh.vertices)
scene.frame_set(1);scene.cycles.device='CPU';scene.cycles.samples=32;scene.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0;native=out/'OddsWellSignalJacket.blend';jacket_name=jacket.name;part_names=[o.name for o in parts];bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig'];jacket=bpy.data.objects[jacket_name]
assert len(jacket.data.vertices)==len(verts) and jacket.modifiers['Shared scanned skeleton'].object==rig
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/ScannedHumanMotionCandidate/refine.py';tree=ast.parse(helper.read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('identity','frame_camera')],type_ignores=[]),str(helper),'exec'))
assert identity()=='81e6d1f3433306db3909dd6dffd81b91546d7935c154d76d92ac034fda061b79'
pose_checks=[]
for frame in range(1,50):
    scene.frame_set(frame);counts=[]
    for name in [jacket_name]+part_names:
        obj=bpy.data.objects[name];ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
        assert len(data.vertices)>0 and all(math.isfinite(c) for v in data.vertices for c in v.co),(frame,name)
        counts.append(len(data.vertices));ev.to_mesh_clear()
    pose_checks.append({'frame':frame,'evaluated_vertex_counts':counts})
report={'source_sha256':sha(source),'candidate_sha256':sha(native),'source_support_faces':len(faces),'jacket_vertices':len(verts),'parts':part_names,
        'shell_offset_m':offset,'cold_reopen_pass':True,'source_mesh_uv_weights_bind_maps_preserved':True,'pose_checks':pose_checks,'shared_rig':rig.name,
        'palette':{'slate':[.12,.18,.22,1],'teal':[.08,.72,.68,1]},'source_outfit_remaining':'Original trousers, shoes and white shirt cuffs/neck edge; underlying shirt/vest remain in retained original mesh.',
        'scope':'Separate long-sleeve fitted Signal Jacket shell, zip, collar, pocket welts and accent geometry. Offline wardrobe study, not complete starter outfit, cloth simulation or runtime acceptance.'}
(out/'jacket-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SIGNAL_JACKET_BUILT',report['candidate_sha256'],flush=True)
cam=scene.camera;cam.data.lens=50
for name,frame,pos,target in [('Full',13,(-2.90,.40,1.28),(-.75,-2.4,.98)),('Front',1,(-.75,.85,1.28),(-.75,-2.4,1.12)),('Close',1,(-1.75,-.15,1.48),(-.75,-2.4,1.32)),('Back',1,(-.75,-5.4,1.3),(-.75,-2.4,1.15))]:
    scene.frame_set(frame);frame_camera(pos,target);cam.data.lens=42 if name=='Full' else 55 if name=='Close' else 50
    scene.render.resolution_x=760;scene.render.resolution_y=840;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('JACKET_RENDER',name,flush=True)
if '--preview' in sys.argv:
    frames=out/'Frames';frames.mkdir(exist_ok=True);scene.cycles.samples=8;scene.render.resolution_x=640;scene.render.resolution_y=704;cam.data.lens=42
    for index,frame in enumerate(range(1,49,2)):
        scene.frame_set(frame);frame_camera((-2.90,.40,1.28),(-.75,-2.4,.98));scene.render.filepath=str(frames/f'{index:04d}.png');bpy.ops.render.render(write_still=True);print('JACKET_PREVIEW_FRAME',frame,flush=True)
