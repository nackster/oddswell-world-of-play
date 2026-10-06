"""Native fabric-thickness correction and a sewn knitted waist fit."""
import bpy,json,hashlib,math
from collections import Counter
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/HipSeatMotionCandidate/HipSeat.blend'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='9775f815af14570a673dc000ea9535c05ef35f06c6b0aeea1260a3105396cb20'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];band=bpy.data.objects['Character | ribbed waistband'];rig=bpy.data.objects['Walk study | native anatomical controls']
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY')
report={'source_sha256':'9775f815af14570a673dc000ea9535c05ef35f06c6b0aeea1260a3105396cb20','thickness_before':{'mode':solid.solidify_mode,'nonmanifold_thickness_mode':solid.nonmanifold_thickness_mode,'thickness_m':solid.thickness,'offset':solid.offset,'even_offset':solid.use_even_offset,'quality_normals':solid.use_quality_normals,'clamp':solid.thickness_clamp}}
solid.solidify_mode='EXTRUDE';solid.use_even_offset=False;solid.use_quality_normals=True;solid.thickness_clamp=0
report['thickness_after']={'mode':solid.solidify_mode,'thickness_m':solid.thickness,'offset':solid.offset,'even_offset':solid.use_even_offset,'reason':'Use bounded native normal extrusion instead of the constrained non-manifold shell solver; shell displacement is checked separately.'}
solid.show_viewport=False
sub=next(m for m in coat.modifiers if m.type=='SUBSURF');old_level=sub.levels;sub.levels=sub.render_levels
bpy.context.view_layer.update();ev=coat.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
points=[ev.matrix_world@v.co for v in mesh.vertices];counts=Counter(tuple(sorted((a,b))) for p in mesh.polygons for a,b in zip(p.vertices,(*p.vertices[1:],p.vertices[0])))
graph={}
for (a,b),count in counts.items():
    if count==1:graph.setdefault(a,set()).add(b);graph.setdefault(b,set()).add(a)
pending=set(graph);loops=[]
while pending:
    current=min(pending);loop=[]
    while current not in loop:
        loop.append(current);pending.discard(current);remaining=graph[current]-set(loop)
        if not remaining:break
        current=min(remaining)
    loops.append(loop)
assert len(loops)==4
opening=max(loops,key=lambda loop:sum((points[a]-points[b]).length for a,b in zip(loop,loop[1:]+loop[:1])))
opening=[points[i] for i in opening];ev.to_mesh_clear();sub.levels=old_level;solid.show_viewport=True
center=sum(opening,Vector())/len(opening);assert .80<center.z<1.05,('Wrong garment opening',list(center))
pants=bpy.data.objects['Character | shorts leg continuous tailoring'];pants_solid=next(m for m in pants.modifiers if m.type=='SOLIDIFY');pants_solid.show_viewport=False
bpy.context.view_layer.update();ev=pants.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());uv=mesh.uv_layers['Four cut cotton panels'];ids=set()
for poly in mesh.polygons:
    mean=sum(uv.data[i].uv.y for i in poly.loop_indices)/len(poly.loop_indices)
    top=.50 if mean<.50 else .98
    for i in poly.loop_indices:
        if abs(uv.data[i].uv.y-top)<1e-6:ids.add(mesh.loops[i].vertex_index)
lower_opening=[ev.matrix_world@mesh.vertices[i].co for i in ids];ev.to_mesh_clear();pants_solid.show_viewport=True
lower_center=sum(lower_opening,Vector())/len(lower_opening);lower_opening.sort(key=lambda p:math.atan2(p.y-lower_center.y,p.x-lower_center.x))
lower_projected=[Vector((p.x-lower_center.x,p.y-lower_center.y)) for p in lower_opening]
assert len(band.data.vertices)==13*384
world=band.matrix_world.copy();inverse=world.inverted();ps=[world@v.co for v in band.data.vertices]
centers=[sum(ps[k*384:(k+1)*384],Vector())/384 for k in range(13)]
axis=Vector((0,0,1));shape=band.shape_key_add(name='Continuous knitted waist fit');shape.value=1.;maximum=0
def cross(a,b):return a.x*b.y-a.y*b.x
projected=[Vector((p.x-center.x,p.y-center.y)) for p in opening]
for j in range(384):
    p=ps[12*384+j];radial=p-centers[-1];direction=Vector((radial.x,radial.y)).normalized();hits=[]
    for index,(a,b) in enumerate(zip(projected,projected[1:]+projected[:1])):
        edge=b-a;denom=cross(direction,edge)
        if abs(denom)<1e-10:continue
        distance=cross(a,edge)/denom;t=cross(a,direction)/denom
        if distance>0 and 0<=t<=1:hits.append((distance,index,t))
    assert hits,('Waist opening not radially traceable',j)
    _,index,t=min(hits);join=opening[index].lerp(opening[(index+1)%len(opening)],t)
    outward=Vector((direction.x,direction.y,0))
    lower_hits=[]
    for index,(a,b) in enumerate(zip(lower_projected,lower_projected[1:]+lower_projected[:1])):
        edge=b-a;denom=cross(direction,edge)
        if abs(denom)<1e-10:continue
        distance=cross(a,edge)/denom;t=cross(a,direction)/denom
        if distance>0 and 0<=t<=1:lower_hits.append((distance,index,t))
    assert lower_hits,('Shorts waist not radially traceable',j)
    _,index,t=min(lower_hits);lower=lower_opening[index].lerp(lower_opening[(index+1)%len(lower_opening)],t)+outward*.0004
    lower.z=min(lower.z+.0005,join.z-.010)
    for k in range(13):
        fraction=k/12;rib=.00025*math.cos(j*math.tau*96/384)
        upper=join+axis*.0006-outward*.0005
        q=lower.lerp(upper,fraction)+outward*rib
        index=k*384+j;shape.data[index].co=inverse@q;maximum=max(maximum,(q-ps[index]).length)
assert maximum<.065,('Unbounded waist fit',maximum)
# The actual jacket opening is a pelvis attachment. The knit shares that
# native control, keeping its seam continuous through the counter-rotation.
for bone in rig.data.bones:
    if bone.name not in band.vertex_groups:band.vertex_groups.new(name=bone.name)
ids=list(range(len(band.data.vertices)))
for g in band.vertex_groups:
    if g.name in rig.data.bones:g.remove(ids)
band.vertex_groups['pelvis'].add(ids,1.,'REPLACE')
transfer=band.modifiers.new('Shared actual jacket waist weights','DATA_TRANSFER');transfer.object=coat;transfer.use_vert_data=True;transfer.data_types_verts={'VGROUP_WEIGHTS'};transfer.vert_mapping='POLYINTERP_NEAREST';transfer.layers_vgroup_select_src='ALL';transfer.layers_vgroup_select_dst='NAME';band.modifiers.move(len(band.modifiers)-1,0)
flags=[(m,m.show_viewport) for m in band.modifiers if m!=transfer]
for m,_ in flags:m.show_viewport=False
bpy.context.view_layer.update();ev=band.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();names={g.index:g.name for g in band.vertex_groups};records=[{names[g.group]:g.weight for g in v.groups if names[g.group] in rig.data.bones} for v in mesh.vertices];ev.to_mesh_clear()
band.modifiers.remove(transfer)
for m,flag in flags:m.show_viewport=flag
for g in band.vertex_groups:
    if g.name in rig.data.bones:g.remove(ids)
for i,weights in enumerate(records):
    total=sum(weights.values());assert total>.99
    t=(i//384)/12;t=t*t*(3-2*t);weights={name:w/total*t for name,w in weights.items()};weights['pelvis']=weights.get('pelvis',0)+1-t
    for name,w in weights.items():
        if w>1e-7:band.vertex_groups[name].add([i],w,'REPLACE')
band_solid=next(m for m in band.modifiers if m.type=='SOLIDIFY');band_solid.solidify_mode='EXTRUDE';band_solid.use_even_offset=False;band_solid.use_quality_normals=True;band_solid.thickness_clamp=0
report['waist_fit']={'key':shape.name,'opening_controls':len(opening),'opening_center':list(center),'shorts_waist_controls':len(lower_opening),'shorts_waist_center':list(lower_center),'minimum_knit_height_m':.0106,'maximum_control_delta_m':maximum,'normal_rib_amplitude_m':.00025,'binding':'Knitted control rings grade from the actual shorts waist into the actual jacket opening. Normalized native weights blend from pelvis at the shorts into actual jacket weights at the upper seam; normal-extruded fabric thickness.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'WaistNeck.blend'),compress=True);print('WAIST_NECK_SAVED',maximum,flush=True)
