"""Relax shoulder ease against the native anatomy and map licensed fabric to cut panels."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/TorsoFlowCandidate/TorsoFlow.blend';source_sha='3d4b732f51a6d2b79a0ed18a9b4f94b67c843cefd1b14a968bc62bf4591f4dc3'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source_sha
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);coat=bpy.data.objects['Character | tailored slate jacket'];cage=bpy.data.objects['Walk cage | refined jacket surface'];body=bpy.data.objects['Character | internal torso support'];coat.data=coat.data.copy();cage.data=coat.data
flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='ARMATURE']
for m,f in flags:m.show_viewport=False
tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get());key=coat.shape_key_add(name='Relaxed anatomical shoulder ease',from_mix=False);key.value=1;pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index;changes=[]
def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)
for v in coat.data.vertices:
    local=v.co.copy()
    for old in coat.data.shape_keys.key_blocks[1:]:
        if old!=key and old.value:local+=(old.data[v.index].co-coat.data.shape_keys.key_blocks['Basis'].data[v.index].co)*old.value
    p=coat.matrix_world@local;d=min(sum(((p[i]-c[i])/r)**2 for i,r in enumerate((.125,.170,.150))) for c in ((-.802,-2.35,1.455),(-.579,-2.35,1.455)));held=max((g.weight for g in v.groups if g.group==pin),default=0);weight=smooth(2*(1-d))*(1-smooth((held-.65)/.30))
    if weight<1e-6:continue
    hit,normal,face,distance=tree.find_nearest(body.matrix_world.inverted()@p)
    if distance<=.010:continue
    delta=-(p-body.matrix_world@hit).normalized()*min(.032,distance-.010)*weight;key.data[v.index].co+=coat.matrix_world.inverted().to_3x3()@delta;changes.append({'id':v.index,'move_m':delta.length,'rest_gap_m':distance,'held':held})
for m,f in flags:m.show_viewport=f
# Retain all old UVs. Scale a derived six-panel atlas by measured rest derivatives.
old_uv=coat.data.uv_layers['Cut raglan cloth panels'];new_uv=coat.data.uv_layers.new(name='Physical rest jacket weave');coat.data.calc_loop_triangles();stats={}
def panel(u,v):return ('neg' if u<.32 else 'pos')+('_front' if v<.32 else '_rear') if u<.65 else ('neg_sleeve' if v<.5 else 'pos_sleeve')
for tri in coat.data.loop_triangles:
    a,b,c=[old_uv.data[i].uv.copy() for i in tri.loops];p,q,r=[coat.data.vertices[i].co for i in tri.vertices];ab=b-a;ac=c-a;det=ab.cross(ac)
    if abs(det)<1e-12:continue
    du=((q-p)*ac.y-(r-p)*ab.y)/det;dv=((r-p)*ab.x-(q-p)*ac.x)/det;name=panel(*((a+b+c)/3));row=stats.setdefault(name,[0.,0.,0.]);row[0]+=du.length*tri.area;row[1]+=dv.length*tri.area;row[2]+=tri.area
scales={n:[r[0]/r[2]/.266,r[1]/r[2]/.266] for n,r in stats.items()}
for poly in coat.data.polygons:
    center=sum((old_uv.data[i].uv for i in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices);su,sv=scales[panel(*center)]
    for i in poly.loop_indices:new_uv.data[i].uv=(old_uv.data[i].uv.x*su,old_uv.data[i].uv.y*sv)
material=coat.data.materials[0].copy();material.name='Shoulder study | slate physical-panel weave';coat.data.materials[0]=material;nodes=material.node_tree.nodes;links=material.node_tree.links;uv_node=nodes.new('ShaderNodeUVMap');uv_node.name='Stable physical rest-panel weave';uv_node.uv_map=new_uv.name
for node in nodes:
    if node.type=='TEX_IMAGE':node.projection='FLAT';links.new(uv_node.outputs['UV'],node.inputs['Vector'])
    elif node.type=='BSDF_PRINCIPLED':node.inputs['Diffuse Roughness'].default_value=.45;node.inputs['Specular IOR Level'].default_value=.20;node.inputs['Sheen Weight'].default_value=.22
    elif node.type=='BUMP' and node.inputs['Height'].is_linked and node.inputs['Height'].links[0].from_node.type=='TEX_IMAGE':node.inputs['Strength'].default_value=.4;node.inputs['Distance'].default_value=.0004
    elif node.type=='MAP_RANGE' and any(l.to_socket.name=='Roughness' for l in node.outputs['Result'].links):node.inputs['To Min'].default_value=.72;node.inputs['To Max'].default_value=.92
    elif node.type=='MIX_RGB' and node.name=='Mix (Legacy)':
        color=node.inputs['Color1'].default_value;node.inputs['Color1'].default_value=(*(min(1,c*1.25) for c in color[:3]),color[3])
report={'source_sha256':source_sha,'added_key':key.name,'changed_controls':len(changes),'maximum_key_move_m':max(r['move_m'] for r in changes),'method':'Graded bilateral shoulder region, preserving full collar attachments. Reduce excessive rest ease toward anatomical support with proposed 10 mm rest stand-off, capped at 32 mm. Existing outside-body constraint, weight blending and shell clamp retained; animated clearance requires separate review.','controls':changes,'added_uv':new_uv.name,'physical_weave_scales':scales,'licensed_texture_tile_m':.266,'new_bitmap_assets':0,'material_copy':material.name,'material_scope':'Visible jacket only. Derived sewn-panel UVs scaled from area-weighted rest derivatives, existing licensed terlenka maps, 25 percent dye multiplier and matte fiber response. Existing collar/cuffs and original shaders remain unchanged.'}
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ShoulderChest.blend'),compress=True);(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('SHOULDER_CHEST_SAVED',len(changes),report['maximum_key_move_m'],flush=True)
