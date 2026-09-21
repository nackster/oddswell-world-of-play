"""Retain pinned CC0 MakeHuman hm08 facial targets without changing the OBJ."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
COMMIT='a8bc2d54ff0ac92e78ff71431b1023eda42bf482'
folder=ROOT/'source-assets/facial-targets';folder.mkdir(exist_ok=True)
def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'OddsWell-native-character-study'})
    with urllib.request.urlopen(request,timeout=30) as response:return response.read()
records={}
for relative in ('head/head-age-incr.target','eyes/l-eye-height2-decr.target','eyes/r-eye-height2-decr.target'):
    path='makehuman/data/targets/'+relative
    metadata=json.loads(get('https://api.github.com/repos/makehumancommunity/makehuman/contents/'+path+'?ref='+COMMIT))
    url='https://raw.githubusercontent.com/makehumancommunity/makehuman/'+COMMIT+'/'+path
    destination=folder/Path(relative).name
    data=destination.read_bytes() if destination.exists() else get(url)
    assert b'CC0' in data and b'basemesh hm08' in data
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==metadata['sha']
    destination.write_bytes(data)
    records[destination.name]={'url':url,'git_blob_sha1':metadata['sha'],'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
source={'commit':COMMIT,'license':'CC0 1.0 Universal','license_url':'https://github.com/makehumancommunity/makehuman/blob/'+COMMIT+'/LICENSE.ASSETS.md','basemesh':'hm08','files':records}
(ROOT/'source-assets/facial-targets.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8',newline='\n')
print('FACIAL_TARGET_SOURCES_PASS',len(records))
