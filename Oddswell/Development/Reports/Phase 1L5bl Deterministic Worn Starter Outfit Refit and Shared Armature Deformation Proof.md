# Phase 1L.5bl — Deterministic Worn Starter-Outfit Refit and Shared-Armature Deformation Proof

Date: 2026-09-01
Status: **COMPLETE LOCALLY — EXACT TWO-PIECE STARTER-PROXY REFIT/STATIC-DIAGNOSTIC SOURCE ONLY; NOT RUNTIME OR FINAL CLOTHING**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bl advances [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]] with the smallest worn starter-outfit source allowed by the accepted contract. It derives `Oddswell/Art/Production/PlayerCharacter/WornStarterOutfitCandidate/WornStarterOutfitCharacterCandidate.blend` from the exact retained Phase 1L.5bk source and leaves every accepted predecessor byte unchanged.

Exactly two clothing mesh identities exist: `starter_offwhite_top` and `starter_offwhite_bottom`. They reproduce only the Phase 1L.3g starter proxy transform signature and exact `[0.92, 0.90, 0.82, 1.0]` off-white color. The top is the accepted single torso proxy; the bottom consolidates the accepted pelvis and two upper-leg proxies into one item mesh. No garment design was added.

All `48` clothing vertices have one normalized rigid influence to the retained shared armature. The top's `8` vertices use only `spine`; the bottom's `40` vertices use only `root`, `thigh.L`, and `thigh.R`. The retained temporary shoulder/elbow/hip/knee diagnostic moves the `32` upper-leg garment vertices and clears to rest. The top truthfully moves `0` vertices because the diagnostic does not pose its `spine` owner. This proves the required lower outfit components follow their shared-armature deformation without claiming animation or runtime behavior.

## Source and fit custody

| Surface | Evidence |
| --- | --- |
| Accepted 1L.5bk `.blend` | unchanged SHA-256 `9CBD196FDB42FA76788673467D16954733796AE6820073075005444B0942A443` |
| Accepted 1L.5bk manifest | unchanged SHA-256 `09BCC9BFDA60E1F7FE6F0288D52AA8C4FA22671653C2A190D96A682802CF9751` |
| Accepted 1L.5bk builder | unchanged SHA-256 `985FE86049B28108E0A56573CA4328755062644EB4AAA4EB5C518D3BF5248FFD` |
| Phase 1L.3g fit authority | review manifest SHA-256 `CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A`; exact one starter design / two item IDs / four proxy transforms |
| Body | geometry identity `3ADB62F5D9577FDE2E45D8FFA45B5AB448D088D72A239496D5170122473F8FE3`, stature, landmarks, presets, tones, and skinning unchanged |
| Armature | exact one retained `12`-bone shared armature; names, hierarchy, and landmarks unchanged |

## Outfit binding and static proof

| Predicate | Top | Bottom |
| --- | --- | --- |
| Item ID | `starter_offwhite_top` | `starter_offwhite_bottom` |
| Proxy components | torso `1` | pelvis `1` + upper legs `2` |
| Vertices / polygons | `8 / 6` | `40 / 26` |
| Allowed bone groups | `spine` | `root`, `thigh.L`, `thigh.R` |
| Coverage | `8/8`; unweighted `0` | `40/40`; unweighted `0` |
| Normalization / max influences | exact `1.0 / 1` | exact `1.0 / 1` |
| Armature modifiers | `1` | `1` |
| Diagnostic movement | `0` vertices; spine unposed | `32` vertices; maximum `.080378 m` |

Combined deformation delta identity is `07450DEE4E51FE3DF8A633318E152F377BCD2EFDFF80E7CDCAED69A74EC850BB`; the saved source is clear rest pose. Semantic identity is `244E7CCCC5AECA4B118AD74CBC959B97AEBEBB2D2B5139E98F243155361345A2`; custody manifest SHA-256 is `CEA9E5C49AEB93587BCD88535271B6AC807BDC5D2995F1321BE97CA31C617DDF`. Rest render SHA-256 is `01E120CF309E031C8297351746C1B175EFEA093D2CFF8DE4BA478B26E598C02A`; static render SHA-256 is `19D77BE007D613B9B5CF6FE68BA466BF285CEE9629393A6C2C9A44DAA4640CDD`.

The full additive build reproduced semantic, custody-manifest, and both render identities exactly. Saved-source reopen and focused fit/binding/deformation validation also passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender fit/binding/static diagnostic | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Rest/static visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and process exit `0`; report JSON SHA-256 `11298B5E63A918CEC9F3211E117F6B68D3C29E642064FC6CC462ACB91DB24FCC` |
| Frozen Python regression | PASS — `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted 3.12 split |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

## Hard boundary

This phase creates no Signal Jacket, other clothing, cloth physics, collision modifier, texture, shape key, control rig, IK, constraint, driver, Action, NLA track, motion clip, walk/run/jump/land proof, FBX/export, Unreal import, client/map/config/package input, runtime/economy/catalog change, external asset, paid input, final-art claim, beta-readiness claim, or production-readiness claim. Existing movement, collision capsule, camera, replication, persistence, economy, wagering, simulator, brain behavior, and frozen Phase 0 simulation remain unchanged.
