# Phase 1L.5bq — Deterministic In-Place Landing Action and Clothed Contact/Recovery Deformation Proof

Date: 2026-09-03
Status: **COMPLETE LOCALLY — RETAINED WALK/RUN/JUMP PLUS EXACT ONE IN-PLACE LANDING-POSE ACTION SOURCE PROOF ONLY; NOT UNREAL OR FINAL ANIMATION**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bq advances roadmap Phase 1L items 1–2 after 1L.5bp and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey item 1]] plus [[Design/Beta Game Bible#Avatar and clothing]]. It derives `Oddswell/Art/Production/PlayerCharacter/LandingActionCandidate/LandingActionCharacterCandidate.blend` from the exact retained Phase 1L.5bp source and leaves every predecessor byte unchanged.

The source preserves exact `walk_candidate_v1`, `run_candidate_v1`, and `jump_candidate_v1` semantics and adds only `land_candidate_v1`. Frames `1`, `6`, and `11` at `30 fps` define one bounded airborne-to-contact-to-neutral-recovery pose sequence. Nine rotation curves remain inside a `30°` pitch envelope; three root-location curves stay exact zero. Native `ACharacter` therefore remains the sole gameplay trajectory authority.

Three time samples prove finite bounded deformation for the mannequin and both authorized presentations. Four deterministic reviews show contact and neutral-recovery poses for starter top/bottom and Signal Jacket/bottom. The saved source remains at clear neutral-recovery frame `11`.

## Source custody

All eight Phase 1L.5bp files remain exact: builder `75DEABE42D0581700C0436315159EC5703F5E10509A017D8C1016544704E5256`, provenance `ED26256F3A753E50E39278ECA04D7E1D0A057F72FC579B0852C6B29995139A2A`, manifest `CD30E679450CF548EF39480342F06BA767C76BC42529078BFCED106E669936AC`, `.blend` `BABA8F5E655EB2629E5736F4D2DF8DD206BFA09EC55A2E3708A35CFD6DB52848`, and jump reviews `D91FCF84…`, `59D208BF…`, `925F1526…`, `51D3C07E…`.

Mannequin geometry, exact `1.80 m` stature, eight presets/four tones, landmarks, 12-bone names and hierarchy, skin weights, starter clothing, Signal Jacket identity/materials, walk Action identity `5CC1C4A368F9CEC7FD1AED67004D3C40E5D920FC353B8141422C54DDE2E97C58`, run Action identity `AA1707665B79313DABFD33142F99391CA9A144B37A7E217597633EA7E5E4E115`, and jump Action identity `B3F55824631C4C558253002A4B10FF9F52C4FB9C861CD77595F52C0F7934D506` remain semantically exact.

## Action and deformation proof

| Predicate | Evidence |
| --- | --- |
| Actions | exactly retained walk/run/jump plus new `land_candidate_v1` |
| Landing Action identity | `34BB5D6C502B42AA5FC2ACA0AB1BF4F3F98B8A753E4CE9A78BB6B2216ED922B2` |
| Poses | frame `1` airborne, frame `6` contact, frame `11` neutral recovery at `30 fps` |
| Curves | `12`: nine rotation-Y curves plus root X/Y/Z; `36` deterministic linear keys |
| Bounded pose | spine, bilateral upper arms/forearms/thighs/shins; maximum absolute pitch `30°` |
| Trajectory boundary | root translation `[0, 0, 0]` at every sample; `ACharacter` remains sole authority |
| Mannequin | `292/302` vertices move; maximum `.091580 m` |
| Starter top | `8/8` vertices move; maximum `.042593 m` |
| Starter bottom | `32/40` vertices move; maximum `.038252 m` |
| Signal Jacket | `16/16` vertices move; maximum `.048213 m` |

Combined time-sampled delta identity is `4CBB23052D67EAB4CDF9189CEB9BE63358720C9B37764F3A037BB75F01C8B528`. Semantic identity is `A2AA26058CD05C948CE7F4E9BAB7F9B5E926F8318436B9079BE51094A680102E`; custody manifest SHA-256 is `499A4622BF744B936513BD6BC42309A3C83FB1D52DA70C4196FB5D4C2B898ABC`.

Review identities are starter contact `FBE164EE418F1E7AA5C02315096FFD6BF19F0BF8215F5D1CFD37931DDEDBAB78`, starter neutral recovery `16C9276542F5AC194EAEC359E52AD7FE5FD1673DEE43A13B4D0CC48DA179C199`, Signal Jacket contact `8BC7AA9439AC27B79F69F94BD28A9A3D7D7B784B25D9855C1CCC20896050B9EC`, and Signal Jacket neutral recovery `01754DC240B50D364B0528F9DDE6ABDF4EBF24634F5C38C202D8E6B5622C3916`.

The full additive build reproduced Action, semantic, custody-manifest, and all four render identities exactly. Saved-source reopen validation passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender Action/time-sampled deformation | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Four-frame visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and exit `0`; log SHA-256 `0A7D070F78C825DF7BD39BF9E62261FFD2714A27C92BE3627F3573B75FE0DDCB`; report JSON SHA-256 `4A20C676D4CD7150D4890946784FB09EB890D3E8CE3EE75D2CF9734831DA8B59` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted bundled 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

The first build attempt stopped before output because retained run-specific custom-property validation was also being applied to the jump Action, which intentionally has pose-sequence semantics instead. The corrected builder retains exact curve validation for all three predecessor Actions and retains run-property validation where applicable. No predecessor file or product runtime changed during that failed attempt. The initial Python command also used a nonexistent `Oddswell/Tests/` prefix and stopped before loading tests; the corrected established roots passed all `105/105` tests.

## Hard boundary

This phase adds no fifth Action, root motion or gameplay trajectory, collision change, NLA track, IK, control rig, constraint, driver, new geometry or clothing, FBX/export, Unreal import/integration, runtime/client/map/config/package-input change, `ACharacter` movement, capsule, camera, replication, save, economy, wager, simulator, brain, external asset, paid input, final-art claim, beta-readiness claim, or Version 1 claim. The frozen Phase 0 simulation and all authoritative event-log, settlement, equal-information, Odds Bucks, inventory, and history boundaries remain unchanged.
