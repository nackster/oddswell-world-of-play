# Phase 1L.5bs — Deterministic Eight-File Character FBX Export and Source-Custody Proof

Date: 2026-09-03
Status: **COMPLETE LOCALLY — EXACT EIGHT-FILE DETERMINISTIC FBX EXPORT PROOF ONLY; NOT UNREAL IMPORT OR RUNTIME**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bs advances roadmap Phase 1L items 1–2 and [[Design/Beta Game Bible#Avatar and clothing]] after the frozen 1L.5br handoff contract. `Oddswell/Art/Production/PlayerCharacter/CharacterFBXExport/` exports only the exact retained 1L.5bq Blender source into the contract’s minimum eight-file partition.

Four skeletal-mesh FBXs keep the mannequin body, starter top, starter bottom, and Signal Jacket separately replaceable while carrying the same shared skeleton. Four animation-only FBXs carry the exact walk, run, jump, and land Actions. Every binary has one uppercase SHA-256 sidecar.

## Source and topology custody

| Predicate | Evidence |
| --- | --- |
| Source blend | `B837C11190DE64F5848F4880FA0098473DFAA3C8BA4E5D8564566587E11721FE` |
| Source manifest | `499A4622BF744B936513BD6BC42309A3C83FB1D52DA70C4196FB5D4C2B898ABC` |
| Source semantic | `A2AA26058CD05C948CE7F4E9BAB7F9B5E926F8318436B9079BE51094A680102E` |
| Frozen contract | `3DAA1D94A19148F03D31682D15B2FA40D9D43133008A1DA099097FCC4AAD88C6` |
| Shared skeleton | exactly one retained skeleton; exact 12 bones; leaf bones `0` |
| Mesh partition | exactly body, starter top, starter bottom, Signal Jacket |
| Animation partition | exactly walk/run/jump/land; root translation `0` |
| Coordinates | source meter, Unreal centimeter, `-Y` forward, `Z` up, scale `1`, stature `180 cm` |

## Deterministic outputs

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `SK_OddsWell_PlayerBody_v1.fbx` | 55,724 | `79A327DADFC90BD16C44BA955E4FF24AA12EA2011D8A686C5E6FDD4006F2CE87` |
| `SK_OddsWell_StarterTop_v1.fbx` | 39,004 | `011839AFAB6C673CEB1EABA2DFADB8A63690131A4E57FA9EDD7C08DCDDC42D04` |
| `SK_OddsWell_StarterBottom_v1.fbx` | 40,476 | `3C8FFB1383D237638CA8179BA9FC3C838BEAF2D40F19EA4595E37BBC3D223F4B` |
| `SK_OddsWell_SignalJacket_v1.fbx` | 40,316 | `416D0FACBC9235DC51BAC6A45D4A2E31C1D7B73666125E437F620EBA42F9CC92` |
| `AN_OddsWell_Walk_v1.fbx` | 109,500 | `0F81CD6A8D630643D97AC4CE4FA56DFC90B878D4771213535DAADF7993974220` |
| `AN_OddsWell_Run_v1.fbx` | 109,500 | `422AECEC36CDFF2258B683776537EB25254A3DD8B3D52EE834B34281FC6DFAAE` |
| `AN_OddsWell_Jump_v1.fbx` | 98,972 | `B54F3943FBF62031A13BE99832148175F2684829E73BAA4FEB5E51E7BC525855` |
| `AN_OddsWell_Land_v1.fbx` | 98,972 | `C80D54AE6156353B640091CF05D78E5E47E315D16D5A02A863CA5CA817C7CDCD` |

The builder fixes the FBX creation timestamp and derives FBX object identifiers from stable exact keys. Two same-path passes inside each build and two independent Blender invocations reproduce all eight binaries, sidecars, and custody evidence with changed-file count `0`. Export custody manifest SHA-256 is `81EF175D7600D188E06305FAB5DD0366BE1AD0D4093C9F77C3C8CBAF135F2433`.

## Verification

| Gate | Result |
| --- | --- |
| Focused FBX/source/contract/sidecar validation | PASS — skeleton `1`, bones `12`, meshes `4`, animations `4`, FBX `8`, sidecars `8`, repeat hashes equal, root translation `0`, leaf bones `0`, UAsset/import/runtime/client `0` |
| Independent deterministic rerun | PASS — `0/19` export/evidence files changed |
| Native Unreal regression | PASS — fresh `74/74`, failures/test warnings `0`, natural Queue Empty/TestExit, exit `0`; log `34BC4F28604F4B634E06D85AD16650BEC7F07DA8BAD2F3C412FEDD6E3DBE3336`; report JSON `282AD9FD409D28246FA9F48C9EB377A480F6BB725ACF241DB4D5AE499601FC85` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains `50` files / `1,052,124,588` bytes / Python `0`; wrapper `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first two determinism attempts correctly stopped before accepting outputs: Blender’s FBX header timestamp differed between passes, then process-randomized FBX object identifiers differed between independent launches. Freezing the timestamp, stable identifier derivation, and output path made both the in-process and independent gates pass. One intermediate same-directory copy attempt deleted staged FBXs before manifest completion and also stopped without accepted evidence; the builder now keeps same-path outputs in place. No retained source or runtime file changed during these corrections.

## Hard boundary

This phase performs no Unreal import and creates no UAsset. It changes no Blender source, rig, bone, Action, geometry, clothing, Unreal source/map/config/package input, runtime character, movement, capsule, camera, replication, persistence, authority, economy, wager, simulator, brain, external/paid input, final-art status, beta-readiness status, or Version 1 status. Import remains a separate gate.
