"""Draft four new, welded shorts panels around the retained walking stance."""
import ast
import bpy
import bmesh
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out = Path(__file__).resolve().parent
root = Path(__file__).resolve().parents[5]
source = root / 'Oddswell/Art/Production/SundaleStreetSlice/BodyFlowCandidate/BodyFlow.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='13B5DE6E9BA2471F2A19F538B806FB05C052B35E0CC50D56CD65E5178E82B18A'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
pants = bpy.data.objects['Character | shorts leg continuous tailoring']
old = pants.data
world, inverse = pants.matrix_world, pants.matrix_world.inverted()
points = [world @ vertex.co for vertex in old.vertices]
materials = list(old.materials)
flow = bpy.data.objects['Body flow | stance blend']
functions = ast.parse((source.parent / 'build.py').read_text())
context = {'math': math, 'Vector': Vector, 'center': Vector((-.75, -2.4, .88))}
exec(compile(ast.Module(body=[node for node in functions.body if isinstance(node, ast.FunctionDef) and node.name in ('smooth', 'band', 'warp')], type_ignores=[]), 'body-flow-functions', 'exec'), context)
smooth, warp = context['smooth'], context['warp']

def unwarp(p):
    q = p.copy()
    for _ in range(24):
        q += p - warp(q)
    assert (warp(q) - p).length < .000001
    return q

def ring(offset, station):
    a = math.floor(station)
    return points[offset + a % 80].lerp(points[offset + (a + 1) % 80], station - a)

def bezier(a, b, c, d, t):
    return a * (1-t)**3 + b * (3*t*(1-t)**2) + c * (3*t*t*(1-t)) + d*t**3

# Measure original detail clearance before replacing the underlying surface.
names = [obj.name for obj in scene.objects if obj.name.startswith('Character | ') and
         any(token in obj.name for token in ('back pocket', 'pocket mouth', 'shorts leg hem', 'shorts side', 'shorts fly', 'shorts waistband'))]
oldtree = BVHTree.FromObject(pants, bpy.context.evaluated_depsgraph_get())
details = {}
for name in names:
    obj = bpy.data.objects[name]
    values = ([v.co.copy() for v in obj.data.vertices] if obj.type == 'MESH' else
              [Vector(p.co[:3]) for s in obj.data.splines for p in s.points])
    record = []
    for value in values:
        local = inverse @ (obj.matrix_world @ value)
        hit, normal, _, distance = oldtree.find_nearest(local)
        rear_hit = None
        if 'pocket' in name:
            p = obj.matrix_world @ value
            start = Vector((p.x, -3, p.z))
            rear_hit, _, _, _ = oldtree.ray_cast(inverse @ start, (inverse.to_3x3() @ Vector((0,1,0))).normalized())
        record.append((value, max(.0008, (local - hit).dot(normal)),
                       (world @ rear_hit).y - (obj.matrix_world @ value).y if rear_hit is not None else None))
    details[name] = record
del oldtree

cols = 40
rows = [0, .02, .04, .06, .08, .10, .13, .16, .19, .22, .25, .28,
        .31, .34, .37, .40, .43, .46, .49, .50, .53, .56, .60, .64,
        .68, .72, .76, .80, .84, .88, .92, .96, 1]
vc = .50
saddle = Vector((-.729, -2.390, .746))
vertices, faces, uvfaces, weld = [], [], [], {}
panels = {}
for side in ('left', 'right'):
    for half in ('front', 'rear'):
        left, front = side == 'left', half == 'front'
        hem_offset = 1438 if left else 4318
        hem_start = 40 if left else 0
        hem_sign = (-1 if front else 1) if left else (1 if front else -1)
        waist_start = 40 if left else 0
        waist_sign = hem_sign
        H = lambda u: ring(hem_offset, hem_start + hem_sign * 40*u)
        W = lambda u: ring(1280, waist_start + waist_sign * 20*u)
        h0, h1, w0, w1 = H(0), H(1), W(0), W(1)
        # Side seam rises along the thigh, with a shallow hip rather than an inflated ring.
        hip = Vector((-.914 if left else -.548, -2.406 if left else -2.375, .812))
        S = lambda v: bezier(h0, h0.lerp(hip, .70), hip.lerp(w0, .18), w0, v)
        def I(v):
            if v <= vc:
                t = v / vc
                return bezier(h1, h1 + Vector((0, 0, .053)),
                              saddle + Vector((-.012 if left else .012, -.012 if left else .012, -.041)), saddle, t)
            t = (v-vc)/(1-vc)
            outward = .062 if front else -.076
            return bezier(saddle, saddle + Vector((0, outward, .035)),
                          w1 + Vector((0, -.006 if front else .006, -.044)), w1, t)
        grid = []
        for row, v in enumerate(rows):
            line = []
            for col in range(cols+1):
                u = col/cols
                p = ((1-v)*H(u) + v*W(u) + (1-u)*S(v) + u*I(v)
                     - ((1-u)*(1-v)*h0 + u*(1-v)*h1 + (1-u)*v*w0 + u*v*w1))
                # Keep existing hem/facing registration, fade to the new four-panel pattern.
                blend = smooth((v-.10)/.21)
                if blend < 1:
                    k = min(35, v/.02)
                    a = math.floor(k)
                    legacy = ring(hem_offset + 80*a, hem_start + hem_sign*40*u)
                    if a < 35:
                        legacy = legacy.lerp(ring(hem_offset+80*(a+1), hem_start+hem_sign*40*u), k-a)
                    p = legacy.lerp(p, blend)
                if col == 0:
                    token = ('side', side, row)
                elif col == cols and v == vc:
                    token = ('saddle',)
                elif col == cols and v < vc:
                    token = ('inseam', side, row)
                elif col == cols:
                    token = ('center', half, row)
                else:
                    token = (side, half, row, col)
                if token not in weld:
                    weld[token] = len(vertices)
                    vertices.append(inverse @ p)
                index = weld[token]
                assert (world @ vertices[index]-p).length < 1e-5, token
                line.append(index)
            grid.append(line)
        panels[side+'_'+half] = grid
        island = (0 if left else 1) + (0 if front else 2)
        for row in range(len(rows)-1):
            for col in range(cols):
                faces.append((grid[row][col],grid[row][col+1],grid[row+1][col+1],grid[row+1][col]))
                uvfaces.append([((island % 2 + c/cols)*.48+.02, (island//2 + rows[r])*.48+.02)
                                for r,c in ((row,col),(row,col+1),(row+1,col+1),(row+1,col))])

mesh = bpy.data.meshes.new('Four cut cotton panels | welded rise and inseams')
mesh.from_pydata(vertices, [], faces)
mesh.update()
bm = bmesh.new(); bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
if bm.calc_volume(signed=True) < 0: bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
bm.to_mesh(mesh); bm.free()
for material in materials: mesh.materials.append(material)
for polygon in mesh.polygons: polygon.use_smooth = True
uv = mesh.uv_layers.new(name='Four cut cotton panels')
# UVs are associated by vertex identity, surviving the outward winding correction.
for polygon, ids, coords in zip(mesh.polygons, faces, uvfaces):
    by_id = dict(zip(ids,coords))
    for loop in polygon.loop_indices: uv.data[loop].uv = by_id[mesh.loops[loop].vertex_index]
pants.data = mesh
for group in list(pants.vertex_groups): pants.vertex_groups.remove(group)
drafted=[v.co.copy() for v in mesh.vertices]
# Fit a broad displacement field to the actual supports before any cloth settle.
# Moving complete sewn panels preserves the new saddle topology.
supports=[]
for name in ('anatomical legs', 'posed pelvic fitting support'):
    obj=bpy.data.objects['Character | '+name]
    supports.append((name,obj,BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())))
neighbors=[set() for _ in mesh.vertices]
for edge in mesh.edges:
    a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
maximum_fit=0
for iteration in range(10):
    deltas=[]
    for vertex in mesh.vertices:
        p=world@vertex.co
        delta=Vector()
        for name,obj,body in supports:
            if name=='anatomical legs' and not .625<p.z<.714: continue
            if name=='posed pelvic fitting support' and not .696<p.z<.888: continue
            q=obj.matrix_world.inverted()@p
            hit,normal,_,distance=body.find_nearest(q)
            if name=='anatomical legs' and normal.z>.85: continue
            gap=(q-hit).dot(normal)
            if gap<.009:
                correction=obj.matrix_world.to_3x3()@(normal*(.009-gap))
                if correction.length>delta.length: delta=correction
        deltas.append(delta)
    if iteration<7:
        for _ in range(3):
            deltas=[d*.55 + sum((deltas[j] for j in neighbors[i]),Vector())*(.45/len(neighbors[i])) for i,d in enumerate(deltas)]
    for vertex,delta in zip(mesh.vertices,deltas):
        maximum_fit=max(maximum_fit,delta.length)
        vertex.co+=inverse.to_3x3()@delta
    mesh.update()
print('NEW_PANEL_BODY_FIT',maximum_fit,flush=True)
fitted=[v.co.copy() for v in mesh.vertices]

# Keep the attached waist and original hem facings while the new body panels settle.
pin=pants.vertex_groups.new(name='Four panel attached waist and hems')
for vertex in mesh.vertices:
    z=(world@vertex.co).z
    weight=max(smooth((z-.871)/.020),1-smooth((z-.624)/.035))
    if weight>0: pin.add([vertex.index],weight,'REPLACE')
collision=[]
for _,obj,_ in supports:
    modifier=obj.modifiers.new('Four panel cloth contact','COLLISION')
    obj.collision.thickness_outer=.003
    collision.append((obj,modifier))
cloth=pants.modifiers.new('Four panel cotton gravity','CLOTH')
bpy.context.view_layer.objects.active=pants
while list(pants.modifiers).index(cloth)>0: bpy.ops.object.modifier_move_up(modifier=cloth.name)
s=cloth.settings;s.quality=10;s.mass=.20;s.air_damping=5
s.tension_stiffness=28;s.compression_stiffness=28;s.shear_stiffness=14;s.bending_stiffness=.65
s.vertex_group_mass=pin.name;s.pin_stiffness=1
c=cloth.collision_settings;c.use_collision=True;c.distance_min=.003
c.use_self_collision=True;c.self_distance_min=.002;c.collision_quality=4
cloth.point_cache.frame_start=1;cloth.point_cache.frame_end=35
for frame in range(1,36):
    scene.frame_set(frame);bpy.context.view_layer.update()
    if frame%10==0: print('FOUR_PANEL_CLOTH_FRAME',frame,flush=True)
bpy.ops.object.modifier_apply(modifier=cloth.name)
for obj,modifier in collision: obj.modifiers.remove(modifier)
scene.frame_set(1)
gravity=[v.co.copy() for v in mesh.vertices]
legs=bpy.data.objects['Character | anatomical legs']
leg_tree=BVHTree.FromObject(legs,bpy.context.evaluated_depsgraph_get())
for _ in range(5):
    for vertex in mesh.vertices:
        p=world@vertex.co
        if not .626<p.z<.714: continue
        q=legs.matrix_world.inverted()@p
        hit,normal,_,distance=leg_tree.find_nearest(q)
        gap=(q-hit).dot(normal)
        if gap<.009 and normal.z<.85:
            vertex.co += inverse.to_3x3()@(legs.matrix_world.to_3x3()@(normal*(.009-gap)))
    mesh.update()
before_fillet=[world@v.co for v in mesh.vertices]
positions=[p.copy() for p in before_fillet]
for _ in range(14):
    updated=[]
    for i,p in enumerate(positions):
        radius=((p.x+.729)/.026)**2+((p.y+2.371)/.058)**2+((p.z-.756)/.045)**2
        factor=.5*(1-smooth(radius))
        average=sum((positions[j] for j in neighbors[i]),Vector())/len(neighbors[i])
        updated.append(p.lerp(average,factor))
    positions=updated
for vertex,p in zip(mesh.vertices,positions): vertex.co=inverse@p
fillet=max((a-b).length for a,b in zip(before_fillet,positions))
print('CROTCH_FILLET_MAXIMUM_M',fillet,flush=True)
for modifier in pants.modifiers:
    if modifier.type=='SOLIDIFY':
        modifier.solidify_mode='NON_MANIFOLD'
        modifier.nonmanifold_thickness_mode='CONSTRAINTS'
        modifier.thickness=.001
        modifier.thickness_clamp=1.
        modifier.use_thickness_angle_clamp=True
vertices=[v.co.copy() for v in mesh.vertices]
for name,values in (('Four panel drafted',drafted),('Four panel collision fit',fitted),('Four panel gravity result',gravity)):
    attr=mesh.attributes.new(name=name,type='FLOAT_VECTOR',domain='POINT')
    for value,p in zip(attr.data,values): value.vector=p
basis = pants.shape_key_add(name='Basis')
previous = pants.shape_key_add(name='Previous torso hip stance')
attribute = mesh.attributes.new(name='Before torso hip flow', type='FLOAT_VECTOR', domain='POINT')
for p, key, attr in zip(vertices,previous.data,attribute.data):
    key.co = inverse @ unwarp(world @ p); attr.vector = key.co
driver = previous.driver_add('value').driver
variable = driver.variables.new(); variable.name='flow'; variable.type='SINGLE_PROP'
variable.targets[0].id=flow; variable.targets[0].data_path='["flow"]'; driver.expression='1-flow'
bpy.context.view_layer.update()

tree = BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
for name, record in details.items():
    obj = bpy.data.objects[name]
    transform = obj.matrix_world.inverted()
    values = []
    for value, offset, rear_offset in record:
        local = inverse @ (obj.matrix_world @ value)
        if rear_offset is not None:
            p=obj.matrix_world@value
            start=Vector((p.x,-3,p.z))
            hit,_,_,_=tree.ray_cast(inverse@start,(inverse.to_3x3()@Vector((0,1,0))).normalized())
            assert hit is not None,(name,list(p))
            p.y=(world@hit).y-rear_offset
            values.append(transform@p)
        else:
            hit, normal, _, distance = tree.find_nearest(local)
            values.append(transform @ (world @ (hit + normal * offset)))
    if obj.type == 'MESH':
        for vertex,p in zip(obj.data.vertices, values): vertex.co = p
    else:
        for point,p in zip((p for s in obj.data.splines for p in s.points),values): point.co=(*p,point.co.w)
    keys = obj.data.shape_keys
    if keys:
        for key in keys.key_blocks:
            for point,p in zip(key.data,values):
                point.co = transform @ unwarp(obj.matrix_world @ p) if key.name == 'Previous torso hip stance' else p
        retained=obj.data.attributes.get('Before torso hip flow') if obj.type=='MESH' else None
        if retained:
            for value,p in zip(retained.data,keys.key_blocks['Previous torso hip stance'].data):value.vector=p.co
    obj.data.update_tag()
del tree
scene['four_panel_shorts_study'] = True
scene['four_panel_shorts_saddle_m'] = list(saddle)
scene['four_panel_shorts_controls'] = len(vertices)
scene['four_panel_shorts_crotch_fillet_maximum_m'] = fillet
scene['four_panel_shorts_gravity_frames'] = 35
scene['four_panel_shorts_maximum_body_fit_m'] = maximum_fit
scene['four_panel_shorts_maximum_gravity_motion_m'] = max((a-b).length for a,b in zip(fitted,gravity))
scene['four_panel_shorts_maximum_final_clearance_adjustment_m'] = max((a-b).length for a,b in zip(vertices,gravity))
scene['previous_cotton_drape_frames']=scene['cotton_drape_frames']
scene['previous_cotton_drape_maximum_delta_m']=scene['cotton_drape_maximum_delta_m']
scene['cotton_drape_frames']=scene['four_panel_shorts_gravity_frames']
scene['cotton_drape_maximum_delta_m']=scene['four_panel_shorts_maximum_gravity_motion_m']
scene['four_panel_shorts_source'] = str(source.relative_to(root))
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'FourPanelCotton.blend'),compress=True)
(out/'panel-layout.json').write_text(json.dumps({'panels':panels,'rows':rows,'saddle':list(saddle)},indent=2))
print('FOUR_PANEL_SAVED',len(vertices),len(faces),names,flush=True)
