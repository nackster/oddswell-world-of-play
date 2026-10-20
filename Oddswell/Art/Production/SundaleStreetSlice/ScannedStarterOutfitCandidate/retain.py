"""Copy permitted renders and reports into the repository and write the manifest. Vendor-derived models stay local."""
from pathlib import Path
import json, hashlib, subprocess
dest=Path(__file__).resolve().parent;root=next(p for p in dest.parents if (p/'.git').exists())
out=root/'downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy';native=out/'OddsWellStarterOutfit.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report=json.loads((out/'starter-report.json').read_text(encoding='utf-8'));coverage=json.loads((out/'coverage-report.json').read_text(encoding='utf-8'))
street=json.loads((out/'street-report.json').read_text(encoding='utf-8'))
assert report['candidate_sha256']==sha(native)==coverage['candidate_sha256']==street['candidate_sha256']
assert report['source_sha256']==sha(out.parent/'MotionRefinement/OddsWellHumanMotion.blend')
assert report['cold_reopen_pass'] and report['source_mesh_uv_weights_bind_maps_preserved'] and len(report['pose_checks'])==49
assert not street['runtime_integrated'] and street['appended_actor_objects']==16
assert subprocess.run(['git','check-ignore','-q',str(native.relative_to(root))],cwd=root).returncode==0
video=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',str(out/'Walking.mp4')]))
s=video['streams'][0];assert int(s['nb_read_frames'])==24 and s['r_frame_rate']=='12/1' and (s['width'],s['height'])==(640,704) and abs(float(video['format']['duration'])-2)<.01
(out/'video-report.json').write_bytes((json.dumps(video,indent=2)+'\n').encode('utf-8'))
# One contact sheet of the worst-frame show-through masks across the five cameras.
frame=coverage['worst']['frame'];masks=[str(out/'Coverage'/f'{v}_{frame:02d}.png') for v in coverage['views']]
subprocess.run(['ffmpeg','-loglevel','error','-y',*sum((['-i',m] for m in masks),[]),'-filter_complex',f'hstack={len(masks)},format=rgb24',str(out/'Coverage.png')],check=True)
evidence=['selection.json','starter-report.json','coverage-report.json','street-report.json','video-report.json','Full.png','Front.png','Side.png','Back.png','Close.png','Feet.png','Neck.png','NeckBack.png','Jacket.png','Gameplay.png','Coverage.png','Walking.mp4']
for name in evidence:
    data=(out/name).read_bytes()
    if name.endswith('.json'):data=data.replace(b'\r\n',b'\n')
    (dest/name).write_bytes(data)
assert not any(p.suffix.lower() in ('.blend','.fbx','.jpg','.zip') for p in dest.iterdir())
files=sorted(p.name for p in dest.iterdir() if p.is_file() and p.name!='manifest.json')
manifest={'native_candidate_local_path':str(native.relative_to(root)).replace('\\','/'),'native_candidate_sha256':report['candidate_sha256'],'native_candidate_bytes':native.stat().st_size,
          'raw_vendor_files_committed':False,'files':[{'path':n,'bytes':(dest/n).stat().st_size,'sha256':sha(dest/n)} for n in files]}
(dest/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
print('STARTER_OUTFIT_RETAINED',len(files),report['candidate_sha256'])
