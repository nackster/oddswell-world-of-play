import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(out/'SeatFlow.blend'));pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];uv=pants.data.uv_layers['Four cut cotton panels'];rear={v.index:[] for v in pants.data.vertices}
for p in pants.data.polygons:
    for i in p.loop_indices:rear[pants.data.loops[i].vertex_index].append(float(uv.data[i].uv.y>.5))
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
group=pants.vertex_groups.get('Posterior cotton finite bend radius') or pants.vertex_groups.new(name='Posterior cotton finite bend radius');count=0
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;weight=sum(rear[v.index])/len(rear[v.index])*smooth((p.z-.690)/.060)*(1-smooth((p.z-.860)/.045))*smooth((abs(p.x+.75)-.020)/.040)
    if weight:group.add([v.index],weight,'REPLACE');count+=1
for o in (pants,mid):
    if group.name not in o.vertex_groups:g=o.vertex_groups.new(name=group.name);assert g.index==group.index
    mod=o.modifiers.get('Soft posterior cotton bend radius') or o.modifiers.new('Soft posterior cotton bend radius','SMOOTH');mod.factor=.55;mod.iterations=40;mod.vertex_group=group.name;current=list(o.modifiers).index(mod);target=next(i for i,m in enumerate(o.modifiers) if m.type=='SUBSURF');o.modifiers.move(current,target-int(current<target))
bpy.context.scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'SeatFlow.blend'),compress=True)
with (out/'SeatFlow.blend').open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((out/'build-report.json').read_text());r['candidate_sha256']=digest;r['rear_softening']={'group':group.name,'controls':count,'factor':.55,'iterations':40,'placement':'After authored folds and before subdivision on both visible shorts and registered cloth midsurface','method':'Graded posterior cut-panel selection from lower seat to upper hips, fading at the waist/hem and central saddle. Round the tight cloth curvature beneath the sewn rear patches.'};(out/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print('REAR_COTTON_SOFTENED',digest,flush=True)
