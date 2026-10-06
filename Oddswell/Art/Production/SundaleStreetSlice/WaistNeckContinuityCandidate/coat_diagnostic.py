import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
bpy.ops.wm.open_mainfile(filepath=str(root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/HipSeat.blend'));scene=bpy.context.scene;scene.frame_set(33);coat=bpy.data.objects['Character | tailored slate jacket']
flags=[m.show_viewport for m in coat.modifiers];records=[]
for m in coat.modifiers:m.show_viewport=False
for count in range(len(flags)+1):
    if count:coat.modifiers[count-1].show_viewport=flags[count-1]
    bpy.context.view_layer.update();ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();ps=[ev.matrix_world@v.co for v in mesh.vertices]
    edges=sorted([(ps[e.vertices[0]]-ps[e.vertices[1]]).length,tuple(e.vertices)] for e in mesh.edges)[-8:]
    records.append({'stage':'base' if count==0 else coat.modifiers[count-1].name,'type':None if count==0 else coat.modifiers[count-1].type,'vertices':len(ps),'edges':[{'length_m':length,'indices':indices,'endpoints':[list(ps[i]) for i in indices]} for length,indices in reversed(edges)]});ev.to_mesh_clear()
(out/'coat-deformation.json').write_text(json.dumps(records,indent=2)+'\n');print('COAT_DIAGNOSTIC_DONE',flush=True)
