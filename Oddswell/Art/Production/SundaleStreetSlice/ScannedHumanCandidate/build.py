"""Local licensed scanned-human scene study; vendor mesh is not redistributed."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
root=next(p for p in Path(__file__).resolve().parents if (p/'.git').exists());out=root/'downloads/licensed-characters/RenderpeopleEric';root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/TorsoHipEaseCandidate/PosedEase.blend'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(source)=='85fef82c3e865a76dcd11515ec8f7c4148f407d07a23a3fb6a1896036d19fbaf'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
old=set(scene.objects)
for o in old:
    if o.name.startswith(('Character | ','Walk surface | Character | ')):o.hide_render=True;o.hide_set(True)
fbx=out/'EricSource/rp_eric_rigged_001_zup_a.fbx';bpy.ops.import_scene.fbx(filepath=str(fbx));new=[o for o in scene.objects if o not in old];rig=next(o for o in new if o.type=='ARMATURE');body=next(o for o in new if o.type=='MESH');rig.name='Scan character | Eric rig';body.name='Scan character | Eric mesh'
# Relax the scanned A pose using its original skinning; preserve source topology and UVs.
for side,angle in [('l',.48),('r',-.48)]:
    pb=rig.pose.bones['upperarm_'+side];pb.rotation_mode='QUATERNION';axis=(rig.matrix_world.to_3x3()@pb.bone.matrix_local.to_3x3()).inverted()@Vector((0,1,0));pb.rotation_quaternion=Quaternion(axis.normalized(),angle)
bpy.context.view_layer.update();height=body.dimensions.z;scale=1.80/height
holder=bpy.data.objects.new('Scan character | placement',None);scene.collection.objects.link(holder);rig.parent=holder
holder.matrix_world=Matrix.Translation(Vector((-.75,-2.4,0)))@Matrix.Rotation(math.pi,4,'Z')@Matrix.Scale(scale,4)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);mesh=ev.to_mesh();minimum_z=min((ev.matrix_world@v.co).z for v in mesh.vertices);ev.to_mesh_clear();holder.location.z-=minimum_z
mat=body.data.materials[0];mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.48
tex=out/'EricSource/tex'
for node in n:
    if node.type=='TEX_IMAGE' and node.image:node.image.filepath=str(tex/Path(node.image.filepath.replace('\\','/')).name);node.image.reload()
normal=n.new('ShaderNodeTexImage');normal.image=bpy.data.images.load(str(tex/'rp_eric_rigged_001_norm.jpg'),check_existing=True);normal.image.colorspace_settings.name='Non-Color';map_node=n.new('ShaderNodeNormalMap');map_node.inputs['Strength'].default_value=.6;l.new(normal.outputs['Color'],map_node.inputs['Color']);l.new(map_node.outputs['Normal'],bs.inputs['Normal'])
gloss=n.new('ShaderNodeTexImage');gloss.image=bpy.data.images.load(str(tex/'rp_eric_rigged_001_gloss.jpg'),check_existing=True);gloss.image.colorspace_settings.name='Non-Color';inverse=n.new('ShaderNodeMath');inverse.operation='SUBTRACT';inverse.inputs[0].default_value=1.;l.new(gloss.outputs['Color'],inverse.inputs[1]);l.new(inverse.outputs[0],bs.inputs['Roughness'])
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath and not image.packed_file:image.pack()
scene.frame_set(1);scene.cycles.device='CPU';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ScannedHumanScene.blend'),compress=True)
report={'scene_source_sha256':sha(source),'download_url':'https://renderpeople.com/sample/free/renderpeople_free_rigged_people_FBX.zip','download_sha256':sha(out/'rigged-free.zip'),'fbx_sha256':sha(fbx),'candidate_sha256':sha(out/'ScannedHumanScene.blend'),'vendor':'Renderpeople','model':'Eric Rigged 001','license_url':'https://renderpeople.com/general-terms-and-conditions/','source_mesh_vertices':len(body.data.vertices),'source_mesh_polygons':len(body.data.polygons),'uvs':[u.name for u in body.data.uv_layers],'bones':len(rig.data.bones),'height_m':1.8,'arm_relaxation_radians':.48,'scope':'New licensed local scanned-human quality study. Original scene retained with prior human hidden. Vendor geometry/UV/weights retained; imported skeleton not yet retargeted to original walk or runtime. Source clothing remains; OddsWell wardrobe adaptation is pending. Raw assets/native source kept in ignored local storage due vendor redistribution restrictions.'}
(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCANNED_HUMAN_BUILT',report['candidate_sha256'],flush=True)
