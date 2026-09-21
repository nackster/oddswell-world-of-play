"""Retain one CC0 MakeHuman skin and its original material/license metadata."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip'
ARCHIVE_SHA='b542127a8e25547c7c29c19f2d1d2adb9a664c80396ecd694095dbc8028a0107'
archive=ROOT.parents[3]/'client/OddsWell/Saved/NextTen20260912/makehuman_system_assets_cc0.zip'
archive.parent.mkdir(parents=True,exist_ok=True)
if not archive.exists():urllib.request.urlretrieve(URL,archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==ARCHIVE_SHA,'Changed source archive'
members={
    'young_lightskinned_male_diffuse.png':'862a26e335e958b70534cb5f0d7c47ef30ab148a56c42b3e9da969cf76f12963',
    'young_caucasian_male.mhmat':'6eda60b07ff2afbde078a2535ef3913593d84e9de92b2eb76c30f396a181fe2e',
}
target=ROOT/'textures/makehuman-skin';target.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as source:
    for name,digest in members.items():
        data=source.read('skins/young_caucasian_male/'+name)
        assert hashlib.sha256(data).hexdigest()==digest,name
        (target/name).write_bytes(data)
manifest={'source':URL,'catalog':'https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html','archive_sha256':ARCHIVE_SHA,'asset':'young_caucasian_male','license':'CC0; explicit declaration in original .mhmat','source_metadata_note':'The original material name says old_caucasian_male_detailed; its tags and archive path identify young_caucasian_male. Original bytes are retained.','copyright_at_release':['Data Collection AB','Joel Palmius','Jonas Hauquier'],'maps':members,'adaptation':'Original body UVs retained on exposed anatomical meshes; color adjusted only in native shader, original texture unchanged.'}
(ROOT/'source-assets/skin-source.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_SKIN_SOURCE_PASS',json.dumps(members))
