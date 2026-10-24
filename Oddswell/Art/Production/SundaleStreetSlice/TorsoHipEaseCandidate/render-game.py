import bpy,json,hashlib
from pathlib import Path
out=Path(__file__).resolve().parent;native=out/'PosedEase.blend'
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;scene.frame_set(7);scene.camera=bpy.data.objects['CAM | gameplay street'];scene.cycles.device='CPU';scene.cycles.samples=16;scene.render.resolution_percentage=100;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.filepath=str(out/'Gameplay.png');bpy.ops.render.render(write_still=True)
with native.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
(out/'game-render.json').write_bytes((json.dumps({'candidate_sha256':sha,'frame':7,'renderer':'Blender 4.5.5 LTS / Cycles / CPU','samples':16,'resolution':[1280,720],'native_geometry':True,'scene_geometry_changed_for_render':False},indent=2)+'\n').encode());print('UPPER_DRAPE_GAME_RENDERED',flush=True)
