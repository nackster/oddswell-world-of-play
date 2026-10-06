"""Native hip cloth relaxation and stable sewn shorts attachments."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/HandArticulationCandidate/HandMotion.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='dc0b0884a33e515d982cccc89c315de5f693fd170220028d786b43af8ae90750'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
rig=bpy.data.objects['Walk study | native anatomical controls'];pants=bpy.data.objects['Character | shorts leg continuous tailoring']
uv=pants.data.uv_layers['Four cut cotton panels'];sides={i:[] for i in range(len(pants.data.vertices))}
for poly in pants.data.polygons:
    side=0. if sum(uv.data[i].uv.x for i in poly.loop_indices)/len(poly.loop_indices)<.5 else 1.
    for i in poly.vertices:sides[i].append(side)
leg_names=[side+'.'+part for side in ('neg','pos') for part in ('thigh','shin')]
weight_changes=0
for v in pants.data.vertices:
    old={g.name:max((w.weight for w in v.groups if w.group==g.index),default=0.) for g in pants.vertex_groups if g.name in leg_names}
    pos=sum(sides[v.index])/len(sides[v.index])
    new={side+'.'+part:sum(old.get(s+'.'+part,0.) for s in ('neg','pos'))*(pos if side=='pos' else 1-pos) for side in ('neg','pos') for part in ('thigh','shin')}
    if max(abs(new[n]-old.get(n,0.)) for n in leg_names)<1e-7:continue
    weight_changes+=1
    for name,w in new.items():
        g=pants.vertex_groups[name]
        if w>1e-7:g.add([v.index],w,'REPLACE')
        else:g.remove([v.index])
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
group=pants.vertex_groups.new(name='Hip seat fabric relaxation')
for v in pants.data.vertices:
    p=pants.matrix_world@v.co
    weight=smooth((p.z-.69)/.08)*(1-smooth((p.z-.87)/.035))
    # Leave the deepest inseam and top/leg opening anchors intact.
    weight*=smooth((abs(p.x+.75)-.025)/.04)
    if weight:group.add([v.index],weight,'REPLACE')
mod=pants.modifiers.new('Rounded hip seat cloth transitions','SMOOTH');mod.factor=.4;mod.iterations=12;mod.vertex_group=group.name
pants.modifiers.move(len(pants.modifiers)-1,1)
legs=bpy.data.objects['Character | anatomical legs'];skin=legs.copy();skin.data=legs.data.copy();skin.name='Hip study | actual leg skin clearance';scene.collection.objects.link(skin)
bm=bmesh.new();bm.from_mesh(skin.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.z)>.85],context='FACES_ONLY');bm.to_mesh(skin.data);bm.free()
skin.hide_render=True;skin.hide_set(True)
clearance=pants.vertex_groups.new(name='Lower shorts leg skin clearance')
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;w=smooth((p.z-.575)/.025)*(1-smooth((p.z-.70)/.035))
    if w:clearance.add([v.index],w,'REPLACE')
outside=pants.modifiers.new('Outside real leg skin','SHRINKWRAP');outside.target=skin;outside.wrap_method='NEAREST_SURFACEPOINT';outside.wrap_mode='OUTSIDE';outside.offset=.012;outside.vertex_group=clearance.name
pants.modifiers.move(len(pants.modifiers)-1,2)
report={'source_sha256':'dc0b0884a33e515d982cccc89c315de5f693fd170220028d786b43af8ae90750','panel_leg_weight_controls_corrected':weight_changes,'hip_relaxation':{'factor':.4,'iterations':12,'group':group.name},'leg_skin_constraint':{'target':skin.name,'offset_m':outside.offset,'scope':'Native duplicate of retained anatomical leg skin with near-horizontal artificial closure faces omitted; lower garment group only'},'bindings':{}}
# Keep every original control/UV/key. Replace fragile cage bindings with weights
# from the actual garment, then project the small details to its moving surface.
followers=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o!=pants and (any(m.type=='SURFACE_DEFORM' and m.target and m.target.name=='Walk cage | shorts' for m in o.modifiers) or o.name.startswith(('Walk surface | Character | inset back pocket stitch','Walk surface | Character | pocket mouth topstitch')))]
for obj in followers:
    target=bpy.data.objects['Character | tailored slate jacket'] if obj.name.startswith('Walk surface | Character | front welt pocket') else pants
    world=obj.matrix_world.copy()
    for m in list(obj.modifiers):
        if m.type in {'SURFACE_DEFORM','ARMATURE'}:obj.modifiers.remove(m)
    for bone in rig.data.bones:
        if bone.name not in obj.vertex_groups:obj.vertex_groups.new(name=bone.name)
    transfer=obj.modifiers.new('Actual garment anatomical weights','DATA_TRANSFER');transfer.object=target;transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'}
    transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME';obj.modifiers.move(len(obj.modifiers)-1,0)
    bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();names={g.index:g.name for g in obj.vertex_groups}
    records=[{names[g.group]:g.weight for g in v.groups if names[g.group] in rig.data.bones} for v in mesh.vertices[:len(obj.data.vertices)]];ev.to_mesh_clear()
    assert len(records)==len(obj.data.vertices)
    hem='hem' in obj.name.lower()
    if hem:
        graph={i:set() for i in range(len(records))}
        for e in obj.data.edges:
            a,b=e.vertices;graph[a].add(b);graph[b].add(a)
        pending=set(graph)
        while pending:
            queue=[pending.pop()];component=set(queue)
            while queue:
                for i in graph[queue.pop()]:
                    if i in pending:pending.remove(i);component.add(i);queue.append(i)
            center=sum((world@obj.data.vertices[i].co for i in component),Vector())/len(component)
            side='neg' if center.x<-.75 else 'pos'
            for i in component:
                weights=records[i]
                records[i]={side+'.'+part:sum(weights.get(s+'.'+part,0.) for s in ('neg','pos')) for part in ('thigh','shin')}
                for name,w in weights.items():
                    if name not in leg_names:records[i][name]=w
    ids=list(range(len(records)))
    for g in obj.vertex_groups:
        if g.name in rig.data.bones:g.remove(ids)
    for i,weights in enumerate(records):
        total=sum(weights.values());assert total>.99
        for name,w in weights.items():
            if w>1e-7:obj.vertex_groups[name].add([i],w/total,'REPLACE')
    obj.modifiers.remove(transfer);obj.parent=rig;obj.parent_type='OBJECT';obj.matrix_world=world
    arm=obj.modifiers.new('Sewn shorts shared armature','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True;obj.modifiers.move(len(obj.modifiers)-1,0)
    contact=obj.modifiers.new('Sewn garment cloth contact','SHRINKWRAP');contact.target=target;contact.wrap_method='NEAREST_SURFACEPOINT';contact.wrap_mode='ABOVE_SURFACE'
    pocket=obj.name.startswith('Character | sewn cotton back pocket')
    contact.offset=.0009 if pocket else .00045
    obj.modifiers.move(len(obj.modifiers)-1,1)
    if pocket:
        # A sewn patch should follow the seat, with a fine fabric edge.
        for m in obj.modifiers:
            if m.type=='SOLIDIFY':m.thickness=.00045;m.offset=1
    report['bindings'][obj.name]={'controls':len(records),'target':target.name,'cloth_offset_m':contact.offset,'method':'Connected hem components follow their own native leg weights and actual moving garment projection' if hem else 'Normalized native garment armature weights and actual moving garment projection'}
assert len(followers)>=15,len(followers)
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'HipSeat.blend'),compress=True)
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
print('HIP_SEAT_SAVED',len(followers),flush=True)
