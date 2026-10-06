"""Matched whole figure views and native walking preview."""
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
code=(root/'Oddswell/Art/Production/SundaleStreetSlice/HandArticulationCandidate/render.py').read_text()
exec(compile(code.replace("out/'HandMotion.blend'","out/'HipSeat.blend'"),str(out/'render.py'),'exec'))
