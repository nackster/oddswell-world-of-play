"""Local native cloth smoothing and sewn-detail binding to its subdivided surface."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(__file__).resolve().parent; root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/NativeWalkingStudy/NativeWalk.blend'
with source.open('rb') as f: assert hashlib.file_digest(f,'sha256').hexdigest()=='c0be82b985ca4be23f38271e4dcdff6d93960c499e871d66723149d3a6636a22'
bpy.ops.wm.open_mainfile(filepath=str(source)); scene=bpy.context.scene;scene.frame_set(1)
coat=bpy.data.objects['Character | tailored slate jacket']; old=bpy.data.objects['Walk cage | jacket']
followers=[o for o in scene.objects if any(m.type=='SURFACE_DEFORM' and m.target==old for m in o.modifiers)]
for o in followers:
    for m in list(o.modifiers):
        if m.type=='SURFACE_DEFORM' and m.target==old: o.modifiers.remove(m)
group=coat.vertex_groups.new(name='Rounded shoulder cloth')
pin=coat.vertex_groups['Collar zipper hem and cuff attachments'].index
for v in coat.data.vertices:
    p=coat.matrix_world@v.co
    d=min(sum(((p[i]-c[i])/r[i])**2 for i in range(3)) for c,r in [((-.89,-2.38,1.36),(.105,.15,.16)),((-.49,-2.38,1.36),(.105,.15,.16))])
    w=max(0.,1-d); w=w*w*(3-2*w)
    held=max((g.weight for g in v.groups if g.group==pin),default=0)
    if w>0 and held<.8: group.add([v.index],w,'REPLACE')
mod=coat.modifiers.new('Round shoulder cloth transition','SMOOTH');mod.factor=.6;mod.iterations=18;mod.vertex_group=group.name
coat.modifiers.move(len(coat.modifiers)-1,1)
cage=coat.copy(); cage.data=coat.data; cage.name='Walk cage | refined jacket surface';scene.collection.objects.link(cage)
for m in list(cage.modifiers):
    if m.type=='SOLIDIFY': cage.modifiers.remove(m)
    elif m.type=='SUBSURF': m.levels=2;m.render_levels=2
cage.modifiers.new('Stable triangular refined surface','TRIANGULATE');cage.hide_render=True;cage.hide_set(False)
bpy.context.view_layer.update();surface=BVHTree.FromObject(coat,bpy.context.evaluated_depsgraph_get())
regenerated=[]
for obj in followers:
    if 'raglan topstitch' in obj.name:
        original=bpy.data.objects[obj.name.removeprefix('Walk surface | ')]
        curve=original.copy();curve.data=original.data.copy();curve.name='Refined rest seam | '+original.name;scene.collection.objects.link(curve);curve.hide_set(False);curve.hide_render=True
        for spline in curve.data.splines:
            for p in spline.points:
                q=coat.matrix_world.inverted()@(curve.matrix_world@Vector(p.co[:3]));hit,normal,_,_=surface.find_nearest(q)
                p.co=(*(curve.matrix_world.inverted()@(coat.matrix_world@(hit+normal*.00055))),1)
        bpy.context.view_layer.update();ev=curve.evaluated_get(bpy.context.evaluated_depsgraph_get())
        obj.data=bpy.data.meshes.new_from_object(ev);obj.matrix_world=curve.matrix_world.copy();curve.hide_set(True);regenerated.append(obj.name)
    m=obj.modifiers.new('Refined sewn garment surface following','SURFACE_DEFORM');m.target=cage;obj.modifiers.move(len(obj.modifiers)-1,0)
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.surfacedeform_bind(modifier=m.name);assert m.is_bound
    print('REFINED_SEAM_BOUND',obj.name,flush=True)
cage.hide_set(True);scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'RoundedShoulder.blend'),compress=True)
(out/'round-report.json').write_text(json.dumps({'native_smooth_factor':mod.factor,'iterations':mod.iterations,'bound_followers':len(followers),'regenerated_raglan_followers':regenerated,'source_controls_uv_keys_unchanged':True},indent=2)+'\n')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU';scene.cycles.samples=16;scene.render.use_persistent_data=True
data=bpy.data.cameras.new('Rounded shoulder review');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
rig=bpy.data.objects['Walk study | native anatomical controls']
for label,frame,pos,target in [('Rounded_Hips_Rear',13,(-1.10,-4.1,1.12),(-.76,-2.4,.91)),('Rounded_Torso_Front',13,(-.85,-.80,1.23),(-.80,-2.4,1.20))]:
    scene.frame_set(frame);phi=(frame-1)/24;shift=Vector((.012*math.sin(2*math.pi*phi)-.009*(1-math.cos(2*math.pi*phi)),rig['root_stride_m']*phi,0))
    camera.location=Vector(pos)+shift;camera.rotation_euler=(Vector(target)+shift-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=65
    scene.render.resolution_x=840;scene.render.resolution_y=840;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    print('ROUNDED_REVIEW',label,flush=True)
