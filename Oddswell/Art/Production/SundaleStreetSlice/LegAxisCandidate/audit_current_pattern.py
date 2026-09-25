"""Measure the current sewn-short controls before replacing the upper pattern."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parent
source=root/'LegAxis.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='EA9524588054A81A69D5C7FC4FDC7B956DFB318DC5D9BDA4C687E22F2CFB1C4C'
bpy.ops.wm.open_mainfile(filepath=str(source))
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
assert len(pants.data.vertices)==7198

def world(index):return pants.matrix_world@pants.data.vertices[index].co
def length(indices):
    points=[world(index) for index in indices]
    return sum((b-a).length for a,b in zip(points,points[1:]))
def rounded(point):return [round(v,6) for v in point]

rings=[]
for k in range(17):
    base=k*80
    points=[world(base+j) for j in range(80)]
    front=length([base+j for j in range(41)])
    back=length([base+j for j in range(40,80)]+[base])
    rings.append({'row':k,'mean_height_m':round(sum(p.z for p in points)/80,6),
                  'front_arc_m':round(front,6),'back_arc_m':round(back,6),
                  'circumference_m':round(front+back,6),
                  'x_range_m':[round(min(p.x for p in points),6),round(max(p.x for p in points),6)],
                  'y_range_m':[round(min(p.y for p in points),6),round(max(p.y for p in points),6)]})

gusset=[]
for station in range(39):
    left=world(1360+2*station)
    right=world(1361+2*station)
    gusset.append({'station':station,'center_m':rounded((left+right)/2),
                   'span_m':round((right-left).length,6)})

hem=[]
for side,offset in (('left',1438),('right',4318)):
    indices=[offset+j for j in range(80)]
    points=[world(index) for index in indices]
    center=sum(points,Vector())/80
    hem.append({'side':side,'center_m':rounded(center),
                'perimeter_m':round(length(indices+[indices[0]]),6),
                'x_range_m':[round(min(p.x for p in points),6),round(max(p.x for p in points),6)],
                'y_range_m':[round(min(p.y for p in points),6),round(max(p.y for p in points),6)]})

layout={'source_sha256':'EA9524588054A81A69D5C7FC4FDC7B956DFB318DC5D9BDA4C687E22F2CFB1C4C',
        'mesh':pants.name,'vertices':len(pants.data.vertices),'faces':len(pants.data.polygons),
        'upper_ring_rows':17,'vertices_per_ring':80,
        'front_panel_columns':'0..40','back_panel_columns':'40..79,0',
        'side_seam_columns':[0,40],
        'paired_gusset_vertex_range':[1360,1437],
        'leg_tube_start_vertices':{'left':1438,'right':4318},
        'leg_tube_control_rows':36,'rings':rings,'gusset':gusset,'leg_openings':hem}
legs=bpy.data.objects['Character | anatomical legs']
leg_points=[legs.matrix_world@vertex.co for vertex in legs.data.vertices]
layout['exposed_leg_mesh']={'vertices':len(leg_points),'faces':len(legs.data.polygons),
    'ranges_m':{axis:[round(min(p[i] for p in leg_points),6),round(max(p[i] for p in leg_points),6)] for i,axis in enumerate(('x','y','z'))},
    'cross_sections':[]}
for height in (.25,.35,.45,.50,.55,.60,.65):
    band=[p for p in leg_points if abs(p.z-height)<.006]
    for side in ('left','right'):
        pts=[p for p in band if (p.x<-.75)==(side=='left')]
        if pts:
            layout['exposed_leg_mesh']['cross_sections'].append({'side':side,'height_m':height,
                'count':len(pts),'center_xy_m':[round(sum(p[i] for p in pts)/len(pts),6) for i in (0,1)],
                'x_range_m':[round(min(p.x for p in pts),6),round(max(p.x for p in pts),6)],
                'y_range_m':[round(min(p.y for p in pts),6),round(max(p.y for p in pts),6)]})
(root/'CurrentPatternLayout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
print('CURRENT_PATTERN_LAYOUT_PASS',rings[0],rings[-1],hem,flush=True)
