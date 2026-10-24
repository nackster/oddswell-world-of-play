"""Fit editable inner cotton panels to the actual anatomical rest skin."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/CottonTailoringCandidate/CottonDetail.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='9ebfbc9007d4752a568c094d988f36ee9c1fbe342f27f683d7d29d5aa24b8d6f'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];legs=bpy.data.objects['Character | anatomical legs'];rig=bpy.data.objects['Walk study | native anatomical controls']
# Keep the hidden historical walk cage's mesh, shape keys and weights intact.
pants.data=pants.data.copy();mid.data=pants.data
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
uv=pants.data.uv_layers['Four cut cotton panels'];samples={v.index:[] for v in pants.data.vertices};sides={v.index:[] for v in pants.data.vertices}
for poly in pants.data.polygons:
    sign=-1 if sum(uv.data[i].uv.x for i in poly.loop_indices)/len(poly.loop_indices)<.5 else 1
    for i in poly.loop_indices:
        j=pants.data.loops[i].vertex_index;sides[j].append(sign);samples[j].append(tuple(uv.data[i].uv))
# Inspect the exact closed skin in its native armature rest position.
flags=[(m,m.show_viewport) for m in legs.modifiers if m.type=='ARMATURE'];levels=[(m,m.levels) for m in legs.modifiers if m.type=='SUBSURF']
for m,_ in flags:m.show_viewport=False
for m,_ in levels:m.levels=m.render_levels
deps=bpy.context.evaluated_depsgraph_get();ev=legs.evaluated_get(deps);mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps);mesh.calc_loop_triangles();points=[ev.matrix_world@v.co for v in mesh.vertices]
triangles={s:[] for s in (-1,1)}
for tri in mesh.loop_triangles:
    center=sum((points[j] for j in tri.vertices),Vector())/3;triangles[-1 if center.x<-.75 else 1].append(tuple(tri.vertices))
trees={s:BVHTree.FromPolygons(points,fs,all_triangles=True) for s,fs in triangles.items()}
key=pants.shape_key_add(name='Anatomical inner thigh cotton ease',from_mix=False);key.value=1;inside_weights={};maximum=0.;changed=0
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;inside=1-smooth((abs(p.x+.75)-.025)/.065);vertical=1-smooth((p.z-.645)/.105);side=sum(sides[v.index])/len(sides[v.index]);inside_weights[v.index]=inside
    if abs(side)<.9 or inside*vertical<1e-6:continue
    sign=-1 if side<0 else 1;hit,normal,idx,distance=trees[sign].find_nearest(p);goal=hit+normal*.0045;delta=(goal-p)*(inside*vertical)
    key.data[v.index].co+=pants.matrix_world.inverted().to_3x3()@delta;maximum=max(maximum,delta.length);changed+=1
ev.to_mesh_clear()
for m,flag in flags:m.show_viewport=flag
for m,level in levels:m.levels=level
leg_names=[s+'.'+part for s in ('neg','pos') for part in ('thigh','shin')];weight_changes=0
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;hold=.94*smooth((p.z-.665)/.105)*(1-smooth((abs(p.x+.75)-.022)/.073));values={g.name:next((w.weight for w in v.groups if w.group==g.index),0.) for g in pants.vertex_groups if g.name in rig.data.bones};total=sum(values.get(n,0.) for n in leg_names)
    if total*hold<1e-7:continue
    for name in leg_names:
        w=values.get(name,0.)*(1-hold)
        if w:pants.vertex_groups[name].add([v.index],w,'REPLACE')
    pants.vertex_groups['pelvis'].add([v.index],values.get('pelvis',0.)+total*hold,'REPLACE');weight_changes+=1
medial=pants.vertex_groups.new(name='Medial thigh cotton skin fit');clearance=pants.vertex_groups['Lower shorts leg skin clearance']
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;lower=1-smooth((p.z-.70)/.035);inside=inside_weights[v.index];clearance.add([v.index],lower*(1-inside),'REPLACE');medial.add([v.index],lower*inside,'REPLACE')
for obj in (pants,mid):
    if medial.name not in obj.vertex_groups:
        g=obj.vertex_groups.new(name=medial.name);assert g.index==medial.index
    mod=obj.modifiers.new('Medial cloth actual leg skin clearance','SHRINKWRAP');mod.target=bpy.data.objects['Hip study | actual leg skin clearance'];mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='OUTSIDE';mod.offset=.0045;mod.vertex_group=medial.name;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.name=='Outside real leg skin')+1)
group=pants.vertex_groups.new(name='Outer thigh cotton transition fillet')
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;weights=[]
    for u,t in samples[v.index]:
        side=0 if u<.5 else 1;across=(u-(.02 if side==0 else .50))/.48;outer=1-across;weights.append(smooth((outer-.52)/.27)*smooth((p.z-.64)/.045)*(1-smooth((p.z-.80)/.06)))
    w=sum(weights)/len(weights)
    if w:group.add([v.index],w,'REPLACE')
for obj in (pants,mid):
    if group.name not in obj.vertex_groups:
        g=obj.vertex_groups.new(name=group.name);assert g.index==group.index
    mod=obj.modifiers.new('Soft outer thigh cotton transition','SMOOTH');mod.factor=.45;mod.iterations=20;mod.vertex_group=group.name;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.type=='NODES' and m.name=='Cotton directional compression and tension folds'))
    solid=next((m for m in obj.modifiers if m.type=='SOLIDIFY'),None)
    if solid:solid.solidify_mode='EXTRUDE';solid.use_even_offset=False;solid.thickness_clamp=0
fold=pants.vertex_groups.new(name='Cotton inner fold bend radius')
for v in pants.data.vertices:
    values=[]
    for u,t in samples[v.index]:
        local_u=u if u<.5 else u-.48
        local_v=t if t<.5 else t-.48
        values.append((1-smooth((abs(local_u-.37)-.012)/.025))*(1-smooth((abs(local_v-.177)-.015)/.035)))
    w=sum(values)/len(values)
    if w:fold.add([v.index],w,'REPLACE')
for obj in (pants,mid):
    if fold.name not in obj.vertex_groups:
        g=obj.vertex_groups.new(name=fold.name);assert g.index==fold.index
    mod=obj.modifiers.new('Cotton inner fold finite bend radius','SMOOTH');mod.factor=.5;mod.iterations=4;mod.vertex_group=fold.name;obj.modifiers.move(len(obj.modifiers)-1,next(j for j,m in enumerate(obj.modifiers) if m.type=='SUBSURF'))
report={'source_sha256':'9ebfbc9007d4752a568c094d988f36ee9c1fbe342f27f683d7d29d5aa24b8d6f','inner_panel_key':{'name':key.name,'controls_changed':changed,'maximum_control_change_m':maximum,'method':'One editable fit against actual closed subdivided skin in armature rest position, 4.5 mm stand-off, stable cut-panel sides and graded medial/lower panel selection. Shared saddle controls remain joined.'},'saddle_weight_controls_changed':weight_changes,'saddle_support':'Grade opposing thigh/shin influence into pelvis across upper central saddle, preserving total native bone influence.','lower_hem_clearance':'Remove unsupported lower fade. Medial stand-off 4.5 mm; retained lateral stand-off 12 mm. No post-subdivision projection trial retained.','outer_transition':{'factor':.45,'iterations':20,'scope':'Both outer panels, graded around the existing sharp upper-thigh crease.'},'inner_fold_bend_radius':{'factor':.5,'iterations':4,'scope':'Graded cotton atlas region around the diagnosed inner-layer fold; symmetric front/rear and left/right support.'},'shell':'Native normal extrusion, nominal 1 mm; inherited non-manifold constraints are not retained.'}
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ThighDrape.blend'),compress=True);(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('THIGH_DRAPE_SAVED',flush=True)
