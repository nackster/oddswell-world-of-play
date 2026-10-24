# Phase 1L.5bk — Deterministic Mannequin Skin Binding and Static Deformation Proof

Date: 2026-09-01
Status: **COMPLETE LOCALLY — ADDITIVE SKIN-BINDING/STATIC-DIAGNOSTIC SOURCE ONLY; NOT ANIMATION OR RUNTIME**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bk advances [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]] with the smallest deterministic binding proof for the accepted shared-skeleton candidate. It derives `Oddswell/Art/Production/PlayerCharacter/SkinnedSharedSkeletonCandidate/SkinnedSharedSkeletonCharacterCandidate.blend` from the exact retained Phase 1L.5bj source without rewriting that accepted source.

All `302` mannequin vertices are assigned explicitly across the exact `12` accepted bone groups. Each disconnected primitive component has one rigid `1.0` bone influence, so unweighted vertices, non-normalized vertices, and vertices above one influence are all `0`. Exactly one armature modifier links the unchanged mannequin geometry to the unchanged armature.

A bounded static diagnostic rotates only the accepted shoulder, elbow, hip, and knee bones. It moves `228` vertices with maximum `.151338 m` displacement, produces one readable diagnostic render, and is then cleared. The additive `.blend` is retained in rest pose. This reduces the player-facing risk that the primitive production source cannot follow its shared skeleton, but it does not prove animation or locomotion.

## Source custody and preserved contract

| Surface | Evidence |
| --- | --- |
| Accepted 1L.5bj `.blend` | unchanged SHA-256 `27D4F7D5585B7AACD90AEF9A03D0426E5415EF2C17F002F79C832F080F9D9F80` |
| Accepted 1L.5bj manifest | unchanged SHA-256 `63A839B581E8DB21F4F98861D734372A79581126F542174022ACA950B6060A95` |
| Base geometry | unchanged identity `3ADB62F5D9577FDE2E45D8FFA45B5AB448D088D72A239496D5170122473F8FE3`; `302` vertices / `354` polygons / `540` triangles |
| Character contract | one faceless neutral `1.80 m` mannequin; exact eight presets, four tones, eight landmarks |
| Armature | exact one shared bilateral armature; `12` unchanged bone names, landmarks, and hierarchy |
| Scene | exact one mannequin, one armature, one review camera; clothing meshes `0` |

## Binding and static proof

| Predicate | Result |
| --- | --- |
| Vertex groups | exact `12`, one per accepted bone; every group nonempty |
| Vertex coverage | `302/302`; unweighted `0` |
| Normalization | every vertex total `1.0`; non-normalized `0` |
| Influence bound | exactly one influence per vertex; maximum `1` |
| Modifier | exact one armature modifier; vertex groups enabled; envelopes/preserve-volume disabled |
| Static joints | shoulders, elbows, hips, knees only |
| Static result | moved vertices `228`; maximum displacement `.151338 m`; delta identity `61819BDCAAC79CC8F86AEE354AE9B74B2FF0F4F5D3045BA1AA47A4EB9352C005` |
| Saved pose | clear rest pose |
| Actions / NLA / clips | `0 / 0 / 0` |

Semantic identity is `8F86A1FE89E9975C75B31D6700FA3FD64A98F87139C2C7DF0B721197ED25F146`. Machine-readable custody manifest SHA-256 is `09BCC9BFDA60E1F7FE6F0288D52AA8C4FA22671653C2A190D96A682802CF9751`. Rest render SHA-256 is `21735DCBC14B42D43659CD3D0679DA814BDEA12F2D4ECC6BEFF9611599D58E61`; static diagnostic render SHA-256 is `CDCAE381CC14D33776CBDF264ABB810520B53D1E377CEC8427381FA85E973E59`.

The full additive build reproduced semantic, custody-manifest, rest-render, and diagnostic-render identities exactly. Saved-source reopen and focused deformation validation also passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender build/binding/static diagnostic | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Rest/static visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and process exit `0`; report JSON SHA-256 `25D034213949AE01ACB45818215A10C0272F8C264ACF698A18286AA4424BEA27` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

## Hard boundary

The static local-axis pose is diagnostic evidence only and is cleared from the retained source. This phase creates no Action, NLA track, motion clip, walk/run/jump/land proof, clothing refit, control rig, IK, constraint, driver, shape key, FBX/export, Unreal import, client/map/config/package input, runtime replacement, external asset, paid input, final-art claim, beta-readiness claim, or production-readiness claim. Existing movement, collision capsule, camera, replication, persistence, economy, wagering, simulator, brain behavior, and frozen Phase 0 simulation remain unchanged.
