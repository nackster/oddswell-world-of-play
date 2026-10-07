"""A deeper native OddsWell apparel shop in the first foreground retail bay."""
import bpy,ast,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';source=art/'ShoulderChestCandidate/ShoulderChest.blend';expected='8b2f0e5634f1198bbdbb5054c961668cb86825764ada8d24355296cbc290de7a';layout_offset=Vector((-1.2,8,0))
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);before_objects=set(bpy.data.objects);original_names={o.name for o in scene.objects}
wood=bpy.data.materials['OW | oiled oak'];wood_along_y=bpy.data.materials['OW | oak grain along shelf'];plaster=bpy.data.materials['OW | mineral ivory plaster'];dark=bpy.data.materials['OW | graphite anodized frames'];teal=bpy.data.materials['OW | restrained signal teal']
helper=art/'build_scene.py';parsed=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('mesh','box','tube')],type_ignores=[]),str(helper),'exec'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU';scene.cycles.samples=24;scene.render.use_persistent_data=True;scene.render.resolution_percentage=100
data=bpy.data.cameras.new('Retail study | matched camera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
def render(label,pos,target,lens,w=1280,h=900):
    scene.camera=camera;camera.location=Vector(pos)+layout_offset;camera.rotation_euler=(Vector(target)+layout_offset-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True);print('RETAIL_RENDER',label,flush=True)
render('Before_Storefront',(-2.8,-6.9,1.65),(-7.1,-1.0,1.55),42)
render('Before_Interior',(-4.3,.9625,1.65),(-9.2,.9625,1.55),28)
hidden=[]
def center(obj):return sum((obj.matrix_world@Vector(p) for p in obj.bound_box),Vector())/8
for obj in scene.objects:
    if obj.name not in original_names or obj.type not in ('MESH','CURVE'):continue
    p=center(obj)-layout_offset;replace=False
    if obj.name.startswith('Building | retail rear volume') and -10.1<p.x<-9.6 and abs(p.y+1)<.1:replace=True
    if obj.name.startswith('Shop | recessed interior') and -7.6<p.x<-7.35 and -4.9<p.y<2.9:replace=True
    if obj.name.startswith(('Shop | display goods','Shop | hanging garment','Shop | brass hanger')) and -7.1<p.x<-6.2 and -4.9<p.y<2.9:replace=True
    if replace:hidden.append({'name':obj.name,'center':list(p+layout_offset),'old_hide_render':obj.hide_render});obj.hide_render=True;obj.hide_set(True)
assert sum(r['name'].startswith('Building | retail rear volume') for r in hidden)==1
assert sum(r['name'].startswith('Shop | recessed interior') for r in hidden)==2
box('Retail | deep oak floor',(-8.535,-1,.11),(2.13,7.5,.12),wood,.008)
box('Retail | deep plaster ceiling',(-8.535,-1,3.1),(2.13,7.5,.12),plaster,.008)
box('Retail | ivory back wall',(-9.65,-1,1.66),(.10,7.5,3.0),plaster,.012)
for y in (-4.75,2.75):box('Retail | shop side return',(-7.84,y,1.66),(3.62,.10,3.0),plaster,.012)
box('Retail | oak island cabinet',(-8.50,-1.1,.64),(.92,1.72,.94),wood,.015)
box('Retail | oak island top',(-8.50,-1.1,1.145),(1.06,1.85,.07),wood,.015)
for y in (-1.51,-.69):
    box('Retail | cabinet drawer front',(-8.01,y,.74),(.027,.77,.36),wood,.01)
    tube('Retail | graphite drawer pull',[(-7.977,y-.14,.84),(-7.977,y+.14,.84)],.007,dark)
cloth=bpy.data.materials['Character | offwhite cotton twill'];slate=cloth.copy();slate.name='Retail | slate folded cotton';cream=cloth.copy();cream.name='Retail | cream folded cotton'
for mat,color in ((slate,(.055,.079,.092,1)),(cream,(.54,.48,.36,1))):
    for node in mat.node_tree.nodes:
        if node.type=='MIX_RGB' and node.blend_type=='MULTIPLY':node.inputs['Color1'].default_value=color
def folded(x,y,z,mat):
    obj=box('Retail | folded cotton apparel',(x,y,z+.028),(.31,.43,.056),mat,.016);mod=next(m for m in obj.modifiers if m.type=='BEVEL');mod.segments=4
    tube('Retail | soft folded edge',[(x+.151,y-.185,z+.028),(x+.156,y,z+.026),(x+.151,y+.185,z+.028)],.0012,mat)
    box('Retail | sewn teal size tab',(x+.088,y-.213,z+.039),(.025,.015,.0008),teal,.001)
    tube('Retail | folded cotton collar',[(x-.04+.045*math.cos(j*math.tau/24),y+.075*math.sin(j*math.tau/24),z+.060) for j in range(24)],.0035,mat,closed=True)
for bay_y in (-2.9625,.9625):
    for z in (.5725,1.0725,1.5725):
        for j in range(3):
            for layer in range(2 if z<1.3 else 1):folded(-6.78,bay_y-.72+j*.72,z+layer*.057,slate if (j+layer)%2 else cream)
for y in (-1.65,-.65):
    for layer in range(3):folded(-8.48,y,1.18+layer*.057,slate if layer%2 else cream)
# Reuse the actual modeled outfit as static retail merchandise, without its rig.
coat=bpy.data.objects['Character | tailored slate jacket'];sub=next(m for m in coat.modifiers if m.type=='SUBSURF');old_level=sub.levels;sub.levels=sub.render_levels
part_names=[coat.name,'Character | standing collar','Character | ribbed waistband','Walk surface | Character | front zipper tape']
part_names += [o.name for o in scene.objects if o.name.startswith('Character | ') and 'cuff' in o.name and not o.hide_render]
deps=bpy.context.evaluated_depsgraph_get();parts=[]
for name in dict.fromkeys(part_names):
    obj=bpy.data.objects.get(name)
    if not obj or obj.hide_render or obj.type not in ('MESH','CURVE'):continue
    ev=obj.evaluated_get(deps);d=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);copy=bpy.data.objects.new('Retail temporary | '+name,d);scene.collection.objects.link(copy);copy.matrix_world=obj.matrix_world.copy();parts.append(copy)
sub.levels=old_level;bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();merch=bpy.context.object;merch.name='Retail | hanging OddsWell jacket A';source_origin=Vector((-.70,-2.4,1.21))
for v in merch.data.vertices:v.co=merch.matrix_world@v.co-source_origin
merch.matrix_world=Matrix.Identity(4);merch.rotation_euler.z=-math.pi/2;merch.location=(-6.07,-1.90,2.12)
second=merch.copy();second.data=merch.data;second.name='Retail | hanging OddsWell jacket B';scene.collection.objects.link(second);second.location=(-6.60,1.45,2.13)
for x,y,z in ((-6.10,-1.90,2.385),(-6.63,1.45,2.395)):
    tube('Retail | wooden apparel hanger',[(x,y-.20,z-.02),(x,y,z+.065),(x,y+.20,z-.02)],.009,wood)
    tube('Retail | hanger hook',[(x,y,z+.064),(x,y,z+.12),(x+.015,y,z+.135),(x+.026,y,z+.12)],.003,dark)
for x,y,z in ((-6.085,-1.90,2.520),(-6.615,1.45,2.530)):
    tube('Retail | graphite apparel rail',[(x,y-.65,z),(x,y+.65,z)],.015,dark)
    for dy in (-.53,.53):tube('Retail | ceiling rail dropper',[(x,y+dy,z),(x,y+dy,3.04)],.007,dark)
plate=box('Retail | OddsWell shop plaque',(-5.745,.9625,2.91),(.025,2.08,.23),plaster,.008)
rotation=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_euler()
for name,body,size,y,z in [('wordmark','ODDSWELL',.15,.075,2.872),('descriptor','COURT & EVERYDAY',.034,.085,2.822)]:
    d=bpy.data.curves.new('Retail | '+name,'FONT');d.body=body;d.size=size;d.extrude=.0008;d.materials.append(dark);o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(-5.728,y,z);o.rotation_euler=rotation
for y in (-3.25,.75):
    d=bpy.data.lights.new('Retail | warm interior soft light','AREA');d.energy=140;d.color=(1,.77,.51);d.shape='DISK';d.size=1.1;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(-8.1,y,2.86)
collection=bpy.data.collections.new('OddsWell | foreground retail refinement');scene.collection.children.link(collection)
added=[o for o in bpy.data.objects if o not in before_objects and o!=camera]
for o in added:
    o.location+=layout_offset
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o)
report={'source_sha256':expected,'changed_visibility':hidden,'added_objects':[o.name for o in added],'layout_offset_m':list(layout_offset),'native_room_depth_m':3.65,'former_back_panel_depth_m':1.48,'display_jackets_reuse':'Static evaluated coat/collar/waist/cuff/tape copies from the reviewed native outfit. Original rig and character remain unchanged. Two instances share the baked product mesh; licensed maps retained.','licensed_packed_maps_unchanged':True,'new_bitmap_assets':0,'scope':'First apparel shop visible along the gameplay approach, at facade x=-7.2, y=7. Replace its solid rear volume/back panels and generic goods by deeper native room surfaces, cotton apparel, modeled jacket displays, an oak island and physical OddsWell lettering. Original source objects retained with explicit visibility changes; main character geometry, walk, other architecture, court and planting remain unchanged. No runtime/entry/collision/beta credit.'}
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'RetailDepth.blend'),compress=True)
with (out/'RetailDepth.blend').open('rb') as f:report['candidate_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
render('After_Storefront',(-2.8,-6.9,1.65),(-7.1,-1.0,1.55),42)
render('After_Interior',(-4.3,.9625,1.65),(-9.2,.9625,1.55),28)
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(7);scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/'Gameplay.png');bpy.ops.render.render(write_still=True);print('RETAIL_DEPTH_FINISHED',len(added),len(hidden),flush=True)
