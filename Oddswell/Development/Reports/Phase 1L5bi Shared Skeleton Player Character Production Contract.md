# Phase 1L.5bi — Shared-Skeleton Player-Character Production Contract

Date: 2026-08-31
Status: **COMPLETE LOCALLY — OPTION B ACCEPTED; 1.80 M ONE-NEUTRAL-SILHOUETTE CONTRACT FROZEN; MODELING NOT STARTED**
Cost: **$0.00**

## Outcome

The owner approved Option B from Phase 1L.5bh with the recommended `1.80 m` controlling stature and one neutral beta silhouette. [[Design/Decisions/DEC-034 Shared Skeleton Player Character Production Candidate]] records the accepted authority and `Oddswell/Art/Production/PlayerCharacter/production_candidate_contract.json` freezes the smallest machine-readable input for the next Blender phase.

All eight existing preset IDs keep their current four skin tones and share one geometry/skeleton path. The candidate may refit only the starter top, starter bottom, and Signal Jacket and may prove only walk, run, jump, and landing. Existing Unreal movement, capsule collision, camera, replication, saves, economy, wagering, simulator, and brains remain unchanged.

This advances [[Design/Beta Game Bible#Avatar and clothing|Avatar and clothing]] and Phase 1L delivery steps 1, 2, and 5 by resolving the production-bridge owner gate without claiming that a character asset exists.

## Frozen contract

| Surface | Accepted value |
| --- | --- |
| Direction | Option B — bounded shared-skeleton production candidate |
| Stature | exact crown `1.80 m` |
| Silhouettes | one neutral beta silhouette |
| Appearance | exact eight existing preset IDs; exact four existing tones; shared geometry |
| Landmarks | ankle `.10`, knee `.53`, hip `.94`, wrist `.78`, elbow `1.12`, shoulder `1.45`, head center `1.66`, crown `1.80 m` |
| Clothing | starter top, starter bottom, Signal Jacket only |
| Motion | walk, run, jump, land only |
| Runtime integration | visual replacement only; preserve movement/capsule/camera/replication/saves |
| Cost/dependencies | `$0`; no external asset, paid service, marketplace download, plugin, or new dependency |

## Verification

| Gate | Result |
| --- | --- |
| Contract parse and exact counts | PASS — presets `8` unique, tones `4`, landmarks `8`, items `3`, motion states `4`, stature `1.80`, silhouettes `1` |
| Decision/report/wiki targets and roadmap canvas | PASS — files present; canvas JSON `22` unique nodes / `0` edges; NOW node `1L.5bi` |
| Frozen Python regression | PASS `9 + 2 + 8 + 46 + 40 = 105/105` on the established Python 3.13/allowlisted 3.12 split |
| Brain Admin `--check` | PASS |
| Native/package verification | REUSED — Phase 1L.5bh native `74/74` and accepted Phase 1L.5bg `50`-file / `1,052,124,588`-byte / Python-`0` package remain applicable because client/package-input diff is `0` |
| Diff hygiene | PASS — `git diff --check`; no Unreal source, content, config, map, package input, save, economy, wager, simulator, or brain file changed |

## Boundary and next gate

This is decision and contract evidence, not completed 3D work. No mesh, armature, rig, skin weight, animation asset, FBX, Unreal import, package, or runtime character replacement was created. The next separately verified subphase is one deterministic Blender source containing the faceless neutral mannequin and shared armature described by the contract.
