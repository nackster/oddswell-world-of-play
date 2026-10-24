"""Retain original CC0 fabric maps and their upstream checksums."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
out=ROOT/'textures/fabrics';out.mkdir(parents=True,exist_ok=True)
assets={}
for asset in ('terlenka','denim_fabric_04'):
    def get(url):
        request=urllib.request.Request(url,headers={'User-Agent':'OddsWell art source retrieval/1.0'})
        with urllib.request.urlopen(request,timeout=60) as response:return json.load(response)
    files=get('https://api.polyhaven.com/files/'+asset)
    info=get('https://api.polyhaven.com/info/'+asset)
    entry={'source':'https://polyhaven.com/a/'+asset,'license':'CC0','authors':info['authors'],'dimensions_mm':info['dimensions'],'maps':{}}
    for kind,ext in (('Diffuse','jpg'),('Displacement','png'),('Rough','jpg')):
        source=files[kind]['2k'][ext];name=source['url'].rsplit('/',1)[-1];path=out/name
        if not path.exists():urllib.request.urlretrieve(source['url'],path)
        data=path.read_bytes()
        assert hashlib.md5(data).hexdigest()==source['md5'] and len(data)==source['size'],name
        entry['maps'][kind]={**source,'file':name,'sha256':hashlib.sha256(data).hexdigest()}
    assets[asset]=entry
(ROOT/'source-assets/fabric-sources.json').write_text(json.dumps(assets,indent=2)+'\n',encoding='utf-8',newline='\n')
print('FABRIC_SOURCES_PASS',len(assets)*3)
