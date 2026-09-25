"""Measure where the retained upper shorts still exceed the posed pelvis."""
import bpy
import sys
from pathlib import Path
from statistics import median
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out=Path(__file__).resolve().parent
source=Path(sys.argv[sys.argv.index('--scene')+1]) if '--scene' in sys.argv else out/'PelvicCotton.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
pants=bpy.data.objects['Character | shorts leg continuous tailoring']
pelvis=bpy.data.objects['Character | posed pelvic fitting support']
cloth=BVHTree.FromObject(pants,bpy.context.evaluated_depsgraph_get())
body=BVHTree.FromObject(pelvis,bpy.context.evaluated_depsgraph_get())

def hit_world(obj,tree,start,direction):
    inverse=obj.matrix_world.inverted()
    position,_,_,_=tree.ray_cast(inverse@start,(inverse.to_3x3()@direction).normalized())
    return obj.matrix_world@position if position is not None else None

for side,start_y,step in (('rear',-3,1),('front',-1,-1)):
    direction=Vector((0,step,0))
    # Above 0.88 m the open waist can make the ray hit the opposite panel.
    for z in (.78,.80,.82,.84,.86,.88):
        samples=[]
        for index in range(33):
            x=-.99+index*.015
            start=Vector((x,start_y,z))
            outer=hit_world(pants,cloth,start,direction)
            inner=hit_world(pelvis,body,start,direction)
            if outer is not None and inner is not None:
                clearance=(inner.y-outer.y)*step
                samples.append(clearance)
        if samples:
            print('UPPER_COTTON_EASE_MM',side,z,'count',len(samples),
                  'negative',sum(value<0 for value in samples),
                  'min',round(min(samples)*1000,1),'median',round(median(samples)*1000,1),
                  'max',round(max(samples)*1000,1),flush=True)
print('UPPER_COTTON_EASE_MEASURED',flush=True)
