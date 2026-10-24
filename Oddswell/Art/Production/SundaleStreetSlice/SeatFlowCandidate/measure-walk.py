"""Compare visible rear-patch dimensions at corresponding cloth-atlas endpoints."""
import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/ChestContourCandidate/ChestContour.blend';rows={}
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for label,path in [('source',source),('candidate',out/'SeatFlow.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
    for o in scene.objects:
        if o.name.startswith(('Character | sewn cotton back pocket','Cotton | actual pocket sewing surface','Hip study | registered cloth midsurface','Character | shorts leg continuous tailoring')):
            for m in o.modifiers:
                if m.type=='SUBSURF':m.levels=m.render_levels
    records=[]
    for frame in range(1,50):
        scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();details={}
        for side in ('left','right'):
            o=bpy.data.objects['Character | sewn cotton back pocket '+side];ev=o.evaluated_get(deps);mesh=ev.to_mesh();uv=mesh.attributes['Tailored rear cotton patch UV'];points=[]
            for u,t in ((0,0),(.5,0),(1,0),(0,1),(.5,1),(1,1)):
                errors=[(v.vector.x-u)**2+(v.vector.y-t)**2 for v in uv.data];best=min(errors);ids=[i for i,value in enumerate(errors) if value<best+1e-10];points.append(min((ev.matrix_world@mesh.vertices[i].co for i in ids),key=lambda p:p.y))
            details[side]={'mouth_width_m':(points[2]-points[0]).length,'center_height_m':(points[4]-points[1]).length,'bottom_width_m':(points[5]-points[3]).length};ev.to_mesh_clear()
        records.append({'frame':frame,'pockets':details});print('SEAT_DIMENSIONS',label,frame,flush=True)
    rows[label]=records
summary={label:{side:{metric:{'min_m':min(r['pockets'][side][metric] for r in records),'max_m':max(r['pockets'][side][metric] for r in records),'range_m':max(r['pockets'][side][metric] for r in records)-min(r['pockets'][side][metric] for r in records)} for metric in ('mouth_width_m','center_height_m','bottom_width_m')} for side in ('left','right')} for label,records in rows.items()}
report={'source_sha256':sha(source),'candidate_sha256':sha(out/'SeatFlow.blend'),'method':'Render-subdivision complete visible pocket geometry. Corresponding nearest atlas endpoints, choosing the rear-facing shell point when thickness duplicates coordinates. Euclidean endpoint distances, not cloth geodesic dimensions or physical strain. All 49 authored integer frames.','summary':summary,'frames':rows};(out/'pocket-dimensions.json').write_text(json.dumps(report,indent=2)+'\n');print('SEAT_DIMENSIONS_DONE',flush=True)
