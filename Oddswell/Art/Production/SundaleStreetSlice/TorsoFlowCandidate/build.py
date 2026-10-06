"""Blend native torso/upper-arm influence across the connected underarm cloth."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/CanvasWeaveCandidate/NaturalCanvas.blend';source_sha='a32c6cbae8fd1767da6c03559f1addd948da46259064eb0ff85e38fedad8f50a'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source_sha
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];rig=bpy.data.objects['Walk study | native anatomical controls']
shared_before=[o.name for o in scene.objects if o.type=='MESH' and o.data==coat.data]
coat.data=coat.data.copy();cage.data=coat.data
body=bpy.data.objects['Character | internal torso support'];body_flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='ARMATURE']
for m,flag in body_flags:m.show_viewport=False
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());uv=coat.data.uv_layers['Cut raglan cloth panels'];panel={v.index:[] for v in coat.data.vertices}
for polygon in coat.data.polygons:
    torso=sum(uv.data[i].uv.x for i in polygon.loop_indices)/len(polygon.loop_indices)<.65
    for i in polygon.vertices:panel[i].append(float(torso))
ease=coat.shape_key_add(name='Anatomical upper torso jacket ease',from_mix=False);ease.value=1;fit_changes=[];pin_index=coat.vertex_groups['Collar zipper hem and cuff attachments'].index
def s_curve(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for v in coat.data.vertices:
    p=coat.matrix_world@v.co;held=max((g.weight for g in v.groups if g.group==pin_index),default=0.);mask=s_curve((p.z-1.17)/.07)*(1-s_curve((p.z-1.365)/.07))*(1-s_curve((held-.1)/.6))*sum(panel[v.index])/len(panel[v.index])
    if mask<1e-6:continue
    q=body.matrix_world.inverted()@p;hit,normal,face,distance=tree.find_nearest(q)
    if distance<=.022:continue
    delta=-(p-body.matrix_world@hit).normalized()*min(.012,distance-.022)*mask;ease.data[v.index].co+=coat.matrix_world.inverted().to_3x3()@delta;fit_changes.append({'id':v.index,'change_m':delta.length,'source_rest_body_distance_m':distance})
for m,flag in body_flags:m.show_viewport=flag
names=[g.name for g in coat.vertex_groups if g.name in rig.data.bones];assert all(coat.vertex_groups[n].index==cage.vertex_groups[n].index for n in names)
neighbors=[[] for v in coat.data.vertices]
for edge in coat.data.edges:
    a,b=edge.vertices;neighbors[a].append(b);neighbors[b].append(a)
before=[{g.name:next((w.weight for w in v.groups if w.group==g.index),0.) for g in coat.vertex_groups if g.name in names} for v in coat.data.vertices];weights=[row.copy() for row in before];mask=[];pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
centers=[]
for side,sign in (('neg',-1),('pos',1)):
    head=rig.matrix_world@rig.data.bones[side+'.upperarm'].head_local;centers.append(Vector((head.x-sign*.03,head.y,1.22)))
for v in coat.data.vertices:
    p=coat.matrix_world@v.co;d=min(sum(((p[i]-c[i])/r)**2 for i,r in enumerate((.09,.18,.15))) for c in centers);w=smooth(1-d);held=max((g.weight for g in v.groups if g.group==pin),default=0.);mask.append(w*(1-smooth((held-.1)/.6)))
for iteration in range(48):
    result=[]
    for i,row in enumerate(weights):
        strength=.5*mask[i]
        if strength<1e-7:result.append(row.copy());continue
        averaged={n:sum(weights[j][n] for j in neighbors[i])/len(neighbors[i]) for n in names};original_total=sum(before[i].values());average_total=sum(averaged.values());scale=original_total/average_total
        result.append({n:row[n]*(1-strength)+averaged[n]*scale*strength for n in names})
    weights=result
changed=[]
for i,(old,row) in enumerate(zip(before,weights)):
    delta=max(abs(row[n]-old[n]) for n in names)
    if delta<1e-6:continue
    for n,w in row.items():
        if w>1e-8:coat.vertex_groups[n].add([i],w,'REPLACE')
        else:coat.vertex_groups[n].remove([i])
    changed.append({'id':i,'maximum_influence_change':delta,'before':old,'after':row})
samples={v.index:[] for v in coat.data.vertices}
for polygon in coat.data.polygons:
    for i in polygon.loop_indices:samples[coat.data.loops[i].vertex_index].append(tuple(uv.data[i].uv))
bend=coat.vertex_groups.new(name='Underarm cotton finite bend radius')
for v in coat.data.vertices:
    held=max((g.weight for g in v.groups if g.group==pin),default=0);values=[]
    for u,t in samples[v.index]:
        if u>.65:values.append(0.);continue
        centers_uv=[(a,b) for a in (.056,.366) for b in (.210,.520)];d=min(((u-a)/.065)**2+((t-b)/.080)**2 for a,b in centers_uv);values.append(smooth(2*(1-d)))
    w=sum(values)/len(values)*(1-smooth((held-.1)/.6))
    if w:bend.add([v.index],w,'REPLACE')
for obj in (coat,cage):
    if bend.name not in obj.vertex_groups:
        g=obj.vertex_groups.new(name=bend.name);assert g.index==bend.index
    m=obj.modifiers.new('Underarm cotton bend radius','SMOOTH');m.factor=.5;m.iterations=32;m.vertex_group=bend.name;obj.modifiers.move(len(obj.modifiers)-1,next(i for i,m in enumerate(obj.modifiers) if m.type=='SHRINKWRAP'))
solid=next(m for m in coat.modifiers if m.type=='SOLIDIFY');solid.thickness_clamp=1.;solid.use_thickness_angle_clamp=False
fixed=[]
for obj in scene.objects:
    if obj.parent_type=='BONE' and obj.parent_bone=='head':
        for mod in list(obj.modifiers):
            if mod.type=='SURFACE_DEFORM' and mod.target==cage:
                fixed.append({'object':obj.name,'removed':mod.name,'reason':'Rigid head parenting already supplies collar motion; additional garment surface deformation doubles root travel.'});obj.modifiers.remove(mod)
report={'source_sha256':source_sha,'method':'48 local Jacobi neighbor averages at factor 0.5 across connected native underarm cloth. Graded rest-space mask and attachment protection; per-control total bone influence retained. Original control geometry, UVs, old keys, body weights, bones and action remain intact.','historical_shared_meshes':shared_before,'derived_mesh_objects':[coat.name,cage.name],'region_centers':[list(c) for c in centers],'changed_controls':len(changed),'maximum_bone_influence_change':max(x['maximum_influence_change'] for x in changed),'upper_torso_ease':{'added_key':ease.name,'target_rest_body_distance_m':.022,'maximum_control_change_m':max(x['change_m'] for x in fit_changes),'changed_controls':len(fit_changes),'method':'Graded torso-quarter selection in the upper chest/back. One editable rest fit reduces excessive ease by at most 12 mm, retaining at least the proposed 22 mm rest stand-off before later deformation/modifiers. This is not an animated clearance certificate.'},'underarm_fold_bend':{'factor':.5,'iterations':8,'scope':'Graded paired front/rear torso UV regions around the diagnosed residual fold; attachment protection and retained body constraint.'},'controls':changed,'fit_controls':fit_changes}
report['underarm_fold_bend'].update(iterations=32,radius_uv=[.065,.080],mask='smoothstep(2*(1-elliptic_squared_distance))');report['shell_thickness_clamp']={'nominal_m':solid.thickness,'clamp':1.,'angle_clamp':False};report['fixed_collar_zipper_objects']=fixed
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'TorsoFlow.blend'),compress=True);(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('TORSO_FLOW_SAVED',flush=True)
