from pathlib import Path
from PIL import Image
import json
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy'
d=json.loads((out/'inspection.json').read_text(encoding='utf-8'))
image=Image.open(out.parent/'EricSource/tex/rp_eric_rigged_001_dif.jpg').convert('RGB')
def share(w,prefixes):return sum(value for name,value in w.items() if name.startswith(prefixes))
top=[];bottom=[];shoes=[];skin_faces=[]
for p in d['polygons']:
    u,v=p['uv'];r,g,b=image.getpixel((min(image.width-1,max(0,int(u*image.width))),min(image.height-1,max(0,int((1-v)*image.height)))))
    w=p['weights'];z=p['center'][2]
    hands=share(w,('hand_','thumb_','index_','middle_','ring_','pinky_'));arms=hands+share(w,('upperarm','lowerarm'));feet=share(w,('foot_','ball_'));head=share(w,('head','jaw','eye','mouth'))
    if r-g>25 and r-b>38:
        skin_faces.append(p['index']);continue
    # Long-sleeve top: hip to the shirt collar (hidden inside the mock neck), including the shirt cuffs but not the hands or hair.
    if z>=.955 and z<1.56 and head<.3 and hands<.35:top.append(p['index'])
    # Joggers: waist to ankle, including the belt but excluding arms and shoes.
    if z<=1.05 and arms<.2 and feet<.5:bottom.append(p['index'])
    if feet>=.5:shoes.append(p['index'])
assert 1500<len(top)<5000 and 1000<len(bottom)<4000 and 300<len(shoes)<2000,(len(top),len(bottom),len(shoes))
(out/'selection.json').write_text(json.dumps({'top_faces':top,'bottom_faces':bottom,'shoe_faces':shoes,'skin_faces':skin_faces,
    'selection':'Clothed scan faces split by rest height, hand/arm/foot weights and warm skin-color exclusion; no texture or source mesh is edited.'})+'\n',encoding='utf-8')
print('STARTER_SUPPORT_FACE_COUNTS',len(top),len(bottom),len(shoes),len(skin_faces))
