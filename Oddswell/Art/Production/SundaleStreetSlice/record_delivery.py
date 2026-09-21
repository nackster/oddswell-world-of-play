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
log=LOGS/'character-realism-final-views.log'
text=log.read_text(encoding='utf-8-sig',errors='replace')
assert 'ODDSWELL_STREET_SLICE_REOPEN_PASS' in text
assert all('ODDSWELL_STREET_SLICE_VIEW_PASS '+name in text for name in views if name!='Gameplay')
iterations=[]
for pattern in ('character-landscape-preview[0-9]*.log','character-landscape-tailoring-preview[0-9]*.log','character-human-preview[0-9]*.log','character-reference-preview[0-9]*.log','character-body-preview[0-9]*.log','character-realism-preview[0-9]*.log'):
    for path in sorted(LOGS.glob(pattern),key=lambda p:int(p.stem.split('preview')[-1])):
        assert 'ODDSWELL_STREET_SLICE_RENDER_PASS' in path.read_text(encoding='utf-8-sig',errors='replace')
        iterations.append({'log':path.name,'sha256':sha(path),'native_render':'PASS'})
files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in ('.blend','.py','.obj','.jpg','.exr','.md','.mhmat')}
for p in sorted((ROOT/'textures').rglob('*.png')):files[p.relative_to(ROOT).as_posix()]=sha(p)
files['source-assets/skin-source.json']=sha(ROOT/'source-assets/skin-source.json')
files['source-assets/fabric-sources.json']=sha(ROOT/'source-assets/fabric-sources.json')
manifest={'request':'Complete the new very realistic human goal, then continue the scene roadmap','goal_status':'active','delivery':'Editable native Blender scene and eight native renders; offline art study','starting_checkpoint':'76ccb76','previous_checkpoint':'3af6bd9','evidence':evidence,'cold_reopen':cold,'renders':renders,'files_sha256':files,'render_log':{'path':str(log),'sha256':sha(log)},'preview_iterations':iterations,'original_source_bytes_preserved':True,'runtime_map_modified':False,'runtime_character_modified':False,'visual_review':'The owner set a new sustained human-realism goal from 3af6bd9. This first iteration articulates the hips, knees and ankles separately, with a flat forward stance foot and a raised trailing heel. A 40-frame native cotton simulation develops shorts drape; its result is blended with the tailored base and relaxed to avoid excessive tiny wrinkles. The simulation uses body proxies plus the actual leg surface, with a final skin-clearance correction and refitted seams. Six original CC0 Poly Haven fabric maps now add photographed surface variation, displacement-derived bump and roughness to the jacket, shorts and canvas shoes. Terlenka provides the jacket weave; Denim Fabric 04 supplies the cotton weave, recolored in the shader to the existing OddsWell palette. Source photography is by colormass, processed by Rico Cilliers. The scene contains 31 packed maps. Box projection is an interim shading method; production garment UVs remain open.','body_detail_review':'Further native refinement reduces jacket torso/sleeve volume and concentrates folds around the armholes, elbows and waistband. Ribbed cuffs taper toward the wrists, with the sleeve ends fitted inside them. Each finger now bends around its three retained anatomical joints, with progressively deeper ring/little-finger curl and mild left/right asymmetry. The shoes have crossed laces, paired eyelets and a stitched toe panel. Fine tapered calf hairs follow the posed skin, and denser pocket-stitch samples follow the simulated shorts surface.','remaining':'This is a realism development checkpoint, not completion of the new goal. The overall figure still reads as a digital model: shoulder/armhole shaping, garment tension and collar construction need more work, alongside hand tendon/nail detail, face/eyelid expression and skin response. The calf hair is deliberately subtle at gameplay distance. Cloth is retained as static editable geometry after simulation; no gameplay cloth, animation rig or runtime integration is claimed. Architecture/retail and planting remain next in the roadmap after the human passes the visual criteria.'}
(ROOT/'delivery.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
canvas=PROJECT/'Oddswell/Visual Maps/Beta Delivery Roadmap.canvas'
raw=canvas.read_bytes().decode('utf-8');data=json.loads(raw)
node=next(n for n in data['nodes'] if n['id']=='bdr-now');old=json.dumps(node['text'],ensure_ascii=False)
new='## NOW - CHARACTER AND LANDSCAPE GOAL\n[TARGET] First OddsWell concept picture; more human character\n[DEVELOPED] Articulated body/hands | cotton drape | fitted cuffs and footwear\n[RENDERED] Gameplay + seven native inspection views\n[SOURCE] Editable Blender | packed maps | retained licenses\n[NEXT] Shoulder/collar construction, fine skin/face, whole-character realism review\nVisual-quality goal active; offline art evidence.\n[[Art/Production/SundaleStreetSlice/DevelopmentGoal]]'
assert raw.count(old)==1
canvas.write_bytes(raw.replace(old,json.dumps(new,ensure_ascii=False),1).encode('utf-8'))
print(json.dumps({'renders':renders,'blend_bytes':(ROOT/'OddsWell_Sundale_StreetSlice.blend').stat().st_size,'cold_check':cold,'goal_status':'active'},indent=2))
