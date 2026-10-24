import bpy,ast,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());art=root/'Oddswell/Art/Production/SundaleStreetSlice'
helper=art/'BodyBalanceCandidate/audit.py';tree=ast.parse(helper.read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('dependencies','surface')],type_ignores=[]),str(helper),'exec'))
report={}
targets=['Character | tailored slate jacket','Character | shorts leg continuous tailoring'];seed=set(targets+['Walk cage | refined jacket surface','Hip study | registered cloth midsurface'])
for label,path in [('SOURCE',art/'UpperHipHandCandidate/UpperDrape.blend'),('CANDIDATE',out/'PosedEase.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));changed=dependencies(seed);names=sorted(n for n in changed-seed if not bpy.data.objects[n].hide_render and bpy.data.objects[n].type in ('MESH','CURVE'));rows=[]
    for name in seed:
        for m in bpy.data.objects[name].modifiers:
            if m.type=='SUBSURF':m.levels=m.render_levels
    for frame in (1,13,35):
        bpy.context.scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();surfaces={n:surface(bpy.data.objects[n],deps) for n in targets};details={}
        for n in names:
            p,f,e,tree=surface(bpy.data.objects[n],deps)
            target=targets[1] if any(word in n.lower() for word in ('short','cotton','pocket','hem','waist')) and 'jacket' not in n.lower() and 'front welt' not in n.lower() else targets[0]
            details[n]={'target':target,'maximum_sampled_gap_m':max(surfaces[target][3].find_nearest(v)[3] for v in p[::4]),'maximum_edge_m':max((p[a]-p[b]).length for a,b in e)}
        rows.append({'frame':frame,'details':details});print('EASE_FOLLOWERS',label,frame,len(names),flush=True)
    report[label]=rows
for prior,row in zip(report['SOURCE'],report['CANDIDATE']):
    assert prior['details'].keys()==row['details'].keys()
    for n,d in row['details'].items():
        old=prior['details'][n]
        assert d['maximum_sampled_gap_m']<old['maximum_sampled_gap_m']+.004,('Sewing gap',row['frame'],n)
        assert d['maximum_edge_m']<old['maximum_edge_m']*1.5+.002,('Sewing edge',row['frame'],n)
for key,path in [('source_sha256',art/'UpperHipHandCandidate/UpperDrape.blend'),('candidate_sha256',out/'PosedEase.blend')]:
    with path.open('rb') as f:report[key]=hashlib.file_digest(f,'sha256').hexdigest()
report['scope']='Source-relative sewn follower gap and edge bounds in poses 1,13,35 only; not all-frame sewing or complete contact proof.'
(out/'followers.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('EASE_FOLLOWERS_PASS',flush=True)
