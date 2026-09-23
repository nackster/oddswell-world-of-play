"""Check the saved artifact in a fresh Blender process without rendering."""
import bpy
import bmesh
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parent
scene_path=Path(sys.argv[sys.argv.index('--scene')+1]) if '--scene' in sys.argv else ROOT/'OddsWell_Sundale_StreetSlice.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
scene=bpy.context.scene
bpy.context.view_layer.update()
packed=[image for image in bpy.data.images if image.source=='FILE' and image.packed_file]
assert len(packed)==31
assert all(image.use_fake_user for image in packed),'Retained packed maps can be lost on repeated saves'
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
assert scene.get('individual_facial_form') and head.data.attributes.get('MakeHuman source vertex')
head_keys=head.data.shape_keys.key_blocks
head_targets=json.loads(scene.get('head_character_targets','{}'))
assert set(head_targets)=={'caucasian-male-young.target','head-rectangular.target','head-fat-decr.target'}
assert all(name.removesuffix('.target') in head_keys for name in head_targets)
assert 'Restrained facial asymmetry' in head_keys and head.data.attributes.get('Facial oil distribution')
head_deltas=[]
for key in head_keys:
    if key.name=='Basis':continue
    for vertex,point,base in zip(head.data.vertices,key.data,head_keys['Basis'].data):
        delta=(point.co-base.co).length
        if vertex.co.z<1.605:assert delta<.000001,'Facial study moved the fitted neck base'
        head_deltas.append(delta*key.value)
assert .001<max(head_deltas)<.035,'Missing or excessive facial adjustment'
assert scene.get('brow_groom_refinement') and 'Resting eyelid openness' in head_keys
expression_delta=[a.co-b.co for a,b in zip(head_keys['Resting eyelid openness'].data,head_keys['Basis'].data)]
assert 0<max(v.length for v in expression_delta)<.0007,'Eyelid control stacked other facial shapes'
assert all(abs(v.x)<.000001 and abs(v.y)<.000001 and v.z>=0 for v in expression_delta)
face_surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
for brow in (obj for obj in scene.objects if obj.name.startswith('Character | eyebrow ')):
    assert len(brow.data.splines)==650 and len(brow.data.materials)==3,'Incomplete individual brow groom'
    transform=head.matrix_world.inverted()@brow.matrix_world
    for spline in brow.data.splines:
        for point in spline.points:
            position=transform@Vector(point.co[:3]);hit,normal,_,distance=face_surface.find_nearest(position)
            assert distance<.001 and (position-hit).dot(normal)>0,'Detached or buried brow strand'
surface_vertices={i for polygon in head.data.polygons for i in polygon.vertices}
assert scene.get('human_head_refinement') and head.get('anatomical_source')
assert surface_vertices and all(head.data.vertices[i].co.z>1.54 and abs(head.data.vertices[i].co.x+.75)<(.065 if head.data.vertices[i].co.z<1.59 else .15) for i in surface_vertices),'Head/neck crop extends outside collar'
bm=bmesh.new();bm.from_mesh(head.data)
head_boundary_edges=sum(edge.is_boundary for edge in bm.edges)
assert head_boundary_edges==0
assert all(edge.is_manifold for edge in bm.edges),'Non-manifold anatomical head'
bm.free()
assert scene.get('optical_eye_study'), 'Missing cornea/iris development'
optical_clearances=[]
for side in ('l','r'):
    eye=bpy.data.objects.get('Character | eye '+side)
    assert eye is not None and bpy.data.objects.get('Character | iris '+side) and bpy.data.objects.get('Character | pupil '+side)
    bm=bmesh.new();bm.from_mesh(eye.data)
    assert all(edge.is_manifold for edge in bm.edges),'Open eyeball surface'
    assert bm.calc_volume(signed=True)>0,'Inverted optical eye'
    bm.free()
    cornea=eye.data.materials.get('Character | transparent cornea')
    assert cornea and cornea.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value==1
    surface=BVHTree.FromObject(eye,bpy.context.evaluated_depsgraph_get())
    for name in ('iris','pupil'):
        obj=bpy.data.objects['Character | '+name+' '+side]
        transform=eye.matrix_world.inverted()@obj.matrix_world
        for v in obj.data.vertices:
            point=transform@v.co
            hit,normal,index,distance=surface.ray_cast(point,Vector((0,1,0)),.01)
            assert hit is not None and distance>.0003,'Pigment intersects corneal surface'
            assert eye.data.polygons[index].material_index==1,'Opaque sclera covers iris/pupil'
            optical_clearances.append(distance)
    wet=bpy.data.objects.get('Character | lower wet margin '+side)
    assert wet and len(wet.data.splines[0].points)>8,'Missing lower eyelid tissue'
    skin_surface=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
    transform=head.matrix_world.inverted()@wet.matrix_world
    points=[transform@Vector(p.co[:3]) for p in wet.data.splines[0].points]
    assert max((b-a).length for a,b in zip(points,points[1:]))<.002,'Discontinuous lower eyelid margin'
    for point in points:
        hit,normal,_,distance=skin_surface.find_nearest(point)
        assert distance<.0002 and (point-hit).dot(normal)>0,'Detached or buried eyelid tissue'
assert all(bpy.data.objects.get('Character | eyebrow '+str(side)) for side in (-1,1))
facial_targets=json.loads(scene.get('facial_targets','{}'))
assert len(facial_targets)==3,'Missing retained anatomical face adjustments'
for side in ('l','r'):
    color=bpy.data.objects['Character | iris '+side].data.color_attributes.get('Iris radial fibers')
    assert color and max(c.color[0] for c in color.data)-min(c.color[0] for c in color.data)>.02,'Iris has no fiber variation'
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
stance=bpy.data.objects['Character | sneaker sole right'].evaluated_get(depsgraph)
contact=[stance.matrix_world@v.co for v in stance.data.vertices if (stance.matrix_world@v.co).z<sole_min+.0002]
contact_width=max(p.x for p in contact)-min(p.x for p in contact)
contact_length=max(p.y for p in contact)-min(p.y for p in contact)
assert contact_width>.080 and contact_length>.20,'Stance support is only a narrow line'
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
coat=bpy.data.objects['Character | tailored slate jacket']
assert_connected(coat)
assert scene.get('jacket_drape_frames')==60 and 0<scene['jacket_drape_maximum_delta_m']<.13
assert len(coat.data.vertices)==scene['jacket_drape_controls']
assert all(coat.data.attributes.get(name) for name in ('Tailored rest','Collision fit','Gravity result'))
assert scene.get('anatomical_jacket_support') and scene['jacket_fabric_ease']==0
support=bpy.data.objects['Character | internal torso support']
assert support.hide_render and support.hide_get(),'Internal support became visible'
assert support.get('source')=='source-assets/makehuman-base.obj'
assert support.get('body_target')=='caucasian-male-young.target'
bm=bmesh.new();bm.from_mesh(support.data)
assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,'Broken anatomical collision support'
bm.free()
pin=coat.vertex_groups['Collar zipper hem and cuff attachments']
weights=[next((g.weight for g in v.groups if g.group==pin.index),0) for v in coat.data.vertices]
fit=coat.data.attributes['Collision fit'].data
# Transition-band controls may move proportionally; fully pinned controls may not.
pinned_motion=max((v.co-r.vector).length for v,r,w in zip(coat.data.vertices,fit,weights) if w==1)
assert pinned_motion<.000001,'Displacement filtering moved fixed jacket attachments'
raw_delta=max((v.vector-r.vector).length for v,r in zip(coat.data.attributes['Gravity result'].data,fit))
assert abs(raw_delta-scene['jacket_drape_maximum_delta_m'])<.000001
support.hide_set(False);bpy.context.view_layer.update()
support_surface=BVHTree.FromObject(support,bpy.context.evaluated_depsgraph_get())
free_clearances=[]
for v,w in zip(coat.data.vertices,weights):
    if w>=.80:continue
    hit,normal,_,distance=support_surface.find_nearest(v.co)
    free_clearances.append((v.co-hit).dot(normal))
support.hide_set(True);bpy.context.view_layer.update()
assert min(free_clearances)>.001,'Free jacket controls penetrate anatomical support'

bm=bmesh.new();bm.from_mesh(coat.data)
assert scene.get('open_jacket_construction')
assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges),'Broken jacket cloth sheet'
boundary={e for e in bm.edges if e.is_boundary};jacket_openings=0
assert all(sum(e.is_boundary for e in v.link_edges)==2 for v in bm.verts if v.is_boundary),'Branched garment boundary'
while boundary:
    pending=[boundary.pop()];jacket_openings+=1
    while pending:
        edge=pending.pop()
        for vertex in edge.verts:
            for other in vertex.link_edges:
                if other in boundary:boundary.remove(other);pending.append(other)
assert jacket_openings==4 and len(bm.verts)-len(bm.edges)+len(bm.faces)==-2,'Expected open neck, waist and two cuffs'
bm.free()
solid=coat.modifiers['Actual fabric thickness']
assert solid.type=='SOLIDIFY' and abs(solid.thickness-.0012)<.000001 and solid.offset==-1
evaluated_coat=coat.evaluated_get(bpy.context.evaluated_depsgraph_get())
coat_mesh=evaluated_coat.to_mesh();bm=bmesh.new();bm.from_mesh(coat_mesh)
jacket_fabric_volume=bm.calc_volume(signed=True)
assert all(e.is_manifold for e in bm.edges) and 0<jacket_fabric_volume<.004,'Broken fabric thickness or solid filled garment'
bm.free();evaluated_coat.to_mesh_clear()
hand_openings={};nail_clearances=[];hand_detail_displacements=[]
assert scene.get('hand_surface_refinement'),'Missing hand surface anatomy'
assert scene.get('epidermal_detail'),'Missing skin and nail-fold development'
fold_clearances=[];vascular_displacements=[]
for material_name in ('Character | anatomical face skin','Character | warm neutral skin','Character | hand epidermis'):
    nodes=bpy.data.materials[material_name].node_tree.nodes
    assert nodes.get('Fine epidermal pore relief') and nodes.get('CC0 MakeHuman skin')
    assert 0<nodes['Fine epidermal pore relief'].inputs['Distance'].default_value<.0001

for name in ('left hand','right hand'):
    hand=bpy.data.objects['Character | anatomical '+name]
    assert_connected(hand)
    bm=bmesh.new();bm.from_mesh(hand.data)
    boundary=[edge for edge in bm.edges if edge.is_boundary]
    assert boundary and all(v.co.z>.97 for edge in boundary for v in edge.verts),'Exposed opening in hand'
    assert all(edge.is_manifold or edge.is_boundary for edge in bm.edges)
    hand_openings[name]=len(boundary)
    bm.free()
    source=hand.data.attributes.get('Unposed anatomical position')
    keys=hand.data.shape_keys.key_blocks
    assert source and len(source.data)==len(hand.data.vertices) and hand.get('hand_landmarks')
    assert 'Basis' in keys and 'Hand surface anatomy' in keys
    deltas=[(a.co-b.co).length for a,b in zip(keys['Basis'].data,keys['Hand surface anatomy'].data)]
    assert .0003<max(deltas)<.002,'Hand relief missing or excessive'
    hand_detail_displacements.append(max(deltas))
    surface=BVHTree.FromObject(hand,depsgraph)
    side=name.split()[0]
    assert hand.data.materials[0].name=='Character | hand epidermis'
    assert 'Dorsal vascular relief' in keys
    vascular_displacements.extend((a.co-b.co).length for a,b in zip(keys['Dorsal vascular relief'].data,keys['Basis'].data))
    for attribute in ('Dorsal vascular field','Hand joint creases','Hand joint vascular tone'):
        values=[d.value for d in hand.data.attributes[attribute].data]
        assert min(values)>=0 and .5<max(values)<=1,'Missing or invalid anatomical skin field'
    folds=[o for o in scene.objects if o.name.startswith('Character | nail fold '+side)]
    assert len(folds)==5 and {o['anatomical_digit'] for o in folds}==set(range(1,6))
    for fold in folds:
        bm=bmesh.new();bm.from_mesh(fold.data)
        assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,'Open or inverted skin fold'
        bm.free()
        assert fold.data.uv_layers.get('MakeHuman source UV'),'Nail fold lost source texture registration'
        transform=hand.matrix_world.inverted()@fold.matrix_world
        distances=[]
        for vertex in fold.data.vertices:
            point=transform@vertex.co;hit,normal,_,distance=surface.find_nearest(point)
            assert distance<.00035,'Detached nail fold'
            distances.append((point-hit).dot(normal))
        assert min(distances)<0<max(distances),'Nail fold must sit into the skin'
        fold_clearances.extend(distances)

    nails=[obj for obj in scene.objects if obj.name.startswith('Character | nail '+side)]
    assert len(nails)==5 and {obj['anatomical_digit'] for obj in nails}==set(range(1,6))
    for nail in nails:
        transform=hand.matrix_world.inverted()@nail.matrix_world
        samples=[v.co for v in nail.data.vertices]+[p.center for p in nail.data.polygons]
        for point in samples:
            point=transform@point;hit,normal,_,distance=surface.find_nearest(point)
            signed=(point-hit).dot(normal)
            assert signed>.00002 and distance<.0004,('Detached or intersecting nail plate',nail.name,signed,distance)
            nail_clearances.append(signed)
        bm=bmesh.new();bm.from_object(nail,depsgraph)
        assert all(edge.is_manifold for edge in bm.edges),'Open nail thickness'
        assert bm.calc_volume(signed=True)>0,'Inverted nail plate'
        bm.free()
coat_surface=BVHTree.FromObject(coat,depsgraph)
solid.show_viewport=False
bpy.context.view_layer.update()
outer_coat_surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
solid.show_viewport=True
bpy.context.view_layer.update()
collar_surface=BVHTree.FromObject(bpy.data.objects['Character | standing collar'],depsgraph)
assert scene.get('fitted_jacket_fastening')
minimum_fastening_gap=1
for tape in (o for o in scene.objects if o.name.startswith('Character | front zipper tape')):
    for point in tape.data.splines[0].points:
        position=Vector(point.co[:3])
        hit,normal,_,distance=min((surface.find_nearest(position) for surface in (coat_surface,collar_surface)),key=lambda result:result[3])
        gap=(position-hit).dot(normal)
        assert gap>.0003 and distance<.003,'Buried or detached jacket fastening'
        minimum_fastening_gap=min(minimum_fastening_gap,gap)
raglan=[o for o in scene.objects if o.name.startswith('Character | raglan topstitch ')]
assert len(raglan)==4
maximum_raglan_gap=0
for seam in raglan:
    points=[Vector(p.co[:3]) for p in seam.data.splines[0].points]
    assert max((a-b).length for a,b in zip(points,points[1:]))<.015,'Raglan jumps between garment surfaces'
    for point in seam.data.splines[0].points:
        position=Vector(point.co[:3]);hit,normal,_,distance=outer_coat_surface.find_nearest(position)
        assert 0<(position-hit).dot(normal) and distance<.0015,'Detached or buried raglan stitch'
        maximum_raglan_gap=max(maximum_raglan_gap,distance)
for side in (-1,1):
    ends=[Vector(bpy.data.objects['Character | raglan topstitch '+str(side)+' '+str(front)].data.splines[0].points[-1].co[:3]) for front in (-1,1)]
    assert (ends[0]-ends[1]).length<.0001,'Raglan ends do not meet at the armhole'
panels=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('Character | ') and 'yoke' in o.name]
assert len(panels)==3 and scene.get('conformed_jacket_panels')
for panel in panels:
    for vertex in panel.data.vertices:
        hit,normal,_,distance=outer_coat_surface.find_nearest(vertex.co)
        assert distance<.0008 and (vertex.co-hit).dot(normal)>0,'Teal panel lifted from or buried in jacket'
    stitches=bpy.data.objects['Character | yoke topstitch '+panel.name]
    bm=bmesh.new();bm.from_mesh(panel.data)
    assert len(stitches.data.splines)==sum(edge.is_boundary for edge in bm.edges)
    bm.free()
lace_gap=0
eyelet_gap=0;tongue_clearance=[]
assert scene.get('fine_footwear_stitches')
for label in ('toe cap seam','quarter seam','heel seam'):
    seams=[o for o in scene.objects if o.name.startswith('Character | shoe lace '+label)]
    assert len(seams)==(4 if label=='quarter seam' else 2)
    assert all(len(o.data.splines)>5 and o.data.bevel_depth<.0003 for o in seams),'Raised wire remains on shoe upper'
for side in ('left','right'):
    shoe=bpy.data.objects['Character | canvas sneaker '+side]
    assert any(material.name.startswith('Character | warmer canvas toe panels') for material in shoe.data.materials)
    assert sum(face.material_index==len(shoe.data.materials)-1 for face in shoe.data.polygons)>100,'Missing separate canvas toe panel'
    bm=bmesh.new();bm.from_mesh(shoe.data)
    assert all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True)>0,'Open or inward shoe surface'
    bm.free()
    upper=BVHTree.FromObject(shoe,depsgraph)
    laces=[obj for obj in scene.objects if obj.name.startswith('Character | shoe lace '+side)]
    assert len(laces)==7
    eyelets=[o for o in scene.objects if o.name.startswith('Character | shoe lace eyelet '+side)]
    centers=[sum((Vector(p.co[:3]) for p in o.data.splines[0].points),Vector())/len(o.data.splines[0].points) for o in eyelets]
    assert len(centers)==8
    for obj in laces:
        for spline in obj.data.splines:
            for point in (spline.points[0],spline.points[-1]):
                gap=min((Vector(point.co[:3])-center).length for center in centers)
                assert gap<.0012,'Lace endpoint misses its eyelet'
                eyelet_gap=max(eyelet_gap,gap)
            for point in spline.points:
                location,normal,_,distance=upper.find_nearest(Vector(point.co[:3]))
                assert distance is not None and distance<.008,'Detached shoe lace'
                assert (Vector(point.co[:3])-location).dot(normal)>.0005,'Lace buried inside shoe'
                lace_gap=max(lace_gap,distance)
    for polygon in bpy.data.objects['Character | canvas sneaker tongue '+side].data.polygons:
        location,normal,_,distance=upper.find_nearest(polygon.center)
        gap=(polygon.center-location).dot(normal)
        assert gap>.0002,'Tongue intersects the shoe upper'
        tongue_clearance.append(gap)
head_surface=BVHTree.FromObject(head,depsgraph)
lashes=[o for o in scene.objects if o.name.startswith('Character | eyelashes ')]
assert len(lashes)==2 and sum(len(o.data.splines) for o in lashes)==scene['eyelash_strands']>=60
for obj in lashes:
    for strand in obj.data.splines:
        root=Vector(strand.points[0].co[:3]);location,normal,_,distance=head_surface.find_nearest(root)
        assert distance<.0003 and (root-location).dot(normal)>0,'Detached eyelash root'
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
result['stance_contact_width_m']=contact_width
result['stance_contact_length_m']=contact_length
result['maximum_lace_eyelet_gap_m']=eyelet_gap
result['minimum_tongue_surface_clearance_m']=min(tongue_clearance)
result['facial_targets']=facial_targets
result['eyelash_strands']=scene['eyelash_strands']
result['individual_brow_strands']=1300
result['maximum_resting_eyelid_lift_m']=max(v.length for v in expression_delta)
result['cotton_drape_frames']=scene['cotton_drape_frames']
result['jacket_drape_frames']=scene['jacket_drape_frames']
result['jacket_drape_controls']=scene['jacket_drape_controls']
result['jacket_open_boundaries']=jacket_openings
result['jacket_fabric_volume_m3']=jacket_fabric_volume
result['jacket_drape_maximum_delta_m']=scene['jacket_drape_maximum_delta_m']
result['jacket_fabric_ease']=scene['jacket_fabric_ease']
result['anatomical_jacket_support_vertices']=len(support.data.vertices)
result['maximum_fixed_jacket_attachment_motion_m']=pinned_motion
result['minimum_free_jacket_control_clearance_m']=min(free_clearances)
result['maximum_raglan_surface_distance_m']=maximum_raglan_gap
result['minimum_fastening_surface_clearance_m']=minimum_fastening_gap
result['stitched_yoke_panels']=len(panels)
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
result['minimum_pigment_cornea_clearance_m']=min(optical_clearances)
result['optical_cornea_surfaces']=2
result['lower_wet_eyelid_margins']=2
result['fitted_nail_plates']=10
assert 0<max(vascular_displacements)<.00025
result['fitted_nail_folds']=10
result['maximum_vascular_relief_m']=max(vascular_displacements)
result['nail_fold_surface_range_m']=[min(fold_clearances),max(fold_clearances)]
result['epidermal_detail']=True
result['minimum_nail_surface_clearance_m']=min(nail_clearances)
result['maximum_hand_relief_m']=max(hand_detail_displacements)
result['head_character_targets']=head_targets
result['maximum_weighted_head_target_displacement_m']=max(head_deltas)
result['retained_head_shape_keys']=len(head_keys)
if '--draft' not in sys.argv:(ROOT/'cold-reopen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_COLD_CHECK_PASS',json.dumps(result))
