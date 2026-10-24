"""Measure the retained shorts ring and saddle control paths for a panel rebuild."""
import bpy
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
source = root/'CrewCut.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest().upper() == '974ADD328315034C3DD09C6C4393B825E47FFC994315366552446A313AE89EE5'
bpy.ops.wm.open_mainfile(filepath=str(source))
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
vertices = pants.data.vertices
assert len(vertices) == 17*80+2*39+2*36*80


def arc(indices):
    points = [pants.matrix_world @ vertices[i].co for i in indices]
    return sum((b-a).length for a, b in zip(points, points[1:]))


rows = []
for row in range(17):
    base = row*80
    points = [pants.matrix_world @ vertices[base+j].co for j in range(80)]
    front = arc([base+j for j in range(41)])
    rear = arc([base+j for j in range(40,80)]+[base])
    rows.append({'row': row, 'mean_height_m': round(sum(p.z for p in points)/80, 6),
                 'front_arc_m': round(front, 6), 'rear_arc_m': round(rear, 6),
                 'circumference_m': round(front+rear, 6)})

bridge = [pants.matrix_world @ vertices[i].co for i in range(17*80,17*80+2*39)]
gusset_widths = [(bridge[2*j+1]-bridge[2*j]).length for j in range(39)]
measure = {
    'source_sha256': '974ADD328315034C3DD09C6C4393B825E47FFC994315366552446A313AE89EE5',
    'mesh': pants.name,
    'upper_ring_rows': 17,
    'vertices_per_ring': 80,
    'front_panel_control_columns': '0..40',
    'rear_panel_control_columns': '40..79,0',
    'side_seam_columns': [0, 40],
    'paired_gusset_vertex_range': [17*80, 17*80+77],
    'gusset_station_count': 39,
    'gusset_width_range_m': [round(min(gusset_widths),6),round(max(gusset_widths),6)],
    'gusset_height_range_m': [round(min(p.z for p in bridge),6),round(max(p.z for p in bridge),6)],
    'rings': rows,
}
(root/'PatternLayout.json').write_text(json.dumps(measure, indent=2)+'\n', encoding='utf-8')
print('SHORTS_PATTERN_AUDIT_PASS', rows[0], rows[-1], flush=True)
