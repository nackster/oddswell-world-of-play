import bpy,sys,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());helper=root/'Oddswell/Art/Production/SundaleStreetSlice/HandArticulationCandidate/render.py'
code=helper.read_text().replace("out/'HandMotion.blend'","out/'ThighDrape.blend'")
if '--close' in sys.argv:code=code.split("if '--preview' in sys.argv:")[0]
exec(compile(code,str(helper),'exec'))
if '--preview' not in sys.argv:
    scene.camera=camera
    render('Thigh_ProfileClose',1,(-1.80,-2.4,.83),(-.75,-2.4,.75),65,1000,900)
    render('Thigh_OppositeClose',13,(-1.80,-2.4,.83),(-.75,-2.4,.75),65,1000,900)
    render('Cotton_RearClose',13,(-.95,-3.22,.94),(-.75,-2.4,.775),65,1000,900)
record=out/'render-provenance.json';records=json.loads(record.read_text()) if record.exists() else {};mode='preview' if '--preview' in sys.argv else 'close' if '--close' in sys.argv else 'matched_and_close'
with (out/'ThighDrape.blend').open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
records[mode]={'candidate_sha256':sha,'renderer':'Blender 4.5.5 LTS / Cycles / OPTIX','frames':list(range(1,49,2)) if mode=='preview' else [1,7,13] if mode=='matched_and_close' else [1,13]};record.write_text(json.dumps(records,indent=2)+'\n')
