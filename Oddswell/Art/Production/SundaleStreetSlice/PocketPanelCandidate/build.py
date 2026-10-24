import bpy
import hashlib
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

output=Path(__file__).resolve().parent
source=output.parent/'FoldedHemCandidate/FoldedHem.blend'
with source.open('rb') as stream:
    assert hashlib.file_digest(stream,'sha256').hexdigest().upper()=='01AAE0208F86F7A60B2880276AFB64F56D3C9B10ECACE711ACE1C16CEDA0AA9C'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
surface=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
thread=bpy.data.materials['Character | matching cotton topstitch'].copy()
thread.name='Character | inset pocket topstitch'
thread.diffuse_color=(.52,.50,.44,1)
thread.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=thread.diffuse_color

def stitch(name,points):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D';data.bevel_depth=.00027;data.bevel_resolution=2
    data.materials.append(thread)
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for point,position in zip(spline.points,points):point.co=(*position,1)
    obj=bpy.data.objects.new(name,data)
    scene.collection.objects.link(obj)
    obj.matrix_world=pants.matrix_world.copy()

def lerp(a,b,t):return a.lerp(b,t)
def curve_point(points,t):
    position=t*(len(points)-1)
    i=min(int(position),len(points)-2)
    return lerp(points[i],points[i+1],position-i)

for side in ('left','right'):
    seam=bpy.data.objects['Character | back pocket seam '+side]
    transform=pants.matrix_world.inverted()@seam.matrix_world
    outline=[transform@Vector(pt.co[:3]) for spline in seam.data.splines for pt in spline.points]
    assert len(outline)==49
    left=outline[:13]
    bottom=outline[12:37]
    right=list(reversed(outline[36:]))
    top=[outline[0],outline[-1]]
    vertices=[];faces=[];gaps=[]
    columns=24;rows=12
    for r in range(rows+1):
        v=r/rows
        L=curve_point(left,v);R=curve_point(right,v)
        for c in range(columns+1):
            u=c/columns
            T=curve_point(top,u);B=curve_point(bottom,u)
            P=T*(1-v)+B*v+L*(1-u)+R*u
            P-=outline[0]*(1-u)*(1-v)+outline[-1]*u*(1-v)+outline[12]*(1-u)*v+outline[36]*u*v
            hit,normal,_,_=surface.ray_cast(Vector((P.x,-3.0,P.z)),Vector((0,1,0)),2)
            assert hit is not None and normal.y<-.1,(side,c,r,P,normal)
            ease=.0015*math.sin(math.pi*u)*math.sin(math.pi*v)
            vertices.append(hit+normal*(.0008+ease))
            gaps.append((vertices[-1]-hit).length)
    for r in range(rows):
        for c in range(columns):
            a=r*(columns+1)+c;b=a+1;d=(r+1)*(columns+1)+c;e=d+1
            faces.append((a,d,e,b))
    mesh=bpy.data.meshes.new('Fitted cotton rear pocket '+side)
    mesh.from_pydata(vertices,[],faces);mesh.update()
    panel=bpy.data.objects.new('Character | sewn cotton back pocket '+side,mesh)
    scene.collection.objects.link(panel)
    panel.matrix_world=pants.matrix_world.copy()
    mesh.materials.append(bpy.data.materials['Character | offwhite cotton twill'])
    for polygon in mesh.polygons:polygon.use_smooth=True
    solid=panel.modifiers.new('Pouched cotton thickness','SOLIDIFY');solid.thickness=.0006;solid.offset=-1
    bpy.data.objects.remove(seam,do_unlink=True)
    inset=[]
    for r in range(1,12):inset.append(vertices[r*(columns+1)+1])
    for c in range(2,24):inset.append(vertices[11*(columns+1)+c])
    for r in range(10,0,-1):inset.append(vertices[r*(columns+1)+23])
    stitch('Character | inset back pocket stitch '+side,inset)
    stitch('Character | pocket mouth topstitch '+side,[vertices[2*(columns+1)+c] for c in range(2,23)])
    print('POCKET_PANEL',side,len(vertices),len(faces),min(gaps),max(gaps),flush=True)

if '--render' in sys.argv:
    for label,place,target,lens,width,height in (
        ('Rear_Close',(-.75,-3.55,.82),(-.75,-2.4,.8),52,900,900),
        ('Full_Rear',(-1.45,-5.85,1.25),(-.75,-2.4,.97),58,900,990),
    ):
        data=bpy.data.cameras.new('Pocket panel '+label)
        camera=bpy.data.objects.new('Pocket panel '+label,data)
        scene.collection.objects.link(camera)
        camera.location=place
        camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.lens=lens
        scene.camera=camera
        scene.cycles.samples=20
        scene.render.resolution_x=width
        scene.render.resolution_y=height
        scene.render.resolution_percentage=100
        scene.render.filepath=str(output/('Pocket_Panel_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(camera,do_unlink=True)
scene.camera=bpy.data.objects['CAM | gameplay street']
scene['sewn_back_pocket_panels']=True
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(output/'PocketPanel.blend'),compress=True)
print('POCKET_PANEL_CANDIDATE_PASS',flush=True)
