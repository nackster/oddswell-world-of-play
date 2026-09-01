# Phase 1L.5bn — Deterministic In-Place Walk-Cycle Action and Clothed Time-Sampled Deformation Proof

Date: 2026-09-01
Status: **COMPLETE LOCALLY — EXACT ONE IN-PLACE WALK ACTION/TIME-SAMPLED SOURCE PROOF ONLY; NOT UNREAL OR FINAL ANIMATION**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bn advances roadmap Phase 1L items 1–2 after 1L.5bm and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey item 1]] plus [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]]. It derives `Oddswell/Art/Production/PlayerCharacter/WalkCycleCandidate/WalkCycleCharacterCandidate.blend` from the exact retained Phase 1L.5bm source and leaves every predecessor byte unchanged.

Exactly one Action exists: `walk_candidate_v1`. Its frames `1–21` at `28 fps` reproduce the accepted Phase 1L.5bg primitive walk basis at exact `1.4` cycles/second. Left/right upper arms and thighs pitch oppositely up to `18°`; three root-location curves stay exact zero; start/end Action values and evaluated mesh coordinates are equal. One bounded `3°` spine counter-sway lets both torso-bound garment alternatives participate in the proof without adding a control rig or second animation.

Five time samples prove finite bounded deformation for the mannequin and both authorized presentations. Four deterministic review frames show frames `6` and `16` for starter top/bottom and Signal Jacket/bottom. The saved source remains at clear loop-start frame `1`.

## Source custody

| Accepted Phase 1L.5bm file | Unchanged SHA-256 |
| --- | --- |
| `build_signal_jacket_candidate.py` | `AEF602088661869625461D29C818B433D4EB86D88BAD19099CC6B52ADA4582DE` |
| `PROVENANCE.md` | `FF3EB12355DAC84A08A00FE6B58883F64D69547DD4125027CAADF9D9FD3D515E` |
| rest review | `E90EFB2DBCFCBC35D20D58BE682529C3A6E836F29B11EDB39A0E426308CC4B0E` |
| static review | `5425F6C898A458DFFDFB2FEDB778EC95ED44DD61910AF84F9E391880F445220E` |
| `signal_jacket_custody.json` | `F8AD6E6671876D65E3A846B0E2AF69848CAD29C0321D036FAE25AA068826F15B` |
| `SignalJacketCharacterCandidate.blend` | `6BA252C2B7E51360582673EBEA408B6E036708122834C3BEC01E6812A883FBBB` |

Mannequin geometry, exact `1.80 m` stature, eight presets/four tones, landmarks, 12-bone names and hierarchy, skin weights, starter clothing, Signal Jacket identity/materials, and saved review visibility remain semantically exact.

## Action and deformation proof

| Predicate | Evidence |
| --- | --- |
| Action | exactly one `walk_candidate_v1`; identity `5CC1C4A368F9CEC7FD1AED67004D3C40E5D920FC353B8141422C54DDE2E97C58` |
| Timing | frames `1, 6, 11, 16, 21`; `28 fps`; duration `.714285714 s`; rate `1.4 Hz` |
| Curves | `8`: five rotation-Y curves plus root X/Y/Z; `40` deterministic linear keys |
| Limb motion | opposing `upper_arm.L/R` and `thigh.L/R`; exact maximum `18°` |
| Torso motion | bounded `spine` counter-sway; exact maximum `3°` |
| In-place/loop | root translation `[0, 0, 0]` at every sample; Action and evaluated mesh endpoints equal |
| Mannequin | `292/302` vertices move; maximum `.070374 m` |
| Starter top | `8/8` vertices move; maximum `.015983 m` |
| Starter bottom | `32/40` vertices move; maximum `.031361 m` |
| Signal Jacket | `16/16` vertices move; maximum `.018092 m` |

Combined time-sampled delta identity is `6776CEE1418DFD555012649C99375D77339BDFDEA8486CCCD6A31913D4A7A273`. Semantic identity is `01EE564AD289A5768863E7818F8D08C0F592FD9C8C497F239B80EDF05E7EF6E2`; custody manifest SHA-256 is `F5677DA0726B9FD050C206A984174F91CE933AC537A7E2383A98B1A786DFF575`.

Review render identities are starter frame 6 `F0BAA8230A89C79E844A8B061101F3C05F23886D4A4129BE6CEAC1439861B860`, starter frame 16 `7C2681951E61CC6968160D3835B8F76596D832102A304CFD4D5595689383BA2D`, Signal Jacket frame 6 `B2CA11E3648BF3A55770FFE34AD59BA90886FF27E92C8C6EDD87197FF60FD406`, and Signal Jacket frame 16 `DEB37B226E937EA8A078D59D70C8108CE3C77B79EB2E43D65AE24A6A44285715`.

The full additive build reproduced Action, semantic, custody-manifest, and all four render identities exactly. Saved-source reopen and focused Action/deformation validation also passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender Action/time-sampled deformation | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Four-frame visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS — builder AST, exact Action/manifest/source hashes, affected four-document `963`-link resolution, `22` unique canvas nodes / `0` edges, diff hygiene, and client diff `0` |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and exit `0`; log SHA-256 `AF2344AC88DF7463DB2EA5FA2BC1B0D529ED481AE84D704A869DC991E9CB06C3`; report JSON SHA-256 `40CFF0447DBDAF28429161458F3DD17375687B145089F080216D0B88A6833334` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted bundled 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first Blender attempt stopped before output because the builder used `upper_leg.L/R`; the accepted armature names those exact owners `thigh.L/R`. The corrected builder uses the retained names. No predecessor file or product runtime changed during that failed attempt.

## Hard boundary

This phase adds no run, jump, land, extra Action, NLA track, root motion, IK, control rig, constraint, driver, export, FBX, Unreal import/integration, runtime/client/map/config/package-input change, ACharacter movement, capsule/collision, camera, replication, save, economy, wager, simulator, brain, external asset, paid input, final-art claim, beta-readiness claim, or Version 1 claim. The frozen Phase 0 simulation and all authoritative event-log, settlement, equal-information, Odds Bucks, inventory, and history boundaries remain unchanged.
