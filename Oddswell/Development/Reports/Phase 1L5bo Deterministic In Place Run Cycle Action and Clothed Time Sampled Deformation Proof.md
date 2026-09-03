# Phase 1L.5bo — Deterministic In-Place Run-Cycle Action and Clothed Time-Sampled Deformation Proof

Date: 2026-09-03
Status: **COMPLETE LOCALLY — RETAINED WALK PLUS EXACT ONE IN-PLACE RUN ACTION/TIME-SAMPLED SOURCE PROOF ONLY; NOT UNREAL OR FINAL ANIMATION**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bo advances roadmap Phase 1L items 1–2 after 1L.5bn and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey item 1]] plus [[Design/Beta Game Bible#Avatar and clothing]]. It derives `Oddswell/Art/Production/PlayerCharacter/RunCycleCandidate/RunCycleCharacterCandidate.blend` from the exact retained Phase 1L.5bn source and leaves every predecessor byte unchanged.

The source preserves exact `walk_candidate_v1` and adds only `run_candidate_v1`. The run's frames `1–21` at `44 fps` reproduce the accepted Phase 1L.5bg primitive run basis at exact `2.2` cycles/second. Left/right upper arms and thighs pitch oppositely up to `30°`; three root-location curves stay exact zero; start/end Action values and evaluated mesh coordinates are equal. One bounded `5°` spine counter-sway lets both torso-bound garment alternatives participate without adding a control rig or root motion.

Five time samples prove finite bounded deformation for the mannequin and both authorized presentations. Four deterministic review frames show frames `6` and `16` for starter top/bottom and Signal Jacket/bottom. The saved source remains at clear run-loop start frame `1`.

## Source custody

All eight Phase 1L.5bn files remain exact: builder `9F8D53CC316D1B5C211132C50907C6C965F37952AC91620896F1A543E76A107E`, provenance `46042F992B14BA33632A16E152EEEEF9F9F004FFFE4E60CF8B8C753EEF92AE45`, manifest `F5677DA0726B9FD050C206A984174F91CE933AC537A7E2383A98B1A786DFF575`, `.blend` `FCADE6F5004730F1A5307F75BEB75D54ADA33F7ECD285B52F44F6165B2B07F9C`, and retained review renders `B2CA11E3…`, `DEB37B22…`, `F0BAA823…`, `7C268195…`.

Mannequin geometry, exact `1.80 m` stature, eight presets/four tones, landmarks, 12-bone names and hierarchy, skin weights, starter clothing, Signal Jacket identity/materials, and walk Action identity `5CC1C4A368F9CEC7FD1AED67004D3C40E5D920FC353B8141422C54DDE2E97C58` remain semantically exact.

## Action and deformation proof

| Predicate | Evidence |
| --- | --- |
| Actions | exactly retained `walk_candidate_v1` plus new `run_candidate_v1` |
| Run Action identity | `AA1707665B79313DABFD33142F99391CA9A144B37A7E217597633EA7E5E4E115` |
| Timing | frames `1, 6, 11, 16, 21`; `44 fps`; duration `.454545455 s`; rate `2.2 Hz` |
| Curves | `8`: five rotation-Y curves plus root X/Y/Z; `40` deterministic linear keys |
| Limb motion | opposing `upper_arm.L/R` and `thigh.L/R`; exact maximum `30°` basis |
| Torso motion | bounded `spine` counter-sway; maximum `5°` |
| In-place/loop | root translation `[0, 0, 0]` at every sample; Action and evaluated mesh endpoints equal |
| Mannequin | `292/302` vertices move; maximum `.116433 m` |
| Starter top | `8/8` vertices move; maximum `.026634 m` |
| Starter bottom | `32/40` vertices move; maximum `.051886 m` |
| Signal Jacket | `16/16` vertices move; maximum `.030148 m` |

Combined time-sampled delta identity is `4810AA7DBA424EF9CE6ECF6FAF71044E5455D3FBE4CFCCD30A4F6321EE724BDB`. Semantic identity is `1B8E652909D8A316A604689B90816A2276AC3831C4F8DC85073DD1F5F8BA9350`; custody manifest SHA-256 is `258BBA1F1FE2EBE14184E931DE5BB697816D3BD615933BABB1EFDCC38B95A50F`.

Review render identities are starter frame 6 `C0A757CB3E8D100FCE47ABA39D04B0B23E5238A80D118559E462D922DDC0A40A`, starter frame 16 `5708DC36B2C0E88F7B2A00EA6F2624E747E2E4E06BB0BCDF79D7D0A5BE2202F0`, Signal Jacket frame 6 `79ACAA4353CAB23D04C26FC66FA93D7909226212ADE88AC3ADA4A380295016DC`, and Signal Jacket frame 16 `0D3608083214FE99BC479A70EBC3FE3BF860E9F0C2586BCDF1232750AE98EFC1`.

The full additive build reproduced Action, semantic, custody-manifest, and all four render identities exactly. Saved-source reopen validation passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender Action/time-sampled deformation | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Four-frame visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and exit `0`; log SHA-256 `1238E111CC16133E1333A916361C1CA2FE41A8879B3E920FA38DF8B7331C371D`; report JSON SHA-256 `9C8308FDA2C9053DBFDAEC5377F226AA72EB084579808F43E1F5E2DD1BA07862` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted bundled 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first build attempts stopped before output while the retained walk-property comparator was narrowed to the manifest's recorded precision and the run curve tolerance was aligned with Blender's deterministic float32 key storage. No predecessor file or product runtime changed during those failed attempts.

## Hard boundary

This phase adds no jump, land, further Action, NLA track, root motion, IK, control rig, constraint, driver, new geometry or clothing, FBX/export, Unreal import/integration, runtime/client/map/config/package-input change, ACharacter movement, capsule/collision, camera, replication, save, economy, wager, simulator, brain, external asset, paid input, final-art claim, beta-readiness claim, or Version 1 claim. The frozen Phase 0 simulation and all authoritative event-log, settlement, equal-information, Odds Bucks, inventory, and history boundaries remain unchanged.
