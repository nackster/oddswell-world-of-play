"""An inset arena entrance and visible native front concourse."""
import bpy,ast,json,math,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice';source=art/'LayeredPlantingCandidate/LayeredPlanting.blend';expected='e2559843759bcf76db05c0e97caf790e1f012d5ccfe9cb01db2f5344811a8f94'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(7);original=set(bpy.data.objects)
stone=bpy.data.materials['OW | honed warm limestone'];wood=bpy.data.materials['OW | oiled oak'];wood_along_y=bpy.data.materials['OW | oak grain along shelf'];dark=bpy.data.materials['OW | graphite anodized frames'];teal=bpy.data.materials['OW | restrained signal teal'];plaster=bpy.data.materials['OW | mineral ivory plaster'];bark=stone
parsed=ast.parse((art/'build_scene.py').read_text());exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in ('mesh','box','tube','branch')],type_ignores=[]),str(art/'build_scene.py'),'exec'))
glass=bpy.data.materials['OW | blue arena curtain wall'].copy();glass.name='Arrival | clear blue laminated glazing';n=glass.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.70,.81,.85,1);n.inputs['Metallic'].default_value=0;n.inputs['Transmission Weight'].default_value=1;n.inputs['Roughness'].default_value=.075;n.inputs['IOR'].default_value=1.45
interior=bpy.data.materials.new('Arrival | warm gray concourse plaster');interior.use_nodes=True;n=interior.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.26,.25,.215,1);n.inputs['Roughness'].default_value=.84
noise=interior.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;relief=interior.node_tree.nodes.new('ShaderNodeBump');relief.inputs['Strength'].default_value=.16;relief.inputs['Distance'].default_value=.0004;interior.node_tree.links.new(noise.outputs['Fac'],relief.inputs['Height']);interior.node_tree.links.new(relief.outputs['Normal'],n.inputs['Normal'])
diffuser=bpy.data.materials.new('Arrival | small warm LED diffuser');diffuser.use_nodes=True;n=diffuser.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.7,.62,.48,1);n.inputs['Emission Color'].default_value=(1,.83,.64,1);n.inputs['Emission Strength'].default_value=3
hidden=[];panel_records=[]
def hide(o):
    hidden.append({'name':o.name,'old_hide_render':o.hide_render});o.hide_render=True;o.hide_set(True)
def front(o):return sum((o.matrix_world@Vector(p)).y for p in o.bound_box)/8<75
for o in list(scene.objects):
    if o.name.startswith('Arena | curtain wall panel') and front(o):
        points=[o.matrix_world@v.co for v in o.data.vertices];hide(o);cut=all(abs(p.x-3)<3.5 for p in points[:2])
        if cut:
            for j in (0,1):points[j]=points[j].lerp(points[3-j],(4.96-1.62)/(9.9-1.62))
        new=mesh('Arrival | front glazed bay',points,[(0,1,2,3)],glass);m=new.modifiers.new('Six millimeter glazing','SOLIDIFY');m.thickness=.006;m.offset=0
        panel_records.append({'source':o.name,'new':new.name,'entry_cut':cut})
    elif o.name.startswith('Arena | curtain wall mullion') and front(o):
        points=[o.matrix_world@Vector(p.co[:3]) for p in o.data.splines[0].points]
        if abs(points[0].x-3)<3.5:
            hide(o);a,b=points[0],points[-1];a=a.lerp(b,(4.96-a.z)/(b.z-a.z));tube('Arrival | upper mullion above canopy',[a,b],.022,dark)
for name in ('Arena | limestone angled column.018','Arena | horizontal ring','Arena | signal course'):hide(bpy.data.objects[name])
for o in list(scene.objects):
    if o.name.startswith('Arena | interior concourse edge'):hide(o)
# Carry the center roof support onto the new entrance beam.
bark=stone
branch('Arrival | upper center stone support',Vector((3,65.87,4.96)),Vector((3,65.32,9.90)),.235,.246,stone)
for name,rx,ry,z,radius,mat in [('limestone base',13.2,8.8,1.80,.20,stone),('teal course',13.376,8.976,2.16,.09,teal)]:
    # An open front arc retains the original band around the sides and rear.
    gap=math.asin(3.5/rx);start=-math.pi/2+gap;end=3*math.pi/2-gap
    tube('Arrival | open '+name,[(3+rx*math.cos(start+(end-start)*j/160),75+ry*math.sin(start+(end-start)*j/160),z) for j in range(161)],radius,mat)

def arc(rx,ry,z,segments=64):return [Vector((3+rx*math.cos(math.radians(-155+130*j/segments)),75+ry*math.sin(math.radians(-155+130*j/segments)),z)) for j in range(segments+1)]
for level,z in enumerate((1.65,4.88,7.58)):
    f=(z-1.62)/8.28;outer=arc(13.2+1.76*f-.025,8.8+.88*f-.025,z);inner=arc(11.25,6.40,z);verts=outer+inner;count=len(outer);faces=[(j,j+1,count+j+1,count+j) for j in range(count-1)]
    o=mesh('Arrival | curved concourse floor '+str(level),verts,faces,stone);mod=o.modifiers.new('Native concourse slab','SOLIDIFY');mod.thickness=.16;mod.offset=-1
    if level:
        rail=arc(11.28,6.43,z+1.04);tube('Arrival | inner concourse handrail',rail,.024,dark)
        for j in range(0,len(rail),2):tube('Arrival | inner rail baluster',[rail[j]-Vector((0,0,1.04)),rail[j]],.010,dark)
        # Visible inside edge near the glazing defines each occupied level.
        edge=arc(13.2+1.76*f-.22,8.8+.88*f-.22,z+1.0);tube('Arrival | front concourse handrail',edge,.022,dark)
        for j in range(0,len(edge),2):tube('Arrival | front rail baluster',[edge[j]-Vector((0,0,1.0)),edge[j]],.010,dark)
# A curved inner wall creates true concourse depth behind the glass.
a=arc(11.1,6.23,1.65);b=arc(11.1,6.23,9.46);verts=a+b;faces=[];passage=[]
for j in range(len(a)-1):
    if abs((a[j].x+a[j+1].x)/2-3)<1.83:
        passage.append(j);n=len(verts);verts.extend((Vector((a[j].x,a[j].y,4.10)),Vector((a[j+1].x,a[j+1].y,4.10))));faces.append((n,n+1,len(a)+j+1,len(a)+j))
    else:faces.append((j,j+1,len(a)+j+1,len(a)+j))
o=mesh('Arrival | curved concourse back wall',verts,faces,interior);m=o.modifiers.new('Concourse wall thickness','SOLIDIFY');m.thickness=.10
box('Arrival | central passage floor',(3,72.4,1.57),(3.60,7.8,.16),stone,.008)
for x in (1.10,4.90):box('Arrival | central passage side wall',(x,72.4,2.9),(.16,7.8,2.5),interior,.008)
box('Arrival | central passage ceiling',(3,72.4,4.16),(3.96,7.8,.12),interior,.008)
box('Arrival | distant passage wall',(3,76.35,2.9),(3.80,.12,2.5),dark,.005)
for x in (-5.5,-1.4,7.4,11.5):
    y=75-6.4*math.sqrt(max(0,1-((x-3)/11.25)**2))
    box('Arrival | interior stone pier',(x,y-.18,5.51),(.26,.32,7.72),stone,.015)

floor=1.647
box('Arrival | entrance canopy',(3,65.82,4.72),(7.9,1.72,.46),stone,.025)
box('Arrival | canopy graphite soffit',(3,65.82,4.474),(7.52,1.52,.026),dark,.004)
for cx in (.8,3,5.2):
    for side in (-1,1):
        x=cx+side*.514;o=box('Arrival | inset glass door',(x,66.62,floor+1.40),(1.00,.012,2.79),glass)
        for xx in (x-.5,x+.5):box('Arrival | graphite door stile',(xx,66.6,floor+1.4),(.034,.046,2.8),dark,.003)
        for z in (floor+.018,floor+2.80):box('Arrival | graphite door rail',(x,66.6,z),(1.03,.046,.036),dark,.003)
        tube('Arrival | brushed door pull',[(cx+side*.09,66.535,floor+.95),(cx+side*.09,66.535,floor+1.55)],.011,dark)
    box('Arrival | inset door transom',(cx,66.62,4.457),(2.08,.015,.070),glass)
box('Arrival | entry threshold',(3,66.52,floor+.012),(6.54,.26,.024),stone,.004)
for body,size,z in [('ODDSWELL ARENA',.44,4.61),('SUNDALE  /  MAIN ENTRANCE',.135,4.50)]:
    d=bpy.data.curves.new('Arrival | physical arena lettering','FONT');d.body=body;d.align_x='CENTER';d.size=size;d.extrude=.001;d.materials.append(dark);o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(3,64.948,z);o.rotation_euler=(math.pi/2,0,0)
# Actual interior lights reveal slabs/rails through the physical glazing.
for z in (4.62,7.32,9.20):
    for x in (-6.4,-1.7,3,7.7,12.4):
        y=75-7.5*math.sqrt(max(0,1-((x-3)/13.4)**2))
        d=bpy.data.lights.new('Arrival | warm concourse downlight','AREA');d.energy=90;d.shape='DISK';d.size=.85;d.color=(1,.83,.64);o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(x,y,z);o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
        # Native fixture housing is visible even where daylight dominates.
        box('Arrival | recessed light trim',(x,y,z+.045),(.22,.22,.028),dark,.01)
        box('Arrival | physical LED diffuser',(x,y,z+.028),(.18,.18,.009),diffuser,.008)
collection=bpy.data.collections.new('OddsWell | arena arrival refinement');scene.collection.children.link(collection);added=[o for o in bpy.data.objects if o not in original]
for o in added:
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o)
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(7);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ArenaArrival.blend'),compress=True)
with (out/'ArenaArrival.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'candidate_sha256':sha,'source_sha256':expected,'changed_visibility':hidden,'added_objects':[o.name for o in added],'front_glazed_bays':panel_records,'entry_door_leaf_count':6,'entry_floor_z':floor,'back_wall_passage_segments':passage,'new_bitmap_assets':0,'scope':'Native front arena glazing, concourse depths/floors/rails/back wall with central passage, inset doors and signed canopy. Original replaced arena elements retained hidden. Original human, walk, planting, retail, court, roof silhouette and approach remain unchanged. Offline visual study, no runtime or physical entry acceptance.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('ARRIVAL_BUILT',len(added),len(hidden),len(panel_records),sha,flush=True)
