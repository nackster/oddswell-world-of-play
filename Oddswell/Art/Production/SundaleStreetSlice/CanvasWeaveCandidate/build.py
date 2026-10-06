"""Stable native UVs and restrained woven-canvas response on existing footwear."""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent;root=next(p for p in out.parents if (p/'.git').exists());source=root/'Oddswell/Art/Production/SundaleStreetSlice/ThighDrapeCandidate/ThighDrape.blend';source_sha='c14ec89ca354a9dbe498c6955cde745e2edcb977c9b8603d9e37080247fffeac'
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==source_sha
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1)
uv_name='Rest sewn canvas panels';reports={};new_materials={}
for side in ('left','right'):
    for prefix in ('canvas sneaker ','canvas sneaker tongue '):
        obj=bpy.data.objects['Character | '+prefix+side];obj.data=obj.data.copy();bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        layer=obj.data.uv_layers.new(name=uv_name);obj.data.uv_layers.active=layer;layer.active_render=True
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.015,area_weight=.5,correct_aspect=True,scale_to_bounds=False);bpy.ops.object.mode_set(mode='OBJECT')
        layer=obj.data.uv_layers[uv_name]
        obj.data.calc_loop_triangles();area=sum(t.area for t in obj.data.loop_triangles);uv_area=0.
        for t in obj.data.loop_triangles:
            a,b,c=[layer.data[i].uv for i in t.loops];uv_area+=abs((b-a).cross(c-a))*.5
        assert uv_area>1e-8;scale=math.sqrt(area/uv_area)/.266
        for item in layer.data:item.uv*=scale
        zero=0
        for t in obj.data.loop_triangles:
            a,b,c=[layer.data[i].uv for i in t.loops]
            if t.area>1e-10 and abs((b-a).cross(c-a))<1e-12:zero+=1
        assert zero==0,(obj.name,zero)
        reports[obj.name]={'added_uv':layer.name,'triangles':len(obj.data.loop_triangles),'nondegenerate_triangles_with_zero_uv_area':zero,'surface_area_m2':area,'uv_scale':scale,'licensed_tile_size_m':.266}
        for i,slot in enumerate(obj.material_slots):
            old=slot.material
            if old.name=='Character | shadowed canvas lining':continue
            if old.name not in new_materials:
                material=old.copy();material.name='Canvas study | '+old.name.removeprefix('Character | ');new_materials[old.name]=material
                nodes=material.node_tree.nodes;links=material.node_tree.links;uv_node=nodes.new('ShaderNodeUVMap');uv_node.uv_map=uv_name;uv_node.name='Actual sewn rest-panel UV'
                for node in nodes:
                    if node.type=='TEX_IMAGE':links.new(uv_node.outputs['UV'],node.inputs['Vector'])
                    if node.type=='BSDF_PRINCIPLED':
                        node.inputs['Specular IOR Level'].default_value=.24;node.inputs['Diffuse Roughness'].default_value=.4;node.inputs['Sheen Weight'].default_value=.24;node.inputs['Sheen Roughness'].default_value=.8
                    if node.type=='BUMP':node.inputs['Strength'].default_value=.25;node.inputs['Distance'].default_value=.0002
                    if node.type=='MAP_RANGE' and any(link.to_socket.name=='Roughness' for link in node.outputs['Result'].links):
                        node.inputs['To Min'].default_value=.78;node.inputs['To Max'].default_value=.95
            obj.data.materials[i]=new_materials[old.name]
seam_reports={};deps=bpy.context.evaluated_depsgraph_get()
for side in ('left','right'):
    shoe=bpy.data.objects['Character | canvas sneaker '+side];tree=BVHTree.FromObject(shoe,deps)
    for obj in scene.objects:
        if obj.type!='CURVE' or side not in obj.name or not obj.name.startswith('Character | shoe lace ') or not any(n in obj.name for n in ('quarter seam','toe cap seam')):continue
        assert obj.parent==shoe.parent and obj.parent_bone==shoe.parent_bone
        if not obj.data.shape_keys:obj.shape_key_add(name='Basis')
        fit=obj.shape_key_add(name='Fitted canvas panel seam',from_mix=False);fit.value=1;index=0;maximum=0.;source_gap=0.
        for spline in obj.data.splines:
            assert spline.type!='BEZIER'
            for point in spline.points:
                world=obj.matrix_world@Vector(point.co[:3]);local=shoe.matrix_world.inverted()@world;hit,normal,face,distance=tree.find_nearest(local);target=shoe.matrix_world@(hit+normal*.0003);fit.data[index].co=obj.matrix_world.inverted()@target;index+=1;maximum=max(maximum,(target-world).length);source_gap=max(source_gap,distance)
        assert index==len(fit.data);seam_reports[obj.name]={'added_key':fit.name,'points':index,'source_maximum_upper_gap_m':source_gap,'maximum_fit_change_m':maximum,'centerline_stand_off_m':.0003,'parent_bone':obj.parent_bone}
detail_weights={};rig=bpy.data.objects['Walk study | native anatomical controls']
for obj in scene.objects:
    if not obj.name.startswith('Walk surface | Character | ') or not any(n in obj.name for n in ('foxing edge','outsole groove','sewn heel counter')):continue
    side='neg' if 'left' in obj.name else 'pos';indices=[v.index for v in obj.data.vertices]
    for group in obj.vertex_groups:
        if group.name in rig.data.bones:group.remove(indices)
    group=obj.vertex_groups.get(side+'.foot') or obj.vertex_groups.new(name=side+'.foot');group.add(indices,1,'REPLACE')
    detail_weights[obj.name]={'foot_bone':side+'.foot','controls':len(indices),'method':'Replace generic shin-dominated native weights with the actual foot bone, retaining original controls and modifier.'}
assert len(detail_weights)==6,detail_weights
report={'source_sha256':source_sha,'method':'Native smart-projected rest-panel UV islands scaled by measured cloth area to a 266 mm licensed texture tile. Existing original UVs, mesh controls and modifiers remain intact. UVs follow native foot deformation. Shader changes only the existing uppers and tongues.','objects':reports,'materials':{k:v.name for k,v in new_materials.items()},'fitted_panel_seams':seam_reports,'foot_detail_weights':detail_weights,'new_bitmap_assets':0}
scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'NaturalCanvas.blend'),compress=True);(out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('CANVAS_SAVED',flush=True)
