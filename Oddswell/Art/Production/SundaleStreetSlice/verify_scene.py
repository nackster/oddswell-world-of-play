"""Check the saved artifact in a fresh Blender process without rendering."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'OddsWell_Sundale_StreetSlice.blend'))
scene=bpy.context.scene
bpy.context.view_layer.update()
packed=[image for image in bpy.data.images if image.source=='FILE' and image.packed_file]
assert len(packed)==6
assert scene.camera.name=='CAM | gameplay street'
assert all(bpy.data.objects.get('CAM | '+name) for name in ('Court_and_Arena','Architecture_Detail'))
assert scene['flat_court_paint'] and scene['clothing_details_posed']
paint=[obj for obj in scene.objects if obj.name.startswith('Court | ') and obj.type=='CURVE']
assert paint and all(obj.dimensions.z<.001 for obj in paint)
head=bpy.data.objects['Character | anatomical head']
surface_vertices={i for polygon in head.data.polygons for i in polygon.vertices}
assert surface_vertices and all(head.data.vertices[i].co.z>1.59 and abs(head.data.vertices[i].co.x+.75)<.15 for i in surface_vertices)
result={'result':'PASS','packed_texture_maps':len(packed),'cameras':3,'court_paint_max_thickness_m':max(obj.dimensions.z for obj in paint),'collar_stray_faces':0,'mesh_objects':sum(obj.type=='MESH' for obj in scene.objects),'native_scene_objects':len(scene.objects),'runtime_claim':False}
(ROOT/'cold-reopen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('ODDSWELL_STREET_SLICE_COLD_CHECK_PASS',json.dumps(result))
