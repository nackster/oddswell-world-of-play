import bpy
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[5]
bpy.ops.wm.open_mainfile(filepath=str(root/'Oddswell/Art/Production/SundaleStreetSlice/SignalJoinCandidate/SignalJoin.blend'))
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
print('CHARACTER_MESHES',[(o.name,len(o.data.vertices)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Character | ') and len(o.data.vertices)>500],flush=True)
support=bpy.data.objects['Character | internal torso support']
print('SUPPORT',support.hide_render,tuple((round(min((support.matrix_world@v.co)[axis] for v in support.data.vertices),3),round(max((support.matrix_world@v.co)[axis] for v in support.data.vertices),3)) for axis in range(3)),flush=True)
for obj in bpy.data.objects:
    if obj.type=='MESH' and obj.name.startswith('Character | ') and any(w in obj.name for w in ('anatomical','skin','shorts')):
        if len(obj.data.vertices)<100:continue
        print('OBJECT',obj.name,len(obj.data.vertices),'hide',obj.hide_render,'bounds',tuple((round(min((obj.matrix_world@v.co)[axis] for v in obj.data.vertices),3),round(max((obj.matrix_world@v.co)[axis] for v in obj.data.vertices),3)) for axis in range(3)),flush=True)
for row in (0,4,8,12,16):
    points=[pants.matrix_world@pants.data.vertices[row*80+j].co for j in range(80)]
    print('RING',row,'z',round(sum(p.z for p in points)/80,4),'x',round(min(p.x for p in points),4),round(max(p.x for p in points),4),'y',round(min(p.y for p in points),4),round(max(p.y for p in points),4),flush=True)
skin=bpy.data.objects['Character | anatomical legs']
for z in (.7,.75,.8,.85,.9):
    points=[skin.matrix_world@v.co for v in skin.data.vertices if abs((skin.matrix_world@v.co).z-z)<.008]
    if points:print('SKIN_SLICE',z,len(points),'x',round(min(p.x for p in points),4),round(max(p.x for p in points),4),'y',round(min(p.y for p in points),4),round(max(p.y for p in points),4),flush=True)
