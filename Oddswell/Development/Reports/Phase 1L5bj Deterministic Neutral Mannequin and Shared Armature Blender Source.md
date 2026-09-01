# Phase 1L.5bj — Deterministic Neutral Mannequin and Shared-Armature Blender Source

Date: 2026-09-01
Status: **COMPLETE LOCALLY — DETERMINISTIC SOURCE/REVIEW EVIDENCE ONLY; NOT SKINNED, ANIMATED, EXPORTED, OR IMPORTED**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bj advances [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]] and the Phase 1L character-production bridge with the smallest source that satisfies the frozen DEC-034 contract. `Oddswell/Art/Production/PlayerCharacter/SharedSkeletonCandidate/SharedSkeletonCharacterCandidate.blend` contains exactly one faceless non-anatomical neutral `1.80 m` mannequin and exactly one shared bilateral armature. The armature has `12` bones and represents the exact eight accepted landmark heights.

The mannequin uses the arithmetic midpoint of each corresponding horizontal dimension from the two Phase 1L.3g review silhouettes: shoulder half-width `.245 m`, elbow `.280 m`, wrist `.265 m`, hip `.155 m`, knee/ankle `.130 m`, torso `.455 x .250 m`, and pelvis `.350 x .240 m`. Its source metadata preserves all eight existing gameplay-identical preset IDs and all four approved tone values/materials.

This reduces the player-facing beta risk that the eight appearance presets diverge at the first production-source boundary. It does not make the character playable or production ready.

## Artifacts

| Artifact | Purpose |
| --- | --- |
| `build_shared_skeleton_candidate.py` | Original deterministic Blender 4.5.5 LTS builder and focused validator |
| `SharedSkeletonCharacterCandidate.blend` | One mannequin, one armature, and one review camera |
| `manifest.json` | Machine-readable contract, semantic identity, counts, hashes, and zero-surface boundaries |
| `PROVENANCE.md` | `$0` original-source provenance and explicit exclusions |
| `renders/Review_Front.png` | Front review view |
| `renders/Review_Side.png` | Side review view |
| `renders/Review_ThreeQuarter.png` | Three-quarter review view |

## Exact source evidence

| Surface | Evidence |
| --- | --- |
| Mannequin | `1`; faceless; non-anatomical; neutral; floor `0.00 m`; crown `1.80 m`; `302` vertices / `354` polygons / `540` triangles |
| Armature | `1`; shared bilateral; `12` bones; no parenting to mannequin |
| Identity | exact presets `8`; tones/materials `4`; silhouette `1` |
| Landmarks | ankle `.10`; knee `.53`; hip `.94`; wrist `.78`; elbow `1.12`; shoulder `1.45`; head center `1.66`; crown `1.80 m` |
| Scene | `3` objects: mannequin, armature, review camera |
| Semantic SHA-256 | `C34CD757A694EC897350350BA1B977A67EFCE6B8E959799992559DB9A0A54860` |
| Manifest SHA-256 | `63A839B581E8DB21F4F98861D734372A79581126F542174022ACA950B6060A95` |
| Front render SHA-256 | `21735DCBC14B42D43659CD3D0679DA814BDEA12F2D4ECC6BEFF9611599D58E61` |
| Side render SHA-256 | `F36336F949EE802E2C6740A1DD5D0095B228CDF5A30E721CD742947A45A9177C` |
| Three-quarter render SHA-256 | `144CFDC7078272A3CEA6B23875A10F6EF0942D973A6BA1C1832ED5962AE3B25E` |

The deterministic rerun reproduced the semantic, manifest, and all three render identities exactly. Blender `.blend` identity is intentionally semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Fresh Blender build and internal validation | PASS — exact `1` mannequin, `1` armature, `12` bones, `4` materials, `8` presets, `8` landmarks, `1.80 m` stature, and all prohibited surfaces `0` |
| Deterministic rerun | PASS — semantic, manifest, and three render SHA-256 identities reproduced exactly |
| Saved-source reopen validation | PASS — semantic/manifest/render identities match the retained `.blend` |
| Front/side/three-quarter visual review | PASS — one faceless neutral primitive mannequin is fully framed and readable in all views |
| Focused contract/wiki/canvas checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and process exit `0`; report JSON SHA-256 `4249A57807696240BB36CCA7BF36FAB59970F465E1CCDA4C22D7710515DFA738` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

## Hard boundary

There is no mannequin-to-armature parenting, skin weight, vertex group, deformation, control rig, IK, constraint, driver, shape key, clothing refit, animation, action, FBX/export, Unreal import, runtime/client/map/config/package-input change, external asset, paid input, or final-art claim. Existing movement, collision capsule, camera, replication, persistence, economy, wagering, simulator, brain behavior, and frozen Phase 0 simulation remain unchanged. Any following character-production or integration step requires a separately selected and verified roadmap gate.
