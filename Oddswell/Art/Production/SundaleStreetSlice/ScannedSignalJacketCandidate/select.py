from pathlib import Path
from PIL import Image
import json
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/SignalJacketStudy'
d=json.loads((out/'inspection.json').read_text(encoding='utf-8'))
image=Image.open(out.parent/'EricSource/tex/rp_eric_rigged_001_dif.jpg').convert('RGB')
selected=[]
for p in d['polygons']:
    u,v=p['uv'];r,g,b=image.getpixel((min(image.width-1,max(0,int(u*image.width))),min(image.height-1,max(0,int((1-v)*image.height)))))
    skin=r-g>25 and r-b>38
    w=p['weights'];hands=sum(value for name,value in w.items() if name.startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')))
    if p['z'][1]>1.005 and p['z'][0]<1.505 and not skin and hands<.20:
        selected.append(p['index'])
assert 1000<len(selected)<5000,len(selected)
(out/'selection.json').write_text(json.dumps({'selected_faces':selected,'selection':'Upper torso and arms selected by rest height, hand weights and warm skin-color exclusion; no texture is edited.'})+'\n',encoding='utf-8')
print('JACKET_SUPPORT_FACE_COUNT',len(selected))
