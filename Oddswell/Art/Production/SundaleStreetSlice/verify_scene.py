"""Check the saved artifact in a fresh Blender process without rendering."""
import bpy
import bmesh
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
scene=bpy.context.scene
bpy.context.view_layer.update()
packed=[image for image in bpy.data.images if image.source=='FILE' and image.packed_file]
assert len(packed)==24
assert not [image.name for image in bpy.data.images if image.source=='FILE' and not image.packed_file],'Unpacked source image'
assert scene.camera.name=='CAM | gameplay street'
if '--draft' not in sys.argv:
    assert all(bpy.data.objects.get('CAM | '+name) for name in ('Court_and_Arena','Architecture_Detail','Character_Detail','Landscape_Detail','Character_ThreeQuarter','Head_Front','Head_Profile'))
assert scene['flat_court_paint'] and scene['clothing_details_posed']
paint=[obj for obj in scene.objects if obj.name.startswith('Court | ') and obj.type=='CURVE']
assert paint and all(obj.dimensions.z<.001 for obj in paint)
head=bpy.data.objects['Character | anatomical head']
surface_vertices={i for polygon in head.data.polygons for i in polygon.vertices}
assert scene.get('human_head_refinement') and head.get('anatomical_source')
assert surface_vertices and all(head.data.vertices[i].co.z>1.54 and abs(head.data.vertices[i].co.x+.75)<(.065 if head.data.vertices[i].co.z<1.59 else .15) for i in surface_vertices),'Head/neck crop extends outside collar'
bm=bmesh.new();bm.from_mesh(head.data)
head_boundary_edges=sum(edge.is_boundary for edge in bm.edges)
assert head_boundary_edges==0
assert all(edge.is_manifold for edge in bm.edges),'Non-manifold anatomical head'
bm.free()
for side in ('l','r'):
    eye=bpy.data.objects.get('Character | eye '+side)
    assert eye is not None and bpy.data.objects.get('Character | iris '+side) and bpy.data.objects.get('Character | pupil '+side)
    bm=bmesh.new();bm.from_mesh(eye.data)
    assert all(edge.is_manifold for edge in bm.edges),'Open eyeball surface'
    bm.free()
assert all(bpy.data.objects.get('Character | eyebrow '+str(side)) for side in (-1,1))
depsgraph=bpy.context.evaluated_depsgraph_get()
sole_min=min((obj.evaluated_get(depsgraph).matrix_world@v.co).z for obj in scene.objects if obj.name.startswith('Character | sneaker sole') for v in obj.evaluated_get(depsgraph).data.vertices)
assert abs(sole_min-.051)<.0002,sole_min
def assert_connected(obj):
    adj=[set() for _ in obj.data.vertices]
    for edge in obj.data.edges:
        a,b=edge.vertices;adj[a].add(b);adj[b].add(a)
    visited={0};pending=[0]
    while pending:
        for neighbor in adj[pending.pop()]-visited:
            visited.add(neighbor);pending.append(neighbor)
    assert len(visited)==len(adj),'Disconnected garment: '+obj.name
pants=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Character | shorts leg')]
assert len(pants)==1
assert_connected(pants[0])
bm=bmesh.new();bm.from_mesh(pants[0].data)
shorts_boundary_edges=sum(edge.is_boundary for edge in bm.edges)
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges),'Non-manifold shorts'
boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in boundary),'Broken garment boundary'
shorts_openings=0
while boundary:
    shorts_openings+=1;pending=[boundary.pop()]
    while pending:
        vertex=pending.pop()
        for edge in vertex.link_edges:
            other=edge.other_vert(vertex)
            if edge.is_boundary and other in boundary:
                boundary.remove(other);pending.append(other)
assert shorts_openings==3,'Expected open waist and two leg hems'
assert len(bm.verts)-len(bm.edges)+len(bm.faces)==-1,'Expected three garment openings'
bm.free()
assert scene.get('continuous_jacket')
assert_connected(bpy.data.objects['Character | tailored slate jacket'])
assert scene.get('character_landscape_development')
trees=[o for o in scene.objects if o.name.startswith('Tree | mature Sundale')]
tree_meshes=len({o.data.as_pointer() for o in trees})
assert len(trees)==13 and tree_meshes==3
assert {o['growth_variant'] for o in trees}=={0,1,2}
assert all(o.get('raised_clear_trunk') for o in trees)
assert all(any('island_tree_01_leaves' in m.name for m in o.data.materials if m) for o in trees)
result={'result':'PASS','packed_texture_maps':len(packed),'cameras':sum(o.type=='CAMERA' for o in scene.objects),'court_paint_max_thickness_m':max(obj.dimensions.z for obj in paint),'collar_stray_faces':0,'head_boundary_edges':head_boundary_edges,'stance_sole_min_z_m':sole_min,'shorts_surface_components':1,'jacket_surface_components':1,'mature_tree_instances':len(trees),'shared_tree_meshes':tree_meshes,'mesh_objects':sum(obj.type=='MESH' for obj in scene.objects),'native_scene_objects':len(scene.objects),'runtime_claim':False}
result['shorts_boundary_edges']=shorts_boundary_edges
result['shorts_openings']=shorts_openings
result['anatomical_head']='Closed source-derived head and fitted neck; paired closed eyes, irises, pupils and brows'
if '--draft' not in sys.argv:(ROOT/'cold-reopen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_COLD_CHECK_PASS',json.dumps(result))
