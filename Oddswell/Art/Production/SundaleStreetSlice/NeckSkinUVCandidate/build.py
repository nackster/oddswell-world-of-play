"""Give the extruded neck skirt real texture depth without changing anatomy."""
import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
root=next(p for p in out.parents if (p/'.git').exists())
source=root/'Oddswell/Art/Production/SundaleStreetSlice/ShoulderEaseCandidate/ShoulderEase.blend'
with source.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='9A6BB3CA8D257CD7E130D0CDDC460264D7B645D4669E4D68416F7CA35E80730F'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene;head=bpy.data.objects['Character | anatomical head']
mods=[(m,m.show_viewport) for m in head.modifiers]
for m,_ in mods:m.show_viewport=False
bpy.context.view_layer.update()
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
points=[head.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
uv=head.data.uv_layers['MakeHuman source UV']
layer=head.data.uv_layers.new(name='Continuous neck skin UV')
for a,b in zip(layer.data,uv.data):a.uv=b.uv
center=Vector((-.6873,-2.3287,1.50))
theta=[math.atan2(p.y-center.y,p.x-center.x) for p in points]
samples=[];collapsed=[]
for face in head.data.polygons:
    ps=[points[i] for i in face.vertices]
    if max(p.z for p in ps)-min(p.z for p in ps)>.045 and max(p.z for p in ps)<1.51:
        collapsed.append(face)
    elif min(p.z for p in ps)>=1.5007 and max(p.z for p in ps)<1.54:
        for index in face.loop_indices:
            i=head.data.loops[index].vertex_index
            samples.append((i,uv.data[index].uv.copy()))
assert collapsed and len(samples)>50
def wrap(a):return (a+math.pi)%math.tau-math.pi
slopes=[];bottom_uvs={}
for face in collapsed:
    for index in face.loop_indices:
        i=head.data.loops[index].vertex_index;p=points[i]
        if p.z>1.48:continue
        anchor=min(face.loop_indices,key=lambda j:(0 if points[head.data.loops[j].vertex_index].z>1.49 else 1,abs(wrap(theta[head.data.loops[j].vertex_index]-theta[i]))))
        top=head.data.loops[anchor].vertex_index;top_uv=uv.data[anchor].uv.copy()
        nearby=[(j,t) for j,t in samples if abs(wrap(theta[j]-theta[top]))<.26 and (t-top_uv).length<.10]
        assert len(nearby)>=6,('Missing upper neck UV slope',i,len(nearby))
        a=np.array([[wrap(theta[j]-theta[top])*.056,points[j].z-points[top].z] for j,t in nearby])
        b=np.array([[t.x-top_uv.x,t.y-top_uv.y] for j,t in nearby])
        coefficients=np.linalg.lstsq(a,b,rcond=None)[0]
        derivative=Vector(tuple(coefficients[1]))
        assert .1<derivative.length<4,('Unstable UV height slope',i,list(derivative))
        value=top_uv+derivative*(p.z-points[top].z)
        layer.data[index].uv=value;bottom_uvs.setdefault(i,[]).append((top_uv,value))
        slopes.append({'vertex':i,'derivative_per_m':list(derivative),'old_uv':list(uv.data[index].uv),'new_uv':list(value)})
# Give the hidden closing cap the matching bottom rim on the same UV island.
for face in head.data.polygons:
    if face in collapsed:continue
    for index in face.loop_indices:
        i=head.data.loops[index].vertex_index
        if i in bottom_uvs:
            old=uv.data[index].uv
            _,value=min(bottom_uvs[i],key=lambda pair:(pair[0]-old).length)
            layer.data[index].uv=value
for m,visible in mods:m.show_viewport=visible
head.data.uv_layers.active=layer;layer.active_render=True
material=head.data.materials[0];nodes,links=material.node_tree.nodes,material.node_tree.links
mapping=nodes.new('ShaderNodeUVMap');mapping.name='Continuous lower neck atlas';mapping.uv_map=layer.name
links.new(mapping.outputs['UV'],nodes['CC0 MakeHuman skin'].inputs['Vector'])
scene['continuous_neck_texture_map']=True
scene['neck_uv_repaired_strip_faces']=len(collapsed)
scene['neck_uv_source_preserved']=True
(out/'uv-slope.json').write_text(json.dumps({'strip_faces':len(collapsed),'bottom_uv_controls':len(slopes),'slopes':slopes},indent=2)+'\n')
scene.camera=bpy.data.objects['CAM | gameplay street']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'NeckSkinUV.blend'),compress=True)
print('NECK_UV_SAVED',len(collapsed),len(slopes),flush=True)
