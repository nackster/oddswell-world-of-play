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
assert evidence['independent_reopen']=='PASS' and evidence['packed_texture_maps']==25
assert cold['result']=='PASS' and cold['cameras']==8
views={'Gameplay':(1920,1080),'Court_and_Arena':(1600,900),'Architecture_Detail':(1600,900),'Character_Detail':(1000,1100),'Landscape_Detail':(1000,1100),'Character_ThreeQuarter':(1000,1100),'Head_Front':(1000,1100),'Head_Profile':(1000,1100)}
renders={}
for name,size in views.items():
    path=ROOT/f'StreetSlice_{name}.png'
    with path.open('rb') as stream:header=stream.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==size
    renders[path.name]={'width':size[0],'height':size[1],'sha256':sha(path)}
log=LOGS/'character-reference-final-views.log'
text=log.read_text(encoding='utf-8-sig',errors='replace')
assert 'ODDSWELL_STREET_SLICE_REOPEN_PASS' in text
assert all('ODDSWELL_STREET_SLICE_VIEW_PASS '+name in text for name in views if name!='Gameplay')
iterations=[]
for pattern in ('character-landscape-preview[0-9]*.log','character-landscape-tailoring-preview[0-9]*.log','character-human-preview[0-9]*.log','character-reference-preview[0-9]*.log'):
    for path in sorted(LOGS.glob(pattern),key=lambda p:int(p.stem.split('preview')[-1])):
        assert 'ODDSWELL_STREET_SLICE_RENDER_PASS' in path.read_text(encoding='utf-8-sig',errors='replace')
        iterations.append({'log':path.name,'sha256':sha(path),'native_render':'PASS'})
files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in ('.blend','.py','.obj','.jpg','.exr','.md','.mhmat')}
for p in sorted((ROOT/'textures').rglob('*.png')):files[p.relative_to(ROOT).as_posix()]=sha(p)
files['source-assets/skin-source.json']=sha(ROOT/'source-assets/skin-source.json')
manifest={'request':'Make the character more human while continuing toward the first OddsWell picture','goal_status':'active','delivery':'Editable native Blender scene and eight native renders; offline art study','starting_checkpoint':'76ccb76','previous_checkpoint':'f46ac3b','evidence':evidence,'cold_reopen':cold,'renders':renders,'files_sha256':files,'render_log':{'path':str(log),'sha256':sha(log)},'preview_iterations':iterations,'original_source_bytes_preserved':True,'runtime_map_modified':False,'runtime_character_modified':False,'visual_review':'Slimmer coordinated jacket/arm fit, lower fabric sheen, localized cotton creases and reduced rear-seat indentation move the silhouette toward the original design. Retained anatomical UVs carry a CC0 skin map across head, hands and legs. Front/profile and full-figure review checked skin registration, neck/cuffs and garment joins. Eye surface relief and reflections were refined.','remaining':'The neutral static face still needs eyelid/eye refinement, expression and individual identity. Cloth drape, architectural variety, planting composition and photographic surface detail remain open. Runtime LODs/collision/material baking/rigging/performance are not proven.'}
(ROOT/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
canvas=PROJECT/'Oddswell/Visual Maps/Beta Delivery Roadmap.canvas'
raw=canvas.read_bytes().decode('utf-8');data=json.loads(raw)
node=next(n for n in data['nodes'] if n['id']=='bdr-now');old=json.dumps(node['text'],ensure_ascii=False)
new='## NOW - CHARACTER AND LANDSCAPE GOAL\n[TARGET] First OddsWell concept picture; more human character\n[DEVELOPED] Textured human skin | slimmer slate jacket | cotton gathers\n[RENDERED] Gameplay + seven native inspection views\n[SOURCE] Editable Blender | packed maps | retained licenses\n[NEXT] Eyelids/expression, cloth drape, then facade/retail variety\nVisual-quality goal active; offline art evidence.\n[[Art/Production/SundaleStreetSlice/DevelopmentGoal]]'
assert raw.count(old)==1
canvas.write_bytes(raw.replace(old,json.dumps(new,ensure_ascii=False),1).encode('utf-8'))
print(json.dumps({'renders':renders,'blend_bytes':(ROOT/'OddsWell_Sundale_StreetSlice.blend').stat().st_size,'cold_check':cold,'goal_status':'active'},indent=2))
