"""Authored adult chest planes in the editable body and fitted jacket."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/TorsoSilhouetteCandidate/TorsoSilhouette.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected='3acafeea461315270a579cbddfd3031d98a4478ed2441740ae57ade55a516fe5';assert sha(source)==expected
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
body=bpy.data.objects['Character | internal torso support'];coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];contact=bpy.data.objects['Torso fit | isolated anatomical arm contact']
body.data=body.data.copy();contact.data=body.data;coat.data=coat.data.copy();cage.data=coat.data
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3.-2.*t)
def gaussian(v,w):return math.exp(-(v/w)**2)
def contour(p):
    u=abs(p.x+.75);front=smooth((p.y+2.32)/.075);region=smooth((p.z-1.18)/.07)*(1-smooth((p.z-1.435)/.025))*(1-smooth((u-.14)/.045))
    pec=.011*gaussian(u-.077,.060)*gaussian(p.z-1.333,.055)
    lower=-.0045*gaussian(u-.08,.065)*gaussian(p.z-(1.272-.055*u),.018)
    sternum=-.0035*gaussian(u,.024)*gaussian(p.z-1.337,.067)
    clavicle=.0045*gaussian(p.z-(1.411-.11*u),.012)*smooth(u/.035)-.0025*gaussian(p.z-(1.389-.11*u),.016)*smooth(u/.035)
    return front*region*(pec+lower+sternum+clavicle)
report={'source_sha256':expected,'method':'Graded authored paired pectoral planes, shallow lower-chest transition, sternum and clavicle relief in existing rest geometry. Original controls/UVs/keys/weights/walk retained. No anatomical scan or physical simulation claim.','objects':{}}
for o,name,scale in ((body,'Adult pectoral and clavicle contours',.75),(coat,'Fitted cotton chest contours',1.0)):
    positions=[]
    for v in o.data.vertices:
        p=v.co.copy()
        for k in o.data.shape_keys.key_blocks[1:]:
            if k.value:p+=(k.data[v.index].co-o.data.shape_keys.key_blocks['Basis'].data[v.index].co)*k.value
        positions.append(o.matrix_world@p)
    key=o.shape_key_add(name=name,from_mix=False);key.value=1;changes=[];chest=o.vertex_groups['chest'].index
    for v,p in zip(o.data.vertices,positions):
        weight=max((w.weight for w in v.groups if w.group==chest),default=0);amount=contour(p)*scale*smooth((weight-.55)/.35)
        if o==coat:amount*=smooth(abs(p.x+.75)/.025)
        if abs(amount)<1e-8:continue
        key.data[v.index].co+=o.matrix_world.inverted().to_3x3()@Vector((0,amount,0));changes.append({'id':v.index,'delta_y_m':amount})
    report['objects'][o.name]={'added_key':name,'changed_controls':len(changes),'minimum_y_delta_m':min(c['delta_y_m'] for c in changes),'maximum_y_delta_m':max(c['delta_y_m'] for c in changes),'controls':changes}
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ChestContour.blend'),compress=True);report['candidate_sha256']=sha(out/'ChestContour.blend');(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('CHEST_CONTOUR_BUILT',report['candidate_sha256'],flush=True)
