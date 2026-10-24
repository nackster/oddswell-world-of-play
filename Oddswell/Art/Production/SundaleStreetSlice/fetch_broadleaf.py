"""Retain CC0 Island Tree 01 source and its broad-leaf maps for adaptation."""
import hashlib,json,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
asset='island_tree_01'
request=urllib.request.Request('https://api.polyhaven.com/files/'+asset,headers={'User-Agent':'OddsWell-Art-Study/1.0'})
catalog=json.load(urllib.request.urlopen(request))
entry=catalog['blend']['2k']['blend']
folder=ROOT/'textures/broadleaf';folder.mkdir(exist_ok=True)
jobs=[(entry,ROOT/'source-assets/island_tree_01_2k.blend')]
jobs.extend((record,folder/Path(name).name) for name,record in entry['include'].items() if '_leaves_' in name or '_branches_' in name)
def fetch(job):
    record,path=job
    if not path.exists():urllib.request.urlretrieve(record['url'],path)
    data=path.read_bytes()
    assert hashlib.md5(data).hexdigest()==record['md5'],path
    print('BROADLEAF_SOURCE_PASS',path.name,len(data),flush=True)
    return {'file':path.relative_to(ROOT).as_posix(),'url':record['url'],'bytes':len(data),'source_md5':record['md5'],'sha256':hashlib.sha256(data).hexdigest()}
with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,jobs))
(ROOT/'source-assets/broadleaf-source.json').write_text(json.dumps({'asset':'https://polyhaven.com/a/island_tree_01','authors':['Rico Cilliers (cleanup, processing)','Rob Tuytel (scanning, processing)'],'license':'CC0','license_url':'https://polyhaven.com/license','scope':'Retained original native source and leaf/twig maps for broad-leaf geometry adaptation. Source trunk geometry and trunk-specific maps are not used.','adaptation':'LOD1 leaf clusters retain their UVs, use a 0.40 decimation ratio and 6x local scaling, and replace the Jacaranda leaf family in a single branch-mask emission pass. Raised woody geometry preserves scanned leaf proportions. Understory instances use a separate leaf material. See broadleaf_canopy.py and mature_trees.py.','files':records},indent=2)+'\n',encoding='utf-8')
