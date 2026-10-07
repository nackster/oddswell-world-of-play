"""Keep the actual open waist edge fixed while rounding the posterior seat."""
import bpy,json,hashlib,heapq,math
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/SeatFlowCandidate/SeatFlow.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='ec5b658a9f7724687c6589587436979411f00e1e91b52fcf1de44a6b8daa4a7a';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];mid=bpy.data.objects['Hip study | registered cloth midsurface'];pants.data=pants.data.copy();mid.data=pants.data
points=[pants.matrix_world@v.co for v in pants.data.vertices];edges={tuple(sorted(e.vertices)):0 for e in pants.data.edges};graph=[[] for p in points]
for poly in pants.data.polygons:
    ids=list(poly.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]+=1
for a,b in edges:
    length=(points[a]-points[b]).length;graph[a].append((b,length));graph[b].append((a,length))
boundary=sorted({i for edge,count in edges.items() if count==1 for i in edge if points[i].z>.8});assert len(boundary)==160
distance=[math.inf]*len(points);heap=[]
for i in boundary:distance[i]=0.;heapq.heappush(heap,(0.,i))
while heap:
    d,i=heapq.heappop(heap)
    if d!=distance[i]:continue
    for j,length in graph[i]:
        if d+length<distance[j]:distance[j]=d+length;heapq.heappush(heap,(d+length,j))
group=pants.vertex_groups['Posterior cotton finite bend radius'];changes=[]
for v in pants.data.vertices:
    old=next((w.weight for w in v.groups if w.group==group.index),0.)
    t=max(0.,min(1.,distance[v.index]/.060));new=old*t*t*(3-2*t)
    if abs(new-old)>1e-9:group.add([v.index],new,'REPLACE');changes.append({'id':v.index,'distance_from_waist_m':distance[v.index],'old':old,'new':new})
assert all(next((w.weight for w in pants.data.vertices[i].groups if w.group==group.index),0.)==0 for i in boundary)
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'WaistJoin.blend'),compress=True)
report={'source_sha256':expected,'candidate_sha256':sha(out/'WaistJoin.blend'),'method':'Preserve the complete 160-control open waist boundary. Multiply only the existing posterior smoothing group by a cubic smoothstep of shortest native-edge distance / 60 mm. Original controls, old fields and bone influence are unchanged. Shared registered cloth midsurface uses the same edited mesh. No new collision/physical simulation claim.','waist_boundary_ids':boundary,'fade_distance_m':.060,'changed_controls':changes}
(out/'build-report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('WAIST_JOIN_BUILT',len(changes),report['candidate_sha256'],flush=True)
