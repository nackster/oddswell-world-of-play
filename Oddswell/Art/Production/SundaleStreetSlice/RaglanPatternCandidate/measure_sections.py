"""Measure actual posed arm loops instead of assuming a straight sleeve axis."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent
root=next(p for p in Path(__file__).resolve().parents if (p/'Oddswell').is_dir() and (p/'.git').exists())
bpy.ops.wm.open_mainfile(filepath=str(root/'Oddswell/Art/Production/SundaleStreetSlice/FourPanelCottonCandidate/FourPanelCotton.blend'))
obj=bpy.data.objects['Character | internal torso support']
tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
inverse=obj.matrix_world.inverted()
sections={}
for z in (.98,1.04,1.10,1.16,1.22,1.26,1.30,1.34,1.38):
    groups=[];group=[]
    for j in range(321):
        x=-1.10+j*.0025
        rear=tree.ray_cast(inverse@Vector((x,-3,z)),Vector((0,1,0)))[0]
        front=tree.ray_cast(inverse@Vector((x,-1.8,z)),Vector((0,-1,0)))[0]
        if rear is not None and front is not None:
            a,b=obj.matrix_world@rear,obj.matrix_world@front
            group.append((a.lerp(b,.5),abs(b.y-a.y)))
        elif group:groups.append(group);group=[]
    if group:groups.append(group)
    sections[str(z)]=[{'center':list(sum((p*w for p,w in group),Vector())/sum(w for _,w in group)),
                        'x_bounds':[group[0][0].x,group[-1][0].x],'max_depth':max(w for _,w in group)} for group in groups]
(out/'body-sections.json').write_text(json.dumps(sections,indent=2))
print('POSED_ARM_SECTIONS',json.dumps(sections),flush=True)
