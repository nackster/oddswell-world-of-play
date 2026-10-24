"""Save the licensed character as a compact local editable Blender asset."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric'
bpy.ops.wm.open_mainfile(filepath=str(out/'ScannedHumanWalk.blend'))
actor_scene=bpy.data.scenes.new('OddsWell scanned human study');actor_scene.frame_start=1;actor_scene.frame_end=49;actor_scene.render.fps=24;actor_scene.render.engine='CYCLES';actor_scene.cycles.device='CPU';actor_scene.cycles.samples=32
for name in ('Scan character | Eric mesh','Scan character | Eric rig','Scan character | placement'):actor_scene.collection.objects.link(bpy.data.objects[name])
world=bpy.data.worlds.new('Character studio world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.15,.15,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4;actor_scene.world=world
d=bpy.data.cameras.new('Character studio camera');cam=bpy.data.objects.new(d.name,d);actor_scene.collection.objects.link(cam);cam.location=(-2.9,.4,1.28);cam.rotation_euler=(Vector((-.75,-2.4,.98))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=50;actor_scene.camera=cam
for name,pos,power,size in [('Character key',(-3,0,3.5),450,3),('Character fill',(2,-1,2.3),180,2)]:
    light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;o=bpy.data.objects.new(name,light);actor_scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((-.75,-2.4,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.context.window.scene=actor_scene;actor_scene.frame_set(1);path=out/'OddsWellHuman.blend';bpy.data.libraries.write(str(path),{actor_scene},path_remap='RELATIVE',fake_user=True,compress=True)
bpy.ops.wm.open_mainfile(filepath=str(path));assert len(bpy.data.scenes)==1;mesh=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig'];assert len(mesh.data.vertices)==10353 and len(rig.data.bones)==88 and len([i for i in bpy.data.images if i.packed_file])==3
assert rig.animation_data.action and bpy.data.objects['Scan character | placement'].animation_data.action
# Convert the library-only file into a normal directly openable Blender document.
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(path));assert len(bpy.context.scene.objects)==6 and bpy.context.scene.camera is not None;mesh=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'standalone_sha256':sha,'bytes':path.stat().st_size,'objects':len(bpy.context.scene.objects),'vertices':len(mesh.data.vertices),'bones':len(rig.data.bones),'packed_maps':3,'animation_keys':49,'scope':'Local editable vendor-based human with packed materials, original skinning and offline walk study. Source outfit, no runtime certification.'}
(out/'standalone-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCAN_STANDALONE_PASS',report,flush=True)
