"""Retain the CC0 Jacaranda geometry and 2K surface maps for the tree study."""
import hashlib,json,urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parent
maps=ROOT/'textures/jacaranda';maps.mkdir(exist_ok=True)
files=[]
for part in ('branches','leaves','trunk'):
    for channel in ('diff','nor_gl','rough')+ (('alpha',) if part=='leaves' else ()):
        ext='png' if channel=='alpha' else 'jpg'
        name=f'jacaranda_tree_{part}_{channel}_2k.{ext}'
        files.append((f'https://dl.polyhaven.org/file/ph-assets/Models/{ext}/2k/jacaranda_tree/{name}',maps/name))
files.append(('https://dl.polyhaven.org/file/ph-assets/Models/blend/4k/jacaranda_tree/jacaranda_tree_4k.blend',ROOT/'source-assets/jacaranda_tree_4k.blend'))
def fetch(item):
    url,path=item
    if not path.exists():urllib.request.urlretrieve(url,path)
    result={'file':path.relative_to(ROOT).as_posix(),'url':url,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    print('TREE_SOURCE_SAVED',path.name,result['bytes'],flush=True)
    return result
with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,files))
record={'asset':'https://polyhaven.com/a/jacaranda_tree','authors':['Rico Cilliers (model and textures)','Rob Tuytel (guidance)'],'license':'CC0','license_url':'https://polyhaven.com/license','adaptation':'Original source file unmodified. Current Sundale derivative raises woody geometry, combines original branch growth masks, and uses one emission pass with retained Island Tree 01 leaf clusters. Three shared crown variants use different seeds and proportions. 2K maps replace original 4K paths. See mature_trees.py and broadleaf_canopy.py for reproducible parameters.','files':records}
(ROOT/'source-assets/jacaranda-source.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
