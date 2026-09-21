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
assert len(packed)==31
assert scene.get('source_skin_uvs') and scene.get('reference_upper_body_fit')
assert scene.get('body_refinement')
assert scene.get('articulated_walking_pose') and scene.get('photographic_fabric_maps')
assert scene.get('anatomical_finger_articulation')
assert scene.get('cotton_drape_frames')==40 and 0<scene['cotton_drape_maximum_delta_m']<.12
for obj in scene.objects:
    if obj.name.startswith('Character | anatomical '):
        uv=obj.data.uv_layers.get('MakeHuman source UV')
        assert uv is not None and len(uv.data)==len(obj.data.loops),'Missing anatomical source UVs'
        assert max(p.uv.x for p in uv.data)-min(p.uv.x for p in uv.data)>.01,'Collapsed skin UVs'
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
feet={}
for side in ('left','right'):
    obj=bpy.data.objects['Character | sneaker sole '+side].evaluated_get(depsgraph)
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    low=min(p.y for p in points);high=max(p.y for p in points)
    feet[side]={'min_z':min(p.z for p in points),'heel_min_z':min(p.z for p in points if p.y<low+.035),'toe_min_z':min(p.z for p in points if p.y>high-.035)}
assert abs(feet['right']['min_z']-.051)<.0002,'Forward stance foot is floating'
assert abs(feet['right']['heel_min_z']-feet['right']['toe_min_z'])<.001,'Stance sole is not flat'
assert feet['left']['heel_min_z']>feet['left']['toe_min_z']+.04,'Trailing heel is not raised'
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
hand_openings={}
for name in ('left hand','right hand'):
    hand=bpy.data.objects['Character | anatomical '+name]
    assert_connected(hand)
    bm=bmesh.new();bm.from_mesh(hand.data)
    boundary=[edge for edge in bm.edges if edge.is_boundary]
    assert boundary and all(v.co.z>.97 for edge in boundary for v in edge.verts),'Exposed opening in hand'
    assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges)
    hand_openings[name]=len(boundary)
    bm.free()
from mathutils.bvhtree import BVHTree
from mathutils import Vector
lace_gap=0
for side in ('left','right'):
    shoe=bpy.data.objects['Character | canvas sneaker '+side]
    bm=bmesh.new();bm.from_mesh(shoe.data)
    assert all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True)>0,'Open or inward shoe surface'
    bm.free()
    upper=BVHTree.FromObject(shoe,depsgraph)
    laces=[obj for obj in scene.objects if obj.name.startswith('Character | shoe lace '+side)]
    assert len(laces)==8
    for obj in laces:
        for spline in obj.data.splines:
            for point in spline.points:
                location,normal,_,distance=upper.find_nearest(Vector(point.co[:3]))
                assert distance is not None and distance<.008,'Detached shoe lace'
                assert (Vector(point.co[:3])-location).dot(normal)>.0005,'Lace buried inside shoe'
                lace_gap=max(lace_gap,distance)
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
result['skin_source_uvs']=True
result['reference_upper_body_fit']=True
result['hand_boundary_edges_under_sleeves']=hand_openings
result['maximum_lace_surface_distance_m']=lace_gap
result['foot_contact']=feet
result['cotton_drape_frames']=scene['cotton_drape_frames']
result['cotton_drape_maximum_delta_m']=scene['cotton_drape_maximum_delta_m']
skin_surface=BVHTree.FromObject(bpy.data.objects['Character | anatomical legs'],depsgraph)
hair=bpy.data.objects['Character | fine calf hair']
assert len(hair.data.splines)==scene['calf_hair_strands']==2600
for strand in list(hair.data.splines)[::50]:
    root=Vector(strand.points[0].co[:3])
    hit,normal,_,distance=skin_surface.find_nearest(root)
    assert distance<.0003 and (root-hit).dot(normal)>0,'Detached or buried body hair root'
result['calf_hair_strands']=len(hair.data.splines)
result['anatomical_finger_articulation']=True
garment_surface=BVHTree.FromObject(pants[0],depsgraph)
for seam in (o for o in scene.objects if o.name.startswith('Character | back pocket seam')):
    for point in seam.data.splines[0].points:
        hit,normal,_,distance=garment_surface.find_nearest(Vector(point.co[:3]))
        assert distance<.003,'Detached pocket stitch'
clearance=[]
for vertex in pants[0].evaluated_get(depsgraph).data.vertices:
    hit,normal,_,distance=skin_surface.find_nearest(vertex.co)
    if distance is not None and distance<.025 and vertex.co.z<.76:clearance.append((vertex.co-hit).dot(normal))
assert clearance and min(clearance)>-.0015,('Cloth intersects exposed thigh',min(clearance))
result['minimum_cloth_thigh_clearance_m']=min(clearance)
if '--draft' not in sys.argv:(ROOT/'cold-reopen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_COLD_CHECK_PASS',json.dumps(result))
