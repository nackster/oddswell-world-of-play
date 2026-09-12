---
tags:
  - decision
  - character
  - phase-1l
status: implementation-decision
date: 2026-09-12
---

# DEC-035 Character Unreal Bone Name Mapping

## Context and authority

After reviewing the prior task's import blocker, the owner asked to pick up the work and continue on 2026-09-12. The implementation follows the previously recommended explicit Unreal mapping while preserving Blender names. This is an engineering choice under that continuation request; the owner did not separately select or quote a naming option.

The previous Unreal import log records `thigh.L` becoming `thigh_L`, with the same conversion for the other seven dotted limb names. The old exact-name check rejected those assets, which were removed. That historical failure remains unchanged.

## Decision

Retain the frozen Blender source, eight exported FBXs, and original `character_fbx_unreal_contract.json` byte-for-byte. Add `character_unreal_import_contract.json` to state the exact twelve-entry source-to-Unreal mapping. The four undotted names remain identical; each of the eight dotted limb names uses an underscore in Unreal.

The mapping must be one-to-one, preserve every parent relationship, and apply consistently to the body, three clothing meshes, and four animations on one shared skeleton. No additional or missing bone, arbitrary rename, scale adjustment, or root motion is accepted. The import validator checks saved assets again in a fresh editor process.

## Measured handoff corrections

Inspection during the resumed phase found that the original exporter used the final scene's 30 fps for the retained 28 fps walk and 44 fps run Actions. A separate `CharacterFBXTimingCorrection` set now uses each Action's authored rate; the historical exports remain untouched. This is a defect correction, not a change to the authored motion or its source files.

The temporary export object wrapper uses the standard `Armature` name so Unreal's Blender compatibility path excludes it from animation bone tracks. No source bone is renamed and the Blender file is never saved. Import explicitly converts source meters to Unreal centimeters with uniform scale 1. The animation interval is rounded outward to a float32-safe FBX tick span (less than 0.0000001 seconds); the imported integer frame counts and authored durations must still match. This prevents loss of the final run frame through importer rounding. Unreal's case-insensitive FName semantics are used only when comparing observed animation-track casing.

Installed engine evidence: `FbxMainImport.cpp` contains `FFbxImporter::MakeName` (dot-to-underscore mapping) and the Blender `armature` wrapper exception; `SkeletalMeshEdit.cpp` sets animation frame counts from the imported time interval. The phase report records the rejected attempts and successful saved-asset evidence.

## Scope

### Runtime verification corrections — September 12, 2026

The owner's subsequent ten-step goal exposed two further handoff defects. Mesh import scale remains 1, but animation-only import must explicitly use scale 100 to retain the skeleton's meter-to-centimeter bind scale after the Armature wrapper is removed. The evaluated head must remain at 166 cm in neutral pose. The original local-Y curves also twisted limbs without moving the knees; a derivative changes the four existing Actions to local-X pitch, preserving key times and angle values. Original Blender/FBX sources remain historical evidence. `CharacterMotionAxisCorrection` is the current derivative handoff. These are measured corrections to the approved four motions, not additional animation or a new silhouette. See [[Development/OddsWell Next Ten Steps 2026-09-12]].

Resume the isolated asset-import phase. This decision does not change movement, capsule collision, camera, networking, saves, game simulation, wagering, or the economy. Runtime wiring is the subsequent character integration step. The mannequin remains a production candidate, not approved final art or beta-readiness evidence.

See [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]], [[Development/Reports/Phase 1L5bs Deterministic Eight File Character FBX Export and Source Custody Proof]], and [[Art/Visual Consistency]] for the new screenshot-recognition requirement.
