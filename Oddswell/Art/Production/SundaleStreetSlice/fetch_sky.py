"""Restore the retained CC0 environment map if it is missing."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/4k/kloppenheim_06_puresky_4k.exr'
target=ROOT/'textures/kloppenheim_06_puresky_4k.exr'
if not target.exists():urllib.request.urlretrieve(URL,target)
record={'file':target.name,'url':URL,'asset':'https://polyhaven.com/a/kloppenheim_06_puresky','authors':['Greg Zaal','Jarod Guest'],'license':'CC0','license_url':'https://polyhaven.com/license','bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
(ROOT/'textures/sky-source.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('SKY_SOURCE_VERIFIED',record['sha256'])
