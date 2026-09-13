"""Fetch the selected CC0 sandstone and bark maps from Poly Haven."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parent / 'textures'
root.mkdir(exist_ok=True)
records=[]
for asset in ('sandstone_blocks_08','bark_brown_01'):
    for channel in ('diff','disp','rough'):
        name=f'{asset}_{channel}_4k.jpg'
        url=f'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/4k/{asset}/'+name
        path=root/name
        if not path.exists():
            with urlopen(url,timeout=60) as response:
                data=response.read()
            assert data[:2]==b'\xff\xd8', 'Expected a JPEG texture'
            path.write_bytes(data)
        records.append({'file':name,'source_page':'https://polyhaven.com/a/'+asset,'source_url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={'assets':['Sandstone Blocks 08','Bark Brown 01'],'author':'Rob Tuytel','license':'CC0','license_url':'https://polyhaven.com/license','maps':records}
(root/'sources.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STONE_TEXTURES_READY')
