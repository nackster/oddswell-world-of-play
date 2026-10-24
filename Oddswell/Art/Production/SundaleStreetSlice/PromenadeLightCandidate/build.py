"""Open the arrival sightline with complete scene groups and restrained bounce."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/ArenaArrivalCandidate/ArenaArrival.blend';expected='4be22d54515ef82276331c3286147e5f77dad9ddc2491d4e29d39eaf720cd524'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(7);moves=[]
def move(o,delta,group):
    assert not o.parent,('Unexpected scene parenting',o.name)
    before=list(o.location);o.location+=delta;moves.append({'name':o.name,'group':group,'old_location':before,'new_location':list(o.location),'delta':list(delta)})
delta=Vector((-6.9,2,0));tree_names=['Tree | mature Sundale broadleaf.007','Tree pit stone surround.007','Tree pit soil.007','Civic | tree pit groundcover.007','Civic | low tree pit foliage.007']
for name in tree_names:move(bpy.data.objects[name],delta,'arrival tree and complete bed')
for o in scene.objects:
    if o.name.startswith('Planting | Tree pit soil.007 '):move(o,delta,'arrival tree and complete bed')
for o in scene.objects:
    if o.name.startswith('Civic light |') and o.type=='MESH':
        center=sum((o.matrix_world@Vector(p) for p in o.bound_box),Vector())/8
        if abs(center.x-1.6)<.18:move(o,Vector((.5,0,0)),'court-edge lamp row')
assert len([r for r in moves if r['group']=='court-edge lamp row'])==27
lights=[];hidden=[];collection=bpy.data.collections.new('OddsWell | promenade light refinement');scene.collection.children.link(collection)
for name,energy in [('Sundale | broad warm bounce',300),('Sundale | reflected courtyard light',950)]:
    original=bpy.data.objects[name];original.hide_render=True;original.hide_set(True);hidden.append({'name':name,'old_hide_render':False});new=original.copy();new.data=original.data.copy();new.name='Promenade | '+name.split(' | ')[1];new.hide_render=False;collection.objects.link(new);new.hide_set(False);new.data.energy=energy
    lights.append({'source':name,'new':new.name,'source_data':original.data.name,'new_data':new.data.name,'old_energy':original.data.energy,'new_energy':energy})
scene.camera=bpy.data.objects['CAM | gameplay street'];scene.frame_set(7);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'PromenadeLight.blend'),compress=True)
with (out/'PromenadeLight.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
report={'candidate_sha256':sha,'source_sha256':expected,'object_moves':moves,'changed_visibility':hidden,'added_objects':[r['new'] for r in lights],'light_copies':lights,'new_bitmap_assets':0,'scope':'Arrival tree and complete soil/stone/understory bed move together, lamp row shifts 0.5 m toward court edge outside blue play surface. Two retained bounce-light copies increase shade illumination modestly. Original control meshes/curves, materials, packed maps, rig, human, walk, court and gameplay camera unchanged.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('PROMENADE_BUILT',len(moves),sha,flush=True)
