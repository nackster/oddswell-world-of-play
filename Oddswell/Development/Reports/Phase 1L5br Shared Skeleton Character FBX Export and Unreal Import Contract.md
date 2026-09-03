# Phase 1L.5br — Shared-Skeleton Character FBX Export and Unreal Import Contract

Date: 2026-09-03
Status: **COMPLETE LOCALLY — FAIL-CLOSED EXPORT/IMPORT CONTRACT ONLY; NO FBX, UASSET, OR RUNTIME CHANGE**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5br advances roadmap Phase 1L items 1–2 and [[Design/Beta Game Bible#Avatar and clothing]] after the completed walk/run/jump/land source proofs. It adds one machine-readable contract, `Oddswell/Art/Production/PlayerCharacter/character_fbx_unreal_contract.json`, without changing the exact Phase 1L.5bq Blender source or generating an export/import artifact.

The contract freezes the smallest truthful later handoff: one shared 12-bone skeleton, four separately replaceable skeletal meshes, and four animation-only files. Keeping starter top and bottom separate preserves independent replacement; keeping the Signal Jacket separate preserves its role as the authorized alternative presentation.

## Frozen source custody

| Input | Identity |
| --- | --- |
| Landing `.blend` | `B837C11190DE64F5848F4880FA0098473DFAA3C8BA4E5D8564566587E11721FE` |
| Landing custody manifest | `499A4622BF744B936513BD6BC42309A3C83FB1D52DA70C4196FB5D4C2B898ABC` |
| Landing semantic | `A2AA26058CD05C948CE7F4E9BAB7F9B5E926F8318436B9079BE51094A680102E` |
| Contract file | `3DAA1D94A19148F03D31682D15B2FA40D9D43133008A1DA099097FCC4AAD88C6` |

Exact geometry identities are mannequin `3ADB62F5…`, starter top `0E0E1EA3…`, starter bottom `1D170FE2…`, and Signal Jacket `07050BB4…`. Exact Action identities remain walk `5CC1C4A3…`, run `AA170766…`, jump `B3F55824…`, and land `34BB5D6C…`.

## Contract

| Predicate | Frozen requirement |
| --- | --- |
| Skeleton | exactly one `ARMATURE__shared_bilateral_v1`; exact 12 names; no rename/addition |
| Meshes | body, starter top, starter bottom, and Signal Jacket remain four distinct identities |
| Animation | exactly walk/run/jump/land; root translation zero for every key |
| Coordinates | source meter; Unreal centimeter; `-Y` forward; `Z` up; scale `1`; stature `180 cm` |
| Partition | exactly eight FBXs: four skeletal meshes plus four animation-only files |
| Integrity | deterministic filenames and one uppercase SHA-256 sidecar per binary; repeat hash required |
| Unreal | intended `/Game/OddsWell/Characters/Player/...` paths; every asset reuses one skeleton |
| Failure | missing, extra, renamed, mismatched, non-finite, unweighted, or hash-divergent output stops before import |

The player-facing risk reduced is accidental scale drift, duplicate skeletons, lost clothing replaceability, or animation trajectory taking authority from native `ACharacter` during a later import.

## Verification

| Gate | Result |
| --- | --- |
| Focused source/contract validation | PASS — exact source hashes; skeleton `1`; bones `12`; meshes `4`; animations `4`; partitions `8`; root translation `0`; fail-closed `true`; FBX `0`; UAsset `0` |
| Documentation/canvas/client diff | PASS |
| Native Unreal regression | PASS — fresh `74/74`, failures `0`, test warnings `0`, natural Queue Empty/TestExit, exit `0`; log SHA-256 `88D2565396B9A99D64979D9CEEA03C86FA086214AF07F207CE10448F4054D862`; report JSON `3A4C80BDD6A0E2F71368455DD3C1E2AF6D8F6F5314797E654E8F3EBA94E4DF5A` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains `50` files / `1,052,124,588` bytes / Python `0`; wrapper `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first focused-validation command used contract-friendly names (`starter_top`) directly against predecessor custody keys (`starter_offwhite_top`) and stopped before any mutation. Mapping those labels explicitly to their exact custody keys made the check pass; the contract itself did not change because its player-facing labels and source object names were already exact.

## Hard boundary

This phase creates no FBX, UAsset, Blender mutation, new rig, bone, Action, geometry, clothing, retargeting framework, Unreal source/config/map/package-input change, runtime replacement, movement/capsule/camera/replication/save change, authority/economy/wager/simulator/brain change, external or paid input, final-art claim, beta-readiness claim, or Version 1 claim. Export and import require a separate Scope Director gate.
