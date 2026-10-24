"""Visible show-through check: flat mask renders where any original scan clothing seen past the new garments is red.

Opens the saved candidate, recolours in memory only and never saves, so the candidate file is untouched.
"""
import bpy, json, hashlib, ast
from mathutils import Vector
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric/StarterOutfitStudy'
native=out/'OddsWellStarterOutfit.blend'
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report=json.loads((out/'starter-report.json').read_text(encoding='utf-8'));assert sha(native)==report['candidate_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
body=bpy.data.objects['Scan character | Eric mesh'];rig=bpy.data.objects['Scan character | Eric rig']
skin=set(json.loads((out/'selection.json').read_text(encoding='utf-8'))['skin_faces'])
def flat(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
red,black,white=flat('mask | original clothing',(1,0,0)),flat('mask | skin and hair',(0,0,0)),flat('mask | new garment',(1,1,1))
body.data.materials.clear();body.data.materials.append(red);body.data.materials.append(black)
names=[g.name for g in body.vertex_groups]
def share(poly,prefixes):
    total=0
    for i in poly.vertices:total+=sum(g.weight for g in body.data.vertices[i].groups if names[g.group].startswith(prefixes))
    return total/len(poly.vertices)
# Hair, eyes and hands are exposed by design (black); only original clothing counts as show-through.
exempt=lambda poly:share(poly,('head','jaw','eye','mouth'))>=.3 or share(poly,('hand_','thumb_','index_','middle_','ring_','pinky_'))>=.35
for p in body.data.polygons:p.material_index=1 if p.index in skin or exempt(p) else 0
new=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(('OddsWell wardrobe | starter','Starter top | ','Joggers | ','Sneaker | '))]
assert len(new)==13,len(new)
for o in new:
    o.data.materials.clear();o.data.materials.append(white)
for o in scene.objects:
    if o.type=='MESH' and o!=body and o not in new:o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';d=scene.display;d.shading.light='FLAT';d.shading.color_type='MATERIAL';d.render_aa='OFF'
scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=600,700,100;scene.render.film_transparent=True
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
helper=root/'Oddswell/Art/Production/SundaleStreetSlice/ScannedHumanMotionCandidate/refine.py';tree=ast.parse(helper.read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='frame_camera'],type_ignores=[]),str(helper),'exec'))
cam=scene.camera;cam.data.lens=40
views={'front':(-.75,.85,1.15),'back':(-.75,-5.6,1.15),'left':(-4,-2.4,1.15),'right':(2.5,-2.4,1.15),'three_quarter':(-2.9,.4,1.28)}
masks=out/'Coverage';masks.mkdir(exist_ok=True);rows=[]
for frame in range(1,50,4):
    scene.frame_set(frame)
    for view,pos in views.items():
        frame_camera(pos,(-.75,-2.4,.95));path=masks/f'{view}_{frame:02d}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        img=bpy.data.images.load(str(path));px=list(img.pixels);n=len(px)//4
        shown=sum(1 for i in range(n) if px[4*i+3]>.5 and px[4*i]>.8 and px[4*i+1]<.2);garment=sum(1 for i in range(n) if px[4*i+3]>.5 and px[4*i+1]>.8)
        bpy.data.images.remove(img);rows.append({'frame':frame,'view':view,'original_clothing_pixels':shown,'new_garment_pixels':garment,'show_through_ratio':round(shown/max(1,shown+garment),5)})
worst=max(rows,key=lambda r:r['show_through_ratio'])
coverage={'candidate_sha256':report['candidate_sha256'],'frames':list(range(1,50,4)),'views':list(views),'resolution':[600,700],'samples':rows,'worst':worst,
          'mean_show_through_ratio':round(sum(r['show_through_ratio'] for r in rows)/len(rows),5),
          'method':'Workbench flat masks without anti-aliasing: original scan clothing red, skin plus head/hand-weighted faces black, new garments white. Counts visible original-clothing pixels per camera; hidden interpenetration is not measured.'}
(out/'coverage-report.json').write_text(json.dumps(coverage,indent=2)+'\n',encoding='utf-8');print('STARTER_COVERAGE',coverage['mean_show_through_ratio'],json.dumps(worst),flush=True)
