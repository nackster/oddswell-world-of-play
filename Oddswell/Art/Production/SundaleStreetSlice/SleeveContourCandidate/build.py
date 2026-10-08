"""Fit the existing sleeves more closely to their preserved anatomical arms."""
import bpy,json,hashlib,math
from mathutils import Vector
from pathlib import Path
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/WaistJoinCandidate/WaistJoin.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='15eaf6cf97f43895d2fdee1f48828b5d10740d6916776a611a9c29f057ddf0d5';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];coat.data=coat.data.copy();cage.data=coat.data
body=bpy.data.objects['Character | internal torso support'];contact=bpy.data.objects['Torso fit | isolated anatomical arm contact'];rig=bpy.data.objects['Walk study | native anatomical controls'];body.data=body.data.copy();contact.data=body.data
positions=[]
basis=body.data.shape_keys.key_blocks['Basis'];assert body.data.shape_keys.use_relative
for v in body.data.vertices:
    p=basis.data[v.index].co.copy()
    for k in body.data.shape_keys.key_blocks[1:]:
        assert not k.vertex_group,'Handle masked source shape keys explicitly'
        if k.value:p+=(k.data[v.index].co-k.relative_key.data[v.index].co)*k.value
    positions.append(body.matrix_world@p)
key=body.shape_key_add(name='Adult forearm elliptical muscle taper',from_mix=False);key.relative_key=basis;key.value=1.;body_changes=[];profiles={}
for i,v in enumerate(key.data):v.co=basis.data[i].co
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for side in ('neg','pos'):
    name=side+'.forearm';bone=rig.data.bones[name];a=rig.matrix_world@bone.head_local;axis=rig.matrix_world@bone.tail_local-a;unit=axis.normalized();width_axis=Vector((1,0,0));width_axis=(width_axis-unit*width_axis.dot(unit)).normalized();depth_axis=unit.cross(width_axis).normalized();index=body.vertex_groups[name].index
    weights=[next((w.weight for w in v.groups if w.group==index),0.) for v in body.data.vertices];along=[(p-a).dot(axis)/axis.length_squared for p in positions];ids=[i for i,w in enumerate(weights) if w>.75 and -.05<along[i]<1.05];centers=[]
    for j in range(13):
        at=j/12;ws=[weights[i]**3*math.exp(-((along[i]-at)/.11)**2) for i in ids];assert sum(ws)>0
        centers.append(sum(((positions[i]-a-axis*along[i])*w for i,w in zip(ids,ws)),Vector())/sum(ws))
    for i,(p,w,t) in enumerate(zip(positions,weights,along)):
        if w<.05 or not 0<t<1:continue
        q=t*12;j=min(11,int(q));center=a+axis*t+centers[j].lerp(centers[j+1],q-j);radial=p-center;radial-=unit*radial.dot(unit)
        if radial.length<1e-6:continue
        direction=radial.normalized();target=.040-.011*t+.004*math.sin(math.pi*t);rx=target*.92;rz=target
        limit=1/math.sqrt((direction.dot(width_axis)/rx)**2+(direction.dot(depth_axis)/rz)**2);mask=smooth((t-.10)/.20)*(1-smooth((t-.77)/.20))*w
        if radial.length<=limit or mask<1e-6:continue
        delta=-direction*min(.008,radial.length-limit)*mask;local=body.matrix_world.inverted().to_3x3()@delta;key.data[i].co+=local;body_changes.append({'id':i,'delta_local_m':list(local),'move_m':delta.length,'mask':mask})
    profiles[name]={'cross_section_centers':list(map(list,centers)),'maximum_inward_step_m':.008,'width_depth_ratio':.92}
group=coat.vertex_groups['Posed sleeve anatomical ease'];assert cage.vertex_groups[group.name].index==group.index
changes=[]
for v in coat.data.vertices:
    old=next((w.weight for w in v.groups if w.group==group.index),0.)
    if not old:continue
    new=min(.98,old*.98/.85);group.add([v.index],new,'REPLACE');changes.append({'id':v.index,'old':old,'new':new})
modifiers=[]
for o in (coat,cage):
    mod=o.modifiers['Sleeve cotton follows posed arm contours'];old=mod.offset;mod.offset=.007
    modifiers.append({'object':o.name,'name':mod.name,'old_offset_m':old,'new_offset_m':mod.offset,'target':mod.target.name})
shell=coat.modifiers['Actual fabric thickness'];shell_changes={}
for prop,row in shell_changes.items():setattr(shell,prop,row['new'])
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'SleeveContour.blend'),compress=True)
report={'source_sha256':expected,'candidate_sha256':sha(out/'SleeveContour.blend'),'fit_group':group.name,'old_peak_influence':.85,'new_peak_influence':.98,'changed_controls':changes,'modifiers':modifiers,'method':'Increase existing anatomically fitted sleeve influence from 0.85 to 0.98 and reduce its stand-off from 12 to 7 mm, matching the existing full-body clearance allowance. Preserve the original geodesic raglan/cuff/shoulder fades, original body keys, old garment controls/fields/keys, bone weights, rig, walk and licensed maps. No physical cloth simulation or full-body collision claim.'}
report['body_taper']={'added_key':key.name,'shared_objects':[body.name,contact.name],'controls':body_changes,'profiles':profiles,'maximum_control_move_m':max(r['move_m'] for r in body_changes),'method':'New editable support key, evaluated relative to the retained mixed source body. Thirteen weighted cross sections define each existing forearm centerline. Reduce radial excess toward a mildly elliptical adult forearm profile, capped at 8 mm with elbow/wrist fades. Original controls/keys/UVs/bone weights remain exact; this is authored fitting anatomy, not a measured scan or a visible replacement skin mesh.'}
report['shell_correction']={'object':coat.name,'modifier':shell.name,'properties':shell_changes,'thickness_m':shell.thickness,'method':'Original thickness settings retained. Even-offset, thickness-clamp and increased smoothing experiments rejected for new overlap pairs elsewhere in the walk. Existing source shell contacts remain an open cloth issue.'}
(out/'build-report.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('SLEEVE_CONTOUR_BUILT',len(changes),report['candidate_sha256'],flush=True)
