"""Record reviewed native renders and reproducible sources after a cold check."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[3]
LOGS=PROJECT/'client/OddsWell/Saved/NextTen20260912'
def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
evidence=json.loads((ROOT/'scene-evidence.json').read_text(encoding='utf-8'))
cold=json.loads((ROOT/'cold-reopen.json').read_text(encoding='utf-8'))
assert evidence['independent_reopen']=='PASS' and evidence['packed_texture_maps']==24
assert cold['result']=='PASS' and cold['cameras']==6
views={'Gameplay':(1920,1080),'Court_and_Arena':(1600,900),'Architecture_Detail':(1600,900),'Character_Detail':(1000,1100),'Landscape_Detail':(1000,1100),'Character_ThreeQuarter':(1000,1100)}
renders={}
for name,size in views.items():
    path=ROOT/f'StreetSlice_{name}.png'
    with path.open('rb') as stream:header=stream.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==size
    renders[path.name]={'width':size[0],'height':size[1],'sha256':sha(path)}
log=LOGS/'character-landscape-tailoring-final-views.log'
text=log.read_text(encoding='utf-8-sig',errors='replace')
assert 'ODDSWELL_STREET_SLICE_REOPEN_PASS' in text
assert all('ODDSWELL_STREET_SLICE_VIEW_PASS '+name in text for name in views if name!='Gameplay')
iterations=[]
for path in sorted(LOGS.glob('character-landscape-preview[0-9]*.log'),key=lambda p:int(p.stem.split('preview')[-1])):
    assert 'ODDSWELL_STREET_SLICE_RENDER_PASS' in path.read_text(encoding='utf-8-sig',errors='replace')
    iterations.append({'log':path.name,'sha256':sha(path),'native_render':'PASS'})
for path in sorted(LOGS.glob('character-landscape-tailoring-preview[0-9]*.log')):
    assert 'ODDSWELL_STREET_SLICE_RENDER_PASS' in path.read_text(encoding='utf-8-sig',errors='replace')
    iterations.append({'log':path.name,'sha256':sha(path),'native_render':'PASS'})
files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in ('.blend','.py','.obj','.jpg','.exr','.md')}
for p in sorted((ROOT/'textures').rglob('*.png')):files[p.relative_to(ROOT).as_posix()]=sha(p)
manifest={'request':'Develop the character and landscape toward the first OddsWell picture; sustain the visual-quality goal','goal_status':'active','delivery':'Editable native Blender scene and six native renders; offline art study','starting_checkpoint':'76ccb76','previous_checkpoint':'8c868ec','evidence':evidence,'cold_reopen':cold,'renders':renders,'files_sha256':files,'render_log':{'path':str(log),'sha256':sha(log)},'preview_iterations':iterations,'original_source_bytes_preserved':True,'runtime_map_modified':False,'runtime_character_modified':False,'visual_review':'Continuous hip/inseam topology replaces overlapping shorts volumes; the first sharp leg transition was rejected and smoothed. Retained views show less crotch bulk and softer sleeve caps/shoulder joins. Civic limestone has quieter grain and broken sediment variation. The static character remains below reference fidelity.','remaining':'Reference fidelity remains an active art goal, especially head/neck proportions, rear inseam and cloth behavior, architectural variety, planting composition and photographic surface detail. Runtime LODs/collision/material baking/rigging/performance are not proven.'}
(ROOT/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
canvas=PROJECT/'Oddswell/Visual Maps/Beta Delivery Roadmap.canvas'
raw=canvas.read_bytes().decode('utf-8');data=json.loads(raw)
node=next(n for n in data['nodes'] if n['id']=='bdr-now');old=json.dumps(node['text'],ensure_ascii=False)
new='## NOW - CHARACTER AND LANDSCAPE GOAL\n[TARGET] First OddsWell concept picture\n[DEVELOPED] Continuous shorts | softer shoulders | sediment stone\n[RENDERED] Gameplay + five native inspection views\n[SOURCE] Editable Blender | packed maps | retained licenses\n[NEXT] Head/neck, rear inseam, then facade/retail variety\nVisual-quality goal active; offline art evidence.\n[[Art/Production/SundaleStreetSlice/DevelopmentGoal]]'
assert raw.count(old)==1
canvas.write_bytes(raw.replace(old,json.dumps(new,ensure_ascii=False),1).encode('utf-8'))
print(json.dumps({'renders':renders,'blend_bytes':(ROOT/'OddsWell_Sundale_StreetSlice.blend').stat().st_size,'cold_check':cold,'goal_status':'active'},indent=2))
