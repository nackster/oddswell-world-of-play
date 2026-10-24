# Phase 1L.5bt — Character Unreal Import and Handoff Corrections

Date: 2026-09-12
Status: **COMPLETE LOCALLY - SAVED ASSET HANDOFF AND REGRESSIONS PASS**
Cost: **$0.00**

## Outcome

Resumed the failed character import from the **Verify game plans** task after the owner asked to continue. Unreal now contains exactly one shared skeleton, four separate skeletal meshes (body, starter top, starter bottom, Signal Jacket), and four animation sequences (walk, run, jump, land) at the established `/Game/OddsWell/Characters/Player/` paths.

This advances roadmap Phase 1L, Avatar and clothing in the Beta Game Bible, and the DEC-034 character bridge. It reduces the risk that the authored character cannot pass from Blender to the actual engine with its scale, clothing partitions, bone relationships, and motion intact. It does not yet replace the runtime primitive pawn.

## Corrections backed by measured failures

1. **Bone names:** DEC-035 explicitly maps the eight dotted limb names to Unreal underscores. The twelve source bones and their hierarchy are unchanged. Observed animation-track casing follows Unreal FName identity.
2. **Authored timing:** the old exporter used the landing scene's 30 fps for every Action. Both old walk and run FBXs lasted about 0.666667 seconds. The corrected handoff uses the source's 28 fps walk, 44 fps run, and 30 fps jump/land.
3. **Unit conversion:** the legacy importer defaults to no scene-unit conversion. Import now explicitly converts meters to centimeters at uniform scale 1; measured body height is exactly 180 cm.
4. **Wrapper track:** the long Blender object name became an extra animation track. The temporary export object is named `Armature`, activating Unreal's existing Blender wrapper removal. No source bone or saved Blender object is renamed.
5. **Final run frame:** integer FBX tick rounding and downstream precision caused the 20-frame run interval to import as 19 frames. Outward float32-safe time-span serialization preserves the final frame. Each interval adjustment is below 0.0000001 seconds; authored pose keys are unchanged. Imported integer frame counts are checked against the source contract, rather than accepting a visually plausible shortened clip.

The original Blender source, original handoff contract, and historical eight-file export set remain unchanged. The corrected exports live in `CharacterFBXTimingCorrection`, with a separate manifest and hash sidecars. The new importer verifies hashes before importing, refuses destination overwrites, and accepts only the exact complete set. Earlier failed attempts remain diagnostic and have no completion credit. Their sole saved skeleton files were moved out of Content into the attempt evidence directory; no unrelated assets were removed.

## Saved-asset evidence

| Check | Measured result |
| --- | --- |
| Asset partition | 1 Skeleton + 4 SkeletalMesh + 4 AnimSequence = 9 UAssets |
| Shared skeleton | Exact reference reused by every mesh and animation |
| Hierarchy | All 4 meshes retain the mapped 12-bone hierarchy |
| Body stature | 180.0 cm |
| Walk | 20 frame intervals at 28 fps; 0.714285731 seconds; approximately 18-degree maximum rotation change |
| Run | 20 frame intervals at 44 fps; 0.454545468 seconds; approximately 30-degree maximum rotation change |
| Jump and land | 10 frame intervals each at 30 fps; 0.333333343 seconds each |
| Poses | All sampled translation, rotation, and scale components finite; all clips contain changing rotations |
| Root translation | Exactly 0 cm in every sampled frame of every clip |
| Independent export repeat | 17/17 binary, sidecar, and manifest files unchanged; process exit 0 |
| Fresh editor reopen | PASS; 9/9 assets revalidated; asset hash changes 0; process exit 0 |
| Full native regression | 74 clean successes; 0 warning-successes; 0 failures; process exit 0 |
| Python regression | 105/105 tests passed: Phase 0A 9, 0B 2, 0C 8, 0D 46, 1H 40 |
| Brain Admin | Self-check passed |
| Windows asset cook | Exit 0; 0 errors/warnings; all 9 character packages in the cooked referenced set |

Raw attempt evidence is retained in `client/OddsWell/Saved/CharacterImport20260912/`: the accepted import is `import9.json` / `import9.log`; the independent load is `reopen.json` / `reopen.log`; native results are `AutomationReport/index.json`. Process-exit files are retained separately because Unreal may exit zero after a Python error. Accepted results require both a PASS report and an explicit log marker.

The durable `Art/Production/PlayerCharacter/UnrealImport/character_import_evidence.json` records artifact hashes and verification summaries. The source scripts include repeatable export and cold-import checks; they add no runtime Python dependency or project plugin setting.

## Local toolchain compatibility

The Codex-managed interpreter at the already fixed path advanced from Python 3.12.13 to 3.12.14. The local supervisor correctly rejected that mismatch. This checkpoint updates only its exact patch-version pin and the two downstream supervisor checksum references (including the seal supervisor checksum). The fixed 28-file simulator/brain manifest remains `6a92c3067e2cab3a14e70accd5f6c4b3bcf4df9b8cddbb3413950ea2301c137c`; no gameplay module, interpreter search, version range, retry rule, or process authority changed. The affected 40-test suite passes after the integrity chain is updated. DEC-019 records the compatibility update separately from historical evidence.

The Windows cook used the engine Entry map plus the character directory and configured dependencies. All nine character package names are present in its referenced set. This is asset cook compatibility evidence, not a fresh packaged game or visual playtest.

## Visual direction and remaining work

The owner's new requirement is explicit in [[Art/Visual Consistency]]: an ordinary screenshot should communicate **this is OddsWell** through a coherent visual identity. Character silhouette, clothing, architecture, material treatment, lighting, and interface should work together. Recognition cannot depend on a logo or title. The later accepted six-district planning concept remains the city ambition; the smaller measured graybox remains the production route until a layout change is approved.

The imported mannequin remains a primitive production candidate. This phase does not prove final art, material quality, on-screen clothing fit, runtime animation blending, multiplayer clothing behavior with these meshes, packaged character performance, first-hour usability, or beta readiness. Runtime source, movement, camera, collision, appearance IDs, saves, economy, wagering, and simulation are unchanged.

Next character milestone: wire the accepted skeletal visuals and clips to the existing movement/equipment paths, then verify them in Sundale and a packaged build. Follow that with one coherent character-and-street art composition for owner review before expanding the final asset family. Phase 1K integration, Phase 1L accessibility/performance, and Phase 1M beta-exit evidence remain incomplete; Version 1 stays inactive.
