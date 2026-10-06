"""Matched native body views plus close waist and neckline review."""
from pathlib import Path
import sys
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
code=(root/'Oddswell/Art/Production/SundaleStreetSlice/HandArticulationCandidate/render.py').read_text().replace("out/'HandMotion.blend'","out/'WaistNeck.blend'")
exec(compile(code,str(out/'render.py'),'exec'))
if '--preview' not in sys.argv:
    scene.camera=camera;scene.cycles.samples=20
    render('Waist_Rear',13,(-1.10,-3.8,1.00),(-.76,-2.4,.92),85,840,840)
    render('Waist_Front',7,(-.82,-.9,1.00),(-.76,-2.4,.92),85,840,840)
    for frame in (7,33):
        render('Neck_Rear_%02d'%frame,frame,(-1.12,-3.10,1.58),(-.69,-2.33,1.525),85,704,704)
