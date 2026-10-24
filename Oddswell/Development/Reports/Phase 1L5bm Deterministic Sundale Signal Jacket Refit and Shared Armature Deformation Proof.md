# Phase 1L.5bm — Deterministic Sundale Signal Jacket Refit and Shared-Armature Deformation Proof

Date: 2026-09-01
Status: **COMPLETE LOCALLY — EXACT ONE-ITEM SIGNAL-JACKET PROXY/STATIC-DIAGNOSTIC SOURCE ONLY; NOT RUNTIME OR FINAL CLOTHING**
Cost: **$0.00**
Cursor delegation: **NO**

## Outcome

Phase 1L.5bm advances roadmap Phase 1L items 1–2 and [[Design/Beta Game Bible#First-hour player journey|First-hour player journey item 6]] plus [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]] with the smallest authorized Signal Jacket source proof. It derives `Oddswell/Art/Production/PlayerCharacter/SignalJacketCandidate/SignalJacketCharacterCandidate.blend` from the exact retained Phase 1L.5bl source and leaves every predecessor byte unchanged.

Exactly one alternative top item exists: `sundale_signal_jacket`. Its one consolidated mesh contains only the accepted Phase 1L.3g shell and accent cubes. The two material slots use the exact locked slate and teal colors. The review hides the retained starter top and wears the jacket with the retained starter bottom; it changes no inventory or equip state.

All `16` jacket vertices have one normalized rigid `spine` influence and one retained shared-armature modifier. A temporary bounded `8°` spine rotation extends the existing shoulder/elbow/hip/knee diagnostic, moves every jacket and retained starter-top vertex, and then clears to rest. This proves both torso-bound alternatives follow the shared armature without claiming animation or runtime behavior.

## Source and fit custody

| Surface | Evidence |
| --- | --- |
| Accepted 1L.5bl source | every retained file byte exact; `.blend` SHA-256 `8638D6EEA3D8414EFFA4D2F8F656E1F761AB176C3D47F1DB11CE016159675D90` |
| Accepted 1L.5bl manifest | unchanged SHA-256 `CEA9E5C49AEB93587BCD88535271B6AC807BDC5D2995F1321BE97CA31C617DDF` |
| Accepted 1L.5bl builder | unchanged SHA-256 `2F6C89F04DAF1F906CB1094961BBC7B436A9FF6DC2CC5627BC9CF7E85F585296` |
| Accepted 1L.5bl provenance/renders | unchanged SHAs `DC590745...`, `01E120CF...`, `19D77BE0...` |
| Phase 1L.3g fit authority | review manifest SHA-256 `CCA6E44FC213D9F23547C2BE0964CAB9D85E4EE472E696183A864E44B95B811A`; exact one jacket design / one item / two proxy transforms |
| Body and starter outfit | geometry, `1.80 m` stature, landmarks, eight presets/four tones, starter top/bottom geometry and weights unchanged |
| Armature | exact one retained `12`-bone shared armature; names, hierarchy, and landmarks unchanged |

## Signal Jacket binding and static proof

| Predicate | Evidence |
| --- | --- |
| Item/object | `sundale_signal_jacket` / `CLOTHING__sundale_signal_jacket` |
| Shell | dimensions `0.58 × 0.315 × 0.50 m`; location `(0, -.012, 1.235)` |
| Accent | dimensions `0.59 × .018 × .075 m`; location `(0, -.171, 1.29)` |
| Materials | slot 0 slate `[0.12, 0.18, 0.22, 1.0]`; slot 1 teal `[0.08, 0.72, 0.68, 1.0]`; textures `0` |
| Mesh | one consolidated mesh; two components; `16` vertices / `12` polygons; geometry SHA-256 `07050BB48C19F8E1EAEB5600F88C3F49F4E7C2F24761190ED1440A6A36BC2D80` |
| Binding | `16/16` coverage; unweighted `0`; non-normalized `0`; exact `1.0` / maximum one influence; `spine` only; one armature modifier |
| Jacket diagnostic | `16/16` moved; maximum `.048213 m`; delta SHA-256 `AB71B8B390934C13F4DACCD22C9B9A3ADB0A33DB2B4654D015213BFD8851B6BE` |
| Retained starter top | `8/8` moved; maximum `.042593 m`; delta SHA-256 `4FC2D15714D816611F5B0763C3E96A6D5E892F3C8C23B875AD61ED06616D4334` |
| Retained starter bottom | `32/40` moved; maximum `.080378 m`; prior lower-body diagnostic preserved |

Combined deformation delta identity is `28A339F26ECDA82CCBE53550A4D3EDDC5BD3F5457467872D84707A4C372C77C7`; the saved source is clear rest pose. Semantic identity is `DBE2724EFA94F7969C80BEF6D6B885D2E568475BC00BA8D0270ADDF15CFB807D`; custody manifest SHA-256 is `F8AD6E6671876D65E3A846B0E2AF69848CAD29C0321D036FAE25AA068826F15B`. Rest render SHA-256 is `E90EFB2DBCFCBC35D20D58BE682529C3A6E836F29B11EDB39A0E426308CC4B0E`; static render SHA-256 is `5425F6C898A458DFFDFB2FEDB778EC95ED44DD61910AF84F9E391880F445220E`.

The full additive build reproduced semantic, custody-manifest, and both render identities exactly. Saved-source reopen and focused fit/binding/deformation validation also passed. `.blend` identity is semantic rather than byte-for-byte because Blender file serialization is not the accepted deterministic gate.

## Verification

| Gate | Result |
| --- | --- |
| Blender fit/binding/static diagnostic | PASS |
| Deterministic rerun and saved-source reopen | PASS |
| Rest/static visual review | PASS |
| Focused contract/wiki/canvas/client-diff checks | PASS — builder AST, exact manifest/source hashes, affected four-document `960`-link resolution, `22` unique canvas nodes / `0` edges, diff hygiene, and client diff `0` |
| Native Unreal regression | PASS — fresh `74/74`, warnings `0`, failures `0`; natural Queue Empty/TestExit and exit `0`; log SHA-256 `881C40E49DF0669DF4DE4E855B14A0636D238DF050AF6FDD3DD03DD28EAA6D23`; report JSON SHA-256 `C458918D5DB0B0E6FA263E202EAA5FC728A9089A323F5B48CA3B53FB458AC741` |
| Frozen Python regression | PASS — corrected canonical repository-root run `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted bundled 3.12 split. One earlier pre-discovery command used the suite directory as working directory and failed import; it executed no test before the corrected full run. |
| Brain Admin `--check` | PASS |
| Packaged Unreal integrity | REUSED/PASS — client/package-input diff `0`; accepted package remains exact at `50` files / `1,052,124,588` bytes / Python `0`; wrapper SHA-256 `5061151C8E07C919AB91281636CA840E63858F210F9FAE75FCACDDA1386CCDBD`; game SHA-256 `AC55B91E2B05CE45BEEADF03F29BF5AED9F9BE8E03376D4B9AD56B1767A81292`; accepted log SHA-256 `86C758F0D2125EC17E2DABE502CC6A561A475DD30788D37816F79ED83AB46E1D` |

## Hard boundary

This phase adds no sleeves or invented garment design, other clothing, inventory mutation, price, catalog, equip or economy behavior, cloth physics, collision modifier, texture, shape key, control rig, IK, constraint, driver, Action, NLA track, motion clip, walk/run/jump/land proof, FBX/export, Unreal import, client/map/config/package input, runtime change, face, hair, second silhouette, external asset, paid input, final-art claim, beta-readiness claim, or production-readiness claim. Existing movement, collision capsule, camera, replication, persistence, purchase/equip authority, economy, wagering, simulator, brain behavior, and frozen Phase 0 simulation remain unchanged.
