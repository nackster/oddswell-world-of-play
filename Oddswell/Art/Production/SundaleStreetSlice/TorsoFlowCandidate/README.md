# Native torso flow and collar zipper correction

`TorsoFlow.blend` continues `CanvasWeaveCandidate/NaturalCanvas.blend` from SHA-256 `a32c6cbae8fd1767da6c03559f1addd948da46259064eb0ff85e38fedad8f50a`.

The inherited underarm tab came from a sharp change in torso-quarter skinning: an adjacent rear control followed the upper arm completely while its front neighbor mostly followed the chest. Local neighbor weight diffusion blends that transition while preserving each control's total bone influence. A graded, editable upper-torso key reduces excess cloth ease, with a maximum rest-control move of 10.632 mm. The historical jacket cage retains its original mesh; the visible jacket and refined detail cage share a derived copy.

A local native smoothing modifier gives the underarm fold a finite bend radius. Native Solidify thickness clamping avoids shell crossings in narrow regions while retaining the nominal 1.2 mm fabric thickness. Twelve upper zipper parts already follow the head bone with the standing collar; removing their redundant Surface Deform modifier prevents doubled root travel. Original controls and parent transforms remain intact.

Run `build.py`, `audit.py`, then `render.py` with Blender 4.5.5 LTS and `--python-exit-code 1 --python`. The render helper remains in `HandArticulationCandidate/render.py`; custody helpers remain in `HipSeatMotionCandidate/audit.py`. `render.py -- --preview` produces 24 frames for a two-second walking preview. The retained modifier settings are in the build report; the final native hash is in the delivery manifest and cold audit.

`cold-audit.json` compares the complete jacket shell with its anatomical support and screens nonadjacent shell intersections at render subdivision through all 49 authored integer frames. It records inherited contacts explicitly. Collar zipper distance includes the slider's physical projection from the collar: its retained maximum is about 6.82 mm, with an 8 mm bound. That is a bounded attachment check, not an assertion that every hardware vertex lies on the fabric.

Original mesh/curve controls, edges, UVs, old keys, packed maps and native rig rest/six poses are preserved. Existing shorts and footwear reports remain inherited scoped evidence. See `WholeFigureReview.md` for current visual findings. Full-body collision freedom, physical cloth simulation, animated subframes, final human realism and runtime compatibility remain open.
