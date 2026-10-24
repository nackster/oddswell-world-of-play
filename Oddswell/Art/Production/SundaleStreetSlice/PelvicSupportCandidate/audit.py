import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'PelvicSupport.blend'))
scene=bpy.context.scene
pelvis=bpy.data.objects['Character | posed pelvic fitting support']
legs=bpy.data.objects['Character | anatomical legs']
torso=bpy.data.objects['Character | internal torso support']
source=[pelvis.matrix_world@v.co for v in pelvis.data.vertices]
visible=[legs.matrix_world@v.co for v in legs.data.vertices]
for side in (-1,1):
    for label,collection in (('pelvis',source),('legs',visible)):
        points=[p for p in collection if .66<p.z<.68 and (p.x+.75)*side>.02]
        assert len(points)>=8,(side,label,len(points))
        print('PELVIC_LOWER',side,label,'count',len(points),'x',round(min(p.x for p in points),4),round(max(p.x for p in points),4),'y',round(min(p.y for p in points),4),round(max(p.y for p in points),4),flush=True)
tree=BVHTree.FromObject(torso,bpy.context.evaluated_depsgraph_get())
leg_tree=BVHTree.FromObject(legs,bpy.context.evaluated_depsgraph_get())
leg_inverse=legs.matrix_world.inverted()
for zmin,zmax in ((.62,.66),(.66,.68),(.68,.70),(.70,.74)):
    distances=[]
    for p in source:
        if not zmin<p.z<zmax:continue
        hit,normal,_,distance=leg_tree.find_nearest(leg_inverse@p)
        if hit is not None:distances.append(distance)
    if distances:
        distances.sort()
        print('PELVIC_LEG_CONTACT',zmin,zmax,'n',len(distances),'median_mm',round(distances[len(distances)//2]*1000,2),'max_mm',round(distances[-1]*1000,2),flush=True)
inverse=torso.matrix_world.inverted()
for zmin,zmax in ((.82,.84),(.84,.86),(.86,.88),(.88,.90),(.90,.93)):
    distances=[]
    for p in source:
        if not zmin<p.z<zmax:continue
        hit,normal,_,distance=tree.find_nearest(inverse@p)
        if hit is not None:distances.append(distance)
    assert distances
    distances.sort()
    print('PELVIC_UPPER',zmin,zmax,'n',len(distances),'median_mm',round(distances[len(distances)//2]*1000,2),'max_mm',round(distances[-1]*1000,2),flush=True)
print('PELVIC_SUPPORT_AUDIT_PASS',flush=True)
