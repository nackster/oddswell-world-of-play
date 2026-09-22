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
assert evidence['independent_reopen']=='PASS' and evidence['packed_texture_maps']==31
assert cold['result']=='PASS' and cold['cameras']==10
views={'Gameplay':(1920,1080),'Court_and_Arena':(1600,900),'Architecture_Detail':(1600,900),'Character_Detail':(1000,1100),'Landscape_Detail':(1000,1100),'Character_ThreeQuarter':(1000,1100),'Head_Front':(1000,1100),'Head_Profile':(1000,1100),'Hand_Left':(1000,1000),'Hand_Right':(1000,1000)}
renders={}
for name,size in views.items():
    path=ROOT/f'StreetSlice_{name}.png'
    with path.open('rb') as stream:header=stream.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==size
    renders[path.name]={'width':size[0],'height':size[1],'sha256':sha(path)}
log=LOGS/'anatomical-jacket-final-views.log'
text=log.read_text(encoding='utf-8-sig',errors='replace')
assert 'ODDSWELL_STREET_SLICE_REOPEN_PASS' in text
assert all('ODDSWELL_STREET_SLICE_VIEW_PASS '+name in text for name in views if name!='Gameplay')
iterations=[]
for pattern in ('character-landscape-preview[0-9]*.log','character-landscape-tailoring-preview[0-9]*.log','character-human-preview[0-9]*.log','character-reference-preview[0-9]*.log','character-body-preview[0-9]*.log','character-realism-preview[0-9]*.log','character-presence-preview[0-9]*.log','character-drape-preview[0-9]*.log'):
    for path in sorted(LOGS.glob(pattern),key=lambda p:int(p.stem.split('preview')[-1])):
        assert 'ODDSWELL_STREET_SLICE_RENDER_PASS' in path.read_text(encoding='utf-8-sig',errors='replace')
        iterations.append({'log':path.name,'sha256':sha(path),'native_render':'PASS'})
files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in ('.blend','.py','.obj','.jpg','.exr','.md','.mhmat','.target')}
for p in sorted((ROOT/'textures').rglob('*.png')):files[p.relative_to(ROOT).as_posix()]=sha(p)
files['source-assets/skin-source.json']=sha(ROOT/'source-assets/skin-source.json')
files['source-assets/fabric-sources.json']=sha(ROOT/'source-assets/fabric-sources.json')
files['source-assets/facial-targets.json']=sha(ROOT/'source-assets/facial-targets.json')
manifest={'request':'Complete the new very realistic human goal, then continue the scene roadmap','goal_status':'active','delivery':'Editable native Blender scene and ten native renders; offline art study','starting_checkpoint':'76ccb76','previous_checkpoint':'f73e021','evidence':evidence,'cold_reopen':cold,'renders':renders,'files_sha256':files,'render_log':{'path':str(log),'sha256':sha(log)},'preview_iterations':iterations,'optical_studies':[{'log':p.name,'sha256':sha(p)} for p in sorted(LOGS.glob('optical-study*.log'))],'hand_studies':[{'log':p.name,'sha256':sha(p)} for p in sorted(LOGS.glob('hand-surface-study*.log'))],'facial_form_studies':[{'log':p.name,'sha256':sha(p)} for p in sorted(LOGS.glob('facial-form-study*.log'))],'original_source_bytes_preserved':True,'runtime_map_modified':False,'runtime_character_modified':False,'visual_review':'Continuing from `f73e021`, the jacket now settles against a hidden, editable torso and arm surface derived from the retained CC0 anatomy and male body target. The support follows the posed shoulders, elbows and wrists. The cloth uses zero added expansion, a smoother collision surface and firmer waistband attachment. Original tailoring, the fitted starting surface and raw gravity output are retained separately; displacement filtering now preserves fully pinned trim. Pockets, raglan seams, teal panels and fastening follow the final cloth.','body_detail_review':'Four native drape studies exposed collapsed shoulders, incorrect torso skinning, an unstable fit across closed garment caps and a scalloped hem. Those versions were rejected or revised. The retained version limits fitting to free cloth, corrects the torso/arm transition, smooths anatomical contact and reapplies attachment weights after filtering. A cold check also caught inward teal-panel vertices; the shared fitting function now explicitly seats them on the outward surface. The final checks measure zero displacement at fully pinned attachments and about 5.99 mm minimum clearance for free cloth control vertices. These are construction checks, not proof of photographic realism.','remaining':'The human-realism goal remains active. The jacket has a slimmer, more body-supported silhouette, but fold transitions and material response still need refinement; skin and cuticles remain too uniform. Next improve these visible surface qualities and review the full character against the original reference. Architecture/retail variety and planting realism follow human acceptance. The internal torso is a cloth-fitting aid; this is an editable offline Blender study, not a visible replacement body, production animation rig or runtime update.'}
manifest['anatomical_jacket_studies']=[{'log':p.name,'sha256':sha(p)} for p in sorted(LOGS.glob('anatomical-jacket-study*.log'))]
reproduction=LOGS/'anatomical-jacket-reproduction.log'
assert 'AUTHORED_DRAPE_REPRODUCTION_PASS' in reproduction.read_text(encoding='utf-8-sig',errors='replace')
manifest['authored_drape_reproduction']={'log':reproduction.name,'sha256':sha(reproduction),'maximum_allowed_control_difference_m':.00001}
basis_log=LOGS/'hand-surface-basis-check.log'
basis_text=basis_log.read_text(encoding='utf-8-sig',errors='replace')
assert all('HAND_BASE_POSE_PRESERVED '+side+' 26569 0.0' in basis_text for side in ('left','right'))
manifest['hand_basis_check']={'log':basis_log.name,'sha256':sha(basis_log),'compared_checkpoint':'0fb8d78','vertices_per_hand':26569,'maximum_world_position_difference_m':0.0}
(ROOT/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
canvas=PROJECT/'Oddswell/Visual Maps/Beta Delivery Roadmap.canvas'
raw=canvas.read_bytes().decode('utf-8');data=json.loads(raw)
node=next(n for n in data['nodes'] if n['id']=='bdr-now');old=json.dumps(node['text'],ensure_ascii=False)
new='## NOW - CHARACTER AND LANDSCAPE GOAL\n[TARGET] First OddsWell concept picture; more human character\n[DEVELOPED] Anatomical jacket support | gravity drape | fixed trim | fitted seams\n[RENDERED] Gameplay + nine native inspection views\n[SOURCE] Editable Blender | packed maps | retained licenses\n[NEXT] Cloth fold/material refinement | skin/cuticles | whole-character review\nVisual-quality goal active; offline art evidence.\n[[Art/Production/SundaleStreetSlice/DevelopmentGoal]]'
assert raw.count(old)==1
canvas.write_bytes(raw.replace(old,json.dumps(new,ensure_ascii=False),1).encode('utf-8'))
print(json.dumps({'renders':renders,'blend_bytes':(ROOT/'OddsWell_Sundale_StreetSlice.blend').stat().st_size,'cold_check':cold,'goal_status':'active'},indent=2))
