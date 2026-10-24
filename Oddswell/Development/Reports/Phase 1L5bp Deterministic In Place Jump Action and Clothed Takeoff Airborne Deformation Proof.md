# Phase 1L.5bp — Deterministic In-Place Jump Action and Clothed Takeoff/Airborne Deformation Proof

Date: 2026-09-03
Status: **COMPLETE LOCALLY — RETAINED WALK/RUN PLUS EXACT ONE IN-PLACE JUMP-POSE ACTION SOURCE PROOF ONLY; NOT UNREAL OR FINAL ANIMATION**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bp advances roadmap Phase 1L items 1–2 after 1L.5bo and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey item 1]] plus [[Design/Beta Game Bible#Avatar and clothing]]. It derives `Oddswell/Art/Production/PlayerCharacter/JumpActionCandidate/JumpActionCharacterCandidate.blend` from the exact retained Phase 1L.5bo source and leaves every predecessor byte unchanged.

The source preserves exact `walk_candidate_v1` and `run_candidate_v1` semantics and adds only `jump_candidate_v1`. Frames `1`, `6`, and `11` at `30 fps` define one bounded neutral-to-takeoff-to-airborne pose sequence. Nine rotation curves remain inside a `30°` pitch envelope; three root-location curves stay exact zero. Native `ACharacter` therefore remains the sole gameplay trajectory authority.

Three time samples prove finite bounded deformation for the mannequin and both authorized presentations. Four deterministic reviews show takeoff and airborne poses for starter top/bottom and Signal Jacket/bottom. The saved source remains at clear neutral frame `1`.

## Source custody

All eight Phase 1L.5bo files remain exact: builder `17CEBD817AF7EE672ADB918FC70B8997F60FA6941FFFB4E1FD4B200062F77411`, provenance `4E57B2172C0A61AA2A65154417BA87AA578DD661DD6D38825267D560FC8F0E84`, manifest `258BBA1F1FE2EBE14184E931DE5BB697816D3BD615933BABB1EFDCC38B95A50F`, `.blend` `E830E204C13F5F268C71D26EA5C45B4264E72C8C4E799857CE80F39AB5F8AE78`, and run reviews `79ACAA43…`, `0D360808…`, `C0A757CB…`, `5708DC36…`.

Mannequin geometry, exact `1.80 m` stature, eight presets/four tones, landmarks, 12-bone names and hierarchy, skin weights, starter clothing, Signal Jacket identity/materials, walk Action identity `5CC1C4A368F9CEC7FD1AED67004D3C40E5D920FC353B8141422C54DDE2E97C58`, and run Action identity `AA1707665B79313DABFD33142F99391CA9A144B37A7E217597633EA7E5E4E115` remain semantically exact.

## Action and deformation proof

| Predicate | Evidence |
| --- | --- |
| Actions | exactly retained walk/run plus new `jump_candidate_v1` |
| Jump Action identity | `B3F55824631C4C558253002A4B10FF9F52C4FB9C861CD77595F52C0F7934D506` |
| Poses | frame `1` neutral, frame `6` takeoff, frame `11` airborne at `30 fps` |
| Curves | `12`: nine rotation-Y curves plus root X/Y/Z; `36` deterministic linear keys |
| Bounded pose | spine, bilateral upper arms/forearms/thighs/shins; maximum absolute pitch `30°` |
| Trajectory boundary | root translation `[0, 0, 0]` at every sample; `ACharacter` remains sole authority |
| Mannequin | `292/302` vertices move; maximum `.091580 m` |
| Starter top | `8/8` vertices move; maximum `.031956 m` |
| Starter bottom | `32/40` vertices move; maximum `.038252 m` |
| Signal Jacket | `16/16` vertices move; maximum `.036172 m` |

Combined time-sampled delta identity is `D9DFF0A8E17F0E71BB7159092C5FA8407F0D58233A5C22782A867EFA8750368A`. Semantic identity is `D582C924E160C4086BCFAEF4781D3902B47254E55410C4089797D1BD178C4BA8`; custody manifest SHA-256 is `CD30E679450CF548EF39480342F06BA767C76BC42529078BFCED106E669936AC`.

Review identities are starter takeoff `51D3C07E79A8E2D2AD4B24F859A62CD51116DBF0E66FD9D84017493CB5869579`, starter airborne `925F1526AF4FDDC8AC0896BA7D8437C4D891B5BA54B0B692A4795EBE5F708806`, Signal Jacket takeoff `59D208BF6FEA5BB177378793282B70688C5BE33823C1D4536B0EB78C7F7C3A78`, and Signal Jacket airborne `D91FCF84708EC4FBCF4F6ED9ADA7DFCF8DA6CCCA6D48890557C623F77550E466`.

The full additive build reproduced Action, semantic, custody-manifest, and all four render identities exactly. Saved-source reopen validation passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender Action/time-sampled deformation | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Four-frame visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and exit `0`; log SHA-256 `6893A57512267719056A415F9E39F64691D5CBA5D26C3AAA9F3E172E6C7D6C7B`; report JSON SHA-256 `0A426475764950E9274178A6ACF268B12F353C841D0074B0E279EADDC71498ED` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted bundled 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first build attempt stopped before output because the retained armature uses `forearm.L/R`, not `lower_arm.L/R`. The corrected builder uses the exact retained names. No predecessor file or product runtime changed during that failed attempt.

## Hard boundary

This phase adds no landing Action, further animation, root motion or gameplay trajectory, NLA track, IK, control rig, constraint, driver, new geometry or clothing, FBX/export, Unreal import/integration, runtime/client/map/config/package-input change, ACharacter movement, capsule/collision, camera, replication, save, economy, wager, simulator, brain, external asset, paid input, final-art claim, beta-readiness claim, or Version 1 claim. The frozen Phase 0 simulation and all authoritative event-log, settlement, equal-information, Odds Bucks, inventory, and history boundaries remain unchanged.
