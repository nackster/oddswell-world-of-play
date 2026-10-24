"""Fetch one public vendor pack for the local licensee; never publish its assets."""
from pathlib import Path
import urllib.request,zipfile,hashlib,io,json
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists())
out=root/'downloads/licensed-characters/RenderpeopleEric';out.mkdir(parents=True,exist_ok=True)
url='https://renderpeople.com/sample/free/renderpeople_free_rigged_people_FBX.zip'
archive=urllib.request.urlopen(url,timeout=120).read();sha=hashlib.sha256(archive).hexdigest()
assert sha=='dadbe6fb83345566ff1d2822c0fa38e05aaa09c17d7f1340719a4c8e01dbadcd','Vendor download changed; inspect model and current license before updating this pin'
with zipfile.ZipFile(io.BytesIO(archive)) as z:data=z.read('rp_eric_rigged_001_FBX.zip')
(out/'rp_eric_rigged_001_FBX.zip').write_bytes(data)
dest=(out/'EricSource').resolve();dest.mkdir(exist_ok=True)
with zipfile.ZipFile(io.BytesIO(data)) as z:
    for name in z.namelist():
        path=(dest/name).resolve();assert path.is_relative_to(dest)
        if name.endswith('/'):path.mkdir(parents=True,exist_ok=True)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(name))
(out/'download-receipt.json').write_text(json.dumps({'url':url,'archive_sha256':sha,'selected_asset':'Eric Rigged 001','license':'https://renderpeople.com/general-terms-and-conditions/','storage':'Ignored local licensed assets'},indent=2)+'\n',encoding='utf-8')
print('SCANNED_SOURCE_DOWNLOADED',out)
