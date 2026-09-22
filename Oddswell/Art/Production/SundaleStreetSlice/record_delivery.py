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
assert cold['result']=='PASS' and cold['cameras']==8
views={'Gameplay':(1920,1080),'Court_and_Arena':(1600,900),'Architecture_Detail':(1600,900),'Character_Detail':(1000,1100),'Landscape_Detail':(1000,1100),'Character_ThreeQuarter':(1000,1100),'Head_Front':(1000,1100),'Head_Profile':(1000,1100)}
renders={}
for name,size in views.items():
    path=ROOT/f'StreetSlice_{name}.png'
    with path.open('rb') as stream:header=stream.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==size
    renders[path.name]={'width':size[0],'height':size[1],'sha256':sha(path)}
log=LOGS/'character-drape-final-views.log'
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
manifest={'request':'Complete the new very realistic human goal, then continue the scene roadmap','goal_status':'active','delivery':'Editable native Blender scene and eight native renders; offline art study','starting_checkpoint':'76ccb76','previous_checkpoint':'f406b8e','evidence':evidence,'cold_reopen':cold,'renders':renders,'files_sha256':files,'render_log':{'path':str(log),'sha256':sha(log)},'preview_iterations':iterations,'original_source_bytes_preserved':True,'runtime_map_modified':False,'runtime_character_modified':False,'visual_review':'Continuing from `f406b8e`, the jacket now uses a 45-frame native gravity study on a lighter control mesh, with 4% fabric ease and fixed collar, fastening, hem and cuff attachments. A smooth inner fitting envelope supports the cloth; this is a garment proxy, not newly scanned body anatomy. The retained result blends 85% filtered simulation displacement with the tailored base. Original tailoring and raw simulation positions remain editable point attributes.','body_detail_review':'The first dense, low-bending-resistance study produced a crumpled leather-like surface and was rejected. A coarser, stiffer study reduced the small wrinkles; strong filtering then made it too rigid. The retained version adds fabric ease and uses six displacement-filter passes to keep broader folds. Native front/rear comparisons also led to a darker slate dye, a more matte fabric response and fitted front/back raglan seams. Stray shoulder lines were traced to old torso-profile yoke stitch ends. All three teal panels now receive stitches from their actual boundary edges. Further close-ups led to nearly flush, subdivided teal panels, removal of the old overlapping sleeve/panel lines, and continuous raglan paths over connected garment faces that meet beneath each arm. The seam search permits face diagonals to avoid the stair-step paths of a rectangular edge grid. A later clearance review caught zipper tape buried by the drape; tape and teeth are fitted to the final jacket/collar front surface, and the saved-scene check now verifies positive tape clearance.','remaining':'The human-realism goal remains active. This improves the jacket development baseline, but the figure still reads as a digital model. Garment fold sharpness and tailoring, hand tendon/nail detail, skin response, eye tissue and individual facial expression remain unfinished. Continue close-up and whole-figure review against the original reference, then architectural/retail variety and planting realism. The scene is an editable static Blender study; no runtime cloth, animation rig, game-character update or beta-exit credit is claimed.'}
(ROOT/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
canvas=PROJECT/'Oddswell/Visual Maps/Beta Delivery Roadmap.canvas'
raw=canvas.read_bytes().decode('utf-8');data=json.loads(raw)
node=next(n for n in data['nodes'] if n['id']=='bdr-now');old=json.dumps(node['text'],ensure_ascii=False)
new='## NOW - CHARACTER AND LANDSCAPE GOAL\n[TARGET] First OddsWell concept picture; more human character\n[DEVELOPED] Native jacket drape | fabric ease | fitted raglan and panel stitches\n[RENDERED] Gameplay + seven native inspection views\n[SOURCE] Editable Blender | packed maps | retained licenses\n[NEXT] Fine garment/hands, skin/eyes/expression, whole-character realism review\nVisual-quality goal active; offline art evidence.\n[[Art/Production/SundaleStreetSlice/DevelopmentGoal]]'
assert raw.count(old)==1
canvas.write_bytes(raw.replace(old,json.dumps(new,ensure_ascii=False),1).encode('utf-8'))
print(json.dumps({'renders':renders,'blend_bytes':(ROOT/'OddsWell_Sundale_StreetSlice.blend').stat().st_size,'cold_check':cold,'goal_status':'active'},indent=2))
