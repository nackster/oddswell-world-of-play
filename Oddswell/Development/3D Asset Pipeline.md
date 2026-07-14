---
tags:
  - development
  - art
  - 3d
  - pipeline
status: active
---

# 3D Asset Pipeline

## Production decision

Blender is the permanent source of truth for OddsWell 3D assets. AI-generated models are first passes until they have been reviewed and completed in Blender.

## Tool responsibilities

| Tool | Status | Responsibility |
| --- | --- | --- |
| Higgsfield | Available | Consistent character turnarounds, expressions, clothing, item concepts, and presentation references. |
| Meshy | Pilot | First-pass image-to-3D generation for props, furniture, vehicles, and environment pieces. |
| Blender | Primary | Modeling, sculpting, retopology, UVs, materials, LODs, collision, optimization, rig review, and final export. |
| Rigify | Primary rigging | Controllable Blender character rigs for main production characters. |
| AccuRIG | Fast alternative | Quick automatic humanoid rigging for imported or experimental meshes. |
| Character Creator + Headshot | Deferred | Optional human bases, faces, and high-volume NPC production if the approved style benefits from it. |
| TRELLIS.2 / Hunyuan3D | Later evaluation | Possible private, local image-to-3D generation on project servers after hardware and output-quality benchmarking. |
| Game-engine retargeting | Pending engine choice | Runtime skeleton mapping, animation retargeting, validation, and final in-engine setup. |

## Main-character workflow

1. Approve the style in [[Art/Visual Consistency]].
2. Create a controlled Higgsfield turnaround: front, side, back, face, expressions, clothing, scale, and colors.
3. Model or rebuild the production mesh in Blender.
4. Complete clean animation topology, UVs, materials, and optimization.
5. Rig with Rigify; use AccuRIG only when it provides a useful faster starting point.
6. Export and validate deformation, animation retargeting, materials, and performance in the selected game engine.

## Prop and environment workflow

1. Approve a concept image and its world-style assignment.
2. Generate a first-pass model in Meshy.
3. Review silhouette, scale, polygon count, topology, UVs, and PBR materials.
4. Clean and optimize the approved asset in Blender.
5. Add LODs and collision appropriate to the asset class.
6. Export and validate it in the selected game engine.

## Quality gate

No generated asset becomes production-ready until it passes:

- Visual-style comparison against approved references.
- Clean topology and deformation review where applicable.
- UV and material review.
- Scale, pivot, naming, and folder-convention review.
- Polygon, texture-memory, LOD, and collision budgets.
- In-engine lighting, animation, and performance validation.

## Pilot benchmark

Before scaling production, process one main character and one representative city prop end to end. Record generation time, cleanup time, visual fidelity, topology quality, material quality, performance, and revision difficulty.

## References

- [Meshy game-asset workflow](https://docs.meshy.ai/en/webapp/guides/use-cases/game-assets)
- [Blender Rigify](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html)
- [Reallusion AccuRIG](https://actorcore.reallusion.com/static-page/auto-rig/pre_page/accurig/accurig.html)
- [Reallusion Headshot](https://www.reallusion.com/character-creator/headshot/photo-to-3d-head.html)
- [Microsoft TRELLIS.2](https://github.com/microsoft/TRELLIS.2)
- [Tencent Hunyuan3D 2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)
