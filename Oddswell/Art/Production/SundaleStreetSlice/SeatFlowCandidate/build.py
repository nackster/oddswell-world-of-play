"""Reduce exaggerated leg pull through the posterior cotton seat."""
import bpy,json,hashlib,math
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/ChestContourCandidate/ChestContour.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='2cfb15e7fe5f96feff0a48e1b744a254e22ba24bbe3e330ca37c201862785cdb';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1);pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];pants.data=pants.data.copy();mid.data=pants.data
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
uv=pants.data.uv_layers['Four cut cotton panels'];rear={v.index:[] for v in pants.data.vertices}
for poly in pants.data.polygons:
    for i in poly.loop_indices:rear[pants.data.loops[i].vertex_index].append(float(uv.data[i].uv.y>.5))
legs=[s+'.'+p for s in ('neg','pos') for p in ('thigh','shin')];groups={n:pants.vertex_groups[n] for n in legs+['pelvis']};changes=[]
for v in pants.data.vertices:
    p=pants.matrix_world@v.co;posterior=sum(rear[v.index])/len(rear[v.index]);mask=.90*smooth((p.z-.665)/.105)*posterior*smooth((abs(p.x+.75)-.025)/.040)*(1-smooth((abs(p.x+.75)-.18)/.065))
    weights={n:max((w.weight for w in v.groups if w.group==g.index),default=0.) for n,g in groups.items()};transfer=sum(weights[n] for n in legs)*mask
    if transfer<1e-7:continue
    for n in legs:
        value=weights[n]*(1-mask)
        if value:groups[n].add([v.index],value,'REPLACE')
    groups['pelvis'].add([v.index],weights['pelvis']+transfer,'REPLACE');changes.append({'id':v.index,'posterior_fraction':posterior,'mask':mask,'leg_influence_to_pelvis':transfer})
report={'source_sha256':expected,'method':'Graded posterior cut-panel selection. Shift a fraction of existing thigh/shin influence into pelvis across the upper seat, fading through lower thigh and medial/outer seams. Total native bone influence and existing cloth/skin constraints retained. No physical cloth simulation.','weight_controls_changed':len(changes),'maximum_leg_influence_to_pelvis':max(r['leg_influence_to_pelvis'] for r in changes),'controls':changes}
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'SeatFlow.blend'),compress=True);report['candidate_sha256']=sha(out/'SeatFlow.blend');(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SEAT_FLOW_BUILT',len(changes),report['candidate_sha256'],flush=True)
