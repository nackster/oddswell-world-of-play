import bpy,json,statistics
from pathlib import Path
from mathutils.kdtree import KDTree
from mathutils import Vector
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'StableRecut.blend'));o=bpy.data.objects['Character | recut settled cotton shorts'];mesh=o.data;p=[v.co.copy() for v in mesh.shape_keys.key_blocks['Basis'].data];adj=[set() for _ in p];lengths=[]
for e in mesh.edges:
    a,b=e.vertices;adj[a].add(b);adj[b].add(a);lengths.append((p[a]-p[b]).length)
tree=KDTree(len(p))
for i,v in enumerate(p):tree.insert(v,i)
tree.balance();near=[]
for i,v in enumerate(p):
    skip={i}|adj[i]|{k for j in adj[i] for k in adj[j]};hits=[(distance,j) for _,j,distance in tree.find_n(v,32) if j not in skip]
    if hits:
        distance,j=min(hits)
        if distance<.003:near.append({'id':i,'other':j,'distance_m':distance,'world':list(v)})
areas=[]
for face in mesh.polygons:
    origin=p[face.vertices[0]];areas.append(sum((p[face.vertices[j]]-origin).cross(p[face.vertices[j+1]]-origin).length*.5 for j in range(1,len(face.vertices)-1)))
report={'rest_control_edge_min_m':min(lengths),'rest_control_edge_median_m':statistics.median(lengths),'rest_faces_below_1e_10_square_m':sum(a<1e-10 for a in areas),'near_non_two_hop_vertex_pairs_below_3mm':near,'scope':'Diagnostic source-evaluated initial control sheet density; nearest-vertex and triangle-fan area sampling, not complete self-intersection certification.'}
(out/'pattern-inspection.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('PATTERN_INSPECTION',report['rest_control_edge_min_m'],report['rest_control_edge_median_m'],report['rest_faces_below_1e_10_square_m'],len(near),flush=True)
